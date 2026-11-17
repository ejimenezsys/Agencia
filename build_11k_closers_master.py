#!/usr/bin/env python3
"""Extracción paralela en Apify + unificación local (Cortexia) para armar 11,000 leads
calificados y etiquetados (1,000 por Closer, conservando la base actual de Claudio).

Uso:
    ./venv/bin/python3 build_11k_closers_master.py
"""
import csv
import glob
import gzip
import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

BASE_DIR = Path(__file__).resolve().parent
CORTEXIA_DIR = Path("/Users/ejimenezsys/Desktop/Cortexia/777_cortexia_v15.2_Ejimenezsys")
CORTEXIA_GP_DIR = CORTEXIA_DIR / "DOCS" / "CONTENIDO" / "PROYECTOS" / "prosper_ia" / "fuentes" / "google_places"
APIFY_CACHE_DIR = BASE_DIR / "scratch" / "apify_batches"
SEED_OUTPUT_PATH = BASE_DIR / "seeds" / "closers_11k_master_seed.json.gz"
SUMMARY_OUTPUT_PATH = BASE_DIR / "scratch" / "closers_11k_summary.json"

PER_JOB_TIMEOUT_SECS = 240

INTERNAL_EMAILS = {
    "sheille.perez@gmail.com",
    "diegoarriondo03@gmail.com",
    "cinthyapenida0@gmail.com",
    "claudiniosan@yahoo.com.ar",
    "loremrodriguezafb@gmail.com",
    "sergiotorales608@gmail.com",
    "laverdaderafuerza02@gmail.com",
    "wendyleiva59@gmail.com",
    "digitalblups@gmail.com",
    "bruno.hernan.espinosa1694@gmail.com",
    "tanyah.unity@gmail.com",
    "admin@prosperia.com",
    "edward@agenciaprosperia.com",
}

COUNTRY_META = {
    "MX": {"name": "México", "flag": "🇲🇽", "dial": "52", "tz": "America/Mexico_City"},
    "CO": {"name": "Colombia", "flag": "🇨🇴", "dial": "57", "tz": "America/Bogota"},
    "PE": {"name": "Perú", "flag": "🇵🇪", "dial": "51", "tz": "America/Lima"},
    "ES": {"name": "España", "flag": "🇪🇸", "dial": "34", "tz": "Europe/Madrid"},
    "AR": {"name": "Argentina", "flag": "🇦🇷", "dial": "54", "tz": "America/Argentina/Buenos_Aires"},
    "US": {"name": "Estados Unidos", "flag": "🇺🇸", "dial": "1", "tz": "America/New_York"},
    "CL": {"name": "Chile", "flag": "🇨🇱", "dial": "56", "tz": "America/Santiago"},
}

NICHE_META = {
    "dental": {
        "label": "Clínica Dental",
        "emoji": "🦷",
        "db_niche": "clinica",
        "template": "clinica_dental_estetica",
    },
    "estetica": {
        "label": "Clínica Estética & Spa",
        "emoji": "✨",
        "db_niche": "clinica",
        "template": "clinica_dental_estetica",
    },
    "capilar": {
        "label": "Clínica Capilar",
        "emoji": "💆",
        "db_niche": "clinica",
        "template": "clinica_dental_estetica",
    },
    "belleza": {
        "label": "Salón de Belleza",
        "emoji": "💅",
        "db_niche": "clinica",
        "template": "clinica_dental_estetica",
    },
    "inmobiliaria": {
        "label": "Inmobiliaria / Bienes Raíces",
        "emoji": "🏢",
        "db_niche": "inmobiliaria",
        "template": "inmobiliaria_bienes_raices",
    },
    "academia": {
        "label": "Academia & Cursos",
        "emoji": "🎓",
        "db_niche": "profesionales",
        "template": "academia_cursos_coaching",
    },
    "coaching": {
        "label": "Coaching & Consultoría",
        "emoji": "🚀",
        "db_niche": "profesionales",
        "template": "academia_cursos_coaching",
    },
    "hvac": {
        "label": "Aire Acondicionado / HVAC",
        "emoji": "❄️",
        "db_niche": "servicios_locales",
        "template": "aire_acondicionado_hvac",
    },
    "plomeria": {
        "label": "Plomería & Fugas 24/7",
        "emoji": "🚿",
        "db_niche": "servicios_locales",
        "template": "plomeria_fugas_24_7",
    },
    "electricista": {
        "label": "Electricistas Urgencias 24/7",
        "emoji": "⚡",
        "db_niche": "servicios_locales",
        "template": "electricistas_urgencias_24_7",
    },
    "legal": {
        "label": "Firma Legal / Abogados",
        "emoji": "⚖️",
        "db_niche": "profesionales",
        "template": "estudio_contable_legal",
    },
}

APIFY_BATCHES = [
    {
        "id": "pe_clinics_beauty",
        "country": "PE",
        "maxCrawledPlacesPerSearch": 115,
        "maxItems": 750,
        "searches": [
            "clínica dental Lima Perú",
            "dentista Miraflores San Isidro Lima",
            "clínica estética medicina estética Lima Perú",
            "salón de belleza spa Lima Perú",
            "clínica dental Arequipa Perú",
            "salón de belleza Miraflores Surco Lima",
            "clínica estética dental Trujillo Perú",
        ],
    },
    {
        "id": "pe_inmob_academies_elec",
        "country": "PE",
        "maxCrawledPlacesPerSearch": 120,
        "maxItems": 1100,
        "searches": [
            "inmobiliaria Lima Perú",
            "bienes raíces Miraflores San Isidro Lima",
            "agencia inmobiliaria Arequipa Trujillo Perú",
            "academia cursos capacitación Lima Perú",
            "escuela de negocios capacitación empresarial Lima",
            "academia de inglés cursos Arequipa Trujillo",
            "electricista 24 horas emergencia Lima Perú",
            "servicio eléctrico instalaciones eléctricas Lima",
            "electricista domicilio Arequipa Trujillo Perú",
        ],
    },
    {
        "id": "es_all",
        "country": "ES",
        "maxCrawledPlacesPerSearch": 110,
        "maxItems": 880,
        "searches": [
            "agencia inmobiliaria Madrid España",
            "agencia inmobiliaria Barcelona España",
            "inmobiliaria Valencia Málaga España",
            "clínica dental estética Madrid Barcelona",
            "clínica dental Valencia Málaga España",
            "academia formación cursos Madrid Barcelona",
            "salón de belleza peluquería estética Madrid",
            "salón de belleza peluquería Barcelona Valencia",
        ],
    },
    {
        "id": "ar_academies_coach",
        "country": "AR",
        "maxCrawledPlacesPerSearch": 115,
        "maxItems": 700,
        "searches": [
            "academia cursos capacitación Buenos Aires Argentina",
            "centro de formación profesional cursos CABA Palermo",
            "coaching empresarial mentoría negocios Buenos Aires",
            "academia cursos capacitación Córdoba Argentina",
            "academia cursos capacitación Rosario Argentina",
            "escuela de negocios cursos online Argentina",
        ],
    },
    {
        "id": "ar_inmob_beauty",
        "country": "AR",
        "maxCrawledPlacesPerSearch": 110,
        "maxItems": 850,
        "searches": [
            "inmobiliaria Buenos Aires CABA Argentina",
            "inmobiliaria Palermo Belgrano Recoleta Buenos Aires",
            "inmobiliaria Córdoba Rosario Mendoza Argentina",
            "clínica estética medicina estética Buenos Aires",
            "salón de belleza peluquería spa Buenos Aires",
            "centro de estética peluquería Córdoba Rosario",
            "clínica odontológica dental Buenos Aires",
        ],
    },
    {
        "id": "mx_hvac",
        "country": "MX",
        "maxCrawledPlacesPerSearch": 115,
        "maxItems": 800,
        "searches": [
            "aire acondicionado climatización CDMX Ciudad de México",
            "mantenimiento aire acondicionado Monterrey Nuevo León",
            "aire acondicionado instalación reparación Guadalajara",
            "aire acondicionado climatización Cancún Quintana Roo",
            "aire acondicionado refrigeración Mérida Yucatán",
            "climatización HVAC Querétaro Puebla",
            "aire acondicionado Tijuana León Guanajuato",
        ],
    },
    {
        "id": "mx_plumbing",
        "country": "MX",
        "maxCrawledPlacesPerSearch": 110,
        "maxItems": 500,
        "searches": [
            "plomero 24 horas fugas destapes CDMX",
            "plomería destapes urgencias Monterrey",
            "plomero 24 horas Guadalajara Jalisco",
            "plomería fugas de agua Puebla Querétaro",
            "plomero destape de drenajes Estado de México León",
        ],
    },
    {
        "id": "mx_inmob",
        "country": "MX",
        "maxCrawledPlacesPerSearch": 120,
        "maxItems": 750,
        "searches": [
            "inmobiliaria bienes raíces Guadalajara Jalisco",
            "inmobiliaria Monterrey San Pedro Garza García",
            "agencia inmobiliaria CDMX Polanco Roma Condesa",
            "bienes raíces Cancún Playa del Carmen Tulum",
            "inmobiliaria Querétaro Puebla Mérida",
            "bienes raíces Estado de México Toluca Metepec",
        ],
    },
    {
        "id": "mx_academies_coach",
        "country": "MX",
        "maxCrawledPlacesPerSearch": 120,
        "maxItems": 1050,
        "searches": [
            "academia cursos capacitación CDMX",
            "coaching empresarial escuela de negocios CDMX",
            "academia cursos capacitación Monterrey",
            "coaching capacitación empresarial Guadalajara",
            "academia cursos idiomas capacitación Puebla Querétaro",
            "centro de capacitación cursos Mérida León Tijuana",
            "escuela de belleza cursos técnicos CDMX Monterrey",
        ],
    },
    {
        "id": "co_hvac_academies",
        "country": "CO",
        "maxCrawledPlacesPerSearch": 120,
        "maxItems": 1050,
        "searches": [
            "aire acondicionado climatización Bogotá",
            "aire acondicionado mantenimiento Medellín",
            "aire acondicionado refrigeración Barranquilla Cartagena Cali",
            "academia cursos capacitación Bogotá",
            "escuela de negocios coaching empresarial Bogotá",
            "academia cursos capacitación Medellín Cali",
            "centro de formación capacitación Barranquilla Bucaramanga",
        ],
    },
    {
        "id": "us_realestate_legal",
        "country": "US",
        "maxCrawledPlacesPerSearch": 115,
        "maxItems": 800,
        "searches": [
            "real estate agency bienes raíces Miami Doral Florida",
            "realtor bienes raíces Orlando Kissimmee Tampa Florida",
            "real estate agency bienes raíces Houston Dallas Texas",
            "real estate agencia bienes raíces Los Angeles California",
            "abogado inmigración immigration lawyer Miami Doral Florida",
            "abogado accidentes personal injury lawyer Miami Houston",
            "abogado defensa negocios law firm Orlando Los Angeles",
        ],
    },
    # ── Round 2 Neighborhood-Level Batches (proven 2-3 word queries) ──
    {
        "id": "r2_pe_lima_zones",
        "country": "PE",
        "maxCrawledPlacesPerSearch": 55,
        "maxItems": 1100,
        "searches": [
            "clinica dental miraflores lima",
            "clinica dental san isidro lima",
            "clinica dental surco lima",
            "clinica dental la molina lima",
            "clinica dental arequipa",
            "clinica dental trujillo",
            "inmobiliaria miraflores lima",
            "inmobiliaria san isidro lima",
            "inmobiliaria surco lima",
            "inmobiliaria arequipa",
            "inmobiliaria trujillo",
            "electricista lima",
            "electricista miraflores surco",
            "electricista arequipa",
            "electricista trujillo",
            "salon de belleza miraflores lima",
            "salon de belleza san isidro lima",
            "salon de belleza surco lima",
            "academia ingles lima",
            "centro capacitacion lima",
            "escuela negocios lima",
            "academia cursos arequipa",
            "academia cursos trujillo",
            "estetica miraflores lima",
        ],
    },
    {
        "id": "r2_mx_academies_coach_zones",
        "country": "MX",
        "maxCrawledPlacesPerSearch": 55,
        "maxItems": 1000,
        "searches": [
            "academia polanco cdmx",
            "academia coyoacan cdmx",
            "academia del valle cdmx",
            "academia roma condesa cdmx",
            "centro capacitacion monterrey",
            "escuela negocios monterrey",
            "academia zapopan guadalajara",
            "coaching empresarial cdmx",
            "coaching monterrey",
            "coaching guadalajara",
            "academia idiomas puebla",
            "academia cursos queretaro",
            "cursos capacitacion leon guanajuato",
            "academia cursos merida",
            "academia cursos tijuana",
            "escuela gastronomia cdmx",
            "academia belleza cdmx",
            "academia belleza monterrey",
            "cursos ingles guadalajara",
            "escuela computacion cdmx",
        ],
    },
    {
        "id": "r2_co_academies_coach_zones",
        "country": "CO",
        "maxCrawledPlacesPerSearch": 55,
        "maxItems": 700,
        "searches": [
            "academia chapinero bogota",
            "academia usaquen bogota",
            "academia poblado medellin",
            "academia laureles medellin",
            "coaching empresarial bogota",
            "coaching medellin",
            "academia cursos cali",
            "academia cursos barranquilla",
            "centro capacitacion bogota",
            "escuela idiomas bogota",
            "academia cursos bucaramanga",
            "aire acondicionado bogota",
            "aire acondicionado medellin",
            "aire acondicionado barranquilla",
            "aire acondicionado cali",
        ],
    },
    {
        "id": "r2_ar_zones",
        "country": "AR",
        "maxCrawledPlacesPerSearch": 55,
        "maxItems": 950,
        "searches": [
            "inmobiliaria palermo buenos aires",
            "inmobiliaria belgrano buenos aires",
            "inmobiliaria recoleta buenos aires",
            "inmobiliaria caballito buenos aires",
            "inmobiliaria cordoba argentina",
            "inmobiliaria rosario argentina",
            "academia cursos buenos aires",
            "centro capacitacion caba",
            "coaching buenos aires",
            "academia cursos cordoba",
            "academia cursos rosario",
            "peluqueria palermo buenos aires",
            "salon belleza belgrano caba",
            "centro estetica recoleta caba",
            "clinica odontologica palermo",
            "clinica odontologica cordoba",
            "salon belleza rosario",
        ],
    },
    {
        "id": "r2_es_zones",
        "country": "ES",
        "maxCrawledPlacesPerSearch": 55,
        "maxItems": 800,
        "searches": [
            "inmobiliaria salamanca madrid",
            "inmobiliaria chamberi madrid",
            "inmobiliaria eixample barcelona",
            "inmobiliaria valencia centro",
            "inmobiliaria malaga centro",
            "clinica dental salamanca madrid",
            "clinica dental eixample barcelona",
            "salon belleza madrid",
            "peluqueria eixample barcelona",
            "centro estetica valencia",
            "academia formacion madrid",
            "academia barcelona",
            "academia valencia",
            "clinica estetica madrid",
            "inmobiliaria sevilla",
        ],
    },
    {
        "id": "r2_mx_hvac_plumb_inmob_zones",
        "country": "MX",
        "maxCrawledPlacesPerSearch": 55,
        "maxItems": 950,
        "searches": [
            "plomero benito juarez cdmx",
            "plomero coyoacan cdmx",
            "plomero naucalpan",
            "plomero monterrey",
            "plomero guadalajara",
            "aire acondicionado polanco cdmx",
            "aire acondicionado monterrey",
            "aire acondicionado san pedro garza",
            "aire acondicionado guadalajara",
            "aire acondicionado cancun",
            "aire acondicionado merida",
            "inmobiliaria zapopan guadalajara",
            "inmobiliaria san pedro monterrey",
            "inmobiliaria polanco cdmx",
            "inmobiliaria queretaro",
            "inmobiliaria cancun",
            "inmobiliaria puebla",
            "inmobiliaria merida",
        ],
    },
    {
        "id": "r2_us_legal_realestate_zones",
        "country": "US",
        "maxCrawledPlacesPerSearch": 55,
        "maxItems": 600,
        "searches": [
            "abogado inmigracion miami",
            "personal injury lawyer miami",
            "abogado accidentes doral fl",
            "abogado orlando fl",
            "abogado houston tx",
            "abogado los angeles ca",
            "real estate miami doral",
            "real estate brickell coral gables",
            "bienes raices orlando fl",
            "real estate houston tx",
            "real estate los angeles ca",
            "law firm miami fl",
        ],
    },
    {
        "id": "r3_ar_inmob_academia_clinica",
        "country": "AR",
        "maxCrawledPlacesPerSearch": 55,
        "maxItems": 650,
        "searches": [
            "inmobiliaria mendoza",
            "inmobiliaria la plata",
            "inmobiliaria mar del plata",
            "inmobiliaria san isidro",
            "inmobiliaria vicente lopez",
            "inmobiliaria villa urquiza",
            "academia mendoza argentina",
            "academia la plata",
            "coaching cordoba argentina",
            "clinica estetica san isidro",
            "clinica dental belgrano caba",
            "peluqueria recoleta caba",
            "inmobiliaria tucuman",
            "clinica estetica mendoza",
        ],
    },
    {
        "id": "r3_es_clinics_inmob_academia",
        "country": "ES",
        "maxCrawledPlacesPerSearch": 55,
        "maxItems": 650,
        "searches": [
            "inmobiliaria bilbao",
            "inmobiliaria zaragoza",
            "inmobiliaria alicante",
            "inmobiliaria palma mallorca",
            "clinica dental bilbao",
            "clinica dental valencia",
            "clinica dental sevilla",
            "clinica estetica barcelona",
            "centro estetica madrid",
            "peluqueria valencia centro",
            "inmobiliaria murcia",
            "inmobiliaria granada",
            "clinica estetica malaga",
        ],
    },
    {
        "id": "r3_mx_inmob_academias_fill",
        "country": "MX",
        "maxCrawledPlacesPerSearch": 55,
        "maxItems": 650,
        "searches": [
            "inmobiliaria tijuana",
            "inmobiliaria leon guanajuato",
            "inmobiliaria toluca",
            "inmobiliaria aguascalientes",
            "inmobiliaria san luis potosi",
            "inmobiliaria playa del carmen",
            "inmobiliaria cuernavaca",
            "bienes raices monterrey",
            "academia cursos tijuana",
            "academia cursos leon guanajuato",
            "coaching guadalajara",
            "coaching monterrey",
            "escuela idiomas guadalajara",
        ],
    },
    {
        "id": "r3_co_academia_coach_fill",
        "country": "CO",
        "maxCrawledPlacesPerSearch": 55,
        "maxItems": 500,
        "searches": [
            "academia pereira",
            "academia cartagena",
            "academia manizales",
            "academia cucuta",
            "instituto capacitacion bogota",
            "escuela belleza medellin",
            "escuela idiomas cali",
            "coaching bogota",
            "coaching medellin",
            "consultoria empresarial bogota",
        ],
    },
    {
        "id": "r4_ar_es_quick_fill",
        "country": "AR",
        "maxCrawledPlacesPerSearch": 60,
        "maxItems": 320,
        "searches": [
            "inmobiliaria neuquen argentina",
            "inmobiliaria salta argentina",
            "inmobiliaria puerto madero caba",
            "inmobiliaria nunez belgrano caba",
            "academia ingles buenos aires",
            "curso marketing digital buenos aires",
            "clinica estetica villa crespo",
            "clinica estetica san telmo caba",
        ],
    },
]


def load_apify_token() -> str:
    env_tok = os.environ.get("APIFY_TOKEN", "").strip()
    if env_tok:
        return env_tok
    for env_path in [CORTEXIA_DIR / ".env", BASE_DIR / ".env"]:
        if env_path.exists():
            txt = env_path.read_text(errors="ignore")
            m = re.search(r"APIFY[A-Z0-9_]*\s*=\s*[\"']?([a-zA-Z0-9_\-]+)", txt)
            if m:
                return m.group(1)
    raise RuntimeError("No se encontró APIFY_TOKEN en variables de entorno ni .env")


def api_req(method: str, url: str, payload: Optional[dict] = None, timeout: int = 30) -> Any:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json", "User-Agent": "ProsperIA-MasterSeed/1.0"}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def run_single_apify_batch(batch: dict, token: str) -> Tuple[str, List[dict], dict]:
    bid = batch["id"]
    cache_file = APIFY_CACHE_DIR / f"{bid}.json"
    if cache_file.exists():
        try:
            cached = json.loads(cache_file.read_text(encoding="utf-8"))
            if isinstance(cached, list) and len(cached) >= 20:
                print(f"[CACHE] {bid}: {len(cached)} items", flush=True)
                return bid, cached, {"cached": True, "count": len(cached), "usd": 0.0}
        except Exception:
            pass

    actor_input = {
        "searchStringsArray": batch["searches"],
        "maxCrawledPlacesPerSearch": batch["maxCrawledPlacesPerSearch"],
        "maxItems": batch["maxItems"],
        "language": "es",
        "maxReviews": 0,
        "maxImages": 0,
        "maxQuestions": 0,
        "scrapeReviewerProfile": False,
        "scrapeReviewsPersonalData": False,
        "scrapeImageAuthors": False,
        "skipClosedPlaces": True,
        "exportPlaceUrls": False,
        "includeWebResults": False,
    }
    start_url = f"https://api.apify.com/v2/acts/compass~crawler-google-places/runs?token={token}&memory=4096"
    run_resp = api_req("POST", start_url, actor_input, timeout=30)
    run_data = run_resp.get("data", {})
    run_id = run_data["id"]
    dataset_id = run_data["defaultDatasetId"]
    print(f"[APIFY START] {bid} -> run={run_id} (maxItems={batch['maxItems']})", flush=True)

    t0 = time.time()
    status = run_data.get("status", "RUNNING")
    usage_usd = 0.0
    aborted = False
    while status in ("READY", "RUNNING"):
        if time.time() - t0 >= PER_JOB_TIMEOUT_SECS:
            print(f"[APIFY TIMEOUT 240s] {bid} -> abortando run {run_id} y cosechando dataset...", flush=True)
            try:
                api_req("POST", f"https://api.apify.com/v2/actor-runs/{run_id}/abort?token={token}", {}, timeout=15)
                aborted = True
            except Exception as ae:
                print(f"[APIFY ABORT WARN] {bid}: {ae}", flush=True)
            break
        time.sleep(6)
        try:
            st_resp = api_req("GET", f"https://api.apify.com/v2/actor-runs/{run_id}?token={token}", timeout=20)
            st_data = st_resp.get("data", {})
            status = st_data.get("status", status)
            usage_usd = float(st_data.get("usageTotalUsd") or 0.0)
        except Exception:
            pass

    if not aborted:
        try:
            st_resp = api_req("GET", f"https://api.apify.com/v2/actor-runs/{run_id}?token={token}", timeout=20)
            usage_usd = float(st_resp.get("data", {}).get("usageTotalUsd") or usage_usd)
        except Exception:
            pass

    # Harvest dataset items
    ds_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?format=json&clean=true&limit=2500&token={token}"
    items = api_req("GET", ds_url, timeout=60)
    if not isinstance(items, list):
        items = []

    cache_file.write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")
    elapsed = round(time.time() - t0, 1)
    print(f"[APIFY DONE] {bid}: status={status} items={len(items)} usd=${usage_usd:.3f} time={elapsed}s", flush=True)
    return bid, items, {"cached": False, "status": status, "count": len(items), "usd": usage_usd, "elapsed_s": elapsed}


def load_blacklist() -> Tuple[set, set]:
    bl_emails = set()
    bl_companies = set()
    bl_path = BASE_DIR / "BLACKLIST_DO_NOT_CONTACT.json"
    if bl_path.exists():
        for item in json.loads(bl_path.read_text(encoding="utf-8")):
            em = (item.get("email") or "").strip().lower()
            comp = (item.get("empresa") or "").strip().lower()
            if em:
                bl_emails.add(em)
            if comp:
                bl_companies.add(comp)
    return bl_emails, bl_companies


def load_local_enrichment() -> Dict[str, dict]:
    enrich = {}
    for p in glob.glob(str(CORTEXIA_GP_DIR / "*enriquecimiento_local.json")):
        try:
            for it in json.loads(Path(p).read_text(encoding="utf-8")):
                u = (it.get("originalStartUrl") or "").strip().lower().rstrip("/")
                if u:
                    enrich[u] = it
        except Exception:
            pass
    return enrich


def infer_country(raw_cc: str, address: str, default_cc: str = "MX") -> str:
    cc = (raw_cc or "").strip().upper()
    if cc in COUNTRY_META:
        return cc
    low = (address or "").lower()
    if any(k in low for k in ["perú", "peru", "lima", "arequipa", "trujillo", "miraflores", "san isidro"]):
        return "PE"
    if any(k in low for k in ["españa", "spain", "madrid", "barcelona", "valencia", "málaga", "malaga"]):
        return "ES"
    if any(k in low for k in ["argentina", "buenos aires", "caba", "córdoba", "cordoba", "rosario", "palermo"]):
        return "AR"
    if any(k in low for k in ["colombia", "bogotá", "bogota", "medellín", "medellin", "cali", "barranquilla", "cartagena"]):
        return "CO"
    if any(k in low for k in ["méxico", "mexico", "cdmx", "ciudad de méxico", "monterrey", "guadalajara", "cancún", "cancun", "querétaro", "puebla", "mérida", "tijuana", "león"]):
        return "MX"
    if any(k in low for k in ["chile", "santiago", "providencia", "las condes", "viña del mar"]):
        return "CL"
    if any(k in low for k in ["united states", "estados unidos", "florida", "texas", "california", ", fl ", ", tx ", ", ca ", "miami", "orlando", "houston"]):
        return "US"
    return default_cc


def normalize_country_e164(raw_phone: str, cc: str) -> str:
    s = (raw_phone or "").strip()
    if not s:
        return ""
    has_plus = s.startswith("+")
    digits = re.sub(r"\D", "", s)
    if len(digits) < 7 or len(digits) > 15:
        return ""

    dial = COUNTRY_META.get(cc, COUNTRY_META["MX"])["dial"]
    if has_plus:
        return "+" + digits

    # Local formatting fixes by country when missing leading +
    if cc == "US":
        if len(digits) == 10:
            return "+1" + digits
        if len(digits) == 11 and digits.startswith("1"):
            return "+" + digits
    elif cc == "MX":
        if digits.startswith("52") and len(digits) >= 12:
            return "+" + digits
        if len(digits) == 10:
            return "+52" + digits
    elif cc == "CO":
        if digits.startswith("57") and len(digits) >= 12:
            return "+" + digits
        if len(digits) in (7, 10):
            return "+57" + digits
    elif cc == "PE":
        if digits.startswith("51") and len(digits) >= 10:
            return "+" + digits
        if digits.startswith("0"):
            digits = digits.lstrip("0")
        return "+51" + digits
    elif cc == "AR":
        if digits.startswith("54") and len(digits) >= 11:
            return "+" + digits
        if digits.startswith("0"):
            digits = digits.lstrip("0")
        return "+54" + digits
    elif cc == "ES":
        if digits.startswith("34") and len(digits) >= 11:
            return "+" + digits
        return "+34" + digits
    elif cc == "CL":
        if digits.startswith("56") and len(digits) >= 10:
            return "+" + digits
        if digits.startswith("0"):
            digits = digits.lstrip("0")
        return "+56" + digits

    if not digits.startswith(dial):
        return "+" + dial + digits
    return "+" + digits


def is_clean_website(url: str) -> bool:
    u = (url or "").strip().lower()
    if not u or u in ("none", "null", "#"):
        return False
    # Redes sociales / wa.me solos NO cuentan como sitio web propio
    social_only = ["instagram.com", "facebook.com", "fb.com", "wa.me", "linktr.ee", "tiktok.com", "youtube.com", "api.whatsapp.com"]
    return not any(s in u for s in social_only)


def classify_macro_niche(item: dict) -> str:
    search_str = (item.get("searchString") or "").lower()
    cat = (item.get("categoryName") or "").lower()
    title = (item.get("title") or "").lower()
    combined = f"{cat} {title}"

    # Check category/title strong signals first
    if any(w in combined for w in ["abogad", "law ", "legal", "jurídic", "juridic", "attorney", "inmigración", "notar"]):
        return "legal"
    if any(w in combined for w in ["plomer", "fontaner", "destape", "fuga", "plumb"]):
        return "plomeria"
    if any(w in combined for w in ["electric", "iluminación", "tablero eléctrico", "electr"]):
        if "electrodom" not in combined:
            return "electricista"
    if any(w in combined for w in ["aire acondicionado", "climatiz", "hvac", "refrigerac", "minisplit", "mini split"]):
        return "hvac"
    if any(w in combined for w in ["inmobil", "bienes ra", "real estate", "realtor", "propiedad", "constructora", "corredor de"]):
        return "inmobiliaria"
    if any(w in combined for w in ["coach", "mentor", "consultor"]):
        return "coaching"
    if any(w in combined for w in ["academ", "curso", "escuela", "instituto", "capacitac", "formación", "idioma", "talleres"]):
        return "academia"
    if any(w in combined for w in ["capilar", "trasplante", "hair transplant", "alopecia"]):
        return "capilar"
    if any(w in combined for w in ["salón de belleza", "salon de belleza", "peluquer", "estilist", "uñas", "barber", "salon"]):
        return "belleza"
    if any(w in combined for w in ["dent", "odont", "ortodon", "implant"]):
        return "dental"
    if any(w in combined for w in ["estét", "estet", "spa", "dermat", "belleza", "cosmet", "plástic", "plastic", "medspa"]):
        return "estetica"

    # Fallback by Apify search string used to fetch the record
    if "inmobili" in search_str or "real estate" in search_str or "bienes" in search_str:
        return "inmobiliaria"
    if "abogado" in search_str or "lawyer" in search_str or "law firm" in search_str:
        return "legal"
    if "aire acondicionado" in search_str or "hvac" in search_str:
        return "hvac"
    if "plomer" in search_str:
        return "plomeria"
    if "electric" in search_str:
        return "electricista"
    if "coach" in search_str:
        return "coaching"
    if "academia" in search_str or "curso" in search_str or "formación" in search_str or "escuela" in search_str:
        return "academia"
    if "salón de belleza" in search_str or "peluquer" in search_str:
        return "belleza"
    if "dental" in search_str or "dentista" in search_str:
        return "dental"
    if "estét" in search_str:
        return "estetica"
    return "dental"


def build_speech_and_notes(rec: dict) -> Tuple[str, str, str, int]:
    biz = rec["business_name"]
    city = rec["city"] or rec["country_name"]
    cc_meta = COUNTRY_META[rec["country_code"]]
    n_meta = NICHE_META[rec["macro_niche"]]
    has_web = rec["has_web"]
    web = rec["website"]
    rating = rec["rating"]
    reviews = rec["reviews"]
    em_real = rec["real_email"]
    ig_url = rec["instagram"]

    if not has_web:
        diag_short = "🔴 SIN SITIO WEB"
        diag_tag = f"🔴 SIN SITIO WEB · SOLO GOOGLE MAPS ({rating:.1f}★ · {reviews} res.)"
        score = 96 if reviews >= 15 else 92
        pain_hook = (
            f"hoy aparecen en Google Maps ({reviews} reseñas, {rating:.1f}★), pero no tienen un Sitio Web Inteligente propio; "
            f"los clientes que buscan en Google terminan contactando a la competencia"
        )
    elif reviews >= 50:
        diag_short = f"🟢 LÍDER +{reviews} RESEÑAS"
        diag_tag = f"🟢 LÍDER +{reviews} RESEÑAS ({rating:.1f}★) · ESCALA CON IA 24/7"
        score = 93
        pain_hook = (
            f"tienen excelente reputación en Google ({reviews} reseñas, {rating:.1f}★), pero su web actual no atiende ni agenda citas con IA 24/7 "
            f"cuando un cliente escribe de noche o en fin de semana"
        )
    else:
        diag_short = "🟡 WEB SIN IA 24/7"
        diag_tag = f"🟡 TIENE WEB TRADICIONAL · SIN IA 24/7 ({rating:.1f}★ · {reviews} res.)"
        score = 86
        pain_hook = (
            f"vi su web actual en {city}, pero hoy es solo informativa y no tiene una Recepcionista IA 24/7 que cotice y agende directo en WhatsApp"
        )

    m = rec["macro_niche"]
    if m in ("dental", "estetica", "capilar", "belleza"):
        speech = (
            f"«Hola, hablo a {biz} en {city}. Soy [Tu Nombre] de Agencia ProsperIA. Vi en Google que {pain_hook}. "
            f"Les armé una muestra en vivo personalizada de cómo su clínica/salón captura y agenda pacientes automáticamente por WhatsApp las 24 horas. "
            f"¿Me regalas 90 segundos para enseñártela en pantalla?»"
        )
        wa_msg = (
            f"Hola equipo de {biz} 👋 Vi su perfil en Google Maps en {city} ({rating:.1f}★). "
            f"Les preparé una demo en vivo de su Sitio Web Inteligente con Recepcionista IA 24/7 para agendar pacientes directo en WhatsApp sin perder leads fuera de horario. "
            f"¿Te paso el link para que la veas en 1 minuto?"
        )
    elif m in ("hvac", "plomeria", "electricista"):
        speech = (
            f"«Hola, hablo a {biz} en {city}. Soy [Tu Nombre] de Agencia ProsperIA. En emergencias y servicios de {n_meta['label']}, "
            f"el cliente llama a los 3 primeros de Google y contrata al que responde en menos de 60 segundos. Vi que {pain_hook}. "
            f"Les preparé el prototipo en vivo de su web de atención 24/7 que diagnostica la falla en WhatsApp y asigna al técnico al instante. ¿Te la muestro en 1 minuto?»"
        )
        wa_msg = (
            f"Hola {biz} 👋 En servicios urgentes de {n_meta['label']} en {city}, quien responde primero en WhatsApp se queda el servicio. "
            f"Les monté una muestra funcional de Sitio Web Inteligente 24/7 con filtro automático de dirección y tipo de urgencia. ¿Te la comparto?"
        )
    elif m == "inmobiliaria":
        speech = (
            f"«Hola, hablo a {biz} en {city}. Soy [Tu Nombre] de Agencia ProsperIA. Vi sus propiedades en {city} y detecté que {pain_hook}. "
            f"Creamos un Portal Inmobiliario con Agente Pre-calificador IA 24/7 que filtra presupuesto, zona, financiamiento y agenda la cita solo con compradores reales. "
            f"¿Tienes 2 minutos para ver la demo aplicada a su inmobiliaria?»"
        )
        wa_msg = (
            f"Hola {biz} 👋 Vi su inmobiliaria en {city}. Armamos un prototipo con Agente IA 24/7 que pre-califica presupuesto, zona y método de compra por WhatsApp antes de pasarle la cita al asesor. ¿Te envío el enlace?"
        )
    elif m in ("academia", "coaching"):
        speech = (
            f"«Hola, hablo a {biz} en {city}. Soy [Tu Nombre] de Agencia ProsperIA. En academias y cursos, el 70% de los alumnos piden informes de noche o fin de semana y se enfrían antes del lunes. "
            f"Vi que {pain_hook}. Les armé una demo en vivo de cómo un Asesor IA 24/7 responde temarios, precios y cierra inscripciones o citas en automático. ¿La vemos juntos 2 minutos?»"
        )
        wa_msg = (
            f"Hola {biz} 👋 Vimos su perfil en {city}. Creamos una demo de Sitio Web Inteligente para academias que responde programas, costos y agenda citas o inscripciones 24/7 en WhatsApp. ¿Te paso el link?"
        )
    else:  # legal
        speech = (
            f"«Hello / Hola, llamo a la firma {biz} en {city}. Soy [Tu Nombre] de Agencia ProsperIA. Trabajamos con despachos legales en EE. UU. para automatizar la recepción bilingüe de casos 24/7. "
            f"Vi que {pain_hook}. Les preparé una muestra en vivo de cómo su web hace el intake inicial del cliente y agenda la consulta calificada directo en su calendario. ¿Te la muestro 2 minutos?»"
        )
        wa_msg = (
            f"Hola equipo de {biz} 👋 Desarrollamos para firmas en {city} un Sitio Web Inteligente bilingüe con Recepcionista Legal IA 24/7 que realiza el intake del caso y agenda citas calificadas. ¿Les comparto la demo?"
        )

    campaign_label = f"{cc_meta['flag']} {cc_meta['name']} ({city}) | {n_meta['emoji']} {n_meta['label']} | {diag_short}"
    interest_label = f"{n_meta['label']} · {diag_tag}"

    notes_parts = [
        f"🏷️ ORIGEN Y NICHO: {campaign_label}",
        f"🔍 DIAGNÓSTICO DIGITAL: {diag_tag}",
        f"🌐 WEB ACTUAL: {web if web else 'NO TIENE SITIO WEB PROPIO'} | ⭐ GOOGLE: {rating:.1f}★ ({reviews} reseñas)",
    ]
    if em_real:
        notes_parts.append(f"📧 EMAIL DETECTADO: {em_real}")
    if ig_url:
        notes_parts.append(f"📱 INSTAGRAM: {ig_url}")
    if rec.get("address"):
        notes_parts.append(f"📍 DIRECCIÓN: {rec['address']}")
    notes_parts.append(f"\n🎙️ SPEECH TELEFÓNICO (25s):\n{speech}")
    notes_parts.append(f"\n💬 GUION WHATSAPP (1-Clic):\n{wa_msg}")

    return campaign_label, interest_label, "\n".join(notes_parts), score


def normalize_place_item(item: dict, default_cc: str, source_tag: str, enrich_map: dict, bl_emails: set, bl_companies: set) -> Optional[dict]:
    if not isinstance(item, dict):
        return None
    title = (item.get("title") or item.get("Nombre") or item.get("name") or "").strip()
    if not title or len(title) < 2:
        return None
    if title.lower() in bl_companies:
        return None

    addr = (item.get("address") or item.get("formattedAddress") or item.get("Dirección") or "").strip()
    city = (item.get("city") or item.get("neighborhood") or item.get("Ciudad") or item.get("state") or "").strip()
    cc = infer_country(item.get("countryCode") or "", addr or city, default_cc=default_cc)
    if cc not in COUNTRY_META:
        return None

    raw_phone = (item.get("phone") or item.get("phoneUnformatted") or item.get("Teléfono") or "").strip()
    e164 = normalize_country_e164(raw_phone, cc)
    if not e164:
        return None

    web = (item.get("website") or item.get("Sitio Web") or "").strip()
    has_web = is_clean_website(web)
    enr = enrich_map.get(web.lower().rstrip("/"), {}) if web else {}

    real_email = ""
    raw_emails = item.get("emails") or enr.get("emails") or ([] if not item.get("email") else [item.get("email")])
    if isinstance(raw_emails, list) and raw_emails:
        for ce in raw_emails:
            ce_s = str(ce or "").strip().lower()
            if "@" in ce_s and not ce_s.endswith((".png", ".jpg", ".webp")) and ce_s not in INTERNAL_EMAILS and ce_s not in bl_emails:
                real_email = ce_s
                break
    elif isinstance(raw_emails, str) and "@" in raw_emails:
        ce_s = raw_emails.strip().lower()
        if ce_s not in INTERNAL_EMAILS and ce_s not in bl_emails:
            real_email = ce_s

    ig_list = enr.get("instagrams") or []
    instagram = ig_list[0] if isinstance(ig_list, list) and ig_list else ""

    try:
        rating = float(item.get("totalScore") or item.get("Rating_Score") or 4.5)
    except Exception:
        rating = 4.5
    try:
        reviews = int(float(item.get("reviewsCount") or item.get("Reseñas") or 0))
    except Exception:
        reviews = 0

    macro = classify_macro_niche(item)
    if macro not in NICHE_META:
        macro = "dental"

    cc_meta = COUNTRY_META[cc]
    n_meta = NICHE_META[macro]

    rec = {
        "business_name": title,
        "country_code": cc,
        "country_name": cc_meta["name"],
        "timezone": cc_meta["tz"],
        "city": city or cc_meta["name"],
        "address": addr,
        "phone": raw_phone or e164,
        "phone_e164": e164,
        "website": web if has_web else "",
        "has_web": has_web,
        "real_email": real_email,
        "instagram": instagram,
        "rating": rating,
        "reviews": reviews,
        "macro_niche": macro,
        "niche": n_meta["db_niche"],
        "selected_template": n_meta["template"],
        "source_tag": source_tag,
    }
    campaign_label, interest_label, notes, score = build_speech_and_notes(rec)
    rec["source_campaign"] = campaign_label
    rec["interest_primary"] = interest_label
    rec["notes"] = notes
    rec["score"] = score
    return rec


def load_local_cortexia_pool(enrich_map: dict, bl_emails: set, bl_companies: set) -> List[dict]:
    pool = []
    # 1. All raw JSON files
    raw_files = sorted(glob.glob(str(CORTEXIA_GP_DIR / "*_raw.json")))
    for rp in raw_files:
        fname = os.path.basename(rp).lower()
        default_cc = "CO"
        if "chile" in fname:
            default_cc = "CL"
        elif "mexico" in fname:
            default_cc = "MX"
        elif "florida" in fname:
            default_cc = "US"
        try:
            items = json.loads(Path(rp).read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(items, list):
            continue
        for it in items:
            if isinstance(it, dict) and "inmobiliaria" in fname and not it.get("searchString"):
                it["searchString"] = "inmobiliaria bienes raices"
            norm = normalize_place_item(it, default_cc, f"local:{fname}", enrich_map, bl_emails, bl_companies)
            if norm:
                pool.append(norm)

    # 2. Also pull rows from prospeccion_1000_clinicas_master.csv if any extra
    master_csv = CORTEXIA_GP_DIR / "prospeccion_1000_clinicas_master.csv"
    if master_csv.exists():
        country_map = {"Estados Unidos": "US", "México": "MX", "Colombia": "CO", "Chile": "CL"}
        niche_map_csv = {"Dental": "dental", "Estética": "estetica", "Capilar": "capilar"}
        with open(master_csv, encoding="utf-8", errors="ignore") as f:
            for row in csv.DictReader(f):
                cc = country_map.get((row.get("País") or "").strip(), "MX")
                fake_it = {
                    "title": row.get("Nombre", ""),
                    "countryCode": cc,
                    "city": row.get("Ciudad", ""),
                    "address": row.get("Dirección", ""),
                    "phone": row.get("Teléfono", "") or row.get("WhatsApp", ""),
                    "website": row.get("Sitio Web", ""),
                    "email": row.get("Email", ""),
                    "totalScore": row.get("Rating_Score", 4.7),
                    "reviewsCount": row.get("Reseñas", 0),
                    "categoryName": row.get("Categoría", "") or row.get("Nicho", ""),
                    "searchString": niche_map_csv.get(row.get("Nicho", ""), "dental"),
                }
                norm = normalize_place_item(fake_it, cc, "local:clinicas_master_csv", enrich_map, bl_emails, bl_companies)
                if norm:
                    if row.get("Instagram") and not norm["instagram"]:
                        norm["instagram"] = row["Instagram"].strip()
                    pool.append(norm)
    return pool


def main():
    APIFY_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    SEED_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    token = load_apify_token()
    bl_emails, bl_companies = load_blacklist()
    enrich_map = load_local_enrichment()

    # Step 1: Run all 11 Apify batches concurrently
    t_start = time.time()
    apify_results: Dict[str, List[dict]] = {}
    apify_stats: Dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=11) as ex:
        futs = {ex.submit(run_single_apify_batch, b, token): b for b in APIFY_BATCHES}
        for fut in as_completed(futs):
            b = futs[fut]
            try:
                bid, items, stats = fut.result()
                apify_results[bid] = items
                apify_stats[bid] = stats
            except Exception as exc:
                print(f"[APIFY ERROR] {b['id']}: {exc}", flush=True)
                apify_results[b["id"]] = []
                apify_stats[b["id"]] = {"error": str(exc), "count": 0, "usd": 0.0}

    total_usd = sum(s.get("usd", 0.0) for s in apify_stats.values())
    print(f"\n=== APIFY FASE COMPLETADA en {time.time() - t_start:.1f}s | Gasto acumulado aprox: ${total_usd:.2f} USD ===", flush=True)

    # Step 2: Normalize & deduplicate ALL places (Apify first for freshest geo/niches, then local Cortexia)
    seen_phones = set()
    all_records: List[dict] = []

    def add_record(r: Optional[dict]):
        if not r:
            return
        ph = r["phone_e164"]
        if ph in seen_phones:
            return
        # Avoid toll-free 800 unless needed? Skip obvious invalid repeated zeroes
        if ph.endswith("000000"):
            return
        seen_phones.add(ph)
        all_records.append(r)

    for b in APIFY_BATCHES:
        bid = b["id"]
        cc = b["country"]
        for it in apify_results.get(bid, []):
            add_record(normalize_place_item(it, cc, f"apify:{bid}", enrich_map, bl_emails, bl_companies))

    local_pool = load_local_cortexia_pool(enrich_map, bl_emails, bl_companies)
    for r in local_pool:
        add_record(r)

    # Sort all_records by quality score desc, no-website priority, reviews desc
    all_records.sort(key=lambda x: (x["score"], not x["has_web"], x["reviews"], bool(x["real_email"])), reverse=True)

    counts_cn = Counter((r["country_code"], r["macro_niche"]) for r in all_records)
    print(f"TOTAL_UNIQUE_DEDUPLICATED_LEADS: {len(all_records)}")
    for k, v in counts_cn.most_common(40):
        print(f"  {v:4d} | {k[0]} | {k[1]}")

    # Step 3: Allocate 1,000 leads per Closer cleanly without cross-closer duplicates
    # Rules: list of (countries_set, macro_niches_set, target_count) priority slices per closer
    CLOSER_QUOTAS = [
        {
            "email": "claudiniosan@yahoo.com.ar",
            "name": "Claudio A. Sánchez",
            "target": 1000,  # database.py keeps existing 163 and tops up to 1,000
            "slices": [
                ({"CL"}, {"dental", "estetica", "capilar", "belleza"}, 800),
                ({"US"}, {"dental", "estetica", "capilar"}, 200),
            ],
            "fallback_countries": {"CL", "US", "MX", "CO"},
            "fallback_niches": {"dental", "estetica", "capilar", "belleza", "inmobiliaria"},
        },
        {
            "email": "diegoarriondo03@gmail.com",
            "name": "Diego Arriondo",
            "target": 1000,
            "slices": [
                ({"PE"}, {"electricista"}, 250),
                ({"PE"}, {"dental"}, 250),
                ({"PE"}, {"inmobiliaria"}, 250),
                ({"PE"}, {"academia", "coaching"}, 250),
            ],
            "fallback_countries": {"PE"},
            "fallback_niches": {"dental", "estetica", "belleza", "inmobiliaria", "academia", "electricista", "coaching"},
        },
        {
            "email": "tanyah.unity@gmail.com",
            "name": "Tanya Headley Mullings",
            "target": 1000,
            "slices": [
                ({"US"}, {"legal"}, 350),
                ({"US"}, {"inmobiliaria"}, 350),
                ({"US"}, {"dental", "estetica", "capilar"}, 300),
            ],
            "fallback_countries": {"US"},
            "fallback_niches": {"legal", "inmobiliaria", "dental", "estetica", "capilar"},
        },
        {
            "email": "loremrodriguezafb@gmail.com",
            "name": "Lorena Rodríguez",
            "target": 1000,
            "slices": [
                ({"MX"}, {"plomeria"}, 350),
                ({"MX"}, {"hvac"}, 350),
                ({"MX"}, {"dental", "estetica", "capilar"}, 300),
            ],
            "fallback_countries": {"MX"},
            "fallback_niches": {"plomeria", "hvac", "dental", "estetica", "capilar"},
        },
        {
            "email": "bruno.hernan.espinosa1694@gmail.com",
            "name": "Bruno Espinoza",
            "target": 1000,
            "slices": [
                ({"MX", "CO"}, {"coaching"}, 400),
                ({"MX", "CO"}, {"academia"}, 600),
            ],
            "fallback_countries": {"MX", "CO"},
            "fallback_niches": {"academia", "coaching"},
        },
        {
            "email": "wendyleiva59@gmail.com",
            "name": "Wendy Leiva",
            "target": 1000,
            "slices": [
                ({"AR"}, {"academia", "coaching"}, 300),
                ({"AR"}, {"inmobiliaria"}, 250),
                ({"MX"}, {"academia", "coaching"}, 250),
                ({"MX"}, {"inmobiliaria"}, 200),
            ],
            "fallback_countries": {"AR", "MX"},
            "fallback_niches": {"academia", "coaching", "inmobiliaria"},
        },
        {
            "email": "sheille.perez@gmail.com",
            "name": "Sheille Pérez",
            "target": 1000,
            "slices": [
                ({"ES"}, {"inmobiliaria", "dental", "estetica", "belleza"}, 400),
                ({"AR"}, {"inmobiliaria", "dental", "estetica", "belleza"}, 350),
                ({"PE"}, {"dental", "estetica", "belleza", "inmobiliaria"}, 250),
            ],
            "fallback_countries": {"PE", "AR", "ES"},
            "fallback_niches": {"belleza", "estetica", "dental", "inmobiliaria"},
        },
        {
            "email": "laverdaderafuerza02@gmail.com",
            "name": "Agustín García",
            "target": 1000,
            "slices": [
                ({"PE"}, {"inmobiliaria", "dental", "academia"}, 250),
                ({"ES"}, {"inmobiliaria", "dental", "academia"}, 250),
                ({"CO"}, {"inmobiliaria", "dental", "academia"}, 250),
                ({"MX"}, {"inmobiliaria", "dental", "academia"}, 250),
            ],
            "fallback_countries": {"PE", "ES", "CO", "MX"},
            "fallback_niches": {"inmobiliaria", "dental", "academia", "coaching", "estetica"},
        },
        {
            "email": "digitalblups@gmail.com",
            "name": "Jhonatan Rivero",
            "target": 1000,
            "slices": [
                ({"MX", "CO"}, {"hvac"}, 400),
                ({"MX", "CO"}, {"inmobiliaria"}, 300),
                ({"MX", "CO"}, {"dental", "estetica", "capilar"}, 300),
            ],
            "fallback_countries": {"MX", "CO"},
            "fallback_niches": {"hvac", "inmobiliaria", "dental", "estetica", "capilar"},
        },
        {
            "email": "sergiotorales608@gmail.com",
            "name": "Sergio Torales",
            "target": 1000,
            "slices": [
                ({"MX", "CO"}, {"academia", "coaching"}, 400),
                ({"MX", "CO", "US"}, {"estetica", "belleza", "dental"}, 600),
            ],
            "fallback_countries": {"MX", "CO", "US", "ES"},
            "fallback_niches": {"dental", "estetica", "belleza", "academia", "coaching", "capilar"},
        },
        {
            "email": "cinthyapenida0@gmail.com",
            "name": "Cinthya Penida",
            "target": 1000,
            "slices": [
                ({"MX"}, {"dental", "estetica", "capilar"}, 400),
                ({"CO"}, {"dental", "estetica", "capilar"}, 300),
                ({"US"}, {"dental", "estetica", "capilar"}, 300),
            ],
            "fallback_countries": {"MX", "CO", "US"},
            "fallback_niches": {"dental", "estetica", "capilar", "belleza"},
        },
    ]

    used_indices = set()
    assigned_by_closer: Dict[str, List[dict]] = {q["email"]: [] for q in CLOSER_QUOTAS}

    def take_matching(closer_email: str, countries: set, niches: set, limit: int):
        bucket = assigned_by_closer[closer_email]
        taken = 0
        for idx, rec in enumerate(all_records):
            if idx in used_indices:
                continue
            if len(bucket) >= 1000 or taken >= limit:
                break
            if rec["country_code"] in countries and rec["macro_niche"] in niches:
                used_indices.add(idx)
                bucket.append(rec)
                taken += 1

    # Pass 1: Strict planned slices
    for q in CLOSER_QUOTAS:
        for countries_s, niches_s, lim in q["slices"]:
            take_matching(q["email"], countries_s, niches_s, lim)

    # Pass 2: Same closer allowed countries & niches
    for q in CLOSER_QUOTAS:
        rem = q["target"] - len(assigned_by_closer[q["email"]])
        if rem > 0:
            take_matching(q["email"], q["fallback_countries"], q["fallback_niches"], rem)

    # Pass 3: Same closer allowed niches in any country
    for q in CLOSER_QUOTAS:
        rem = q["target"] - len(assigned_by_closer[q["email"]])
        if rem > 0:
            take_matching(q["email"], set(COUNTRY_META.keys()), q["fallback_niches"], rem)

    # Pass 4: Any remaining high-quality lead so every single closer reaches 1,000 leads cleanly
    for q in CLOSER_QUOTAS:
        rem = q["target"] - len(assigned_by_closer[q["email"]])
        if rem > 0:
            take_matching(q["email"], set(COUNTRY_META.keys()), set(NICHE_META.keys()), rem)

    # Serialize final compressed payload for database.py
    final_leads = []
    per_closer_report = {}
    for q in CLOSER_QUOTAS:
        em = q["email"]
        bucket = assigned_by_closer[em]
        by_cn = Counter((r["country_code"], r["macro_niche"]) for r in bucket)
        per_closer_report[em] = {
            "name": q["name"],
            "count": len(bucket),
            "top_breakdown": {f"{k[0]}_{k[1]}": v for k, v in by_cn.most_common(8)},
        }
        for i, r in enumerate(bucket):
            ph_hash = hashlib.md5(r["phone_e164"].encode()).hexdigest()[:10]
            email_val = r["real_email"] or f"prospecto_{ph_hash}@sin-correo.local"
            final_leads.append({
                "name": r["business_name"],
                "full_name": r["business_name"],
                "business_name": r["business_name"],
                "email": email_val,
                "phone": r["phone"],
                "phone_e164": r["phone_e164"],
                "owner_id": em,
                "niche": r["niche"],
                "macro_niche": r["macro_niche"],
                "country": r["country_name"],
                "country_code": r["country_code"],
                "timezone": r["timezone"],
                "source": "apify_sprint_nov18",
                "source_channel": f"Google Maps ({r['country_name']})",
                "source_campaign": r["source_campaign"],
                "interest_primary": r["interest_primary"],
                "selected_template": r["selected_template"],
                "score": r["score"],
                "notes": r["notes"],
            })

    payload = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_leads": len(final_leads),
        "apify_stats": apify_stats,
        "apify_total_usd": round(total_usd, 3),
        "per_closer_report": per_closer_report,
        "leads": final_leads,
    }

    with gzip.open(SEED_OUTPUT_PATH, "wt", encoding="utf-8") as gz:
        json.dump(payload, gz, ensure_ascii=False)

    summary = {k: v for k, v in payload.items() if k != "leads"}
    SUMMARY_OUTPUT_PATH.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    seed_mb = SEED_OUTPUT_PATH.stat().st_size / 1024 / 1024
    print(f"\n✅ SEED GENERATED: {SEED_OUTPUT_PATH} ({seed_mb:.2f} MB), total_leads={len(final_leads)}")
    for em, rep in per_closer_report.items():
        print(f"   - {rep['name']:24s} ({em:36s}) => {rep['count']} leads | {rep['top_breakdown']}")


if __name__ == "__main__":
    main()

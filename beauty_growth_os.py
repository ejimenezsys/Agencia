"""Mini-Sistema Web independiente para la vertical Beauty Growth & Business System.

100% aislado de los usuarios (/login) y leads (/dashboard) de Sitios Web Inteligentes.
Permite a Jhonkelwins David Becerra Cañas (Admin) y sus 3 Setters:
  - Trabajar la base unificada de Instagram con descripciones/biografías completas,
    seguidores/seguidos, foto de perfil, links de agenda, ubicación, correos y teléfonos E.164.
  - Filtrar sobre la marcha por Setter, etapa (14 etapas), nicho, país/región,
    plataforma de agenda, seguidores mínimos, presencia de teléfono/bio y estado GHL.
  - Repartir equitativamente la base de datos entre los 3 Setters y actualizar sus correos reales.
  - Importar nuevos archivos Excel/CSV (.xlsx/.csv) preservando todas las descripciones.
  - Opción A: Sincronizar bajo demanda o al avanzar de etapa hacia GoHighLevel
    (subcuenta V8tM5xk6xl15wKhbQS0p, pipeline BBQlDFhNVE0NRmKNTMS2 de 14 etapas).
"""
import csv
import gzip
import io
import json
import os
import re
import uuid
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, Response, UploadFile, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import Column, Float, Integer, String, func, or_
from sqlalchemy.orm import Session

from database import (
    BEAUTY_GROWTH_PIPELINE_STAGES,
    Base,
    IntegrationSetting,
    OFFER_CATALOG,
    SessionLocal,
    engine,
    hash_password,
    normalize_email,
    verify_password,
)
from ghl_client import (
    BEAUTY_DEFAULT_USER_ID,
    BEAUTY_LOCATION_ID,
    BEAUTY_PIPELINE_ID,
    BEAUTY_PIPELINE_NAME,
    check_beauty_ghl_connection,
    sync_beauty_growth_ig_lead_to_ghl,
)

BASE_DIR = Path(__file__).resolve().parent
SEED_CANDIDATE_PATHS = [
    BASE_DIR / "seeds" / "beauty_growth_ig_seed_3635.json.gz",
    BASE_DIR / "seeds" / "beauty_growth_ig_seed_3635.json",
    BASE_DIR / "data" / "beauty_growth_ig_seed_3635.json.gz",
    BASE_DIR / "data" / "beauty_growth_ig_seed_3635.json",
]

BG_COOKIE_NAME = "bg_auth_token"

GARBAGE_TOKENS = {
    "",
    "<<not-applicable>>",
    "not-applicable",
    "#error!",
    "#n/a",
    "#value!",
    "#ref!",
    "null",
    "none",
    "n/a",
    "na",
    "nan",
    "undefined",
    "-",
}

BEAUTY_NICHE_RE = re.compile(
    r"(beauty|belleza|salon|sal[oó]n|spa|nail|u[ñn]as|unas|lash|pesta[ñn]a|pestana|brow|ceja|"
    r"estetic|est[ée]tic|hair|pelo|cabello|peluquer|barber|makeup|maquillaje|skin|piel|facial|"
    r"cosmet|wax|depil|medspa|klinik|clinic|cl[ií]nica|botox|laser|l[áa]ser|microblading|pmu|"
    r"stylist|estilista|balayage|keratin|manicure|pedicure|acrilic|acr[ií]lic|glam|masaje|"
    r"massage|micropig|filler|maderoterapia|hydra|esika|yanbal|natura|mary\s*kay|skincare|"
    r"facialist|esthetician|studio.*hair|hair.*studio|permanent\s*makeup|extensiones)",
    re.IGNORECASE,
)

SUPPLIER_B2B_RE = re.compile(
    r"(manufacturer|wholesale\s+supplier|factory|oem|odm|tweezers|surgical\s+instruments|"
    r"exporter|private\s+label\s+manufacturer|sialkot|qingdao|guangzhou|shenzhen)",
    re.IGNORECASE,
)

BEAUTY_PACKAGE_PRICES = {
    "BEAUTY_BOOST_1499": 1499.0,
    "BEAUTY_ELEVATE_2499": 2499.0,
    "BEAUTY_EMPIRE_3499": 3499.0,
    "BEAUTY_HIGHTICKET_5000": 5000.0,
}

REGION_CHOICES = [
    "USA / PR",
    "Chile",
    "México",
    "Colombia",
    "España",
    "LATAM / Otros",
    "Proveedores Asia",
]

NICHE_CHOICES = [
    "Belleza / Estética / Salón",
    "Otros Giros Comerciales",
    "Proveedor B2B / Insumos",
]

PLATFORM_CHOICES = [
    "Booksy",
    "GlossGenius",
    "Square",
    "Vagaro",
    "Fresha",
    "Otro Sistema Agenda",
    "Linktree / Bio",
    "WhatsApp Directo",
    "Red Social",
    "Web Propia",
    "Sin Web",
]


# ─── MODELOS ORM EXCLUSIVOS BEAUTY GROWTH ────────────────────────────────────

class BeautyGrowthUser(Base):
    """Usuarios exclusivos del Mini-Sistema Beauty Growth (Admins y los 3 Setters)."""
    __tablename__ = "beauty_growth_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="setter", nullable=False)        # "admin" | "setter"
    setter_slot = Column(Integer, default=0, nullable=False, index=True)  # 0=Admin, 1..3=Setters
    phone = Column(String, default="", nullable=True)
    ghl_user_id = Column(String, default="", nullable=True)
    is_active = Column(Integer, default=1, nullable=False)
    created_at = Column(String, default="", nullable=False)
    last_login_at = Column(String, default="", nullable=True)


class BeautyGrowthSession(Base):
    """Sesiones aisladas del Mini-Sistema Beauty Growth."""
    __tablename__ = "beauty_growth_sessions"

    token = Column(String, primary_key=True, index=True)
    email = Column(String, nullable=False, index=True)
    created_at = Column(String, nullable=False)


class BeautyGrowthLead(Base):
    """Base de datos unificada de Instagram + CRM comercial para Beauty Growth."""
    __tablename__ = "beauty_growth_leads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ig_username = Column(String, unique=True, index=True, nullable=False)
    ig_profile_url = Column(String, default="", nullable=True)
    ig_profile_pic_url = Column(String, default="", nullable=True)
    is_business = Column(Integer, default=0, nullable=False)
    followers_count = Column(Integer, default=0, nullable=False, index=True)
    following_count = Column(Integer, default=0, nullable=False)

    full_name = Column(String, default="", nullable=True)
    first_name = Column(String, default="", nullable=True)
    last_name = Column(String, default="", nullable=True)
    email_primary = Column(String, default="", nullable=True, index=True)
    email_secondary = Column(String, default="", nullable=True)
    phone_raw = Column(String, default="", nullable=True)
    phone_e164 = Column(String, default="", nullable=True, index=True)

    biography = Column(String, default="", nullable=True)
    website_url = Column(String, default="", nullable=True)
    booking_platform = Column(String, default="Sin Web", nullable=True, index=True)
    location_raw = Column(String, default="", nullable=True)
    city = Column(String, default="", nullable=True)
    country_region = Column(String, default="LATAM / Otros", nullable=True, index=True)
    niche_category = Column(String, default="Belleza / Estética / Salón", nullable=True, index=True)

    pipeline_stage = Column(String, default="1. Prospecto identificado", nullable=False, index=True)
    assigned_setter_slot = Column(Integer, default=1, nullable=False, index=True)
    assigned_setter_email = Column(String, default="", nullable=True, index=True)
    assigned_setter_name = Column(String, default="", nullable=True)

    offer_package = Column(String, default="BEAUTY_ELEVATE_2499", nullable=True)
    quoted_amount = Column(Float, default=0.0, nullable=True)
    ai_diagnostic_note = Column(String, default="", nullable=True)
    setter_notes = Column(String, default="", nullable=True)
    source_file = Column(String, default="", nullable=True)

    ghl_synced = Column(Integer, default=0, nullable=False, index=True)
    ghl_contact_id = Column(String, default="", nullable=True)
    ghl_opportunity_id = Column(String, default="", nullable=True)
    last_touch_at = Column(String, default="", nullable=True)
    created_at = Column(String, default="", nullable=False)


# ─── NORMALIZADORES Y PARSER EXCEL/CSV COMPARTIDO ────────────────────────────

def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _clean_text(val: Any) -> str:
    if val is None:
        return ""
    s = str(val).replace("\r\n", "\n").replace("\r", "\n").strip()
    if s.lower() in GARBAGE_TOKENS:
        return ""
    return s


def _clean_int(val: Any) -> int:
    s = _clean_text(val)
    if not s:
        return 0
    try:
        return max(0, int(float(s.replace(",", ""))))
    except (ValueError, TypeError):
        digits = re.sub(r"\D", "", s)
        return int(digits) if digits else 0


def _clean_emails(raw_val: Any) -> Tuple[str, str]:
    s = _clean_text(raw_val)
    if not s:
        return "", ""
    tokens = re.split(r"[\s,;]+", s)
    unique_valid: List[str] = []
    seen = set()
    for tok in tokens:
        cand = tok.strip().strip("<>\"'()").lower()
        if not cand or cand in GARBAGE_TOKENS:
            continue
        if "@" in cand and "." in cand.split("@")[-1] and cand not in seen:
            seen.add(cand)
            unique_valid.append(cand)
    primary = unique_valid[0] if unique_valid else ""
    secondary = ", ".join(unique_valid[1:4]) if len(unique_valid) > 1 else ""
    return primary, secondary


def _parse_numeric_phone_string(raw_val: Any) -> str:
    s = _clean_text(raw_val)
    if not s:
        return ""
    # Convierte notación científica de Excel (ej. 3.002791564E9) sin añadir dígitos falsos
    if re.match(r"^\d+(\.\d+)?[eE]\+?\d+$", s):
        try:
            d = Decimal(s)
            return str(int(d.to_integral_value()))
        except (InvalidOperation, ValueError):
            pass
    if re.match(r"^\d+\.0+$", s):
        return s.split(".", 1)[0]
    return s


def normalize_beauty_phone(
    raw_phone: str,
    phone_ext: str = "",
    location_hint: str = "",
) -> Tuple[str, str]:
    """Devuelve (phone_raw_limpio, phone_e164) manejando notación científica y códigos de país."""
    cleaned_raw = _parse_numeric_phone_string(raw_phone)
    ext_digits = re.sub(r"\D", "", _clean_text(phone_ext))
    if not cleaned_raw:
        return "", ""

    digits = re.sub(r"\D", "", cleaned_raw)
    if len(digits) < 7 or len(digits) > 16:
        return cleaned_raw, ""

    loc = (location_hint or "").lower()
    if cleaned_raw.startswith("+"):
        return cleaned_raw, "+" + digits

    if ext_digits and not digits.startswith(ext_digits):
        return cleaned_raw, "+" + ext_digits + digits

    # Detección por prefijo internacional ya incluido (11-13 dígitos)
    if len(digits) == 11 and digits.startswith("1"):
        return cleaned_raw, "+" + digits
    if len(digits) in (11, 12, 13) and (
        digits.startswith("56")
        or digits.startswith("57")
        or digits.startswith("52")
        or digits.startswith("54")
        or digits.startswith("55")
        or digits.startswith("58")
        or digits.startswith("34")
        or digits.startswith("51")
        or digits.startswith("92")
        or digits.startswith("86")
        or digits.startswith("351")
        or digits.startswith("506")
        or digits.startswith("507")
        or digits.startswith("593")
        or digits.startswith("595")
        or digits.startswith("598")
    ):
        return cleaned_raw, "+" + digits

    # 9 dígitos móviles (Chile, España, Perú)
    if len(digits) == 9:
        if digits.startswith("9") and any(k in loc for k in ("chile", "santiago", "temuco", "viña", "vina", "concepcion", "concepción", "valparaiso", "valparaíso", "serena", "chillan", "chillán", "montt", "antofagasta", "talca", "rancagua", "osorno", "iquique", "angeles")):
            return cleaned_raw, "+56" + digits
        if digits[0] in ("6", "7") and any(k in loc for k in ("spain", "españa", "espana", "madrid", "barcelona", "valencia", "sevilla", "malaga", "málaga", "bilbao")):
            return cleaned_raw, "+34" + digits
        if digits.startswith("9") and any(k in loc for k in ("peru", "perú", "lima", "arequipa")):
            return cleaned_raw, "+51" + digits
        if digits.startswith("9"):
            return cleaned_raw, "+56" + digits

    # 10 dígitos (Colombia 3xx, México, Argentina o USA/PR/RD)
    if len(digits) == 10:
        if digits.startswith("3") and any(k in loc for k in ("colombia", "bogota", "bogotá", "medellin", "medellín", "cali", "barranquilla", "cartagena", "bucaramanga", "pereira", "cucuta", "cúcuta")):
            return cleaned_raw, "+57" + digits
        if any(k in loc for k in ("mexico", "méxico", "cdmx", "puebla", "monterrey", "guadalajara", "tijuana", "cancun", "cancún", "merida", "mérida", "queretaro", "querétaro", "toluca", "leon", "león")):
            return cleaned_raw, "+52" + digits
        if any(k in loc for k in ("chile", "santiago")):
            return cleaned_raw, "+56" + digits
        return cleaned_raw, "+1" + digits

    return cleaned_raw, "+" + digits


def detect_booking_platform(raw_url: str) -> Tuple[str, str]:
    val = _clean_text(raw_url)
    if not val:
        return "", "Sin Web"
    norm_url = val if re.match(r"^https?://", val, re.IGNORECASE) else f"https://{val}"
    low = norm_url.lower()
    if "booksy.com" in low:
        return norm_url, "Booksy"
    if "glossgenius.com" in low:
        return norm_url, "GlossGenius"
    if "squareup.com" in low or "square.site" in low:
        return norm_url, "Square"
    if "vagaro.com" in low:
        return norm_url, "Vagaro"
    if "fresha.com" in low:
        return norm_url, "Fresha"
    if any(k in low for k in ("joinblvd", "zenoti", "mindbody", "acuityscheduling", "calendly", "setmore", "mangomint", "schedulicity", "styleseat", "phorest", "timely", "agendapro")):
        return norm_url, "Otro Sistema Agenda"
    if any(k in low for k in ("wa.me/", "wa.link/", "api.whatsapp.com")):
        return norm_url, "WhatsApp Directo"
    if any(k in low for k in ("linktr.ee", "beacons.ai", "bio.site", "instabio.cc", "taplink", "solo.to", "campsite.bio", "stan.store", "canva.site", "milkshake.app", "hoo.be", "snipfeed", "komi.io", "allinbeautyinstitute.com/quicklinks", "quicklinks")):
        return norm_url, "Linktree / Bio"
    if any(k in low for k in ("instagram.com", "facebook.com", "tiktok.com", "fb.com", "youtube.com")):
        return norm_url, "Red Social"
    return norm_url, "Web Propia"


def classify_country_region(location_raw: str, phone_e164: str, bio: str = "") -> str:
    loc = (location_raw or "").lower()
    bio_l = (bio or "").lower()
    blob = f"{loc} {bio_l}"
    ph = (phone_e164 or "").strip()

    if any(k in loc for k in ("sialkot", "punjab", "pakistan", "pakistán", "qingdao", "shandong", "guangzhou", "shenzhen", "yiwu", "china", "india", "delhi", "mumbai")):
        return "Proveedores Asia"

    us_loc_tokens = (
        "florida", "miami", "hialeah", "doral", "coral gables", "kendall", "key biscayne",
        "brickell", "aventura", "homestead", "west palm beach", "palm beach", "boca raton",
        "fort lauderdale", "hollywood fl", "orlando", "kissimmee", "tampa", "jacksonville",
        "naples", "texas", "houston", "dallas", "austin", "san antonio", "el paso", "katy",
        "plano", "fort worth", "new york", "brooklyn", "manhattan", "queens", "bronx",
        "california", "los angeles", "san diego", "san francisco", "nevada", "las vegas",
        "illinois", "chicago", "indiana", "georgia", "atlanta", "arizona", "phoenix",
        "new jersey", "north carolina", "charlotte", "virginia", "boston", "massachusetts",
        "puerto rico", "san juan", "bayamon", "bayamón", "ponce", "caguas", "carolina pr",
        "united states", "estados unidos", " usa", "fl,", "tx,", " fl", " tx", " ny", " ca", " pr",
    )
    if any(k in loc for k in us_loc_tokens):
        return "USA / PR"

    if ph.startswith("+56") or any(k in loc for k in ("chile", "santiago", "temuco", "viña", "vina", "valparaiso", "valparaíso", "concepcion", "concepción", "chillan", "chillán", "puerto montt", "la serena", "punta arenas", "antofagasta", "rancagua", "talca", "osorno", "iquique", "los angeles, chile", "los ángeles, chile", "curico", "curicó")):
        return "Chile"

    if ph.startswith("+52") or any(k in loc for k in ("mexico", "méxico", "cdmx", "puebla", "monterrey", "guadalajara", "tijuana", "cancun", "cancún", "merida", "mérida", "queretaro", "querétaro", "toluca", "chihuahua", "jalisco", "nuevo leon", "nuevo león")):
        return "México"

    if ph.startswith("+57") or any(k in loc for k in ("colombia", "bogota", "bogotá", "medellin", "medellín", "cali", "barranquilla", "cartagena", "bucaramanga", "pereira", "cucuta", "cúcuta", "envigado", "santa marta")):
        return "Colombia"

    if ph.startswith("+34") or any(k in loc for k in ("spain", "españa", "espana", "madrid", "barcelona", "valencia", "sevilla", "malaga", "málaga", "bilbao", "zaragoza", "alicante")):
        return "España"

    if any(k in loc for k in ("dominicana", "santo domingo", "santiago de los caballeros", "peru", "perú", "lima", "argentina", "buenos aires", "venezuela", "caracas", "maracaibo", "ecuador", "quito", "guayaquil", "panama", "panamá", "costa rica", "san jose", "san josé", "uruguay", "montevideo", "guatemala", "el salvador", "honduras", "bolivia", "paraguay", "portugal", "lisbon", "brazil", "brasil", "sao paulo", "rio de janeiro", "canada", "canadá", "toronto", "montreal", "united kingdom", "london")):
        return "LATAM / Otros"

    # Si no hay ubicación explícita, usar prefijo telefónico + señales en bio
    if ph.startswith("+1787") or ph.startswith("+1939"):
        return "USA / PR"
    if ph.startswith("+1809") or ph.startswith("+1829") or ph.startswith("+1849"):
        return "LATAM / Otros"
    if ph.startswith("+1"):
        if any(k in bio_l for k in ("república dominicana", "republica dominicana", "santo domingo", "desde rd", "en rd", "punta cana")):
            return "LATAM / Otros"
        return "USA / PR"
    if any(k in blob for k in ("miami", "houston", "orlando", "dallas", "florida", "texas", "puerto rico", "🇺🇸", "🇵🇷")):
        return "USA / PR"
    if "🇨🇱" in blob or "chile" in blob:
        return "Chile"
    if "🇲🇽" in blob or "mexico" in blob or "méxico" in blob:
        return "México"
    if "🇨🇴" in blob or "colombia" in blob:
        return "Colombia"
    if "🇪🇸" in blob or "españa" in blob:
        return "España"
    return "LATAM / Otros"


def classify_niche_category(
    username: str,
    full_name: str,
    biography: str,
    website_url: str,
    country_region: str,
) -> str:
    blob = " ".join(x for x in [username, full_name, biography, website_url] if x)
    if country_region == "Proveedores Asia" or SUPPLIER_B2B_RE.search(blob):
        return "Proveedor B2B / Insumos"
    if BEAUTY_NICHE_RE.search(blob):
        return "Belleza / Estética / Salón"
    return "Otros Giros Comerciales"


def _extract_city(location_raw: str) -> str:
    loc = _clean_text(location_raw)
    if not loc:
        return ""
    if "," in loc:
        return loc.split(",", 1)[0].strip()
    return loc


def _extract_xlsx_rows(raw_bytes: bytes) -> List[List[str]]:
    """Lee archivos .xlsx usando únicamente librería estándar (sin requerir openpyxl/pandas)."""
    ns = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    all_rows: List[List[str]] = []
    with zipfile.ZipFile(io.BytesIO(raw_bytes)) as z:
        strings: List[str] = []
        if "xl/sharedStrings.xml" in z.namelist():
            root = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in root.findall("main:si", ns):
                strings.append("".join(t.text or "" for t in si.findall(".//main:t", ns)))

        sheet_names = sorted(
            [n for n in z.namelist() if re.match(r"^xl/worksheets/sheet\d+\.xml$", n)],
            key=lambda p: int(re.search(r"sheet(\d+)\.xml$", p).group(1)),
        )
        for sh_path in sheet_names:
            sroot = ET.fromstring(z.read(sh_path))
            for row in sroot.findall(".//main:row", ns):
                rdict: Dict[int, str] = {}
                max_col = 0
                for c in row.findall("main:c", ns):
                    ref = c.attrib.get("r", "")
                    col_idx = 0
                    for ch in ref:
                        if ch.isalpha():
                            col_idx = col_idx * 26 + (ord(ch.upper()) - 64)
                    if col_idx == 0:
                        col_idx = max_col + 1
                    max_col = max(max_col, col_idx)
                    t = c.attrib.get("t")
                    v_el = c.find("main:v", ns)
                    is_el = c.find("main:is", ns)
                    val = ""
                    if t == "s" and v_el is not None and v_el.text is not None:
                        sidx = int(v_el.text)
                        val = strings[sidx] if 0 <= sidx < len(strings) else ""
                    elif t == "inlineStr" and is_el is not None:
                        val = "".join(x.text or "" for x in is_el.findall(".//main:t", ns))
                    elif v_el is not None and v_el.text is not None:
                        val = v_el.text
                    rdict[col_idx] = (val or "").strip()
                if any(rdict.values()):
                    row_list = [rdict.get(i, "") for i in range(1, max(max_col, 15) + 1)]
                    all_rows.append(row_list)
    return all_rows


def _extract_csv_rows(raw_bytes: bytes) -> List[List[str]]:
    text = ""
    for enc in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            text = raw_bytes.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    if not text:
        return []
    first_line = text.splitlines()[0] if text.splitlines() else ""
    delimiter = ";" if first_line.count(";") > first_line.count(",") else ","
    reader = csv.reader(io.StringIO(text), delimiter=delimiter)
    return [[cell.strip() for cell in row] for row in reader if any(cell.strip() for cell in row)]


def _normalize_header_token(h: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (h or "").strip().lower())


def _is_header_row(row: List[str]) -> bool:
    if not row:
        return False
    first = _normalize_header_token(row[0])
    second = _normalize_header_token(row[1] if len(row) > 1 else "")
    return first in ("username", "name", "usuario", "igusername", "account") and second in (
        "firstname", "fullname", "nombre", "nombrecompleto", "email", "correo"
    )


def _derive_ig_identity(raw_user: str, raw_profile_url: str, raw_full_name: str) -> Tuple[str, str, str]:
    """Obtiene (ig_username_unico, ig_profile_url, full_name_limpio) preservando handles reales."""
    u_raw = _clean_text(raw_user).lstrip("@")
    url_raw = _clean_text(raw_profile_url)
    full_raw = _clean_text(raw_full_name)

    extracted_from_url = ""
    if url_raw:
        m = re.search(r"instagram\.com/([^/?#\s]+)", url_raw, re.IGNORECASE)
        if m:
            extracted_from_url = m.group(1).strip().strip("/").lstrip("@")

    if extracted_from_url and extracted_from_url.lower() not in ("p", "reel", "explore", "stories"):
        username = extracted_from_url.lower()
        profile_url = url_raw if url_raw.lower().startswith("http") else f"https://instagram.com/{username}"
        if u_raw and " " in u_raw and u_raw.lower() not in full_raw.lower():
            full_raw = f"{u_raw} — {full_raw}" if full_raw else u_raw
        return username, profile_url, full_raw or username

    # Si no vino URL explícita: revisar si Name./Username es handle válido o nombre con espacios
    if u_raw and " " not in u_raw and re.match(r"^[A-Za-z0-9._]+$", u_raw):
        username = u_raw.lower()
        profile_url = url_raw or f"https://instagram.com/{username}"
        return username, profile_url, full_raw or u_raw

    # Caso especial (ej. 'Vl beaute Salon' sin profile_url): conservar full_name legible y generar slug limpio
    if u_raw:
        slug = re.sub(r"[^a-z0-9._]+", "_", u_raw.lower()).strip("_") or f"ig_{uuid.uuid4().hex[:8]}"
        combined_full = f"{u_raw} — {full_raw}" if (full_raw and u_raw.lower() not in full_raw.lower()) else (full_raw or u_raw)
        return slug, url_raw, combined_full

    slug = f"lead_{uuid.uuid4().hex[:8]}"
    return slug, url_raw, full_raw or slug


def parse_instagram_spreadsheet_bytes(raw_bytes: bytes, filename: str) -> List[Dict[str, Any]]:
    """Convierte archivos Excel (.xlsx) o CSV de prospección IG al esquema unificado Beauty Growth."""
    low_name = (filename or "upload.xlsx").lower()
    if low_name.endswith(".xlsx"):
        rows = _extract_xlsx_rows(raw_bytes)
    else:
        rows = _extract_csv_rows(raw_bytes)

    if not rows:
        return []

    header_map: Dict[str, int] = {}
    parsed_records: List[Dict[str, Any]] = []

    for r in rows:
        if _is_header_row(r):
            header_map = {}
            for idx, col in enumerate(r):
                tok = _normalize_header_token(col)
                if tok and tok not in header_map:
                    header_map[tok] = idx
            continue

        if not header_map:
            # Asumir esquema por defecto según número de columnas si no hubo encabezado previo
            header_map = (
                {
                    "username": 0, "firstname": 1, "lastname": 2, "fullname": 3, "email": 4,
                    "isbusiness": 5, "biography": 6, "profilepicurl": 7, "phoneextension": 8,
                    "phonenumber": 9, "fullphonenumber": 10, "website": 11, "city": 12,
                    "followers": 13, "following": 14,
                }
                if len(r) >= 13
                else {
                    "name": 0, "fullname": 1, "correo": 2, "numero": 3, "location": 4,
                    "profileurl": 5, "biography": 6, "website": 7, "pipeline": 8,
                }
            )

        def _get(*keys: str) -> str:
            for k in keys:
                idx = header_map.get(k)
                if idx is not None and idx < len(r):
                    return r[idx]
            return ""

        raw_user = _get("username", "name", "usuario", "igusername", "account")
        if not _clean_text(raw_user) and not _clean_text(_get("profileurl")):
            continue

        first_name = _clean_text(_get("firstname"))
        last_name = _clean_text(_get("lastname"))
        raw_full = _clean_text(_get("fullname", "nombrecompleto", "nombre"))
        if not raw_full and (first_name or last_name):
            raw_full = f"{first_name} {last_name}".strip()

        ig_username, ig_profile_url, full_name = _derive_ig_identity(
            raw_user,
            _get("profileurl", "igprofileurl"),
            raw_full,
        )

        email_primary, email_secondary = _clean_emails(_get("email", "correo"))
        location_raw = _clean_text(_get("location", "city", "ciudad", "ubicacion"))
        raw_phone = _get("fullphonenumber", "numero", "contact", "phone", "telefono", "whatsapp")
        phone_num = _get("phonenumber")
        phone_ext = _get("phoneextension")
        if not _clean_text(raw_phone) and _clean_text(phone_num):
            raw_phone = phone_num

        phone_raw, phone_e164 = normalize_beauty_phone(raw_phone, phone_ext, location_raw)
        if not phone_e164 and _clean_text(phone_num) and phone_num != raw_phone:
            _, phone_e164 = normalize_beauty_phone(phone_num, phone_ext, location_raw)

        biography = _clean_text(_get("biography", "bio", "descripcion"))
        website_raw = _get("website", "web", "sitio")
        website_url, booking_platform = detect_booking_platform(website_raw)
        profile_pic_url = _clean_text(_get("profilepicurl"))
        is_business_str = _clean_text(_get("isbusiness")).lower()
        is_business = 1 if is_business_str in ("true", "1", "yes", "si", "sí") else 0
        followers = _clean_int(_get("followers", "seguidores"))
        following = _clean_int(_get("following", "seguidos"))

        # Notas de diagnóstico extendidas (col 10 en Archivo 2 o columna dedicada)
        extra_col10 = _clean_text(r[9]) if (len(r) > 9 and 9 not in header_map.values()) else ""
        diag_col = _clean_text(_get("diagnostic", "diagnostico", "resumen", "aidiagnosticnote"))
        ai_diag = diag_col or extra_col10

        country_region = classify_country_region(location_raw, phone_e164, biography)
        niche_category = classify_niche_category(ig_username, full_name, biography, website_url, country_region)
        city = _extract_city(location_raw)

        parsed_records.append({
            "ig_username": ig_username,
            "ig_profile_url": ig_profile_url,
            "ig_profile_pic_url": profile_pic_url,
            "is_business": is_business,
            "followers_count": followers,
            "following_count": following,
            "full_name": full_name,
            "first_name": first_name or (full_name.split()[0] if full_name else ig_username),
            "last_name": last_name,
            "email_primary": email_primary,
            "email_secondary": email_secondary,
            "phone_raw": phone_raw,
            "phone_e164": phone_e164,
            "biography": biography,
            "website_url": website_url,
            "booking_platform": booking_platform,
            "location_raw": location_raw,
            "city": city,
            "country_region": country_region,
            "niche_category": niche_category,
            "ai_diagnostic_note": ai_diag,
            "source_file": os.path.basename(filename),
        })

    return parsed_records


def merge_lead_dicts(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Deduplica por ig_username conservando la información más rica de cada registro."""
    by_user: Dict[str, Dict[str, Any]] = {}
    for rec in records:
        key = (rec.get("ig_username") or "").strip().lower()
        if not key:
            continue
        if key not in by_user:
            by_user[key] = dict(rec)
            continue

        cur = by_user[key]
        for field in (
            "ig_profile_url",
            "ig_profile_pic_url",
            "full_name",
            "first_name",
            "last_name",
            "biography",
            "website_url",
            "location_raw",
            "city",
            "ai_diagnostic_note",
            "phone_raw",
            "phone_e164",
        ):
            new_val = (rec.get(field) or "").strip()
            old_val = (cur.get(field) or "").strip()
            if len(new_val) > len(old_val):
                cur[field] = new_val

        # Emails combinados sin duplicar
        emails = []
        for em_field in (cur.get("email_primary", ""), cur.get("email_secondary", ""), rec.get("email_primary", ""), rec.get("email_secondary", "")):
            for part in str(em_field or "").split(","):
                p = part.strip().lower()
                if p and "@" in p and p not in emails:
                    emails.append(p)
        if emails:
            cur["email_primary"] = emails[0]
            cur["email_secondary"] = ", ".join(emails[1:4])

        cur["followers_count"] = max(int(cur.get("followers_count") or 0), int(rec.get("followers_count") or 0))
        cur["following_count"] = max(int(cur.get("following_count") or 0), int(rec.get("following_count") or 0))
        cur["is_business"] = max(int(cur.get("is_business") or 0), int(rec.get("is_business") or 0))
        if cur.get("booking_platform") in ("", "Sin Web") and rec.get("booking_platform") not in ("", "Sin Web"):
            cur["booking_platform"] = rec["booking_platform"]
        # Recalcular país y nicho sobre los campos fusionados
        cur["country_region"] = classify_country_region(cur.get("location_raw", ""), cur.get("phone_e164", ""), cur.get("biography", ""))
        cur["niche_category"] = classify_niche_category(
            cur.get("ig_username", ""),
            cur.get("full_name", ""),
            cur.get("biography", ""),
            cur.get("website_url", ""),
            cur["country_region"],
        )
        src_old = cur.get("source_file") or ""
        src_new = rec.get("source_file") or ""
        if src_new and src_new not in src_old:
            cur["source_file"] = f"{src_old}, {src_new}".strip(", ")

    return list(by_user.values())


def assign_stratified_setter_slots(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Reparte los prospectos equitativamente (1/3 - 1/3 - 1/3) por nicho, región y seguidores."""
    ordered = sorted(
        records,
        key=lambda r: (
            0 if r.get("niche_category") == "Belleza / Estética / Salón" else (1 if r.get("niche_category") == "Otros Giros Comerciales" else 2),
            0 if r.get("country_region") == "USA / PR" else 1,
            r.get("country_region") or "",
            -(int(r.get("followers_count") or 0)),
            -(1 if r.get("phone_e164") else 0),
            r.get("ig_username") or "",
        ),
    )
    for idx, rec in enumerate(ordered):
        rec["assigned_setter_slot"] = (idx % 3) + 1
    return ordered


# ─── SERIALIZACIÓN Y AUTENTICACIÓN ──────────────────────────────────────────

def _verify_bg_password(password: str, stored_hash: str, email: str = "") -> bool:
    if verify_password(password, stored_hash):
        return True
    norm_em = normalize_email(email)
    admin_env_pw = (os.environ.get("ADMIN_PASSWORD") or "").strip()
    if norm_em in ("dbecerra@agenciaprosperia.com", "edward@agenciaprosperia.com"):
        if admin_env_pw and password == admin_env_pw:
            return True
    return False


def _serialize_bg_user(u: BeautyGrowthUser) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "name": u.name,
        "role": u.role,
        "setter_slot": int(u.setter_slot or 0),
        "phone": u.phone or "",
        "ghl_user_id": u.ghl_user_id or "",
        "is_active": int(u.is_active or 0),
        "last_login_at": u.last_login_at or "",
        "created_at": u.created_at or "",
    }


def _serialize_bg_lead(l: BeautyGrowthLead) -> dict:
    return {
        "id": l.id,
        "ig_username": l.ig_username,
        "ig_profile_url": l.ig_profile_url or "",
        "ig_profile_pic_url": l.ig_profile_pic_url or "",
        "is_business": int(l.is_business or 0),
        "followers_count": int(l.followers_count or 0),
        "following_count": int(l.following_count or 0),
        "full_name": l.full_name or "",
        "first_name": l.first_name or "",
        "last_name": l.last_name or "",
        "email_primary": l.email_primary or "",
        "email_secondary": l.email_secondary or "",
        "phone_raw": l.phone_raw or "",
        "phone_e164": l.phone_e164 or "",
        "biography": l.biography or "",
        "website_url": l.website_url or "",
        "booking_platform": l.booking_platform or "Sin Web",
        "location_raw": l.location_raw or "",
        "city": l.city or "",
        "country_region": l.country_region or "LATAM / Otros",
        "niche_category": l.niche_category or "Belleza / Estética / Salón",
        "pipeline_stage": l.pipeline_stage or "1. Prospecto identificado",
        "assigned_setter_slot": int(l.assigned_setter_slot or 0),
        "assigned_setter_email": l.assigned_setter_email or "",
        "assigned_setter_name": l.assigned_setter_name or "",
        "offer_package": l.offer_package or "BEAUTY_ELEVATE_2499",
        "quoted_amount": float(l.quoted_amount or 0.0),
        "ai_diagnostic_note": l.ai_diagnostic_note or "",
        "setter_notes": l.setter_notes or "",
        "source_file": l.source_file or "",
        "ghl_synced": int(l.ghl_synced or 0),
        "ghl_contact_id": l.ghl_contact_id or "",
        "ghl_opportunity_id": l.ghl_opportunity_id or "",
        "last_touch_at": l.last_touch_at or "",
        "created_at": l.created_at or "",
    }


def _get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _extract_bg_token(request: Request) -> Optional[str]:
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ", 1)[1].strip()
    return request.cookies.get(BG_COOKIE_NAME)


def get_current_bg_user(request: Request, db: Session = Depends(_get_db)) -> BeautyGrowthUser:
    token = _extract_bg_token(request)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sesión Beauty Growth no iniciada.")
    sess = db.query(BeautyGrowthSession).filter(BeautyGrowthSession.token == token).first()
    if not sess:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sesión expirada o inválida.")
    user = db.query(BeautyGrowthUser).filter(BeautyGrowthUser.email == sess.email).first()
    if not user or int(user.is_active or 0) == 0:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario Beauty Growth inactivo.")
    return user


def require_bg_admin(user: BeautyGrowthUser = Depends(get_current_bg_user)) -> BeautyGrowthUser:
    if (user.role or "").lower() != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo administradores de Beauty Growth pueden realizar esta acción.")
    return user


def _get_setter_slot_map(db: Session) -> Dict[int, BeautyGrowthUser]:
    users = db.query(BeautyGrowthUser).filter(BeautyGrowthUser.setter_slot.in_([1, 2, 3])).all()
    return {int(u.setter_slot): u for u in users}


def _load_seed_records() -> List[Dict[str, Any]]:
    for path in SEED_CANDIDATE_PATHS:
        if not path.exists():
            continue
        if path.suffix == ".gz":
            with gzip.open(path, "rt", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else data.get("leads", [])
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else data.get("leads", [])
    return []


def init_beauty_growth_os() -> None:
    """Crea tablas exclusivas de Beauty Growth, siembra Admins + 3 Setters y carga los 3,635 leads si está vacía."""
    BeautyGrowthUser.__table__.create(bind=engine, checkfirst=True)
    BeautyGrowthSession.__table__.create(bind=engine, checkfirst=True)
    BeautyGrowthLead.__table__.create(bind=engine, checkfirst=True)

    db = SessionLocal()
    try:
        now_iso = _now_iso()

        # 1. Admins (Jhonkelwins David Becerra Cañas + Edward Jiménez)
        admins = [
            {
                "email": "dbecerra@agenciaprosperia.com",
                "name": "Jhonkelwins David Becerra Cañas",
                "password_hash": hash_password("BeautyGrowth2026!"),
                "ghl_user_id": BEAUTY_DEFAULT_USER_ID,
            },
            {
                "email": "edward@agenciaprosperia.com",
                "name": "Edward Jiménez",
                "password_hash": hash_password((os.environ.get("ADMIN_PASSWORD") or "Digital2@26!").strip()),
                "ghl_user_id": BEAUTY_DEFAULT_USER_ID,
            },
        ]
        for adm in admins:
            existing_adm = db.query(BeautyGrowthUser).filter(BeautyGrowthUser.email == adm["email"]).first()
            if not existing_adm:
                db.add(BeautyGrowthUser(
                    email=adm["email"],
                    name=adm["name"],
                    password_hash=adm["password_hash"],
                    role="admin",
                    setter_slot=0,
                    ghl_user_id=adm["ghl_user_id"],
                    is_active=1,
                    created_at=now_iso,
                ))

        # 2. Tres Setters iniciales por slot (1, 2, 3) — nunca sobrescribe correos ya actualizados por Jhon
        for slot in (1, 2, 3):
            existing_slot = db.query(BeautyGrowthUser).filter(BeautyGrowthUser.setter_slot == slot).first()
            if not existing_slot:
                db.add(BeautyGrowthUser(
                    email=f"setter{slot}@agenciaprosperia.com",
                    name=f"Setter {slot} · Beauty Growth",
                    password_hash=hash_password("Setter2026!"),
                    role="setter",
                    setter_slot=slot,
                    is_active=1,
                    created_at=now_iso,
                ))

        db.commit()

        # 3. Sembrar base unificada de Instagram (3,635 registros) si está vacía
        lead_count = db.query(BeautyGrowthLead).count()
        if lead_count == 0:
            seed_rows = _load_seed_records()
            if seed_rows:
                slot_map = _get_setter_slot_map(db)
                objects = []
                for idx, rec in enumerate(seed_rows):
                    slot = int(rec.get("assigned_setter_slot") or ((idx % 3) + 1))
                    if slot not in (1, 2, 3):
                        slot = (idx % 3) + 1
                    setter_user = slot_map.get(slot)
                    objects.append(BeautyGrowthLead(
                        ig_username=(rec.get("ig_username") or f"ig_{idx+1}").strip().lower(),
                        ig_profile_url=rec.get("ig_profile_url") or "",
                        ig_profile_pic_url=rec.get("ig_profile_pic_url") or "",
                        is_business=int(rec.get("is_business") or 0),
                        followers_count=int(rec.get("followers_count") or 0),
                        following_count=int(rec.get("following_count") or 0),
                        full_name=rec.get("full_name") or "",
                        first_name=rec.get("first_name") or "",
                        last_name=rec.get("last_name") or "",
                        email_primary=rec.get("email_primary") or "",
                        email_secondary=rec.get("email_secondary") or "",
                        phone_raw=rec.get("phone_raw") or "",
                        phone_e164=rec.get("phone_e164") or "",
                        biography=rec.get("biography") or "",
                        website_url=rec.get("website_url") or "",
                        booking_platform=rec.get("booking_platform") or "Sin Web",
                        location_raw=rec.get("location_raw") or "",
                        city=rec.get("city") or "",
                        country_region=rec.get("country_region") or "LATAM / Otros",
                        niche_category=rec.get("niche_category") or "Belleza / Estética / Salón",
                        pipeline_stage="1. Prospecto identificado",
                        assigned_setter_slot=slot,
                        assigned_setter_email=setter_user.email if setter_user else f"setter{slot}@agenciaprosperia.com",
                        assigned_setter_name=setter_user.name if setter_user else f"Setter {slot} · Beauty Growth",
                        offer_package="BEAUTY_ELEVATE_2499",
                        quoted_amount=0.0,
                        ai_diagnostic_note=rec.get("ai_diagnostic_note") or "",
                        setter_notes="",
                        source_file=rec.get("source_file") or "seed_unificado",
                        ghl_synced=0,
                        ghl_contact_id="",
                        ghl_opportunity_id="",
                        last_touch_at="",
                        created_at=now_iso,
                    ))
                db.bulk_save_objects(objects)
                db.commit()
                print(f"✅ [BEAUTY GROWTH OS] Sembrados {len(objects)} leads únicos de Instagram repartidos en 3 Setters.", flush=True)
    except Exception as exc:
        db.rollback()
        print(f"⚠️ [BEAUTY GROWTH OS] Error inicializando: {exc}", flush=True)
    finally:
        db.close()


# ─── SCHEMAS PYDANTIC Y ROUTER API ───────────────────────────────────────────

router = APIRouter(prefix="/api/beautygrowth", tags=["Beauty Growth OS"])


class BgLoginRequest(BaseModel):
    email: str
    password: str


class BgLeadUpdateRequest(BaseModel):
    pipeline_stage: Optional[str] = None
    assigned_setter_slot: Optional[int] = None
    setter_notes: Optional[str] = None
    ai_diagnostic_note: Optional[str] = None
    biography: Optional[str] = None
    full_name: Optional[str] = None
    phone_raw: Optional[str] = None
    email_primary: Optional[str] = None
    location_raw: Optional[str] = None
    website_url: Optional[str] = None
    offer_package: Optional[str] = None
    quoted_amount: Optional[float] = None
    sync_to_ghl: Optional[bool] = None


class BgLeadCreateRequest(BaseModel):
    ig_username: str
    full_name: Optional[str] = ""
    phone_raw: Optional[str] = ""
    email_primary: Optional[str] = ""
    location_raw: Optional[str] = ""
    website_url: Optional[str] = ""
    biography: Optional[str] = ""
    followers_count: Optional[int] = 0
    following_count: Optional[int] = 0
    ai_diagnostic_note: Optional[str] = ""
    assigned_setter_slot: Optional[int] = 0
    pipeline_stage: Optional[str] = "1. Prospecto identificado"
    sync_to_ghl: Optional[bool] = False


class BgFilterSpec(BaseModel):
    q: Optional[str] = ""
    setter_slot: Optional[str] = "all"
    pipeline_stage: Optional[str] = "all"
    niche_category: Optional[str] = "all"
    country_region: Optional[str] = "all"
    booking_platform: Optional[str] = "all"
    min_followers: Optional[int] = 0
    has_phone: Optional[str] = "all"
    has_bio: Optional[str] = "all"
    ghl_synced: Optional[str] = "all"


class BgBulkActionRequest(BaseModel):
    action: str  # assign_setter | redistribute_equally | change_stage | sync_ghl_batch
    lead_ids: Optional[List[int]] = None
    apply_to_filter: Optional[bool] = False
    filters: Optional[BgFilterSpec] = None
    target_setter_slot: Optional[int] = None
    target_stage: Optional[str] = None


class BgSetterUpdateRequest(BaseModel):
    name: str
    email: str
    phone: Optional[str] = ""
    new_password: Optional[str] = ""
    is_active: Optional[int] = 1


def _apply_lead_filters(
    query,
    user: BeautyGrowthUser,
    q: str = "",
    setter_slot: str = "all",
    pipeline_stage: str = "all",
    niche_category: str = "all",
    country_region: str = "all",
    booking_platform: str = "all",
    min_followers: int = 0,
    has_phone: str = "all",
    has_bio: str = "all",
    ghl_synced: str = "all",
    skip_stage_filter: bool = False,
):
    # RBAC: Un Setter solo ve su cartera asignada (1/3); Jhon (Admin) ve todo y puede filtrar
    if (user.role or "").lower() != "admin":
        query = query.filter(BeautyGrowthLead.assigned_setter_slot == int(user.setter_slot or 1))
    elif setter_slot and setter_slot not in ("all", ""):
        if setter_slot == "unassigned":
            query = query.filter((BeautyGrowthLead.assigned_setter_slot == None) | (BeautyGrowthLead.assigned_setter_slot == 0))
        elif setter_slot.isdigit():
            query = query.filter(BeautyGrowthLead.assigned_setter_slot == int(setter_slot))

    if not skip_stage_filter and pipeline_stage and pipeline_stage not in ("all", ""):
        query = query.filter(BeautyGrowthLead.pipeline_stage == pipeline_stage)

    if niche_category and niche_category not in ("all", ""):
        query = query.filter(BeautyGrowthLead.niche_category == niche_category)

    if country_region and country_region not in ("all", ""):
        query = query.filter(BeautyGrowthLead.country_region == country_region)

    if booking_platform and booking_platform not in ("all", ""):
        query = query.filter(BeautyGrowthLead.booking_platform == booking_platform)

    if min_followers and min_followers > 0:
        query = query.filter(BeautyGrowthLead.followers_count >= int(min_followers))

    if has_phone == "yes":
        query = query.filter((BeautyGrowthLead.phone_e164 != None) & (BeautyGrowthLead.phone_e164 != ""))
    elif has_phone == "no":
        query = query.filter((BeautyGrowthLead.phone_e164 == None) | (BeautyGrowthLead.phone_e164 == ""))

    if has_bio == "yes":
        query = query.filter((BeautyGrowthLead.biography != None) & (BeautyGrowthLead.biography != ""))
    elif has_bio == "no":
        query = query.filter((BeautyGrowthLead.biography == None) | (BeautyGrowthLead.biography == ""))

    if ghl_synced == "1":
        query = query.filter(BeautyGrowthLead.ghl_synced == 1)
    elif ghl_synced == "0":
        query = query.filter((BeautyGrowthLead.ghl_synced == None) | (BeautyGrowthLead.ghl_synced == 0))

    search = (q or "").strip()
    if search:
        pat = f"%{search}%"
        query = query.filter(
            or_(
                BeautyGrowthLead.ig_username.ilike(pat),
                BeautyGrowthLead.full_name.ilike(pat),
                BeautyGrowthLead.biography.ilike(pat),
                BeautyGrowthLead.ai_diagnostic_note.ilike(pat),
                BeautyGrowthLead.setter_notes.ilike(pat),
                BeautyGrowthLead.email_primary.ilike(pat),
                BeautyGrowthLead.phone_e164.ilike(pat),
                BeautyGrowthLead.phone_raw.ilike(pat),
                BeautyGrowthLead.location_raw.ilike(pat),
                BeautyGrowthLead.website_url.ilike(pat),
            )
        )
    return query


@router.post("/auth/login")
async def api_bg_login(req: BgLoginRequest, request: Request, response: Response, db: Session = Depends(_get_db)):
    email_clean = normalize_email(req.email)
    user = db.query(BeautyGrowthUser).filter(BeautyGrowthUser.email == email_clean).first()
    if not user or int(user.is_active or 0) == 0:
        return JSONResponse(status_code=400, content={"success": False, "error": "Usuario no autorizado en Beauty Growth OS."})
    if not _verify_bg_password(req.password, user.password_hash, user.email):
        return JSONResponse(status_code=400, content={"success": False, "error": "Contraseña incorrecta."})

    token = f"bg_{uuid.uuid4().hex}"
    now_iso = _now_iso()
    db.add(BeautyGrowthSession(token=token, email=user.email, created_at=now_iso))
    user.last_login_at = now_iso
    db.commit()

    is_secure = (request.url.scheme == "https") or (request.headers.get("x-forwarded-proto") == "https")
    response.set_cookie(
        key=BG_COOKIE_NAME,
        value=token,
        max_age=604800,
        path="/",
        httponly=True,
        samesite="none" if is_secure else "lax",
        secure=is_secure,
    )
    return {
        "success": True,
        "data": {
            "token": token,
            "user": _serialize_bg_user(user),
        },
    }


@router.post("/auth/logout")
async def api_bg_logout(request: Request, response: Response, db: Session = Depends(_get_db)):
    token = _extract_bg_token(request)
    if token:
        sess = db.query(BeautyGrowthSession).filter(BeautyGrowthSession.token == token).first()
        if sess:
            db.delete(sess)
            db.commit()
    response.delete_cookie(BG_COOKIE_NAME, path="/")
    return {"success": True}


@router.get("/auth/me")
async def api_bg_me(user: BeautyGrowthUser = Depends(get_current_bg_user), db: Session = Depends(_get_db)):
    slot_map = _get_setter_slot_map(db)
    team = [_serialize_bg_user(slot_map[s]) for s in (1, 2, 3) if s in slot_map]
    return {
        "success": True,
        "data": {
            "user": _serialize_bg_user(user),
            "team": team,
            "stages": BEAUTY_GROWTH_PIPELINE_STAGES,
            "regions": REGION_CHOICES,
            "niches": NICHE_CHOICES,
            "platforms": PLATFORM_CHOICES,
            "packages": {k: v for k, v in OFFER_CATALOG.items() if k.startswith("BEAUTY_")},
            "ghl": check_beauty_ghl_connection(),
        },
    }


@router.get("/leads")
async def api_bg_list_leads(
    q: str = "",
    setter_slot: str = "all",
    pipeline_stage: str = "all",
    niche_category: str = "all",
    country_region: str = "all",
    booking_platform: str = "all",
    min_followers: int = 0,
    has_phone: str = "all",
    has_bio: str = "all",
    ghl_synced: str = "all",
    sort_by: str = "followers_desc",
    page: int = 1,
    per_page: int = 50,
    user: BeautyGrowthUser = Depends(get_current_bg_user),
    db: Session = Depends(_get_db),
):
    page = max(1, page)
    per_page = max(10, min(200, per_page))

    base_q = _apply_lead_filters(
        db.query(BeautyGrowthLead),
        user=user,
        q=q,
        setter_slot=setter_slot,
        pipeline_stage=pipeline_stage,
        niche_category=niche_category,
        country_region=country_region,
        booking_platform=booking_platform,
        min_followers=min_followers,
        has_phone=has_phone,
        has_bio=has_bio,
        ghl_synced=ghl_synced,
    )

    total_filtered = base_q.count()

    if sort_by == "followers_asc":
        order_expr = [BeautyGrowthLead.followers_count.asc(), BeautyGrowthLead.id.asc()]
    elif sort_by == "recent_touch":
        order_expr = [BeautyGrowthLead.last_touch_at.desc(), BeautyGrowthLead.followers_count.desc()]
    elif sort_by == "stage_asc":
        order_expr = [BeautyGrowthLead.pipeline_stage.asc(), BeautyGrowthLead.followers_count.desc()]
    elif sort_by == "name_asc":
        order_expr = [BeautyGrowthLead.full_name.asc(), BeautyGrowthLead.ig_username.asc()]
    elif sort_by == "newest":
        order_expr = [BeautyGrowthLead.id.desc()]
    else:
        # Por defecto: priorizar Nicho Belleza + seguidores + teléfono disponible
        order_expr = [
            BeautyGrowthLead.followers_count.desc(),
            BeautyGrowthLead.id.asc(),
        ]

    rows = base_q.order_by(*order_expr).offset((page - 1) * per_page).limit(per_page).all()

    # Conteo por cada una de las 14 etapas con los demás filtros activos
    stage_q = _apply_lead_filters(
        db.query(BeautyGrowthLead.pipeline_stage, func.count(BeautyGrowthLead.id)),
        user=user,
        q=q,
        setter_slot=setter_slot,
        pipeline_stage="all",
        niche_category=niche_category,
        country_region=country_region,
        booking_platform=booking_platform,
        min_followers=min_followers,
        has_phone=has_phone,
        has_bio=has_bio,
        ghl_synced=ghl_synced,
        skip_stage_filter=True,
    )
    stage_rows = stage_q.group_by(BeautyGrowthLead.pipeline_stage).all()
    stage_counts = {st: 0 for st in BEAUTY_GROWTH_PIPELINE_STAGES}
    for st_name, cnt in stage_rows:
        if st_name in stage_counts:
            stage_counts[st_name] = int(cnt or 0)
        else:
            stage_counts[st_name or "1. Prospecto identificado"] = int(cnt or 0)

    # KPIs globales del alcance del usuario (Admin ve toda la base; Setter ve su 1/3)
    scope_q = db.query(BeautyGrowthLead)
    if (user.role or "").lower() != "admin":
        scope_q = scope_q.filter(BeautyGrowthLead.assigned_setter_slot == int(user.setter_slot or 1))

    total_scope = scope_q.count()
    beauty_scope = scope_q.filter(BeautyGrowthLead.niche_category == "Belleza / Estética / Salón").count()
    usa_scope = scope_q.filter(BeautyGrowthLead.country_region == "USA / PR").count()
    phone_scope = scope_q.filter((BeautyGrowthLead.phone_e164 != None) & (BeautyGrowthLead.phone_e164 != "")).count()
    bio_scope = scope_q.filter((BeautyGrowthLead.biography != None) & (BeautyGrowthLead.biography != "")).count()
    ghl_scope = scope_q.filter(BeautyGrowthLead.ghl_synced == 1).count()

    setter_counts_raw = (
        db.query(BeautyGrowthLead.assigned_setter_slot, func.count(BeautyGrowthLead.id))
        .group_by(BeautyGrowthLead.assigned_setter_slot)
        .all()
    )
    setter_counts = {str(s or 0): int(c or 0) for s, c in setter_counts_raw}

    return {
        "success": True,
        "data": {
            "leads": [_serialize_bg_lead(r) for r in rows],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total_filtered,
                "total_pages": max(1, (total_filtered + per_page - 1) // per_page),
            },
            "stage_counts": stage_counts,
            "stats": {
                "total": total_scope,
                "beauty_count": beauty_scope,
                "usa_count": usa_scope,
                "with_phone": phone_scope,
                "with_bio": bio_scope,
                "ghl_synced": ghl_scope,
                "setter_counts": setter_counts,
            },
        },
    }


@router.post("/leads")
async def api_bg_create_lead(
    req: BgLeadCreateRequest,
    user: BeautyGrowthUser = Depends(get_current_bg_user),
    db: Session = Depends(_get_db),
):
    ig_username, ig_profile_url, full_name = _derive_ig_identity(req.ig_username, "", req.full_name or "")
    existing = db.query(BeautyGrowthLead).filter(BeautyGrowthLead.ig_username == ig_username).first()
    if existing:
        return JSONResponse(
            status_code=409,
            content={"success": False, "error": f"Ya existe un prospecto con el usuario @{ig_username}."},
        )

    phone_raw, phone_e164 = normalize_beauty_phone(req.phone_raw or "", "", req.location_raw or "")
    email_primary, email_secondary = _clean_emails(req.email_primary or "")
    website_url, booking_platform = detect_booking_platform(req.website_url or "")
    country_region = classify_country_region(req.location_raw or "", phone_e164, req.biography or "")
    niche_category = classify_niche_category(ig_username, full_name, req.biography or "", website_url, country_region)

    slot = int(req.assigned_setter_slot or 0)
    if (user.role or "").lower() != "admin":
        slot = int(user.setter_slot or 1)
    elif slot not in (1, 2, 3):
        # Asignar automáticamente al slot con menor carga actual
        counts = (
            db.query(BeautyGrowthLead.assigned_setter_slot, func.count(BeautyGrowthLead.id))
            .filter(BeautyGrowthLead.assigned_setter_slot.in_([1, 2, 3]))
            .group_by(BeautyGrowthLead.assigned_setter_slot)
            .all()
        )
        cnt_map = {s: 0 for s in (1, 2, 3)}
        for s_num, cnt in counts:
            cnt_map[int(s_num)] = int(cnt)
        slot = min(cnt_map, key=lambda k: cnt_map[k])

    slot_map = _get_setter_slot_map(db)
    setter_user = slot_map.get(slot)
    now_iso = _now_iso()

    lead = BeautyGrowthLead(
        ig_username=ig_username,
        ig_profile_url=ig_profile_url,
        followers_count=int(req.followers_count or 0),
        following_count=int(req.following_count or 0),
        full_name=full_name,
        first_name=full_name.split()[0] if full_name else ig_username,
        email_primary=email_primary,
        email_secondary=email_secondary,
        phone_raw=phone_raw,
        phone_e164=phone_e164,
        biography=_clean_text(req.biography or ""),
        website_url=website_url,
        booking_platform=booking_platform,
        location_raw=_clean_text(req.location_raw or ""),
        city=_extract_city(req.location_raw or ""),
        country_region=country_region,
        niche_category=niche_category,
        pipeline_stage=req.pipeline_stage or "1. Prospecto identificado",
        assigned_setter_slot=slot,
        assigned_setter_email=setter_user.email if setter_user else f"setter{slot}@agenciaprosperia.com",
        assigned_setter_name=setter_user.name if setter_user else f"Setter {slot} · Beauty Growth",
        ai_diagnostic_note=_clean_text(req.ai_diagnostic_note or ""),
        source_file="alta_manual_web",
        created_at=now_iso,
        last_touch_at=now_iso,
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)

    ghl_res = None
    if req.sync_to_ghl or lead.pipeline_stage != "1. Prospecto identificado":
        ghl_res = sync_beauty_growth_ig_lead_to_ghl(_serialize_bg_lead(lead))
        if ghl_res.get("ok"):
            lead.ghl_synced = 1
            lead.ghl_contact_id = ghl_res.get("contact_id") or ""
            lead.ghl_opportunity_id = ghl_res.get("opportunity_id") or ""
            db.commit()
            db.refresh(lead)

    return {"success": True, "data": _serialize_bg_lead(lead), "ghl_sync": ghl_res}


@router.put("/leads/{lead_id}")
async def api_bg_update_lead(
    lead_id: int,
    req: BgLeadUpdateRequest,
    user: BeautyGrowthUser = Depends(get_current_bg_user),
    db: Session = Depends(_get_db),
):
    lead = db.query(BeautyGrowthLead).filter(BeautyGrowthLead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Prospecto Beauty Growth no encontrado.")

    is_admin = (user.role or "").lower() == "admin"
    if not is_admin and int(lead.assigned_setter_slot or 0) != int(user.setter_slot or -1):
        raise HTTPException(status_code=403, detail="Solo puedes editar los prospectos asignados a tu cartera.")

    old_stage = lead.pipeline_stage
    if req.pipeline_stage is not None:
        if req.pipeline_stage not in BEAUTY_GROWTH_PIPELINE_STAGES:
            raise HTTPException(status_code=400, detail="Etapa inválida para el pipeline de 14 etapas.")
        lead.pipeline_stage = req.pipeline_stage

    if req.assigned_setter_slot is not None:
        if not is_admin:
            raise HTTPException(status_code=403, detail="Solo el Administrador puede reasignar prospectos entre Setters.")
        slot = int(req.assigned_setter_slot)
        if slot not in (1, 2, 3):
            raise HTTPException(status_code=400, detail="El slot del Setter debe ser 1, 2 o 3.")
        slot_map = _get_setter_slot_map(db)
        setter_user = slot_map.get(slot)
        lead.assigned_setter_slot = slot
        lead.assigned_setter_email = setter_user.email if setter_user else f"setter{slot}@agenciaprosperia.com"
        lead.assigned_setter_name = setter_user.name if setter_user else f"Setter {slot} · Beauty Growth"

    if req.setter_notes is not None:
        lead.setter_notes = req.setter_notes.strip()
    if req.ai_diagnostic_note is not None:
        lead.ai_diagnostic_note = req.ai_diagnostic_note.strip()
    if req.biography is not None:
        lead.biography = req.biography.strip()
    if req.full_name is not None:
        lead.full_name = req.full_name.strip()
        if lead.full_name:
            lead.first_name = lead.full_name.split()[0]
    if req.email_primary is not None:
        em1, em2 = _clean_emails(req.email_primary)
        lead.email_primary = em1
        if em2:
            lead.email_secondary = em2
    if req.location_raw is not None:
        lead.location_raw = req.location_raw.strip()
        lead.city = _extract_city(lead.location_raw)
        lead.country_region = classify_country_region(lead.location_raw, lead.phone_e164 or "", lead.biography or "")
    if req.phone_raw is not None:
        ph_raw, ph_e164 = normalize_beauty_phone(req.phone_raw, "", lead.location_raw or "")
        lead.phone_raw = ph_raw
        lead.phone_e164 = ph_e164
    if req.website_url is not None:
        web_url, platform = detect_booking_platform(req.website_url)
        lead.website_url = web_url
        lead.booking_platform = platform
    if req.offer_package is not None:
        pkg = req.offer_package.strip().upper()
        lead.offer_package = pkg
        if req.quoted_amount is None and pkg in BEAUTY_PACKAGE_PRICES:
            lead.quoted_amount = BEAUTY_PACKAGE_PRICES[pkg]
    if req.quoted_amount is not None:
        lead.quoted_amount = float(req.quoted_amount)

    lead.last_touch_at = _now_iso()
    db.commit()
    db.refresh(lead)

    # Opción A: Sincronizar automáticamente hacia GHL cuando avanza a etapa 2+ o si ya estaba en GHL
    should_sync = bool(req.sync_to_ghl) or (
        lead.pipeline_stage != old_stage and lead.pipeline_stage != "1. Prospecto identificado"
    ) or (int(lead.ghl_synced or 0) == 1 and req.pipeline_stage is not None)

    ghl_res = None
    if should_sync:
        ghl_res = sync_beauty_growth_ig_lead_to_ghl(_serialize_bg_lead(lead))
        if ghl_res.get("ok"):
            lead.ghl_synced = 1
            lead.ghl_contact_id = ghl_res.get("contact_id") or lead.ghl_contact_id
            lead.ghl_opportunity_id = ghl_res.get("opportunity_id") or lead.ghl_opportunity_id
            db.commit()
            db.refresh(lead)

    return {
        "success": True,
        "data": _serialize_bg_lead(lead),
        "ghl_sync": ghl_res,
    }


@router.post("/leads/{lead_id}/sync-ghl")
async def api_bg_sync_single_ghl(
    lead_id: int,
    user: BeautyGrowthUser = Depends(get_current_bg_user),
    db: Session = Depends(_get_db),
):
    lead = db.query(BeautyGrowthLead).filter(BeautyGrowthLead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Prospecto Beauty Growth no encontrado.")
    if (user.role or "").lower() != "admin" and int(lead.assigned_setter_slot or 0) != int(user.setter_slot or -1):
        raise HTTPException(status_code=403, detail="Solo puedes sincronizar prospectos de tu cartera.")

    res = sync_beauty_growth_ig_lead_to_ghl(_serialize_bg_lead(lead))
    if not res.get("ok"):
        return JSONResponse(status_code=400, content={"success": False, "error": res.get("error", "No se pudo sincronizar con GoHighLevel."), "ghl": res})

    lead.ghl_synced = 1
    lead.ghl_contact_id = res.get("contact_id") or lead.ghl_contact_id
    lead.ghl_opportunity_id = res.get("opportunity_id") or lead.ghl_opportunity_id
    lead.last_touch_at = _now_iso()
    db.commit()
    db.refresh(lead)
    return {"success": True, "data": _serialize_bg_lead(lead), "ghl": res}


@router.post("/leads/bulk-action")
async def api_bg_bulk_action(
    req: BgBulkActionRequest,
    admin: BeautyGrowthUser = Depends(require_bg_admin),
    db: Session = Depends(_get_db),
):
    if req.apply_to_filter and req.filters:
        f = req.filters
        target_q = _apply_lead_filters(
            db.query(BeautyGrowthLead),
            user=admin,
            q=f.q or "",
            setter_slot=f.setter_slot or "all",
            pipeline_stage=f.pipeline_stage or "all",
            niche_category=f.niche_category or "all",
            country_region=f.country_region or "all",
            booking_platform=f.booking_platform or "all",
            min_followers=int(f.min_followers or 0),
            has_phone=f.has_phone or "all",
            has_bio=f.has_bio or "all",
            ghl_synced=f.ghl_synced or "all",
        )
        leads = target_q.all()
    elif req.lead_ids:
        leads = db.query(BeautyGrowthLead).filter(BeautyGrowthLead.id.in_(req.lead_ids)).all()
    else:
        raise HTTPException(status_code=400, detail="Selecciona prospectos o aplica la acción al filtro activo.")

    if not leads:
        return {"success": True, "affected": 0, "message": "No hay prospectos que coincidan."}

    slot_map = _get_setter_slot_map(db)
    now_iso = _now_iso()

    if req.action == "assign_setter":
        slot = int(req.target_setter_slot or 0)
        if slot not in (1, 2, 3):
            raise HTTPException(status_code=400, detail="target_setter_slot debe ser 1, 2 o 3.")
        su = slot_map.get(slot)
        for ld in leads:
            ld.assigned_setter_slot = slot
            ld.assigned_setter_email = su.email if su else f"setter{slot}@agenciaprosperia.com"
            ld.assigned_setter_name = su.name if su else f"Setter {slot} · Beauty Growth"
            ld.last_touch_at = now_iso
        db.commit()
        return {"success": True, "affected": len(leads), "action": "assign_setter", "target_setter_slot": slot}

    if req.action == "redistribute_equally":
        ordered = sorted(
            leads,
            key=lambda ld: (
                0 if ld.niche_category == "Belleza / Estética / Salón" else 1,
                0 if ld.country_region == "USA / PR" else 1,
                -(int(ld.followers_count or 0)),
                ld.id,
            ),
        )
        counts = {1: 0, 2: 0, 3: 0}
        for idx, ld in enumerate(ordered):
            slot = (idx % 3) + 1
            su = slot_map.get(slot)
            ld.assigned_setter_slot = slot
            ld.assigned_setter_email = su.email if su else f"setter{slot}@agenciaprosperia.com"
            ld.assigned_setter_name = su.name if su else f"Setter {slot} · Beauty Growth"
            counts[slot] += 1
        db.commit()
        return {"success": True, "affected": len(ordered), "action": "redistribute_equally", "distribution": counts}

    if req.action == "change_stage":
        st = (req.target_stage or "").strip()
        if st not in BEAUTY_GROWTH_PIPELINE_STAGES:
            raise HTTPException(status_code=400, detail="Etapa destino inválida.")
        for ld in leads:
            ld.pipeline_stage = st
            ld.last_touch_at = now_iso
        db.commit()
        return {"success": True, "affected": len(leads), "action": "change_stage", "target_stage": st}

    if req.action == "sync_ghl_batch":
        batch = leads[:50]
        synced_ok = 0
        failed = 0
        errors: List[str] = []
        for ld in batch:
            res = sync_beauty_growth_ig_lead_to_ghl(_serialize_bg_lead(ld))
            if res.get("ok"):
                ld.ghl_synced = 1
                ld.ghl_contact_id = res.get("contact_id") or ld.ghl_contact_id
                ld.ghl_opportunity_id = res.get("opportunity_id") or ld.ghl_opportunity_id
                ld.last_touch_at = now_iso
                synced_ok += 1
            else:
                failed += 1
                if len(errors) < 5:
                    errors.append(f"@{ld.ig_username}: {res.get('error', 'error')}")
        db.commit()
        return {
            "success": True,
            "action": "sync_ghl_batch",
            "processed": len(batch),
            "synced_ok": synced_ok,
            "failed": failed,
            "errors": errors,
            "capped_to_50": len(leads) > 50,
        }

    raise HTTPException(status_code=400, detail=f"Acción en lote no soportada: {req.action}")


@router.post("/leads/import-excel")
async def api_bg_import_excel(
    file: UploadFile = File(...),
    assign_mode: str = Form("equitable"),
    admin: BeautyGrowthUser = Depends(require_bg_admin),
    db: Session = Depends(_get_db),
):
    raw_bytes = await file.read()
    if not raw_bytes:
        raise HTTPException(status_code=400, detail="El archivo está vacío.")

    parsed = parse_instagram_spreadsheet_bytes(raw_bytes, file.filename or "import.xlsx")
    if not parsed:
        raise HTTPException(status_code=400, detail="No se detectaron filas válidas de Instagram en el archivo (.xlsx o .csv).")

    merged = merge_lead_dicts(parsed)
    slot_map = _get_setter_slot_map(db)
    now_iso = _now_iso()

    existing_rows = db.query(BeautyGrowthLead).all()
    existing_by_user = {r.ig_username.lower(): r for r in existing_rows}

    inserted = 0
    updated = 0
    new_idx = 0
    fixed_slot = int(assign_mode) if assign_mode in ("1", "2", "3") else 0

    for rec in merged:
        uname = (rec.get("ig_username") or "").lower()
        if not uname:
            continue
        cur = existing_by_user.get(uname)
        if cur:
            # Enriquecer sin borrar el avance comercial ni notas del equipo
            if len(rec.get("biography") or "") > len(cur.biography or ""):
                cur.biography = rec["biography"]
            if len(rec.get("ai_diagnostic_note") or "") > len(cur.ai_diagnostic_note or ""):
                cur.ai_diagnostic_note = rec["ai_diagnostic_note"]
            if not cur.phone_e164 and rec.get("phone_e164"):
                cur.phone_raw = rec.get("phone_raw") or ""
                cur.phone_e164 = rec["phone_e164"]
            if not cur.email_primary and rec.get("email_primary"):
                cur.email_primary = rec["email_primary"]
            if rec.get("email_secondary") and not cur.email_secondary:
                cur.email_secondary = rec["email_secondary"]
            if not cur.website_url and rec.get("website_url"):
                cur.website_url = rec["website_url"]
                cur.booking_platform = rec.get("booking_platform") or "Web Propia"
            if not cur.ig_profile_pic_url and rec.get("ig_profile_pic_url"):
                cur.ig_profile_pic_url = rec["ig_profile_pic_url"]
            cur.followers_count = max(int(cur.followers_count or 0), int(rec.get("followers_count") or 0))
            cur.following_count = max(int(cur.following_count or 0), int(rec.get("following_count") or 0))
            if fixed_slot in (1, 2, 3):
                su = slot_map.get(fixed_slot)
                cur.assigned_setter_slot = fixed_slot
                cur.assigned_setter_email = su.email if su else f"setter{fixed_slot}@agenciaprosperia.com"
                cur.assigned_setter_name = su.name if su else f"Setter {fixed_slot} · Beauty Growth"
            updated += 1
        else:
            slot = fixed_slot if fixed_slot in (1, 2, 3) else ((new_idx % 3) + 1)
            new_idx += 1
            su = slot_map.get(slot)
            lead_obj = BeautyGrowthLead(
                ig_username=uname,
                ig_profile_url=rec.get("ig_profile_url") or "",
                ig_profile_pic_url=rec.get("ig_profile_pic_url") or "",
                is_business=int(rec.get("is_business") or 0),
                followers_count=int(rec.get("followers_count") or 0),
                following_count=int(rec.get("following_count") or 0),
                full_name=rec.get("full_name") or "",
                first_name=rec.get("first_name") or "",
                last_name=rec.get("last_name") or "",
                email_primary=rec.get("email_primary") or "",
                email_secondary=rec.get("email_secondary") or "",
                phone_raw=rec.get("phone_raw") or "",
                phone_e164=rec.get("phone_e164") or "",
                biography=rec.get("biography") or "",
                website_url=rec.get("website_url") or "",
                booking_platform=rec.get("booking_platform") or "Sin Web",
                location_raw=rec.get("location_raw") or "",
                city=rec.get("city") or "",
                country_region=rec.get("country_region") or "LATAM / Otros",
                niche_category=rec.get("niche_category") or "Belleza / Estética / Salón",
                pipeline_stage="1. Prospecto identificado",
                assigned_setter_slot=slot,
                assigned_setter_email=su.email if su else f"setter{slot}@agenciaprosperia.com",
                assigned_setter_name=su.name if su else f"Setter {slot} · Beauty Growth",
                offer_package="BEAUTY_ELEVATE_2499",
                quoted_amount=0.0,
                ai_diagnostic_note=rec.get("ai_diagnostic_note") or "",
                setter_notes="",
                source_file=rec.get("source_file") or (file.filename or "excel_upload"),
                created_at=now_iso,
            )
            db.add(lead_obj)
            existing_by_user[uname] = lead_obj
            inserted += 1

    db.commit()
    return {
        "success": True,
        "data": {
            "rows_read": len(parsed),
            "unique_accounts": len(merged),
            "inserted": inserted,
            "updated_merged": updated,
            "assign_mode": assign_mode,
        },
    }


@router.get("/leads/export.csv")
async def api_bg_export_csv(
    q: str = "",
    setter_slot: str = "all",
    pipeline_stage: str = "all",
    niche_category: str = "all",
    country_region: str = "all",
    booking_platform: str = "all",
    min_followers: int = 0,
    has_phone: str = "all",
    has_bio: str = "all",
    ghl_synced: str = "all",
    user: BeautyGrowthUser = Depends(get_current_bg_user),
    db: Session = Depends(_get_db),
):
    rows = _apply_lead_filters(
        db.query(BeautyGrowthLead),
        user=user,
        q=q,
        setter_slot=setter_slot,
        pipeline_stage=pipeline_stage,
        niche_category=niche_category,
        country_region=country_region,
        booking_platform=booking_platform,
        min_followers=min_followers,
        has_phone=has_phone,
        has_bio=has_bio,
        ghl_synced=ghl_synced,
    ).order_by(BeautyGrowthLead.followers_count.desc(), BeautyGrowthLead.id.asc()).all()

    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow([
        "ID", "IG Username", "IG Profile URL", "Nombre Completo", "Seguidores", "Seguidos",
        "Teléfono E.164", "Email Principal", "Email Secundario", "Ubicación", "Región",
        "Nicho", "Plataforma Agenda", "Sitio Web", "Etapa 14 Pipeline", "Setter Asignado",
        "Email Setter", "Biografía / Descripción Instagram", "Diagnóstico IA", "Notas Setter",
        "Sincronizado GHL", "GHL Contact ID", "GHL Opportunity ID", "Origen Archivo",
    ])
    for r in rows:
        writer.writerow([
            r.id, r.ig_username, r.ig_profile_url, r.full_name, r.followers_count, r.following_count,
            r.phone_e164, r.email_primary, r.email_secondary, r.location_raw, r.country_region,
            r.niche_category, r.booking_platform, r.website_url, r.pipeline_stage,
            r.assigned_setter_name, r.assigned_setter_email, r.biography, r.ai_diagnostic_note,
            r.setter_notes, "Sí" if r.ghl_synced else "No", r.ghl_contact_id, r.ghl_opportunity_id,
            r.source_file,
        ])

    csv_bytes = ("\ufeff" + out.getvalue()).encode("utf-8")
    return Response(
        content=csv_bytes,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="beauty_growth_leads_filtrados.csv"'},
    )


@router.get("/team")
async def api_bg_get_team(user: BeautyGrowthUser = Depends(get_current_bg_user), db: Session = Depends(_get_db)):
    users = db.query(BeautyGrowthUser).order_by(BeautyGrowthUser.setter_slot.asc(), BeautyGrowthUser.id.asc()).all()
    rows = []
    for u in users:
        item = _serialize_bg_user(u)
        if u.setter_slot in (1, 2, 3):
            q_slot = db.query(BeautyGrowthLead).filter(BeautyGrowthLead.assigned_setter_slot == u.setter_slot)
            item["metrics"] = {
                "total_assigned": q_slot.count(),
                "contacted": q_slot.filter(BeautyGrowthLead.pipeline_stage != "1. Prospecto identificado").count(),
                "meetings": q_slot.filter(BeautyGrowthLead.pipeline_stage.in_(["8. Reunión agendada", "9. Reunión confirmada", "10. Reunión realizada", "11. Propuesta enviada", "12. Negociación activa", "13. Ganado / Cierre"])).count(),
                "won": q_slot.filter(BeautyGrowthLead.pipeline_stage == "13. Ganado / Cierre").count(),
                "ghl_synced": q_slot.filter(BeautyGrowthLead.ghl_synced == 1).count(),
            }
        rows.append(item)
    return {"success": True, "data": {"team": rows}}


@router.put("/team/{setter_slot}")
async def api_bg_update_setter(
    setter_slot: int,
    req: BgSetterUpdateRequest,
    admin: BeautyGrowthUser = Depends(require_bg_admin),
    db: Session = Depends(_get_db),
):
    if setter_slot not in (1, 2, 3):
        raise HTTPException(status_code=400, detail="Solo se pueden configurar los Setters 1, 2 o 3.")
    setter = db.query(BeautyGrowthUser).filter(BeautyGrowthUser.setter_slot == setter_slot).first()
    if not setter:
        raise HTTPException(status_code=404, detail=f"Setter {setter_slot} no encontrado.")

    new_email = normalize_email(req.email)
    if not new_email or "@" not in new_email:
        raise HTTPException(status_code=400, detail="Ingresa un correo electrónico válido.")

    clash = db.query(BeautyGrowthUser).filter(
        BeautyGrowthUser.email == new_email,
        BeautyGrowthUser.id != setter.id,
    ).first()
    if clash:
        raise HTTPException(status_code=409, detail=f"El correo {new_email} ya pertenece a otro usuario de Beauty Growth.")

    old_email = setter.email
    setter.name = req.name.strip() or f"Setter {setter_slot} · Beauty Growth"
    setter.email = new_email
    setter.phone = (req.phone or "").strip()
    if req.is_active is not None:
        setter.is_active = 1 if int(req.is_active) else 0
    if req.new_password and req.new_password.strip():
        setter.password_hash = hash_password(req.new_password.strip())

    # Actualizar sesiones activas del Setter anterior si cambió su correo y propagar a sus leads
    if old_email != new_email:
        db.query(BeautyGrowthSession).filter(BeautyGrowthSession.email == old_email).update({"email": new_email})

    db.query(BeautyGrowthLead).filter(BeautyGrowthLead.assigned_setter_slot == setter_slot).update({
        "assigned_setter_email": new_email,
        "assigned_setter_name": setter.name,
    })
    db.commit()
    db.refresh(setter)
    return {"success": True, "data": _serialize_bg_user(setter)}

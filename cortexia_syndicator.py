"""Sindicación pública automática, indexación de videos de YouTube e IndexNow 24/7 para Agencia Prosper IA."""

from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import threading
import time
from typing import Any, Dict, List, Optional
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

BASE_DIR = Path(__file__).resolve().parent
CONTENT_DIR = BASE_DIR / "content"
PUBLISHED_DIR = CONTENT_DIR / "editorial_published"
BLOG_STATIC_DIR = BASE_DIR / "static" / "blog"
REGISTRY_PATH = CONTENT_DIR / "syndication_registry.json"

SITE_URL = "https://agenciaprosperia.com"
YOUTUBE_CHANNEL_ID = "UCES2Wk2rP1_jsK4ywih1-TA"
YOUTUBE_CHANNEL_URL = "https://www.youtube.com/@AgenciaProsper_IA"
INDEXNOW_KEY = "777prosperiaindexnow2026edward"
EXMA_SPRINT_CUTOFF = datetime(2026, 12, 6, 0, 0, 0, tzinfo=ZoneInfo("America/New_York"))

PUBLISHED_DIR.mkdir(parents=True, exist_ok=True)
BLOG_STATIC_DIR.mkdir(parents=True, exist_ok=True)

_WORKER_LOCK = threading.Lock()
_WORKER_STARTED = False
_TELEGRAPH_TOKEN_CACHE: Optional[str] = None

# Catálogo semilla de los 8 videos estratégicos de YouTube (@AgenciaProsper_IA)
YOUTUBE_SEED_VIDEOS: List[Dict[str, Any]] = [
    {
        "video_id": "HVzuReRZwnU",
        "slug": "claude-vs-chatgpt-work-gemini-spark-prueba-real-empresas",
        "title": "Claude Co-Work vs ChatGPT Work vs Gemini Spark: Prueba Real con 5 Archivos Empresariales",
        "lane": "radar-disrupcion",
        "country_focus": "México y Latinoamérica (CDMX, Monterrey, Guadalajara, Bogotá y Buenos Aires)",
        "hook": "Comparar Claude vs ChatGPT no es un debate de moda: pusimos a competir a Claude Co-Work, ChatGPT Work y Gemini Spark frente a 5 archivos operativos reales para saber cuál sostiene criterio directivo y cuál falla en producción.",
        "takeaways": [
            "Por qué la mayoría de PyMEs y corporativos pierden tiempo usando prompts sueltos en ChatGPT sin flujos auditables.",
            "Dónde destaca Claude en síntesis documental compleja y dónde fallan las implementaciones sin gobernanza de datos.",
            "Cómo elegir una arquitectura multimodelo con PassportAI y Metodología SVE90 sin casarse ciegamente con una sola API.",
        ],
    },
    {
        "video_id": "PA0pqGGyzQE",
        "slug": "como-ganar-dinero-clientes-claude-agentes-ia-empresas",
        "title": "Cómo Ganar Dinero y Conseguir Clientes con Claude y Agentes de IA en 2026",
        "lane": "criterio-edward",
        "country_focus": "México, Colombia, Argentina, Perú y mercado hispano en Miami",
        "hook": "Quien hoy ofrece solo 'hacer dibujitos o textos con IA' compite por centavos; quien instala sistemas comerciales que responden en 3 segundos y convierten leads por WhatsApp vende infraestructura de alto valor.",
        "takeaways": [
            "Cómo pasar de enseñar trucos básicos a entregar un Sitio Web Inteligente + Chatbot Recepcionista IA 24/7 + CRM listo en 7 días.",
            "Por qué la Inteligencia Financiera del libro Las 4 Inteligencias exige conectar cada automatización con ingresos medibles.",
            "Cómo escalar desde una oferta entrada para PyMEs hacia proyectos corporativos de ingeniería SVE90.",
        ],
    },
    {
        "video_id": "X-T1Hv-siPM",
        "slug": "chatgpt-work-vs-claude-arquitectura-ia-empresarial",
        "title": "ChatGPT Work vs Claude: Cómo Elegir la Arquitectura de IA Correcta para tu Empresa",
        "lane": "laboratorio-prosperia",
        "country_focus": "Corporativos en México, Perú, Chile y EE. UU.",
        "hook": "Cuando las grandes plataformas copian funciones entre sí cada semana, la ventaja de una empresa no está en la herramienta de turno, sino en la soberanía de su conocimiento y sus procesos.",
        "takeaways": [
            "Qué cambia operativamente cuando el conocimiento corporativo vive en un RAG privado gobernado y no en chats aislados.",
            "Los riesgos de filtrar nóminas, contratos o historiales clínicos en cuentas personales sin control administrativo.",
            "Arquitectura técnica con equipo senior (FIUBA Argentina, México y Miami) en agenciaprosperia.com/ia.",
        ],
    },
    {
        "video_id": "fZ9dFuq4MRc",
        "slug": "anthropic-alerta-ia-mejorarse-sola-las-4-inteligencias",
        "title": "Anthropic Alerta: ¿La IA Está Cerca de Mejorarse Sola? Impacto Directivo y Las 4 Inteligencias",
        "lane": "cuatro-inteligencias",
        "country_focus": "Directores y fundadores en Latinoamérica y España",
        "hook": "La aceleración de los ciclos de entrenamiento y validación técnica obliga a cualquier CEO o director médico a replantear sus 4 Inteligencias antes de quedar fuera de juego en los próximos trimestres.",
        "takeaways": [
            "Diferencia crítica entre la velocidad del laboratorio de IA y la velocidad real de adopción humana en tu empresa.",
            "Cómo aplicar la Inteligencia Emocional y Estratégica descrita en el libro Las 4 Inteligencias para liderar cambios sin parálisis.",
            "Por qué esperar 18 meses a ver qué pasa convierte a una empresa rentable en un negocio rezagado.",
        ],
    },
    {
        "video_id": "12grSW22-HY",
        "slug": "7-tareas-agente-ia-empresa-24-7-mexico-latinoamerica",
        "title": "7 Tareas que un Agente de IA Puede Hacer por tu Empresa 24/7 en México y Latinoamérica",
        "lane": "inteligencia-clinicas",
        "country_focus": "Clínicas, despachos, inmobiliarias y empresas B2B en México, Argentina y Perú",
        "hook": "Tu mejor vendedor humano no debería gastar el 70% de su jornada respondiendo las mismas 15 preguntas por WhatsApp ni cargando leads fríos a mano.",
        "takeaways": [
            "Las 7 tareas concretas: calificación inmediata 24/7, agendamiento en calendario, reactivación de base antigua, resumen de llamadas y seguimiento omnicanal.",
            "Por qué la OIT demuestra que el 25% de la fuerza laboral se transforma por tareas en lugar de desaparecer.",
            "Cómo iniciar hoy en 7 días con el Plan Impulso (Web Inteligente + Bot IA + 3 meses gratis de CRM).",
        ],
    },
    {
        "video_id": "KHuvaWLDaKk",
        "slug": "por-que-empresas-gastan-4x-en-ia-sin-ganancias-sve90",
        "title": "Por Qué las Empresas Gastan 4 Veces Más en IA sin Ver Ganancias (Y Cómo Corregirlo con SVE90)",
        "lane": "laboratorio-prosperia",
        "country_focus": "CEOs y directores financieros en México, Argentina y Colombia",
        "hook": "Pagar docenas de licencias aisladas de IA para empleados que no cambian sus flujos de trabajo multiplica el gasto tecnológico sin mover ni un punto el margen neto.",
        "takeaways": [
            "El error de comprar software sin Auditoría previa de procesos ni Procedimientos Operativos Estándar (SOPs).",
            "Las 3 fases de La Metodología SVE90: Auditoría, Automatización con retorno en 90 días y Adopción del equipo.",
            "Centralización ejecutiva en PassportAI para evitar la dispersión de suscripciones inconexas.",
        ],
    },
    {
        "video_id": "WZ0hHoRWN4A",
        "slug": "la-ia-superara-procesos-humanos-guia-profesionales-30-40-50",
        "title": "La IA Superará Procesos Humanos en 1,000 Días: Guía para Profesionales de 30, 40 y 50+ Años",
        "lane": "cuatro-inteligencias",
        "country_focus": "Profesionales, médicos, abogados, contadores y empresarios de 30 a 50+ años en LATAM",
        "hook": "El mayor riesgo para los profesionales de 30, 40 y 50+ años en Latinoamérica no es su edad ni su falta de talento: es postergar el uso estratégico de la IA por miedo a quedar obsoletos.",
        "takeaways": [
            "Tu experiencia de 15 o 25 años multiplicada por Inteligencia de Aumento Tecnológico te vuelve imposible de reemplazar por un principiante.",
            "Caso real: la experiencia de Edward Jiménez tras 25 años arquitecturando sistemas críticos en Banco Azteca, SYNETCOM y JPX Miami.",
            "Hoja de ruta práctica del libro Las 4 Inteligencias (ISBN 979-8-9824777-0-5 · LCCN 2026970390) para monetizar tu criterio.",
        ],
    },
    {
        "video_id": "BUxBQxHo1OY",
        "slug": "integrar-inteligencia-artificial-sin-despedir-equipo-sve90",
        "title": "El Secreto para Integrar Inteligencia Artificial en tu Negocio sin Despedir a tu Equipo",
        "lane": "criterio-edward",
        "country_focus": "Empresas familiares y PyMEs en México, Argentina, Perú y Miami",
        "hook": "El Anthropic Economic Index analizó 1 millón de usos reales de Claude y confirmó que el 57% corresponde a aumento de la capacidad humana frente a un 43% de automatización directa.",
        "takeaways": [
            "Cómo vencer la resistencia interna del equipo comercial y administrativo mediante Inteligencia Emocional aplicada.",
            "Por qué dotar a cada colaborador de un copiloto en PassportAI multiplica las citas atendidas sin inflar la nómina.",
            "Cómo tu equipo pasa de responder tarde a cerrar operaciones con apoyo de agentes autónomos.",
        ],
    },
]


def is_exma_active() -> bool:
    """Devuelve True hasta el 5 de diciembre de 2026 (hora de Miami) para activar el sprint de boletos EXMA."""
    now_miami = datetime.now(ZoneInfo("America/New_York"))
    return now_miami < EXMA_SPRINT_CUTOFF


def _exma_html_block() -> str:
    if is_exma_active():
        return (
            '<h2>Presentación en Vivo: EXMA Miami (4 y 5 de Diciembre en Fort Lauderdale)</h2>'
            '<p>Edward Jiménez presentará en el escenario principal de <strong>EXMA Miami 2026</strong> '
            '(4 y 5 de diciembre en el Broward County Convention Center / Fort Lauderdale, FL) los principios '
            'de <strong>Las 4 Inteligencias</strong> y sistemas comerciales autónomos. Si deseas acompañarnos en persona '
            'con beneficio especial, revisa las opciones en '
            '<a href="https://agenciaprosperia.com/exmaboletos">agenciaprosperia.com/exmaboletos</a> '
            'o los pases corporativos VIP en <a href="https://agenciaprosperia.com/exmamiami">agenciaprosperia.com/exmamiami</a>.</p>'
        )
    return (
        '<h2>Del Escenario de EXMA Miami a tu Operación Empresarial</h2>'
        '<p>Los marcos estratégicos presentados por Edward Jiménez en <strong>EXMA Miami</strong> ahora están '
        'disponibles para tu empresa a través del libro oficial <strong>Las 4 Inteligencias</strong> '
        '(<a href="https://agenciaprosperia.com/libro">agenciaprosperia.com/libro</a>) y los entrenamientos en vivo '
        'para Latinoamérica y EE. UU.</p>'
    )


def _slugify(text: str) -> str:
    clean = text.lower().strip()
    replacements = {
        "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ü": "u", "ñ": "n",
    }
    for src, dst in replacements.items():
        clean = clean.replace(src, dst)
    clean = re.sub(r"[^a-z0-9]+", "-", clean).strip("-")
    return clean[:78].rstrip("-") or f"prosperia-{int(time.time())}"


def _build_youtube_article_dict(spec: Dict[str, Any], published_at: Optional[str] = None) -> Dict[str, Any]:
    """Construye el paquete JSON canónico para un artículo con video de YouTube indexado."""
    slug = spec["slug"]
    title = spec["title"]
    vid = spec["video_id"]
    lane = spec.get("lane", "radar-disrupcion")
    country_focus = spec.get("country_focus", "México, Argentina, Perú, Colombia y Estados Unidos")
    hook = spec.get("hook") or (
        f"Análisis ejecutivo de Edward Jiménez sobre {title} aplicado a empresas, clínicas y profesionales en {country_focus}."
    )
    takeaways = spec.get("takeaways") or [
        "Cómo evitar quedar obsoleto frente a la aceleración tecnológica independientemente de si tienes 30, 40 o 50+ años.",
        "Cómo conectar la Inteligencia Estratégica con herramientas prácticas bajo la Metodología SVE90.",
        "Ruta clara para pasar de pruebas básicas con IA a un sistema comercial activo 24/7.",
    ]
    li_items = "".join(f"<li>{t}</li>" for t in takeaways)
    yt_url = f"https://www.youtube.com/watch?v={vid}"
    pub_iso = published_at or datetime.now(timezone.utc).isoformat()

    content_html = (
        f"<p><strong>{hook}</strong></p>"
        f"<p>En este análisis en video publicado en el canal oficial "
        f"<a href=\"{yt_url}\">@AgenciaProsper_IA</a>, <strong>Edward Jiménez</strong> —fundador de "
        f"<strong>Agencia Prosper IA LLC</strong> (<em>dos poderosas palabras: Prosperar e Inteligencia Artificial, unidas para ti</em>) "
        f"y autor del libro oficial <strong>Las 4 Inteligencias</strong>— desglosa lo que realmente funciona en producción para {country_focus}.</p>"
        f"<h2>Puntos Clave del Video ({title})</h2>"
        f"<ul>{li_items}</ul>"
        f"<h2>Evidencia Real y Criterio Directivo (Sin Trucos Básicos)</h2>"
        f"<p>De acuerdo con el <strong>Stanford HAI AI Index 2025</strong>, el <strong>78%</strong> de las organizaciones encuestadas ya utiliza "
        f"inteligencia artificial (frente al 55% del año anterior). Al mismo tiempo, la <strong>Organización Internacional del Trabajo (OIT)</strong> "
        f"señala que alrededor del <strong>25%</strong> de los puestos está expuesto a la IA generativa bajo un enfoque de transformación de tareas, "
        f"y el <strong>Anthropic Economic Index</strong> (sobre 1 millón de usos reales de Claude) confirma que el <strong>57%</strong> corresponde a "
        f"aumento de capacidad humana.</p>"
        f"<p>Tras más de 25 años liderando sistemas de misión crítica —incluyendo la migración bancaria nocturna de 1,500 sucursales de Grupo Elektra "
        f"y Banco Azteca bajo supervisión de la CNBV en México, arquitectura telecom en SYNETCOM y operaciones en JPX Miami—, Edward Jiménez advierte "
        f"el mismo patrón: quienes solo consumen trucos aislados se frustran, mientras quienes integran gobernanza e infraestructura ganan mercado.</p>"
        f"<h2>Evangelización para Profesionales de 30, 40 y 50+ Años y Las 4 Inteligencias</h2>"
        f"<p>Nuestro movimiento nace con una convicción firme: <strong>ningún profesional, médico, abogado, empresario o dueño de negocio de 30, 40 o 50+ años "
        f"en Latinoamérica debe quedar obsoleto por temor a la tecnología</strong>. En el libro oficial "
        f"<a href=\"https://agenciaprosperia.com/libro\"><strong>Las 4 Inteligencias</strong></a> "
        f"(ISBN-13: <code>979-8-9824777-0-5</code>, Library of Congress <code>LCCN: 2026970390</code>, prólogo de Fernando Anzures, disponible en "
        f"<a href=\"https://www.amazon.com/dp/B0HS33VP6C?th=1\">Amazon</a>), integramos las cuatro dimensiones clave: "
        f"<strong>Inteligencia Financiera, Emocional, Estratégica y de Aumento Tecnológico</strong>.</p>"
        f"<h2>Cómo Implementarlo Hoy: De PyMEs a Corporativos</h2>"
        f"<ul>"
        f"<li><strong>Para Negocios y Clínicas (Flujo Inmediato en 7 días):</strong> Activamos tu Sitio Web Inteligente + Chatbot Recepcionista IA 24/7 + CRM en "
        f"<a href=\"https://agenciaprosperia.com/crm-saas\">agenciaprosperia.com/crm-saas</a> para capturar y cerrar prospectos sin fricción por WhatsApp.</li>"
        f"<li><strong>Para Directores y Corporativos en México, Argentina, Perú y EE. UU.:</strong> Nuestra división de ingeniería en "
        f"<a href=\"https://agenciaprosperia.com/ia\">agenciaprosperia.com/ia</a> despliega sistemas <strong>SVE90</strong>, RAG privado y agentes autónomos "
        f"respaldados por <strong>20 ingenieros de alto calibre entre FIUBA (Argentina), México y Miami</strong>.</li>"
        f"<li><strong>Plataforma Centralizada:</strong> Todo el ecosistema opera conectado a <a href=\"https://passportai.app\">PassportAI.app</a> "
        f"(registros federales U.S. Copyright Cases #1-15304798691, #1-15304799169 y #1-15304997611).</li>"
        f"</ul>"
        f"{_exma_html_block()}"
        f"<p><strong>Mira el análisis completo en YouTube:</strong> <a href=\"{yt_url}\">{yt_url}</a></p>"
    )

    return {
        "slug": slug,
        "title": title,
        "summary": hook,
        "content": content_html,
        "lane": lane,
        "author": "Edward Jiménez",
        "author_type": "person",
        "status": "published",
        "reviewed_by": "Edward Jiménez",
        "author_approved": True,
        "youtube_video_id": vid,
        "youtube_url": yt_url,
        "sources": [
            {"title": f"Video Oficial en YouTube (@AgenciaProsper_IA): {title}", "url": yt_url},
            {"title": "Stanford HAI AI Index Report 2025", "url": "https://hai.stanford.edu/ai-index/2025-ai-index-report"},
            {"title": "Anthropic Economic Index", "url": "https://www.anthropic.com/research/the-anthropic-economic-index"},
            {"title": "Libro Oficial Las 4 Inteligencias (LCCN 2026970390)", "url": "https://agenciaprosperia.com/libro"},
        ],
        "cta": "diagnostic",
        "editorial_notes": "Generado por Cortexia Syndicator con video oficial indexado de @AgenciaProsper_IA.",
        "published_at": pub_iso,
        "image_url": f"/static/blog/{slug}.jpg",
    }


def _ensure_cover_image(slug: str, title: str, summary: str, lane_name: str, video_id: Optional[str] = None) -> None:
    """Genera portada JPEG si no existe (usando render_blog_cover_pillow o miniatura de YouTube)."""
    cover_file = BLOG_STATIC_DIR / f"{slug}.jpg"
    if cover_file.exists() and cover_file.stat().st_size > 10_000:
        return
    try:
        from cortexia_renderer import render_blog_cover_pillow
        render_blog_cover_pillow(title=title, subtitle=summary, lane_name=lane_name, output_path=cover_file)
        return
    except Exception:
        pass
    if video_id:
        for res in ("hqdefault.jpg", "sddefault.jpg"):
            try:
                req = urllib.request.Request(f"https://i.ytimg.com/vi/{video_id}/{res}", headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=10) as r:
                    cover_file.write_bytes(r.read())
                return
            except Exception:
                continue


def fetch_youtube_rss_videos() -> List[Dict[str, str]]:
    """Lee el feed RSS público de @AgenciaProsper_IA para detectar videos publicados."""
    rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={YOUTUBE_CHANNEL_ID}"
    try:
        req = urllib.request.Request(rss_url, headers={"User-Agent": "Mozilla/5.0"})
        xml_data = urllib.request.urlopen(req, timeout=15).read().decode("utf-8")
        root = ET.fromstring(xml_data)
        ns = {"atom": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015"}
        results = []
        for entry in root.findall("atom:entry", ns):
            vid_el = entry.find("yt:videoId", ns)
            title_el = entry.find("atom:title", ns)
            pub_el = entry.find("atom:published", ns)
            if vid_el is not None and title_el is not None:
                results.append({
                    "video_id": vid_el.text.strip(),
                    "title": title_el.text.strip(),
                    "published_at": pub_el.text.strip() if pub_el is not None else datetime.now(timezone.utc).isoformat(),
                })
        return results
    except Exception as e:
        print(f"⚠️ [SYNDICATOR] No se pudo leer RSS de YouTube: {e}", flush=True)
        return []


def _load_registry() -> Dict[str, Any]:
    merged: Dict[str, Any] = {"telegraph": {}, "devto": {}, "hashnode": {}, "indexnow_last": None, "articles": {}}
    data_reg_path = BASE_DIR / "data" / "syndication_registry.json"
    for candidate in (data_reg_path, REGISTRY_PATH):
        if not candidate.exists():
            continue
        try:
            loaded = json.loads(candidate.read_text(encoding="utf-8"))
            for section in ("telegraph", "devto", "hashnode", "articles"):
                if isinstance(loaded.get(section), dict):
                    merged[section].update(loaded[section])
            if loaded.get("indexnow_last"):
                merged["indexnow_last"] = loaded["indexnow_last"]
        except Exception:
            pass
    return merged


def _save_registry(reg: Dict[str, Any]) -> None:
    serialized = json.dumps(reg, ensure_ascii=False, indent=2) + "\n"
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.write_text(serialized, encoding="utf-8")
    data_dir = BASE_DIR / "data"
    if data_dir.exists():
        (data_dir / "syndication_registry.json").write_text(serialized, encoding="utf-8")


def ensure_youtube_articles_published(normalize_existing: bool = True) -> List[str]:
    """Asegura artículos completos publicados para todos los videos semilla y nuevos del canal @AgenciaProsper_IA."""
    from editorial import LANES

    known_by_vid: Dict[str, Dict[str, Any]] = {}
    if normalize_existing:
        for path in PUBLISHED_DIR.glob("*.json"):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                changed = False
                if data.get("status") != "published":
                    data["status"] = "published"
                    changed = True
                if data.get("author") != "Edward Jiménez" or not data.get("author_approved"):
                    data["author"] = "Edward Jiménez"
                    data["author_type"] = "person"
                    data["author_approved"] = True
                    changed = True
                if changed:
                    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                if data.get("youtube_video_id"):
                    known_by_vid[data["youtube_video_id"]] = data
            except Exception as e:
                print(f"⚠️ [SYNDICATOR] Error normalizando {path.name}: {e}", flush=True)

    rss_videos = fetch_youtube_rss_videos()
    rss_dates = {v["video_id"]: v["published_at"] for v in rss_videos}

    created_slugs: List[str] = []
    # 1. Seed estratégico (incluyendo Claude vs ChatGPT HVzuReRZwnU y los 8 pilares)
    for spec in YOUTUBE_SEED_VIDEOS:
        slug = spec["slug"]
        pub_path = PUBLISHED_DIR / f"{slug}.json"
        if not pub_path.exists():
            article = _build_youtube_article_dict(spec, published_at=rss_dates.get(spec["video_id"]))
            pub_path.write_text(json.dumps(article, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            created_slugs.append(slug)
        else:
            article = json.loads(pub_path.read_text(encoding="utf-8"))
            if not article.get("youtube_video_id"):
                article["youtube_video_id"] = spec["video_id"]
                article["youtube_url"] = f"https://www.youtube.com/watch?v={spec['video_id']}"
                pub_path.write_text(json.dumps(article, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        known_by_vid[spec["video_id"]] = article
        _ensure_cover_image(slug, article["title"], article["summary"], LANES.get(article.get("lane", "radar-disrupcion"), "Radar de Disrupción"), spec["video_id"])

    # 2. Cualquier video nuevo detectado en el RSS del canal
    for v in rss_videos:
        vid = v["video_id"]
        if vid in known_by_vid:
            continue
        slug = _slugify(v["title"])
        pub_path = PUBLISHED_DIR / f"{slug}.json"
        if pub_path.exists():
            slug = f"{slug}-{vid[:4].lower()}"
            pub_path = PUBLISHED_DIR / f"{slug}.json"
        spec = {
            "video_id": vid,
            "slug": slug,
            "title": v["title"],
            "lane": "radar-disrupcion",
            "country_focus": "México, Argentina, Perú, Colombia y Miami",
        }
        article = _build_youtube_article_dict(spec, published_at=v["published_at"])
        pub_path.write_text(json.dumps(article, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        _ensure_cover_image(slug, article["title"], article["summary"], "Radar de Disrupción", vid)
        created_slugs.append(slug)

    # Sincronizar hacia SQLite si ya existe tabla BlogPost
    try:
        from database import SessionLocal, sync_blog_posts
        db = SessionLocal()
        try:
            sync_blog_posts(db)
        finally:
            db.close()
    except Exception as e:
        print(f"⚠️ [SYNDICATOR] Sync SQLite diferido: {e}", flush=True)

    return created_slugs


class _TelegraphHTMLParser(HTMLParser):
    """Convierte HTML editorial a lista de nodos JSON válidos para la API de Telegraph."""

    TAG_MAP = {"h1": "h3", "h2": "h3", "h4": "h4", "b": "strong", "div": "p"}
    ALLOWED = {
        "a", "aside", "b", "blockquote", "br", "code", "em", "figcaption", "figure",
        "h3", "h4", "hr", "i", "iframe", "img", "li", "ol", "p", "pre", "s", "strong", "u", "ul",
    }

    def __init__(self) -> None:
        super().__init__()
        self.root: List[Any] = []
        self.stack: List[tuple] = [(None, self.root)]

    def handle_starttag(self, tag: str, attrs: list) -> None:
        tag = self.TAG_MAP.get(tag.lower(), tag.lower())
        if tag not in self.ALLOWED:
            return
        node: Dict[str, Any] = {"tag": tag}
        attr_dict = dict(attrs)
        if tag == "a" and "href" in attr_dict:
            node["attrs"] = {"href": attr_dict["href"]}
        elif tag == "img" and "src" in attr_dict:
            node["attrs"] = {"src": attr_dict["src"]}
        if tag not in ("br", "hr", "img"):
            node["children"] = []
            self.stack[-1][1].append(node)
            self.stack.append((tag, node["children"]))
        else:
            self.stack[-1][1].append(node)

    def handle_endtag(self, tag: str) -> None:
        tag = self.TAG_MAP.get(tag.lower(), tag.lower())
        for idx in range(len(self.stack) - 1, 0, -1):
            if self.stack[idx][0] == tag:
                self.stack = self.stack[:idx]
                break

    def handle_data(self, data: str) -> None:
        txt = unescape(data)
        if txt:
            self.stack[-1][1].append(txt)


def _html_to_telegraph_nodes(html_str: str, article: Dict[str, Any]) -> List[Any]:
    """Construye los nodos completos de Telegraph incluyendo portada, video YouTube y enlaces del ecosistema."""
    nodes: List[Any] = []
    slug = article["slug"]
    canonical_url = f"{SITE_URL}/blog/{slug}"
    vid = article.get("youtube_video_id")

    if vid:
        nodes.append({"tag": "figure", "children": [{"tag": "img", "attrs": {"src": f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"}}]})
        nodes.append({"tag": "p", "children": [
            {"tag": "strong", "children": ["📺 Video en YouTube: "]},
            {"tag": "a", "attrs": {"href": f"https://www.youtube.com/watch?v={vid}"}, "children": [f"Ver análisis completo en @AgenciaProsper_IA ({vid}) ↗"]},
        ]})
    else:
        img_url = article.get("image_url", "")
        full_img = f"{SITE_URL}{img_url}" if img_url.startswith("/") else img_url
        if full_img:
            nodes.append({"tag": "figure", "children": [{"tag": "img", "attrs": {"src": full_img}}]})

    parser = _TelegraphHTMLParser()
    parser.feed(html_str or "")
    parser.close()
    nodes.extend(parser.root)

    nodes.append({"tag": "hr"})
    nodes.append({"tag": "h3", "children": ["Ecosistema Agencia Prosper IA · Edward Jiménez"]})
    nodes.append({"tag": "ul", "children": [
        {"tag": "li", "children": ["Artículo original canónico: ", {"tag": "a", "attrs": {"href": canonical_url}, "children": [canonical_url]}]},
        {"tag": "li", "children": ["Libro Oficial Las 4 Inteligencias (ISBN 979-8-9824777-0-5 · LCCN 2026970390): ", {"tag": "a", "attrs": {"href": f"{SITE_URL}/libro"}, "children": [f"{SITE_URL}/libro"]}, " · ", {"tag": "a", "attrs": {"href": "https://www.amazon.com/dp/B0HS33VP6C?th=1"}, "children": ["Amazon"]}]},
        {"tag": "li", "children": ["Consultoría Corporativa IA (20 Ingenieros FIUBA Argentina, México y Miami): ", {"tag": "a", "attrs": {"href": f"{SITE_URL}/ia"}, "children": [f"{SITE_URL}/ia"]}]},
        {"tag": "li", "children": ["Sitios Web Inteligentes + Chatbot IA + CRM: ", {"tag": "a", "attrs": {"href": f"{SITE_URL}/crm-saas"}, "children": [f"{SITE_URL}/crm-saas"]}, " · Plataforma SaaS: ", {"tag": "a", "attrs": {"href": "https://passportai.app"}, "children": ["PassportAI.app"]}]},
    ]})
    if is_exma_active():
        nodes.append({"tag": "aside", "children": [
            {"tag": "strong", "children": ["🎤 EXMA Miami 2026 (4 y 5 de Diciembre · Fort Lauderdale): "]},
            "Boletos con 20% OFF en ",
            {"tag": "a", "attrs": {"href": f"{SITE_URL}/exmaboletos"}, "children": [f"{SITE_URL}/exmaboletos"]},
            " | Patrocinios VIP en ",
            {"tag": "a", "attrs": {"href": f"{SITE_URL}/exmamiami"}, "children": [f"{SITE_URL}/exmamiami"]},
        ]})
    return nodes


def _get_telegraph_token() -> str:
    global _TELEGRAPH_TOKEN_CACHE
    env_tok = os.environ.get("TELEGRAPH_ACCESS_TOKEN", "").strip()
    if env_tok:
        return env_tok
    if _TELEGRAPH_TOKEN_CACHE:
        return _TELEGRAPH_TOKEN_CACHE
    tok_cache = Path("/tmp/.prosperia_telegraph_token")
    if tok_cache.exists():
        val = tok_cache.read_text(encoding="utf-8").strip()
        if val:
            _TELEGRAPH_TOKEN_CACHE = val
            return val
    payload = json.dumps({
        "short_name": "ProsperIA",
        "author_name": "Edward Jiménez · Agencia Prosper IA",
        "author_url": f"{SITE_URL}/ia",
    }).encode("utf-8")
    req = urllib.request.Request("https://api.telegra.ph/createAccount", data=payload, method="POST")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if not data.get("ok"):
        raise RuntimeError(f"Telegraph createAccount failed: {data}")
    token = data["result"]["access_token"]
    _TELEGRAPH_TOKEN_CACHE = token
    try:
        tok_cache.write_text(token, encoding="utf-8")
    except Exception:
        pass
    return token


def syndicate_all_to_telegraph() -> Dict[str, str]:
    """Publica en telegra.ph todos los artículos publicados que aún no están registrados."""
    reg = _load_registry()
    telegraph_map = reg.setdefault("telegraph", {})
    articles_meta = reg.setdefault("articles", {})
    token = None

    for path in sorted(PUBLISHED_DIR.glob("*.json")):
        try:
            article = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if article.get("status") != "published":
            continue
        slug = article["slug"]
        articles_meta[slug] = {
            "title": article["title"],
            "url": f"{SITE_URL}/blog/{slug}",
            "youtube_video_id": article.get("youtube_video_id", ""),
            "published_at": article.get("published_at", ""),
        }
        if slug in telegraph_map and telegraph_map[slug].startswith("https://telegra.ph/"):
            continue
        if token is None:
            token = _get_telegraph_token()
        nodes = _html_to_telegraph_nodes(article.get("content", ""), article)
        payload = json.dumps({
            "access_token": token,
            "title": article["title"][:256],
            "author_name": "Edward Jiménez · Agencia Prosper IA",
            "author_url": f"{SITE_URL}/ia",
            "content": nodes,
            "return_content": False,
        }).encode("utf-8")
        for attempt in range(2):
            try:
                req = urllib.request.Request("https://api.telegra.ph/createPage", data=payload, method="POST")
                req.add_header("Content-Type", "application/json")
                with urllib.request.urlopen(req, timeout=25) as resp:
                    res = json.loads(resp.read().decode("utf-8"))
                if res.get("ok") and res.get("result", {}).get("url"):
                    telegraph_map[slug] = res["result"]["url"]
                    print(f"📰 [TELEGRAPH] Publicado: {slug} -> {telegraph_map[slug]}", flush=True)
                    time.sleep(1.0)
                    break
                err_str = str(res.get("error", ""))
                if err_str.startswith("FLOOD_WAIT_") and attempt == 0:
                    wait_sec = int(err_str.split("_")[-1]) + 1
                    print(f"⏳ [TELEGRAPH] Esperando {wait_sec}s por rate-limit en {slug}...", flush=True)
                    time.sleep(wait_sec)
                    continue
                print(f"⚠️ [TELEGRAPH] Error en {slug}: {res}", flush=True)
                break
            except Exception as e:
                print(f"⚠️ [TELEGRAPH] Excepción en {slug}: {e}", flush=True)
                break

    _save_registry(reg)
    return telegraph_map


def _html_to_markdown_simple(article: Dict[str, Any]) -> str:
    txt = article.get("content", "")
    txt = re.sub(r"<h[1-3][^>]*>(.*?)</h[1-3]>", r"\n\n## \1\n\n", txt, flags=re.S)
    txt = re.sub(r"<li[^>]*>(.*?)</li>", r"\n- \1", txt, flags=re.S)
    txt = re.sub(r"<strong[^>]*>(.*?)</strong>", r"**\1**", txt, flags=re.S)
    txt = re.sub(r"<a[^>]*href=[\"']([^\"']+)[\"'][^>]*>(.*?)</a>", r"[\2](\1)", txt, flags=re.S)
    txt = re.sub(r"</p>", "\n\n", txt)
    txt = unescape(re.sub(r"<[^>]+>", "", txt))
    vid = article.get("youtube_video_id")
    prefix = f"{{% youtube https://www.youtube.com/watch?v={vid} %}}\n\n" if vid else ""
    footer = f"\n\n---\nArtículo canónico original en [Agencia Prosper IA]({SITE_URL}/blog/{article['slug']}).\n"
    return prefix + re.sub(r"\n{3,}", "\n\n", txt).strip() + footer


def syndicate_to_devto() -> Dict[str, str]:
    """Opcional: publica vía API de Dev.to cuando DEVTO_API_KEY está configurada."""
    api_key = os.environ.get("DEVTO_API_KEY", "").strip()
    if not api_key:
        return {}
    reg = _load_registry()
    devto_map = reg.setdefault("devto", {})
    for path in sorted(PUBLISHED_DIR.glob("*.json")):
        article = json.loads(path.read_text(encoding="utf-8"))
        slug = article["slug"]
        if article.get("status") != "published" or slug in devto_map:
            continue
        payload = json.dumps({
            "article": {
                "title": article["title"][:120],
                "published": True,
                "body_markdown": _html_to_markdown_simple(article),
                "canonical_url": f"{SITE_URL}/blog/{slug}",
                "tags": ["ia", "automatizacion", "negocios", "inteligenciaartificial"],
            }
        }).encode("utf-8")
        try:
            req = urllib.request.Request("https://dev.to/api/articles", data=payload, method="POST")
            req.add_header("api-key", api_key)
            req.add_header("Content-Type", "application/json")
            req.add_header("User-Agent", "AgenciaProsperIA/1.0")
            with urllib.request.urlopen(req, timeout=20) as r:
                res = json.loads(r.read().decode("utf-8"))
            if res.get("url"):
                devto_map[slug] = res["url"]
        except Exception as e:
            print(f"⚠️ [DEVTO] {slug}: {e}", flush=True)
    _save_registry(reg)
    return devto_map


def syndicate_to_hashnode() -> Dict[str, str]:
    """Opcional: publica vía GraphQL API de Hashnode cuando HASHNODE_TOKEN y HASHNODE_PUBLICATION_ID existen."""
    token = os.environ.get("HASHNODE_TOKEN", "").strip()
    pub_id = os.environ.get("HASHNODE_PUBLICATION_ID", "").strip()
    if not token or not pub_id:
        return {}
    reg = _load_registry()
    hn_map = reg.setdefault("hashnode", {})
    mutation = """
    mutation PublishPost($input: PublishPostInput!) {
      publishPost(input: $input) { post { url } }
    }"""
    for path in sorted(PUBLISHED_DIR.glob("*.json")):
        article = json.loads(path.read_text(encoding="utf-8"))
        slug = article["slug"]
        if article.get("status") != "published" or slug in hn_map:
            continue
        payload = json.dumps({
            "query": mutation,
            "variables": {
                "input": {
                    "title": article["title"],
                    "publicationId": pub_id,
                    "contentMarkdown": _html_to_markdown_simple(article),
                    "originalArticleURL": f"{SITE_URL}/blog/{slug}",
                }
            },
        }).encode("utf-8")
        try:
            req = urllib.request.Request("https://gql.hashnode.com", data=payload, method="POST")
            req.add_header("Authorization", token)
            req.add_header("Content-Type", "application/json")
            with urllib.request.urlopen(req, timeout=20) as r:
                res = json.loads(r.read().decode("utf-8"))
            url = (res.get("data") or {}).get("publishPost", {}).get("post", {}).get("url")
            if url:
                hn_map[slug] = url
        except Exception as e:
            print(f"⚠️ [HASHNODE] {slug}: {e}", flush=True)
    _save_registry(reg)
    return hn_map


def build_indexnow_url_list() -> List[str]:
    urls = [
        f"{SITE_URL}/",
        f"{SITE_URL}/ia",
        f"{SITE_URL}/corporativos",
        f"{SITE_URL}/consultoria",
        f"{SITE_URL}/consultoriadeinteligenciaartificial",
        f"{SITE_URL}/libro",
        f"{SITE_URL}/crm-saas",
        f"{SITE_URL}/arsenal",
        f"{SITE_URL}/codigos",
        f"{SITE_URL}/blog",
        f"{SITE_URL}/intelligence",
        f"{SITE_URL}/podcast",
        f"{SITE_URL}/diagnostico",
        f"{SITE_URL}/exmaboletos",
        f"{SITE_URL}/exmamiami",
        f"{SITE_URL}/sitemap.xml",
        f"{SITE_URL}/video-sitemap.xml",
        f"{SITE_URL}/feed.xml",
    ]
    for path in sorted(PUBLISHED_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if data.get("status") == "published" and data.get("slug"):
                urls.append(f"{SITE_URL}/blog/{data['slug']}")
        except Exception:
            continue
    return list(dict.fromkeys(urls))


def notify_indexnow(urls: Optional[List[str]] = None) -> Dict[str, Any]:
    """Envía lote de URLs a api.indexnow.org para indexación inmediata en Bing/ChatGPT/Yandex."""
    url_list = urls or build_indexnow_url_list()
    payload = json.dumps({
        "host": "agenciaprosperia.com",
        "key": INDEXNOW_KEY,
        "keyLocation": f"{SITE_URL}/{INDEXNOW_KEY}.txt",
        "urlList": url_list[:10000],
    }).encode("utf-8")
    req = urllib.request.Request("https://api.indexnow.org/indexnow", data=payload, method="POST")
    req.add_header("Content-Type", "application/json; charset=utf-8")
    status_code = 0
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            status_code = resp.status
    except urllib.error.HTTPError as e:
        status_code = e.code
    except Exception as e:
        return {"status": "error", "error": str(e), "count": len(url_list)}

    reg = _load_registry()
    reg["indexnow_last"] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "http_status": status_code,
        "url_count": len(url_list),
    }
    _save_registry(reg)
    return reg["indexnow_last"]


def run_syndication_cycle(run_daily_ai_generation: bool = True) -> Dict[str, Any]:
    """Ejecuta un ciclo completo: YouTube RSS + Artículo Diario Cortexia (sin LinkedIn) + Telegraph + Dev.to/Hashnode + IndexNow."""
    created_yt = ensure_youtube_articles_published(normalize_existing=True)

    daily_ran = False
    if run_daily_ai_generation and os.environ.get("GEMINI_API_KEY"):
        today_str = datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d")
        diario_dir = CONTENT_DIR / "diario"
        already_today = diario_dir.exists() and any(diario_dir.glob(f"{today_str}_*"))
        if not already_today:
            try:
                from cortexia_engine import run_daily_pipeline
                day_idx = (datetime.now().timetuple().tm_yday % 5) + 1
                run_daily_pipeline(day_index=day_idx, date_str=today_str, publish_linkedin=False)
                daily_ran = True
            except Exception as e:
                print(f"⚠️ [SYNDICATOR] Error en ciclo diario Cortexia: {e}", flush=True)

    telegraph = syndicate_all_to_telegraph()
    devto = syndicate_to_devto()
    hashnode = syndicate_to_hashnode()
    indexnow = notify_indexnow()
    return {
        "created_youtube_articles": created_yt,
        "daily_ai_generated": daily_ran,
        "telegraph_count": len(telegraph),
        "devto_count": len(devto),
        "hashnode_count": len(hashnode),
        "indexnow": indexnow,
    }


def start_background_syndication_worker() -> None:
    """Inicia el worker matutino y nocturno 24/7 (Lunes a Domingo cada 12h, publish_linkedin=False)."""
    global _WORKER_STARTED
    with _WORKER_LOCK:
        if _WORKER_STARTED:
            return
        _WORKER_STARTED = True

    def _loop() -> None:
        time.sleep(45)
        while True:
            try:
                res = run_syndication_cycle(run_daily_ai_generation=True)
                print(f"🚀 [CORTEXIA 24/7] Ciclo completado: {json.dumps(res, ensure_ascii=False)}", flush=True)
            except Exception as exc:
                print(f"⚠️ [CORTEXIA 24/7] Error en ciclo: {exc}", flush=True)
            # Repetir cada 12 horas (mañana y noche, 7 días a la semana)
            time.sleep(12 * 3600)

    t = threading.Thread(target=_loop, name="cortexia-syndication-24x7", daemon=True)
    t.start()
    print("🌐 [CORTEXIA 24/7] Worker de Indexación y Sindicación Pública inicializado (cada 12h, L-D).", flush=True)


if __name__ == "__main__":
    summary = run_syndication_cycle(run_daily_ai_generation=False)
    print(json.dumps(summary, ensure_ascii=False, indent=2))

"""Reglas editoriales de PROSPERIA Intelligence.

La base histórica continúa en SQLite. Este módulo añade la capa de criterio,
autoría y trazabilidad sin romper las URLs ya indexadas.
"""

from html import unescape
import json
from pathlib import Path
import re


LANES = {
    "radar-disrupcion": "Radar de Disrupción",
    "criterio-edward": "Criterio de Edward",
    "inteligencia-clinicas": "Inteligencia para Clínicas",
    "laboratorio-prosperia": "Laboratorio ProsperIA",
    "cuatro-inteligencias": "Los 4 Pilares de Soberanía Empresarial",
}

LEGACY_CATEGORY_LANES = {
    "Marketing & CRM": "inteligencia-clinicas",
    "Operaciones": "laboratorio-prosperia",
    "Automatización": "laboratorio-prosperia",
    "Casos de Éxito": "laboratorio-prosperia",
}

PUBLISHED_DIR = Path(__file__).parent / "content" / "editorial_published"
STATIC_DIR = Path(__file__).parent / "static"


def published_metadata(slug: str) -> dict:
    path = PUBLISHED_DIR / f"{slug}.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def reading_minutes(html: str) -> int:
    words = re.findall(r"\b[\wáéíóúüñÁÉÍÓÚÜÑ]+\b", unescape(re.sub(r"<[^>]+>", " ", html or "")))
    return max(1, round(len(words) / 210))


def enrich_post(post: dict) -> dict:
    """Normaliza un artículo antiguo al contrato editorial nuevo."""
    metadata = published_metadata(post.get("slug", ""))
    enriched = {**post, **metadata}
    post = enriched
    lane_key = post.get("lane") or LEGACY_CATEGORY_LANES.get(post.get("category"), "radar-disrupcion")
    personal_byline_approved = bool(post.get("author_approved"))
    if post.get("author") == "Edward Jiménez" and not personal_byline_approved:
        enriched["original_author"] = post["author"]
        enriched["author"] = "Equipo editorial ProsperIA"

    # Inyección de cache-buster automático en image_url si existe el archivo local
    raw_img = enriched.get("image_url") or post.get("image_url")
    if raw_img and not (raw_img.startswith("http://") or raw_img.startswith("https://")):
        clean_img = raw_img.lstrip("/")
        if clean_img.startswith("static/"):
            clean_img = clean_img[len("static/"):]
        clean_img = clean_img.split("?")[0]
        local_file = STATIC_DIR / clean_img
        if local_file.exists():
            try:
                mtime = int(local_file.stat().st_mtime)
                enriched["image_url"] = f"/static/{clean_img}?v={mtime}"
            except OSError:
                enriched["image_url"] = f"/static/{clean_img}"
        else:
            enriched["image_url"] = f"/static/{clean_img}"

    enriched.update({
        "lane": lane_key,
        "lane_name": LANES[lane_key],
        "author_type": post.get("author_type", "person" if personal_byline_approved else "organization"),
        "reading_minutes": post.get("reading_minutes") or reading_minutes(post.get("content", "")),
        "sources": post.get("sources", []),
        "review_status": post.get("status", post.get("review_status", "legacy")),
        "cta": post.get("cta", "diagnostic"),
    })
    return enriched

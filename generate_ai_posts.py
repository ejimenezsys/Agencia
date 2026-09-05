"""Genera un borrador editorial; nunca publica ni atribuye autoría por sí solo."""

import argparse
import datetime as dt
import json
import os
from pathlib import Path

import requests

from editorial import LANES
from editorial_workflow import validate

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def build_prompt(lane: str, source_packet: str) -> str:
    return f"""
Eres investigador editorial de PROSPERIA Intelligence. Escribe UN borrador en español
para empresarios y profesionales de Latinoamérica. Ruta: {LANES[lane]}.

Explica qué cambia, qué significa para la empresa y la persona, y qué decisión merece
consideración. Distingue hechos, inferencias y opinión. No inventes cifras, casos, citas
ni fuentes. Usa exclusivamente el paquete de fuentes incluido abajo. Evita sensacionalismo,
promesas de riqueza y jerga técnica innecesaria.

No firmes como Edward Jiménez. El autor inicial es "Equipo editorial ProsperIA" con
author_type "organization". Edward solo puede firmar después de aprobar el texto.

Devuelve JSON con: slug, title, summary, content (HTML semántico), lane, author,
author_type, status="draft", reviewed_by=null, author_approved=false,
sources (copia título y URL del paquete), cta y editorial_notes.

PAQUETE DE FUENTES REVISADO:
{source_packet}
""".strip()


def generate(lane: str, source_file: Path, output_dir: Path) -> Path:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Configura GEMINI_API_KEY en el entorno.")
    source_packet = source_file.read_text(encoding="utf-8")
    if not source_packet.strip():
        raise ValueError("El paquete de fuentes está vacío.")
    response = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent",
        params={"key": api_key},
        headers={"Content-Type": "application/json"},
        json={
            "contents": [{"parts": [{"text": build_prompt(lane, source_packet)}]}],
            "generationConfig": {"responseMimeType": "application/json"},
        },
        timeout=90,
    )
    response.raise_for_status()
    post = json.loads(response.json()["candidates"][0]["content"]["parts"][0]["text"])
    post.update({
        "lane": lane,
        "status": "draft",
        "author": "Equipo editorial ProsperIA",
        "author_type": "organization",
        "reviewed_by": None,
        "author_approved": False,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    })
    errors = validate(post)
    if errors:
        raise ValueError("Borrador inválido: " + "; ".join(errors))
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f"{post['slug']}.json"
    output.write_text(json.dumps(post, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Crea un borrador basado en fuentes revisadas")
    parser.add_argument("--lane", required=True, choices=LANES)
    parser.add_argument("--sources", required=True, type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("content/editorial_drafts"))
    args = parser.parse_args()
    print(generate(args.lane, args.sources, args.output_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

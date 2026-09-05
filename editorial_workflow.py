"""Valida y mueve borradores por un flujo editorial con aprobación humana."""

import argparse
import json
from pathlib import Path
from urllib.parse import urlparse

from editorial import LANES


REQUIRED = {"slug", "title", "summary", "content", "lane", "author", "author_type", "status", "sources"}


def validate(post: dict, publish: bool = False) -> list[str]:
    errors = [f"Falta el campo: {key}" for key in sorted(REQUIRED - post.keys())]
    if post.get("lane") not in LANES:
        errors.append("La ruta editorial no es válida.")
    if post.get("author_type") not in {"person", "organization"}:
        errors.append("author_type debe ser person u organization.")
    if len(post.get("title", "")) < 20:
        errors.append("El título debe tener al menos 20 caracteres.")
    if len(post.get("summary", "")) < 50:
        errors.append("El resumen debe tener al menos 50 caracteres.")
    if len(post.get("content", "")) < 500:
        errors.append("El contenido debe tener al menos 500 caracteres.")
    for index, source in enumerate(post.get("sources", []), 1):
        if not source.get("title") or urlparse(source.get("url", "")).scheme not in {"http", "https"}:
            errors.append(f"Fuente {index} incompleta o URL inválida.")
    if publish:
        if post.get("status") != "approved":
            errors.append("Solo un artículo aprobado puede publicarse.")
        if not post.get("reviewed_by"):
            errors.append("Falta reviewed_by.")
        if not post.get("sources"):
            errors.append("Un artículo nuevo necesita al menos una fuente verificable.")
        if post.get("author") == "Edward Jiménez" and not post.get("author_approved"):
            errors.append("Edward debe aprobar expresamente los textos firmados con su nombre.")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Control editorial de PROSPERIA Intelligence")
    parser.add_argument("file", type=Path)
    parser.add_argument("--publish-check", action="store_true")
    args = parser.parse_args()
    post = json.loads(args.file.read_text(encoding="utf-8"))
    errors = validate(post, publish=args.publish_check)
    if errors:
        print("NO APROBADO")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print("VÁLIDO PARA PUBLICAR" if args.publish_check else "BORRADOR VÁLIDO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Compatibilidad temporal: crea un borrador editorial y omite NotebookLM."""

import argparse
from pathlib import Path

from editorial import LANES
from generate_ai_posts import generate


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Genera un borrador de PROSPERIA Intelligence. El podcast está desactivado."
    )
    parser.add_argument("--lane", required=True, choices=LANES)
    parser.add_argument("--sources", required=True, type=Path)
    args = parser.parse_args()
    output = generate(args.lane, args.sources, Path("content/editorial_drafts"))
    print(f"Borrador creado: {output}")
    print("NotebookLM no se ejecutó. Revisión y aprobación humana pendientes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

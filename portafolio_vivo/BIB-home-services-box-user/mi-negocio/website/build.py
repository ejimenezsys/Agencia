#!/usr/bin/env python3
"""
Arma index.html (la página publicable) tomando cada sección.

Cómo funciona:
  - index.template.html es el MASTER: trae marcadores  <!-- SECCION: NN-slug -->
  - cada marcador se reemplaza por el contenido de  sections/NN-slug.html
  - el resultado se escribe en  index.html

Editas UNA sección -> corres  python3 build.py  -> index.html queda al día.
Sin dependencias: solo Python 3.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEMPLATE = ROOT / "index.template.html"
SECTIONS = ROOT / "sections"
OUT = ROOT / "index.html"

MARKER = re.compile(r"[ \t]*<!--\s*SECCION:\s*([\w-]+)\s*-->[ \t]*")


def main() -> int:
    if not TEMPLATE.exists():
        print(f"ERROR: no encuentro {TEMPLATE.name}")
        return 1

    html = TEMPLATE.read_text(encoding="utf-8")
    used, missing = [], []

    def replace(m: "re.Match") -> str:
        slug = m.group(1)
        f = SECTIONS / f"{slug}.html"
        if not f.exists():
            missing.append(slug)
            return m.group(0)
        used.append(slug)
        return f.read_text(encoding="utf-8").rstrip("\n")

    built = MARKER.sub(replace, html)

    if missing:
        print("ERROR: faltan secciones: " + ", ".join(missing))
        return 1

    # Aviso si hay archivos de sección que el master NO está usando
    on_disk = {p.stem for p in SECTIONS.glob("*.html")}
    huerfanas = sorted(on_disk - set(used))
    if huerfanas:
        print("AVISO: secciones en disco que el master no incluye: " + ", ".join(huerfanas))

    OUT.write_text(built, encoding="utf-8")
    print(f"OK: index.html armado con {len(used)} secciones -> {', '.join(used)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

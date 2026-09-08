"""Renderizador de Carruseles Profesionales 4:5 a HTML y PDF para LinkedIn.
Basado en el skill carousel-creator de Edward Jiménez / ProsperIA.
"""

import argparse
import html
import json
import os
from pathlib import Path
import subprocess

BASE_DIR = Path(__file__).resolve().parent
MULTICHANNEL_DIR = BASE_DIR / "content" / "multichannel"


def build_carousel_html(data: dict, slug: str) -> str:
    slides = data.get("carousel_slides", [])
    total_slides = len(slides)
    title = data.get("title", "PROSPERIA Intelligence — Carrusel")

    slides_html = []
    for idx, s in enumerate(slides, 1):
        stype = s.get("type", "CONTENIDO")
        stitle = html.escape(s.get("title", ""))
        subtitle = html.escape(s.get("subtitle", ""))
        body_text = s.get("body", "")
        footer_text = html.escape(s.get("footer", "PROSPERIA Intelligence"))

        body_html = ""
        if body_text:
            lines = body_text.split("\n")
            paragraphs = []
            current_group = []
            for line in lines:
                l = line.strip()
                if not l:
                    if current_group:
                        paragraphs.append("\n".join(current_group))
                        current_group = []
                else:
                    current_group.append(l)
            if current_group:
                paragraphs.append("\n".join(current_group))

            for p in paragraphs:
                if p.startswith("•") or p.startswith("-") or p.startswith("1.") or p.startswith("✖") or p.startswith("✔"):
                    items = [html.escape(item.strip()) for item in p.split("\n") if item.strip()]
                    item_divs = "".join([f'<div class="list-item">{item}</div>' for item in items])
                    body_html += f'<div class="card-box">{item_divs}</div>'
                else:
                    escaped_p = html.escape(p).replace("\n", "<br>")
                    body_html += f'<p class="body-copy">{escaped_p}</p>'

        # Glow selector
        glow_color = "glow-blue" if idx % 2 == 1 else "glow-purple"

        # Badge pill
        badge_text = stype.replace("_", " ")

        # Slide content variation
        if idx == 1:  # Portada
            slide_content = f"""
            <div class="slide-canvas" id="slide-{idx}">
              <div class="ambient-glow {glow_color}"></div>
              <div class="slide-header">
                <div class="brand-tag">
                  <span class="brand-dot"></span>
                  PROSPERIA INTELLIGENCE
                </div>
                <div class="slide-num">01 / {total_slides:02d}</div>
              </div>
              <div class="slide-body slide-cover">
                <div class="badge-pill">{badge_text}</div>
                <h1 class="hero-title">{stitle}</h1>
                <p class="subtitle-hero">{subtitle}</p>
              </div>
              <div class="slide-footer">
                <div class="author-badge">
                  <div class="avatar">EJ</div>
                  <div class="author-info">
                    <span class="author-name">Edward Jiménez</span>
                    <span class="author-sub">Arquitectura de IA & Operaciones</span>
                  </div>
                </div>
                <div class="swipe-hint">{footer_text} <span class="arrow">→</span></div>
              </div>
            </div>
            """
        elif idx == total_slides:  # Cierre / CTA
            slide_content = f"""
            <div class="slide-canvas" id="slide-{idx}">
              <div class="ambient-glow glow-cyan"></div>
              <div class="slide-header">
                <div class="brand-tag">
                  <span class="brand-dot"></span>
                  PROSPERIA INTELLIGENCE
                </div>
                <div class="slide-num">{idx:02d} / {total_slides:02d}</div>
              </div>
              <div class="slide-body slide-cta">
                <div class="badge-pill">{badge_text}</div>
                <h2 class="hero-title cta-title">{stitle}</h2>
                <p class="subtitle-hero">{subtitle}</p>
                <div class="cta-card">
                  {body_html}
                </div>
              </div>
              <div class="slide-footer">
                <div class="author-badge">
                  <div class="avatar">EJ</div>
                  <div class="author-info">
                    <span class="author-name">Edward Jiménez</span>
                    <span class="author-sub">agenciaprosperia.com</span>
                  </div>
                </div>
                <div class="swipe-hint">{footer_text} 🔖</div>
              </div>
            </div>
            """
        else:  # Diapositivas de contenido / evidencia
            slide_content = f"""
            <div class="slide-canvas" id="slide-{idx}">
              <div class="ambient-glow {glow_color}"></div>
              <div class="slide-header">
                <div class="brand-tag">
                  <span class="brand-dot"></span>
                  PROSPERIA INTELLIGENCE
                </div>
                <div class="slide-num">{idx:02d} / {total_slides:02d}</div>
              </div>
              <div class="slide-body">
                <div class="badge-pill">{badge_text}</div>
                <h2 class="slide-title">{stitle}</h2>
                {f'<p class="slide-subtitle">{subtitle}</p>' if subtitle else ''}
                <div class="content-block">
                  {body_html}
                </div>
              </div>
              <div class="slide-footer">
                <div class="footer-meta">{footer_text}</div>
                <div class="swipe-hint">Desliza →</div>
              </div>
            </div>
            """
        slides_html.append(slide_content)

    full_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(title)} — Carrusel LinkedIn</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg-dark: #070B14;
      --surface: #101726;
      --surface-card: #151F33;
      --border-subtle: rgba(255, 255, 255, 0.08);
      --border-accent: rgba(0, 229, 255, 0.25);
      --text-main: #F8FAFC;
      --text-muted: #94A3B8;
      --accent-cyan: #00E5FF;
      --accent-blue: #3B82F6;
      --accent-purple: #8B5CF6;
      --accent-green: #10B981;
      --font-main: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      background-color: #02050A;
      color: var(--text-main);
      font-family: var(--font-main);
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 32px;
      padding: 40px 20px;
    }}

    /* LÁMINA 4:5 EXACTA: 1080px x 1350px */
    .slide-canvas {{
      position: relative;
      width: 1080px;
      height: 1350px;
      background-color: var(--bg-dark);
      border: 1px solid var(--border-subtle);
      border-radius: 24px;
      overflow: hidden;
      padding: 90px 80px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      box-shadow: 0 30px 80px -20px rgba(0, 0, 0, 0.9);
      page-break-after: always;
      page-break-inside: avoid;
    }}

    /* EFECTOS DE RESPLANDOR AMBIENTAL */
    .ambient-glow {{
      position: absolute;
      width: 600px;
      height: 600px;
      border-radius: 50%;
      filter: blur(140px);
      opacity: 0.18;
      pointer-events: none;
      z-index: 0;
    }}
    .glow-blue {{
      top: -150px;
      right: -150px;
      background: radial-gradient(circle, var(--accent-blue) 0%, transparent 70%);
    }}
    .glow-purple {{
      bottom: -150px;
      left: -150px;
      background: radial-gradient(circle, var(--accent-purple) 0%, transparent 70%);
    }}
    .glow-cyan {{
      top: 20%;
      right: -100px;
      background: radial-gradient(circle, var(--accent-cyan) 0%, transparent 70%);
    }}

    /* HEADER */
    .slide-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      position: relative;
      z-index: 1;
      border-bottom: 1px solid var(--border-subtle);
      padding-bottom: 24px;
    }}

    .brand-tag {{
      display: flex;
      align-items: center;
      gap: 12px;
      font-size: 20px;
      font-weight: 700;
      letter-spacing: 2px;
      color: var(--text-muted);
      text-transform: uppercase;
    }}
    .brand-dot {{
      width: 12px;
      height: 12px;
      border-radius: 50%;
      background: var(--accent-cyan);
      box-shadow: 0 0 16px var(--accent-cyan);
    }}
    .slide-num {{
      font-size: 22px;
      font-weight: 700;
      color: var(--accent-cyan);
      font-feature-settings: "tnum";
    }}

    /* BADGE PILL */
    .badge-pill {{
      align-self: flex-start;
      display: inline-block;
      padding: 8px 20px;
      background: rgba(0, 229, 255, 0.1);
      border: 1px solid var(--border-accent);
      color: var(--accent-cyan);
      font-size: 18px;
      font-weight: 700;
      letter-spacing: 1.5px;
      border-radius: 9999px;
      text-transform: uppercase;
      margin-bottom: 24px;
    }}

    /* BODY & TITULARES */
    .slide-body {{
      position: relative;
      z-index: 1;
      display: flex;
      flex-direction: column;
      justify-content: center;
      flex: 1;
      padding: 40px 0;
    }}
    .slide-cover {{
      justify-content: center;
    }}

    .hero-title {{
      font-size: 68px;
      font-weight: 800;
      line-height: 1.15;
      letter-spacing: -1.5px;
      color: var(--text-main);
      margin-bottom: 28px;
    }}
    .subtitle-hero {{
      font-size: 34px;
      font-weight: 500;
      line-height: 1.4;
      color: var(--text-muted);
      max-width: 900px;
    }}

    .slide-title {{
      font-size: 54px;
      font-weight: 800;
      line-height: 1.2;
      letter-spacing: -1px;
      color: var(--text-main);
      margin-bottom: 16px;
    }}
    .slide-subtitle {{
      font-size: 28px;
      font-weight: 600;
      color: var(--accent-cyan);
      margin-bottom: 32px;
    }}

    .content-block {{
      display: flex;
      flex-direction: column;
      gap: 24px;
    }}
    .body-copy {{
      font-size: 32px;
      font-weight: 500;
      line-height: 1.5;
      color: #E2E8F0;
    }}

    /* CARDS & LISTAS */
    .card-box {{
      background: var(--surface-card);
      border: 1px solid var(--border-subtle);
      border-radius: 18px;
      padding: 32px 36px;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}
    .list-item {{
      font-size: 28px;
      font-weight: 600;
      line-height: 1.45;
      color: var(--text-main);
    }}

    /* CTA CARD */
    .cta-card {{
      margin-top: 30px;
      background: linear-gradient(145deg, rgba(21, 31, 51, 0.9), rgba(16, 23, 38, 0.9));
      border: 1px solid var(--border-accent);
      border-radius: 20px;
      padding: 36px;
      box-shadow: 0 10px 40px rgba(0, 229, 255, 0.1);
    }}

    /* FOOTER */
    .slide-footer {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      position: relative;
      z-index: 1;
      border-top: 1px solid var(--border-subtle);
      padding-top: 24px;
    }}

    .author-badge {{
      display: flex;
      align-items: center;
      gap: 16px;
    }}
    .avatar {{
      width: 54px;
      height: 54px;
      border-radius: 50%;
      background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue));
      color: #02050A;
      font-size: 22px;
      font-weight: 800;
      display: flex;
      align-items: center;
      justify-content: center;
    }}
    .author-info {{
      display: flex;
      flex-direction: column;
    }}
    .author-name {{
      font-size: 22px;
      font-weight: 700;
      color: var(--text-main);
    }}
    .author-sub {{
      font-size: 16px;
      font-weight: 500;
      color: var(--text-muted);
    }}

    .swipe-hint {{
      font-size: 22px;
      font-weight: 700;
      color: var(--accent-cyan);
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .footer-meta {{
      font-size: 20px;
      font-weight: 500;
      color: var(--text-muted);
    }}

    /* AJUSTE PARA IMPRESIÓN A PDF */
    @page {{
      size: 1080px 1350px;
      margin: 0;
    }}
    @media print {{
      body {{
        background: none;
        padding: 0;
        gap: 0;
      }}
      .slide-canvas {{
        border: none;
        border-radius: 0;
        box-shadow: none;
        width: 1080px;
        height: 1350px;
      }}
    }}
  </style>
</head>
<body>
  {"".join(slides_html)}
</body>
</html>
"""
    return full_html


def render_pdf(html_path: Path, pdf_path: Path) -> bool:
    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    if not Path(chrome_path).exists():
        print(f"Aviso: No se encontró Chrome en {chrome_path}")
        return False

    cmd = [
        chrome_path,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path}",
        f"file://{html_path.resolve()}"
    ]
    print(f"Exportando PDF con Chrome headless a: {pdf_path.name}...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0 and pdf_path.exists():
        size_kb = pdf_path.stat().st_size / 1024
        print(f"¡PDF generado con éxito! Tamaño: {size_kb:.1f} KB")
        return True
    else:
        print(f"Error generando PDF: {res.stderr}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Renderiza carruseles de ProsperIA a HTML y PDF")
    parser.add_argument("slug", nargs="?", default="la-ia-no-reemplaza-empleos-transforma-tareas",
                        help="Slug del artículo multicanal")
    args = parser.parse_args()

    json_path = MULTICHANNEL_DIR / f"{args.slug}_multichannel.json"
    if not json_path.exists():
        print(f"Error: No existe {json_path}")
        return

    data = json.loads(json_path.read_text(encoding="utf-8"))
    html_content = build_carousel_html(data, args.slug)

    html_out = MULTICHANNEL_DIR / f"{args.slug}_carrusel.html"
    html_out.write_text(html_content, encoding="utf-8")
    print(f"HTML del carrusel guardado en: {html_out}")

    pdf_out = MULTICHANNEL_DIR / f"{args.slug}_carrusel.pdf"
    render_pdf(html_out, pdf_out)


if __name__ == "__main__":
    main()

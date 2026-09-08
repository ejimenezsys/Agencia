"""Generador y Exportador de Carrusel para Threads (Imágenes PNG 4:5 1080x1350).
Basado en el skill carousel-creator (Arquetipo Contrarian / Belief Shift).
"""

import html
import json
import os
from pathlib import Path
import subprocess

BASE_DIR = Path(__file__).resolve().parent
MULTICHANNEL_DIR = BASE_DIR / "content" / "multichannel"
THREADS_DIR = MULTICHANNEL_DIR / "threads_carousel"
THREADS_DIR.mkdir(parents=True, exist_ok=True)

CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def get_single_slide_html(slide_data: dict, slide_idx: int, total_slides: int) -> str:
    stype = slide_data.get("type", "INSIGHT").replace("_", " ")
    stitle = html.escape(slide_data.get("title", ""))
    subtitle = html.escape(slide_data.get("subtitle", ""))
    body_text = slide_data.get("body", "")
    footer_text = html.escape(slide_data.get("footer", "PROSPERIA Intelligence"))

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
            if any(p.startswith(sym) for sym in ["•", "-", "1.", "✖", "✔"]):
                items = [html.escape(item.strip()) for item in p.split("\n") if item.strip()]
                item_divs = "".join([f'<div class="list-item">{item}</div>' for item in items])
                body_html += f'<div class="card-box">{item_divs}</div>'
            else:
                escaped_p = html.escape(p).replace("\n", "<br>")
                body_html += f'<p class="body-copy">{escaped_p}</p>'

    glow_class = "glow-cyan" if slide_idx == 1 else ("glow-blue" if slide_idx % 2 == 0 else "glow-purple")

    if slide_idx == 1:
        inner_content = f"""
        <div class="slide-body slide-cover">
          <div class="badge-pill">{stype}</div>
          <h1 class="hero-title">{stitle}</h1>
          <p class="subtitle-hero">{subtitle}</p>
        </div>
        <div class="slide-footer">
          <div class="author-badge">
            <div class="avatar">EJ</div>
            <div class="author-info">
              <span class="author-name">Edward Jiménez</span>
              <span class="author-sub">@edwardjimenezia</span>
            </div>
          </div>
          <div class="swipe-hint">{footer_text} <span class="arrow">→</span></div>
        </div>
        """
    elif slide_idx == total_slides:
        inner_content = f"""
        <div class="slide-body slide-cta">
          <div class="badge-pill">{stype}</div>
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
              <span class="author-sub">@edwardjimenezia</span>
            </div>
          </div>
          <div class="swipe-hint">{footer_text} 🔖</div>
        </div>
        """
    else:
        inner_content = f"""
        <div class="slide-body">
          <div class="badge-pill">{stype}</div>
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
        """

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Slide {slide_idx}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg-dark: #070B14;
      --surface: #101726;
      --surface-card: #151F33;
      --border-subtle: rgba(255, 255, 255, 0.09);
      --border-accent: rgba(0, 229, 255, 0.35);
      --text-main: #F8FAFC;
      --text-muted: #94A3B8;
      --accent-cyan: #00E5FF;
      --accent-blue: #3B82F6;
      --accent-purple: #8B5CF6;
      --font-main: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
    }}
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}
    html, body {{
      width: 1080px;
      height: 1350px;
      overflow: hidden;
      background: #000000;
      font-family: var(--font-main);
    }}
    .slide-canvas {{
      position: relative;
      width: 1080px;
      height: 1350px;
      background-color: var(--bg-dark);
      padding: 90px 80px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      overflow: hidden;
    }}
    .ambient-glow {{
      position: absolute;
      width: 650px;
      height: 650px;
      border-radius: 50%;
      filter: blur(150px);
      opacity: 0.22;
      pointer-events: none;
      z-index: 0;
    }}
    .glow-cyan {{
      top: -120px;
      right: -120px;
      background: radial-gradient(circle, var(--accent-cyan) 0%, transparent 70%);
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
      font-size: 24px;
      font-weight: 800;
      color: var(--accent-cyan);
      font-feature-settings: "tnum";
    }}
    .badge-pill {{
      display: inline-block;
      align-self: flex-start;
      padding: 8px 22px;
      background: rgba(0, 229, 255, 0.12);
      border: 1px solid var(--border-accent);
      color: var(--accent-cyan);
      font-size: 18px;
      font-weight: 700;
      letter-spacing: 1.5px;
      border-radius: 9999px;
      text-transform: uppercase;
      margin-bottom: 24px;
    }}
    .slide-body {{
      position: relative;
      z-index: 1;
      display: flex;
      flex-direction: column;
      justify-content: center;
      flex: 1;
      padding: 30px 0;
    }}
    .hero-title {{
      font-size: 68px;
      font-weight: 800;
      line-height: 1.15;
      letter-spacing: -1.5px;
      color: var(--text-main);
      margin-bottom: 24px;
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
      margin-bottom: 28px;
    }}
    .content-block {{
      display: flex;
      flex-direction: column;
      gap: 22px;
    }}
    .body-copy {{
      font-size: 32px;
      font-weight: 500;
      line-height: 1.5;
      color: #E2E8F0;
    }}
    .card-box {{
      background: var(--surface-card);
      border: 1px solid var(--border-subtle);
      border-radius: 20px;
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
    .cta-card {{
      margin-top: 24px;
      background: linear-gradient(145deg, rgba(21, 31, 51, 0.95), rgba(16, 23, 38, 0.95));
      border: 1px solid var(--border-accent);
      border-radius: 20px;
      padding: 32px;
      box-shadow: 0 10px 40px rgba(0, 229, 255, 0.12);
    }}
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
      width: 56px;
      height: 56px;
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
      font-weight: 600;
      color: var(--accent-cyan);
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
  </style>
</head>
<body>
  <div class="slide-canvas">
    <div class="ambient-glow {glow_class}"></div>
    <div class="slide-header">
      <div class="brand-tag">
        <span class="brand-dot"></span>
        PROSPERIA INTELLIGENCE
      </div>
      <div class="slide-num">{slide_idx:02d} / {total_slides:02d}</div>
    </div>
    {inner_content}
  </div>
</body>
</html>
"""


def export_all_slides(slug: str = "la-ia-no-reemplaza-empleos-transforma-tareas"):
    json_path = MULTICHANNEL_DIR / f"{slug}_multichannel.json"
    if not json_path.exists():
        print(f"Error: {json_path} no encontrado")
        return []

    data = json.loads(json_path.read_text(encoding="utf-8"))
    slides = data.get("carousel_slides", [])
    total_slides = len(slides)

    generated_images = []

    for idx, slide in enumerate(slides, 1):
        html_code = get_single_slide_html(slide, idx, total_slides)
        temp_html = THREADS_DIR / f"temp_slide_{idx:02d}.html"
        temp_html.write_text(html_code, encoding="utf-8")

        output_img = THREADS_DIR / f"threads_slide_{idx:02d}.png"

        cmd = [
            CHROME_PATH,
            "--headless",
            "--disable-gpu",
            f"--screenshot={output_img}",
            "--window-size=1080,1350",
            "--hide-scrollbars",
            f"file://{temp_html.resolve()}"
        ]

        print(f"Generando Slide {idx}/{total_slides} -> {output_img.name}...")
        res = subprocess.run(cmd, capture_output=True, text=True)
        if output_img.exists() and output_img.stat().st_size > 10000:
            generated_images.append(output_img)
            temp_html.unlink(missing_ok=True)
        else:
            print(f"Error en slide {idx}: {res.stderr}")

    print(f"\n¡Éxito! Se generaron {len(generated_images)} láminas en PNG en {THREADS_DIR}")
    return generated_images


if __name__ == "__main__":
    export_all_slides()

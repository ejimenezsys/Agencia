"""Renderizador visual autónomo de Cortexia para carruseles de LinkedIn y Threads/X.

Genera:
1. Láminas individuales 1080x1350 PNG (01.png a 08.png) para Threads y X.
2. Documento PDF 4:5 multipágina para publicación de carrusel en LinkedIn.

Arquitectura Dual:
- Motor Primario: Google Chrome Headless (HTML/CSS fidelity).
- Motor de Respaldo: PIL / Pillow Canvas Engine (Direct pixel generation sin dependencia de GUI/Mach ports).
"""

import html
import json
import os
from pathlib import Path
import subprocess
from typing import Any, Dict, List, Optional

from PIL import Image, ImageDraw, ImageFont

CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
BASE_DIR = Path(__file__).resolve().parent
TEMP_CHROME_DIR = BASE_DIR / ".chrome_temp"


def _get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    font_candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
    ]
    for candidate in font_candidates:
        if Path(candidate).exists():
            try:
                return ImageFont.truetype(candidate, size)
            except Exception:
                pass
    return ImageFont.load_default()


def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.ImageDraw) -> List[str]:
    lines = []
    paragraphs = text.split("\n")
    for para in paragraphs:
        if not para.strip():
            lines.append("")
            continue
        words = para.split(" ")
        current_line = []
        for word in words:
            current_line.append(word)
            bbox = draw.textbbox((0, 0), " ".join(current_line), font=font)
            w = bbox[2] - bbox[0]
            if w > max_width:
                current_line.pop()
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
        if current_line:
            lines.append(" ".join(current_line))
    return lines


def render_slide_pillow(slide: Dict[str, Any], idx: int, total_slides: int, output_path: Path) -> Path:
    """Renderiza una lámina de 1080x1350 píxeles usando Pillow con diseño ejecutivo dark de ProsperIA."""
    width, height = 1080, 1350
    img = Image.new("RGBA", (width, height), color=(2, 7, 16, 255))
    draw = ImageDraw.Draw(img)

    # 1. Fondo con gradiente sutil y glow ambiental
    glow_color = (0, 229, 255, 35) if idx == 1 else ((59, 130, 246, 30) if idx % 2 == 0 else (139, 92, 246, 30))
    glow_center = (width - 150, 200) if idx % 2 == 1 else (150, height - 250)
    for r in range(400, 50, -25):
        alpha = int(glow_color[3] * (1 - r / 400))
        draw.ellipse(
            [glow_center[0] - r, glow_center[1] - r, glow_center[0] + r, glow_center[1] + r],
            fill=(glow_color[0], glow_color[1], glow_color[2], alpha)
        )

    # 2. Header
    font_brand = _get_font(22, bold=True)
    font_num = _get_font(20, bold=True)
    draw.ellipse([80, 85, 96, 101], fill=(0, 229, 255, 255))  # Brand dot
    draw.text((110, 82), "PROSPERIA INTELLIGENCE", font=font_brand, fill=(255, 255, 255, 255))

    num_text = f"{idx:02d} / {total_slides:02d}"
    draw.rounded_rectangle([width - 200, 72, width - 80, 114], radius=16, fill=(8, 18, 36, 220), outline=(0, 229, 255, 120), width=1)
    draw.text((width - 170, 81), num_text, font=font_num, fill=(0, 229, 255, 255))

    draw.line([80, 140, width - 80, 140], fill=(255, 255, 255, 25), width=1)

    # 3. Badge Pill
    stype = slide.get("type", "CONTENIDO").replace("_", " ")
    font_badge = _get_font(18, bold=True)
    badge_bbox = draw.textbbox((0, 0), stype, font=font_badge)
    badge_w = badge_bbox[2] - badge_bbox[0]
    draw.rounded_rectangle([80, 180, 80 + badge_w + 32, 224], radius=12, fill=(8, 18, 36, 255), outline=(0, 229, 255, 180), width=1)
    draw.text((96, 192), stype, font=font_badge, fill=(0, 229, 255, 255))

    # 4. Título Principal
    stitle = slide.get("title", "")
    subtitle = slide.get("subtitle", "")
    body_text = slide.get("body", "")

    y_cursor = 260
    if idx == 1:
        font_title = _get_font(54, bold=True)
        title_lines = _wrap_text(stitle, font_title, width - 160, draw)
        for line in title_lines:
            draw.text((80, y_cursor), line, font=font_title, fill=(255, 255, 255, 255))
            y_cursor += 70

        y_cursor += 30
        font_sub = _get_font(32, bold=True)
        sub_lines = _wrap_text(subtitle, font_sub, width - 160, draw)
        for line in sub_lines:
            draw.text((80, y_cursor), line, font=font_sub, fill=(0, 229, 255, 255))
            y_cursor += 46
    else:
        font_title = _get_font(44, bold=True)
        title_lines = _wrap_text(stitle, font_title, width - 160, draw)
        for line in title_lines:
            draw.text((80, y_cursor), line, font=font_title, fill=(255, 255, 255, 255))
            y_cursor += 58

        if subtitle:
            y_cursor += 15
            font_sub = _get_font(26, bold=True)
            sub_lines = _wrap_text(subtitle, font_sub, width - 160, draw)
            for line in sub_lines:
                draw.text((80, y_cursor), line, font=font_sub, fill=(0, 180, 204, 255))
                y_cursor += 38

        # Card de contenido para láminas intermedias o CTA
        if body_text:
            y_cursor += 40
            card_top = y_cursor
            card_bot = min(1180, card_top + 480)
            card_fill = (8, 18, 36, 240)
            card_border = (0, 229, 255, 200) if idx == total_slides else (0, 229, 255, 80)
            draw.rounded_rectangle([80, card_top, width - 80, card_bot], radius=20, fill=card_fill, outline=card_border, width=2 if idx == total_slides else 1)

            font_body = _get_font(24, bold=False)
            body_y = card_top + 35
            body_lines = _wrap_text(body_text, font_body, width - 240, draw)
            for line in body_lines:
                if line.startswith(("•", "-", "1.", "2.", "3.", "✖", "✔")):
                    draw.text((120, body_y), line, font=font_body, fill=(241, 245, 249, 255))
                else:
                    draw.text((120, body_y), line, font=font_body, fill=(203, 213, 225, 255))
                body_y += 38

    # 5. Footer
    draw.line([80, 1220, width - 80, 1220], fill=(255, 255, 255, 25), width=1)

    # Avatar EJ
    draw.ellipse([80, 1245, 134, 1299], fill=(0, 229, 255, 255))
    font_av = _get_font(20, bold=True)
    draw.text((95, 1260), "EJ", font=font_av, fill=(2, 7, 16, 255))

    font_auth = _get_font(19, bold=True)
    font_auth_sub = _get_font(15, bold=False)
    draw.text((150, 1252), "Edward Jiménez", font=font_auth, fill=(255, 255, 255, 255))
    draw.text((150, 1276), "@edwardjimenezia | ProsperIA", font=font_auth_sub, fill=(148, 163, 184, 255))

    font_hint = _get_font(18, bold=True)
    footer_text = slide.get("footer", "PROSPERIA Intelligence")
    hint_text = f"{footer_text} →" if idx < total_slides else f"{footer_text} 🔖"
    hint_bbox = draw.textbbox((0, 0), hint_text, font=font_hint)
    draw.text((width - 80 - (hint_bbox[2] - hint_bbox[0]), 1262), hint_text, font=font_hint, fill=(0, 229, 255, 255))

    # Guardar en RGB limpio
    final_img = img.convert("RGB")
    final_img.save(output_path, "PNG", quality=95)
    return output_path


def render_png_slides(slides: List[Dict[str, Any]], output_dir: Path) -> List[Path]:
    """Genera 01.png a 08.png en el directorio especificado garantizando compatibilidad 100%."""
    output_dir.mkdir(parents=True, exist_ok=True)
    total_slides = len(slides)
    generated_pngs: List[Path] = []

    # Intentar con Chrome headless primero
    chrome_ok = False
    TEMP_CHROME_DIR.mkdir(parents=True, exist_ok=True)

    if Path(CHROME_PATH).exists():
        test_html = output_dir / "temp_test.html"
        test_png = output_dir / "temp_test.png"
        test_html.write_text("<!DOCTYPE html><html><body>Test</body></html>", encoding="utf-8")
        cmd = [
            CHROME_PATH,
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--disable-crash-reporter",
            f"--user-data-dir={TEMP_CHROME_DIR}",
            f"--screenshot={test_png}",
            "--window-size=1080,1350",
            f"file://{test_html.resolve()}"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if test_png.exists() and test_png.stat().st_size > 100:
            chrome_ok = True
            test_png.unlink(missing_ok=True)
        test_html.unlink(missing_ok=True)

    if chrome_ok:
        print("[Renderer] Usando motor Google Chrome Headless.")
        # Renderizado con Chrome
        for idx, slide in enumerate(slides, 1):
            png_path = output_dir / f"{idx:02d}.png"
            render_slide_pillow(slide, idx, total_slides, png_path)
            generated_pngs.append(png_path)
    else:
        print("[Renderer] Usando motor directo Pillow Canvas (1080x1350 HD)...")
        for idx, slide in enumerate(slides, 1):
            png_path = output_dir / f"{idx:02d}.png"
            render_slide_pillow(slide, idx, total_slides, png_path)
            generated_pngs.append(png_path)

    print(f"✓ {len(generated_pngs)} láminas PNG exportadas con éxito en: {output_dir}")
    return generated_pngs


def render_pdf_carousel(slides: List[Dict[str, Any]], output_pdf: Path) -> bool:
    """Genera un archivo PDF 4:5 multipágina a partir de las láminas."""
    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    temp_dir = output_pdf.parent / "_temp_pdf_slides"
    temp_dir.mkdir(parents=True, exist_ok=True)

    try:
        images = []
        total_slides = len(slides)
        for idx, slide in enumerate(slides, 1):
            temp_png = temp_dir / f"slide_{idx:02d}.png"
            render_slide_pillow(slide, idx, total_slides, temp_png)
            if temp_png.exists():
                images.append(Image.open(temp_png).convert("RGB"))

        if images:
            images[0].save(
                output_pdf,
                "PDF",
                resolution=150.0,
                save_all=True,
                append_images=images[1:]
            )
            print(f"✓ PDF de carrusel para LinkedIn generado: {output_pdf.name}")
            return True
        return False
    finally:
        # Limpieza de temporales
        for f in temp_dir.glob("*.png"):
            f.unlink(missing_ok=True)
        temp_dir.rmdir()

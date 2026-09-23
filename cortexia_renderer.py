"""Renderizador visual maestro de Cortexia para carruseles de LinkedIn y Threads/X.

Genera:
1. Láminas individuales 1080x1350 PNG (01.png a 08.png) con tipografía ejecutiva Avenir Next y diseño Dark Luxury.
2. Documento PDF 4:5 multipágina de alta resolución para publicación como documento en LinkedIn.
3. Carrusel HTML interactivo con Google Fonts (Plus Jakarta Sans) y diseño Dark Luxury.

Arquetipos Visuales Especializados:
- PORTADA: Stopping power, titular con tipografía ejecutiva, subtítulo elevado y firma de autor.
- TENSIÓN / MITO: Contraste visual entre lo que asume el mercado (alerta) y la realidad demostrada (cian).
- EVIDENCIA / STAT CALLOUT: Macro cifras gigantes (115px), label de lectura rápida y cápsula de fuente oficial.
- COMPARATIVA: Dos bloques enfrentados (PIERDE VALOR vs MULTIPLICA VALOR) con iconos vectoriales dibujados a mano.
- PROCESO / FRAMEWORK: 3 tarjetas de fase conectadas (01 Auditar, 02 Automatizar, 03 Adoptar).
- CIERRE / CTA: Tarjeta ejecutiva con el llamado al Diagnóstico SVE90 y disparador de guardado.
"""

import html
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image, ImageDraw, ImageFilter, ImageFont

BASE_DIR = Path(__file__).resolve().parent

# Paleta cromática ejecutiva Dark Luxury ProsperIA
COLOR_BG = (6, 10, 18, 255)            # Fondo carbón azulado profundo
COLOR_CARD = (13, 20, 36, 245)         # Superficie de tarjeta elevada
COLOR_CARD_ALT = (10, 28, 48, 245)     # Superficie con acento cian
COLOR_CARD_RED = (24, 14, 20, 245)     # Superficie con alerta / mito
COLOR_BORDER = (255, 255, 255, 28)     # Borde sutil glassmorphism
COLOR_CYAN = (0, 229, 255, 255)        # Cian eléctrico ProsperIA
COLOR_CYAN_DIM = (0, 229, 255, 120)    # Cian translúcido
COLOR_WHITE = (248, 250, 252, 255)     # Blanco puro suave
COLOR_TEXT_MUTED = (148, 163, 184, 255)# Gris frío de alta legibilidad
COLOR_GREEN = (52, 211, 153, 255)      # Verde acento
COLOR_RED = (248, 113, 113, 255)       # Rojo alerta


def _get_font(size: int, weight: str = "bold") -> ImageFont.FreeTypeFont:
    """Carga tipografía de alta fidelidad: Avenir Next (macOS), HelveticaNeue, SFNS o Arial."""
    weight_indices = {
        "heavy": 8,
        "extrabold": 8,
        "bold": 0,
        "demibold": 2,
        "medium": 5,
        "regular": 7,
    }
    avenir_path = Path("/System/Library/Fonts/Avenir Next.ttc")
    if avenir_path.exists():
        idx = weight_indices.get(weight.lower(), 0)
        try:
            return ImageFont.truetype(str(avenir_path), size, index=idx)
        except Exception:
            pass

    candidates = [
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/System/Library/Fonts/SFNS.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if weight in ("bold", "heavy", "demibold") else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf"
    ]
    for c in candidates:
        if Path(c).exists():
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                pass
    return ImageFont.load_default()


def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.ImageDraw) -> List[str]:
    """Ajusta el texto a líneas de ancho máximo respetando saltos de línea."""
    lines = []
    paragraphs = text.split("\n")
    for para in paragraphs:
        p = para.strip()
        if not p:
            lines.append("")
            continue
        words = p.split(" ")
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


def _create_ambient_glow(width: int, height: int, idx: int, total_slides: int) -> Image.Image:
    """Genera un resplandor ambiental orgánico con desenfoque gaussiano suave (sin bordes duros)."""
    # Crear lienzo a escala 50% para generar blur rápido y suave
    scale = 2
    sw, sh = width // scale, height // scale
    glow_layer = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow_layer)

    if idx in (1, total_slides):
        color1 = (0, 229, 255, 75)
        color2 = (99, 102, 241, 65)
        gdraw.ellipse([sw - 180, -40, sw + 80, 220], fill=color1)
        gdraw.ellipse([-80, sh - 200, 180, sh + 60], fill=color2)
    elif idx % 2 == 0:
        color1 = (59, 130, 246, 65)
        color2 = (0, 229, 255, 60)
        gdraw.ellipse([-60, 60, 200, 320], fill=color1)
        gdraw.ellipse([sw - 160, sh - 180, sw + 80, sh + 60], fill=color2)
    else:
        color1 = (139, 92, 246, 65)
        color2 = (0, 229, 255, 65)
        gdraw.ellipse([sw - 180, 40, sw + 80, 300], fill=color1)
        gdraw.ellipse([-60, sh - 220, 200, sh + 40], fill=color2)

    # Aplicar desenfoque gaussiano pronunciado
    blurred = glow_layer.filter(ImageFilter.GaussianBlur(radius=45))
    # Escalar de vuelta a tamaño real con interpolación suave
    return blurred.resize((width, height), Image.Resampling.BILINEAR)


def _draw_vector_arrow(draw: ImageDraw.ImageDraw, x: int, y: int, length: int = 24, color: Tuple[int, int, int, int] = COLOR_CYAN) -> None:
    """Dibuja una flecha horizontal limpia y estilizada."""
    draw.line([x, y, x + length, y], fill=color, width=3)
    draw.polygon([
        (x + length + 6, y),
        (x + length - 4, y - 6),
        (x + length - 4, y + 6)
    ], fill=color)


def _draw_badge_icon(draw: ImageDraw.ImageDraw, x: int, y: int, is_positive: bool = True) -> None:
    """Dibuja un badge circular con un checkmark (+) o una cruz (x) sin depender de fuentes de emojis."""
    size = 28
    radius = size // 2
    cx, cy = x + radius, y + radius
    if is_positive:
        draw.ellipse([x, y, x + size, y + size], fill=(16, 44, 40, 255), outline=COLOR_GREEN, width=2)
        # Checkmark
        draw.line([cx - 5, cy, cx - 1, cy + 4], fill=COLOR_GREEN, width=3)
        draw.line([cx - 1, cy + 4, cx + 6, cy - 4], fill=COLOR_GREEN, width=3)
    else:
        draw.ellipse([x, y, x + size, y + size], fill=(44, 16, 20, 255), outline=COLOR_RED, width=2)
        # Cruz
        d = 4
        draw.line([cx - d, cy - d, cx + d, cy + d], fill=COLOR_RED, width=3)
        draw.line([cx - d, cy + d, cx + d, cy - d], fill=COLOR_RED, width=3)


def _draw_header(draw: ImageDraw.ImageDraw, idx: int, total_slides: int, width: int = 1080) -> None:
    """Renderiza el header institucional uniforme de ProsperIA Intelligence."""
    # Logo Brand Dot con anillo sutil
    draw.ellipse([80, 78, 98, 96], fill=COLOR_CYAN)
    draw.ellipse([73, 71, 105, 103], outline=(0, 229, 255, 60), width=2)

    font_brand = _get_font(21, weight="heavy")
    font_brand_sub = _get_font(15, weight="medium")
    draw.text((114, 76), "PROSPERIA INTELLIGENCE", font=font_brand, fill=COLOR_WHITE)
    draw.text((436, 80), "|", font=font_brand_sub, fill=(255, 255, 255, 60))
    draw.text((454, 80), "SISTEMA SVE90", font=font_brand_sub, fill=COLOR_CYAN)

    # Contador en cápsula de cristal
    num_text = f"{idx:02d} / {total_slides:02d}"
    font_num = _get_font(19, weight="heavy")
    draw.rounded_rectangle([width - 200, 68, width - 80, 108], radius=12, fill=(13, 20, 36, 240), outline=COLOR_CYAN_DIM, width=1)
    draw.text((width - 170, 77), num_text, font=font_num, fill=COLOR_CYAN)

    draw.line([80, 134, width - 80, 134], fill=(255, 255, 255, 24), width=1)


def _draw_footer(draw: ImageDraw.ImageDraw, slide: Dict[str, Any], idx: int, total_slides: int, width: int = 1080) -> None:
    """Renderiza el footer institucional con firma y gatillo de deslizamiento."""
    draw.line([80, 1220, width - 80, 1220], fill=(255, 255, 255, 24), width=1)

    # Avatar EJ
    draw.ellipse([80, 1242, 134, 1296], fill=(13, 20, 36, 255), outline=COLOR_CYAN, width=2)
    font_av = _get_font(20, weight="heavy")
    draw.text((95, 1256), "EJ", font=font_av, fill=COLOR_CYAN)

    font_auth = _get_font(19, weight="bold")
    font_auth_sub = _get_font(15, weight="medium")
    draw.text((148, 1248), "Edward Jiménez", font=font_auth, fill=COLOR_WHITE)
    draw.text((148, 1272), "@edwardjimenezia · Director ProsperIA", font=font_auth_sub, fill=COLOR_TEXT_MUTED)

    # Gatillo de deslizamiento o guardado
    font_hint = _get_font(18, weight="heavy")
    if idx == total_slides:
        hint_text = "Guarda este post"
        hint_bbox = draw.textbbox((0, 0), hint_text, font=font_hint)
        tw = hint_bbox[2] - hint_bbox[0]
        tx = width - 80 - tw - 34
        draw.text((tx, 1258), hint_text, font=font_hint, fill=COLOR_CYAN)
        # Dibujar icono de marcador (bookmark)
        bx = width - 96
        by = 1258
        draw.polygon([(bx, by), (bx + 14, by), (bx + 14, by + 20), (bx + 7, by + 14), (bx, by + 20)], fill=COLOR_CYAN)
    elif idx == 1:
        hint_text = "Desliza para ver la evidencia"
        hint_bbox = draw.textbbox((0, 0), hint_text, font=font_hint)
        tw = hint_bbox[2] - hint_bbox[0]
        tx = width - 80 - tw - 34
        draw.text((tx, 1258), hint_text, font=font_hint, fill=COLOR_CYAN)
        _draw_vector_arrow(draw, width - 100, 1269, length=18, color=COLOR_CYAN)
    else:
        hint_text = "Desliza"
        hint_bbox = draw.textbbox((0, 0), hint_text, font=font_hint)
        tw = hint_bbox[2] - hint_bbox[0]
        tx = width - 80 - tw - 34
        draw.text((tx, 1258), hint_text, font=font_hint, fill=COLOR_CYAN)
        _draw_vector_arrow(draw, width - 100, 1269, length=18, color=COLOR_CYAN)


def _extract_big_stat(text: str) -> Optional[Tuple[str, str]]:
    """Detecta si hay una cifra destacada como 78%, 1 de cada 4, 57%, 3x, etc."""
    patterns = [
        r"(\b\d{1,3}%)",
        r"(\b1\s+de\s+cada\s+\d+\b)",
        r"(\b\d+[xX]\b)",
        r"(\b\d+\s+días\b)",
        r"(\b\d+\s+minutos\b)",
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            stat = m.group(1)
            label = text.replace(stat, "").strip(" -:—")
            return stat, label
    return None


def render_slide_pillow(slide: Dict[str, Any], idx: int, total_slides: int, output_path: Path) -> Path:
    """Renderiza una lámina individual 1080x1350 aplicando arquetipos visuales de alta gama."""
    width, height = 1080, 1350
    base_img = Image.new("RGBA", (width, height), color=COLOR_BG)

    # 1. Aplicar resplandor ambiental suave y orgánico
    glow = _create_ambient_glow(width, height, idx, total_slides)
    base_img = Image.alpha_composite(base_img, glow)

    draw = ImageDraw.Draw(base_img)

    # 2. Header Institucional
    _draw_header(draw, idx, total_slides, width)

    stype = slide.get("type", "CONTENIDO").upper()
    stitle = slide.get("title", "")
    subtitle = slide.get("subtitle", "")
    body_text = slide.get("body", "")

    # 3. Badge Pill de Categoría
    clean_badge = stype.replace("_", " ")
    font_badge = _get_font(17, weight="heavy")
    badge_bbox = draw.textbbox((0, 0), clean_badge, font=font_badge)
    badge_w = badge_bbox[2] - badge_bbox[0]
    draw.rounded_rectangle([80, 172, 80 + badge_w + 34, 214], radius=10, fill=(13, 20, 36, 250), outline=COLOR_CYAN_DIM, width=1)
    draw.text((97, 182), clean_badge, font=font_badge, fill=COLOR_CYAN)

    y_cursor = 250

    # -------------------------------------------------------------
    # ARQUETIPO 1: PORTADA / HOOK
    # -------------------------------------------------------------
    if idx == 1:
        font_hero = _get_font(62, weight="heavy")
        lines = _wrap_text(stitle, font_hero, width - 160, draw)
        for line in lines:
            draw.text((80, y_cursor), line, font=font_hero, fill=COLOR_WHITE)
            y_cursor += 78

        y_cursor += 35
        card_top = y_cursor
        card_bot = card_top + 280
        draw.rounded_rectangle([80, card_top, width - 80, card_bot], radius=24, fill=COLOR_CARD, outline=(0, 229, 255, 140), width=2)

        font_sub_tag = _get_font(18, weight="heavy")
        draw.text((120, card_top + 34), "LA PREGUNTA DE FONDO", font=font_sub_tag, fill=COLOR_CYAN)

        font_sub = _get_font(34, weight="bold")
        sub_lines = _wrap_text(subtitle, font_sub, width - 240, draw)
        sub_y = card_top + 78
        for sline in sub_lines:
            draw.text((120, sub_y), sline, font=font_sub, fill=COLOR_WHITE)
            sub_y += 48

        callout_y = card_bot + 45
        draw.rounded_rectangle([80, callout_y, width - 80, callout_y + 115], radius=16, fill=(10, 24, 44, 220), outline=COLOR_BORDER, width=1)
        font_call_tag = _get_font(16, weight="heavy")
        font_call = _get_font(23, weight="medium")
        draw.text((120, callout_y + 26), "EVIDENCIA VERIFICADA", font=font_call_tag, fill=COLOR_CYAN)
        draw.text((120, callout_y + 58), "Datos cuantitativos de Stanford, OIT y Anthropic para líderes de empresa.", font=font_call, fill=COLOR_TEXT_MUTED)

    # -------------------------------------------------------------
    # ARQUETIPO 2: TENSIÓN / EL MITO VS LA REALIDAD
    # -------------------------------------------------------------
    elif "TENSI" in stype or "MITO" in stype or "PARADOJA" in stype:
        font_title = _get_font(46, weight="heavy")
        for line in _wrap_text(stitle, font_title, width - 160, draw):
            draw.text((80, y_cursor), line, font=font_title, fill=COLOR_WHITE)
            y_cursor += 60

        y_cursor += 30
        # Caja 1: Lo que asume el mercado (Mito - Rojo)
        card1_top = y_cursor
        card1_bot = card1_top + 240
        draw.rounded_rectangle([80, card1_top, width - 80, card1_bot], radius=20, fill=COLOR_CARD_RED, outline=(239, 68, 68, 160), width=1)
        _draw_badge_icon(draw, 120, card1_top + 26, is_positive=False)
        font_tag_red = _get_font(20, weight="heavy")
        draw.text((160, card1_top + 28), "EL ERROR COMÚN DEL MERCADO", font=font_tag_red, fill=COLOR_RED)

        font_card_text = _get_font(26, weight="medium")
        myth_text = subtitle if subtitle else "Asumir que la IA reemplaza empleos enteros de golpe."
        m_y = card1_top + 78
        for mline in _wrap_text(myth_text, font_card_text, width - 240, draw):
            draw.text((120, m_y), mline, font=font_card_text, fill=(254, 226, 226, 255))
            m_y += 38

        # Caja 2: Lo que realmente ocurre (La Realidad - Cian)
        card2_top = card1_bot + 35
        card2_bot = min(1180, card2_top + 360)
        draw.rounded_rectangle([80, card2_top, width - 80, card2_bot], radius=20, fill=COLOR_CARD_ALT, outline=(0, 229, 255, 180), width=2)
        _draw_badge_icon(draw, 120, card2_top + 28, is_positive=True)
        font_tag_cyan = _get_font(20, weight="heavy")
        draw.text((160, card2_top + 30), "LO QUE DEMUESTRAN LOS DATOS", font=font_tag_cyan, fill=COLOR_CYAN)

        real_text = body_text if body_text else "Ningún empleo es un bloque indivisible. Un empleo es una colección de 20 a 50 tareas distintas que se desarticulan una a una."
        body_y = card2_top + 84
        for bline in _wrap_text(real_text, font_card_text, width - 240, draw):
            draw.text((120, body_y), bline, font=font_card_text, fill=COLOR_WHITE)
            body_y += 38

    # -------------------------------------------------------------
    # ARQUETIPO 3, 4, 5: EVIDENCIA / DATOS MACRO (STAT CALLOUT)
    # -------------------------------------------------------------
    elif "EVIDENCIA" in stype or "DATO" in stype or any(k in stitle for k in ["%", "de cada"]):
        stat_tuple = _extract_big_stat(stitle) or _extract_big_stat(body_text)
        stat_num = stat_tuple[0] if stat_tuple else None

        if stat_num:
            # Cifra Gigante 115px en Cian Eléctrico
            font_stat = _get_font(115, weight="heavy")
            draw.text((80, y_cursor), stat_num, font=font_stat, fill=COLOR_CYAN)
            y_cursor += 135

            label_text = stitle.replace(stat_num, "").strip(" -:—")
            if not label_text and subtitle:
                label_text = subtitle
            font_stat_lbl = _get_font(38, weight="bold")
            for line in _wrap_text(label_text, font_stat_lbl, width - 160, draw):
                draw.text((80, y_cursor), line, font=font_stat_lbl, fill=COLOR_WHITE)
                y_cursor += 50
        else:
            font_title = _get_font(48, weight="heavy")
            for line in _wrap_text(stitle, font_title, width - 160, draw):
                draw.text((80, y_cursor), line, font=font_title, fill=COLOR_WHITE)
                y_cursor += 62

        y_cursor += 25
        # Cápsula de Fuente Oficial
        source_label = subtitle if (stat_num and subtitle) else (slide.get("footer", "") if "Fuente" in slide.get("footer", "") else "Datos Verificados")
        font_src = _get_font(17, weight="heavy")
        clean_src = source_label.replace("Fuente:", "").strip()
        draw.rounded_rectangle([80, y_cursor, width - 80, y_cursor + 54], radius=12, fill=(13, 20, 36, 240), outline=COLOR_BORDER, width=1)
        draw.text((114, y_cursor + 16), f"FUENTE OFICIAL:  {clean_src.upper()}", font=font_src, fill=COLOR_CYAN)
        y_cursor += 85

        # Tarjeta de Impacto Ejecutivo
        card_top = y_cursor
        card_bot = min(1180, card_top + 380)
        draw.rounded_rectangle([80, card_top, width - 80, card_bot], radius=22, fill=COLOR_CARD, outline=(0, 229, 255, 100), width=1)

        font_body = _get_font(27, weight="medium")
        body_y = card_top + 42
        for bline in _wrap_text(body_text, font_body, width - 240, draw):
            draw.text((120, body_y), bline, font=font_body, fill=COLOR_WHITE)
            body_y += 42

    # -------------------------------------------------------------
    # ARQUETIPO 6: COMPARACIÓN VISUAL (PIERDE VALOR VS MULTIPLICA)
    # -------------------------------------------------------------
    elif "INTERPRET" in stype or "COMPAR" in stype or "PRECIO" in stype:
        font_title = _get_font(46, weight="heavy")
        for line in _wrap_text(stitle, font_title, width - 160, draw):
            draw.text((80, y_cursor), line, font=font_title, fill=COLOR_WHITE)
            y_cursor += 60

        if subtitle:
            font_sub = _get_font(26, weight="bold")
            draw.text((80, y_cursor), subtitle, font=font_sub, fill=COLOR_CYAN)
            y_cursor += 45

        y_cursor += 20

        # Tarjeta 1: Pierde Valor 
        box1_top = y_cursor
        box1_bot = box1_top + 280
        draw.rounded_rectangle([80, box1_top, width - 80, box1_bot], radius=20, fill=COLOR_CARD_RED, outline=(239, 68, 68, 140), width=1)
        _draw_badge_icon(draw, 120, box1_top + 24, is_positive=False)
        font_head_red = _get_font(20, weight="heavy")
        draw.text((160, box1_top + 26), "PIERDE VALOR EN EL MERCADO", font=font_head_red, fill=COLOR_RED)

        font_items = _get_font(24, weight="medium")
        draw.text((120, box1_top + 80), "•  Redactar borradores iniciales sin contexto", font=font_items, fill=(254, 226, 226, 255))
        draw.text((120, box1_top + 130), "•  Búsqueda manual y resumen de documentos", font=font_items, fill=(254, 226, 226, 255))
        draw.text((120, box1_top + 180), "•  Tareas operativas de 'copiar y pegar'", font=font_items, fill=(254, 226, 226, 255))
        draw.text((120, box1_top + 234), ">  Su coste marginal hoy tiende a cero.", font=_get_font(18, weight="demibold"), fill=(252, 165, 165, 255))

        # Tarjeta 2: Multiplica Valor 
        box2_top = box1_bot + 30
        box2_bot = min(1180, box2_top + 330)
        draw.rounded_rectangle([80, box2_top, width - 80, box2_bot], radius=20, fill=COLOR_CARD_ALT, outline=(0, 229, 255, 180), width=2)
        _draw_badge_icon(draw, 120, box2_top + 24, is_positive=True)
        font_head_cyan = _get_font(20, weight="heavy")
        draw.text((160, box2_top + 26), "MULTIPLICA SU VALOR DIRECTIVO", font=font_head_cyan, fill=COLOR_CYAN)

        draw.text((120, box2_top + 80), "•  Formular el problema de negocio exacto", font=font_items, fill=COLOR_WHITE)
        draw.text((120, box2_top + 130), "•  Auditar veracidad, riesgos y alucinaciones", font=font_items, fill=COLOR_WHITE)
        draw.text((120, box2_top + 180), "•  Asumir la responsabilidad final por los resultados", font=font_items, fill=COLOR_WHITE)
        draw.text((120, box2_top + 238), ">  El valor migró de producir a gobernar.", font=_get_font(21, weight="heavy"), fill=COLOR_CYAN)

    # -------------------------------------------------------------
    # ARQUETIPO 7: PROCESO / FRAMEWORK SVE90
    # -------------------------------------------------------------
    elif "DECISI" in stype or "FRAMEWORK" in stype or "METODOLOG" in stype or "SVE90" in stype:
        font_title = _get_font(46, weight="heavy")
        for line in _wrap_text(stitle, font_title, width - 160, draw):
            draw.text((80, y_cursor), line, font=font_title, fill=COLOR_WHITE)
            y_cursor += 60

        font_sub = _get_font(26, weight="bold")
        sub_title_text = subtitle if subtitle else "Metodología SVE90 (Agencia ProsperIA)"
        draw.text((80, y_cursor), sub_title_text, font=font_sub, fill=COLOR_CYAN)
        y_cursor += 50

        steps = [
            ("01 · AUDITAR", "Mapear las 30 tareas críticas y detectar cuellos de botella.", COLOR_CYAN),
            ("02 · AUTOMATIZAR", "Conectar agentes autónomos en captación, agenda y entrega.", (96, 165, 250, 255)),
            ("03 · ADOPTAR", "Entrenar al equipo directivo para auditar y gobernar la IA.", (167, 139, 250, 255)),
        ]

        step_y = y_cursor + 15
        for snum, sdesc, scolor in steps:
            draw.rounded_rectangle([80, step_y, width - 80, step_y + 150], radius=18, fill=COLOR_CARD, outline=(scolor[0], scolor[1], scolor[2], 140), width=1)
            font_snum = _get_font(21, weight="heavy")
            draw.text((120, step_y + 22), snum, font=font_snum, fill=scolor)
            font_sdesc = _get_font(25, weight="medium")
            for sdline in _wrap_text(sdesc, font_sdesc, width - 240, draw):
                draw.text((120, step_y + 64), sdline, font=font_sdesc, fill=COLOR_WHITE)
                step_y += 36
            step_y = step_y + 105

    # -------------------------------------------------------------
    # ARQUETIPO 8: CIERRE / CTA (SAVE MAGNET & CONVERSIÓN)
    # -------------------------------------------------------------
    elif idx == total_slides or "CIERRE" in stype or "CTA" in stype:
        font_title = _get_font(52, weight="heavy")
        for line in _wrap_text(stitle, font_title, width - 160, draw):
            draw.text((80, y_cursor), line, font=font_title, fill=COLOR_WHITE)
            y_cursor += 68

        y_cursor += 25
        card_top = y_cursor
        card_bot = card_top + 480
        draw.rounded_rectangle([80, card_top, width - 80, card_bot], radius=28, fill=(10, 28, 52, 250), outline=COLOR_CYAN, width=2)

        font_cta_badge = _get_font(17, weight="heavy")
        draw.rounded_rectangle([120, card_top + 38, 480, card_top + 80], radius=10, fill=COLOR_CYAN)
        draw.text((136, card_top + 48), "DIAGNÓSTICO OPERATIVO (3 MIN)", font=font_cta_badge, fill=COLOR_BG)

        font_cta_sub = _get_font(34, weight="bold")
        draw.text((120, card_top + 108), "¿Tu empresa delega o gobierna?", font=font_cta_sub, fill=COLOR_WHITE)

        font_cta_p = _get_font(25, weight="medium")
        p_text = "Descubre en qué tareas estás perdiendo margen y cómo implementar agentes autónomos bajo el Sistema SVE90."
        p_y = card_top + 175
        for pline in _wrap_text(p_text, font_cta_p, width - 240, draw):
            draw.text((120, p_y), pline, font=font_cta_p, fill=COLOR_TEXT_MUTED)
            p_y += 38

        link_box_y = card_top + 330
        draw.rounded_rectangle([120, link_box_y, width - 120, link_box_y + 90], radius=16, fill=(6, 14, 28, 255), outline=COLOR_CYAN_DIM, width=1)
        font_url = _get_font(27, weight="heavy")
        draw.text((160, link_box_y + 28), "agenciaprosperia.com/diagnostico", font=font_url, fill=COLOR_CYAN)

        save_y = card_bot + 45
        draw.rounded_rectangle([80, save_y, width - 80, save_y + 80], radius=16, fill=COLOR_CARD, outline=COLOR_BORDER, width=1)
        font_save = _get_font(22, weight="bold")
        draw.text((120, save_y + 26), "Guarda este carrusel para tu próxima reunión directiva.", font=font_save, fill=COLOR_WHITE)

    # -------------------------------------------------------------
    # DEFAULT CONTENIDO
    # -------------------------------------------------------------
    else:
        font_title = _get_font(46, weight="heavy")
        for line in _wrap_text(stitle, font_title, width - 160, draw):
            draw.text((80, y_cursor), line, font=font_title, fill=COLOR_WHITE)
            y_cursor += 58

        if subtitle:
            font_sub = _get_font(26, weight="bold")
            draw.text((80, y_cursor), subtitle, font=font_sub, fill=COLOR_CYAN)
            y_cursor += 42

        if body_text:
            y_cursor += 20
            card_top = y_cursor
            card_bot = min(1180, card_top + 480)
            draw.rounded_rectangle([80, card_top, width - 80, card_bot], radius=22, fill=COLOR_CARD, outline=COLOR_BORDER, width=1)
            font_body = _get_font(26, weight="medium")
            body_y = card_top + 40
            for bline in _wrap_text(body_text, font_body, width - 240, draw):
                draw.text((120, body_y), bline, font=font_body, fill=COLOR_WHITE)
                body_y += 38

    # 4. Footer Institucional
    _draw_footer(draw, slide, idx, total_slides, width)

    final_img = base_img.convert("RGB")
    final_img.save(output_path, "PNG", quality=95)
    return output_path


def render_html_carousel(slides: List[Dict[str, Any]], output_html_path: Path, title: str = "PROSPERIA Intelligence") -> Path:
    """Genera una página HTML interactiva de alta fidelidad con Plus Jakarta Sans y modo de impresión PDF."""
    total_slides = len(slides)
    slides_markup = []

    for idx, s in enumerate(slides, 1):
        stype = html.escape(s.get("type", "CONTENIDO").replace("_", " "))
        stitle = html.escape(s.get("title", ""))
        subtitle = html.escape(s.get("subtitle", ""))
        body = s.get("body", "")
        active_class = "active" if idx == 1 else ""

        body_html = ""
        if body:
            lines = [html.escape(l.strip()) for l in body.split("\n") if l.strip()]
            paragraphs = "".join([f"<p>{l}</p>" for l in lines])
            body_html = f"<div class='card-content'>{paragraphs}</div>"

        slide_html = f"""
        <div class="slide-canvas {active_class}" id="slide-{idx}">
          <div class="ambient-glow glow-cyan"></div>
          <div class="ambient-glow glow-purple"></div>
          <div class="slide-header">
            <div class="brand">
              <span class="dot"></span>
              <strong>PROSPERIA INTELLIGENCE</strong>
              <span class="sep">|</span>
              <span class="sve">SISTEMA SVE90</span>
            </div>
            <div class="badge-num">{idx:02d} / {total_slides:02d}</div>
          </div>
          <div class="slide-body">
            <div class="pill-type">{stype}</div>
            <h2 class="slide-title">{stitle}</h2>
            {f'<p class="slide-sub">{subtitle}</p>' if subtitle else ''}
            {body_html}
          </div>
          <div class="slide-footer">
            <div class="author">
              <div class="av">EJ</div>
              <div>
                <strong>Edward Jiménez</strong>
                <span>@edwardjimenezia</span>
              </div>
            </div>
            <div class="hint">Desliza →</div>
          </div>
        </div>
        """
        slides_markup.append(slide_html)

    full_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>{html.escape(title)} — Carrusel Interactivo</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #060A12;
      --card: #0D1424;
      --cyan: #00E5FF;
      --text: #F8FAFC;
      --muted: #94A3B8;
      --border: rgba(255, 255, 255, 0.08);
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: #02050A;
      color: var(--text);
      font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 30px 20px;
    }}
    .nav-bar {{
      display: flex;
      gap: 16px;
      align-items: center;
      margin-bottom: 24px;
      background: var(--card);
      padding: 10px 24px;
      border-radius: 9999px;
      border: 1px solid var(--border);
    }}
    .btn {{
      background: #182238;
      color: var(--text);
      border: 1px solid var(--border);
      padding: 8px 16px;
      border-radius: 9999px;
      cursor: pointer;
      font-weight: 700;
    }}
    .btn:hover {{ border-color: var(--cyan); }}
    .stage {{
      position: relative;
      width: 540px;
      height: 675px;
      border-radius: 20px;
      overflow: hidden;
      border: 1px solid var(--border);
      box-shadow: 0 30px 80px rgba(0,0,0,0.8);
    }}
    .slide-canvas {{
      position: absolute;
      top: 0; left: 0;
      width: 1080px; height: 1350px;
      transform: scale(0.5);
      transform-origin: top left;
      background: var(--bg);
      display: none;
      flex-direction: column;
      justify-content: space-between;
      padding: 90px 80px 100px 80px;
      overflow: hidden;
    }}
    .slide-canvas.active {{ display: flex; }}
    .ambient-glow {{
      position: absolute;
      width: 500px; height: 500px;
      border-radius: 50%;
      filter: blur(140px);
      opacity: 0.18;
      pointer-events: none;
    }}
    .glow-cyan {{ top: -100px; right: -100px; background: var(--cyan); }}
    .glow-purple {{ bottom: -100px; left: -100px; background: #818CF8; }}
    .slide-header {{
      display: flex; justify-content: space-between; align-items: center;
      border-bottom: 1px solid var(--border); padding-bottom: 24px;
      position: relative; z-index: 10;
    }}
    .brand {{ display: flex; align-items: center; gap: 12px; font-size: 22px; }}
    .dot {{ width: 14px; height: 14px; border-radius: 50%; background: var(--cyan); }}
    .sep {{ opacity: 0.3; }}
    .sve {{ color: var(--cyan); font-weight: 700; font-size: 18px; }}
    .badge-num {{
      background: var(--card); border: 1px solid rgba(0,229,255,0.4);
      padding: 6px 18px; border-radius: 12px; color: var(--cyan); font-weight: 800; font-size: 20px;
    }}
    .slide-body {{ position: relative; z-index: 10; margin: auto 0; display: flex; flex-direction: column; gap: 24px; }}
    .pill-type {{
      align-self: flex-start; background: var(--card); border: 1px solid rgba(0,229,255,0.4);
      padding: 8px 20px; border-radius: 9999px; color: var(--cyan); font-weight: 800; font-size: 18px;
    }}
    .slide-title {{ font-size: 56px; font-weight: 800; line-height: 1.15; }}
    .slide-sub {{ font-size: 32px; font-weight: 700; color: var(--cyan); line-height: 1.3; }}
    .card-content {{
      background: var(--card); border: 1px solid var(--border); border-radius: 20px;
      padding: 36px; display: flex; flex-direction: column; gap: 16px; font-size: 26px; color: var(--muted);
    }}
    .slide-footer {{
      display: flex; justify-content: space-between; align-items: center;
      border-top: 1px solid var(--border); padding-top: 28px;
      position: relative; z-index: 10;
    }}
    .author {{ display: flex; align-items: center; gap: 14px; }}
    .av {{
      width: 52px; height: 52px; border-radius: 50%; background: var(--card);
      border: 2px solid var(--cyan); color: var(--cyan); display: flex;
      align-items: center; justify-content: center; font-weight: 800; font-size: 20px;
    }}
    .author strong {{ display: block; font-size: 20px; }}
    .author span {{ font-size: 15px; color: var(--muted); }}
    .hint {{ font-weight: 800; color: var(--cyan); font-size: 20px; }}
  </style>
</head>
<body>
  <div class="nav-bar">
    <button class="btn" onclick="prev()">← Anterior</button>
    <span id="counter" style="color: var(--cyan); font-weight: 800;">1 / {total_slides}</span>
    <button class="btn" onclick="next()">Siguiente →</button>
  </div>
  <div class="stage">
    {''.join(slides_markup)}
  </div>
  <script>
    let cur = 1;
    const total = {total_slides};
    function show(n) {{
      document.querySelectorAll('.slide-canvas').forEach(s => s.classList.remove('active'));
      const s = document.getElementById('slide-' + n);
      if (s) s.classList.add('active');
      document.getElementById('counter').innerText = n + ' / ' + total;
    }}
    function next() {{ cur = (cur >= total) ? 1 : cur + 1; show(cur); }}
    function prev() {{ cur = (cur <= 1) ? total : cur - 1; show(cur); }}
  </script>
</body>
</html>
"""
    output_html_path.write_text(full_html, encoding="utf-8")
    return output_html_path


def render_png_slides(slides: List[Dict[str, Any]], output_dir: Path) -> List[Path]:
    """Genera láminas 1080x1350 PNG de alta definición para cada diapositiva."""
    output_dir.mkdir(parents=True, exist_ok=True)
    total_slides = len(slides)
    generated_pngs: List[Path] = []

    print(f"[Renderer] Generando {total_slides} láminas 1080x1350 HD con arquetipos visuales diferenciados...")
    for idx, slide in enumerate(slides, 1):
        png_path = output_dir / f"{idx:02d}.png"
        render_slide_pillow(slide, idx, total_slides, png_path)
        generated_pngs.append(png_path)

    html_path = output_dir.parent / "carrusel_interactivo.html"
    render_html_carousel(slides, html_path)

    print(f"✓ {len(generated_pngs)} láminas PNG generadas con éxito en: {output_dir}")
    return generated_pngs


def render_pdf_carousel(slides: List[Dict[str, Any]], output_pdf: Path) -> bool:
    """Compila las láminas en un archivo PDF multipágina 4:5 de alta definición para LinkedIn."""
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
            print(f"✓ PDF de carrusel para LinkedIn generado: {output_pdf.name} ({output_pdf.stat().st_size / 1024:.1f} KB)")
            return True
        return False
    finally:
        for f in temp_dir.glob("*.png"):
            f.unlink(missing_ok=True)
        try:
            temp_dir.rmdir()
        except Exception:
            pass

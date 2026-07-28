"""Genera portadas para todos los artículos existentes en INITIAL_BLOG_POSTS.

Lee la lista de posts del módulo main.py y genera una imagen de portada
para cada uno en la carpeta static/blog/, utilizando Pollinations AI
con fallback a Pillow (PIL).

Este script NO requiere GEMINI_API_KEY ya que solo genera imágenes,
no texto. Importa las funciones de imagen directamente.
"""
import os
import sys
import requests
from PIL import Image, ImageDraw

# Reconfigurar stdout para soportar emojis UTF-8 en Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def generate_cyber_cover(filepath, title, category="Automatización"):
    """Genera una portada para el artículo del blog.

    Intenta descargar una imagen generada por Pollinations AI.
    Si la API no responde en 5 segundos, genera una portada
    vectorial local con Pillow (PIL) como fallback.

    Args:
        filepath: Ruta donde guardar la imagen resultante.
        title: Título del artículo (usado en el prompt de IA).
        category: Categoría del artículo para contexto del prompt.
    """
    prompt = (
        f"Futuristic 3D corporate banner, dark navy background #020710, "
        f"glowing cyan #00e5ff accents, abstract geometric AI neural network, "
        f"topic: {title[:80]}, category: {category}, "
        f"ultra high quality 8K, no text, no watermark"
    )
    url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=800&height=500&nologo=true"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200 and len(resp.content) > 1000:
            with open(filepath, "wb") as f:
                f.write(resp.content)
            print(f"✅ Imagen IA generada: {filepath}")
            return
    except Exception as e:
        print(f"⚠️ Error conectando con API de imagen IA ({e}). Usando generador gráfico local PIL...")

    # Fallback: generar portada vectorial con PIL
    _generate_pil_fallback(filepath, title)
    print(f"✅ Imagen PIL vectorial creada: {filepath}")


def _generate_pil_fallback(filepath, title):
    """Genera una portada cibernética abstracta con Pillow como fallback."""
    import random
    import math

    width, height = 800, 500
    image = Image.new("RGBA", (width, height), (2, 7, 16, 255))
    draw = ImageDraw.Draw(image, "RGBA")

    # Degradado radial suave
    cx, cy = width // 2, height // 2
    for radius in range(300, 0, -5):
        alpha = max(0, min(255, int(30 * (1 - radius / 300))))
        draw.ellipse(
            [cx - radius, cy - radius, cx + radius, cy + radius],
            fill=(0, 229, 255, alpha)
        )

    # Rejilla vectorial
    grid_color = (0, 229, 255, 12)
    for x in range(0, width, 40):
        draw.line([(x, 0), (x, height)], fill=grid_color, width=1)
    for y in range(0, height, 40):
        draw.line([(0, y), (width, y)], fill=grid_color, width=1)

    # Círculos concéntricos
    tech_cyan = (0, 229, 255, 30)
    tech_blue = (14, 165, 233, 40)
    for r in [120, 180, 240]:
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=tech_cyan, width=1)

    # Hexágonos
    def draw_polygon(center_x, center_y, radius, sides, color, w=1, rotation=0):
        points = []
        for i in range(sides):
            angle = rotation + (i * 2 * math.pi / sides)
            px = center_x + radius * math.cos(angle)
            py = center_y + radius * math.sin(angle)
            points.append((px, py))
        for i in range(sides):
            p1 = points[i]
            p2 = points[(i + 1) % sides]
            draw.line([p1, p2], fill=color, width=w)
            if i % 2 == 0:
                draw.line([p1, (center_x, center_y)], fill=(color[0], color[1], color[2], 12), width=1)
        return points

    draw_polygon(cx, cy, 140, 6, tech_cyan, w=2, rotation=0.5)
    pts = draw_polygon(cx, cy, 200, 6, tech_blue, w=1, rotation=0.2)

    for pt in pts:
        rx = 4
        draw.ellipse([pt[0] - rx, pt[1] - rx, pt[0] + rx, pt[1] + rx], fill=(0, 229, 255, 180))

    final_image = image.convert("RGB")
    final_image.save(filepath, "JPEG", quality=90)


if __name__ == "__main__":
    # Importar INITIAL_BLOG_POSTS sin activar la validación de GEMINI_API_KEY
    # Hacemos un import selectivo del listado de posts
    import importlib.util
    spec = importlib.util.spec_from_file_location("main_module", "main.py")
    # Para evitar el sys.exit de generate_ai_posts al importar main,
    # leemos directamente el listado con un approach más simple
    import re

    with open("main.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Extraer slugs y títulos con regex
    slugs = re.findall(r'"slug":\s*"([^"]+)"', content)
    titles = re.findall(r'"title":\s*"([^"]+)"', content)
    categories = re.findall(r'"category":\s*"([^"]+)"', content)

    blog_dir = os.path.join("static", "blog")
    os.makedirs(blog_dir, exist_ok=True)

    print(f"Procesando {len(slugs)} artículos existentes en '{blog_dir}'...")

    for slug, title, category in zip(slugs, titles, categories):
        filepath = os.path.join(blog_dir, f"{slug}.jpg")
        title_preview = title[:50] + "..." if len(title) > 50 else title
        print(f"Generando imagen IA para: {title_preview}")
        generate_cyber_cover(filepath, title, category)

    print(f"\n✨ Proceso completado exitosamente para todas las publicaciones en {blog_dir}/.")

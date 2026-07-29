"""Genera portadas para todos los artículos existentes usando Gemini Imagen.

Usa la API de Gemini (gemini-2.0-flash-exp) para generar imágenes
fotorrealistas editoriales para cada artículo del blog.

Requiere: GEMINI_API_KEY como variable de entorno.
"""
import os
import sys
import re
import time
import base64
import json
import requests

# Reconfigurar stdout para soportar emojis UTF-8 en Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Cargar API key desde .env local o AIEngineCentral
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    for env_path in [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"),
        r"e:\Proyectos\Central de IAs\AIEngineCentral\.env",
    ]:
        if not os.path.exists(env_path):
            continue
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("GEMINI_API_KEY=") and not line.startswith("#"):
                    GEMINI_API_KEY = line.split("=", 1)[1].strip()
                    break
        if GEMINI_API_KEY:
            break

if not GEMINI_API_KEY:
    print("❌ Error: No se encontró GEMINI_API_KEY.")
    sys.exit(1)

API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-3.1-flash-image:generateContent"
    f"?key={GEMINI_API_KEY}"
)


def generate_cover_gemini(filepath, title, category="Automatización"):
    """Genera una portada editorial con Gemini Imagen.

    Args:
        filepath: Ruta donde guardar la imagen resultante.
        title: Título del artículo.
        category: Categoría del artículo.

    Returns:
        True si la imagen se generó con éxito, False en caso contrario.
    """
    prompt = (
        f"Generate a professional, photorealistic editorial banner image (800x500px) "
        f"for a blog article titled: '{title}'. "
        f"Category: {category}. "
        f"The image should visually represent the article's topic. "
        f"Modern corporate aesthetic, warm cinematic lighting, vivid colors, "
        f"eye-catching composition. "
        f"Do NOT include any text, watermarks, or logos in the image."
    )

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"]
        }
    }

    try:
        resp = requests.post(API_URL, json=payload, timeout=60)
        if resp.status_code != 200:
            print(f"  ❌ API respondió con status {resp.status_code}: {resp.text[:200]}")
            return False

        data = resp.json()

        # Buscar la parte con imagen en la respuesta
        candidates = data.get("candidates", [])
        for candidate in candidates:
            parts = candidate.get("content", {}).get("parts", [])
            for part in parts:
                if "inlineData" in part:
                    img_data = part["inlineData"]["data"]
                    img_bytes = base64.b64decode(img_data)
                    with open(filepath, "wb") as f:
                        f.write(img_bytes)
                    print(f"  ✅ Imagen Gemini generada ({len(img_bytes)//1024}KB)")
                    return True

        print(f"  ⚠️ Respuesta sin imagen: {json.dumps(data)[:200]}")
        return False

    except requests.exceptions.Timeout:
        print(f"  ⏱️ Timeout (60s)")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


if __name__ == "__main__":
    with open("main.py", "r", encoding="utf-8") as f:
        content = f.read()

    slugs = re.findall(r'"slug":\s*"([^"]+)"', content)
    titles = re.findall(r'"title":\s*"([^"]+)"', content)
    categories = re.findall(r'"category":\s*"([^"]+)"', content)

    blog_dir = os.path.join("static", "blog")
    os.makedirs(blog_dir, exist_ok=True)

    total = len(slugs)
    ok = 0
    failed = 0

    print(f"🚀 Generando {total} portadas con Gemini Imagen...")
    print(f"   Modelo: gemini-2.0-flash-exp | Timeout: 60s\n")

    for i, (slug, title, category) in enumerate(zip(slugs, titles, categories), 1):
        filepath = os.path.join(blog_dir, f"{slug}.jpg")
        title_preview = title[:60] + "..." if len(title) > 60 else title
        print(f"[{i}/{total}] {title_preview}")

        success = generate_cover_gemini(filepath, title, category)
        if success:
            ok += 1
        else:
            failed += 1

        # Pausa breve entre peticiones para no saturar
        if i < total:
            time.sleep(2)

    print(f"\n✨ Completado: {ok} exitosas, {failed} fallidas.")

import os
import sys
import json
import random
import datetime
import requests
from PIL import Image, ImageDraw

# Reconfigurar stdout para soportar emojis UTF-8 en Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Configuración de la API de Gemini
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("Error: La variable de entorno GEMINI_API_KEY no está configurada.")
    sys.exit(1)

API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

def generate_blog_posts():
    print("Consultando la API de Gemini para generar 6 artículos del blog...")
    
    prompt = """
    Eres el redactor jefe y experto en Inteligencia Artificial y Ventas B2B de 'Prosper IA'.
    Tu nicho de mercado son los CEOs, dueños de negocios y directores comerciales de empresas de servicios en Latinoamérica (México, Colombia, Chile, Perú).
    El estilo y tono de tu marca es altamente profesional, enfocado en el retorno de inversión (ROI), la optimización operativa y la soberanía de datos.
    Tus pilares conceptuales principales son:
    1. El 'Sistema SVE90' (Sistema de Ventas Eficientes en 90 días).
    2. Los 'AI SDRs' y 'AI Setters' (agentes virtuales autónomos que califican leads en frío y agendan citas 24/7 en WhatsApp e Instagram).
    3. La plataforma 'PassportAI' (software centralizado y seguro de Prosper IA para evitar la dispersión de herramientas).
    4. Los 'SOPs' (Procedimientos Operativos Estándar) y la capacitación del equipo humano a través de 'AZ Academy' para asegurar la adopción.

    Escribe 6 artículos nuevos y relevantes para el blog de Prosper IA en 2026.
    Los artículos deben abarcar temas variados dentro de tu nicho (ej. regulaciones de APIs, Click-to-WhatsApp, IA vs Chatbots obsoletos, casos de estudio en LATAM, blindaje operativo).
    Cada artículo debe ser extremadamente completo, profesional y largo, conteniendo al menos 4-5 párrafos.

    Devuelve la respuesta estrictamente en formato JSON utilizando el esquema requerido, sin bloques markdown de código adicionales.
    """

    headers = {
        "Content-Type": "application/json"
    }

    schema = {
        "type": "ARRAY",
        "description": "Lista de 6 nuevos artículos de blog estructurados para Prosper IA",
        "items": {
            "type": "OBJECT",
            "properties": {
                "slug": {"type": "STRING", "description": "Slug de URL amigable único, todo en minúsculas y con guiones (ej. inteligencia-artificial-crm-latam)"},
                "title": {"type": "STRING", "description": "Título profesional, llamativo e impactante para CEOs"},
                "category": {"type": "STRING", "description": "Debe ser estrictamente una de estas: 'Marketing & CRM', 'Operaciones', 'Automatización', 'Casos de Éxito'"},
                "summary": {"type": "STRING", "description": "Un resumen ejecutivo del artículo de 2 líneas"},
                "content": {"type": "STRING", "description": "Contenido completo del artículo estructurado con etiquetas HTML de párrafo <p class=\\\"mb-4 text-slate-300 leading-relaxed\\\">. Usa negritas con <strong> en palabras clave. Al final del contenido incluye una sección de referencias con título <h3>Referencias y Estudios de Caso</h3> y una lista de 3 viñetas con <ul class=\\\"list-disc pl-5 space-y-2 text-slate-400 text-sm\\\"> y <li> para sustentar científicamente el artículo con marcas como Gartner, McKinsey, Harvard Business Review o Salesforce."},
                "author": {"type": "STRING", "description": "Nombre del autor. Usar 'Edward Jiménez'"}
            },
            "required": ["slug", "title", "category", "summary", "content", "author"]
        }
    }

    body = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": schema
        }
    }

    try:
        response = requests.post(API_URL, headers=headers, json=body)
        response.raise_for_status()
        result = response.json()
        
        # Obtener el texto de la respuesta
        text_content = result["candidates"][0]["content"]["parts"][0]["text"]
        posts = json.loads(text_content)
        
        if not isinstance(posts, list):
            raise ValueError(f"La respuesta no es una lista válida: {type(posts)}")
            
        if len(posts) > 6:
            print(f"Aviso: Se generaron {len(posts)} artículos. Recortando a los primeros 6.")
            posts = posts[:6]
        elif len(posts) < 6:
            print(f"Aviso: Se generaron solo {len(posts)} de los 6 artículos solicitados.")
            
        return posts
    except Exception as e:
        print(f"Error al generar artículos de Gemini: {e}")
        # En caso de error de conexión o API, levantar excepción
        raise e

def generate_cyber_cover(filepath, title, category="Automatización"):
    """Genera una portada editorial fotorrealista con Gemini Imagen.

    Usa el modelo gemini-3.1-flash-image para generar imágenes
    contextualizadas al tema del artículo.

    Args:
        filepath: Ruta donde guardar la imagen resultante.
        title: Título del artículo (usado en el prompt de IA).
        category: Categoría del artículo para contexto del prompt.
    """
    import base64

    image_api_url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "gemini-3.1-flash-image:generateContent"
        f"?key={GEMINI_API_KEY}"
    )
    prompt = (
        f"Generate a professional, photorealistic editorial banner image (800x500px) "
        f"for a blog article titled: '{title[:120]}'. "
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
        resp = requests.post(image_api_url, json=payload, timeout=60)
        if resp.status_code == 200:
            data = resp.json()
            for candidate in data.get("candidates", []):
                for part in candidate.get("content", {}).get("parts", []):
                    if "inlineData" in part:
                        img_bytes = base64.b64decode(part["inlineData"]["data"])
                        with open(filepath, "wb") as f:
                            f.write(img_bytes)
                        print(f"✅ Imagen Gemini generada: {filepath}")
                        return
        print(f"⚠️ Gemini no devolvió imagen (status={resp.status_code})")
    except Exception as e:
        print(f"⚠️ Error generando imagen con Gemini ({e})")

    # Fallback mínimo: crear placeholder con PIL
    _generate_pil_fallback(filepath, title)
    print(f"✅ Imagen PIL placeholder creada: {filepath}")


def _generate_pil_fallback(filepath, title):
    """Genera un placeholder visual único por título usando PIL."""
    import hashlib
    import math

    seed = int(hashlib.md5(title.encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)

    width, height = 800, 500
    hue = rng.randint(0, 60)
    image = Image.new("RGBA", (width, height), (2 + hue // 4, 7 + hue // 3, max(16, 40 - hue // 2), 255))
    draw = ImageDraw.Draw(image, "RGBA")

    accent = (rng.randint(0, 80), rng.randint(160, 255), rng.randint(200, 255))

    # Degradado radial
    cx, cy = rng.randint(200, 600), rng.randint(125, 375)
    for radius in range(300, 0, -5):
        alpha = max(0, min(255, int(35 * (1 - radius / 300))))
        draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
                     fill=(accent[0], accent[1], accent[2], alpha))

    # Rejilla
    spacing = rng.randint(30, 60)
    for x in range(0, width, spacing):
        draw.line([(x, 0), (x, height)], fill=(accent[0], accent[1], accent[2], 12))
    for y in range(0, height, spacing):
        draw.line([(0, y), (width, y)], fill=(accent[0], accent[1], accent[2], 12))

    # Formas
    for _ in range(rng.randint(3, 7)):
        sx, sy = rng.randint(50, 750), rng.randint(50, 450)
        sr = rng.randint(40, 180)
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr],
                     outline=(accent[0], accent[1], accent[2], rng.randint(15, 40)), width=2)

    final_image = image.convert("RGB")
    final_image.save(filepath, "JPEG", quality=90)

def update_main_py(new_posts):
    print("Actualizando el archivo main.py con los nuevos artículos...")
    with open("main.py", "r", encoding="utf-8") as f:
        content = f.read()
        
    # Buscar el inicio de la lista INITIAL_BLOG_POSTS
    target = "INITIAL_BLOG_POSTS = ["
    idx = content.find(target)
    
    if idx == -1:
        print("Error: No se encontró la definición de INITIAL_BLOG_POSTS en main.py")
        sys.exit(1)
        
    # Construir el bloque de strings de los nuevos artículos
    new_posts_str = ""
    for post in new_posts:
        # Escapar caracteres de comillas simples o dobles en los strings
        title_esc = post["title"].replace('"', '\\"').replace('\n', ' ')
        summary_esc = post["summary"].replace('"', '\\"').replace('\n', ' ')
        content_esc = post["content"].replace('"""', '\\"\\"\\"')
        
        new_posts_str += f"""    {{
        "slug": "{post['slug']}",
        "title": "{title_esc}",
        "category": "{post['category']}",
        "summary": "{summary_esc}",
        "content": \"\"\"{content_esc}\"\"\",
        "image_url": "/static/blog/{post['slug']}.jpg",
        "published_at": "{post['published_at']}",
        "author": "{post['author']}"
    }},
"""
    
    # Insertar al inicio de la lista
    insert_pos = idx + len(target) + 1
    updated_content = content[:insert_pos] + new_posts_str + content[insert_pos:]
    
    with open("main.py", "w", encoding="utf-8") as f:
        f.write(updated_content)
        
    print("main.py actualizado correctamente.")

def main():
    try:
        # 1. Generar artículos con Gemini
        posts = generate_blog_posts()
        
        # 2. Agregar fechas progresivas basadas en la hora actual
        now = datetime.datetime.utcnow()
        for i, post in enumerate(posts):
            # Asignar fecha en orden descendente (el primero es el más nuevo)
            publish_time = now + datetime.timedelta(hours=i)
            post["published_at"] = publish_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            
        # 3. Generar portadas en static/blog/ e insertar los posts
        blog_dir = os.path.join("static", "blog")
        os.makedirs(blog_dir, exist_ok=True)
        for post in posts:
            image_filename = f"{post['slug']}.jpg"
            image_filepath = os.path.join(blog_dir, image_filename)
            generate_cyber_cover(image_filepath, post["title"], post.get("category", "Automatización"))
            
        # 4. Modificar main.py
        update_main_py(posts)
        print("Automatización finalizada con éxito. Se crearon 6 artículos y 6 portadas.")
        
    except Exception as e:
        print(f"Error durante el proceso de automatización: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

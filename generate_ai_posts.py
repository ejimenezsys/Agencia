import os
import sys
import json
import random
import datetime
import requests
from PIL import Image, ImageDraw

# Configuración de la API de Gemini
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("Error: La variable de entorno GEMINI_API_KEY no está configurada.")
    sys.exit(1)

API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

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
        
        if not isinstance(posts, list) or len(posts) != 6:
            raise ValueError(f"La respuesta no contiene exactamente 6 elementos: {len(posts) if isinstance(posts, list) else type(posts)}")
            
        return posts
    except Exception as e:
        print(f"Error al generar artículos de Gemini: {e}")
        # En caso de error de conexión o API, levantar excepción
        raise e

def generate_cyber_cover(filepath, title):
    """Genera programáticamente una portada cibernética abstracta de alta calidad."""
    width, height = 800, 500
    image = Image.new("RGBA", (width, height), (2, 7, 16, 255)) # Fondo #020710 (Navy oscuro)
    draw = ImageDraw.Draw(image)
    
    # 1. Dibujar un degradado radial de fondo simulando un glow cian
    glow_color = (0, 229, 255) # Cian
    glow_center_x, glow_center_y = random.randint(150, 450), random.randint(150, 350)
    for radius in range(500, 0, -10):
        alpha = int((1 - (radius / 500)) ** 4 * 25) # Glow suave
        draw.ellipse(
            [glow_center_x - radius, glow_center_y - radius, glow_center_x + radius, glow_center_y + radius],
            fill=(glow_color[0], glow_color[1], glow_color[2], alpha)
        )
        
    # 2. Dibujar rejilla vectorial de fondo (Grid)
    grid_color = (0, 229, 255, 8) # Rejilla cian muy tenue
    for x in range(0, width, 40):
        draw.line([(x, 0), (x, height)], fill=grid_color, width=1)
    for y in range(0, height, 40):
        draw.line([(0, y), (width, y)], fill=grid_color, width=1)
        
    # 3. Dibujar círculos y hexágonos cibernéticos concéntricos
    tech_cyan = (0, 229, 255, 30)
    tech_blue = (14, 165, 233, 40)
    cx, cy = width // 2, height // 2
    
    # Dibujar órbitas tenues
    for r in [120, 180, 240]:
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=tech_cyan, width=1)
        
    # Dibujar hexágono concéntrico con líneas radiales conectadas
    def draw_polygon(center_x, center_y, radius, sides, color, width=1, rotation=0):
        import math
        points = []
        for i in range(sides):
            angle = rotation + (i * 2 * math.pi / sides)
            px = center_x + radius * math.cos(angle)
            py = center_y + radius * math.sin(angle)
            points.append((px, py))
        
        for i in range(sides):
            p1 = points[i]
            p2 = points[(i + 1) % sides]
            draw.line([p1, p2], fill=color, width=width)
            # Conexión radial al centro
            if i % 2 == 0:
                draw.line([p1, (center_x, center_y)], fill=(color[0], color[1], color[2], 12), width=1)
        return points

    # Dibujar varios polígonos
    draw_polygon(cx, cy, 140, 6, tech_cyan, width=2, rotation=0.5)
    pts = draw_polygon(cx, cy, 200, 6, tech_blue, width=1, rotation=0.2)
    
    # Dibujar pequeños nodos brillantes en los vértices
    for pt in pts:
        rx = 4
        draw.ellipse([pt[0] - rx, pt[1] - rx, pt[0] + rx, pt[1] + rx], fill=(0, 229, 255, 180))
        
    # 4. Convertir a RGB y guardar como JPG
    final_image = image.convert("RGB")
    final_image.save(filepath, "JPEG", quality=90)
    print(f"Portada creada exitosamente: {filepath}")

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
        "image_url": "/static/{post['slug']}.jpg",
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
            
        # 3. Generar portadas e insertar los posts
        os.makedirs("static", exist_ok=True)
        for post in posts:
            image_filename = f"{post['slug']}.jpg"
            image_filepath = os.path.join("static", image_filename)
            generate_cyber_cover(image_filepath, post["title"])
            
        # 4. Modificar main.py
        update_main_py(posts)
        print("Automatización finalizada con éxito. Se crearon 6 artículos y 6 portadas.")
        
    except Exception as e:
        print(f"Error durante el proceso de automatización: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

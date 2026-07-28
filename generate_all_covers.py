import os
import sys
import urllib.parse
import requests
from PIL import Image, ImageDraw
from main import INITIAL_BLOG_POSTS

def generate_cyber_cover_fallback(filepath, title):
    """Genera una portada cibernética abstracta mediante Pillow (PIL) en caso de fallback."""
    width, height = 800, 500
    image = Image.new("RGBA", (width, height), (2, 7, 16, 255))
    
    cx, cy = width // 2, height // 2
    for y in range(height):
        for x in range(width):
            dx = x - cx
            dy = y - cy
            dist = (dx*dx + dy*dy) ** 0.5
            factor = min(1.0, dist / 500.0)
            r = int(8 - (8 - 2) * factor)
            g = int(26 - (26 - 7) * factor)
            b = int(48 - (48 - 16) * factor)
            image.putpixel((x, y), (r, g, b, 255))
            
    draw = ImageDraw.Draw(image)
    
    for radius in range(120, 0, -8):
        alpha = int((1.0 - (radius / 120.0)) ** 2 * 30)
        draw.ellipse(
            [cx - radius, cy - radius, cx + radius, cy + radius],
            fill=(0, 229, 255, alpha)
        )
        
    grid_color = (0, 229, 255, 12)
    for x in range(0, width, 40):
        draw.line([(x, 0), (x, height)], fill=grid_color, width=1)
    for y in range(0, height, 40):
        draw.line([(0, y), (width, y)], fill=grid_color, width=1)
        
    tech_cyan = (0, 229, 255, 30)
    tech_blue = (14, 165, 233, 40)
    
    for r in [120, 180, 240]:
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=tech_cyan, width=1)
        
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
            if i % 2 == 0:
                draw.line([p1, (center_x, center_y)], fill=(color[0], color[1], color[2], 12), width=1)
        return points

    draw_polygon(cx, cy, 140, 6, tech_cyan, width=2, rotation=0.5)
    pts = draw_polygon(cx, cy, 200, 6, tech_blue, width=1, rotation=0.2)
    
    for pt in pts:
        rx = 4
        draw.ellipse([pt[0] - rx, pt[1] - rx, pt[0] + rx, pt[1] + rx], fill=(0, 229, 255, 180))
        
    final_image = image.convert("RGB")
    final_image.save(filepath, "JPEG", quality=90)

def generate_ai_image(filepath, title, category):
    """Genera una imagen con IA a través de Pollinations AI o usa fallback en PIL."""
    prompt = f"high tech futuristic 3d banner header representing {title}, theme {category}, dark navy neon cyan lighting, 8k resolution, professional b2b corporate style"
    encoded_prompt = urllib.parse.quote(prompt)
    seed = abs(hash(title)) % 10000
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=800&height=500&nologo=true&seed={seed}"
    
    try:
        print(f"Generando imagen IA para: {title[:45]}...")
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200 and len(resp.content) > 5000:
            with open(filepath, "wb") as f:
                f.write(resp.content)
            print(f"✅ Imagen IA generada: {filepath}")
            return True
    except Exception as e:
        print(f"⚠️ Error conectando con API de imagen IA ({e}). Usando generador gráfico local PIL...")
        
    generate_cyber_cover_fallback(filepath, title)
    print(f"✅ Imagen PIL vectorial creada: {filepath}")
    return False

def process_all_existing_posts():
    blog_dir = os.path.join("static", "blog")
    os.makedirs(blog_dir, exist_ok=True)
    print(f"Procesando {len(INITIAL_BLOG_POSTS)} artículos existentes en '{blog_dir}'...")
    
    for post in INITIAL_BLOG_POSTS:
        slug = post["slug"]
        image_path = os.path.join(blog_dir, f"{slug}.jpg")
        generate_ai_image(image_path, post["title"], post["category"])
        
    print("✨ Proceso completado exitosamente para todas las publicaciones en static/blog/.")

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    process_all_existing_posts()

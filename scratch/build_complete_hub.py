import os
import json
import pypdf
import re

# Load Colección 1
with open('content/codigos_100.json', 'r', encoding='utf-8') as f:
    col1_raw = json.load(f)

# Parse Colección 2 from PDF
reader = pypdf.PdfReader('static/codigos/Codigos_Creativos_ChatGPT_Edward_Jimenez_ES_ProsperIA.pdf')
col2_raw = []
for p_idx in range(1, 11):
    txt = reader.pages[p_idx].extract_text()
    lines = [l.strip() for l in txt.split('\n') if l.strip()]
    cat_id = f'{p_idx:02d}'
    
    cat_name = ''
    for line in lines[1:5]:
        if any(w in line for w in ['ILUMINACIÓN', 'SURREALISTA', 'ENCUADRE', 'TRAS CÁMARAS', 'CÁMARA', 'FOTOGRAFÍA', 'EXPERIMENTOS', 'ESTÉTICAS', 'ACCIÓN', 'PRODUCTO']):
            cat_name = re.sub(r'\s*\d{3}-\d{3}.*', '', line).strip()
            break
    
    items = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith('/'):
            cmd = line
            item_num = ''
            if i > 0 and re.match(r'^\d{2,3}$', lines[i-1]):
                item_num = lines[i-1]
            desc_lines = []
            j = i + 1
            while j < len(lines) and not lines[j].startswith('/') and not re.match(r'^\d{2,3}$', lines[j]) and not lines[j].startswith('@edwardjimenezia'):
                desc_lines.append(lines[j])
                j += 1
            desc = ' '.join(desc_lines).strip()
            items.append({
                'sub_number': item_num,
                'command': cmd,
                'description': desc
            })
            i = j - 1
        i += 1
    col2_raw.append({
        'category_id': cat_id,
        'category_name': cat_name or f'Categoría {cat_id}',
        'items': items
    })

category_icons = {
    "01": "fa-lightbulb",
    "02": "fa-paint-brush",
    "03": "fa-eye",
    "04": "fa-sun",
    "05": "fa-video",
    "06": "fa-palette",
    "07": "fa-film",
    "08": "fa-camera",
    "09": "fa-running",
    "10": "fa-box-open"
}

category_names = {
    "01": "Iluminación de Estudio y Publicidad",
    "02": "Composición y Planos Fotográficos",
    "03": "Retrato Cinematográfico y Expresión",
    "04": "Dirección de Luz Natural y Hora Mágica",
    "05": "Ángulos Dinámicos y Movimiento",
    "06": "Texturas, Moda y Paletas de Color",
    "07": "Efectos Visuales y Cinematografía",
    "08": "Estilismo Editorial y Lookbook",
    "09": "Acción, Impacto y Alto Contraste",
    "10": "Packshot y Fotografía de Producto"
}

# Unify all 200 codes
all_codes = []
for cat in col1_raw:
    cid = cat["category_id"]
    cname = cat["category_name"]
    for item in cat["items"]:
        all_codes.append({
            "collection": "col1",
            "collection_name": "Colección 1: Prompts ChatGPT",
            "collection_badge": "COL 1 · PROMPTS",
            "collection_badge_color": "border-cyan-500/40 bg-cyan-950/60 text-cyan-300",
            "global_num": len(all_codes) + 1,
            "sub_num": item["number"],
            "cat_id": cid,
            "cat_name": cname,
            "command": item["command"],
            "desc": item["description"],
            "icon": category_icons.get(cid, "fa-terminal")
        })

for cat in col2_raw:
    cid = cat["category_id"]
    cname = category_names.get(cid, cat["category_name"])
    for item in cat["items"]:
        all_codes.append({
            "collection": "col2",
            "collection_name": "Colección 2: Fotografía Edward Jiménez",
            "collection_badge": "COL 2 · FOTOGRAFÍA",
            "collection_badge_color": "border-indigo-500/40 bg-indigo-950/60 text-indigo-300",
            "global_num": len(all_codes) + 1,
            "sub_num": item["sub_number"],
            "cat_id": cid,
            "cat_name": cname,
            "command": item["command"],
            "desc": item["description"],
            "icon": category_icons.get(cid, "fa-camera")
        })

print(f"Total codes combined: {len(all_codes)}")

# Build category pills HTML
cat_pills_html = []
cat_pills_html.append('<button class="filter-chip active px-3.5 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap" data-cat="all" onclick="filterCategory(\'all\', this)"><i class="fas fa-th-large mr-1 text-[10px]"></i> Todas las Categorías (200)</button>')
for cat_id in sorted(category_names.keys()):
    cname = category_names[cat_id]
    count_in_cat = sum(1 for c in all_codes if c["cat_id"] == cat_id)
    icon_cls = category_icons.get(cat_id, "fa-tag")
    cat_pills_html.append(f'<button class="filter-chip px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap" data-cat="{cat_id}" onclick="filterCategory(\'{cat_id}\', this)"><i class="fas {icon_cls} mr-1 text-[10px]"></i> {cname} ({count_in_cat})</button>')
pills_str = "\n      ".join(cat_pills_html)

# Build Cards HTML
cards_html = []
for item in all_codes:
    cmd = item["command"]
    desc = item["desc"].replace('"', '&quot;')
    desc_plain = item["desc"].replace('"', '')
    gnum = f"{item['global_num']:03d}"
    snum = item["sub_num"]
    cname = item["cat_name"]
    cid = item["cat_id"]
    col = item["collection"]
    col_badge = item["collection_badge"]
    col_color = item["collection_badge_color"]
    icon_cls = item["icon"]

    search_blob = f"{cmd.lower()} {gnum} {snum} {cname.lower()} {desc_plain.lower()} {col} {item['collection_name'].lower()}"
    
    card = f'''
        <div class="code-card p-5 flex flex-col justify-between" data-category="{cid}" data-collection="{col}" data-search="{search_blob}">
          <div>
            <div class="flex items-center justify-between gap-2 mb-3">
              <span class="badge-category px-2.5 py-0.5 rounded-md text-[11px] font-bold font-mono tracking-wider flex items-center gap-1.5">
                <i class="fas {icon_cls} text-[10px] text-cyan-400"></i> #{gnum} • {cname}
              </span>
              <span class="px-2 py-0.5 rounded text-[9px] font-mono font-bold border {col_color}">
                {col_badge}
              </span>
            </div>
            <div class="flex items-center justify-between gap-2 mb-2">
              <h3 class="text-lg sm:text-xl font-bold font-mono text-cyan-300 tracking-wide break-all">
                {cmd}
              </h3>
              <button 
                type="button" 
                class="btn-copy px-2.5 py-1 rounded-lg text-xs font-bold inline-flex items-center gap-1.5 focus:outline-none flex-shrink-0"
                onclick="copyCode('{cmd}', this)"
                title="Copiar comando al portapapeles"
              >
                <i class="far fa-copy text-xs"></i> <span>Copiar</span>
              </button>
            </div>
            <p class="text-slate-300 text-xs sm:text-sm leading-relaxed mb-4">
              {item["desc"]}
            </p>
          </div>
          <div class="pt-3 border-t border-slate-800/80 mt-2">
            <div class="text-[11px] text-slate-400 font-mono flex items-center justify-between">
              <span class="truncate">Sintaxis: <span class="text-cyan-400">{cmd}</span> + sujeto + contexto</span>
              <button 
                type="button" 
                class="text-slate-400 hover:text-cyan-400 text-xs ml-2 p-1 flex-shrink-0"
                onclick="copyFullPrompt('{cmd} {desc}', this)"
                title="Copiar comando con descripción"
              >
                <i class="fas fa-magic text-[11px]"></i>
              </button>
            </div>
          </div>
        </div>'''
    cards_html.append(card)

cards_str = "\n".join(cards_html)

# Reels List Data
reels_data = [
    {
        "id": "reel-spiderman",
        "title": "Efecto Spiderman 'The Swing' con IA",
        "desc": "Desglose técnico de la escena de salto y vuelo acrobático en NYC usando ChatGPT para fisonomía y Seedance 2.0 para directiva de cámara.",
        "url": "https://www.instagram.com/p/DdsN1nasM46/",
        "tag": "🔥 REEL DESTACADO",
        "tag_color": "border-red-500/50 bg-red-950/70 text-red-400",
        "views": "Viral Instagram",
        "image": "/static/reel_spiderman_thumb.jpg",
        "has_pdf": False,
        "cta_label": "Ver Prompts Traducidos",
        "cta_icon": "fas fa-code",
        "cta_action": "openSpidermanModal()"
    },
    {
        "id": "reel-450k",
        "title": "Reel Viral: Dominio Visual con IA (+450K Vistas)",
        "desc": "El video que superó 450,000 reproducciones explicando cómo dirigir la IA visual como un director de cine en Hollywood.",
        "url": "https://www.instagram.com/p/DdFicUWgz7g/?hl=es-la",
        "tag": "🚀 +450K VISTAS",
        "tag_color": "border-amber-500/50 bg-amber-950/70 text-amber-300",
        "views": "450K Reproducciones",
        "image": "/static/reel_director_thumb.jpg",
        "has_pdf": True,
        "cta_label": "Descargar PDF 1 (3.7 MB)",
        "cta_icon": "far fa-file-pdf",
        "cta_action": "window.open('/static/codigos/ChatGPT_Codigos_Creativos_ProsperIA_ES.pdf', '_blank')"
    },
    {
        "id": "reel-editorial",
        "title": "Códigos Creativos: Edición Editorial Edward Jiménez",
        "desc": "Presentación de la guía de 12 páginas con notas de composición, iluminación de moda y dirección fotográfica.",
        "url": "https://www.instagram.com/p/Ddm_dbggYny/?hl=es-la",
        "tag": "📘 GUÍA EDITORIAL",
        "tag_color": "border-indigo-500/50 bg-indigo-950/70 text-indigo-300",
        "views": "+25K Vistas",
        "image": "/static/reel_editorial_thumb.jpg",
        "has_pdf": True,
        "cta_label": "Descargar PDF 2 (5.3 MB)",
        "cta_icon": "far fa-file-pdf",
        "cta_action": "window.open('/static/codigos/Codigos_Creativos_ChatGPT_Edward_Jimenez_ES_ProsperIA.pdf', '_blank')"
    },
    {
        "id": "reel-prosperia",
        "title": "100 Códigos Creativos de ChatGPT (Edición Dark)",
        "desc": "Guía rápida de referencia visual para creadores y marcas. 10 categorías organizadas de la 001 a la 100 con sintaxis directa.",
        "url": "https://www.instagram.com/p/DdkenvJMKLb/?hl=es-la",
        "tag": "⚡ GUÍA RÁPIDA",
        "tag_color": "border-cyan-500/50 bg-cyan-950/70 text-cyan-300",
        "views": "+20K Vistas",
        "image": "/static/reel_dark_thumb.jpg",
        "has_pdf": True,
        "cta_label": "Descargar PDF 1 (3.7 MB)",
        "cta_icon": "far fa-file-pdf",
        "cta_action": "window.open('/static/codigos/ChatGPT_Codigos_Creativos_ProsperIA_ES.pdf', '_blank')"
    },
    {
        "id": "reel-camaras",
        "title": "Ángulos de Cámara Cinematográfica con IA",
        "desc": "Cómo usar comandos como /birdsview, /POV y /dutchangle para romper la monotonía visual y disparar la retención.",
        "url": "https://www.instagram.com/p/DdutzI8gUXj/",
        "tag": "🎥 DIRECCIÓN VISUAL",
        "tag_color": "border-purple-500/50 bg-purple-950/70 text-purple-300",
        "views": "Instagram",
        "image": "/static/reel_camera_thumb.jpg",
        "has_pdf": False,
        "cta_label": "Ver Códigos de Cámara",
        "cta_icon": "fas fa-video",
        "cta_action": "filterCategory('05', document.querySelector('[data-cat=\"05\"]'))"
    },
    {
        "id": "reel-producto",
        "title": "Fotografía de Producto & Packshot Publicitario",
        "desc": "Domina la presentación visual para marcas de lujo, e-commerce y anuncios con iluminación de estudio controlada.",
        "url": "https://www.instagram.com/p/Dd2cQPos2PV/?hl=es-la",
        "tag": "💎 PRODUCTO",
        "tag_color": "border-emerald-500/50 bg-emerald-950/70 text-emerald-300",
        "views": "Instagram",
        "image": "/static/reel_product_thumb.jpg",
        "has_pdf": False,
        "cta_label": "Ver Códigos de Producto",
        "cta_icon": "fas fa-box-open",
        "cta_action": "filterCategory('10', document.querySelector('[data-cat=\"10\"]'))"
    }
]

reels_cards_html = []
for r in reels_data:
    cta_btn_html = f'''
        <button onclick="{r['cta_action']}" class="flex-1 inline-flex items-center justify-center gap-1.5 px-3 py-2.5 rounded-xl text-xs font-bold bg-cyan-400 text-slate-950 hover:bg-cyan-300 transition-all shadow-[0_0_10px_rgba(0,229,255,0.2)]">
          <i class="{r['cta_icon']}"></i> {r['cta_label']}
        </button>'''

    r_card = f'''
    <div class="glass-panel rounded-2xl overflow-hidden flex flex-col justify-between border-slate-800 hover:border-cyan-500/40 transition-all group p-5">
      <div>
        <div class="relative w-full h-48 rounded-xl overflow-hidden mb-4 bg-slate-950 border border-slate-800/80">
          <img src="{r['image']}" alt="{r['title']}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" loading="lazy" onerror="this.src='/static/reel_director_thumb.jpg'">
          <div class="absolute inset-0 bg-gradient-to-t from-slate-950 via-transparent to-black/30"></div>
          <div class="absolute top-2.5 left-2.5">
            <span class="px-2.5 py-1 rounded-md text-[10px] font-extrabold uppercase tracking-wider border {r['tag_color']} backdrop-blur-md">
              {r['tag']}
            </span>
          </div>
          <div class="absolute bottom-2.5 right-2.5 text-[11px] text-slate-200 font-mono bg-black/70 px-2 py-0.5 rounded-md backdrop-blur-sm border border-white/10">
            <i class="fab fa-instagram text-pink-400 mr-1"></i> {r['views']}
          </div>
        </div>
        <h3 class="text-base sm:text-lg font-bold text-white mb-2 leading-snug group-hover:text-cyan-300 transition-colors">{r['title']}</h3>
        <p class="text-xs text-slate-400 leading-relaxed mb-5">{r['desc']}</p>
      </div>
      <div class="pt-4 border-t border-slate-800/80 flex flex-col sm:flex-row gap-2.5">
        <a href="{r['url']}" target="_blank" rel="noopener" class="flex-1 inline-flex items-center justify-center gap-1.5 px-3 py-2.5 rounded-xl text-xs font-semibold bg-slate-900 border border-slate-700 hover:border-pink-500/40 hover:text-white text-slate-300 transition-colors">
          <i class="fab fa-instagram text-pink-400"></i> Ver Reel en IG
        </a>
        {cta_btn_html}
      </div>
    </div>'''
    reels_cards_html.append(r_card)

reels_grid_str = "\n".join(reels_cards_html)

# Template using placeholders to avoid any f-string curly-brace escaping issues
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>200 Códigos Creativos de ChatGPT para Imágenes y Video | Regalo Instagram @edwardjimenezia & ProsperIA</title>
  <meta name="description" content="200 Códigos Creativos de IA de Edward Jiménez y Agencia ProsperIA: Prompts y Dirección Fotográfica, desglose de The Swing Prompts (Spiderman), 2 guías PDF oficiales y comunidad exclusiva.">
  <meta name="keywords" content="200 codigos chatgpt, prompts de imagenes, test nivel ia, edward jimenez, comunidad whatsapp prosperia, reel spiderman prompt, passportai, automatizacion comercial ia">
  <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
  <link rel="canonical" href="https://agenciaprosperia.com/codigos">
  <link rel="icon" type="image/png" href="__FAVICON__">

  <!-- Open Graph / Instagram / WhatsApp Preview -->
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://agenciaprosperia.com/codigos">
  <meta property="og:title" content="200 Códigos Creativos de ChatGPT — Regalo Exclusivo Instagram & ProsperIA">
  <meta property="og:description" content="200 Códigos Creativos de IA, Prompts de video viral Spiderman y guías PDF descargables oficiales.">
  <meta property="og:image" content="__LOGO__">

  <!-- Twitter -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="200 Códigos Creativos de ChatGPT | ProsperIA & @edwardjimenezia">
  <meta name="twitter:description" content="Arsenal visual con IA: 200 códigos interactivos, 2 guías PDF oficiales, prompt de video viral Spiderman y comunidad.">
  <meta name="twitter:image" content="__LOGO__">

  <link rel="stylesheet" href="/static/tw.css">
  <link rel="stylesheet" href="/static/fonts.css">
  <link rel="stylesheet" href="/static/fa.min.css">

  <style>
    body {
      background-color: #030712;
      color: #f8fafc;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      overflow-x: hidden;
    }
    .font-mono {
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
    }
    .font-heading {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      letter-spacing: -0.02em;
    }

    /* Futuristic glowing mesh background */
    .bg-grid-cyber {
      background-size: 40px 40px;
      background-image: 
        linear-gradient(to right, rgba(0, 229, 255, 0.04) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(0, 229, 255, 0.04) 1px, transparent 1px);
    }
    .mesh-gradient-1 {
      position: absolute;
      top: -100px;
      left: 50%;
      transform: translateX(-50%);
      width: 900px;
      height: 450px;
      background: radial-gradient(circle, rgba(0, 229, 255, 0.15) 0%, rgba(99, 102, 241, 0.12) 40%, rgba(3, 7, 18, 0) 70%);
      filter: blur(80px);
      pointer-events: none;
      z-index: 0;
    }

    /* Glassmorphism Cards */
    .glass-panel {
      background: rgba(11, 18, 35, 0.85);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid rgba(255, 255, 255, 0.08);
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .glass-panel:hover {
      border-color: rgba(0, 229, 255, 0.35);
      box-shadow: 0 10px 30px -10px rgba(0, 229, 255, 0.15);
    }

    .code-card {
      background: rgba(13, 22, 43, 0.9);
      border: 1px solid rgba(0, 229, 255, 0.15);
      border-radius: 16px;
      transition: all 0.25s ease;
      position: relative;
      overflow: hidden;
    }
    .code-card:hover {
      transform: translateY(-3px);
      border-color: rgba(0, 229, 255, 0.5);
      box-shadow: 0 12px 28px -8px rgba(0, 229, 255, 0.25);
    }

    /* Copy Button */
    .btn-copy {
      background: rgba(0, 229, 255, 0.12);
      color: #00e5ff;
      border: 1px solid rgba(0, 229, 255, 0.35);
      transition: all 0.2s ease;
      cursor: pointer;
    }
    .btn-copy:hover {
      background: #00e5ff;
      color: #020710;
      box-shadow: 0 0 15px rgba(0, 229, 255, 0.4);
    }
    .btn-copy.copied {
      background: #10b981 !important;
      color: #020710 !important;
      border-color: #10b981 !important;
      box-shadow: 0 0 15px rgba(16, 185, 129, 0.5) !important;
    }

    /* Filter Chips */
    .filter-chip {
      background: rgba(15, 23, 42, 0.8);
      border: 1px solid rgba(255, 255, 255, 0.1);
      color: #94a3b8;
      transition: all 0.2s ease;
      cursor: pointer;
    }
    .filter-chip:hover {
      border-color: rgba(0, 229, 255, 0.4);
      color: #f1f5f9;
    }
    .filter-chip.active {
      background: #00e5ff;
      color: #020710;
      font-weight: 700;
      border-color: #00e5ff;
      box-shadow: 0 0 15px rgba(0, 229, 255, 0.35);
    }

    /* Input search */
    .input-search {
      background: #060d1f !important;
      border: 1px solid rgba(0, 229, 255, 0.35) !important;
      color: #ffffff !important;
      transition: all 0.2s ease;
    }
    .input-search:focus {
      border-color: #00e5ff !important;
      box-shadow: 0 0 20px rgba(0, 229, 255, 0.3) !important;
      outline: none;
    }
    .input-search::placeholder {
      color: #64748b !important;
    }

    /* Category Badges */
    .badge-category {
      background: rgba(0, 229, 255, 0.1);
      color: #38bdf8;
      border: 1px solid rgba(0, 229, 255, 0.25);
    }

    /* Spiderman Accordion and Prompts */
    .prompt-box {
      background: #020617;
      border: 1px dashed rgba(239, 68, 68, 0.4);
      border-radius: 12px;
      padding: 14px;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 12px;
      line-height: 1.6;
      color: #fca5a5;
      white-space: pre-wrap;
      word-break: break-word;
    }
    .spiderman-header-grid {
      display: grid;
      grid-template-columns: auto 1fr auto;
      gap: 20px;
      align-items: center;
      padding-bottom: 20px;
      margin-bottom: 20px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }
    @media (max-width: 768px) {
      .spiderman-header-grid {
        grid-template-columns: 1fr;
        text-align: center;
        gap: 14px;
        justify-items: center;
      }
    }
    .spiderman-ig-btn {
      white-space: nowrap;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      padding: 10px 18px;
      border-radius: 12px;
      font-size: 13px;
      font-weight: 700;
      background: rgba(80, 7, 36, 0.7);
      border: 1px solid rgba(244, 63, 94, 0.4);
      color: #fda4af;
      text-decoration: none;
      transition: all 0.2s ease;
    }
    .spiderman-ig-btn:hover {
      background: rgba(136, 19, 55, 0.95);
      color: #ffffff;
      border-color: #f43f5e;
      box-shadow: 0 0 20px rgba(244, 63, 94, 0.4);
    }

    /* Search bar grid layout */
    .search-grid-layout {
      display: grid;
      grid-template-columns: 1fr;
      gap: 12px;
      align-items: center;
    }
    @media (min-width: 640px) {
      .search-grid-layout {
        grid-template-columns: 1fr auto;
      }
    }

    .search-counter-badge {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      padding: 12px 18px;
      background: rgba(15, 23, 42, 0.9);
      border: 1px solid rgba(0, 229, 255, 0.25);
      border-radius: 14px;
      font-family: ui-monospace, SFMono-Regular, monospace;
      font-size: 12px;
      color: #94a3b8;
      white-space: nowrap;
    }

    .search-input-field {
      width: 100% !important;
      padding: 14px 44px 14px 44px !important;
      font-size: 15px !important;
      border-radius: 14px !important;
      color: #ffffff !important;
      background-color: #060d1f !important;
      caret-color: #00e5ff !important;
    }

    /* PASSPORTAI SHOWCASE - COLOR AMARILLO / NARANJA ELEGANTE */
    .passportai-container {
      background: linear-gradient(145deg, rgba(28, 18, 5, 0.95) 0%, rgba(12, 8, 4, 0.98) 100%);
      border: 2px solid rgba(245, 158, 11, 0.45);
      border-radius: 28px;
      box-shadow: 0 0 55px rgba(245, 158, 11, 0.16), inset 0 1px 0 rgba(251, 191, 36, 0.15);
      position: relative;
      overflow: hidden;
      transition: all 0.3s ease;
    }
    .passportai-container:hover {
      border-color: rgba(245, 158, 11, 0.7);
      box-shadow: 0 0 70px rgba(245, 158, 11, 0.25), inset 0 1px 0 rgba(251, 191, 36, 0.2);
    }
    .passportai-layout {
      display: grid;
      grid-template-columns: 1fr;
      gap: 2rem;
      align-items: center;
    }
    @media (min-width: 1024px) {
      .passportai-layout {
        grid-template-columns: 1.15fr 0.85fr;
        gap: 2.5rem;
      }
    }
    .text-gradient-amber {
      background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 50%, #ea580c 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .btn-passport-cta {
      background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 50%, #ea580c 100%) !important;
      color: #020710 !important;
      font-weight: 900 !important;
      font-size: 14px !important;
      padding: 14px 26px !important;
      border-radius: 14px !important;
      display: inline-flex !important;
      align-items: center !important;
      justify-content: center !important;
      gap: 10px !important;
      box-shadow: 0 0 30px rgba(245, 158, 11, 0.45) !important;
      transition: all 0.25s ease !important;
      text-decoration: none !important;
      border: none !important;
      cursor: pointer !important;
    }
    .btn-passport-cta:hover {
      transform: translateY(-2px) scale(1.02) !important;
      box-shadow: 0 0 45px rgba(245, 158, 11, 0.7) !important;
      background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 50%, #f97316 100%) !important;
    }
    .btn-passport-secondary {
      background: rgba(20, 14, 6, 0.85) !important;
      color: #fde68a !important;
      font-weight: 600 !important;
      font-size: 13px !important;
      padding: 14px 20px !important;
      border-radius: 14px !important;
      border: 1px solid rgba(245, 158, 11, 0.3) !important;
      display: inline-flex !important;
      align-items: center !important;
      justify-content: center !important;
      gap: 8px !important;
      transition: all 0.2s ease !important;
      text-decoration: none !important;
    }
    .btn-passport-secondary:hover {
      background: rgba(35, 22, 8, 0.95) !important;
      border-color: rgba(245, 158, 11, 0.6) !important;
      color: #ffffff !important;
    }
    .passport-badge-gift {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 6px 14px;
      border-radius: 9999px;
      background: rgba(120, 53, 15, 0.4);
      border: 1px solid rgba(245, 158, 11, 0.5);
      color: #fde68a;
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    /* Real Screen Frame */
    .passport-real-screen-frame {
      border: 2px solid rgba(245, 158, 11, 0.35);
      border-radius: 20px;
      overflow: hidden;
      background: #020617;
      box-shadow: 0 20px 50px rgba(0, 0, 0, 0.8), 0 0 35px rgba(245, 158, 11, 0.15);
      transition: all 0.3s ease;
    }
    .passport-real-screen-frame:hover {
      border-color: rgba(245, 158, 11, 0.65);
      box-shadow: 0 25px 60px rgba(0, 0, 0, 0.9), 0 0 50px rgba(245, 158, 11, 0.25);
    }

    /* CARTA DE VENTAS - COLOR NARANJA ELEGANTE */
    .btn-opt1-cta {
      background: rgba(249, 115, 22, 0.12) !important;
      color: #fb923c !important;
      border: 1px solid rgba(249, 115, 22, 0.5) !important;
      font-weight: 700 !important;
      font-size: 13px !important;
      padding: 14px 20px !important;
      border-radius: 12px !important;
      display: flex !important;
      align-items: center !important;
      justify-content: center !important;
      gap: 8px !important;
      transition: all 0.2s ease !important;
      cursor: pointer !important;
      width: 100% !important;
    }
    .btn-opt1-cta:hover {
      background: #f97316 !important;
      color: #020710 !important;
      box-shadow: 0 0 25px rgba(249, 115, 22, 0.55) !important;
    }
    .btn-opt2-cta {
      background: linear-gradient(135deg, #f59e0b 0%, #ea580c 100%) !important;
      color: #020710 !important;
      border: none !important;
      font-weight: 800 !important;
      font-size: 13px !important;
      padding: 14px 20px !important;
      border-radius: 12px !important;
      display: flex !important;
      align-items: center !important;
      justify-content: center !important;
      gap: 8px !important;
      box-shadow: 0 0 25px rgba(234, 88, 12, 0.45) !important;
      transition: all 0.2s ease !important;
      cursor: pointer !important;
      width: 100% !important;
    }
    .btn-opt2-cta:hover {
      transform: translateY(-2px) !important;
      box-shadow: 0 0 40px rgba(234, 88, 12, 0.65) !important;
      background: linear-gradient(135deg, #fbbf24 0%, #f97316 100%) !important;
    }

    .btn-cotizacion-cta {
      background: linear-gradient(135deg, #f59e0b 0%, #ea580c 100%) !important;
      color: #020710 !important;
      font-weight: 900 !important;
      font-size: 15px !important;
      padding: 16px 28px !important;
      border-radius: 14px !important;
      display: flex !important;
      align-items: center !important;
      justify-content: center !important;
      gap: 10px !important;
      box-shadow: 0 0 30px rgba(245, 158, 11, 0.45) !important;
      transition: all 0.25s ease !important;
      border: none !important;
      cursor: pointer !important;
      width: 100% !important;
    }
    .btn-cotizacion-cta:hover {
      transform: translateY(-2px) scale(1.01) !important;
      box-shadow: 0 0 45px rgba(245, 158, 11, 0.7) !important;
      background: linear-gradient(135deg, #fbbf24 0%, #f97316 100%) !important;
      color: #020710 !important;
    }

    .tab-collection.active {
      background: linear-gradient(135deg, rgba(0, 229, 255, 0.25) 0%, rgba(99, 102, 241, 0.25) 100%) !important;
      border-color: #00e5ff !important;
      color: #ffffff !important;
      box-shadow: 0 0 20px rgba(0, 229, 255, 0.25) !important;
    }
  </style>
</head>
<body class="min-h-screen flex flex-col relative selection:bg-cyan-500 selection:text-slate-950">

  <!-- Glow effect and background grid -->
  <div class="fixed inset-0 bg-grid-cyber pointer-events-none z-0"></div>
  <div class="mesh-gradient-1"></div>

  <!-- ════════════════════════════════════════════════════
       MAIN NAVBAR (AGENCIA PROSPERIA BRANDING)
       ════════════════════════════════════════════════════ -->
  <nav class="site-nav sticky top-0 left-0 w-full z-40 transition-all duration-300 bg-slate-950/85 backdrop-blur-xl border-b border-slate-800/80">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16 sm:h-20">
        
        <!-- Logo -->
        <a href="/" class="flex items-center gap-3 group">
          <img src="__LOGO__" alt="AGENCIA PROSPERIA" class="h-9 sm:h-12 w-auto object-contain rounded-lg group-hover:scale-105 transition-transform">
        </a>

        <!-- Desktop Links -->
        <div class="hidden lg:flex items-center gap-1 xl:gap-2 text-sm">
          <a href="#codigos-grid" class="nav-link-item active px-3 py-1.5 rounded-lg text-slate-300 hover:text-white transition-colors">
            <i class="fas fa-terminal text-xs text-cyan-400"></i> <span>200 Códigos</span>
          </a>
          <a href="#descargas" class="nav-link-item px-3 py-1.5 rounded-lg text-slate-300 hover:text-white transition-colors">
            <i class="far fa-file-pdf text-xs text-red-400"></i> <span>Descargas PDF</span>
          </a>
          <a href="javascript:void(0)" onclick="openSpidermanModal()" class="nav-link-item px-3 py-1.5 rounded-lg text-slate-300 hover:text-white transition-colors">
            <i class="fas fa-spider text-xs text-red-400"></i> <span>Reel Spiderman</span>
          </a>
          <a href="#reels-gallery" class="nav-link-item px-3 py-1.5 rounded-lg text-slate-300 hover:text-white transition-colors">
            <i class="fab fa-instagram text-xs text-pink-400"></i> <span>Nuestros Reels</span>
          </a>
          <a href="#passportai-showcase" class="nav-link-item px-3 py-1.5 rounded-lg text-slate-300 hover:text-white transition-colors">
            <i class="fas fa-bolt text-xs text-amber-400"></i> <span>PassportAI</span>
          </a>
          <!-- Link to new dedicated diagnostic page in new tab -->
          <a href="/test-ia" target="_blank" rel="noopener" class="nav-link-item px-3 py-1.5 rounded-lg text-amber-300 hover:text-white transition-colors flex items-center gap-1.5">
            <i class="fas fa-brain text-xs text-amber-400"></i> <span>Diagnóstico IA</span>
            <span class="px-1.5 py-0.5 rounded text-[9px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">NUEVO</span>
          </a>
          <!-- Cotizar opens popup modal -->
          <a href="javascript:void(0)" onclick="openCotizacionModal('integral')" class="nav-link-item px-3 py-1.5 rounded-lg text-orange-300 hover:text-white transition-colors">
            <i class="fas fa-briefcase text-xs text-orange-400"></i> <span>Cotizar</span>
          </a>
        </div>

        <!-- Action CTAs -->
        <div class="flex items-center gap-2 sm:gap-3">
          <a href="https://chat.whatsapp.com/HIjs3Bytduy9ucOtn6jeKw?s=sh&p=a&ilr=4" target="_blank" rel="noopener" class="inline-flex items-center gap-1.5 px-3 py-1.5 sm:px-3.5 sm:py-2 rounded-xl text-xs font-bold bg-emerald-500 text-slate-950 hover:bg-emerald-400 transition-all shadow-[0_0_15px_rgba(16,185,129,0.3)]">
            <i class="fab fa-whatsapp text-sm"></i> <span>Comunidad VIP</span>
          </a>
          <button type="button" onclick="openCotizacionModal('integral')" class="hidden sm:inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-bold bg-gradient-to-r from-orange-400 to-amber-500 text-slate-950 hover:from-orange-300 hover:to-amber-400 transition-all shadow-[0_0_15px_rgba(249,115,22,0.3)] cursor-pointer">
            <i class="fas fa-file-invoice-dollar text-xs"></i> <span>Cotizar</span>
          </button>
          <!-- Mobile Hamburger Toggle Button -->
          <button type="button" id="mobile-menu-btn" onclick="toggleMobileMenu()" class="lg:hidden p-2 rounded-xl text-slate-300 hover:text-white bg-slate-900 border border-slate-700 focus:outline-none" aria-label="Abrir menú de navegación">
            <i class="fas fa-bars text-base" id="mobile-menu-icon"></i>
          </button>
        </div>

      </div>
    </div>

    <!-- Mobile Navigation Dropdown -->
    <div id="mobile-nav-panel" class="hidden lg:hidden bg-slate-950/98 border-t border-slate-800/80 px-4 py-3 space-y-1.5 backdrop-blur-2xl">
      <a href="#codigos-grid" onclick="closeMobileMenu()" class="flex items-center gap-2 px-3 py-2.5 rounded-xl text-sm font-semibold text-cyan-400 bg-cyan-950/40 border border-cyan-500/20">
        <i class="fas fa-terminal text-xs"></i> <span>200 Códigos Creativos</span>
      </a>
      <a href="#descargas" onclick="closeMobileMenu()" class="flex items-center gap-2 px-3 py-2.5 rounded-xl text-sm font-medium text-slate-300 hover:text-white hover:bg-slate-900">
        <i class="far fa-file-pdf text-xs text-red-400"></i> <span>Descargas PDF (2 Guías)</span>
      </a>
      <a href="javascript:void(0)" onclick="closeMobileMenu(); openSpidermanModal();" class="flex items-center gap-2 px-3 py-2.5 rounded-xl text-sm font-medium text-slate-300 hover:text-white hover:bg-slate-900">
        <i class="fas fa-spider text-xs text-red-400"></i> <span>Reel Spiderman ("The Swing")</span>
      </a>
      <a href="#reels-gallery" onclick="closeMobileMenu()" class="flex items-center gap-2 px-3 py-2.5 rounded-xl text-sm font-medium text-slate-300 hover:text-white hover:bg-slate-900">
        <i class="fab fa-instagram text-xs text-pink-400"></i> <span>Nuestros Reels Virales</span>
      </a>
      <a href="#passportai-showcase" onclick="closeMobileMenu()" class="flex items-center gap-2 px-3 py-2.5 rounded-xl text-sm font-medium text-slate-300 hover:text-white hover:bg-slate-900">
        <i class="fas fa-bolt text-xs text-amber-400"></i> <span>PassportAI (Multi-IA)</span>
      </a>
      <a href="/test-ia" target="_blank" rel="noopener" onclick="closeMobileMenu()" class="flex items-center gap-2 px-3 py-2.5 rounded-xl text-sm font-bold text-amber-300 bg-amber-950/30 border border-amber-500/30">
        <i class="fas fa-brain text-xs text-amber-400"></i> <span>Diagnóstico IA (Página Nueva)</span>
      </a>
      <a href="javascript:void(0)" onclick="closeMobileMenu(); openCotizacionModal('integral');" class="flex items-center gap-2 px-3 py-2.5 rounded-xl text-sm font-bold text-orange-400 bg-orange-950/30 border border-orange-500/20">
        <i class="fas fa-briefcase text-xs"></i> <span>Solicitar Cotización</span>
      </a>
    </div>
  </nav>

  <!-- ════════════════════════════════════════════════════
       HERO SECTION WITH VIRAL SOCIAL PROOF
       ════════════════════════════════════════════════════ -->
  <header class="relative pt-10 sm:pt-14 pb-8 sm:pb-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto z-10 text-center">
    
    <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-cyan-950/80 border border-cyan-400/30 text-cyan-300 text-xs sm:text-sm font-semibold mb-6 backdrop-blur-md shadow-[0_0_15px_rgba(0,229,255,0.15)]">
      🎁 Hub de Recursos Exclusivos para Seguidores de Instagram &amp; Facebook
    </div>

    <h1 class="text-3xl sm:text-5xl lg:text-6xl font-extrabold text-white tracking-tight leading-tight mb-5 sm:mb-6 max-w-4xl mx-auto">
      El Arsenal de <span class="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-sky-300 to-indigo-400">Inteligencia Artificial</span> para Crear Contenido y Escalar tu Negocio
    </h1>

    <p class="text-slate-300 text-sm sm:text-lg max-w-3xl mx-auto mb-8 leading-relaxed font-light">
      Bienvenido al centro oficial de recursos de <strong>Edward Jiménez</strong> y <strong>Agencia ProsperIA</strong>. Aquí tienes acceso inmediato a los prompts virales de Hollywood, los <strong>200 Códigos Creativos de IA</strong> listos para copiar, las 2 guías PDF oficiales y nuestra comunidad.
    </p>

    <!-- Social Proof Metrics Bar -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-2.5 sm:gap-4 max-w-4xl mx-auto mb-6">
      <div class="glass-panel p-3.5 sm:p-4 rounded-2xl text-center border-amber-500/20">
        <div class="text-xl sm:text-3xl font-extrabold text-amber-400 font-heading">+450,000</div>
        <div class="text-[11px] sm:text-xs text-slate-300 mt-1">Vistas en Reel Viral</div>
      </div>
      <div class="glass-panel p-3.5 sm:p-4 rounded-2xl text-center border-cyan-500/20">
        <div class="text-xl sm:text-3xl font-extrabold text-cyan-400 font-heading">10,000+</div>
        <div class="text-[11px] sm:text-xs text-slate-300 mt-1">Seguidores en ProsperIA FB</div>
      </div>
      <div class="glass-panel p-3.5 sm:p-4 rounded-2xl text-center border-pink-500/20">
        <div class="text-xl sm:text-3xl font-extrabold text-pink-400 font-heading">+2,000</div>
        <div class="text-[11px] sm:text-xs text-slate-300 mt-1">Comunidad @edwardjimenezia</div>
      </div>
      <div class="glass-panel p-3.5 sm:p-4 rounded-2xl text-center border-emerald-500/20">
        <div class="text-xl sm:text-3xl font-extrabold text-emerald-400 font-heading">200 Códigos</div>
        <div class="text-[11px] sm:text-xs text-slate-300 mt-1">Visuales 100% Gratuitos</div>
      </div>
    </div>

  </header>

  <!-- ════════════════════════════════════════════════════
       BLOQUE 1: 200 CÓDIGOS CREATIVOS DE IA
       ════════════════════════════════════════════════════ -->
  <main id="codigos-grid" class="py-10 sm:py-14 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto relative z-10 scroll-mt-24">
    <div class="text-center max-w-3xl mx-auto mb-6">
      <span class="text-xs font-bold uppercase tracking-wider text-cyan-400 mb-2 block">Catálogo Interactivo y Buscador</span>
      <h2 class="text-2xl sm:text-4xl font-extrabold text-white mb-3">
        Explora los 200 Códigos y Cópialos con 1 Clic
      </h2>
      <p class="text-slate-300 text-xs sm:text-sm leading-relaxed">
        Filtra por colección, categoría o efecto visual. Toca <strong>Copiar</strong> para pegarlo directamente en ChatGPT o Midjourney.
      </p>
    </div>

    <!-- Tabs de Selección de Colección (200 Códigos) -->
    <div class="flex items-center justify-center gap-2 sm:gap-3 mb-6 max-w-3xl mx-auto flex-wrap">
      <button 
        type="button" 
        class="tab-collection active px-4 py-2 sm:px-5 sm:py-2.5 rounded-xl text-xs sm:text-sm font-bold border border-cyan-500/40 bg-cyan-950/60 text-cyan-300 hover:border-cyan-400 transition-all cursor-pointer flex items-center gap-2"
        data-collection="all"
        onclick="filterCollection('all', this)"
      >
        <i class="fas fa-layer-group text-xs"></i> <span>Todos los Códigos (200)</span>
      </button>
      <button 
        type="button" 
        class="tab-collection px-4 py-2 sm:px-5 sm:py-2.5 rounded-xl text-xs sm:text-sm font-semibold border border-slate-700 bg-slate-900/80 text-slate-300 hover:border-cyan-400/50 hover:text-white transition-all cursor-pointer flex items-center gap-2"
        data-collection="col1"
        onclick="filterCollection('col1', this)"
      >
        <i class="far fa-file-alt text-cyan-400 text-xs"></i> <span>Colección 1: Prompts ChatGPT (100)</span>
      </button>
      <button 
        type="button" 
        class="tab-collection px-4 py-2 sm:px-5 sm:py-2.5 rounded-xl text-xs sm:text-sm font-semibold border border-slate-700 bg-slate-900/80 text-slate-300 hover:border-indigo-400/50 hover:text-white transition-all cursor-pointer flex items-center gap-2"
        data-collection="col2"
        onclick="filterCollection('col2', this)"
      >
        <i class="fas fa-camera-retro text-indigo-400 text-xs"></i> <span>Colección 2: Fotografía Edward Jiménez (100)</span>
      </button>
    </div>

    <!-- Live Search Bar -->
    <div class="glass-panel p-3.5 sm:p-5 rounded-2xl mb-6 max-w-5xl mx-auto border-cyan-500/20">
      <div class="search-grid-layout">
        <div class="relative w-full">
          <i class="fas fa-search absolute left-4 top-1/2 -translate-y-1/2 text-cyan-400 text-sm pointer-events-none"></i>
          <input 
            type="text" 
            id="search-input" 
            placeholder="Buscar entre los 200 códigos: /spotlight, 35mm..." 
            class="search-input-field input-search"
            oninput="handleSearch(this.value)"
          >
          <button id="clear-search" onclick="clearSearch()" class="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white text-xs hidden p-1">
            <i class="fas fa-times-circle text-base"></i>
          </button>
        </div>
        <div class="search-counter-badge">
          <span>Mostrando:</span>
          <strong id="visible-count" class="text-cyan-400 font-bold text-sm">200</strong>
          <span>de 200 códigos</span>
        </div>
      </div>
    </div>

    <!-- Category Pills -->
    <div class="flex items-center gap-1.5 sm:gap-2 mb-6 max-w-5xl mx-auto overflow-x-auto no-scrollbar pb-2 sm:flex-wrap sm:justify-center sm:overflow-visible" id="category-pills">
      __PILLS_STR__
    </div>

    <!-- REQUISITO 1: Botón de Desplegar Catálogo Completo (TOP: Abajo del Índice) -->
    <div class="text-center mb-8">
      <button id="btn-toggle-catalog-top" type="button" onclick="toggleCatalogExpansion()" class="inline-flex items-center gap-2 px-6 py-3 rounded-2xl font-bold text-xs sm:text-sm bg-gradient-to-r from-cyan-400 to-sky-400 text-slate-950 hover:from-cyan-300 hover:to-sky-300 transition-all shadow-[0_0_22px_rgba(0,229,255,0.35)] cursor-pointer">
        <i class="fas fa-chevron-down text-xs transition-transform duration-300 toggle-catalog-icon"></i>
        <span class="toggle-catalog-text">Desplegar Catálogo Completo (Ver los 200 Códigos)</span>
      </button>
    </div>

    <div id="no-results" class="hidden text-center py-16 px-4 glass-panel rounded-3xl max-w-lg mx-auto">
      <h3 class="text-lg font-bold text-white mb-2">No encontramos ningún código coincidente</h3>
      <p class="text-xs text-slate-400 mb-4">Intenta buscar otro término o limpia los filtros.</p>
      <button onclick="clearSearch()" class="px-5 py-2 rounded-xl text-xs font-bold bg-cyan-400 text-slate-950">
        Ver todos los 200 códigos
      </button>
    </div>

    <!-- Cards Collapsible Wrapper -->
    <div id="cards-wrapper" style="max-height: 740px; overflow: hidden;" class="relative transition-all duration-500">
      <div id="cards-container" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5">
__CARDS_STR__
      </div>
      <div id="cards-fade-overlay" class="absolute bottom-0 left-0 right-0 h-48 bg-gradient-to-t from-slate-950 via-slate-950/95 to-transparent pointer-events-none flex items-end justify-center pb-4">
      </div>
    </div>

    <!-- REQUISITO 1: Botón de Desplegar Catálogo Completo (BOTTOM: Abajo donde acaba) -->
    <div class="text-center mt-6">
      <button id="btn-toggle-catalog-bottom" type="button" onclick="toggleCatalogExpansion()" class="inline-flex items-center gap-2 px-6 py-3.5 rounded-2xl font-bold text-xs sm:text-sm bg-gradient-to-r from-cyan-400 to-sky-400 text-slate-950 hover:from-cyan-300 hover:to-sky-300 transition-all shadow-[0_0_25px_rgba(0,229,255,0.35)] cursor-pointer">
        <i class="fas fa-chevron-down text-xs transition-transform duration-300 toggle-catalog-icon"></i>
        <span class="toggle-catalog-text">Desplegar Catálogo Completo (Ver los 200 Códigos)</span>
      </button>
      <p class="text-xs text-slate-400 mt-2">
        O utiliza el buscador o categorías arriba para ver resultados instantáneos.
      </p>
    </div>
  </main>

  <!-- ════════════════════════════════════════════════════
       BLOQUE 2: DESCARGAS OFICIALES DE LOS 2 PDFs
       ════════════════════════════════════════════════════ -->
  <section id="descargas" class="py-12 sm:py-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto relative z-10 scroll-mt-24">
    
    <div class="text-center mb-8">
      <span class="text-xs font-bold uppercase tracking-wider text-cyan-400 mb-2 block">Documentos Oficiales en PDF</span>
      <h2 class="text-2xl sm:text-3xl font-extrabold text-white">Descarga las 2 Colecciones Completas (200 Códigos)</h2>
      <p class="text-slate-300 text-xs sm:text-sm max-w-2xl mx-auto mt-2 mb-4 leading-relaxed">
        Tienes a tu disposición dos guías complementarias de alta resolución: la <strong>Colección 1</strong> enfocada en prompts y comandos de texto para ChatGPT, y la <strong>Colección 2</strong> enfocada en dirección visual y generación de imágenes profesionales por Edward Jiménez.
      </p>

      <!-- Google Drive Alternative -->
      <div class="inline-block">
        <a href="https://drive.google.com/drive/folders/1tMekHUIAkG7-OLcorPOaz2wI2HOLWhrV?usp=sharing" target="_blank" rel="noopener" class="inline-flex items-center gap-2 text-xs sm:text-sm text-slate-400 hover:text-cyan-400 transition-colors py-2 px-4 rounded-xl bg-slate-900/60 border border-slate-800">
          <i class="fab fa-google-drive text-amber-400"></i> ¿Prefieres guardarlos en tu Drive? <strong>Abrir Carpeta en Google Drive</strong> <i class="fas fa-external-link-alt text-[10px]"></i>
        </a>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-5xl mx-auto">
      
      <!-- Card 1: Edición Guía Visual ProsperIA ES -->
      <div class="glass-panel p-6 sm:p-8 rounded-2xl relative overflow-hidden flex flex-col justify-between border-cyan-500/20 shadow-xl">
        <div>
          <div class="flex items-center justify-between mb-4">
            <span class="px-3 py-1 rounded-full text-xs font-bold bg-cyan-950 text-cyan-300 border border-cyan-500/30">
              <i class="far fa-file-pdf mr-1 text-red-400"></i> COLECCIÓN 1 · PROMPTS CHATGPT
            </span>
            <span class="text-xs text-slate-400 font-mono">3.7 MB • 12 PÁGINAS</span>
          </div>

          <h3 class="text-xl font-bold text-white mb-2">100 Códigos Creativos de ChatGPT (Guía Dark)</h3>
          <p class="text-xs sm:text-sm text-slate-300 leading-relaxed mb-6">
            La edición oficial para aprender a comunicarte con ChatGPT y DALL-E en lenguaje cinematográfico. Desglosada en 10 categorías temáticas con ejemplos listos para copiar.
          </p>

          <ul class="space-y-2 text-xs text-slate-300 mb-6">
            <li class="flex items-center gap-2"><i class="fas fa-check text-cyan-400"></i> 100 prompts y comandos verificados</li>
            <li class="flex items-center gap-2"><i class="fas fa-check text-cyan-400"></i> 10 categorías de composición e iluminación</li>
            <li class="flex items-center gap-2"><i class="fas fa-check text-cyan-400"></i> Alta resolución lista para imprimir o leer en tablet</li>
          </ul>
        </div>

        <div class="pt-4 border-t border-slate-800/80 flex flex-col sm:flex-row gap-3">
          <a 
            href="/static/codigos/ChatGPT_Codigos_Creativos_ProsperIA_ES.pdf" 
            target="_blank" 
            download="ChatGPT_Codigos_Creativos_ProsperIA_ES.pdf"
            class="flex-1 inline-flex items-center justify-center gap-2 px-4 py-3 rounded-xl font-bold text-xs sm:text-sm bg-gradient-to-r from-cyan-400 to-sky-400 text-slate-950 hover:from-cyan-300 hover:to-sky-300 transition-all shadow-[0_0_15px_rgba(0,229,255,0.3)]"
          >
            <i class="fas fa-download"></i> Descargar PDF 1 Gratis
          </a>
          <a 
            href="/static/codigos/ChatGPT_Codigos_Creativos_ProsperIA_ES.pdf" 
            target="_blank" 
            rel="noopener"
            class="inline-flex items-center justify-center gap-2 px-4 py-3 rounded-xl font-semibold text-xs text-slate-300 bg-slate-900 border border-slate-700 hover:border-cyan-400/50 hover:text-white transition-colors"
          >
            <i class="fas fa-eye"></i> Previsualizar
          </a>
        </div>
      </div>

      <!-- Card 2: Edición Editorial Edward Jiménez -->
      <div class="glass-panel p-6 sm:p-8 rounded-2xl relative overflow-hidden flex flex-col justify-between border-indigo-500/20 shadow-xl">
        <div>
          <div class="flex items-center justify-between mb-4">
            <span class="px-3 py-1 rounded-full text-xs font-bold bg-indigo-950 text-indigo-300 border border-indigo-500/30">
              <i class="far fa-file-pdf mr-1 text-red-400"></i> COLECCIÓN 2 · FOTOGRAFÍA PROFESIONAL
            </span>
            <span class="text-xs text-slate-400 font-mono">5.3 MB • 12 PÁGINAS</span>
          </div>

          <h3 class="text-xl font-bold text-white mb-2">Edición Editorial Fotográfica Edward Jiménez</h3>
          <p class="text-xs sm:text-sm text-slate-300 leading-relaxed mb-6">
            Guía de dirección de arte y fotografía avanzada con IA. Escrita por Edward Jiménez para creadores y marcas que buscan estética de revista de moda, cine y publicidad.
          </p>

          <ul class="space-y-2 text-xs text-slate-300 mb-6">
            <li class="flex items-center gap-2"><i class="fas fa-check text-indigo-400"></i> 100 comandos fotográficos adicionales (001 a 100)</li>
            <li class="flex items-center gap-2"><i class="fas fa-check text-indigo-400"></i> Estética editorial, planos holandeses y packshots</li>
            <li class="flex items-center gap-2"><i class="fas fa-check text-indigo-400"></i> Notas del autor sobre dirección visual de Hollywood</li>
          </ul>
        </div>

        <div class="pt-4 border-t border-slate-800/80 flex flex-col sm:flex-row gap-3">
          <a 
            href="/static/codigos/Codigos_Creativos_ChatGPT_Edward_Jimenez_ES_ProsperIA.pdf" 
            target="_blank" 
            download="Codigos_Creativos_ChatGPT_Edward_Jimenez_ES_ProsperIA.pdf"
            class="flex-1 inline-flex items-center justify-center gap-2 px-4 py-3 rounded-xl font-bold text-xs sm:text-sm bg-gradient-to-r from-indigo-500 to-purple-500 text-white hover:from-indigo-400 hover:to-purple-400 transition-all shadow-[0_0_15px_rgba(99,102,241,0.3)]"
          >
            <i class="fas fa-download"></i> Descargar PDF 2 Gratis
          </a>
          <a 
            href="/static/codigos/Codigos_Creativos_ChatGPT_Edward_Jimenez_ES_ProsperIA.pdf" 
            target="_blank" 
            rel="noopener"
            class="inline-flex items-center justify-center gap-2 px-4 py-3 rounded-xl font-semibold text-xs text-slate-300 bg-slate-900 border border-slate-700 hover:border-indigo-400/50 hover:text-white transition-colors"
          >
            <i class="fas fa-eye"></i> Previsualizar
          </a>
        </div>
      </div>

    </div>

  </section>

  <!-- ════════════════════════════════════════════════════
       BLOQUE 4: NUESTROS REELS PUBLICADOS Y RECURSOS PROMETIDOS
       ════════════════════════════════════════════════════ -->
  <section id="reels-gallery" class="py-12 sm:py-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto relative z-10 scroll-mt-24">
    <div class="text-center max-w-3xl mx-auto mb-10">
      <span class="text-xs font-bold uppercase tracking-wider text-pink-400 mb-2 block">Casos Reales y Contenido en Redes</span>
      <h2 class="text-2xl sm:text-4xl font-extrabold text-white mb-3">
        Nuestros Reels Virales y sus Recursos Prometidos
      </h2>
      <p class="text-slate-300 text-xs sm:text-sm leading-relaxed">
        ¿Llegaste desde un video específico de Edward Jiménez o ProsperIA? Aquí tienes cada Reel con su botón directo para descargar el material o abrir los prompts traducidos.
      </p>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
__REELS_GRID_STR__
    </div>
  </section>

  <!-- ════════════════════════════════════════════════════
       BLOQUE 5: PASSPORTAI (COLOR AMARILLO / NARANJA ELEGANTE + PANTALLA REAL)
       ════════════════════════════════════════════════════ -->
  <section id="passportai-showcase" class="py-12 sm:py-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto relative z-10 scroll-mt-24">
    <div class="passportai-container p-6 sm:p-10 lg:p-12">
      
      <div class="passportai-layout">
        <div>
          <div class="mb-4">
            <span class="passport-badge-gift">
              <i class="fas fa-gift text-amber-400"></i> Tokens de Cortesía + 5 Días Gratis
            </span>
          </div>

          <h2 class="text-2xl sm:text-4xl lg:text-5xl font-extrabold text-white tracking-tight leading-tight mb-4">
            ¿Quieres probar YA mismo todo este conocimiento? Entra a <span class="text-gradient-amber">PassportAI</span>
          </h2>

          <p class="text-slate-300 text-sm sm:text-base leading-relaxed mb-6 font-light">
            No pierdas tiempo saltando entre 5 pestañas ni pagando suscripciones separadas. <strong>PassportAI</strong> es la plataforma unificada que integra los mejores modelos de Inteligencia Artificial del mundo en una <strong>sola interfaz gráfica intuitiva y sin fricción</strong>.
          </p>

          <div class="space-y-3 mb-8">
            <div class="flex items-start gap-3 p-3 rounded-xl bg-amber-950/20 border border-amber-500/20">
              <div class="w-8 h-8 rounded-lg bg-amber-950 border border-amber-400/40 text-amber-400 flex items-center justify-center flex-shrink-0 text-sm">
                <i class="fas fa-layer-group"></i>
              </div>
              <div>
                <h4 class="text-sm font-bold text-white">Estudio Creativo Multimodal &amp; Modelos Líderes</h4>
                <p class="text-xs text-slate-400 mt-0.5">Alterna al instante entre ChatGPT (GPT-4o), Claude 3.5 Sonnet, Gemini 1.5 Pro, Flux, Runway y generadores de voz y video en un único canvas.</p>
              </div>
            </div>

            <div class="flex items-start gap-3 p-3 rounded-xl bg-amber-950/20 border border-amber-500/20">
              <div class="w-8 h-8 rounded-lg bg-orange-950 border border-orange-400/40 text-orange-400 flex items-center justify-center flex-shrink-0 text-sm">
                <i class="fas fa-bolt"></i>
              </div>
              <div>
                <h4 class="text-sm font-bold text-white">Aplica los 200 Códigos Directamente</h4>
                <p class="text-xs text-slate-400 mt-0.5">Copia y pega cualquiera de nuestros 200 códigos en su canvas visual para crear contenido viral, guiones y dirección de arte en segundos.</p>
              </div>
            </div>

            <div class="flex items-start gap-3 p-3 rounded-xl bg-amber-950/20 border border-amber-500/20">
              <div class="w-8 h-8 rounded-lg bg-yellow-950 border border-yellow-400/40 text-yellow-400 flex items-center justify-center flex-shrink-0 text-sm">
                <i class="fas fa-coins"></i>
              </div>
              <div>
                <h4 class="text-sm font-bold text-white">Suite de Negocio B2B + Tokens Gratis</h4>
                <p class="text-xs text-slate-400 mt-0.5">Incluye PassportAI Leads, Business Constructor y Radar de Audiencia. Pruébalo durante 5 días con saldo precargado.</p>
              </div>
            </div>
          </div>

          <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
            <a href="https://passportai.app" target="_blank" rel="noopener" class="btn-passport-cta">
              <span>Probar PassportAI Gratis</span>
              <i class="fas fa-arrow-right"></i>
            </a>
            <a href="https://passportai.app" target="_blank" rel="noopener" class="btn-passport-secondary">
              <i class="fas fa-desktop"></i>
              <span>Ver Interfaz en passportai.app</span>
            </a>
          </div>
        </div>

        <div>
          <!-- REQUISITO 3: Captura Real de Pantalla de PassportAI -->
          <div class="passport-real-screen-frame">
            <div class="flex items-center justify-between px-4 py-2.5 bg-slate-900/90 border-b border-amber-500/20">
              <div class="flex items-center gap-2">
                <span class="w-2.5 h-2.5 rounded-full bg-red-500 inline-block"></span>
                <span class="w-2.5 h-2.5 rounded-full bg-amber-500 inline-block"></span>
                <span class="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block"></span>
                <span class="text-[11px] font-mono text-slate-400 ml-2">passportai.app/dashboard</span>
              </div>
              <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-950 text-amber-300 border border-amber-500/30">
                PANTALLA REAL EN VIVO
              </span>
            </div>
            <div class="relative bg-slate-950 p-2 overflow-hidden group">
              <img src="__PASSPORTAI_IMG__" alt="Pantalla Real de PassportAI Dashboard" class="w-full h-auto rounded-xl shadow-2xl border border-amber-500/20 group-hover:scale-[1.02] transition-transform duration-300" loading="lazy">
              <div class="absolute bottom-4 left-4 right-4 bg-slate-950/90 backdrop-blur-md p-3 rounded-xl border border-amber-500/30 text-xs text-slate-300 flex items-center justify-between">
                <span class="flex items-center gap-1.5 text-amber-300 font-semibold text-[11px]">
                  <i class="fas fa-check-circle text-amber-400"></i> Estudio Creativo + Suite B2B Unificada
                </span>
                <a href="https://passportai.app" target="_blank" rel="noopener" class="text-[11px] text-amber-400 font-bold hover:underline">
                  Abrir App <i class="fas fa-external-link-alt text-[9px]"></i>
                </a>
              </div>
            </div>
            <div class="text-center py-2 bg-slate-950/80 border-t border-slate-900">
              <span class="text-[11px] text-slate-400">
                <i class="fas fa-shield-alt text-amber-400 mr-1"></i> Sin tarjetas de crédito para probar los 5 días
              </span>
            </div>
          </div>
        </div>
      </div>

    </div>
  </section>

  <!-- ════════════════════════════════════════════════════
       BLOQUE 7: CARTA DE VENTAS (COLOR NARANJA ELEGANTE)
       ════════════════════════════════════════════════════ -->
  <section id="carta-ventas" class="py-12 sm:py-20 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto relative z-10 scroll-mt-24">
    
    <div class="glass-panel p-6 sm:p-12 lg:p-14 rounded-3xl border-2 border-orange-500/35 relative overflow-hidden bg-gradient-to-b from-slate-950 via-[#1a0c02] to-slate-950 shadow-[0_0_60px_rgba(249,115,22,0.14)]">
      <div class="absolute -top-32 -right-32 w-80 h-80 bg-orange-500/10 rounded-full blur-3xl pointer-events-none"></div>

      <div class="max-w-3xl mx-auto text-center mb-10 sm:mb-14">
        <span class="px-3.5 py-1 rounded-full text-xs font-bold bg-orange-950 text-orange-300 border border-orange-500/40 uppercase tracking-wider mb-4 inline-block">
          <i class="fas fa-handshake mr-1"></i> Dos Formas de Crecer con Nosotros
        </span>
        <h2 class="text-2xl sm:text-4xl font-extrabold text-white mb-4">
          Puedes Aprender Solo con Todos Estos Ejemplos...<br>
          <span class="text-transparent bg-clip-text bg-gradient-to-r from-amber-400 via-orange-400 to-amber-500">
            O Dejar que la Agencia ProsperIA lo Haga por Ti.
          </span>
        </h2>
        <p class="text-slate-300 text-xs sm:text-base leading-relaxed">
          Ya viste que nuestros videos superan <strong>+450K reproducciones</strong> y atraen miles de prospectos calificados cada mes. Si tienes el tiempo de experimentar y montar los sistemas tú mismo, aprovecha todo nuestro material gratuito. Pero si eres dueño de empresa y buscas velocidad de ejecución, ponemos a tu disposición nuestras dos modalidades de servicio:
        </p>
      </div>

      <!-- 2 Quotation Cards Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 sm:gap-8 max-w-5xl mx-auto mb-10">
        
        <!-- Cuadro 1: Creación de Contenido Viral -->
        <div class="p-6 sm:p-8 rounded-3xl bg-slate-950/80 border-2 border-orange-500/30 hover:border-orange-400 transition-all flex flex-col justify-between relative shadow-xl">
          <div class="absolute top-0 right-0 transform translate-x-1 sm:translate-x-2 -translate-y-2">
            <span class="px-3 py-1 rounded-full text-[10px] font-extrabold uppercase tracking-wider bg-orange-500 text-slate-950 shadow">
              OPCIÓN 1
            </span>
          </div>

          <div>
            <div class="w-12 h-12 rounded-2xl bg-orange-950 border border-orange-400/40 text-orange-400 flex items-center justify-center text-xl mb-4">
              <i class="fas fa-video"></i>
            </div>
            <h3 class="text-xl font-bold text-white mb-2">Hacemos Este Mismo Contenido para Tu Negocio</h3>
            <p class="text-xs sm:text-sm text-slate-300 leading-relaxed mb-6">
              Producción integral de Reels y videos cortos con IA diseñados para detener el scroll, posicionar tu marca como referente de autoridad y disparar tu alcance orgánico.
            </p>

            <ul class="space-y-3 text-xs sm:text-sm text-slate-300 mb-8">
              <li class="flex items-start gap-2.5">
                <i class="fas fa-check-circle text-orange-400 mt-1"></i>
                <span><strong>Guiones de Alta Retención:</strong> Ganchos psicológicos probados en los primeros 3 segundos.</span>
              </li>
              <li class="flex items-start gap-2.5">
                <i class="fas fa-check-circle text-orange-400 mt-1"></i>
                <span><strong>Generación Visual con IA:</strong> Prompts de Hollywood, efectos visuales tipo Spiderman y dirección de arte.</span>
              </li>
              <li class="flex items-start gap-2.5">
                <i class="fas fa-check-circle text-orange-400 mt-1"></i>
                <span><strong>Edición Cinematográfica 9:16:</strong> Subtítulos cinéticos, música y sonido de estudio listos para publicar.</span>
              </li>
              <li class="flex items-start gap-2.5">
                <i class="fas fa-check-circle text-orange-400 mt-1"></i>
                <span><strong>Llamados a la Acción Estratégicos:</strong> Transformamos vistas en seguidores y mensajes directos.</span>
              </li>
            </ul>
          </div>

          <button type="button" onclick="openCotizacionModal('contenido')" class="btn-opt1-cta">
            <i class="fas fa-paper-plane"></i> Solicitar Cotización Opción 1
          </button>
        </div>

        <!-- Cuadro 2: Administración Integral 360° -->
        <div class="p-6 sm:p-8 rounded-3xl bg-slate-950/80 border-2 border-amber-500/40 hover:border-amber-400 transition-all flex flex-col justify-between relative shadow-xl">
          <div class="absolute top-0 right-0 transform translate-x-1 sm:translate-x-2 -translate-y-2">
            <span class="px-3 py-1 rounded-full text-[10px] font-extrabold uppercase tracking-wider bg-gradient-to-r from-amber-400 to-orange-500 text-slate-950 font-black shadow">
              OPCIÓN 2 · RECOMENDADO
            </span>
          </div>

          <div>
            <div class="w-12 h-12 rounded-2xl bg-amber-950 border border-amber-400/40 text-amber-400 flex items-center justify-center text-xl mb-4">
              <i class="fas fa-chart-line"></i>
            </div>
            <h3 class="text-xl font-bold text-white mb-2">Administración Integral 360° (Contenido + Tráfico + CRM)</h3>
            <p class="text-xs sm:text-sm text-slate-300 leading-relaxed mb-6">
              Nos convertimos en el brazo de crecimiento y adquisición de tu empresa: desde la producción audiovisual hasta el cierre comercial de clientes en WhatsApp.
            </p>

            <ul class="space-y-3 text-xs sm:text-sm text-slate-300 mb-8">
              <li class="flex items-start gap-2.5">
                <i class="fas fa-check-circle text-amber-400 mt-1"></i>
                <span><strong>Administración &amp; Publicación:</strong> Gestión de tus canales (Instagram, Facebook, YouTube, LinkedIn).</span>
              </li>
              <li class="flex items-start gap-2.5">
                <i class="fas fa-check-circle text-amber-400 mt-1"></i>
                <span><strong>Campañas de Tráfico Pago:</strong> Anuncios en Meta Ads y Google Ads para escalar las vistas virales a prospectos.</span>
              </li>
              <li class="flex items-start gap-2.5">
                <i class="fas fa-check-circle text-amber-400 mt-1"></i>
                <span><strong>Infraestructura CRM &amp; WhatsApp:</strong> Automatización para responder en segundos y agendar citas.</span>
              </li>
              <li class="flex items-start gap-2.5">
                <i class="fas fa-check-circle text-amber-400 mt-1"></i>
                <span><strong>Acompañamiento Estratégico:</strong> Asesoría y dirección directa para optimizar tu embudo comercial.</span>
              </li>
            </ul>
          </div>

          <button type="button" onclick="openCotizacionModal('integral')" class="btn-opt2-cta">
            <i class="fas fa-rocket"></i> Solicitar Cotización Opción 2
          </button>
        </div>

      </div>

      <!-- Quick WhatsApp banner -->
      <div class="text-center pt-2 pb-6">
        <a href="https://wa.me/17865573119?text=Hola,%20quiero%20solicitar%20una%20cotizaci%C3%B3n%20para%20mi%20empresa" target="_blank" rel="noopener" class="inline-flex items-center gap-2 text-xs sm:text-sm text-emerald-400 hover:text-emerald-300 transition-colors py-2 px-4 rounded-xl bg-emerald-950/40 border border-emerald-500/30">
          <i class="fab fa-whatsapp text-emerald-400"></i> ¿Quieres respuesta inmediata en 1 clic? <strong>Chatear directamente por WhatsApp con el equipo</strong> <i class="fas fa-arrow-right text-xs"></i>
        </a>
      </div>

      <!-- WhatsApp Community Card -->
      <div class="p-6 sm:p-8 rounded-2xl bg-gradient-to-r from-emerald-950/80 via-slate-950 to-slate-950 border border-emerald-500/40 flex flex-col md:flex-row items-center justify-between gap-6 max-w-5xl mx-auto">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 sm:w-14 sm:h-14 rounded-2xl bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 text-xl sm:text-2xl flex-shrink-0">
            <i class="fab fa-whatsapp"></i>
          </div>
          <div>
            <span class="text-xs font-bold text-emerald-400 uppercase tracking-wider block mb-0.5">Comunidad Oficial y Networking</span>
            <h4 class="text-base sm:text-xl font-bold text-white">¿Quieres hacer preguntas y aprender con otros creadores?</h4>
            <p class="text-xs text-slate-300 mt-0.5">Únete a nuestro grupo oficial de WhatsApp donde compartimos prompts, novedades y sesiones en vivo.</p>
          </div>
        </div>
        <div class="flex-shrink-0 w-full md:w-auto">
          <a href="https://chat.whatsapp.com/HIjs3Bytduy9ucOtn6jeKw?s=sh&p=a&ilr=4" target="_blank" rel="noopener" class="w-full md:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl font-bold text-sm bg-emerald-400 text-slate-950 hover:bg-emerald-300 transition-all shadow-[0_0_20px_rgba(16,185,129,0.3)]">
            <i class="fab fa-whatsapp text-lg"></i> Unirme Gratis a la Comunidad
          </a>
        </div>
      </div>

    </div>
  </section>

  <!-- ════════════════════════════════════════════════════
       FOOTER
       ════════════════════════════════════════════════════ -->
  <footer class="bg-slate-950 border-t border-slate-900 py-12 px-4 sm:px-6 lg:px-8 text-xs text-slate-400 relative z-10">
    <div class="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-8 mb-10">
      
      <!-- Col 1: Branding -->
      <div>
        <a href="/" class="inline-block mb-3">
          <img src="__LOGO__" alt="Agencia ProsperIA" class="h-10 w-auto rounded-lg">
        </a>
        <p class="text-xs text-slate-400 leading-relaxed mb-4">
          Infraestructura de Inteligencia Artificial para marcas y creadores en Latinoamérica y Estados Unidos. Liderado por Edward Jiménez.
        </p>
        <div class="flex items-center gap-3">
          <a href="https://www.instagram.com/edwardjimenezia/" target="_blank" rel="noopener" class="text-slate-400 hover:text-cyan-400 transition-colors" title="Instagram Edward Jiménez"><i class="fab fa-instagram"></i></a>
          <a href="https://www.facebook.com/AgenciaProsperarIA/" target="_blank" rel="noopener" class="text-slate-400 hover:text-cyan-400 transition-colors" title="Facebook"><i class="fab fa-facebook-f"></i></a>
        </div>
      </div>

      <!-- Col 2: Enlaces Rápidos -->
      <div>
        <h4 class="text-white font-bold text-xs uppercase tracking-wider mb-4 text-cyan-400">Recursos de la Página</h4>
        <ul class="space-y-2.5">
          <li><a href="#codigos-grid" class="hover:text-white transition-colors">200 Códigos Creativos</a></li>
          <li><a href="#descargas" class="hover:text-white transition-colors">Descargas PDF Oficiales</a></li>
          <li><a href="javascript:void(0)" onclick="openSpidermanModal()" class="hover:text-white transition-colors">Prompt Reel Spiderman (Popup)</a></li>
          <li><a href="#reels-gallery" class="hover:text-white transition-colors">Galería de Nuestros Reels</a></li>
          <li><a href="/test-ia" target="_blank" rel="noopener" class="text-amber-400 hover:text-amber-300 font-semibold transition-colors">Diagnóstico IA (Página Nueva)</a></li>
          <li><a href="https://chat.whatsapp.com/HIjs3Bytduy9ucOtn6jeKw?s=sh&p=a&ilr=4" target="_blank" rel="noopener" class="text-emerald-400 hover:underline">Comunidad VIP WhatsApp</a></li>
        </ul>
      </div>

      <!-- Col 3: Soluciones -->
      <div>
        <h4 class="text-white font-bold text-xs uppercase tracking-wider mb-4 text-cyan-400">Soluciones de Negocio</h4>
        <ul class="space-y-2.5">
          <li><a href="#carta-ventas" class="hover:text-white transition-colors">Creación de Contenido Viral</a></li>
          <li><a href="#carta-ventas" class="hover:text-white transition-colors">Administración Integral 360°</a></li>
          <li><a href="https://passportai.app" target="_blank" rel="noopener" class="hover:text-white transition-colors text-amber-400 font-semibold">Plataforma PassportAI</a></li>
          <li><a href="javascript:void(0)" onclick="openCotizacionModal('integral')" class="hover:text-white transition-colors text-orange-400 font-semibold">Solicitar Cotización</a></li>
        </ul>
      </div>

      <!-- Col 4: Contacto -->
      <div>
        <h4 class="text-white font-bold text-xs uppercase tracking-wider mb-4 text-cyan-400">Contacto Directo</h4>
        <ul class="space-y-2.5">
          <li class="flex items-center gap-2"><i class="fas fa-envelope text-slate-500"></i> contacto@agenciaprosperia.com</li>
          <li class="flex items-center gap-2"><i class="fas fa-globe text-slate-500"></i> agenciaprosperia.com</li>
          <li class="flex items-center gap-2"><i class="fab fa-whatsapp text-emerald-400"></i> +1 (786) 557-3119</li>
          <li class="pt-2">
            <a href="https://chat.whatsapp.com/HIjs3Bytduy9ucOtn6jeKw?s=sh&p=a&ilr=4" target="_blank" rel="noopener" class="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-500/20 text-emerald-300 font-bold border border-emerald-500/30 hover:bg-emerald-500/30 transition-colors">
              <i class="fab fa-whatsapp"></i> Entrar a la Comunidad
            </a>
          </li>
        </ul>
      </div>

    </div>

    <div class="max-w-7xl mx-auto pt-8 border-t border-slate-900 flex flex-col sm:flex-row items-center justify-between gap-4 text-slate-400 text-center sm:text-left">
      <div>
        © 2026 Agencia ProsperIA LLC &amp; Edward Jiménez. Todos los derechos reservados.
      </div>
      <div class="flex gap-4">
        <a href="/privacidad" class="hover:text-slate-200 transition-colors">Política de Privacidad</a>
        <span>•</span>
        <a href="/terminos" class="hover:text-slate-200 transition-colors">Términos de Servicio</a>
      </div>
    </div>
  </footer>

  <!-- ════════════════════════════════════════════════════
       REQUISITO 2: POPUP MODAL REEL DE SPIDERMAN ("THE SWING PROMPTS")
       ════════════════════════════════════════════════════ -->
  <div id="spiderman-modal" class="fixed inset-0 z-50 hidden bg-slate-950/85 backdrop-blur-md flex items-center justify-center p-3 sm:p-6 overflow-y-auto" role="dialog" aria-modal="true" aria-labelledby="spiderman-modal-title">
    <div class="relative w-full max-w-4xl bg-slate-950 border-2 border-red-500/40 rounded-3xl p-5 sm:p-8 shadow-[0_0_60px_rgba(239,68,68,0.25)] my-auto max-h-[92vh] overflow-y-auto">
      
      <!-- Close Button -->
      <button type="button" onclick="closeSpidermanModal()" class="absolute top-4 right-4 sm:top-6 sm:right-6 w-10 h-10 rounded-full bg-slate-900 border border-slate-700 text-slate-400 hover:text-white hover:border-red-400 flex items-center justify-center transition-all focus:outline-none z-10" aria-label="Cerrar modal">
        <i class="fas fa-times text-base"></i>
      </button>

      <div class="spiderman-header-grid mb-6 pr-10">
        <div class="w-14 h-14 sm:w-16 sm:h-16 rounded-2xl bg-gradient-to-br from-red-600/30 to-slate-950 border border-red-500/50 text-red-400 flex items-center justify-center text-2xl sm:text-3xl shadow-xl flex-shrink-0">
          <i class="fas fa-spider"></i>
        </div>
        <div>
          <div class="flex items-center gap-2 flex-wrap mb-1">
            <span class="px-3 py-0.5 rounded-full text-[11px] font-extrabold uppercase tracking-wider bg-red-950/80 text-red-300 border border-red-500/30">
              🕷️ DESGLOSE TÉCNICO OFICIAL
            </span>
            <span class="text-xs text-slate-400 font-mono">ChatGPT + Seedance 2.0</span>
          </div>
          <h2 id="spiderman-modal-title" class="text-xl sm:text-3xl font-extrabold text-white">
            Reel de Spiderman: "The Swing Prompts"
          </h2>
          <p class="text-xs sm:text-sm text-slate-300 mt-1">
            Por <strong>Edward Jiménez</strong> (<a href="https://www.instagram.com/edwardjimenezia/" target="_blank" rel="noopener" class="text-red-400 font-bold hover:underline">@edwardjimenezia</a>) · Agencia ProsperIA
          </p>
        </div>
        <div class="pt-2 sm:pt-0">
          <a href="https://www.instagram.com/p/DdsN1nasM46/" target="_blank" rel="noopener" class="spiderman-ig-btn">
            <i class="fab fa-instagram text-base"></i> <span>Ver en Instagram</span>
          </a>
        </div>
      </div>

      <p class="text-slate-300 text-xs sm:text-sm leading-relaxed mb-6">
        Aquí tienes el procedimiento técnico en 3 pasos para recrear la transición del sujeto en la ventana lanzándose al vacío como Spiderman. <strong>Pícale a cada paso para desplegar su prompt</strong> traducido y listo para copiar en 1 clic:
      </p>

      <!-- Accordion for the 3 Steps -->
      <div class="space-y-3 mb-6" id="spiderman-accordion">
        
        <!-- Accordion Item 1 -->
        <div class="border border-red-500/40 rounded-2xl bg-slate-950/80 overflow-hidden transition-all duration-200" id="accordion-item-1">
          <button type="button" onclick="toggleSpidermanStep(1)" class="w-full p-4 sm:p-5 flex items-center justify-between text-left hover:bg-slate-900/60 transition-colors">
            <div class="flex items-center gap-3">
              <span class="w-8 h-8 rounded-xl bg-red-950 border border-red-500/40 text-red-400 text-sm flex items-center justify-center font-bold flex-shrink-0">1</span>
              <div>
                <h4 class="text-sm sm:text-base font-bold text-white flex items-center gap-2">
                  <span>Paso 1: Genera tu Retrato Base en ChatGPT</span>
                  <span class="px-2 py-0.5 rounded text-[10px] font-mono bg-red-950/60 text-red-300 border border-red-500/20">DALL-E 3</span>
                </h4>
                <p class="text-xs text-slate-400 mt-0.5">Sube tu foto y genera la escena del sujeto sentado en la ventana abierta de NYC.</p>
              </div>
            </div>
            <div class="flex items-center gap-3 flex-shrink-0 ml-2">
              <span class="text-xs text-red-400 hidden sm:inline font-mono">Pícale aquí</span>
              <i class="fas fa-chevron-down text-slate-400 transition-transform duration-300 rotate-180" id="chevron-1"></i>
            </div>
          </button>
          
          <div id="step-content-1" class="px-4 sm:px-6 pb-6 pt-2 border-t border-slate-800/80">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3 mt-3">
              <span class="text-xs text-slate-300 font-medium"><strong>Instrucción:</strong> Sube tu foto de frente (selfie) a ChatGPT y pega:</span>
              <button onclick="copyCode(document.getElementById('prompt-spiderman-1').innerText, this)" class="btn-copy px-3 py-1.5 rounded-lg text-xs font-bold inline-flex items-center gap-1.5 flex-shrink-0 self-start sm:self-auto">
                <i class="far fa-copy"></i> Copiar Prompt
              </button>
            </div>
            <div id="prompt-spiderman-1" class="prompt-box select-all">Referencia: Utiliza la imagen subida como referencia directa para la fisonomía del rostro, pero coloca al personaje como un hombre joven sentado en el alféizar de una ventana de piso a techo completamente abierta dentro de una acogedora habitación de Nueva York. La ventana está totalmente abierta y deja pasar una brisa natural. El sujeto se sienta con las piernas hacia el cuarto, postura relajada y confiada, mirando a la cámara con una sonrisa natural.

Vestuario: Chaqueta de cuero negro mate, camiseta blanca de algodón grueso, pantalones anchos negros oversize, zapatillas blancas Nike Air Force 1 impecables, y auriculares negros over-ear descansando alrededor del cuello.

Entorno de la Habitación: Iluminación interior cálida y tenue (lámpara cálida fuera de foco en la esquina), pared de ladrillo visto con pósters enmarcados de bandas indie, una planta monstera en maceta, cama deshecha con sábanas blancas y un escritorio de madera con una laptop brillante.

Exterior por la Ventana: Tarde dorada en Nueva York, luz suave del atardecer tiñendo los rascacielos circundantes de tonos ámbar y oro. Calles distantes visibles abajo con tráfico de taxis amarillos desenfocados. Profundidad atmosférica, ligera neblina urbana cálida.

Estilo de Cámara: Fotografía realista de 35mm, ángulo medio ligeramente contrapicado, f/2.0, desenfoque de fondo suave (bokeh agradable), grano de película sutil, colores ricos pero naturales, alto rango dinámico sin sobreexposición.</div>
          </div>
        </div>

        <!-- Accordion Item 2 -->
        <div class="border border-slate-800 rounded-2xl bg-slate-950/80 overflow-hidden transition-all duration-200" id="accordion-item-2">
          <button type="button" onclick="toggleSpidermanStep(2)" class="w-full p-4 sm:p-5 flex items-center justify-between text-left hover:bg-slate-900/60 transition-colors">
            <div class="flex items-center gap-3">
              <span class="w-8 h-8 rounded-xl bg-red-950 border border-red-500/40 text-red-400 text-sm flex items-center justify-center font-bold flex-shrink-0">2</span>
              <div>
                <h4 class="text-sm sm:text-base font-bold text-white flex items-center gap-2">
                  <span>Paso 2: Genera el Fotograma de Acción (Vuelo Spiderman)</span>
                  <span class="px-2 py-0.5 rounded text-[10px] font-mono bg-red-950/60 text-red-300 border border-red-500/20">Acción Aérea</span>
                </h4>
                <p class="text-xs text-slate-400 mt-0.5">Mismo personaje en caída libre balanceándose entre los rascacielos.</p>
              </div>
            </div>
            <div class="flex items-center gap-3 flex-shrink-0 ml-2">
              <span class="text-xs text-red-400 hidden sm:inline font-mono">Pícale aquí</span>
              <i class="fas fa-chevron-down text-slate-400 transition-transform duration-300" id="chevron-2"></i>
            </div>
          </button>
          
          <div id="step-content-2" class="px-4 sm:px-6 pb-6 pt-2 border-t border-slate-800/80 hidden">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3 mt-3">
              <span class="text-xs text-slate-300 font-medium"><strong>Instrucción:</strong> En el mismo chat de ChatGPT pega este prompt:</span>
              <button onclick="copyCode(document.getElementById('prompt-spiderman-2').innerText, this)" class="btn-copy px-3 py-1.5 rounded-lg text-xs font-bold inline-flex items-center gap-1.5 flex-shrink-0 self-start sm:self-auto">
                <i class="far fa-copy"></i> Copiar Prompt
              </button>
            </div>
            <div id="prompt-spiderman-2" class="prompt-box select-all">Plano de acción acrobático en caída libre: El mismo hombre joven del Paso 1 (misma chaqueta de cuero negro, pantalones anchos negros, zapatillas blancas) ahora está en pleno aire lanzándose desde la ventana del rascacielos. Postura dinámica inspirada en Spiderman: cuerpo arqueado en pose de balanceo, una mano estirada hacia adelante como si disparara una telaraña, la otra hacia atrás para estabilizar el equilibrio.

Perspectiva de Cámara: Gran angular dramático en picado extremo (Extreme High Angle), mirando directamente hacia el abismo de las calles de Manhattan con rascacielos convergiendo en perspectiva forzada. La ventana de la habitación queda visible arriba a la izquierda como punto de origen de la caída.

Efectos de Movimiento: Desenfreno de velocidad cinemática (Motion Blur) en las extremidades y el fondo urbano para transmitir adrenalina y velocidad vertiginosa. El viento deforma su ropa y hace volar su cabello. Partículas de polvo dorado en suspensión captadas por el sol poniente.

Iluminación y Color: Luz de atardecer lateral cortante, destellos de lente anamórfico dorado (warm lens flare), sombras profundas contrastadas. Tono cinematográfico estilo Spider-Man: Into the Spider-Verse en acción real de 35mm.</div>
          </div>
        </div>

        <!-- Accordion Item 3 -->
        <div class="border border-slate-800 rounded-2xl bg-slate-950/80 overflow-hidden transition-all duration-200" id="accordion-item-3">
          <button type="button" onclick="toggleSpidermanStep(3)" class="w-full p-4 sm:p-5 flex items-center justify-between text-left hover:bg-slate-900/60 transition-colors">
            <div class="flex items-center gap-3">
              <span class="w-8 h-8 rounded-xl bg-red-950 border border-red-500/40 text-red-400 text-sm flex items-center justify-center font-bold flex-shrink-0">3</span>
              <div>
                <h4 class="text-sm sm:text-base font-bold text-white flex items-center gap-2">
                  <span>Paso 3: Directiva de Cámara y Video (Seedance 2.0 / Luma / Runway)</span>
                  <span class="px-2 py-0.5 rounded text-[10px] font-mono bg-red-950/60 text-red-300 border border-red-500/20">Video IA</span>
                </h4>
                <p class="text-xs text-slate-400 mt-0.5">Prompt de control de movimiento continuo que atraviesa la ventana al vacío.</p>
              </div>
            </div>
            <div class="flex items-center gap-3 flex-shrink-0 ml-2">
              <span class="text-xs text-red-400 hidden sm:inline font-mono">Pícale aquí</span>
              <i class="fas fa-chevron-down text-slate-400 transition-transform duration-300" id="chevron-3"></i>
            </div>
          </button>
          
          <div id="step-content-3" class="px-4 sm:px-6 pb-6 pt-2 border-t border-slate-800/80 hidden">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3 mt-3">
              <span class="text-xs text-slate-300 font-medium"><strong>Instrucción:</strong> Sube la imagen del Paso 1 como First Frame en Seedance 2.0 o Runway Gen-3 y escribe:</span>
              <button onclick="copyCode(document.getElementById('prompt-spiderman-3').innerText, this)" class="btn-copy px-3 py-1.5 rounded-lg text-xs font-bold inline-flex items-center gap-1.5 flex-shrink-0 self-start sm:self-auto">
                <i class="far fa-copy"></i> Copiar Prompt
              </button>
            </div>
            <div id="prompt-spiderman-3" class="prompt-box select-all">Camera Movement: Cinematic continuous forward push through the open window, tracking the character seamlessly as he turns, smiles at the camera, and confidently leans backward dropping out of the window into the urban void.

Motion Dynamic: As the character falls backward through the frame, the camera accelerates rapidly following him over the sill, tilting down 60 degrees into a steep vertigo dive. Subtle natural handheld jitter, high kinetic energy, seamless physics transition from stillness to high-speed drop.

Atmosphere & Speed: Heavy wind turbulence rippling clothes and hair, dynamic sunset flare cutting across the camera lens as it crosses the threshold of the window, realistic atmospheric haze in the distance between Manhattan skyscrapers. 24fps film motion cadence.</div>
          </div>
        </div>

      </div>

      <div class="flex justify-end pt-4 border-t border-slate-800">
        <button type="button" onclick="closeSpidermanModal()" class="px-5 py-2.5 rounded-xl text-xs sm:text-sm font-bold bg-slate-900 border border-slate-700 text-slate-300 hover:text-white hover:bg-slate-800 transition-colors">
          Cerrar
        </button>
      </div>

    </div>
  </div>

  <!-- ════════════════════════════════════════════════════
       REQUISITO 5: POPUP MODAL FORMULARIO DE COTIZACIÓN ENTUSIASTA
       ════════════════════════════════════════════════════ -->
  <div id="cotizacion-modal" class="fixed inset-0 z-50 hidden bg-slate-950/85 backdrop-blur-md flex items-center justify-center p-3 sm:p-6 overflow-y-auto" role="dialog" aria-modal="true" aria-labelledby="cotizacion-modal-title">
    <div class="relative w-full max-w-lg bg-slate-950 border-2 border-orange-500/40 rounded-3xl p-6 sm:p-8 shadow-[0_0_60px_rgba(249,115,22,0.3)] my-auto max-h-[92vh] overflow-y-auto">
      
      <!-- Close Button -->
      <button type="button" onclick="closeCotizacionModal()" class="absolute top-4 right-4 sm:top-5 sm:right-5 w-10 h-10 rounded-full bg-slate-900 border border-slate-700 text-slate-400 hover:text-white hover:border-orange-400 flex items-center justify-center transition-all focus:outline-none z-10" aria-label="Cerrar modal">
        <i class="fas fa-times text-base"></i>
      </button>

      <div class="text-center mb-6 pr-6">
        <span class="px-3.5 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-orange-950 text-orange-300 border border-orange-500/40 inline-block mb-2">
          🚀 ¡Gran Decisión de Crecimiento!
        </span>
        <h3 id="cotizacion-modal-title" class="text-xl sm:text-2xl font-black text-white">
          Cotización de Servicio ProsperIA
        </h3>
        <p class="text-xs text-slate-300 mt-1.5 leading-relaxed">
          Llena tus datos con entusiasmo y coordinamos una propuesta a la medida en tiempo récord.
        </p>
      </div>

      <form id="modal-cotizacion-form" onsubmit="submitCotizacionModal(event)" class="space-y-4 text-left">
        <div>
          <label class="block text-xs font-semibold text-slate-300 mb-1.5">¿Qué modalidad te interesa? *</label>
          <div class="grid grid-cols-2 gap-2 text-xs">
            <label class="flex items-center gap-2 p-3 rounded-xl bg-slate-900/90 border border-slate-700 cursor-pointer hover:border-orange-400 transition-colors" id="modal-label-opt-contenido">
              <input type="radio" name="modal_servicio_opcion" value="contenido" class="text-orange-400 focus:ring-0">
              <span class="text-slate-200 font-medium text-[11px] sm:text-xs">1. Contenido Viral</span>
            </label>
            <label class="flex items-center gap-2 p-3 rounded-xl bg-slate-900/90 border border-slate-700 cursor-pointer hover:border-amber-400 transition-colors" id="modal-label-opt-integral">
              <input type="radio" name="modal_servicio_opcion" value="integral" checked class="text-amber-400 focus:ring-0">
              <span class="text-slate-200 font-medium text-[11px] sm:text-xs">2. Sistema 360°</span>
            </label>
          </div>
        </div>

        <div>
          <label class="block text-xs font-semibold text-slate-300 mb-1">Nombre Completo *</label>
          <input type="text" id="modal-direct-name" required placeholder="Ej. Carlos Mendoza" class="input-cotizacion w-full px-4 py-3 rounded-xl border border-slate-700 text-sm focus:border-orange-400 focus:outline-none" style="background-color: #030712 !important; color: #ffffff !important; font-size: 15px !important;">
        </div>

        <div>
          <label class="block text-xs font-semibold text-slate-300 mb-1">Correo Electrónico *</label>
          <input type="email" id="modal-direct-email" required placeholder="tu@empresa.com" class="input-cotizacion w-full px-4 py-3 rounded-xl border border-slate-700 text-sm focus:border-orange-400 focus:outline-none" style="background-color: #030712 !important; color: #ffffff !important; font-size: 15px !important;">
        </div>

        <div>
          <label class="block text-xs font-semibold text-slate-300 mb-1">WhatsApp (con código de país) *</label>
          <input type="tel" id="modal-direct-phone" required placeholder="+1 786 555 0199" class="input-cotizacion w-full px-4 py-3 rounded-xl border border-slate-700 text-sm focus:border-orange-400 focus:outline-none" style="background-color: #030712 !important; color: #ffffff !important; font-size: 15px !important;">
        </div>

        <button type="submit" id="btn-submit-modal" class="btn-cotizacion-cta mt-3">
          <i class="fab fa-whatsapp text-lg"></i> <span>¡Enviar y Recibir Propuesta en WhatsApp!</span>
        </button>
        
        <div class="text-center pt-2">
          <a href="https://wa.me/17865573119?text=Hola,%20quiero%20solicitar%20una%20cotizaci%C3%B3n%20para%20mi%20empresa" target="_blank" rel="noopener" class="text-xs text-emerald-400 hover:text-emerald-300 transition-colors inline-flex items-center gap-1.5 font-semibold">
            <i class="fab fa-whatsapp"></i> ¿Prefieres escribir directo sin llenar el formulario? Clic aquí
          </a>
        </div>
      </form>
    </div>
  </div>

  <!-- ════════════════════════════════════════════════════
       JAVASCRIPT LOGIC
       ════════════════════════════════════════════════════ -->
  <script>
    // Global filter states
    let activeCat = 'all';
    let activeCol = 'all';
    let currentSearchTerm = '';
    let isCatalogExpanded = false;

    const cardsContainer = document.getElementById('cards-container');
    const cardsWrapper = document.getElementById('cards-wrapper');
    const cardsFadeOverlay = document.getElementById('cards-fade-overlay');
    const searchInput = document.getElementById('search-input');
    const clearSearchBtn = document.getElementById('clear-search');
    const visibleCountEl = document.getElementById('visible-count');
    const noResultsEl = document.getElementById('no-results');

    // Live search handler
    function handleSearch(term) {
      currentSearchTerm = term.trim().toLowerCase();
      if (currentSearchTerm.length > 0) {
        clearSearchBtn.classList.remove('hidden');
        expandCatalogTemporarily();
      } else {
        clearSearchBtn.classList.add('hidden');
      }
      applyFilters();
    }

    // Filter by category
    function filterCategory(catId, btn) {
      activeCat = catId;
      document.querySelectorAll('#category-pills .filter-chip').forEach(chip => {
        chip.classList.remove('active');
      });
      if (btn) btn.classList.add('active');
      expandCatalogTemporarily();
      applyFilters();
    }

    // Filter by collection
    function filterCollection(colId, btn) {
      activeCol = colId;
      document.querySelectorAll('.tab-collection').forEach(tab => {
        tab.classList.remove('active');
        tab.classList.add('border-slate-700', 'bg-slate-900/80', 'text-slate-300');
        tab.classList.remove('border-cyan-500/40', 'bg-cyan-950/60', 'text-cyan-300');
      });
      if (btn) {
        btn.classList.add('active');
        btn.classList.remove('border-slate-700', 'bg-slate-900/80', 'text-slate-300');
        btn.classList.add('border-cyan-500/40', 'bg-cyan-950/60', 'text-cyan-300');
      }
      expandCatalogTemporarily();
      applyFilters();
    }

    // Master filter execution
    function applyFilters() {
      const cards = cardsContainer.querySelectorAll('.code-card');
      let visible = 0;

      cards.forEach(card => {
        const cardCat = card.getAttribute('data-category');
        const cardCol = card.getAttribute('data-collection');
        const cardSearch = card.getAttribute('data-search');

        const matchesCat = (activeCat === 'all') || (cardCat === activeCat);
        const matchesCol = (activeCol === 'all') || (cardCol === activeCol);
        const matchesSearch = (currentSearchTerm === '') || cardSearch.includes(currentSearchTerm);

        if (matchesCat && matchesCol && matchesSearch) {
          card.classList.remove('hidden');
          visible++;
        } else {
          card.classList.add('hidden');
        }
      });

      visibleCountEl.textContent = visible;

      if (visible === 0) {
        noResultsEl.classList.remove('hidden');
        cardsContainer.classList.add('hidden');
      } else {
        noResultsEl.classList.add('hidden');
        cardsContainer.classList.remove('hidden');
      }
    }

    function clearSearch() {
      searchInput.value = '';
      currentSearchTerm = '';
      clearSearchBtn.classList.add('hidden');
      applyFilters();
      searchInput.focus();
    }

    function expandCatalogTemporarily() {
      if (!isCatalogExpanded) {
        toggleCatalogExpansion();
      }
    }

    // REQUISITO 1: Sincronización del botón en ambos lugares (TOP y BOTTOM)
    function toggleCatalogExpansion() {
      isCatalogExpanded = !isCatalogExpanded;
      const icons = document.querySelectorAll('.toggle-catalog-icon');
      const texts = document.querySelectorAll('.toggle-catalog-text');

      if (isCatalogExpanded) {
        cardsWrapper.style.maxHeight = 'none';
        cardsFadeOverlay.classList.add('hidden');
        icons.forEach(ic => ic.classList.add('rotate-180'));
        texts.forEach(tx => tx.textContent = 'Compactar Catálogo (Ver Menos)');
      } else {
        cardsWrapper.style.maxHeight = '740px';
        cardsFadeOverlay.classList.remove('hidden');
        icons.forEach(ic => ic.classList.remove('rotate-180'));
        texts.forEach(tx => tx.textContent = 'Desplegar Catálogo Completo (Ver los 200 Códigos)');
        document.getElementById('codigos-grid').scrollIntoView({ behavior: 'smooth' });
      }
    }

    // 1-Click Clipboard Copier
    async function copyCode(text, btn) {
      try {
        await navigator.clipboard.writeText(text);
        const originalHtml = btn.innerHTML;
        btn.classList.add('copied');
        btn.innerHTML = '<i class="fas fa-check text-xs"></i> <span>¡Copiado!</span>';
        setTimeout(() => {
          btn.classList.remove('copied');
          btn.innerHTML = originalHtml;
        }, 1800);
      } catch (err) {
        const temp = document.createElement('textarea');
        temp.value = text;
        document.body.appendChild(temp);
        temp.select();
        document.execCommand('copy');
        document.body.removeChild(temp);
        btn.classList.add('copied');
        btn.innerHTML = '<i class="fas fa-check text-xs"></i> <span>¡Copiado!</span>';
        setTimeout(() => {
          btn.classList.remove('copied');
          btn.innerHTML = originalHtml;
        }, 1800);
      }
    }

    async function copyFullPrompt(promptText, btn) {
      try {
        await navigator.clipboard.writeText(promptText);
        const icon = btn.querySelector('i');
        icon.className = 'fas fa-check text-emerald-400';
        setTimeout(() => {
          icon.className = 'fas fa-magic text-[11px]';
        }, 1800);
      } catch (e) {}
    }

    // REQUISITO 2: Modal de Spiderman Logic
    function openSpidermanModal() {
      const modal = document.getElementById('spiderman-modal');
      if (modal) {
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
        toggleSpidermanStep(1);
      }
    }

    function closeSpidermanModal() {
      const modal = document.getElementById('spiderman-modal');
      if (modal) {
        modal.classList.add('hidden');
        document.body.style.overflow = '';
      }
    }

    // Spiderman Accordion inside Modal
    function toggleSpidermanStep(stepNum) {
      for (let i = 1; i <= 3; i++) {
        const content = document.getElementById(`step-content-${i}`);
        const chevron = document.getElementById(`chevron-${i}`);
        const item = document.getElementById(`accordion-item-${i}`);

        if (i === stepNum) {
          const isCurrentlyHidden = content.classList.contains('hidden');
          if (isCurrentlyHidden) {
            content.classList.remove('hidden');
            chevron.classList.add('rotate-180');
            item.classList.add('border-red-500/40');
            item.classList.remove('border-slate-800');
          } else {
            content.classList.add('hidden');
            chevron.classList.remove('rotate-180');
            item.classList.remove('border-red-500/40');
            item.classList.add('border-slate-800');
          }
        } else {
          content.classList.add('hidden');
          chevron.classList.remove('rotate-180');
          item.classList.remove('border-red-500/40');
          item.classList.add('border-slate-800');
        }
      }
    }

    // REQUISITO 5: Modal de Cotización Logic
    function openCotizacionModal(option = 'integral') {
      const modal = document.getElementById('cotizacion-modal');
      if (!modal) return;

      const radio = document.querySelector(`input[name="modal_servicio_opcion"][value="${option}"]`);
      if (radio) radio.checked = true;

      modal.classList.remove('hidden');
      document.body.style.overflow = 'hidden';
      setTimeout(() => {
        const nameInput = document.getElementById('modal-direct-name');
        if (nameInput) nameInput.focus();
      }, 300);
    }

    function closeCotizacionModal() {
      const modal = document.getElementById('cotizacion-modal');
      if (modal) {
        modal.classList.add('hidden');
        document.body.style.overflow = '';
      }
    }

    async function submitCotizacionModal(e) {
      e.preventDefault();
      const selectedRadio = document.querySelector('input[name="modal_servicio_opcion"]:checked');
      const servicio = selectedRadio ? selectedRadio.value : 'integral';
      const name = document.getElementById('modal-direct-name').value.trim();
      const email = document.getElementById('modal-direct-email').value.trim();
      const phone = document.getElementById('modal-direct-phone').value.trim();

      const btn = document.getElementById('btn-submit-modal');
      const originalHtml = btn.innerHTML;
      btn.disabled = true;
      btn.innerHTML = '<i class="fas fa-spinner fa-spin text-lg"></i> <span>Coordinando...</span>';

      try {
        await fetch('/api/leads', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: name,
            email: email,
            phone: phone,
            company: 'Solicitud desde Hub Códigos IA (Modal)',
            source: 'hub_codigos_modal',
            service: servicio === 'contenido' ? 'Opción 1: Contenido Viral' : 'Opción 2: Sistema Integral 360',
            notes: `Cotización solicitada desde popup de 200 códigos. Modalidad: ${servicio}`
          })
        });
      } catch (err) {
        console.warn('Silent lead logging sync');
      }

      // WhatsApp redirection
      const servicioText = servicio === 'contenido' ? 'Opción 1: Contenido Viral con IA' : 'Opción 2: Sistema Integral 360°';
      const textWa = encodeURIComponent(`Hola Edward & ProsperIA! Acabo de solicitar una cotización desde su Hub de Códigos de IA:\\n\\n👤 Nombre: ${name}\\n📧 Correo: ${email}\\n📱 WhatsApp: ${phone}\\n🎯 Modalidad: ${servicioText}\\n\\n¿Cuándo podríamos coordinar la propuesta?`);
      
      btn.innerHTML = '<i class="fas fa-check text-lg"></i> <span>¡Abriendo WhatsApp!</span>';
      
      setTimeout(() => {
        window.open(`https://wa.me/17865573119?text=${textWa}`, '_blank');
        closeCotizacionModal();
        btn.disabled = false;
        btn.innerHTML = originalHtml;
      }, 600);
    }

    // Mobile navigation menu toggle
    function toggleMobileMenu() {
      const panel = document.getElementById('mobile-nav-panel');
      const icon = document.getElementById('mobile-menu-icon');
      if (panel.classList.contains('hidden')) {
        panel.classList.remove('hidden');
        if (icon) icon.className = 'fas fa-times text-base';
      } else {
        panel.classList.add('hidden');
        if (icon) icon.className = 'fas fa-bars text-base';
      }
    }

    function closeMobileMenu() {
      const panel = document.getElementById('mobile-nav-panel');
      const icon = document.getElementById('mobile-menu-icon');
      if (panel) panel.classList.add('hidden');
      if (icon) icon.className = 'fas fa-bars text-base';
    }

    // Close modals on Escape key or outside click
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        closeSpidermanModal();
        closeCotizacionModal();
      }
    });

    document.getElementById('spiderman-modal')?.addEventListener('click', (e) => {
      if (e.target.id === 'spiderman-modal') closeSpidermanModal();
    });

    document.getElementById('cotizacion-modal')?.addEventListener('click', (e) => {
      if (e.target.id === 'cotizacion-modal') closeCotizacionModal();
    });

    // Scrollspy for active navbar indicator
    window.addEventListener('scroll', () => {
      const sections = [
        'codigos-grid',
        'descargas',
        'reels-gallery',
        'passportai-showcase',
        'carta-ventas'
      ];
      const scrollPos = window.scrollY + 140;
      let currentSection = '';

      for (const id of sections) {
        const el = document.getElementById(id);
        if (el && el.offsetTop <= scrollPos) {
          currentSection = id;
        }
      }

      if (currentSection) {
        document.querySelectorAll('.nav-link-item').forEach(link => {
          if (link.getAttribute('href') === `#${currentSection}`) {
            link.classList.add('active');
          } else {
            link.classList.remove('active');
          }
        });
      }
    });
  </script>

</body>
</html>
"""

def generate_page(is_template=False):
    def s_asset(filename):
        if is_template:
            return f"{{{{ static_versioned('{filename}') }}}}"
        return f"/static/{filename}"

    html = HTML_TEMPLATE
    html = html.replace('__PILLS_STR__', pills_str)
    html = html.replace('__CARDS_STR__', cards_str)
    html = html.replace('__REELS_GRID_STR__', reels_grid_str)
    html = html.replace('__FAVICON__', s_asset('favicon.png'))
    html = html.replace('__LOGO__', s_asset('logo_prosper_ia_cropped.jpg'))
    html = html.replace('__PASSPORTAI_IMG__', s_asset('passportai_dashboard_real.png'))
    return html

# Generate static version
static_html = generate_page(is_template=False)
with open('static/codigos/index.html', 'w', encoding='utf-8') as f:
    f.write(static_html)
print(f'Successfully generated static/codigos/index.html with {len(all_codes)} codes!')

template_html = generate_page(is_template=True)
with open('scratch/template_codigos.html', 'w', encoding='utf-8') as f:
    f.write(template_html)
print('Successfully generated scratch/template_codigos.html')

with open('templates/codigos.html', 'w', encoding='utf-8') as f:
    f.write(template_html)
print('Successfully generated templates/codigos.html')

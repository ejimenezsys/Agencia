import os
import json

# Load the 100 codes JSON
with open('content/codigos_100.json', 'r', encoding='utf-8') as f:
    categories_data = json.load(f)

category_icons = {
    "01": "fa-lightbulb",
    "02": "fa-paint-brush",
    "03": "fa-eye",
    "04": "fa-sun",
    "05": "fa-video",
    "06": "fa-palette",
    "07": "fa-film",
    "08": "fa-camera",
    "09": "fa-cube",
    "10": "fa-box-open"
}

# Build Categories Filter Pills HTML
pills_html = [
    '<button type="button" class="filter-chip active px-4 py-2 rounded-xl text-xs font-semibold cursor-pointer border border-cyan-500/30 bg-cyan-500/20 text-cyan-300 hover:border-cyan-400 transition-all flex items-center gap-1.5" data-cat="all" onclick="filterCategory(\'all\', this)">'
    '<i class="fas fa-th-large text-xs"></i> <span>Todos los Códigos (100)</span>'
    '</button>'
]

cards_html = []

for cat in categories_data:
    cat_id = cat['category_id']
    cat_name = cat['category_name']
    icon_cls = category_icons.get(cat_id, "fa-tag")
    count = len(cat['items'])

    pills_html.append(
        f'<button type="button" class="filter-chip px-3.5 py-2 rounded-xl text-xs font-semibold cursor-pointer border border-slate-700 bg-slate-900/80 text-slate-300 hover:border-cyan-400/50 hover:text-white transition-all flex items-center gap-1.5" data-cat="{cat_id}" onclick="filterCategory(\'{cat_id}\', this)">'
        f'<i class="fas {icon_cls} text-cyan-400 text-xs"></i> <span>{cat_id}. {cat_name} ({count})</span>'
        f'</button>'
    )

    for it in cat['items']:
        num = it['number']
        cmd = it['command']
        desc = it['description']
        desc_escaped = desc.replace('"', '&quot;').replace("'", "&#39;")
        search_haystack = f"{num} {cmd} {desc_escaped} {cat_name}".lower()

        card = f'''
        <div 
          class="code-card glass-panel rounded-2xl p-5 flex flex-col justify-between border-slate-800 hover:border-cyan-500/40 transition-all"
          data-category="{cat_id}"
          data-search="{search_haystack}"
        >
          <div>
            <div class="flex items-center justify-between gap-2 mb-3">
              <span class="text-[11px] font-mono font-bold px-2 py-0.5 rounded-md bg-cyan-950/80 text-cyan-300 border border-cyan-500/30">
                #{num}
              </span>
              <span class="text-[11px] text-slate-400 flex items-center gap-1 font-medium truncate max-w-[170px]" title="{cat_name}">
                <i class="fas {icon_cls} text-cyan-400 text-[10px]"></i> {cat_name}
              </span>
            </div>

            <h4 class="text-base font-bold text-white mb-2 tracking-tight flex items-center justify-between">
              <span>{cmd}</span>
            </h4>

            <p class="text-xs text-slate-300 leading-relaxed mb-4 font-light">
              {desc}
            </p>
          </div>

          <div class="pt-3 border-t border-slate-800/80">
            <div class="flex items-center justify-between bg-slate-950/90 rounded-xl px-3 py-2 border border-slate-800">
              <code class="font-mono text-xs font-semibold text-cyan-300 truncate max-w-[170px]" title="{cmd}">{cmd}</code>
              <button 
                type="button" 
                class="btn-copy px-2.5 py-1 rounded-lg text-xs font-bold inline-flex items-center gap-1.5 transition-all"
                onclick="copyCode('{cmd}', this)"
                title="Copiar comando al portapapeles"
              >
                <i class="far fa-copy text-[11px]"></i> <span>Copiar</span>
              </button>
              <button 
                type="button" 
                class="text-slate-400 hover:text-cyan-400 text-xs ml-2 p-1"
                onclick="copyFullPrompt('{cmd} {desc_escaped}', this)"
                title="Copiar comando con descripción"
              >
                <i class="fas fa-magic text-[11px]"></i>
              </button>
            </div>
          </div>
        </div>'''
        cards_html.append(card)

pills_str = "\n".join(pills_html)
cards_str = "\n".join(cards_html)


# Reels List Data with Dedicated Thumbnails & Strict PDF Flag
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
        "cta_action": "jumpToSpiderman()"
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
        "cta_icon": "fas fa-cube",
        "cta_action": "filterCategory('10', document.querySelector('[data-cat=\"10\"]'))"
    }
]

reels_cards_html = []
for r in reels_data:
    if r["has_pdf"]:
        cta_btn_html = f'''<button onclick="{r['cta_action']}" class="flex-1 inline-flex items-center justify-center gap-1.5 px-3 py-2.5 rounded-xl text-xs font-bold bg-gradient-to-r from-red-500/20 to-amber-500/20 text-amber-300 border border-amber-500/40 hover:bg-amber-400 hover:text-slate-950 transition-all">
          <i class="far fa-file-pdf text-red-400"></i> {r['cta_label']}
        </button>'''
    else:
        cta_btn_html = f'''<button onclick="{r['cta_action']}" class="flex-1 inline-flex items-center justify-center gap-1.5 px-3 py-2.5 rounded-xl text-xs font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-400/40 hover:bg-cyan-400 hover:text-slate-950 transition-all">
          <i class="{r['cta_icon']}"></i> {r['cta_label']}
        </button>'''

    r_card = f'''
    <div class="glass-panel p-5 sm:p-6 rounded-2xl flex flex-col justify-between border-slate-800 hover:border-cyan-500/40 transition-all group shadow-lg">
      <div>
        <div class="relative w-full h-44 rounded-xl overflow-hidden mb-4 border border-slate-800/80 bg-slate-950">
          <img src="{r['image']}" alt="{r['title']}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" loading="lazy">
          <div class="absolute inset-0 bg-gradient-to-t from-slate-950/90 via-slate-950/20 to-transparent"></div>
          <div class="absolute top-2.5 left-2.5">
            <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider border {r['tag_color']} backdrop-blur-md">
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

def generate_page(is_template=False):
    def s_asset(filename):
        if is_template:
            return f"{{{{ static_versioned('{filename}') }}}}"
        return f"/static/{filename}"

    return f'''<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Hub de Recursos de IA & 100 Códigos Creativos | ProsperIA & @edwardjimenezia</title>
  <meta name="description" content="Recursos oficiales de IA de Edward Jiménez y Agencia ProsperIA: 100 Códigos Creativos de ChatGPT, desglose técnico de The Swing Prompts (Spiderman), 2 guías PDF descargables y comunidad oficial.">
  <meta name="keywords" content="codigos chatgpt, test nivel ia, edward jimenez, comunidad whatsapp prosperia, reel spiderman prompt, passportai, automatizacion comercial ia">
  <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
  <link rel="canonical" href="https://agenciaprosperia.com/codigos">
  <link rel="icon" type="image/png" href="{s_asset('favicon.png')}">

  <!-- Open Graph / Instagram / WhatsApp Preview -->
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://agenciaprosperia.com/codigos">
  <meta property="og:title" content="Hub de IA & 100 Códigos Creativos | @edwardjimenezia">
  <meta property="og:description" content="100 Códigos Creativos de ChatGPT, Prompts de video viral Spiderman y guías PDF descargables oficiales.">
  <meta property="og:image" content="https://agenciaprosperia.com/static/edwar_jimenez.jpg">

  <!-- Twitter -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="Hub de Recursos de IA | @edwardjimenezia & ProsperIA">
  <meta name="twitter:description" content="100 Códigos para imágenes, Test de conocimiento de IA y prompts de Reels virales con más de 450K vistas.">
  <meta name="twitter:image" content="https://agenciaprosperia.com/static/edwar_jimenez.jpg">

  <link rel="stylesheet" href="{s_asset('tw.css')}">
  <link rel="stylesheet" href="{s_asset('fonts.css')}">
  <link rel="stylesheet" href="{s_asset('fa.min.css')}">

  <style>
    :root {{
      --bg-dark: #020710;
      --bg-surface: #070e1b;
      --bg-card: rgba(10, 19, 36, 0.78);
      --border-subtle: rgba(0, 229, 255, 0.15);
      --border-glow: rgba(0, 229, 255, 0.4);
      --accent-cyan: #00e5ff;
      --accent-lavender: #5e6ad2;
      --accent-gold: #f59e0b;
      --accent-green: #10b981;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
    }}

    * {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; box-sizing: border-box; }}
    h1, h2, h3, h4, .font-heading {{ font-family: 'Space Grotesk', sans-serif; }}
    html {{ scroll-behavior: smooth; }}
    body {{ background-color: var(--bg-dark); color: var(--text-main); overflow-x: hidden; }}

    /* Ambient background glows */
    .glow-cyan {{
      position: absolute;
      width: 600px;
      height: 600px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(0, 229, 255, 0.12) 0%, transparent 70%);
      pointer-events: none;
      z-index: 0;
    }}
    .glow-purple {{
      position: absolute;
      width: 500px;
      height: 500px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(94, 106, 210, 0.12) 0%, transparent 70%);
      pointer-events: none;
      z-index: 0;
    }}

    /* Glass Panels */
    .glass-panel {{
      background: var(--bg-card);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border: 1px solid var(--border-subtle);
      transition: all 0.25s ease;
    }}
    .glass-panel:hover {{
      border-color: var(--border-glow);
    }}

    /* Copy button animations */
    .btn-copy {{
      background: rgba(0, 229, 255, 0.12);
      color: #00e5ff;
      border: 1px solid rgba(0, 229, 255, 0.3);
      cursor: pointer;
    }}
    .btn-copy:hover {{
      background: rgba(0, 229, 255, 0.25);
      border-color: #00e5ff;
    }}
    .btn-copy.copied {{
      background: #10b981 !important;
      color: #020710 !important;
      border-color: #10b981 !important;
    }}

    /* Prompt code box */
    .prompt-box {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 13px;
      line-height: 1.6;
      background: #040914;
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 12px;
      color: #e2e8f0;
      white-space: pre-wrap;
    }}

    /* Navigation styling */
    .site-nav {{
      background: rgba(2, 7, 16, 0.85);
      backdrop-filter: blur(16px);
      border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    }}
  </style>
</head>
<body class="relative">

  <div class="glow-cyan -top-40 -left-40"></div>
  <div class="glow-purple top-[40%] -right-40"></div>

  <!-- ════════════════════════════════════════════════════
       1. TOP BAR: WHATSAPP COMMUNITY & SOCIAL ANNOUNCEMENT
       ════════════════════════════════════════════════════ -->
  <div class="bg-gradient-to-r from-emerald-950 via-slate-950 to-cyan-950 border-b border-emerald-500/30 py-2.5 px-4 text-center text-xs sm:text-sm text-slate-200 relative z-50">
    <div class="max-w-7xl mx-auto flex items-center justify-center gap-3 flex-wrap">
      <span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 font-bold text-[11px] uppercase tracking-wider border border-emerald-500/30">
        <i class="fab fa-whatsapp text-emerald-400"></i> Comunidad VIP
      </span>
      <span>Únete gratis al grupo de WhatsApp de <strong>Edward Jiménez</strong> &amp; <strong>Agencia ProsperIA</strong>:</span>
      <a href="https://chat.whatsapp.com/HIjs3Bytduy9ucOtn6jeKw?s=sh&p=a&ilr=4" target="_blank" rel="noopener" class="text-emerald-400 font-bold hover:underline inline-flex items-center gap-1">
        Entrar al Grupo Oficial <i class="fas fa-arrow-right text-[10px]"></i>
      </a>
    </div>
  </div>

  <!-- ════════════════════════════════════════════════════
       MAIN NAVBAR (AGENCIA PROSPERIA BRANDING)
       ════════════════════════════════════════════════════ -->
  <nav class="site-nav sticky top-0 left-0 w-full z-40 transition-all duration-300">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-20">
        
        <!-- Logo -->
        <a href="/" class="flex items-center gap-3 group">
          <img src="{s_asset('logo_prosper_ia_cropped.jpg')}" alt="AGENCIA PROSPERIA" class="h-12 w-auto object-contain rounded-lg group-hover:scale-105 transition-transform">
        </a>

        <!-- Desktop Links -->
        <div class="hidden lg:flex items-center gap-6 text-sm">
          <a href="#spiderman-breakdown" class="text-slate-300 hover:text-red-400 font-medium transition-colors flex items-center gap-1.5">
            <i class="fas fa-spider text-red-400 text-xs"></i> Reel Spiderman
          </a>
          <a href="#codigos-grid" class="text-cyan-400 font-bold flex items-center gap-1.5">
            <i class="fas fa-terminal text-xs"></i> 100 Códigos
          </a>
          <a href="#descargas" class="text-slate-300 hover:text-cyan-400 font-medium transition-colors flex items-center gap-1.5">
            <i class="far fa-file-pdf text-red-400 text-xs"></i> Descargas PDF
          </a>
          <a href="#reels-gallery" class="text-slate-300 hover:text-cyan-400 font-medium transition-colors flex items-center gap-1.5">
            <i class="fab fa-instagram text-pink-400 text-xs"></i> Nuestros Reels
          </a>
          <a href="#test-ia" class="text-slate-300 hover:text-cyan-400 font-medium transition-colors flex items-center gap-1.5">
            <i class="fas fa-brain text-cyan-400 text-xs"></i> Test de IA
          </a>
          <a href="#formulario-cotizacion" class="text-slate-300 hover:text-cyan-400 font-medium transition-colors flex items-center gap-1.5">
            <i class="fas fa-briefcase text-indigo-400 text-xs"></i> Cotizar
          </a>
        </div>

        <!-- Action CTAs -->
        <div class="flex items-center gap-3">
          <a href="https://chat.whatsapp.com/HIjs3Bytduy9ucOtn6jeKw?s=sh&p=a&ilr=4" target="_blank" rel="noopener" class="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-bold bg-emerald-500 text-slate-950 hover:bg-emerald-400 transition-all shadow-[0_0_15px_rgba(16,185,129,0.3)]">
            <i class="fab fa-whatsapp text-sm"></i> <span class="hidden sm:inline">Comunidad WhatsApp</span>
          </a>
          <button onclick="document.getElementById('formulario-cotizacion').scrollIntoView({{ behavior: 'smooth' }})" class="hidden sm:inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-bold bg-gradient-to-r from-cyan-400 to-cyan-500 text-slate-950 hover:from-cyan-300 hover:to-cyan-400 transition-all">
            <i class="fas fa-file-invoice-dollar text-xs"></i> Cotizar
          </button>
        </div>

      </div>
    </div>
  </nav>

  <!-- ════════════════════════════════════════════════════
       HERO SECTION WITH VIRAL SOCIAL PROOF
       ════════════════════════════════════════════════════ -->
  <header class="relative pt-12 pb-10 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto z-10 text-center">
    
    <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-cyan-950/80 border border-cyan-400/30 text-cyan-300 text-xs sm:text-sm font-medium mb-6 backdrop-blur-md">
      <span class="w-2 h-2 rounded-full bg-cyan-400 animate-ping"></span>
      🎁 Hub de Recursos Exclusivos para Seguidores de Instagram &amp; Facebook
    </div>

    <h1 class="text-3xl sm:text-5xl lg:text-6xl font-extrabold text-white tracking-tight leading-tight mb-6 max-w-4xl mx-auto">
      El Arsenal de <span class="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-sky-300 to-indigo-400">Inteligencia Artificial</span> para Crear Contenido y Escalar tu Negocio
    </h1>

    <p class="text-slate-300 text-base sm:text-xl max-w-3xl mx-auto mb-8 leading-relaxed font-light">
      Bienvenido al centro oficial de recursos de <strong>Edward Jiménez</strong> y <strong>Agencia ProsperIA</strong>. Aquí tienes acceso inmediato a los prompts virales de Hollywood, los 100 Códigos Creativos de ChatGPT listos para copiar, las 2 guías PDF oficiales y nuestra comunidad.
    </p>

    <!-- Social Proof Metrics Bar -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4 max-w-4xl mx-auto mb-6">
      <div class="glass-panel p-4 rounded-2xl text-center border-amber-500/20">
        <div class="text-2xl sm:text-3xl font-extrabold text-amber-400 font-heading">+450,000</div>
        <div class="text-xs text-slate-300 mt-1">Vistas en Reel Viral</div>
      </div>
      <div class="glass-panel p-4 rounded-2xl text-center border-cyan-500/20">
        <div class="text-2xl sm:text-3xl font-extrabold text-cyan-400 font-heading">10,000+</div>
        <div class="text-xs text-slate-300 mt-1">Seguidores en ProsperIA FB</div>
      </div>
      <div class="glass-panel p-4 rounded-2xl text-center border-pink-500/20">
        <div class="text-2xl sm:text-3xl font-extrabold text-pink-400 font-heading">+2,000</div>
        <div class="text-xs text-slate-300 mt-1">Comunidad @edwardjimenezia</div>
      </div>
      <div class="glass-panel p-4 rounded-2xl text-center border-emerald-500/20">
        <div class="text-2xl sm:text-3xl font-extrabold text-emerald-400 font-heading">100 Códigos</div>
        <div class="text-xs text-slate-300 mt-1">Visuales 100% Gratuitos</div>
      </div>
    </div>

  </header>

  <!-- ════════════════════════════════════════════════════
       BLOQUE 1 (VALOR PRIMERO): REEL DE SPIDERMAN "THE SWING PROMPTS"
       ════════════════════════════════════════════════════ -->
  <section id="spiderman-breakdown" class="py-10 px-4 sm:px-6 lg:px-8 max-w-5xl mx-auto relative z-10 scroll-mt-24">
    
    <div class="glass-panel p-6 sm:p-10 rounded-3xl border-red-500/30 relative overflow-hidden bg-gradient-to-b from-slate-950 via-red-950/10 to-slate-950 shadow-2xl">
      <div class="absolute -top-24 -right-24 w-80 h-80 bg-red-600/10 rounded-full blur-3xl pointer-events-none"></div>

      <!-- Header without photo, using clean tech badge -->
      <div class="flex flex-col sm:flex-row items-center sm:items-start gap-5 mb-8 pb-8 border-b border-slate-800">
        <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-red-600/30 to-slate-950 border border-red-500/50 text-red-400 flex items-center justify-center text-3xl shadow-xl flex-shrink-0">
          <i class="fas fa-spider"></i>
        </div>
        <div class="text-center sm:text-left flex-1">
          <div class="flex items-center justify-center sm:justify-start gap-2 flex-wrap mb-1">
            <span class="px-3 py-0.5 rounded-full text-[11px] font-extrabold uppercase tracking-wider bg-red-950/80 text-red-300 border border-red-500/30">
              🕷️ DESGLOSE TÉCNICO OFICIAL
            </span>
            <span class="text-xs text-slate-400 font-mono">ChatGPT + Seedance 2.0</span>
          </div>
          <h2 class="text-2xl sm:text-3xl font-extrabold text-white">
            Reel de Spiderman: "The Swing Prompts"
          </h2>
          <p class="text-xs sm:text-sm text-slate-300 mt-1">
            Por <strong>Edward Jiménez</strong> (<a href="https://www.instagram.com/edwardjimenezia/" target="_blank" rel="noopener" class="text-red-400 font-bold hover:underline">@edwardjimenezia</a>) · Agencia ProsperIA
          </p>
        </div>
        <a href="https://www.instagram.com/p/DdsN1nasM46/" target="_blank" rel="noopener" class="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold bg-pink-950/80 border border-pink-500/40 text-pink-300 hover:bg-pink-900/50 transition-colors flex-shrink-0">
          <i class="fab fa-instagram"></i> Ver Video en Instagram
        </a>
      </div>

      <p class="text-slate-300 text-xs sm:text-sm leading-relaxed mb-6">
        Aquí tienes el procedimiento de 3 pasos para recrear la transición del sujeto en la ventana lanzándose al vacío como Spiderman. <strong>Pícale a cada paso para desplegar su prompt</strong> traducido y listo para copiar en 1 clic:
      </p>

      <!-- Compact Clickable Accordion for the 3 Steps -->
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
          
          <div id="step-content-1" class="px-4 sm:px-6 pb-5 pt-1 border-t border-slate-800/80">
            <div class="flex items-center justify-between gap-2 mb-3 mt-3">
              <span class="text-xs text-slate-300 font-medium"><strong>Instrucción:</strong> Sube tu foto de frente (selfie) a ChatGPT y pega:</span>
              <button onclick="copyCode(document.getElementById('prompt-spiderman-1').innerText, this)" class="btn-copy px-3 py-1.5 rounded-lg text-xs font-bold inline-flex items-center gap-1.5 flex-shrink-0">
                <i class="far fa-copy"></i> Copiar Prompt
              </button>
            </div>
            <div id="prompt-spiderman-1" class="prompt-box p-4 select-all text-xs leading-relaxed max-h-72 overflow-y-auto">Referencia: Utiliza la imagen subida como referencia directa para la fisonomía del rostro, pero coloca al personaje como un hombre joven sentado en el alféizar de una ventana de piso a techo completamente abierta dentro de una acogedora habitación de Nueva York. La ventana está totalmente abierta y deja pasar una brisa natural. El sujeto se sienta con las piernas hacia el cuarto, postura relajada y confiada, mirando a la cámara con una sonrisa natural.

Vestuario: Chaqueta de cuero negro mate, camiseta blanca de algodón grueso, pantalones anchos negros oversize, zapatillas blancas Nike Air Force 1 impecables, y auriculares negros over-ear descansando alrededor del cuello.

Entorno: Habitación creativa en Manhattan con estantes llenos de cómics manga, libros de fotografía, equipo de cámaras y pósters de cine. Al fondo de la ventana abierta se observa el skyline de Manhattan en hora dorada (golden hour), con edificios de ladrillo y escaleras de incendio bañadas en luz cálida y suave bruma atmosférica.

Cámara & Estilo: Encuadre centrado a nivel de ojos, lente anamórfico de 35mm, grano orgánico de película estilo A24 y Kodak Vision3 250D, ultra-fotorrealista, 8K HDR, calidad fotográfica de revista.</div>
          </div>
        </div>

        <!-- Accordion Item 2 -->
        <div class="border border-slate-800 rounded-2xl bg-slate-950/80 overflow-hidden transition-all duration-200" id="accordion-item-2">
          <button type="button" onclick="toggleSpidermanStep(2)" class="w-full p-4 sm:p-5 flex items-center justify-between text-left hover:bg-slate-900/60 transition-colors">
            <div class="flex items-center gap-3">
              <span class="w-8 h-8 rounded-xl bg-red-950 border border-red-500/40 text-red-400 text-sm flex items-center justify-center font-bold flex-shrink-0">2</span>
              <div>
                <h4 class="text-sm sm:text-base font-bold text-white flex items-center gap-2">
                  <span>Paso 2: La Salida al Vacío</span>
                  <span class="px-2 py-0.5 rounded text-[10px] font-mono bg-red-950/60 text-red-300 border border-red-500/20">Seedance 2.0 / Kling</span>
                </h4>
                <p class="text-xs text-slate-400 mt-0.5">El sujeto se pone los audífonos y se deja caer hacia atrás con naturalidad.</p>
              </div>
            </div>
            <div class="flex items-center gap-3 flex-shrink-0 ml-2">
              <span class="text-xs text-red-400 hidden sm:inline font-mono">Pícale aquí</span>
              <i class="fas fa-chevron-down text-slate-400 transition-transform duration-300" id="chevron-2"></i>
            </div>
          </button>
          
          <div id="step-content-2" class="px-4 sm:px-6 pb-5 pt-1 border-t border-slate-800/80 hidden">
            <div class="flex items-center justify-between gap-2 mb-3 mt-3">
              <span class="text-xs text-slate-300 font-medium"><strong>Instrucción:</strong> Sube la imagen del Paso 1 a Seedance 2.0 (o Kling/Runway) y pega:</span>
              <button onclick="copyCode(document.getElementById('prompt-spiderman-2').innerText, this)" class="btn-copy px-3 py-1.5 rounded-lg text-xs font-bold inline-flex items-center gap-1.5 flex-shrink-0">
                <i class="far fa-copy"></i> Copiar Prompt
              </button>
            </div>
            <div id="prompt-spiderman-2" class="prompt-box p-4 select-all text-xs leading-relaxed max-h-72 overflow-y-auto">Reference: Use the uploaded image as the exact character reference. Preserve face, hairstyle, leather jacket, sneakers, headphones, and the NYC golden-hour open window.

Camera (Strict): Locked-off tripod shot. No movement, no pan, no tilt, no zoom. Maintain exact framing throughout.

Action: The man sits on the window ledge. Warm evening sunlight fills the room and a gentle breeze moves the curtains. He looks at the camera with a relaxed smile and says naturally: "Alright... let's do this one more time." He calmly lifts the headphones from his neck and places them over his ears, adjusting them with confidence. He then leans backward with complete trust as if pulled smoothly by an invisible superhero force, disappearing gracefully beyond the open window into the skyline. No distress, no panic, no danger. The curtains continue moving gently. Hold on the empty window for two seconds.

Look: Ultra photorealistic Hollywood comic-book film aesthetic, 8K HDR, natural fabric physics.</div>
          </div>
        </div>

        <!-- Accordion Item 3 -->
        <div class="border border-slate-800 rounded-2xl bg-slate-950/80 overflow-hidden transition-all duration-200" id="accordion-item-3">
          <button type="button" onclick="toggleSpidermanStep(3)" class="w-full p-4 sm:p-5 flex items-center justify-between text-left hover:bg-slate-900/60 transition-colors">
            <div class="flex items-center gap-3">
              <span class="w-8 h-8 rounded-xl bg-red-950 border border-red-500/40 text-red-400 text-sm flex items-center justify-center font-bold flex-shrink-0">3</span>
              <div>
                <h4 class="text-sm sm:text-base font-bold text-white flex items-center gap-2">
                  <span>Paso 3: Vuelo Continuo de 15s en Dron por Manhattan</span>
                  <span class="px-2 py-0.5 rounded text-[10px] font-mono bg-red-950/60 text-red-300 border border-red-500/20">Seedance 2.0 (Zero Cuts)</span>
                </h4>
                <p class="text-xs text-slate-400 mt-0.5">Toma continua sin cortes siguiendo las acrobacias aéreas entre taxis y rascacielos.</p>
              </div>
            </div>
            <div class="flex items-center gap-3 flex-shrink-0 ml-2">
              <span class="text-xs text-red-400 hidden sm:inline font-mono">Pícale aquí</span>
              <i class="fas fa-chevron-down text-slate-400 transition-transform duration-300" id="chevron-3"></i>
            </div>
          </button>
          
          <div id="step-content-3" class="px-4 sm:px-6 pb-5 pt-1 border-t border-slate-800/80 hidden">
            <div class="flex items-center justify-between gap-2 mb-3 mt-3">
              <span class="text-xs text-slate-300 font-medium"><strong>Instrucción:</strong> Con la misma imagen de referencia, genera la secuencia de acción continua de 15s:</span>
              <button onclick="copyCode(document.getElementById('prompt-spiderman-3').innerText, this)" class="btn-copy px-3 py-1.5 rounded-lg text-xs font-bold inline-flex items-center gap-1.5 flex-shrink-0">
                <i class="far fa-copy"></i> Copiar Prompt
              </button>
            </div>
            <div id="prompt-spiderman-3" class="prompt-box p-4 select-all text-xs leading-relaxed max-h-72 overflow-y-auto">15-second continuous drone-follow shot. ZERO CUTS. Real Hollywood film, RED Monstro 8K anamorphic lens.

Physics & Movement (Critical): Does NOT float. Interacts physically with the city. Feet push off walls, hands grab ledges. Clean acrobatic rope-swing athlete posture.
0–1s: Wrist snaps, web shoots, camera pulls back immediately.
1–4s: Swings LOW 3 meters above a residential street. White Air Force 1s skim the roof of a parked car, feet bounce off lightly to redirect momentum. Camera banks 40 degrees.
4–7s: Releases web at peak, runs 4 steps horizontally along a brick wall of a brownstone, then pushes off hard and fires a new web across an intersection.
7–10s: Comes LOW down a street packed with yellow taxis, runs 3 steps on wet pavement between cars. A taxi honks. He laughs with an adrenaline grin, kicks off a taxi roof and rockets HIGH shouting "WOOHOO!"
10–15s: Reaches peak altitude at rooftop level against a massive warm orange sunset sky. Hangs weightless for one breathless moment, arms slightly open, pure freedom. The frame holds as he begins to fall.</div>
          </div>
        </div>

      </div>

      <!-- Signature block -->
      <div class="p-4 rounded-xl bg-slate-900/80 border border-slate-800 flex items-center justify-between flex-wrap gap-3">
        <div class="text-xs text-slate-300">
          ¿Te gustó este desglose? Comparte tus resultados y etiquétame en Instagram: <strong class="text-red-400">@edwardjimenezia</strong>
        </div>
        <a href="https://chat.whatsapp.com/HIjs3Bytduy9ucOtn6jeKw?s=sh&p=a&ilr=4" target="_blank" rel="noopener" class="px-4 py-2 rounded-lg text-xs font-bold bg-emerald-500 text-slate-950 hover:bg-emerald-400 transition-colors inline-flex items-center gap-1.5">
          <i class="fab fa-whatsapp"></i> Preguntar en la Comunidad
        </a>
      </div>

    </div>
  </section>

  <!-- ════════════════════════════════════════════════════
       BLOQUE 2 (VALOR PRIMERO): 100 CÓDIGOS CREATIVOS DE CHATGPT
       ════════════════════════════════════════════════════ -->
  <main id="codigos-grid" class="py-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto relative z-10 scroll-mt-24">
    <div class="text-center max-w-3xl mx-auto mb-6">
      <span class="text-xs font-bold uppercase tracking-wider text-cyan-400 mb-2 block">Catálogo Interactivo y Buscador</span>
      <h2 class="text-2xl sm:text-4xl font-extrabold text-white mb-3">
        Explora los 100 Códigos y Cópialos con 1 Clic
      </h2>
      <p class="text-slate-300 text-xs sm:text-sm leading-relaxed">
        Filtra por nombre, categoría o efecto visual. Toca <strong>Copiar</strong> para pegarlo directamente en ChatGPT.
      </p>
    </div>


    <!-- Live Search Bar -->
    <div class="glass-panel p-4 sm:p-5 rounded-2xl mb-8 max-w-4xl mx-auto border-cyan-500/20">
      <div class="flex flex-col sm:flex-row gap-3 items-center">
        <div class="relative flex-1 w-full">
          <i class="fas fa-search absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 text-sm"></i>
          <input 
            type="text" 
            id="search-input" 
            placeholder="Buscar código: ej. /spotlight, packshot, neonnoir, 35mm, macro..." 
            class="w-full pl-11 pr-10 py-3 rounded-xl bg-slate-950/80 border border-slate-700 focus:border-cyan-400 focus:outline-none text-white text-sm placeholder-slate-500 transition-colors"
            oninput="handleSearch(this.value)"
          >
          <button id="clear-search" onclick="clearSearch()" class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 text-xs hidden">
            <i class="fas fa-times-circle text-base"></i>
          </button>
        </div>
        <div class="text-xs text-slate-400 font-mono whitespace-nowrap px-3 py-2 rounded-xl bg-slate-900 border border-slate-800">
          Mostrando: <strong id="visible-count" class="text-cyan-400">100</strong> de 100 códigos
        </div>
      </div>
    </div>

    <!-- Category Pills -->
    <div class="flex flex-wrap items-center justify-center gap-2 mb-10 max-w-5xl mx-auto" id="category-pills">
      {pills_str}
    </div>

    <div id="no-results" class="hidden text-center py-16 px-4 glass-panel rounded-3xl max-w-lg mx-auto">
      <h3 class="text-lg font-bold text-white mb-2">No encontramos ningún código coincidente</h3>
      <button onclick="clearSearch()" class="px-5 py-2 rounded-xl text-xs font-bold bg-cyan-400 text-slate-950 mt-4">
        Ver todos los 100 códigos
      </button>
    </div>

    <!-- Cards Collapsible Wrapper (Prevents eating up whole page) -->
    <div id="cards-wrapper" style="max-height: 720px; overflow: hidden;" class="relative transition-all duration-500">
      <div id="cards-container" class="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
{cards_str}
      </div>
      <div id="cards-fade-overlay" class="absolute bottom-0 left-0 right-0 h-48 bg-gradient-to-t from-slate-950 via-slate-950/95 to-transparent pointer-events-none flex items-end justify-center pb-4">
      </div>
    </div>

    <!-- Toggle Expansion Button -->
    <div class="text-center mt-6">
      <button id="btn-toggle-catalog" type="button" onclick="toggleCatalogExpansion()" class="inline-flex items-center gap-2 px-6 py-3.5 rounded-2xl font-bold text-xs sm:text-sm bg-gradient-to-r from-cyan-400 to-sky-400 text-slate-950 hover:from-cyan-300 hover:to-sky-300 transition-all shadow-[0_0_25px_rgba(0,229,255,0.35)] cursor-pointer">
        <i class="fas fa-chevron-down text-xs transition-transform duration-300" id="toggle-catalog-icon"></i>
        <span id="toggle-catalog-text">Desplegar Catálogo Completo (Ver los 100 Códigos)</span>
      </button>
      <p class="text-xs text-slate-400 mt-2">
        O utiliza el buscador o categorías arriba para ver resultados instantáneos.
      </p>
    </div>
  </main>

  <!-- ════════════════════════════════════════════════════
       BLOQUE 3: DESCARGAS OFICIALES DE LOS 2 PDFs (SIN VISOR IFRAME)
       ════════════════════════════════════════════════════ -->
  <section id="descargas" class="py-14 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto relative z-10 scroll-mt-24">
    
    <div class="text-center mb-10">
      <span class="text-xs font-bold uppercase tracking-wider text-cyan-400 mb-2 block">Documentos Oficiales en PDF</span>
      <h2 class="text-2xl sm:text-3xl font-extrabold text-white">Descarga las 2 Colecciones Completas</h2>
      <p class="text-slate-300 text-xs sm:text-sm max-w-2xl mx-auto mt-2 leading-relaxed">
        Tienes a tu disposición dos guías complementarias de alta resolución: el <strong>Archivo 1</strong> enfocado en prompts y comandos de texto para ChatGPT, y el <strong>Archivo 2</strong> enfocado en dirección visual y generación de imágenes profesionales.
      </p>
    </div>

    <div class="grid md:grid-cols-2 gap-6 max-w-5xl mx-auto mb-10">
      
      <!-- Card 1: Edición Guía Visual ProsperIA ES -->
      <div class="glass-panel p-6 sm:p-8 rounded-2xl relative overflow-hidden flex flex-col justify-between border-cyan-500/20 shadow-xl">
        <div>
          <div class="flex items-center justify-between mb-4">
            <span class="px-3 py-1 rounded-full text-xs font-bold bg-cyan-950 text-cyan-300 border border-cyan-500/30">
              <i class="far fa-file-pdf mr-1 text-red-400"></i> COLECCIÓN 1 · PROMPTS CHATGPT
            </span>
            <span class="text-xs text-slate-400 font-mono">3.7 MB • 12 PÁGINAS</span>
          </div>

          <h3 class="text-xl font-bold text-white mb-2">100 Códigos Creativos de ChatGPT</h3>
          <p class="text-slate-300 text-xs sm:text-sm leading-relaxed mb-6">
            <strong>Edición ProsperIA Dark (Prompts de Texto):</strong> Formato optimizado para memorizar y aplicar comandos de estructuración, guiones y lógica visual con la sintaxis recomendada <code class="text-cyan-400 font-mono">[/]</code>.
          </p>
        </div>

        <div class="pt-4 border-t border-slate-800">
          <a href="/static/codigos/ChatGPT_Codigos_Creativos_ProsperIA_ES.pdf" download="ChatGPT_Codigos_Creativos_ProsperIA_ES.pdf" class="w-full inline-flex items-center justify-center gap-2 px-5 py-3.5 rounded-xl font-bold text-sm bg-gradient-to-r from-cyan-400 to-cyan-500 text-slate-950 hover:from-cyan-300 hover:to-cyan-400 transition-all shadow-[0_0_15px_rgba(0,229,255,0.25)]">
            <i class="fas fa-download"></i> Descargar Colección 1 en PDF (3.7 MB)
          </a>
        </div>
      </div>

      <!-- Card 2: Edición Editorial Extendida -->
      <div class="glass-panel p-6 sm:p-8 rounded-2xl relative overflow-hidden flex flex-col justify-between border-indigo-500/20 shadow-xl">
        <div>
          <div class="flex items-center justify-between mb-4">
            <span class="px-3 py-1 rounded-full text-xs font-bold bg-indigo-950 text-indigo-300 border border-indigo-500/30">
              <i class="far fa-file-pdf mr-1 text-red-400"></i> COLECCIÓN 2 · FOTOGRAFÍA & IMÁGENES
            </span>
            <span class="text-xs text-slate-400 font-mono">5.3 MB • 12 PÁGINAS</span>
          </div>

          <h3 class="text-xl font-bold text-white mb-2">100 Códigos de Imágenes — Edward Jiménez</h3>
          <p class="text-slate-300 text-xs sm:text-sm leading-relaxed mb-6">
            <strong>Edición Editorial Extendida (Generación de Imágenes):</strong> Diagramación de máxima fidelidad con notas técnicas de dirección de arte, lentes anamórficos (35mm), chiaroscuro y fotografía editorial para marcas.
          </p>
        </div>

        <div class="pt-4 border-t border-slate-800">
          <a href="/static/codigos/Codigos_Creativos_ChatGPT_Edward_Jimenez_ES_ProsperIA.pdf" download="Codigos_Creativos_ChatGPT_Edward_Jimenez_ES_ProsperIA.pdf" class="w-full inline-flex items-center justify-center gap-2 px-5 py-3.5 rounded-xl font-bold text-sm bg-gradient-to-r from-indigo-500 to-cyan-400 text-slate-950 hover:from-indigo-400 hover:to-cyan-300 transition-all shadow-[0_0_15px_rgba(94,106,210,0.25)]">
            <i class="fas fa-download"></i> Descargar Colección 2 en PDF (5.3 MB)
          </a>
        </div>
      </div>

    </div>

    <!-- Google Drive Alternative -->
    <div class="text-center">
      <a href="https://drive.google.com/drive/folders/1tMekHUIAkG7-OLcorPOaz2wI2HOLWhrV?usp=sharing" target="_blank" rel="noopener" class="inline-flex items-center gap-2 text-xs sm:text-sm text-slate-400 hover:text-cyan-400 transition-colors py-2 px-4 rounded-xl bg-slate-900/60 border border-slate-800">
        <i class="fab fa-google-drive text-amber-400"></i> ¿Prefieres guardarlos en tu Drive? <strong>Abrir Carpeta en Google Drive</strong> <i class="fas fa-external-link-alt text-[10px]"></i>
      </a>
    </div>

  </section>

  <!-- ════════════════════════════════════════════════════
       BLOQUE 4: NUESTROS REELS PUBLICADOS Y RECURSOS PROMETIDOS
       ════════════════════════════════════════════════════ -->
  <section id="reels-gallery" class="py-14 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto relative z-10 scroll-mt-24">
    
    <div class="text-center max-w-3xl mx-auto mb-10">
      <span class="text-xs font-bold uppercase tracking-wider text-pink-400 mb-2 block">Casos de Estudio &amp; Videos Virales</span>
      <h2 class="text-2xl sm:text-4xl font-extrabold text-white">
        Nuestros Reels Publicados y sus Recursos Prometidos
      </h2>
      <p class="text-slate-300 text-xs sm:text-sm mt-2">
        Cada video que publicamos en Instagram y Facebook tiene su recurso correspondiente. Encuentra aquí el video que viste y obtén su material:
      </p>
    </div>

    <!-- Reels Grid with Photos & Strict PDF Download Buttons -->
    <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
      {reels_grid_str}
    </div>

    <div class="text-center">
      <a href="https://www.instagram.com/edwardjimenezia/" target="_blank" rel="noopener" class="inline-flex items-center gap-2 px-6 py-3 rounded-xl text-xs font-bold bg-pink-950/70 border border-pink-500/40 text-pink-300 hover:bg-pink-900/50 transition-colors">
        <i class="fab fa-instagram text-base"></i> Ver Todos los Reels en Instagram (@edwardjimenezia) <i class="fas fa-arrow-right text-[10px]"></i>
      </a>
    </div>

  </section>

  <!-- ════════════════════════════════════════════════════
       BLOQUE 5: PASSPORTAI BANNER (FREE TOKENS & OFFICIAL LOGO)
       ════════════════════════════════════════════════════ -->
  <section class="py-8 px-4 sm:px-6 lg:px-8 max-w-5xl mx-auto relative z-10">
    <div class="glass-panel p-5 sm:p-6 rounded-2xl border border-cyan-500/30 bg-gradient-to-r from-slate-950 via-slate-900/90 to-slate-950 flex flex-col md:flex-row items-center justify-between gap-5 shadow-[0_0_30px_rgba(0,229,255,0.08)]">
      
      <div class="flex items-center gap-4 text-left w-full md:w-auto">
        <div class="relative flex-shrink-0">
          <img src="{s_asset('passportai_logo_official.jpg')}" alt="PassportAI Logo" class="w-14 h-14 sm:w-16 sm:h-16 rounded-xl object-cover border border-cyan-400/40 shadow-[0_0_15px_rgba(0,229,255,0.25)]">
        </div>
        <div class="flex-1">
          <div class="flex items-center gap-2 flex-wrap mb-1">
            <span class="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
              🎁 Tokens de Cortesía + 5 Días Gratis
            </span>
            <span class="text-[11px] text-slate-400 font-mono">B2B Prospección IA</span>
          </div>
          <h3 class="text-base sm:text-lg font-bold text-white leading-tight">¿Haces prospección comercial? Prueba PassportAI</h3>
          <p class="text-xs text-slate-300 mt-1 leading-relaxed max-w-xl">
            Encuentra empresas, teléfonos y tomadores de decisión verificados en minutos. Regístrate y recibe tus tokens de cortesía para comenzar.
          </p>
        </div>
      </div>

      <div class="flex-shrink-0 w-full md:w-auto">
        <a href="https://passportai.app/register" target="_blank" rel="noopener" class="w-full md:w-auto inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl font-bold text-xs bg-gradient-to-r from-cyan-400 to-cyan-500 text-slate-950 hover:from-cyan-300 hover:to-cyan-400 transition-all shadow-[0_0_15px_rgba(0,229,255,0.3)]">
          <i class="fas fa-bolt"></i> <span>Registrarme Gratis</span> <i class="fas fa-external-link-alt text-[10px] ml-1"></i>
        </a>
      </div>

    </div>
  </section>

  <!-- ════════════════════════════════════════════════════
       BLOQUE 6: DIAGNÓSTICO INTERACTIVO DE NIVEL DE IA (REDISEÑADO & ATRACTIVO)
       ════════════════════════════════════════════════════ -->
  <!-- ════════════════════════════════════════════════════
       BLOQUE 6: DIAGNÓSTICO INTERACTIVO DE NIVEL DE IA (5 PREGUNTAS + FLECHAS + 3 NIVELES)
       ════════════════════════════════════════════════════ -->
  <section id="test-ia" class="py-16 px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto relative z-10 scroll-mt-24">
    
    <div class="text-center mb-8">
      <span class="inline-flex items-center gap-1.5 px-3.5 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-cyan-950/80 text-cyan-300 border border-cyan-400/40 mb-3">
        <i class="fas fa-brain text-cyan-400"></i> Diagnóstico Rápido en 2 Minutos
      </span>
      <h2 class="text-2xl sm:text-4xl font-extrabold text-white">
        ¿Cuál es tu Nivel Real de Conocimiento en IA?
      </h2>
      <p class="text-slate-300 text-xs sm:text-sm max-w-xl mx-auto mt-2 leading-relaxed">
        Responde 5 preguntas prácticas para evaluar tu madurez en prompts, generación de contenido y automatización. Descubre si estás en nivel <strong>Novato, Intermedio o Avanzado</strong> sin formularios obligatorios.
      </p>
    </div>

    <!-- Ultra-Attractive Interactive Box -->
    <div class="glass-panel p-6 sm:p-10 rounded-3xl border-2 border-cyan-500/30 relative shadow-[0_0_50px_rgba(0,229,255,0.12)] bg-gradient-to-b from-slate-950 via-slate-900/90 to-slate-950">
      
      <!-- Progress Bar & Indicator -->
      <div class="flex items-center justify-between text-xs text-slate-400 font-mono mb-3">
        <span id="quiz-step-indicator" class="text-cyan-400 font-bold">Pregunta 1 de 5</span>
        <span id="quiz-percent-indicator">20% Completado</span>
      </div>
      <div class="w-full bg-slate-950 rounded-full h-2.5 mb-8 overflow-hidden border border-slate-800">
        <div id="quiz-progress" class="bg-gradient-to-r from-cyan-400 via-sky-400 to-indigo-500 h-2.5 rounded-full transition-all duration-300 shadow-[0_0_12px_rgba(0,229,255,0.5)]" style="width: 20%;"></div>
      </div>

      <!-- Question 1 -->
      <div id="quiz-step-1" class="quiz-step">
        <div class="flex items-center gap-2 mb-2">
          <span class="w-6 h-6 rounded-md bg-cyan-950 border border-cyan-500/40 text-cyan-400 text-xs flex items-center justify-center font-bold">Q1</span>
          <span class="text-xs text-cyan-400 font-mono uppercase tracking-wider">Frecuencia y Productividad</span>
        </div>
        <h3 class="text-lg sm:text-xl font-bold text-white mb-5">¿Cómo utilizas la Inteligencia Artificial en tu día a día o trabajo?</h3>
        <div class="space-y-3">
          <button type="button" onclick="selectQuizOption(1, 10, 'A', this)" class="quiz-opt w-full p-4 rounded-xl text-left bg-slate-950/70 border border-slate-800 hover:border-cyan-400 hover:bg-slate-900/80 text-slate-300 hover:text-white transition-all text-xs sm:text-sm flex items-center justify-between group">
            <span>A. Solo de vez en cuando para redactar correos o consultas simples en ChatGPT.</span>
            <i class="quiz-opt-icon far fa-circle text-slate-600 group-hover:text-cyan-400 text-sm ml-3"></i>
          </button>
          <button type="button" onclick="selectQuizOption(1, 25, 'B', this)" class="quiz-opt w-full p-4 rounded-xl text-left bg-slate-950/70 border border-slate-800 hover:border-cyan-400 hover:bg-slate-900/80 text-slate-300 hover:text-white transition-all text-xs sm:text-sm flex items-center justify-between group">
            <span>B. A diario para generar ideas, estructurar guiones y organizar mi trabajo.</span>
            <i class="quiz-opt-icon far fa-circle text-slate-600 group-hover:text-cyan-400 text-sm ml-3"></i>
          </button>
          <button type="button" onclick="selectQuizOption(1, 40, 'C', this)" class="quiz-opt w-full p-4 rounded-xl text-left bg-slate-950/70 border border-slate-800 hover:border-cyan-400 hover:bg-slate-900/80 text-slate-300 hover:text-white transition-all text-xs sm:text-sm flex items-center justify-between group">
            <span>C. Genero imágenes, videos y prompts estructurados para redes sociales con regularidad.</span>
            <i class="quiz-opt-icon far fa-circle text-slate-600 group-hover:text-cyan-400 text-sm ml-3"></i>
          </button>
          <button type="button" onclick="selectQuizOption(1, 50, 'D', this)" class="quiz-opt w-full p-4 rounded-xl text-left bg-slate-950/70 border border-slate-800 hover:border-cyan-400 hover:bg-slate-900/80 text-slate-300 hover:text-white transition-all text-xs sm:text-sm flex items-center justify-between group">
            <span>D. Tengo flujos de trabajo conectados a APIs, CRMs, Make/n8n o agentes autónomos.</span>
            <i class="quiz-opt-icon far fa-circle text-slate-600 group-hover:text-cyan-400 text-sm ml-3"></i>
          </button>
        </div>

        <!-- Arrows Navigation -->
        <div class="flex items-center justify-between pt-6 mt-6 border-t border-slate-800/80">
          <button type="button" disabled class="px-4 py-2.5 rounded-xl text-xs font-semibold text-slate-600 border border-slate-800 opacity-40 cursor-not-allowed flex items-center gap-2">
            <i class="fas fa-arrow-left text-[11px]"></i> Anterior
          </button>
          <div class="flex items-center gap-1.5">
            <span class="quiz-dot-1 w-2.5 h-2.5 rounded-full bg-cyan-400"></span>
            <span class="quiz-dot-2 w-2.5 h-2.5 rounded-full bg-slate-800"></span>
            <span class="quiz-dot-3 w-2.5 h-2.5 rounded-full bg-slate-800"></span>
            <span class="quiz-dot-4 w-2.5 h-2.5 rounded-full bg-slate-800"></span>
            <span class="quiz-dot-5 w-2.5 h-2.5 rounded-full bg-slate-800"></span>
          </div>
          <button type="button" id="btn-next-1" onclick="nextQuizStep()" disabled class="px-4 py-2.5 rounded-xl text-xs font-bold text-cyan-400 border border-cyan-500/40 bg-cyan-950/40 opacity-40 cursor-not-allowed hover:bg-cyan-500 hover:text-slate-950 transition-all flex items-center gap-2">
            Siguiente <i class="fas fa-arrow-right text-[11px]"></i>
          </button>
        </div>
      </div>

      <!-- Question 2 -->
      <div id="quiz-step-2" class="quiz-step hidden">
        <div class="flex items-center gap-2 mb-2">
          <span class="w-6 h-6 rounded-md bg-cyan-950 border border-cyan-500/40 text-cyan-400 text-xs flex items-center justify-center font-bold">Q2</span>
          <span class="text-xs text-cyan-400 font-mono uppercase tracking-wider">Ingeniería de Prompts</span>
        </div>
        <h3 class="text-lg sm:text-xl font-bold text-white mb-5">¿Cómo formulas tus prompts cuando buscas un resultado de calidad?</h3>
        <div class="space-y-3">
          <button type="button" onclick="selectQuizOption(2, 10, 'A', this)" class="quiz-opt w-full p-4 rounded-xl text-left bg-slate-950/70 border border-slate-800 hover:border-cyan-400 hover:bg-slate-900/80 text-slate-300 hover:text-white transition-all text-xs sm:text-sm flex items-center justify-between group">
            <span>A. Escribo descripciones breves y espero que la IA adivine lo que busco.</span>
            <i class="quiz-opt-icon far fa-circle text-slate-600 group-hover:text-cyan-400 text-sm ml-3"></i>
          </button>
          <button type="button" onclick="selectQuizOption(2, 25, 'B', this)" class="quiz-opt w-full p-4 rounded-xl text-left bg-slate-950/70 border border-slate-800 hover:border-cyan-400 hover:bg-slate-900/80 text-slate-300 hover:text-white transition-all text-xs sm:text-sm flex items-center justify-between group">
            <span>B. Uso palabras clave genéricas como "sé profesional, 8k, hiperrealista y detallado".</span>
            <i class="quiz-opt-icon far fa-circle text-slate-600 group-hover:text-cyan-400 text-sm ml-3"></i>
          </button>
          <button type="button" onclick="selectQuizOption(2, 40, 'C', this)" class="quiz-opt w-full p-4 rounded-xl text-left bg-slate-950/70 border border-slate-800 hover:border-cyan-400 hover:bg-slate-900/80 text-slate-300 hover:text-white transition-all text-xs sm:text-sm flex items-center justify-between group">
            <span>C. Aplico parámetros de lentes (35mm), iluminación controlada, composición y sintaxis estructurada.</span>
            <i class="quiz-opt-icon far fa-circle text-slate-600 group-hover:text-cyan-400 text-sm ml-3"></i>
          </button>
          <button type="button" onclick="selectQuizOption(2, 50, 'D', this)" class="quiz-opt w-full p-4 rounded-xl text-left bg-slate-950/70 border border-slate-800 hover:border-cyan-400 hover:bg-slate-900/80 text-slate-300 hover:text-white transition-all text-xs sm:text-sm flex items-center justify-between group">
            <span>D. Domino consistencia multi-escena, meta-prompts con variables y directivas físicas de movimiento.</span>
            <i class="quiz-opt-icon far fa-circle text-slate-600 group-hover:text-cyan-400 text-sm ml-3"></i>
          </button>
        </div>

        <!-- Arrows Navigation -->
        <div class="flex items-center justify-between pt-6 mt-6 border-t border-slate-800/80">
          <button type="button" onclick="prevQuizStep()" class="px-4 py-2.5 rounded-xl text-xs font-semibold text-slate-300 border border-slate-700 bg-slate-900/60 hover:text-white hover:border-cyan-400 transition-all flex items-center gap-2">
            <i class="fas fa-arrow-left text-[11px]"></i> Anterior
          </button>
          <div class="flex items-center gap-1.5">
            <span class="quiz-dot-1 w-2.5 h-2.5 rounded-full bg-cyan-400"></span>
            <span class="quiz-dot-2 w-2.5 h-2.5 rounded-full bg-cyan-400"></span>
            <span class="quiz-dot-3 w-2.5 h-2.5 rounded-full bg-slate-800"></span>
            <span class="quiz-dot-4 w-2.5 h-2.5 rounded-full bg-slate-800"></span>
            <span class="quiz-dot-5 w-2.5 h-2.5 rounded-full bg-slate-800"></span>
          </div>
          <button type="button" id="btn-next-2" onclick="nextQuizStep()" disabled class="px-4 py-2.5 rounded-xl text-xs font-bold text-cyan-400 border border-cyan-500/40 bg-cyan-950/40 opacity-40 cursor-not-allowed hover:bg-cyan-500 hover:text-slate-950 transition-all flex items-center gap-2">
            Siguiente <i class="fas fa-arrow-right text-[11px]"></i>
          </button>
        </div>
      </div>

      <!-- Question 3 -->
      <div id="quiz-step-3" class="quiz-step hidden">
        <div class="flex items-center gap-2 mb-2">
          <span class="w-6 h-6 rounded-md bg-cyan-950 border border-cyan-500/40 text-cyan-400 text-xs flex items-center justify-center font-bold">Q3</span>
          <span class="text-xs text-cyan-400 font-mono uppercase tracking-wider">Multimedia &amp; Video</span>
        </div>
        <h3 class="text-lg sm:text-xl font-bold text-white mb-5">¿Qué experiencia tienes generando imágenes o video cinemático con IA?</h3>
        <div class="space-y-3">
          <button type="button" onclick="selectQuizOption(3, 10, 'A', this)" class="quiz-opt w-full p-4 rounded-xl text-left bg-slate-950/70 border border-slate-800 hover:border-cyan-400 hover:bg-slate-900/80 text-slate-300 hover:text-white transition-all text-xs sm:text-sm flex items-center justify-between group">
            <span>A. Ninguna o muy poca; solo he probado herramientas básicas sin control técnico.</span>
            <i class="quiz-opt-icon far fa-circle text-slate-600 group-hover:text-cyan-400 text-sm ml-3"></i>
          </button>
          <button type="button" onclick="selectQuizOption(3, 25, 'B', this)" class="quiz-opt w-full p-4 rounded-xl text-left bg-slate-950/70 border border-slate-800 hover:border-cyan-400 hover:bg-slate-900/80 text-slate-300 hover:text-white transition-all text-xs sm:text-sm flex items-center justify-between group">
            <span>B. He probado generadores estándar como DALL-E en ChatGPT o Canva Magic.</span>
            <i class="quiz-opt-icon far fa-circle text-slate-600 group-hover:text-cyan-400 text-sm ml-3"></i>
          </button>
          <button type="button" onclick="selectQuizOption(3, 40, 'C', this)" class="quiz-opt w-full p-4 rounded-xl text-left bg-slate-950/70 border border-slate-800 hover:border-cyan-400 hover:bg-slate-900/80 text-slate-300 hover:text-white transition-all text-xs sm:text-sm flex items-center justify-between group">
            <span>C. Domino parámetros avanzados en Midjourney o Seedance (iluminación, ángulos, chiaroscuro).</span>
            <i class="quiz-opt-icon far fa-circle text-slate-600 group-hover:text-cyan-400 text-sm ml-3"></i>
          </button>
          <button type="button" onclick="selectQuizOption(3, 50, 'D', this)" class="quiz-opt w-full p-4 rounded-xl text-left bg-slate-950/70 border border-slate-800 hover:border-cyan-400 hover:bg-slate-900/80 text-slate-300 hover:text-white transition-all text-xs sm:text-sm flex items-center justify-between group">
            <span>D. Produzco videos generativos cinematográficos completos con audio y consistencia (Kling, Runway, Seedance 2.0).</span>
            <i class="quiz-opt-icon far fa-circle text-slate-600 group-hover:text-cyan-400 text-sm ml-3"></i>
          </button>
        </div>

        <!-- Arrows Navigation -->
        <div class="flex items-center justify-between pt-6 mt-6 border-t border-slate-800/80">
          <button type="button" onclick="prevQuizStep()" class="px-4 py-2.5 rounded-xl text-xs font-semibold text-slate-300 border border-slate-700 bg-slate-900/60 hover:text-white hover:border-cyan-400 transition-all flex items-center gap-2">
            <i class="fas fa-arrow-left text-[11px]"></i> Anterior
          </button>
          <div class="flex items-center gap-1.5">
            <span class="quiz-dot-1 w-2.5 h-2.5 rounded-full bg-cyan-400"></span>
            <span class="quiz-dot-2 w-2.5 h-2.5 rounded-full bg-cyan-400"></span>
            <span class="quiz-dot-3 w-2.5 h-2.5 rounded-full bg-cyan-400"></span>
            <span class="quiz-dot-4 w-2.5 h-2.5 rounded-full bg-slate-800"></span>
            <span class="quiz-dot-5 w-2.5 h-2.5 rounded-full bg-slate-800"></span>
          </div>
          <button type="button" id="btn-next-3" onclick="nextQuizStep()" disabled class="px-4 py-2.5 rounded-xl text-xs font-bold text-cyan-400 border border-cyan-500/40 bg-cyan-950/40 opacity-40 cursor-not-allowed hover:bg-cyan-500 hover:text-slate-950 transition-all flex items-center gap-2">
            Siguiente <i class="fas fa-arrow-right text-[11px]"></i>
          </button>
        </div>
      </div>

      <!-- Question 4 -->
      <div id="quiz-step-4" class="quiz-step hidden">
        <div class="flex items-center gap-2 mb-2">
          <span class="w-6 h-6 rounded-md bg-cyan-950 border border-cyan-500/40 text-cyan-400 text-xs flex items-center justify-center font-bold">Q4</span>
          <span class="text-xs text-cyan-400 font-mono uppercase tracking-wider">Automatización &amp; Conexiones</span>
        </div>
        <h3 class="text-lg sm:text-xl font-bold text-white mb-5">¿Has conectado la IA con tus procesos o herramientas de trabajo?</h3>
        <div class="space-y-3">
          <button type="button" onclick="selectQuizOption(4, 10, 'A', this)" class="quiz-opt w-full p-4 rounded-xl text-left bg-slate-950/70 border border-slate-800 hover:border-cyan-400 hover:bg-slate-900/80 text-slate-300 hover:text-white transition-all text-xs sm:text-sm flex items-center justify-between group">
            <span>A. No, todo lo que hago es copiar y pegar manualmente entre aplicaciones.</span>
            <i class="quiz-opt-icon far fa-circle text-slate-600 group-hover:text-cyan-400 text-sm ml-3"></i>
          </button>
          <button type="button" onclick="selectQuizOption(4, 25, 'B', this)" class="quiz-opt w-full p-4 rounded-xl text-left bg-slate-950/70 border border-slate-800 hover:border-cyan-400 hover:bg-slate-900/80 text-slate-300 hover:text-white transition-all text-xs sm:text-sm flex items-center justify-between group">
            <span>B. Uso GPTs personalizados o proyectos guardados dentro de ChatGPT o Claude.</span>
            <i class="quiz-opt-icon far fa-circle text-slate-600 group-hover:text-cyan-400 text-sm ml-3"></i>
          </button>
          <button type="button" onclick="selectQuizOption(4, 40, 'C', this)" class="quiz-opt w-full p-4 rounded-xl text-left bg-slate-950/70 border border-slate-800 hover:border-cyan-400 hover:bg-slate-900/80 text-slate-300 hover:text-white transition-all text-xs sm:text-sm flex items-center justify-between group">
            <span>C. He integrado flujos sencillos con Make, Zapier, Notion o Webhooks.</span>
            <i class="quiz-opt-icon far fa-circle text-slate-600 group-hover:text-cyan-400 text-sm ml-3"></i>
          </button>
          <button type="button" onclick="selectQuizOption(4, 50, 'D', this)" class="quiz-opt w-full p-4 rounded-xl text-left bg-slate-950/70 border border-slate-800 hover:border-cyan-400 hover:bg-slate-900/80 text-slate-300 hover:text-white transition-all text-xs sm:text-sm flex items-center justify-between group">
            <span>D. Tengo agentes de WhatsApp o prospección B2B conectados a CRM y bases de datos (PassportAI).</span>
            <i class="quiz-opt-icon far fa-circle text-slate-600 group-hover:text-cyan-400 text-sm ml-3"></i>
          </button>
        </div>

        <!-- Arrows Navigation -->
        <div class="flex items-center justify-between pt-6 mt-6 border-t border-slate-800/80">
          <button type="button" onclick="prevQuizStep()" class="px-4 py-2.5 rounded-xl text-xs font-semibold text-slate-300 border border-slate-700 bg-slate-900/60 hover:text-white hover:border-cyan-400 transition-all flex items-center gap-2">
            <i class="fas fa-arrow-left text-[11px]"></i> Anterior
          </button>
          <div class="flex items-center gap-1.5">
            <span class="quiz-dot-1 w-2.5 h-2.5 rounded-full bg-cyan-400"></span>
            <span class="quiz-dot-2 w-2.5 h-2.5 rounded-full bg-cyan-400"></span>
            <span class="quiz-dot-3 w-2.5 h-2.5 rounded-full bg-cyan-400"></span>
            <span class="quiz-dot-4 w-2.5 h-2.5 rounded-full bg-cyan-400"></span>
            <span class="quiz-dot-5 w-2.5 h-2.5 rounded-full bg-slate-800"></span>
          </div>
          <button type="button" id="btn-next-4" onclick="nextQuizStep()" disabled class="px-4 py-2.5 rounded-xl text-xs font-bold text-cyan-400 border border-cyan-500/40 bg-cyan-950/40 opacity-40 cursor-not-allowed hover:bg-cyan-500 hover:text-slate-950 transition-all flex items-center gap-2">
            Siguiente <i class="fas fa-arrow-right text-[11px]"></i>
          </button>
        </div>
      </div>

      <!-- Question 5 -->
      <div id="quiz-step-5" class="quiz-step hidden">
        <div class="flex items-center gap-2 mb-2">
          <span class="w-6 h-6 rounded-md bg-cyan-950 border border-cyan-500/40 text-cyan-400 text-xs flex items-center justify-center font-bold">Q5</span>
          <span class="text-xs text-cyan-400 font-mono uppercase tracking-wider">Estrategia Comercial &amp; ROI</span>
        </div>
        <h3 class="text-lg sm:text-xl font-bold text-white mb-5">¿Cuál es el impacto real de la Inteligencia Artificial en tus ingresos o negocio?</h3>
        <div class="space-y-3">
          <button type="button" onclick="selectQuizOption(5, 10, 'A', this)" class="quiz-opt w-full p-4 rounded-xl text-left bg-slate-950/70 border border-slate-800 hover:border-cyan-400 hover:bg-slate-900/80 text-slate-300 hover:text-white transition-all text-xs sm:text-sm flex items-center justify-between group">
            <span>A. Aún es un pasatiempo o curiosidad; no genera ingresos directos para mí.</span>
            <i class="quiz-opt-icon far fa-circle text-slate-600 group-hover:text-cyan-400 text-sm ml-3"></i>
          </button>
          <button type="button" onclick="selectQuizOption(5, 25, 'B', this)" class="quiz-opt w-full p-4 rounded-xl text-left bg-slate-950/70 border border-slate-800 hover:border-cyan-400 hover:bg-slate-900/80 text-slate-300 hover:text-white transition-all text-xs sm:text-sm flex items-center justify-between group">
            <span>B. Me ahorra algunas horas a la semana pero no tengo una estrategia comercial definida.</span>
            <i class="quiz-opt-icon far fa-circle text-slate-600 group-hover:text-cyan-400 text-sm ml-3"></i>
          </button>
          <button type="button" onclick="selectQuizOption(5, 40, 'C', this)" class="quiz-opt w-full p-4 rounded-xl text-left bg-slate-950/70 border border-slate-800 hover:border-cyan-400 hover:bg-slate-900/80 text-slate-300 hover:text-white transition-all text-xs sm:text-sm flex items-center justify-between group">
            <span>C. Es el motor principal para crear contenido visual y atraer prospectos a mi marca.</span>
            <i class="quiz-opt-icon far fa-circle text-slate-600 group-hover:text-cyan-400 text-sm ml-3"></i>
          </button>
          <button type="button" onclick="selectQuizOption(5, 50, 'D', this)" class="quiz-opt w-full p-4 rounded-xl text-left bg-slate-950/70 border border-slate-800 hover:border-cyan-400 hover:bg-slate-900/80 text-slate-300 hover:text-white transition-all text-xs sm:text-sm flex items-center justify-between group">
            <span>D. Es la base de un sistema predecible de prospección, captación y ventas automáticas.</span>
            <i class="quiz-opt-icon far fa-circle text-slate-600 group-hover:text-cyan-400 text-sm ml-3"></i>
          </button>
        </div>

        <!-- Arrows Navigation -->
        <div class="flex items-center justify-between pt-6 mt-6 border-t border-slate-800/80">
          <button type="button" onclick="prevQuizStep()" class="px-4 py-2.5 rounded-xl text-xs font-semibold text-slate-300 border border-slate-700 bg-slate-900/60 hover:text-white hover:border-cyan-400 transition-all flex items-center gap-2">
            <i class="fas fa-arrow-left text-[11px]"></i> Anterior
          </button>
          <div class="flex items-center gap-1.5">
            <span class="quiz-dot-1 w-2.5 h-2.5 rounded-full bg-cyan-400"></span>
            <span class="quiz-dot-2 w-2.5 h-2.5 rounded-full bg-cyan-400"></span>
            <span class="quiz-dot-3 w-2.5 h-2.5 rounded-full bg-cyan-400"></span>
            <span class="quiz-dot-4 w-2.5 h-2.5 rounded-full bg-cyan-400"></span>
            <span class="quiz-dot-5 w-2.5 h-2.5 rounded-full bg-cyan-400"></span>
          </div>
          <button type="button" id="btn-next-5" onclick="calculateQuizResult()" disabled class="px-5 py-2.5 rounded-xl text-xs font-bold text-slate-950 bg-gradient-to-r from-cyan-400 to-indigo-400 opacity-40 cursor-not-allowed hover:from-cyan-300 hover:to-indigo-300 transition-all flex items-center gap-2 shadow-[0_0_15px_rgba(0,229,255,0.3)]">
            Ver Mi Resultado <i class="fas fa-bolt text-[11px]"></i>
          </button>
        </div>
      </div>

      <!-- Result Screen (Direct, Zero Forms, 3 Tiers + Community WhatsApp Invitation) -->
      <div id="quiz-result" class="quiz-step hidden text-center">
        
        <span class="px-4 py-1.5 rounded-full text-xs font-extrabold uppercase tracking-wider inline-block mb-3 border bg-cyan-950 text-cyan-300 border-cyan-500/40" id="result-badge">
          NIVEL IDENTIFICADO
        </span>
        
        <h3 class="text-2xl sm:text-3xl font-extrabold text-white mb-2" id="result-title">
          Nivel Intermedio: Creador Visual y Proactivo
        </h3>
        
        <div class="inline-block px-3 py-1 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono text-cyan-400 mb-4" id="result-score-tag">
          Puntaje Obtenido: 145 / 250 Puntos
        </div>

        <p class="text-slate-300 text-xs sm:text-sm max-w-xl mx-auto mb-6 leading-relaxed" id="result-desc">
          Tienes buen manejo de herramientas de generación de contenido, pero aún trabajas de forma manual. Tu siguiente salto es dominar prompts cinemáticos y automatizar la distribución.
        </p>

        <!-- Roadmap recommendations -->
        <div class="p-6 rounded-2xl bg-slate-950/90 border border-slate-800 text-left max-w-xl mx-auto mb-8 shadow-inner">
          <h4 class="text-xs font-bold uppercase tracking-wider text-cyan-400 mb-3.5 flex items-center gap-1.5">
            <i class="fas fa-route"></i> Tu Hoja de Ruta Inmediata Recomendada:
          </h4>
          <ul class="space-y-2.5 text-xs text-slate-300">
            <li class="flex items-start gap-2.5">
              <i class="fas fa-check-circle text-cyan-400 mt-0.5 text-sm flex-shrink-0"></i> 
              <span id="result-step-1">Aplica los 100 Códigos Creativos de ChatGPT para pulir la iluminación de tus tomas.</span>
            </li>
            <li class="flex items-start gap-2.5">
              <i class="fas fa-check-circle text-cyan-400 mt-0.5 text-sm flex-shrink-0"></i> 
              <span id="result-step-2">Implementa la fórmula del Reel de Spiderman para video continuo en Seedance 2.0.</span>
            </li>
            <li class="flex items-start gap-2.5">
              <i class="fas fa-check-circle text-cyan-400 mt-0.5 text-sm flex-shrink-0"></i> 
              <span id="result-step-3">Únete a la comunidad oficial de WhatsApp para recibir casos de estudio semanales.</span>
            </li>
          </ul>
        </div>

        <!-- Community WhatsApp Invitation Box (Requested by User) -->
        <div class="p-6 sm:p-8 rounded-2xl bg-gradient-to-r from-emerald-950/70 via-slate-950 to-slate-950 border border-emerald-500/40 text-center max-w-xl mx-auto shadow-2xl mb-6">
          <div class="w-14 h-14 rounded-2xl bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 text-2xl mx-auto mb-3 shadow-[0_0_20px_rgba(16,185,129,0.3)]">
            <i class="fab fa-whatsapp"></i>
          </div>
          <h4 class="text-lg sm:text-xl font-extrabold text-white mb-2">
            ¿Quieres aprender más de IA y dominar estas herramientas?
          </h4>
          <p class="text-xs sm:text-sm text-slate-300 mb-6 leading-relaxed max-w-md mx-auto">
            Únete a nuestra comunidad oficial y gratuita de WhatsApp donde te enseñaremos a usar la IA paso a paso, compartimos prompts diarios y analizamos casos reales de éxito.
          </p>
          <div class="flex flex-col sm:flex-row items-center justify-center gap-3">
            <a href="https://chat.whatsapp.com/HIjs3Bytduy9ucOtn6jeKw?s=sh&p=a&ilr=4" target="_blank" rel="noopener" class="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl font-bold text-sm bg-emerald-400 text-slate-950 hover:bg-emerald-300 transition-all shadow-[0_0_20px_rgba(16,185,129,0.35)]">
              <i class="fab fa-whatsapp text-lg"></i> Unirme Gratis a la Comunidad
            </a>
            <button type="button" onclick="restartQuiz()" class="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-4 py-3.5 rounded-xl font-medium text-xs text-slate-400 hover:text-white bg-slate-900 border border-slate-700 transition-colors">
              <i class="fas fa-redo-alt text-[10px]"></i> Repetir Test
            </button>
          </div>
        </div>

        <div class="text-center">
          <a href="#codigos-grid" class="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-cyan-400 transition-colors">
            <i class="fas fa-arrow-up text-[10px]"></i> Volver a Explorar los 100 Códigos
          </a>
        </div>

      </div>

    </div>
  </section>

  <!-- ════════════════════════════════════════════════════
       BLOQUE 7: CARTA DE VENTAS: 2 CAMINOS & 2 CUADROS DE COTIZACIÓN
       ════════════════════════════════════════════════════ -->
  <section id="carta-ventas" class="py-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto relative z-10 scroll-mt-24">
    <div class="glass-panel p-8 sm:p-14 rounded-3xl border-indigo-500/30 relative overflow-hidden bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 shadow-2xl">
      <div class="absolute -top-32 -left-32 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none"></div>

      <div class="max-w-3xl mx-auto text-center mb-14">
        <span class="px-3.5 py-1 rounded-full text-xs font-bold bg-indigo-950 text-indigo-300 border border-indigo-500/40 uppercase tracking-wider mb-4 inline-block">
          <i class="fas fa-handshake mr-1"></i> Dos Formas de Crecer con Nosotros
        </span>
        <h2 class="text-2xl sm:text-4xl font-extrabold text-white mb-4">
          Puedes Aprender Solo con Todos Estos Ejemplos...<br>
          <span class="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-sky-300">
            O Dejar que la Agencia ProsperIA lo Haga por Ti.
          </span>
        </h2>
        <p class="text-slate-300 text-sm sm:text-base leading-relaxed">
          Ya viste que nuestros videos superan <strong>+450K reproducciones</strong> y atraen miles de prospectos calificados cada mes. Si tienes el tiempo de experimentar y montar los sistemas tú mismo, aprovecha todo nuestro material gratuito. Pero si eres dueño de empresa y buscas velocidad de ejecución, ponemos a tu disposición nuestras dos modalidades de servicio:
        </p>
      </div>

      <!-- 2 Quotation Cards Grid -->
      <div class="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto mb-12">
        
        <!-- Cuadro 1: Creación de Contenido Viral -->
        <div class="p-8 rounded-3xl bg-slate-950/80 border-2 border-cyan-500/30 hover:border-cyan-400 transition-all flex flex-col justify-between relative shadow-xl">
          <div class="absolute top-0 right-0 transform translate-x-2 -translate-y-2">
            <span class="px-3 py-1 rounded-full text-[10px] font-extrabold uppercase tracking-wider bg-cyan-400 text-slate-950 shadow">
              OPCIÓN 1
            </span>
          </div>

          <div>
            <div class="w-12 h-12 rounded-2xl bg-cyan-950 border border-cyan-400/40 text-cyan-400 flex items-center justify-center text-xl mb-4">
              <i class="fas fa-video"></i>
            </div>
            <h3 class="text-xl font-bold text-white mb-2">Hacemos Este Mismo Contenido para Tu Negocio</h3>
            <p class="text-xs sm:text-sm text-slate-300 leading-relaxed mb-6">
              Producción integral de Reels y videos cortos con IA diseñados para detener el scroll, posicionar tu marca como referente de autoridad y disparar tu alcance orgánico.
            </p>

            <ul class="space-y-3 text-xs sm:text-sm text-slate-300 mb-8">
              <li class="flex items-start gap-2.5">
                <i class="fas fa-check-circle text-cyan-400 mt-1"></i>
                <span><strong>Guiones de Alta Retención:</strong> Ganchos psicológicos probados en los primeros 3 segundos.</span>
              </li>
              <li class="flex items-start gap-2.5">
                <i class="fas fa-check-circle text-cyan-400 mt-1"></i>
                <span><strong>Generación Visual con IA:</strong> Prompts de Hollywood, efectos visuales tipo Spiderman y dirección de arte.</span>
              </li>
              <li class="flex items-start gap-2.5">
                <i class="fas fa-check-circle text-cyan-400 mt-1"></i>
                <span><strong>Edición Cinematográfica 9:16:</strong> Subtítulos cinéticos, música y sonido de estudio listos para publicar.</span>
              </li>
              <li class="flex items-start gap-2.5">
                <i class="fas fa-check-circle text-cyan-400 mt-1"></i>
                <span><strong>Llamados a la Acción Estratégicos:</strong> Transformamos vistas en seguidores y mensajes directos.</span>
              </li>
            </ul>
          </div>

          <button type="button" onclick="selectCotizacionOption('contenido')" class="w-full py-3.5 rounded-xl font-bold text-xs bg-cyan-500/20 text-cyan-300 border border-cyan-400/40 hover:bg-cyan-400 hover:text-slate-950 transition-all flex items-center justify-center gap-2">
            <i class="fas fa-check-circle"></i> Elegir Opción 1: Contenido Viral
          </button>
        </div>

        <!-- Cuadro 2: Administración Integral 360° -->
        <div class="p-8 rounded-3xl bg-slate-950/80 border-2 border-indigo-500/40 hover:border-indigo-400 transition-all flex flex-col justify-between relative shadow-xl">
          <div class="absolute top-0 right-0 transform translate-x-2 -translate-y-2">
            <span class="px-3 py-1 rounded-full text-[10px] font-extrabold uppercase tracking-wider bg-indigo-500 text-white shadow">
              OPCIÓN 2 · RECOMENDADO
            </span>
          </div>

          <div>
            <div class="w-12 h-12 rounded-2xl bg-indigo-950 border border-indigo-400/40 text-indigo-400 flex items-center justify-center text-xl mb-4">
              <i class="fas fa-chart-line"></i>
            </div>
            <h3 class="text-xl font-bold text-white mb-2">Administración Integral 360° (Contenido + Tráfico + CRM)</h3>
            <p class="text-xs sm:text-sm text-slate-300 leading-relaxed mb-6">
              Nos convertimos en el brazo de crecimiento y adquisición de tu empresa: desde la producción audiovisual hasta el cierre comercial de clientes en WhatsApp.
            </p>

            <ul class="space-y-3 text-xs sm:text-sm text-slate-300 mb-8">
              <li class="flex items-start gap-2.5">
                <i class="fas fa-check-circle text-indigo-400 mt-1"></i>
                <span><strong>Administración &amp; Publicación:</strong> Gestión de tus canales (Instagram, Facebook, YouTube, LinkedIn).</span>
              </li>
              <li class="flex items-start gap-2.5">
                <i class="fas fa-check-circle text-indigo-400 mt-1"></i>
                <span><strong>Campañas de Tráfico Pago:</strong> Anuncios en Meta Ads y Google Ads para escalar las vistas virales a prospectos.</span>
              </li>
              <li class="flex items-start gap-2.5">
                <i class="fas fa-check-circle text-indigo-400 mt-1"></i>
                <span><strong>Infraestructura CRM &amp; WhatsApp:</strong> Automatización para responder en segundos y agendar citas.</span>
              </li>
              <li class="flex items-start gap-2.5">
                <i class="fas fa-check-circle text-indigo-400 mt-1"></i>
                <span><strong>Acompañamiento Estratégico:</strong> Dirección directa con Edward Jiménez para optimizar tu embudo comercial.</span>
              </li>
            </ul>
          </div>

          <button type="button" onclick="selectCotizacionOption('integral')" class="w-full py-3.5 rounded-xl font-bold text-xs bg-gradient-to-r from-indigo-500 to-cyan-400 text-slate-950 hover:from-indigo-400 hover:to-cyan-300 transition-all shadow-[0_0_20px_rgba(94,106,210,0.3)] flex items-center justify-center gap-2">
            <i class="fas fa-rocket"></i> Elegir Opción 2: Sistema 360°
          </button>
        </div>

      </div>

      <!-- Formulario Pequeño de Cotización Directa (Sin Modales) -->
      <div id="formulario-cotizacion" class="glass-panel p-6 sm:p-8 rounded-3xl border-2 border-cyan-500/30 max-w-xl mx-auto mb-12 bg-slate-950/90 shadow-2xl relative scroll-mt-28">
        <div class="text-center mb-6">
          <span class="px-3 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider bg-cyan-950 text-cyan-300 border border-cyan-500/30 inline-block mb-2">
            Respuesta en menos de 2 horas
          </span>
          <h3 class="text-xl sm:text-2xl font-extrabold text-white">Solicitar Cotización de Servicio</h3>
          <p class="text-xs text-slate-300 mt-1">Déjanos tus datos básicos y coordinamos una propuesta a la medida de tu empresa.</p>
        </div>

        <form id="direct-cotizacion-form" onsubmit="submitCotizacionDirect(event)" class="space-y-4 text-left">
          
          <!-- Selector de modalidad -->
          <div>
            <label class="block text-xs font-semibold text-slate-300 mb-1.5">¿Qué modalidad te interesa? *</label>
            <div class="grid grid-cols-2 gap-2 text-xs">
              <label class="flex items-center gap-2 p-3 rounded-xl bg-slate-900/90 border border-slate-700 cursor-pointer hover:border-cyan-400 transition-colors" id="label-opt-contenido">
                <input type="radio" name="servicio_opcion" value="contenido" checked class="text-cyan-400 focus:ring-0">
                <span class="text-slate-200 font-medium text-[11px] sm:text-xs">1. Contenido Viral</span>
              </label>
              <label class="flex items-center gap-2 p-3 rounded-xl bg-slate-900/90 border border-slate-700 cursor-pointer hover:border-indigo-400 transition-colors" id="label-opt-integral">
                <input type="radio" name="servicio_opcion" value="integral" class="text-indigo-400 focus:ring-0">
                <span class="text-slate-200 font-medium text-[11px] sm:text-xs">2. Sistema 360°</span>
              </label>
            </div>
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-300 mb-1">Nombre Completo *</label>
            <input type="text" id="direct-name" required placeholder="Ej. Carlos Mendoza" class="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-700 text-white text-sm focus:border-cyan-400 focus:outline-none">
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-300 mb-1">Correo Electrónico *</label>
            <input type="email" id="direct-email" required placeholder="tu@empresa.com" class="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-700 text-white text-sm focus:border-cyan-400 focus:outline-none">
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-300 mb-1">WhatsApp (con código de país) *</label>
            <input type="tel" id="direct-phone" required placeholder="+1 786 555 0199" class="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-700 text-white text-sm focus:border-cyan-400 focus:outline-none">
          </div>

          <button type="submit" id="btn-submit-direct" class="w-full py-4 rounded-xl font-bold text-sm bg-gradient-to-r from-cyan-400 via-sky-400 to-indigo-500 text-slate-950 hover:from-cyan-300 hover:to-indigo-400 transition-all shadow-[0_0_25px_rgba(0,229,255,0.3)] flex items-center justify-center gap-2 mt-2">
            <i class="fab fa-whatsapp text-base"></i> Solicitar Cotización Inmediata
          </button>
          
          <p class="text-[11px] text-slate-500 text-center">Tus datos están protegidos. Sin spam. Te contactamos directamente por WhatsApp.</p>
        </form>
      </div>

      <!-- WhatsApp Community Card -->
      <div class="p-6 sm:p-8 rounded-2xl bg-gradient-to-r from-emerald-950/80 via-slate-950 to-slate-950 border border-emerald-500/40 flex flex-col md:flex-row items-center justify-between gap-6 max-w-5xl mx-auto">
        <div class="flex items-center gap-4">
          <div class="w-14 h-14 rounded-2xl bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 text-2xl flex-shrink-0">
            <i class="fab fa-whatsapp"></i>
          </div>
          <div>
            <span class="text-xs font-bold text-emerald-400 uppercase tracking-wider block mb-0.5">Comunidad Oficial y Networking</span>
            <h4 class="text-lg sm:text-xl font-bold text-white">¿Quieres hacer preguntas y aprender con otros creadores?</h4>
            <p class="text-xs text-slate-300 mt-0.5">Únete a nuestro grupo oficial de WhatsApp donde compartimos prompts, novedades y sesiones en vivo.</p>
          </div>
        </div>
        <div class="flex-shrink-0 w-full md:w-auto">
          <a href="https://chat.whatsapp.com/HIjs3Bytduy9ucOtn6jeKw?s=sh&p=a&ilr=4" target="_blank" rel="noopener" class="w-full md:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl font-bold text-sm bg-emerald-400 text-slate-950 hover:bg-emerald-300 transition-all shadow-[0_0_20px_rgba(16,185,129,0.3)]">
            <i class="fab fa-whatsapp text-lg"></i> Unirme Gratis al WhatsApp
          </a>
        </div>
      </div>

    </div>
  </section>

  <!-- ════════════════════════════════════════════════════
       FOOTER
       ════════════════════════════════════════════════════ -->
  <footer class="bg-black border-t border-slate-800 text-slate-400 text-xs py-14 px-4 sm:px-6 lg:px-8 relative z-10">
    <div class="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-10 mb-10">
      
      <!-- Col 1: Brand -->
      <div>
        <img src="{s_asset('logo_prosper_ia_cropped.jpg')}" alt="AGENCIA PROSPERIA LLC" class="h-10 object-contain rounded mb-4">
        <p class="text-xs leading-relaxed text-slate-400 mb-4 font-light">
          Agencia ProsperIA LLC. Conectamos inteligencia artificial, producción audiovisual de impacto y automatización comercial para acelerar el crecimiento de empresas y marcas.
        </p>
        <div class="flex gap-4 text-base">
          <a href="https://www.instagram.com/edwardjimenezia/" target="_blank" rel="noopener" class="text-slate-400 hover:text-cyan-400 transition-colors" title="Instagram"><i class="fab fa-instagram"></i></a>
          <a href="https://www.linkedin.com/in/edwardjimenezia/" target="_blank" rel="noopener" class="text-slate-400 hover:text-cyan-400 transition-colors" title="LinkedIn"><i class="fab fa-linkedin-in"></i></a>
          <a href="https://www.youtube.com/@AgenciaProsper_IA" target="_blank" rel="noopener" class="text-slate-400 hover:text-cyan-400 transition-colors" title="YouTube"><i class="fab fa-youtube"></i></a>
          <a href="https://www.facebook.com/AgenciaProsperarIA/" target="_blank" rel="noopener" class="text-slate-400 hover:text-cyan-400 transition-colors" title="Facebook"><i class="fab fa-facebook-f"></i></a>
        </div>
      </div>

      <!-- Col 2: Enlaces Rápidos -->
      <div>
        <h4 class="text-white font-bold text-xs uppercase tracking-wider mb-4 text-cyan-400">Recursos de la Página</h4>
        <ul class="space-y-2.5">
          <li><a href="#spiderman-breakdown" class="hover:text-white transition-colors">Prompt Reel Spiderman</a></li>
          <li><a href="#codigos-grid" class="hover:text-white transition-colors">100 Códigos Creativos</a></li>
          <li><a href="#descargas" class="hover:text-white transition-colors">Descargas PDF Oficiales</a></li>
          <li><a href="#reels-gallery" class="hover:text-white transition-colors">Galería de Nuestros Reels</a></li>
          <li><a href="#test-ia" class="hover:text-white transition-colors">Test de Nivel de IA</a></li>
          <li><a href="https://chat.whatsapp.com/HIjs3Bytduy9ucOtn6jeKw?s=sh&p=a&ilr=4" target="_blank" rel="noopener" class="text-emerald-400 hover:underline">Comunidad Oficial WhatsApp</a></li>
        </ul>
      </div>

      <!-- Col 3: Soluciones -->
      <div>
        <h4 class="text-white font-bold text-xs uppercase tracking-wider mb-4 text-cyan-400">Soluciones de Negocio</h4>
        <ul class="space-y-2.5">
          <li><a href="#carta-ventas" class="hover:text-white transition-colors">Creación de Contenido Viral</a></li>
          <li><a href="#carta-ventas" class="hover:text-white transition-colors">Administración Integral 360°</a></li>
          <li><a href="https://passportai.app/register" target="_blank" rel="noopener" class="hover:text-white transition-colors">PassportAI (Tokens Gratis)</a></li>
          <li><a href="/diagnostico" class="hover:text-white transition-colors">Diagnóstico Comercial (3 min)</a></li>
        </ul>
      </div>

      <!-- Col 4: Contacto Oficial -->
      <div>
        <h4 class="text-white font-bold text-xs uppercase tracking-wider mb-4 text-cyan-400">Contacto Directo</h4>
        <ul class="space-y-2.5 leading-relaxed font-light">
          <li><strong>Sede:</strong> Miami, Florida, USA</li>
          <li><strong>Liderazgo:</strong> Edward Jiménez (@edwardjimenezia)</li>
          <li><strong>Email:</strong> <a href="mailto:edward@agenciaprosperia.com" class="hover:text-white transition-colors">edward@agenciaprosperia.com</a></li>
          <li><strong>WhatsApp:</strong> <a href="https://wa.me/17865573119" target="_blank" rel="noopener" class="text-emerald-400 hover:underline">+1 (786) 557-3119</a></li>
        </ul>
      </div>

    </div>

    <div class="border-t border-slate-900 pt-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-slate-500 font-light">
      <p>© 2026 Agencia ProsperIA LLC. Todos los derechos reservados.</p>
      <div class="flex gap-4">
        <a href="/politica-privacidad" class="hover:text-slate-400 transition-colors">Privacidad</a>
        <a href="/terminos-servicio" class="hover:text-slate-400 transition-colors">Términos</a>
      </div>
    </div>
  </footer>

  <!-- ════════════════════════════════════════════════════
       CLIENT-SIDE SCRIPTS
       ════════════════════════════════════════════════════ -->
  <script>
    // Navigation jumps
    function jumpToSpiderman() {{
      document.getElementById('spiderman-breakdown').scrollIntoView({{ behavior: 'smooth' }});
    }}
    function jumpToDownloads() {{
      document.getElementById('descargas').scrollIntoView({{ behavior: 'smooth' }});
    }}

    // Spiderman Accordion Toggle
    function toggleSpidermanStep(stepNum) {{
      const content = document.getElementById('step-content-' + stepNum);
      const chevron = document.getElementById('chevron-' + stepNum);
      const item = document.getElementById('accordion-item-' + stepNum);
      
      const isHidden = content.classList.contains('hidden');
      if (isHidden) {{
        content.classList.remove('hidden');
        chevron.classList.add('rotate-180');
        item.classList.add('border-red-500/40');
      }} else {{
        content.classList.add('hidden');
        chevron.classList.remove('rotate-180');
        item.classList.remove('border-red-500/40');
      }}
    }}

    // AI Quiz Logic (5 Steps with Navigation Arrows & 3 Tiers: Novato, Intermedio, Avanzado)
    let currentQuizStep = 1;
    let quizAnswers = {{}};
    let quizAutoAdvanceTimer = null;

    function selectQuizOption(step, score, optionLetter, btn) {{
      if (quizAutoAdvanceTimer) clearTimeout(quizAutoAdvanceTimer);

      quizAnswers[step] = {{ score: score, option: optionLetter }};

      // Highlight selected button inside the current step
      const stepEl = document.getElementById('quiz-step-' + step);
      if (stepEl) {{
        stepEl.querySelectorAll('.quiz-opt').forEach(opt => {{
          opt.classList.remove('border-cyan-400', 'bg-cyan-950/60', 'text-white', 'shadow-[0_0_15px_rgba(0,229,255,0.2)]');
          opt.classList.add('border-slate-800', 'bg-slate-950/70', 'text-slate-300');
          const icon = opt.querySelector('.quiz-opt-icon');
          if (icon) {{
            icon.className = 'quiz-opt-icon far fa-circle text-slate-600 text-sm ml-3';
          }}
        }});
      }}

      btn.classList.remove('border-slate-800', 'bg-slate-950/70', 'text-slate-300');
      btn.classList.add('border-cyan-400', 'bg-cyan-950/60', 'text-white', 'shadow-[0_0_15px_rgba(0,229,255,0.2)]');
      const activeIcon = btn.querySelector('.quiz-opt-icon');
      if (activeIcon) {{
        activeIcon.className = 'quiz-opt-icon fas fa-check-circle text-cyan-400 text-sm ml-3';
      }}

      // Enable next button for this step
      const nextBtn = document.getElementById('btn-next-' + step);
      if (nextBtn) {{
        nextBtn.removeAttribute('disabled');
        nextBtn.classList.remove('opacity-40', 'cursor-not-allowed');
      }}

      // Auto advance smoothly after 380ms
      quizAutoAdvanceTimer = setTimeout(() => {{
        if (step < 5) {{
          goToQuizStep(step + 1);
        }} else {{
          calculateQuizResult();
        }}
      }}, 380);
    }}

    function goToQuizStep(step) {{
      if (step < 1 || step > 5) return;
      currentQuizStep = step;

      // Hide all steps
      for (let i = 1; i <= 5; i++) {{
        const el = document.getElementById('quiz-step-' + i);
        if (el) el.classList.add('hidden');
      }}
      const resultEl = document.getElementById('quiz-result');
      if (resultEl) resultEl.classList.add('hidden');

      // Show current step
      const currentEl = document.getElementById('quiz-step-' + step);
      if (currentEl) currentEl.classList.remove('hidden');

      // Update progress
      const percent = step * 20;
      document.getElementById('quiz-progress').style.width = percent + '%';
      document.getElementById('quiz-step-indicator').textContent = 'Pregunta ' + step + ' de 5';
      document.getElementById('quiz-percent-indicator').textContent = percent + '% Completado';

      // Update dots
      for (let i = 1; i <= 5; i++) {{
        document.querySelectorAll('.quiz-dot-' + i).forEach(dot => {{
          if (i <= step) {{
            dot.classList.remove('bg-slate-800');
            dot.classList.add('bg-cyan-400');
          }} else {{
            dot.classList.remove('bg-cyan-400');
            dot.classList.add('bg-slate-800');
          }}
        }});
      }}

      // If already answered, enable next button
      const nextBtn = document.getElementById('btn-next-' + step);
      if (nextBtn) {{
        if (quizAnswers[step]) {{
          nextBtn.removeAttribute('disabled');
          nextBtn.classList.remove('opacity-40', 'cursor-not-allowed');
        }} else {{
          nextBtn.setAttribute('disabled', 'true');
          nextBtn.classList.add('opacity-40', 'cursor-not-allowed');
        }}
      }}
    }}

    function prevQuizStep() {{
      if (currentQuizStep > 1) {{
        goToQuizStep(currentQuizStep - 1);
      }}
    }}

    function nextQuizStep() {{
      if (quizAnswers[currentQuizStep]) {{
        if (currentQuizStep < 5) {{
          goToQuizStep(currentQuizStep + 1);
        }} else {{
          calculateQuizResult();
        }}
      }}
    }}

    function calculateQuizResult() {{
      const totalScore = Object.values(quizAnswers).reduce((acc, curr) => acc + curr.score, 0);

      // Hide questions
      for (let i = 1; i <= 5; i++) {{
        const el = document.getElementById('quiz-step-' + i);
        if (el) el.classList.add('hidden');
      }}

      // Progress bar 100%
      document.getElementById('quiz-progress').style.width = '100%';
      document.getElementById('quiz-step-indicator').textContent = 'Diagnóstico Completado';
      document.getElementById('quiz-percent-indicator').textContent = '100%';

      let badgeText = '';
      let badgeClass = '';
      let title = '';
      let desc = '';
      let step1 = '';
      let step2 = '';
      let step3 = '';

      if (totalScore <= 110) {{
        // NOVATO
        badgeText = '🌱 NIVEL IDENTIFICADO: NOVATO';
        badgeClass = 'bg-emerald-950/80 text-emerald-300 border-emerald-500/40 shadow-[0_0_15px_rgba(16,185,129,0.25)]';
        title = 'Nivel Novato: Explorador de Inteligencia Artificial';
        desc = 'Estás dando tus primeros pasos y descubriendo el potencial de la tecnología. Usas la IA de forma ocasional o como buscador. Tu mayor oportunidad es reemplazar prompts improvisados por comandos estructurados para ahorrar horas de trabajo y evitar respuestas genéricas.';
        step1 = 'Aplica los 100 Códigos Creativos de ChatGPT para crear prompts profesionales sin inventar la rueda.';
        step2 = 'Practica la fórmula de estructuración [/] para guiones, resúmenes y generación de ideas.';
        step3 = 'Únete a nuestra comunidad de WhatsApp para aprender trucos semanales y consultar dudas en vivo.';
      }} else if (totalScore <= 185) {{
        // INTERMEDIO
        badgeText = '⚡ NIVEL IDENTIFICADO: INTERMEDIO';
        badgeClass = 'bg-amber-950/80 text-amber-300 border-amber-500/40 shadow-[0_0_15px_rgba(245,158,11,0.25)]';
        title = 'Nivel Intermedio: Creador Visual y Proactivo';
        desc = 'Tienes un dominio notable de herramientas creativas y comprendes la lógica de los prompts. Creas contenido con buena estética, pero aún dependes de procesos manuales y te falta conectar tu contenido con prospección y automatizaciones de venta.';
        step1 = 'Implementa la directiva del Reel de Spiderman para video cinemático continuo y multi-escena.';
        step2 = 'Estandariza tus plantillas de carruseles y guiones con ganchos psicológicos de alta retención.';
        step3 = 'Conecta tu contenido con llamados a la acción comerciales y automatización de respuestas en WhatsApp.';
      }} else {{
        // AVANZADO
        badgeText = '🚀 NIVEL IDENTIFICADO: AVANZADO';
        badgeClass = 'bg-indigo-950/80 text-cyan-300 border-cyan-400/50 shadow-[0_0_20px_rgba(0,229,255,0.35)]';
        title = 'Nivel Avanzado: Arquitecto Comercial de IA';
        desc = 'Dominas herramientas de vanguardia, entiendes el impacto de los sistemas en el flujo de caja y conectas la IA con objetivos de facturación. Tu prioridad no es hacer prompts manuales, sino sistematizar flujos, desplegar agentes autónomos y delegar la ejecución técnica.';
        step1 = 'Despliega agentes AI SDR en WhatsApp con respuestas en menos de 15 segundos y calificación automática.';
        step2 = 'Implementa prospección B2B masiva y enriquecimiento de datos de empresas con PassportAI.';
        step3 = 'Escala la pauta publicitaria (Meta Ads / YouTube Ads) apalancada en creativos visuales de IA.';
      }}

      // Set DOM elements
      const badgeEl = document.getElementById('result-badge');
      badgeEl.textContent = badgeText;
      badgeEl.className = 'px-4 py-1.5 rounded-full text-xs font-extrabold uppercase tracking-wider inline-block mb-3 border ' + badgeClass;

      document.getElementById('result-title').textContent = title;
      document.getElementById('result-desc').textContent = desc;
      document.getElementById('result-score-tag').textContent = `Puntaje Obtenido: ${{totalScore}} / 250 Puntos`;

      document.getElementById('result-step-1').textContent = step1;
      document.getElementById('result-step-2').textContent = step2;
      document.getElementById('result-step-3').textContent = step3;

      const resultBox = document.getElementById('quiz-result');
      resultBox.classList.remove('hidden');
      resultBox.scrollIntoView({{ behavior: 'smooth' }});
    }}

    function restartQuiz() {{
      quizAnswers = {{}};
      currentQuizStep = 1;
      document.querySelectorAll('.quiz-opt').forEach(opt => {{
        opt.classList.remove('border-cyan-400', 'bg-cyan-950/60', 'text-white', 'shadow-[0_0_15px_rgba(0,229,255,0.2)]');
        opt.classList.add('border-slate-800', 'bg-slate-950/70', 'text-slate-300');
        const icon = opt.querySelector('.quiz-opt-icon');
        if (icon) {{
          icon.className = 'quiz-opt-icon far fa-circle text-slate-600 text-sm ml-3';
        }}
      }});
      goToQuizStep(1);
      document.getElementById('test-ia').scrollIntoView({{ behavior: 'smooth' }});
    }}

    // Direct Quotation Form Logic (No Modals)
    function selectCotizacionOption(opcion) {{
      const radio = document.querySelector(`input[name="servicio_opcion"][value="${{opcion}}"]`);
      if (radio) {{
        radio.checked = true;
      }}
      const formSection = document.getElementById('formulario-cotizacion');
      if (formSection) {{
        formSection.scrollIntoView({{ behavior: 'smooth' }});
        const nameInput = document.getElementById('direct-name');
        if (nameInput) setTimeout(() => nameInput.focus(), 500);
      }}
    }}

    async function submitCotizacionDirect(e) {{
      e.preventDefault();
      const selectedRadio = document.querySelector('input[name="servicio_opcion"]:checked');
      const servicio = selectedRadio ? selectedRadio.value : 'general';
      const name = document.getElementById('direct-name').value;
      const email = document.getElementById('direct-email').value;
      const phone = document.getElementById('direct-phone').value;
      const btn = document.getElementById('btn-submit-direct');

      btn.disabled = true;
      btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-1"></i> Enviando Solicitud...';

      const servicioLabel = servicio === 'contenido' ? 'Opción 1: Creación de Contenido Viral' : 'Opción 2: Sistema 360° Integral';

      try {{
        await fetch('/api/auth/contact', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            name: name,
            email: email,
            phone: phone,
            source: 'cotizacion_directa_' + servicio,
            message: `[COTIZACIÓN DIRECTA] Modalidad solicitada: ${{servicioLabel}}. WhatsApp: ${{phone}}. Email: ${{email}}`
          }})
        }});
      }} catch (err) {{
        console.warn('Lead capture notification error (cached locally):', err);
      }}

      btn.innerHTML = '<i class="fas fa-check mr-1"></i> ¡Solicitud Enviada!';
      btn.classList.remove('from-cyan-400', 'to-indigo-500');
      btn.classList.add('bg-emerald-500', 'text-slate-950');

      const waMsg = `Hola Edward, soy ${{name}}. Acabo de solicitar cotización para ${{servicioLabel}} desde la página de códigos. Mi correo es ${{email}} y mi WhatsApp es ${{phone}}.`;

      setTimeout(() => {{
        window.open(`https://wa.me/17865573119?text=${{encodeURIComponent(waMsg)}}`, '_blank');
        btn.innerHTML = '<i class="fab fa-whatsapp mr-1"></i> Abriendo WhatsApp...';
      }}, 1000);
    }}

    // Collapsible Catalog (100 Codes) Logic
    let isCatalogExpanded = false;

    function toggleCatalogExpansion() {{
      const wrapper = document.getElementById('cards-wrapper');
      const fade = document.getElementById('cards-fade-overlay');
      const text = document.getElementById('toggle-catalog-text');
      const icon = document.getElementById('toggle-catalog-icon');

      isCatalogExpanded = !isCatalogExpanded;

      if (isCatalogExpanded) {{
        if (wrapper) {{
          wrapper.style.maxHeight = 'none';
          wrapper.style.overflow = 'visible';
        }}
        if (fade) fade.classList.add('hidden');
        if (text) text.textContent = 'Colapsar Catálogo (Ver Menos)';
        if (icon) icon.classList.add('rotate-180');
      }} else {{
        if (wrapper) {{
          wrapper.style.maxHeight = '720px';
          wrapper.style.overflow = 'hidden';
        }}
        if (fade) fade.classList.remove('hidden');
        if (text) text.textContent = 'Desplegar Catálogo Completo (Ver los 100 Códigos)';
        if (icon) icon.classList.remove('rotate-180');
        document.getElementById('codigos-grid').scrollIntoView({{ behavior: 'smooth' }});
      }}
    }}

    // Filter & Search Logic for 100 codes
    let activeCat = 'all';
    let currentSearchTerm = '';
    const cards = Array.from(document.querySelectorAll('.code-card'));
    const visibleCountEl = document.getElementById('visible-count');
    const noResultsEl = document.getElementById('no-results');
    const cardsContainer = document.getElementById('cards-container');
    const searchInput = document.getElementById('search-input');
    const clearSearchBtn = document.getElementById('clear-search');

    function applyFilters() {{
      let visible = 0;
      const term = currentSearchTerm.toLowerCase().trim();

      // Auto-expand when searching or filtering so all results are visible
      if (term.length > 0 || activeCat !== 'all') {{
        if (!isCatalogExpanded) {{
          const wrapper = document.getElementById('cards-wrapper');
          const fade = document.getElementById('cards-fade-overlay');
          const text = document.getElementById('toggle-catalog-text');
          const icon = document.getElementById('toggle-catalog-icon');
          if (wrapper) {{
            wrapper.style.maxHeight = 'none';
            wrapper.style.overflow = 'visible';
          }}
          if (fade) fade.classList.add('hidden');
          if (text) text.textContent = 'Colapsar Catálogo (Ver Menos)';
          if (icon) icon.classList.add('rotate-180');
          isCatalogExpanded = true;
        }}
      }}

      cards.forEach(card => {{
        const cardCat = card.getAttribute('data-category');
        const cardSearch = card.getAttribute('data-search') || '';

        const matchesCat = (activeCat === 'all' || cardCat === activeCat);
        const matchesSearch = (!term || cardSearch.includes(term));

        if (matchesCat && matchesSearch) {{
          card.style.display = 'flex';
          visible++;
        }} else {{
          card.style.display = 'none';
        }}
      }});

      visibleCountEl.textContent = visible;

      if (visible === 0) {{
        noResultsEl.classList.remove('hidden');
        cardsContainer.classList.add('hidden');
      }} else {{
        noResultsEl.classList.add('hidden');
        cardsContainer.classList.remove('hidden');
      }}
    }}

    function filterCategory(catId, btn) {{
      activeCat = catId;
      document.querySelectorAll('.filter-chip').forEach(b => b.classList.remove('active'));
      if (btn) btn.classList.add('active');
      applyFilters();
      document.getElementById('codigos-grid').scrollIntoView({{ behavior: 'smooth' }});
    }}

    function handleSearch(val) {{
      currentSearchTerm = val;
      if (val.length > 0) {{
        clearSearchBtn.classList.remove('hidden');
      }} else {{
        clearSearchBtn.classList.add('hidden');
      }}
      applyFilters();
    }}

    function clearSearch() {{
      searchInput.value = '';
      currentSearchTerm = '';
      clearSearchBtn.classList.add('hidden');
      applyFilters();
      searchInput.focus();
    }}

    // 1-Click Clipboard Copier
    async function copyCode(text, btn) {{
      try {{
        await navigator.clipboard.writeText(text);
        const originalHtml = btn.innerHTML;
        btn.classList.add('copied');
        btn.innerHTML = '<i class="fas fa-check text-xs"></i> <span>¡Copiado!</span>';
        setTimeout(() => {{
          btn.classList.remove('copied');
          btn.innerHTML = originalHtml;
        }}, 1800);
      }} catch (err) {{
        const temp = document.createElement('textarea');
        temp.value = text;
        document.body.appendChild(temp);
        temp.select();
        document.execCommand('copy');
        document.body.removeChild(temp);
        btn.classList.add('copied');
        btn.innerHTML = '<i class="fas fa-check text-xs"></i> <span>¡Copiado!</span>';
        setTimeout(() => {{
          btn.classList.remove('copied');
          btn.innerHTML = originalHtml;
        }}, 1800);
      }}
    }}

    async function copyFullPrompt(promptText, btn) {{
      try {{
        await navigator.clipboard.writeText(promptText);
        const icon = btn.querySelector('i');
        icon.className = 'fas fa-check text-emerald-400';
        setTimeout(() => {{
          icon.className = 'fas fa-magic text-[11px]';
        }}, 1800);
      }} catch (e) {{}}
    }}
  </script>

</body>
</html>
'''

# Generate static version
static_html = generate_page(is_template=False)
with open('static/codigos/index.html', 'w', encoding='utf-8') as f:
    f.write(static_html)
print('Generated static/codigos/index.html')

# Generate template version
template_html = generate_page(is_template=True)
with open('scratch/template_codigos.html', 'w', encoding='utf-8') as f:
    f.write(template_html)
print('Generated scratch/template_codigos.html')

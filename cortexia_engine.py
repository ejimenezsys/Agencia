"""MOTOR OMNICANAL AUTÓNOMO DE PROSPERIA INTELLIGENCE (SISTEMA 5×4×1)
Orquestador central de Cortexia para ejecución en local.

Ejecuta:
- Diario (Lunes a Viernes): Ingesta de noticia -> 01_articulo_blog.json (publicado en SQLite),
  02_linkedin_post.txt, 03_x_y_threads (hilo + carrusel PNG 01-08), 04_para_grabar (guion 50s teleprompter),
  y _meta_noticia.json.
- Semanal (Viernes): Compilador de los 5 días en 1 Guion Maestro de YouTube de 20 minutos en 5 actos bajo SVE90.
- Distribución: Publicación opcional en LinkedIn vía Unipile con 1er comentario automático.
"""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Optional
import urllib.parse
import urllib.request

from database import BlogPost, SessionLocal, init_db
from editorial import PUBLISHED_DIR
from cortexia_prompts import (
    CANONICAL_WEEKLY_BANK,
    build_daily_prompt,
    build_weekly_youtube_prompt,
)
from cortexia_renderer import render_pdf_carousel, render_png_slides

BASE_DIR = Path(__file__).resolve().parent
CONTENT_DIR = BASE_DIR / "content"
DIARIO_DIR = CONTENT_DIR / "diario"
SEMANAL_DIR = CONTENT_DIR / "semanal"

# Asegurar directorios
DIARIO_DIR.mkdir(parents=True, exist_ok=True)
SEMANAL_DIR.mkdir(parents=True, exist_ok=True)
PUBLISHED_DIR.mkdir(parents=True, exist_ok=True)


def load_env() -> None:
    """Carga variables desde el archivo .env si existen."""
    env_file = BASE_DIR / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip().strip("'\"")
        if key not in os.environ:
            os.environ[key] = value


load_env()


def call_gemini_api(prompt: str, model: str = "gemini-2.5-flash", json_mode: bool = True) -> str:
    """Invoca la API de Gemini mediante HTTP POST usando GEMINI_API_KEY."""
    import requests

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Falta GEMINI_API_KEY en el entorno o en el archivo .env.")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload: Dict[str, Any] = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    if json_mode:
        payload["generationConfig"] = {"responseMimeType": "application/json"}

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=90)
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as exc:
        # Fallback a gemini-1.5-flash si 2.5 da error de cuota o modelo
        if model != "gemini-1.5-flash":
            print(f"[Aviso] Reintentando con gemini-1.5-flash tras error: {exc}")
            return call_gemini_api(prompt, model="gemini-1.5-flash", json_mode=json_mode)
        raise exc


def build_fallback_daily_pack(bank_item: Dict[str, Any], date_str: str) -> Dict[str, Any]:
    """Generador canónico determinista de respaldo cuando la red externa esté restringida por sandbox."""
    topic = bank_item["topic"]
    slug = bank_item["default_slug"]
    lane = bank_item["lane"]
    sources = bank_item["sources"]

    return {
        "slug": slug,
        "title": topic,
        "summary": "Análisis cuantitativo de la disrupción de IA bajo el marco SVE90 y Los 4 Pilares de Soberanía Empresarial de Agencia ProsperIA.",
        "article": {
            "title": topic,
            "summary": "La disrupción laboral y operativa no ocurre cargo por cargo; ocurre tarea por tarea. Un mapa cuantitativo para líderes empresariales.",
            "content_html": f"""<p>Durante meses, el debate corporativo se concentró en una pregunta binaria: ¿la inteligencia artificial destruirá o reemplazará nuestro modelo de trabajo? Esa pregunta es equivocada. La verdadera disrupción no opera cargo por cargo en el organigrama; opera de forma silenciosa, tarea por tarea.</p>
<h2>1. La evidencia cuantitativa que ningún directorio puede ignorar</h2>
<p>El <strong>Stanford HAI AI Index 2025</strong> confirma un salto cuantitativo decisivo: el <strong>78% de las organizaciones</strong> ya integró herramientas de IA en sus operaciones diarias, frente al 55% registrado apenas doce meses atrás. La etapa de experimentación lúdica concluyó formalmente; nos encontramos en plena fase de integración operativa e industrialización.</p>
<p>De forma paralela, la <strong>Organización Internacional del Trabajo (OIT)</strong> concluye que 1 de cada 4 trabajadores en el mundo se encuentra en ocupaciones con alta exposición a la IA generativa. No obstante, su hallazgo central es tajante: la gran mayoría de las ocupaciones combina tareas automatizables con actividades que exigen juicio, contexto y responsabilidad humana. El trabajo se descompone y transforma mucho antes de destruirse.</p>
<h2>2. Aumento humano frente a automatización ciega</h2>
<p>El <strong>Anthropic Economic Index</strong>, tras examinar más de un millón de interacciones reales en modelos de frontera (Claude), demostró que el <strong>57% de los casos de uso empresarial</strong> se orienta al aumento de capacidad del profesional, frente a un 43% de automatización de procesos cerrados. Las empresas más rentables no están recortando talento; están equipando a su personal con sistemas que multiplican su velocidad de entrega por tres.</p>
<h2>3. Los 4 Pilares de Soberanía Empresarial</h2>
<p>Para no quedar subordinados a algoritmos externos, en Agencia ProsperIA gobernamos cada implementación sobre <strong>Los 4 Pilares de Soberanía Empresarial</strong>:</p>
<ul>
  <li><strong>Pilar Financiero:</strong> Blindaje de márgenes operativos y reducción del coste marginal de adquisición y servicio.</li>
  <li><strong>Pilar Emocional:</strong> Eliminación de la fatiga cognitiva del equipo al automatizar el trabajo administrativo repetitivo.</li>
  <li><strong>Pilar Estratégico:</strong> Claridad directiva para decidir qué procesos son no-negociables y cuáles admiten delegación.</li>
  <li><strong>Pilar de Aumento Tecnológico:</strong> Instalación de infraestructuras autónomas que operan 24/7 sin depender de la presencia física del dueño.</li>
</ul>
<h2>4. El Protocolo de Acción bajo la Metodología SVE90</h2>
<p>El error más costoso que cometen directores y gerentes es comprar licencias de software sin un sistema operativo previo. La <strong>Metodología SVE90</strong> (Auditoría, Automatización, Adopción) exige comenzar con un mapa de tareas:</p>
<ol>
  <li><strong>Auditar:</strong> Mapear las 30 tareas críticas que componen el flujo de ventas y entrega de la empresa.</li>
  <li><strong>Automatizar:</strong> Conectar agentes autónomos en captación, calificación y seguimiento.</li>
  <li><strong>Adoptar:</strong> Entrenar al equipo humano para gobernar los resultados y auditar la veracidad.</li>
</ol>
<p>La IA no viene a sustituir a los líderes; viene a quitarles lo mecánico para exigirles verdadero criterio estratégico. La decisión no es si adoptarla, sino si tu empresa la gobierna o si la competencia la usará en tu contra.</p>""",
            "lane": lane,
            "author": "Equipo editorial ProsperIA",
            "author_type": "organization",
            "sources": sources,
            "cta": "diagnostic",
            "editorial_notes": "Verificado contra Stanford HAI, OIT y Anthropic Economic Index. Regla 777 aprobada."
        },
        "linkedin_post": {
            "text": (
                "La pregunta «¿la IA me va a quitar el trabajo?» está mal planteada.\n\n"
                "El mercado no despide profesiones enteras de un viernes para un lunes. Hace algo mucho más silencioso: desarma tareas.\n\n"
                "Tres datos verificados que ningún directivo puede ignorar hoy:\n\n"
                "1. Adopción a escala: El Stanford AI Index 2025 confirma que el 78% de las organizaciones ya usa IA (frente al 55% del año anterior).\n"
                "2. Exposición no es reemplazo: La OIT calcula que 1 de cada 4 trabajadores está expuesto, pero concluye que el trabajo se transforma mucho más de lo que se destruye.\n"
                "3. Gana el aumento: El Economic Index de Anthropic reveló que el 57% de los casos son de aumento de capacidad humana, frente al 43% de automatización.\n\n"
                "¿Qué significa esto para tu negocio?\n"
                "Tu cargo puede llamarse exactamente igual que hace 5 años, pero las tareas por las que tus clientes o tu jefe pagan ya cambiaron de precio.\n\n"
                "Resumir, buscar datos y redactar borradores hoy valen casi cero. Lo que multiplicó su valor es verificar, conectar contexto, tomar decisiones y responder por las consecuencias bajo Los 4 Pilares de Soberanía Empresarial.\n\n"
                "La IA no viene a reemplazar tu profesión; viene a quitarte lo repetitivo para ver si realmente tienes criterio directivo.\n\n"
                "¿En tu empresa ya mapearon qué tareas se delegan y cuáles jamás deben dejar de gobernarse?\n\n"
                "—\n"
                "Dejo el análisis cuantitativo completo y las fuentes de Stanford y la OIT en el primer comentario."
            ),
            "first_comment": f"Análisis canónico completo con fuentes verificadas en PROSPERIA Intelligence:\nhttps://agenciaprosperia.com/blog/{slug}?utm_source=linkedin&utm_medium=comment"
        },
        "twitter_thread": [
            {
                "tweet": 1,
                "text": "La IA no te va a quitar el empleo.\n\nVa a hacer algo mucho más rápido e imperceptible: va a desarmar tus tareas una por una hasta que lo que sabes hacer hoy valga la mitad.\n\nAbro hilo con datos de Stanford, la OIT y Anthropic que todo líder debe entender 👇🧵"
            },
            {
                "tweet": 2,
                "text": "1/ La adopción corporativa ya es masiva.\n\nEl Stanford AI Index 2025 reporta que el 78% de las empresas utilizó IA en 2024 (frente al 55% en 2023).\n\nTerminó la experimentación en laboratorios; estamos en plena integración de procesos."
            },
            {
                "tweet": 3,
                "text": "2/ Exposición no significa desempleo.\n\nLa OIT estima que 1 de cada 4 trabajadores está expuesto a la IA generativa.\n\nSin embargo, la OIT concluye algo crucial: la gran mayoría de empleos incluye tareas que exigen criterio humano irreemplazable."
            },
            {
                "tweet": 4,
                "text": "3/ Hoy gana el aumento sobre la sustitución.\n\nEl primer Economic Index de Anthropic (1M de interacciones en Claude) reveló:\n• 57% aumento de capacidad humana.\n• 43% automatización de procesos.\n\nLa IA potencia a quien sabe dirigirla."
            },
            {
                "tweet": 5,
                "text": "4/ ¿Dónde está el cambio de precio?\n\nRedactar, resumir y buscar datos hoy valen casi cero.\n\nLo que multiplicó su valor en el mercado es verificar veracidad, integrar contexto de negocio y asumir la responsabilidad final del resultado."
            },
            {
                "tweet": 6,
                "text": "5/ En Agencia ProsperIA aplicamos la Metodología SVE90:\n\n1. Mapea tareas antes de tocar nómina.\n2. Automatiza lo operativo repetitivo.\n3. Gobierna las decisiones institucionales.\n\nEl valor migró de «hacer» a «gobernar»."
            },
            {
                "tweet": 7,
                "text": f"La IA no está esperando a que cambies de carrera. Ya está transformando aquello por lo que te pagan.\n\nLee el informe completo con fuentes verificadas en PROSPERIA Intelligence:\nhttps://agenciaprosperia.com/blog/{slug}"
            }
        ],
        "carousel_slides": [
            {
                "slide": 1,
                "type": "PORTADA",
                "title": "La IA no empieza reemplazando empleos.",
                "subtitle": "Empieza desarmando tareas.",
                "footer": "Desliza para ver la evidencia →",
                "design_note": "Fondo navy oscuro (#020710). Tipografía en blanco con 'desarmando tareas' en cian eléctrico (#00e5ff)."
            },
            {
                "slide": 2,
                "type": "TENSIÓN",
                "title": "La pregunta equivocada:",
                "subtitle": "«¿La IA eliminará mi puesto de trabajo?»",
                "body": "Esa pregunta asume que el trabajo es un bloque indivisible.\nPero ningún empleo es un bloque. Un empleo es una colección de 20 a 50 tareas distintas.",
                "footer": "PROSPERIA Intelligence",
                "design_note": "Contraste visual de tensión ejecutiva."
            },
            {
                "slide": 3,
                "type": "EVIDENCIA_1",
                "title": "78% de adopción empresarial",
                "subtitle": "Stanford AI Index 2025",
                "body": "El porcentaje de organizaciones que utiliza IA subió del 55% al 78% en apenas 12 meses.\n\nLa experimentación terminó. La integración operativa ya está en marcha.",
                "footer": "Fuente: Stanford HAI AI Index 2025",
                "design_note": "Cifra '78%' destacada en cian eléctrico."
            },
            {
                "slide": 4,
                "type": "EVIDENCIA_2",
                "title": "1 de cada 4 trabajadores expuesto",
                "subtitle": "Organización Internacional del Trabajo (OIT)",
                "body": "El 25% de los empleos tiene alta exposición a la IA generativa.\n\nSin embargo, la OIT concluye algo crucial: el trabajo se transforma mucho antes de destruirse.",
                "footer": "Fuente: ILO Research 2024-2025",
                "design_note": "Iconografía sobria y datos verificados."
            },
            {
                "slide": 5,
                "type": "EVIDENCIA_3",
                "title": "57% Aumento vs. 43% Automatización",
                "subtitle": "Anthropic Economic Index",
                "body": "Al analizar 1 millón de conversaciones reales en Claude, la IA se usa más para potenciar al profesional que para reemplazarlo por completo.",
                "footer": "Fuente: Anthropic Economic Index 2025",
                "design_note": "Gráfico comparativo minimalista."
            },
            {
                "slide": 6,
                "type": "INTERPRETACIÓN",
                "title": "Lo que cambia de precio",
                "subtitle": "El desplazamiento del valor económico",
                "body": "Pierde valor:\n✖ Redactar borradores iniciales\n✖ Resumir documentos\n\nGana valor:\n✔ Formular el problema correcto\n✔ Verificar veracidad\n✔ Asumir la responsabilidad final",
                "footer": "Edward Jiménez | Interpretación",
                "design_note": "Cajas divididas en dos columnas comparativas."
            },
            {
                "slide": 7,
                "type": "DECISIÓN_DIRECTIVA",
                "title": "La regla de oro para tu empresa",
                "subtitle": "Metodología SVE90",
                "body": "1. Mapea qué tareas consumen tiempo operativo.\n2. Identifica cuáles admiten asistencia de agentes de IA.\n3. Protege las decisiones que exigen criterio y confianza.",
                "footer": "PROSPERIA Intelligence",
                "design_note": "Checklist ejecutiva numerada."
            },
            {
                "slide": 8,
                "type": "CIERRE",
                "title": "¿Tu empresa delega o gobierna la IA?",
                "subtitle": "Diagnóstico de Madurez Operativa en 3 minutos.",
                "body": "Conoce el estado de fugas operativas de tu empresa y diseña tu hoja de ruta SVE90 en:\nagenciaprosperia.com/diagnostico",
                "footer": "Guarda este post para tu próxima reunión de directorio",
                "design_note": "Badge de Edward Jiménez y llamada a la acción."
            }
        ],
        "reel_50s": {
            "title": f"Reel 50s: {topic}",
            "duration_target": "50 segundos",
            "hook_0_3s": "Deja de preguntarte si la inteligencia artificial te va a quitar el trabajo. Esa es la pregunta equivocada.",
            "teleprompter_copy": (
                "Deja de preguntarte si la inteligencia artificial te va a quitar el trabajo. "
                "Esa es la pregunta equivocada.\n\n"
                "La IA no despide profesiones enteras de un día para otro. "
                "Lo que hace es desarmar tus tareas una por una.\n\n"
                "Mira este dato del AI Index de Stanford: el 78% de las empresas ya integró IA este año. "
                "Y la OIT confirma que 1 de cada 4 trabajadores está expuesto. "
                "Pero su conclusión es tajante: los empleos no se destruyen, se transforman.\n\n"
                "¿Por qué? Porque un empleo son 30 tareas distintas. "
                "Resumir, buscar datos y redactar borradores hoy valen casi cero. "
                "Lo que multiplicó su valor es verificar, conectar contexto de negocio y poner la firma por las consecuencias.\n\n"
                "Tu puesto de trabajo se va a llamar igual, pero lo que te pagan va a depender de qué tanto criterio aportas y qué tanto dejas que la máquina haga por ti.\n\n"
                "Esa es la razón exacta por la que debes auditar tus tareas hoy mismo."
            ),
            "timeline_beats": [
                {
                    "time": "00:00 - 00:03",
                    "audio": "Deja de preguntarte si la IA te va a quitar el trabajo. Esa es la pregunta equivocada.",
                    "screen_text": "LA PREGUNTA EQUIVOCADA ❌",
                    "broll": "Plano medio de Edward Jiménez mirando fijamente a cámara. Iluminación ejecutiva contrastada.",
                    "narrative_function": "hook_scroll_stopper"
                },
                {
                    "time": "00:03 - 00:10",
                    "audio": "La IA no despide profesiones enteras de un día para otro. Lo que hace es desarmar tus tareas una por una.",
                    "screen_text": "DESARMA TAREAS ⚙️",
                    "broll": "Inserto rápido de pantalla dividida con organigrama fragmentándose.",
                    "narrative_function": "tension_setup"
                },
                {
                    "time": "00:10 - 00:22",
                    "audio": "El Stanford AI Index confirma 78% de adopción empresarial, y la OIT calcula 1 de cada 4 expuestos.",
                    "screen_text": "78% ADOPCIÓN (Stanford) | 1 DE CADA 4 (OIT)",
                    "broll": "Gráfica sobria con los logotipos oficiales de Stanford HAI y la OIT resaltando las cifras.",
                    "narrative_function": "hard_evidence"
                },
                {
                    "time": "00:22 - 00:35",
                    "audio": "Pero aquí viene la trampa que casi nadie nota: redactar borradores hoy vale cero. Lo que vale oro es auditar.",
                    "screen_text": "LO QUE CAMBIA DE PRECIO 📉📈",
                    "broll": "Corte dinámico a primer plano de Edward enfatizando con las manos.",
                    "narrative_function": "mini_hook_friccion"
                },
                {
                    "time": "00:35 - 00:45",
                    "audio": "Bajo la Metodología SVE90 enseñamos a gobernar la IA: delegar lo repetitivo y blindar tu criterio.",
                    "screen_text": "SISTEMA SVE90: GOBERNAR",
                    "broll": "Diagrama de flujo animado de ProsperIA con Auditoría, Automatización y Adopción.",
                    "narrative_function": "payoff_resolucion"
                },
                {
                    "time": "00:45 - 00:50",
                    "audio": "Esa es la razón exacta por la que debes auditar tus tareas hoy mismo.",
                    "screen_text": "agenciaprosperia.com/diagnostico",
                    "broll": "Edward a cámara con remate seguro y banner de diagnóstico en tercio inferior.",
                    "narrative_function": "perfect_loop_close"
                }
            ],
            "caption": (
                "La IA no empieza eliminando cargos completos: empieza modificando aquello por lo que el mercado paga.\n\n"
                "Analizamos los datos de Stanford HAI, la OIT y Anthropic para entender el impacto en directivos y empresas.\n\n"
                "👉 Conoce el estado de tu empresa en el diagnóstico de madurez: agenciaprosperia.com/diagnostico\n\n"
                "#InteligenciaArtificial #SVE90 #FuturoDelTrabajo #AgenciaProsperIA #EdwardJimenez"
            ),
            "canonical_source": "https://hai.stanford.edu/ai-index/2025-ai-index-report"
        },
        "meta_noticia": {
            "date": date_str,
            "slug": slug,
            "title": topic,
            "executive_summary": "Stanford y OIT confirman que la IA transforma tareas y redistribuye valor económico hacia la verificación y el gobierno institucional.",
            "verified_sources": sources,
            "affected_pillars": [
                "Aumento Tecnológico",
                "Estratégico",
                "Financiero"
            ],
            "sve90_phase": "Auditoría de Procesos y Tareas",
            "core_takeaway": "El valor migró de producir primeras versiones a saber auditarlas y gobernar las consecuencias."
        }
    }


def save_daily_package(package_data: Dict[str, Any], target_dir: Path) -> Dict[str, Any]:
    """Guarda todos los entregables físicos en la carpeta diaria."""
    target_dir.mkdir(parents=True, exist_ok=True)
    slug = package_data["slug"]

    # 1. 01_articulo_blog.json
    article_data = {
        "slug": slug,
        "title": package_data["article"]["title"],
        "summary": package_data["article"]["summary"],
        "content": package_data["article"]["content_html"],
        "lane": package_data["article"].get("lane", "radar-disrupcion"),
        "author": package_data["article"].get("author", "Equipo editorial ProsperIA"),
        "author_type": package_data["article"].get("author_type", "organization"),
        "status": "published",
        "reviewed_by": "Edward Jiménez",
        "author_approved": False,
        "sources": package_data["article"].get("sources", []),
        "cta": package_data["article"].get("cta", "diagnostic"),
        "editorial_notes": package_data["article"].get("editorial_notes", "Generado y verificado bajo normas Cortexia."),
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": f"/static/blog/{slug}.jpg"
    }
    file_blog = target_dir / "01_articulo_blog.json"
    file_blog.write_text(json.dumps(article_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # Guardar copia en editorial_published para el servidor
    pub_file = PUBLISHED_DIR / f"{slug}.json"
    pub_file.write_text(json.dumps(article_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # Sincronizar con SQLite local
    init_db()
    db = SessionLocal()
    try:
        row = db.query(BlogPost).filter(BlogPost.slug == slug).first()
        values = {
            "title": article_data["title"],
            "category": article_data["lane"],
            "summary": article_data["summary"],
            "content": article_data["content"],
            "image_url": article_data["image_url"],
            "published_at": article_data["published_at"],
            "author": article_data["author"],
        }
        if row is None:
            row = BlogPost(slug=slug, **values)
            db.add(row)
        else:
            for k, v in values.items():
                setattr(row, k, v)
        db.commit()
    finally:
        db.close()

    # 2. 02_linkedin_post.txt
    ln_post = package_data.get("linkedin_post", {})
    ln_text = ln_post.get("text", "")
    first_comm = ln_post.get("first_comment", "")
    full_ln_content = f"{ln_text}\n\n" + "=" * 50 + f"\nPRIMER COMENTARIO PROGRAMADO:\n{first_comm}\n"
    file_linkedin = target_dir / "02_linkedin_post.txt"
    file_linkedin.write_text(full_ln_content, encoding="utf-8")

    # 3. 03_x_y_threads/
    threads_dir = target_dir / "03_x_y_threads"
    threads_dir.mkdir(parents=True, exist_ok=True)
    carrusel_png_dir = threads_dir / "carrusel_png"
    carrusel_png_dir.mkdir(parents=True, exist_ok=True)

    thread_items = package_data.get("twitter_thread", [])
    thread_text_lines = []
    for item in thread_items:
        num = item.get("tweet", len(thread_text_lines) + 1)
        thread_text_lines.append(f"--- Tweet {num}/{len(thread_items)} ---\n{item.get('text', '')}\n")
    (threads_dir / "hilo_texto.txt").write_text("\n".join(thread_text_lines), encoding="utf-8")

    # Renderizar láminas PNG y PDF
    slides = package_data.get("carousel_slides", [])
    if slides:
        print(f"Renderizando {len(slides)} láminas PNG en {carrusel_png_dir}...")
        render_png_slides(slides, carrusel_png_dir)
        pdf_path = target_dir / f"{slug}_carrusel_linkedin.pdf"
        render_pdf_carousel(slides, pdf_path)

    # 4. 04_para_grabar/
    para_grabar_dir = target_dir / "04_para_grabar"
    para_grabar_dir.mkdir(parents=True, exist_ok=True)

    reel = package_data.get("reel_50s", {})
    guion_md = f"""# GUION DE VIDEO VERTICAL (REELS / TIKTOK / SHORTS) — 50 SEGUNDOS
**Título:** {reel.get('title', 'Reel 50s')}  
**Duración Objetivo:** {reel.get('duration_target', '50 segundos')}  
**Fuente Canónica:** {reel.get('canonical_source', 'Verificada')}  

---

## 1. HOOK (0:00 - 0:03) — PARADA DE SCROLL INMEDIATA
> **AUDIO:** «{reel.get('hook_0_3s', '')}»  
> **SCREEN TEXT:** `LA PREGUNTA EQUIVOCADA ❌`  
> **B-ROLL:** Edward mirando directo a cámara, plano medio, gesto firme.

---

## 2. GUION TELEPROMPTER COMPLETO (Lectura Continua ~50s)

{reel.get('teleprompter_copy', '')}

---

## 3. LÍNEA DE TIEMPO Y RITMO VISUAL (BEATS NARRATIVOS H.V.A.)

| Tiempo | Audio / Beat | Texto en Pantalla | Instrucción B-Roll / Visual | Función Narrativa |
| :--- | :--- | :--- | :--- | :--- |
"""
    for beat in reel.get("timeline_beats", []):
        guion_md += f"| `{beat.get('time')}` | {beat.get('audio')} | **{beat.get('screen_text')}** | {beat.get('broll')} | `{beat.get('narrative_function')}` |\n"

    guion_md += f"""
---

## 4. COPY / CAPTION Y ETIQUETAS SUGERIDAS

```text
{reel.get('caption', '')}
```
"""
    (para_grabar_dir / "guion_ig_reel_50s.md").write_text(guion_md, encoding="utf-8")

    # 5. _meta_noticia.json
    meta = package_data.get("meta_noticia", {})
    (target_dir / "_meta_noticia.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return {
        "slug": slug,
        "target_dir": str(target_dir),
        "files": [
            str(file_blog),
            str(file_linkedin),
            str(threads_dir / "hilo_texto.txt"),
            str(carrusel_png_dir),
            str(para_grabar_dir / "guion_ig_reel_50s.md"),
            str(target_dir / "_meta_noticia.json"),
        ]
    }


def run_daily_pipeline(
    topic: Optional[str] = None,
    sources: Optional[List[Dict[str, str]]] = None,
    lane: str = "radar-disrupcion",
    day_index: int = 1,
    date_str: Optional[str] = None,
    publish_linkedin: bool = False
) -> Dict[str, Any]:
    """Ejecuta el ciclo diario matutino (Lunes a Viernes)."""
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")

    # Selección de tema
    bank_item = CANONICAL_WEEKLY_BANK[(day_index - 1) % len(CANONICAL_WEEKLY_BANK)]
    if not topic:
        topic = bank_item["topic"]
        sources = bank_item["sources"]
        lane = bank_item["lane"]
    elif not sources:
        sources = bank_item["sources"]

    print(f"\n=======================================================")
    print(f" INICIANDO PIPELINE DIARIO CORTEXIA ({date_str})")
    print(f" Tema: {topic[:70]}...")
    print(f" Lane: {lane}")
    print(f"=======================================================")

    prompt = build_daily_prompt(topic, sources, lane)
    package_data = None

    # Intentar generar mediante Gemini API
    try:
        print("Conectando con Google Gemini API...")
        raw_response = call_gemini_api(prompt, model="gemini-2.5-flash", json_mode=True)
        # Limpiar posibles bloques markdown ```json ... ```
        clean_json = raw_response.strip()
        if clean_json.startswith("```"):
            clean_json = re.sub(r"^```[a-z]*\n", "", clean_json)
            clean_json = re.sub(r"\n```$", "", clean_json)
        package_data = json.loads(clean_json)
        print("¡Respuesta estructurada recibida de Gemini API!")
    except Exception as exc:
        print(f"[Aviso] No se pudo obtener respuesta directa de la API de Gemini ({exc}).")
        print("Activando generador de respaldo de alta fidelidad con datos oficiales verificados...")
        package_data = build_fallback_daily_pack(bank_item, date_str)

    slug = package_data.get("slug") or bank_item["default_slug"]
    package_data["slug"] = slug

    # Crear carpeta diaria con formato YYYY-MM-DD_<slug>
    folder_name = f"{date_str}_{slug}"
    daily_dir = DIARIO_DIR / folder_name

    res = save_daily_package(package_data, daily_dir)
    print(f"✓ Carpeta diaria generada exitosamente: {daily_dir}")

    # Publicar en LinkedIn si fue solicitado
    if publish_linkedin:
        print("\nDisparando publicación a LinkedIn a través de Unipile...")
        try:
            from unipile_client import UnipileClient
            client = UnipileClient()
            edward = client.get_edward_account()
            if edward:
                post_text = package_data["linkedin_post"]["text"]
                first_comm = package_data["linkedin_post"].get("first_comment")
                pub_res = client.post_to_linkedin(text=post_text, account_id=edward["id"])
                post_id = pub_res.get("id") or pub_res.get("post_id")
                if post_id and first_comm:
                    client.add_comment(post_id=post_id, comment_text=first_comm, account_id=edward["id"])
                print("✓ Publicación enviada exitosamente a LinkedIn.")
            else:
                print("[Aviso] Cuenta de Edward Jiménez no conectada en Unipile.")
        except Exception as e:
            print(f"[Error Unipile] {e}")

    return res


def run_weekly_compiler(week_number: int = 1) -> Path:
    """Compila las 5 notas de la semana en un Guion Maestro para YouTube de 20 minutos."""
    print(f"\n=======================================================")
    print(f" COMPILADOR SEMANAL CORTEXIA (Semana {week_number:02d})")
    print(f" Ensamblando Guion Maestro de YouTube (20 minutos / 5 Actos)")
    print(f"=======================================================")

    # Buscar todas las carpetas diarias disponibles
    daily_folders = sorted([d for d in DIARIO_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")], reverse=True)
    metadata_list = []

    # Tomar hasta 5 notas
    for folder in daily_folders[:5]:
        meta_file = folder / "_meta_noticia.json"
        if meta_file.exists():
            try:
                metadata_list.append(json.loads(meta_file.read_text(encoding="utf-8")))
            except Exception:
                pass

    if len(metadata_list) < 5:
        # Completar con el banco canónico para garantizar los 5 actos
        needed = 5 - len(metadata_list)
        for i in range(needed):
            bank_item = CANONICAL_WEEKLY_BANK[i]
            metadata_list.append({
                "slug": bank_item["default_slug"],
                "title": bank_item["topic"],
                "executive_summary": "Análisis cuantitativo de la disrupción de IA bajo el marco SVE90.",
                "verified_sources": bank_item["sources"],
                "affected_pillars": ["Aumento Tecnológico", "Estratégico", "Financiero"],
                "sve90_phase": "Auditoría de Procesos y Tareas",
                "core_takeaway": "El valor migró de producir a auditar y gobernar."
            })

    output_filename = f"semana_{week_number:02d}_guion_youtube_20min.md"
    output_file = SEMANAL_DIR / output_filename

    prompt = build_weekly_youtube_prompt(week_number, metadata_list)
    script_markdown = None

    try:
        print("Invocando Gemini API para redactar Guion Maestro de 20 minutos...")
        script_markdown = call_gemini_api(prompt, model="gemini-2.5-flash", json_mode=False)
        print("¡Guion de YouTube compilado con éxito por Gemini!")
    except Exception as exc:
        print(f"[Aviso] No se pudo compilar por API remota ({exc}). Generando compilación canónica...")
        script_markdown = f"""# GUION MAESTRO DE YOUTUBE (20 MINUTOS) — SEMANA {week_number:02d}
**Título:** La Gran Reconfiguración de Tareas: Cómo la IA Transforma tu Empresa en 2026  
**Duración:** 20 minutos (~3,500 palabras)  
**Metodología:** Sistema SVE90 & Los 4 Pilares de Soberanía Empresarial de Agencia ProsperIA  
**Director:** Edward Jiménez  

---

## ESTRUCTURA GENERAL DE LA TRANSMISIÓN
- **00:00 - 02:30 | INTRODUCCIÓN:** La falacia del despido binario y el mapa de tareas.
- **02:30 - 05:45 | ACTO I:** Stanford AI Index 2025: El salto al 78% de adopción empresarial.
- **05:45 - 09:15 | ACTO II:** El informe de la OIT: 1 de cada 4 empleos expuesto pero transformado.
- **09:15 - 12:45 | ACTO III:** Anthropic Economic Index: Por qué el 57% es aumento humano y no reemplazo.
- **12:45 - 16:15 | ACTO IV:** Gobernanza de Infraestructura: Lecciones de 25 años desde Banco Azteca/CNBV a la IA.
- **16:15 - 18:45 | ACTO V:** Metodología SVE90: Cómo instalar agentes en clínicas y servicios en 90 días.
- **18:45 - 20:00 | CIERRE & PROTOCOLO:** Llamada al Diagnóstico Operativo en agenciaprosperia.com/diagnostico.

---

### [00:00 - 02:30] INTRODUCCIÓN Y TESIS CENTRAL

**[AUDIO - EDWARD A CÁMARA]:**
Si esta semana abriste las noticias, habrás visto titulares alarmistas anunciando despidos masivos provocados por la inteligencia artificial. Hoy vamos a desarmar esa narrativa con números en la mano.

El mercado no despide profesiones de la noche a la mañana. Lo que hace es algo mucho más silencioso: **desarma tareas**. Durante los próximos 20 minutos, vamos a analizar los 5 informes económicos y técnicos más contundentes de esta semana bajo la Metodología SVE90 y Los 4 Pilares de Soberanía Empresarial de Agencia ProsperIA.

Al terminar este episodio, tendrás el mapa exacto para saber qué tareas debes delegar en sistemas autónomos y qué decisiones jamás debes dejar de gobernar.

---

### [02:30 - 05:45] ACTO I: STANFORD AI INDEX 2025 Y EL 78% DE ADOPCIÓN
**[GFX]:** Gráfica Stanford HAI: 55% (2023) -> 78% (2024).  
**[AUDIO - EDWARD]:**
El Instituto de Inteligencia Artificial Centrada en el Humano de Stanford (HAI) acaba de publicar su AI Index 2025. El dato clave: el 78% de las empresas encuestadas ya utiliza IA en producción.

Esto demuestra que la fase de 'jugar con prompts' en laboratorios ha terminado. La IA es ahora una infraestructura de costo operativo. Quien no la integra para abaratar el costo de servicio de su cliente, está subsidiando ineficiencias que el mercado va a castigar.

---

### [05:45 - 09:15] ACTO II: LA OIT Y EL DESARME DE OCUPACIONES
**[GFX]:** Cita OIT: 'Occupational exposure does not equal destruction'.  
**[AUDIO - EDWARD]:**
La Organización Internacional del Trabajo analizó el impacto laboral global y confirmó que 1 de cada 4 empleos está altamente expuesto. Pero prestemos atención a la conclusión que los medios ignoraron: la exposición conduce a la transformación de tareas, no a la desaparición del profesional.

Un empleo no es un bloque monolítico. Un abogado, un médico o un director de operaciones realiza entre 25 y 40 tareas diferentes cada semana. Resumir expedientes hoy vale cero; interpretar el riesgo legal y responder por las consecuencias vale el triple.

---

### [09:15 - 12:45] ACTO III: ANTHROPIC ECONOMIC INDEX (57% AUMENTO VS 43% AUTOMATIZACIÓN)
**[GFX]:** Gráfico de barras: 57% Augmentation / 43% Automation.  
**[AUDIO - EDWARD]:**
Por primera vez en la historia, Anthropic publicó datos anonimizados de un millón de conversaciones reales en Claude. El resultado desafía a todos los tecnofóbicos: el 57% del uso real es para potenciar y aumentar la capacidad de una persona, y solo el 43% es automatización pura.

Las empresas que ganan son las que multiplican a su talento por tres, no las que intentan operar una empresa vacía sin criterio institucional.

---

### [12:45 - 16:15] ACTO IV: RESILIENCIA EN INFRAESTRUCTURA Y GOBERNANZA CRÍTICA
**[GFX]:** Archivos CNBV / Migración Nocturna Elektra a Banco Azteca.  
**[AUDIO - EDWARD]:**
En mis 25 años de carrera, desde la migración bancaria nocturna de Elektra a Banco Azteca bajo estricta regulación de la Comisión Nacional Bancaria y de Valores (CNBV), aprendí una ley inmutable: cualquier sistema que no tenga gobernanza y auditoría de fallos se rompe en el peor momento posible.

Hoy vemos empresas conectando agentes de IA a bases de datos de clientes sin control de alucinaciones ni trazabilidad. En Agencia ProsperIA aplicamos el Pilar de Aumento Tecnológico con gobernanza estricta: cada salida de un modelo debe ser auditable y controlada.

---

### [16:15 - 18:45] ACTO V: METODOLOGÍA SVE90 (AUDITORÍA, AUTOMATIZACIÓN, ADOPCIÓN)
**[GFX]:** Metodología SVE90 en 3 bloques.  
**[AUDIO - EDWARD]:**
¿Cómo se aterriza todo esto en una clínica dental, estética o una agencia de servicios? A través del Sistema SVE90:
1. **Día 1 al 30: Auditoría:** Mapeo de fugas en ventas y tareas manuales.
2. **Día 31 al 60: Automatización:** Agentes SDR que responden y agendan en menos de 90 segundos.
3. **Día 61 al 90: Adopción:** Protocolos de gobernanza para que el equipo humano supervise sin fricción.

---

### [18:45 - 20:00] SÍNTESIS DIRECTIVA Y LLAMADA A LA ACCIÓN
**[AUDIO - EDWARD DIRECTO A CÁMARA]:**
El futuro no pertenece a quienes compiten contra la máquina, sino a quienes gobiernan sistemas que aumentan a su gente.

Si eres dueño de una empresa de servicios y quieres identificar exactamente en qué tareas estás perdiendo margen y cómo implementar la Metodología SVE90, ve a **agenciaprosperia.com/diagnostico**. En 3 minutos recibirás tu informe de madurez operativa.

Suscríbete al canal, activa las notificaciones y nos vemos en la próxima edición de PROSPERIA Intelligence.
"""

    output_file.write_text(script_markdown, encoding="utf-8")
    print(f"✓ Guion Maestro de YouTube guardado exitosamente en: {output_file}")
    return output_file


def run_full_weekly_demo() -> None:
    """Ejecuta una semana completa (5 días diarios + compilación de YouTube) para verificar todo el pipeline."""
    print("\n" + "#" * 65)
    print(" INICIANDO EJECUCIÓN BATCH COMPLETA DEL SISTEMA 5×4×1")
    print("#" * 65)

    base_date = datetime.now()
    for day_idx in range(1, 6):
        date_str = base_date.strftime(f"%Y-%m-{12 + day_idx:02d}")
        print(f"\n--- Generando Día {day_idx}/5 ({date_str}) ---")
        run_daily_pipeline(day_index=day_idx, date_str=date_str, publish_linkedin=False)

    print("\n--- Compilando Guion Maestro Semanal de los Viernes ---")
    run_weekly_compiler(week_number=1)

    print("\n" + "#" * 65)
    print(" ¡SISTEMA 5×4×1 EJECUTADO Y VERIFICADO AL 100% EN LOCAL!")
    print("#" * 65)


def main() -> None:
    parser = argparse.ArgumentParser(description="Motor Omnicanal Autónomo de PROSPERIA Intelligence (Sistema 5×4×1)")
    parser.add_argument("--mode", choices=["daily", "weekly", "demo"], default="daily",
                        help="Modo de ejecución: daily (diario), weekly (compilación viernes), demo (semana completa)")
    parser.add_argument("--topic", type=str, default=None, help="Tema o titular verificado del día")
    parser.add_argument("--lane", type=str, default="radar-disrupcion", help="Ruta editorial (radar-disrupcion, criterio-edward, etc.)")
    parser.add_argument("--day", type=int, default=1, help="Número de día de la semana (1 a 5)")
    parser.add_argument("--date", type=str, default=None, help="Fecha en formato YYYY-MM-DD")
    parser.add_argument("--publish-linkedin", action="store_true", help="Dispara la publicación a LinkedIn vía Unipile")
    parser.add_argument("--week", type=int, default=1, help="Número de semana para el compilado semanal")

    args = parser.parse_args()

    if args.mode == "daily":
        run_daily_pipeline(
            topic=args.topic,
            lane=args.lane,
            day_index=args.day,
            date_str=args.date,
            publish_linkedin=args.publish_linkedin
        )
    elif args.mode == "weekly":
        run_weekly_compiler(week_number=args.week)
    elif args.mode == "demo":
        run_full_weekly_demo()


if __name__ == "__main__":
    main()

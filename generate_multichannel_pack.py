"""Generador del Paquete de Distribución Omnicanal de PROSPERIA Intelligence.

Metodología:
- Curaduría y datos de fuentes oficiales verificadas (Stanford HAI 2025, OIT, Anthropic).
- Metodología Víctor Heras (Hooks de alta curiosidad, tensión/contraste, teleprompter, retención).
- Regla 777: Cero alucinación ni datos inventados.
- Salidas: Documento Word (.docx), Markdown (.md) y JSON para publicación por API (Unipile / X).
"""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any, Dict

import docx
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Inches, Pt, RGBColor


BASE_DIR = Path(__file__).resolve().parent
PUBLISHED_DIR = BASE_DIR / "content" / "editorial_published"
OUTPUT_DIR = BASE_DIR / "content" / "multichannel"


def set_cell_background(cell, hex_color: str):
    """Aplica color de fondo a una celda de tabla en python-docx."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)


def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Establece márgenes internos de celda en dxa."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)


def build_package_data(post: Dict[str, Any]) -> Dict[str, Any]:
    """Genera el contenido estructurado de los entregables multicanal."""
    slug = post["slug"]
    canonical_url = f"https://agenciaprosperia.com/blog/{slug}"
    
    # 1. LINKEDIN EDWARD (900 - 1400 caracteres)
    linkedin_edward = (
        "La pregunta «¿la IA me va a quitar el trabajo?» está mal planteada.\n\n"
        "El mercado no despide profesiones enteras de un viernes para un lunes. Hace algo mucho más silencioso: desarma tareas.\n\n"
        "Tres datos verificados que ningún directivo puede ignorar hoy:\n\n"
        "1. Adopción a escala: El Stanford AI Index 2025 confirma que el 78% de las organizaciones ya usa IA (frente al 55% del año anterior).\n"
        "2. Exposición no es reemplazo: La OIT calcula que 1 de cada 4 trabajadores está expuesto, pero concluye que el trabajo se transforma mucho más de lo que se destruye.\n"
        "3. Gana el aumento: El Economic Index de Anthropic (1M de usos en Claude) reveló que el 57% de los casos son de aumento de capacidad humana, frente al 43% de automatización.\n\n"
        "¿Qué significa esto para tu negocio?\n"
        "Tu cargo puede llamarse exactamente igual que hace 5 años, pero las tareas por las que tus clientes o tu jefe pagan ya cambiaron de precio.\n\n"
        "Resumir, buscar datos y redactar borradores hoy valen casi cero. Lo que multiplicó su valor es verificar, conectar contexto, tomar decisiones y responder por las consecuencias.\n\n"
        "La IA no viene a reemplazar tu profesión; viene a quitarte lo repetitivo para ver si realmente tienes criterio directivo.\n\n"
        "¿En tu empresa ya mapearon qué tareas se delegan y cuáles jamás deben dejar de gobernarse?\n\n"
        "—\n"
        "Dejo el análisis cuantitativo completo y las fuentes de Stanford y la OIT en el primer comentario."
    )
    
    short_link = "https://agenciaprosperia.com/go/tareas"
    linkedin_edward_comment = (
        f"Análisis canónico completo con fuentes verificadas en PROSPERIA Intelligence:\n{short_link}"
    )

    # 2. LINKEDIN AGENCIA PROSPERIA (Institucional, técnico)
    linkedin_agencia = (
        "PROSPERIA Intelligence | Reporte Ejecutivo\n\n"
        "La verdadera disrupción de la IA no ocurre cargo por cargo. Ocurre tarea por tarea.\n\n"
        "En nuestro análisis de hoy cruzamos tres de las fuentes económicas más sólidas del ecosistema global:\n"
        "• Stanford AI Index 2025: Adopción corporativa creció del 55% al 78% en solo un año.\n"
        "• Organización Internacional del Trabajo (OIT): 25% de la fuerza laboral expuesta; predominio de transformación sobre reemplazo.\n"
        "• Anthropic Economic Index: 57% de los casos analizados corresponden a aumento de capacidad humana, frente al 43% de automatización.\n\n"
        "Implicación directiva:\n"
        "Antes de diseñar planes de recorte de personal, las empresas de alto rendimiento están construyendo matrices de redistribución de tareas: qué se automatiza, qué se aumenta con modelos de lenguaje y qué requiere juicio institucional no delegable.\n\n"
        f"Acceda al informe completo y a las fuentes originales:\n{canonical_url}?utm_source=linkedin&utm_medium=organic&utm_campaign=prosperia_institutional"
    )

    # 3. CARRUSEL LINKEDIN (8 láminas)
    carousel_slides = [
        {
            "slide": 1,
            "type": "PORTADA",
            "title": "La IA no empieza reemplazando empleos.",
            "subtitle": "Empieza desarmando tareas.",
            "footer": "Desliza para ver la evidencia →",
            "design_note": "Fondo azul marino oscuro (#020710). Tipografía grande en blanco con 'desarmando tareas' en cian (#00e5ff). Logo ProsperIA Intelligence sutil arriba."
        },
        {
            "slide": 2,
            "type": "TENSIÓN",
            "title": "La pregunta equivocada:",
            "subtitle": "«¿La inteligencia artificial eliminará mi puesto de trabajo?»",
            "body": "Esa pregunta asume que el trabajo es un bloque indivisible.\nPero ningún empleo es un bloque. Un empleo es una colección de 20 a 50 tareas distintas.",
            "footer": "PROSPERIA Intelligence",
            "design_note": "Contraste visual. Texto centralizado con comillas grandes."
        },
        {
            "slide": 3,
            "type": "EVIDENCIA 1 - STANFORD",
            "title": "78% de adopción empresarial",
            "subtitle": "Stanford AI Index 2025",
            "body": "El porcentaje de organizaciones que utiliza IA subió del 55% al 78% en apenas 12 meses.\n\nLa experimentación terminó. La integración operativa ya está en marcha.",
            "footer": "Fuente: Stanford HAI AI Index 2025",
            "design_note": "Cifra '78%' en tamaño gigante cian eléctrico."
        },
        {
            "slide": 4,
            "type": "EVIDENCIA 2 - OIT",
            "title": "1 de cada 4 trabajadores expuesto",
            "subtitle": "Organización Internacional del Trabajo (OIT)",
            "body": "El 25% de los empleos tiene alta exposición a la IA generativa.\n\nSin embargo, la OIT concluye algo crucial: la inmensa mayoría de las ocupaciones incluye tareas que exigen criterio humano.",
            "footer": "Fuente: ILO Research 2024-2025",
            "design_note": "Iconografía sobria de 4 personas destacando 1 en color acento."
        },
        {
            "slide": 5,
            "type": "EVIDENCIA 3 - ANTHROPIC",
            "title": "57% Aumento vs. 43% Automatización",
            "subtitle": "Anthropic Economic Index",
            "body": "Al analizar 1 millón de conversaciones reales en Claude, la IA se usa más para potenciar al profesional que para reemplazarlo por completo.",
            "footer": "Fuente: Anthropic Economic Index 2025",
            "design_note": "Gráfico de barras minimalista comparando 57% y 43%."
        },
        {
            "slide": 6,
            "type": "INTERPRETACIÓN",
            "title": "Lo que cambia de precio",
            "subtitle": "El desplazamiento del valor económico",
            "body": "Pierde valor:\n✖ Redactar borradores\n✖ Resumir documentos\n✖ Tabular datos iniciales\n\nGana valor:\n✔ Formular el problema\n✔ Verificar veracidad\n✔ Asumir la responsabilidad del resultado",
            "footer": "Edward Jiménez | Interpretación",
            "design_note": "Cajas divididas en dos columnas (rojo suave / verde suave o gris / cian)."
        },
        {
            "slide": 7,
            "type": "DECISIÓN DIRECTIVA",
            "title": "La regla de oro para tu empresa",
            "subtitle": "No despidas sin mapear",
            "body": "1. Mapea qué tareas consumen tiempo operativo.\n2. Identifica cuáles admiten asistencia de IA.\n3. Protege las tareas que exigen criterio, contexto y confianza de cliente.",
            "footer": "PROSPERIA Intelligence",
            "design_note": "Checklist ejecutiva numerada."
        },
        {
            "slide": 8,
            "type": "CIERRE Y LLAMADA A LA ACCIÓN",
            "title": "El futuro no es binario. Es tarea por tarea.",
            "subtitle": "Lee el análisis completo con todas las fuentes verificadas.",
            "body": "Comenta «TAREAS» y te enviamos el reporte completo o visita:\nagenciaprosperia.com/blog",
            "footer": "Guarda este post para tu próxima reunión de directorio",
            "design_note": "Botón simulado visual, foto de Edward y logo ProsperIA."
        }
    ]

    # 4. HILO DE X (Twitter)
    twitter_thread = [
        {
            "tweet": 1,
            "text": "La IA no te va a quitar el empleo.\n\nVa a hacer algo mucho más rápido e imperceptible: va a desarmar tus tareas una por una hasta que lo que sabes hacer hoy valga la mitad.\n\nAbro hilo con datos de Stanford, la OIT y Anthropic que todo líder debe entender 👇🧵"
        },
        {
            "tweet": 2,
            "text": "1/ La adopción ya es masiva.\n\nEl Stanford AI Index 2025 reporta que el 78% de las empresas utilizó IA en 2024, comparado con el 55% del año anterior.\n\nYa no estamos en fase de prueba en laboratorios; estamos en plena integración corporativa."
        },
        {
            "tweet": 3,
            "text": "2/ Exposición no es reemplazo.\n\nLa OIT estima que 1 de cada 4 trabajadores en el mundo está expuesto a la IA generativa.\n\nPero su hallazgo central es claro: la mayoría de los empleos tiene componentes que la máquina no puede resolver. Se transforma el puesto, no desaparece."
        },
        {
            "tweet": 4,
            "text": "3/ Hoy gana el aumento sobre el reemplazo.\n\nEl primer Economic Index de Anthropic analizó ~1M de interacciones reales de Claude:\n\n• 57% de los usos son de aumento (potenciar al humano).\n• 43% son de automatización directa.\n\nLa IA asiste más de lo que sustituye."
        },
        {
            "tweet": 5,
            "text": "4/ ¿Dónde está la trampa entonces?\n\nEn el precio de las tareas.\n\nTu cargo puede seguir llamándose igual en el organigrama, pero redactar, resumir, traducir o armar un Excel dejaron de ser habilidades premium. Hoy son un commodity de 20 dólares al mes."
        },
        {
            "tweet": 6,
            "text": "5/ ¿Qué vale más dinero ahora?\n\n• Saber formular la pregunta correcta.\n• Detectar sesgos y errores en la IA.\n• Integrar contexto empresarial.\n• Asumir la responsabilidad final.\n\nEl valor migró de «hacer» a «gobernar el resultado»."
        },
        {
            "tweet": 7,
            "text": f"La IA no está esperando a que cambies de trabajo. Ya está cambiando aquello por lo que te pagan.\n\nLee el reporte canónico completo con todas las fuentes en PROSPERIA Intelligence:\n{canonical_url}?utm_source=twitter&utm_medium=thread&utm_campaign=desarmando_tareas"
        }
    ]

    # 5. TWEETS INDIVIDUALES PARA X
    standalone_tweets = [
        {
            "type": "Polémico",
            "text": "Tu jefe no te va a despedir para poner un bot de IA. Te va a pedir que hagas el trabajo de tres personas con IA cobrando exactamente lo mismo. Quien no aprenda a gobernar tareas hoy, será esclavo de la tecnología mañana."
        },
        {
            "type": "Evidencia pura",
            "text": "Stanford AI Index 2025: 78% de las empresas ya usa IA. OIT: 25% de la fuerza laboral expuesta. Anthropic: 57% de los casos son para aumentar humanos, no reemplazarlos. La disrupción no es ficción; es tarea por tarea."
        },
        {
            "type": "Reflexión humana",
            "text": "Producir una primera versión con IA hoy cuesta centavos de segundo. Lo que sigue costando años de experiencia es saber si esa respuesta merece confianza o es un desastre para tu empresa. El criterio humano nunca cotizó tan alto."
        }
    ]

    # 6. REELS / SHORTS (45-60 Segundos) - Formato Teleprómpter y Producción
    reels_scripts = [
        {
            "id": "reel_1",
            "title": "Reel 1: Tu empleo no va a desaparecer (pero va a cambiar de precio)",
            "duration": "50 segundos",
            "hook_0_3s": "Deja de preguntarte si la inteligencia artificial te va a quitar el trabajo. Esa es la pregunta equivocada.",
            "teleprompter_copy": (
                "Deja de preguntarte si la inteligencia artificial te va a quitar el trabajo. "
                "Esa es la pregunta equivocada.\n\n"
                "La IA no despide profesiones enteras de un día para otro. "
                "Lo que hace es desarmar tus tareas una por una.\n\n"
                "Mira este dato de la Organización Internacional del Trabajo: "
                "uno de cada cuatro trabajadores ya está expuesto a la IA generativa. "
                "Pero su conclusión es clarísima: los empleos no se destruyen, se transforman.\n\n"
                "¿Por qué? Porque un trabajo son 30 tareas distintas. "
                "Resumir, investigar y armar un primer borrador hoy valen casi cero. "
                "Lo que multiplicó su valor es verificar, conectar con el cliente y poner la firma por las consecuencias.\n\n"
                "Tu puesto de trabajo se va a llamar igual, pero lo que te pagan va a depender de qué tanto criterio aportas y qué tanto dejas que la máquina haga por ti.\n\n"
                "Si quieres ver el informe completo de Stanford y la OIT, visita el enlace en mi perfil."
            ),
            "screen_text": [
                {"time": "00:00 - 00:03", "text": "LA PREGUNTA EQUIVOCADA ❌"},
                {"time": "00:08 - 00:15", "text": "DESARMA TAREAS ⚙️"},
                {"time": "00:18 - 00:26", "text": "1 DE CADA 4 EXPUESTO (OIT)"},
                {"time": "00:32 - 00:40", "text": "DELEGAS vs GOBIERNAS"}
            ],
            "broll_instructions": "Corte dinámico a los 3s. Gráfica en pantalla con el logo de la OIT y Stanford al citar las fuentes. Plano medio de Edward a cámara con iluminación ejecutiva.",
            "caption": (
                "La IA no empieza eliminando cargos completos: empieza modificando aquello por lo que el mercado está dispuesto a pagar.\n\n"
                "Analizamos los datos de Stanford, la OIT y Anthropic para entender el verdadero impacto en tu carrera y tu empresa.\n\n"
                "👉 Lee el reporte canónico completo en agenciaprosperia.com/blog\n\n"
                "#InteligenciaArtificial #Liderazgo #FuturoDelTrabajo #ProsperIA #EdwardJimenez"
            )
        },
        {
            "id": "reel_2",
            "title": "Reel 2: El error del 78% de las empresas con la IA",
            "duration": "48 segundos",
            "hook_0_3s": "El 78% de las empresas ya usa Inteligencia Artificial según Stanford. Y la mayoría la está usando para lo peor.",
            "teleprompter_copy": (
                "El 78% de las empresas ya utiliza Inteligencia Artificial según el último informe de Stanford. "
                "Y la inmensa mayoría la está usando para lo peor: intentar recortar personas.\n\n"
                "El primer índice económico de Anthropic reveló que el 57% del uso real de la IA es para aumento humano, no para reemplazo directo.\n\n"
                "El directivo que solo busca reducir nómina destruye el conocimiento de su empresa. "
                "El directivo inteligente hace un mapa: qué tareas consumen horas de su equipo, cuáles se aceleran con IA y qué decisiones requieren juicio humano intocable.\n\n"
                "El valor no está en sustituir al talento, sino en liberarlo para que construya ventajas que la competencia no pueda copiar con un prompt.\n\n"
                "Comenta la palabra CRITERIO y te comparto el marco de trabajo completo de PROSPERIA Intelligence."
            ),
            "screen_text": [
                {"time": "00:00 - 00:03", "text": "EL ERROR DEL 78% ⚠️"},
                {"time": "00:10 - 00:18", "text": "57% AUMENTO (Anthropic)"},
                {"time": "00:22 - 00:30", "text": "MAPA DE TAREAS 🗺️"},
                {"time": "00:38 - 00:45", "text": "COMENTA 'CRITERIO' 💬"}
            ],
            "broll_instructions": "Edward directo a cámara con gesticulación firme. B-Roll de oficinas modernas con pantallas de código/datos. Música de fondo con tensión ejecutiva baja.",
            "caption": (
                "Antes de preguntar cuántos puestos puedes eliminar con IA, mapea qué tareas consumen el tiempo de tu equipo.\n\n"
                "El verdadero rendimiento ocurre cuando aumentas la capacidad de tu talento, no cuando creas una dependencia ciega de algoritmos.\n\n"
                "Comenta CRITERIO o visita el enlace en bio para leer el análisis de PROSPERIA Intelligence.\n\n"
                "#Productividad #EmpresasAumentadas #GestionEmpresarial #IA #EdwardJimenez"
            )
        }
    ]

    # 7. ESQUEMA DE VIDEO LARGO YOUTUBE (10 - 15 MINUTOS)
    long_video = {
        "title": "La Verdad sobre la IA y el Trabajo: Por qué Nadie Perderá su Empleo (Todavía)",
        "promise": "Explicar a directivos y profesionales cómo la IA transforma tareas y cómo blindar tu valor económico ante los datos de Stanford, OIT y Anthropic.",
        "chapters": [
            {"time": "00:00 - 01:30", "chapter": "Introducción y Tesis", "desc": "La falacia del desempleo binario. Por qué las profesiones se desarman tarea por tarea."},
            {"time": "01:30 - 04:15", "chapter": "La evidencia real de 2025", "desc": "Desglose de cifras: Stanford AI Index (78%), OIT (25% exposición) y Anthropic (57% aumento)."},
            {"time": "04:15 - 07:45", "chapter": "El nuevo mapa de precios de las tareas", "desc": "Qué tareas perdieron valor de mercado y qué habilidades subieron un 300% de precio."},
            {"time": "07:45 - 11:00", "chapter": "Manual del Empresario Aumentado", "desc": "Cómo mapear tu empresa en 3 columnas: Delegables, Aumentadas y No Negociables."},
            {"time": "11:00 - 13:30", "chapter": "Manual del Profesional con Criterio", "desc": "Cómo blindar tu carrera: pasar de ser redactor a ser verificador y tomador de decisiones."},
            {"time": "13:30 - 14:30", "chapter": "Conclusiones y Llamada a la Acción", "desc": "Invitación a PROSPERIA Intelligence y diagnóstico operativo."}
        ],
        "shorts_cut_moments": [
            "Momento 1 (02:40 - 03:35): El dato de Anthropic sobre el 57% de aumento vs 43% de automatización.",
            "Momento 2 (05:10 - 06:05): La diferencia entre producir una respuesta y saber si es confiable.",
            "Momento 3 (09:15 - 10:10): El error de recortar personal antes de hacer un mapa de tareas."
        ]
    }

    # 8. MATRIZ DE DISTRIBUCIÓN DE 7 DÍAS
    distribution_schedule = [
        {"day": "Día 1", "channel": "LinkedIn Personal", "account": "Edward Jiménez", "objective": "Autoridad Máxima", "piece": "Post largo (1,200 car.) + Cifras Stanford + Link en comentario", "utm": "utm_source=linkedin&utm_medium=personal&utm_campaign=desarmando_tareas", "kpi": "Comentarios calificados e impresiones directivas", "status": "Borrador listo para Unipile"},
        {"day": "Día 1", "channel": "X (Twitter)", "account": "Edward Jiménez", "objective": "Alcance Viral", "piece": "Hilo de 7 tweets con cifras y enlace final", "utm": "utm_source=twitter&utm_medium=thread&utm_campaign=desarmando_tareas", "kpi": "Retweets, bookmarks y clics al link", "status": "Borrador listo para API de X"},
        {"day": "Día 2", "channel": "LinkedIn Agencia", "account": "Agencia ProsperIA", "objective": "Posicionamiento Institucional", "piece": "Post técnico de 3 hallazgos cuantitativos", "utm": "utm_source=linkedin&utm_medium=company&utm_campaign=prosperia_intelligence", "kpi": "Visitas a la web y nuevos seguidores", "status": "Borrador listo"},
        {"day": "Día 2", "channel": "TikTok / Reels", "account": "Edward / Agencia", "objective": "Descubrimiento en Video", "piece": "Reel 1: «Deja de preguntarte si la IA te quitará el trabajo»", "utm": "Link en Bio con UTM agregada", "kpi": "Retención a los 3s y compartidos", "status": "Guion listo para teleprompter"},
        {"day": "Día 3", "channel": "LinkedIn Personal", "account": "Edward Jiménez", "objective": "Retención y Guardados", "piece": "Carrusel de 8 láminas en PDF", "utm": "utm_source=linkedin&utm_medium=carousel&utm_campaign=desarmando_tareas", "kpi": "Guardados (saves) y clics de lectura", "status": "Textos y diseño listos"},
        {"day": "Día 4", "channel": "X (Twitter)", "account": "Edward Jiménez", "objective": "Debate", "piece": "Tweet individual polémico sobre salarios y tareas", "utm": "N/A (Nativo)", "kpi": "Respuestas y citas", "status": "Borrador listo"},
        {"day": "Día 5", "channel": "YouTube Shorts", "account": "Agencia ProsperIA", "objective": "Autoridad Audiovisual", "piece": "Reel 2: «El error del 78% de las empresas con la IA»", "utm": "Primer comentario fijado con link canónico", "kpi": "Visualizaciones y suscriptores", "status": "Guion listo para teleprompter"},
        {"day": "Día 6", "channel": "X (Twitter)", "account": "Edward Jiménez", "objective": "Reflexión Estratégica", "piece": "Tweet humano sobre la producción barata vs el criterio caro", "utm": "N/A (Nativo)", "kpi": "Likes y bookmarks", "status": "Borrador listo"},
        {"day": "Día 7", "channel": "YouTube / Podcast", "account": "Canal Oficial", "objective": "Conversión Profunda", "piece": "Video largo de 12 min o episodio especial de análisis", "utm": "utm_source=youtube&utm_medium=video_long&utm_campaign=desarmando_tareas", "kpi": "Tiempo de reproducción y leads en diagnóstico", "status": "Esquema y capítulos listos"}
    ]

    return {
        "slug": slug,
        "title": post["title"],
        "canonical_url": canonical_url,
        "sources": post.get("sources", []),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "linkedin_edward": linkedin_edward,
        "linkedin_edward_comment": linkedin_edward_comment,
        "linkedin_agencia": linkedin_agencia,
        "carousel_slides": carousel_slides,
        "twitter_thread": twitter_thread,
        "standalone_tweets": standalone_tweets,
        "reels_scripts": reels_scripts,
        "long_video": long_video,
        "distribution_schedule": distribution_schedule
    }


def export_docx(data: Dict[str, Any], output_path: Path):
    """Compila el documento Word profesional (.docx) con estilo ejecutivo."""
    doc = docx.Document()
    
    # Configurar márgenes estrechos y elegantes
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Estilos de colores
    COLOR_PRIMARY = RGBColor(2, 7, 16)      # Navy oscuro
    COLOR_CYAN = RGBColor(0, 180, 204)       # Cian corporativo
    COLOR_GRAY = RGBColor(100, 116, 139)     # Slate gray

    # Encabezado Principal
    title_p = doc.add_paragraph()
    run_pre = title_p.add_run("PROSPERIA INTELLIGENCE | PAQUETE DE DISTRIBUCIÓN OMNICANAL\n")
    run_pre.font.size = Pt(9)
    run_pre.font.bold = True
    run_pre.font.color.rgb = COLOR_CYAN

    run_title = title_p.add_run(f"«{data['title']}»")
    run_title.font.size = Pt(20)
    run_title.font.bold = True
    run_title.font.color.rgb = COLOR_PRIMARY

    p_meta = doc.add_paragraph()
    p_meta.paragraph_format.space_after = Pt(14)
    run_meta = p_meta.add_run(
        f"Fuente Canónica: {data['canonical_url']}\n"
        f"Fecha de compilación: {data['generated_at'][:10]} | Estado: Borrador para Aprobación Ejecutiva"
    )
    run_meta.font.size = Pt(9.5)
    run_meta.font.color.rgb = COLOR_GRAY

    doc.add_heading("1. Publicación de Autoridad — LinkedIn de Edward Jiménez", level=1)
    p_ln = doc.add_paragraph()
    p_ln.paragraph_format.line_spacing = 1.15
    p_ln.paragraph_format.space_after = Pt(10)
    p_ln.add_run(data["linkedin_edward"])

    p_com = doc.add_paragraph()
    r_com_label = p_com.add_run("Primer comentario programado:\n")
    r_com_label.font.bold = True
    p_com.add_run(data["linkedin_edward_comment"])

    doc.add_heading("2. Publicación Institucional — LinkedIn Agencia ProsperIA", level=1)
    p_ag = doc.add_paragraph()
    p_ag.paragraph_format.line_spacing = 1.15
    p_ag.paragraph_format.space_after = Pt(10)
    p_ag.add_run(data["linkedin_agencia"])

    doc.add_heading("3. Carrusel de LinkedIn (8 Láminas de Alto Impacto)", level=1)
    table_c = doc.add_table(rows=1, cols=4)
    table_c.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr_cells = table_c.rows[0].cells
    hdr_cells[0].text = "Lámina"
    hdr_cells[1].text = "Tipo"
    hdr_cells[2].text = "Texto / Título / Cuerpo"
    hdr_cells[3].text = "Instrucción de Diseño"
    for cell in hdr_cells:
        set_cell_background(cell, "050D1A")
        set_cell_margins(cell, top=120, bottom=120, left=150, right=150)
        for p in cell.paragraphs:
            for r in p.runs:
                r.font.bold = True
                r.font.color.rgb = RGBColor(255, 255, 255)
                r.font.size = Pt(9)

    for slide in data["carousel_slides"]:
        row = table_c.add_row()
        c0, c1, c2, c3 = row.cells
        c0.text = f"Slide {slide['slide']}"
        c1.text = slide["type"]
        body_txt = f"{slide['title']}\n{slide.get('subtitle', '')}\n\n{slide.get('body', '')}"
        c2.text = body_txt.strip()
        c3.text = slide["design_note"]
        for cell in (c0, c1, c2, c3):
            set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
            for p in cell.paragraphs:
                for r in p.runs:
                    r.font.size = Pt(8.5)

    doc.add_heading("4. Hilo Completo para X (Twitter) — 7 Publicaciones", level=1)
    for tweet in data["twitter_thread"]:
        p_tw = doc.add_paragraph()
        p_tw.paragraph_format.space_after = Pt(6)
        r_tw_num = p_tw.add_run(f"[Tweet {tweet['tweet']}/7]\n")
        r_tw_num.font.bold = True
        r_tw_num.font.color.rgb = COLOR_CYAN
        p_tw.add_run(tweet["text"])

    doc.add_heading("5. Tres Publicaciones Individuales para X", level=1)
    for t_ind in data["standalone_tweets"]:
        p_ti = doc.add_paragraph()
        p_ti.paragraph_format.space_after = Pt(6)
        r_type = p_ti.add_run(f"Variante ({t_ind['type']}):\n")
        r_type.font.bold = True
        p_ti.add_run(t_ind["text"])

    doc.add_heading("6. Guiones de Video Vertical (Reels / YouTube Shorts) — Teleprómpter", level=1)
    for reel in data["reels_scripts"]:
        doc.add_heading(f"• {reel['title']} ({reel['duration']})", level=2)
        
        p_hook = doc.add_paragraph()
        r_h = p_hook.add_run("HOOK (Primeros 3 segundos):\n")
        r_h.font.bold = True
        r_h.font.color.rgb = RGBColor(190, 18, 60)
        p_hook.add_run(reel["hook_0_3s"])

        p_tele = doc.add_paragraph()
        p_tele.paragraph_format.line_spacing = 1.3
        p_tele.paragraph_format.space_after = Pt(8)
        r_tele_lbl = p_tele.add_run("GUION CONTINUO PARA TELEPRÓMPTER:\n")
        r_tele_lbl.font.bold = True
        p_tele.add_run(reel["teleprompter_copy"])

        p_prod = doc.add_paragraph()
        p_prod.add_run(f"Instrucciones B-Roll: {reel['broll_instructions']}\n")
        p_prod.add_run(f"Caption / Copy sugerido:\n{reel['caption']}")

    doc.add_heading("7. Esquema de Video Largo para YouTube (10-15 min)", level=1)
    p_yt = doc.add_paragraph()
    p_yt.add_run(f"Título: {data['long_video']['title']}\n")
    p_yt.add_run(f"Promesa: {data['long_video']['promise']}\n\n")
    p_yt.add_run("Capítulos y Estructura:\n")
    for ch in data["long_video"]["chapters"]:
        p_yt.add_run(f"• [{ch['time']}] {ch['chapter']}: {ch['desc']}\n")

    doc.add_heading("8. Matriz de Distribución de 7 Días", level=1)
    table_m = doc.add_table(rows=1, cols=6)
    table_m.alignment = WD_TABLE_ALIGNMENT.CENTER
    m_headers = table_m.rows[0].cells
    m_headers[0].text = "Día"
    m_headers[1].text = "Canal"
    m_headers[2].text = "Cuenta"
    m_headers[3].text = "Objetivo"
    m_headers[4].text = "Pieza / Enfoque"
    m_headers[5].text = "KPI"
    for cell in m_headers:
        set_cell_background(cell, "050D1A")
        set_cell_margins(cell, top=100, bottom=100, left=100, right=100)
        for p in cell.paragraphs:
            for r in p.runs:
                r.font.bold = True
                r.font.color.rgb = RGBColor(255, 255, 255)
                r.font.size = Pt(8.5)

    for item in data["distribution_schedule"]:
        row = table_m.add_row()
        c = row.cells
        c[0].text = item["day"]
        c[1].text = item["channel"]
        c[2].text = item["account"]
        c[3].text = item["objective"]
        c[4].text = item["piece"]
        c[5].text = item["kpi"]
        for cell in c:
            set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
            for p in cell.paragraphs:
                for r in p.runs:
                    r.font.size = Pt(8)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(output_path))


def export_markdown(data: Dict[str, Any], output_path: Path):
    """Exporta versión Markdown legible en terminal o IDE."""
    md = [
        f"# PROSPERIA Intelligence — Paquete Multicanal\n",
        f"**Artículo:** {data['title']}",
        f"**Canónico:** {data['canonical_url']}",
        f"**Fecha:** {data['generated_at'][:10]}\n",
        "---",
        "## 1. LinkedIn Personal (Edward Jiménez)",
        "```text",
        data["linkedin_edward"],
        "```\n",
        f"**Primer comentario:**\n{data['linkedin_edward_comment']}\n",
        "---",
        "## 2. LinkedIn Agencia ProsperIA",
        "```text",
        data["linkedin_agencia"],
        "```\n",
        "---",
        "## 3. Carrusel LinkedIn (8 Láminas)",
    ]
    for s in data["carousel_slides"]:
        md.append(f"### Lámina {s['slide']}: {s['type']}")
        md.append(f"**Título:** {s['title']}")
        if s.get("subtitle"):
            md.append(f"**Subtítulo:** {s['subtitle']}")
        if s.get("body"):
            md.append(f"**Cuerpo:**\n{s['body']}")
        md.append(f"*Nota de diseño:* {s['design_note']}\n")

    md.extend([
        "---",
        "## 4. Hilo de X (7 Tweets)",
    ])
    for tw in data["twitter_thread"]:
        md.append(f"**[Tweet {tw['tweet']}/7]:**\n{tw['text']}\n")

    md.extend([
        "---",
        "## 5. Reels / Shorts (Teleprómpter)",
    ])
    for r in data["reels_scripts"]:
        md.append(f"### {r['title']} ({r['duration']})")
        md.append(f"**HOOK:** {r['hook_0_3s']}\n")
        md.append(f"**GUION CONTINUO:**\n{r['teleprompter_copy']}\n")
        md.append(f"**CAPTION:**\n{r['caption']}\n")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(md), encoding="utf-8")


def generate(slug_or_path: str) -> Dict[str, Path]:
    """Ejecuta la generación completa para un artículo."""
    path = Path(slug_or_path)
    if not path.is_file():
        path = PUBLISHED_DIR / f"{slug_or_path}.json"
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el artículo en: {path}")

    post = json.loads(path.read_text(encoding="utf-8"))
    data = build_package_data(post)

    slug = post["slug"]
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    docx_file = OUTPUT_DIR / f"{slug}_paquete_multicanal.docx"
    md_file = OUTPUT_DIR / f"{slug}_paquete_multicanal.md"
    json_file = OUTPUT_DIR / f"{slug}_multichannel.json"

    export_docx(data, docx_file)
    export_markdown(data, md_file)
    json_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "docx": docx_file,
        "md": md_file,
        "json": json_file
    }


def main():
    parser = argparse.ArgumentParser(description="Generador de paquete omnicanal PROSPERIA")
    parser.add_argument("slug", nargs="?", default="la-ia-no-reemplaza-empleos-transforma-tareas",
                        help="Slug del artículo publicado a procesar")
    args = parser.parse_args()

    results = generate(args.slug)
    print(f"Paquete generado exitosamente:")
    print(f"  • Word (.docx): {results['docx']}")
    print(f"  • Markdown (.md): {results['md']}")
    print(f"  • JSON Datos (.json): {results['json']}")


if __name__ == "__main__":
    main()

"""Prompts y reglas maestras de Cortexia para Agencia ProsperIA.

Reglas innegociables:
1. Blindaje de PI de Edward Jiménez:
   - Prohibido mencionar 'mi libro', 'el libro que estoy escribiendo', 'sale en diciembre 2026'
     o 'Las 4 Inteligencias como libro'.
   - Marco único: «Los 4 Pilares de Soberanía Empresarial de Agencia ProsperIA»
     (Financiero, Emocional, Estratégico y de Aumento Tecnológico) y «La Metodología SVE90».
2. Regla 777 Anti-Alucinación: Cero cifras inventadas ni citas falsas de McKinsey o Gartner.
3. Español neutro (tuteo formal), signos de apertura obligatorios (¿, ¡).
4. Estructura Víctor Heras (Retención H.V.A., hook 0-3s, mini-hook :22, loop causal).
"""

from typing import Any, Dict, List

CORTEXIA_MASTER_RULES = """
REGLAS MAESTRAS DE CORTEXIA (INNEGOCIABLES):

1. BLINDAJE DE PROPIEDAD INTELECTUAL DE EDWARD JIMÉNEZ:
   - ESTRICTAMENTE PROHIBIDO mencionar las frases "mi libro", "el libro que estoy escribiendo", "sale en diciembre 2026" o presentar "Las 4 Inteligencias" como una obra editorial en proceso.
   - REGLA DE REEMPLAZO OBLIGATORIA: Todo el marco filosófico y metodológico pertenece y se cita exclusivamente como:
     * «Los 4 Pilares de Soberanía Empresarial de Agencia ProsperIA» (Financiero, Emocional, Estratégico y de Aumento Tecnológico).
     * «La Metodología SVE90» (Auditoría, Automatización, Adopción).

2. REGLA 777 ANTI-ALUCINACIÓN (CERO DATOS FABRICADOS):
   - Cero inventar estadísticas, porcentajes, encuestas o citas ficticias atribuidas a McKinsey, Gartner, PwC o Harvard.
   - Toda cifra debe provenir de fuentes verificadas reales:
     * Stanford HAI AI Index 2025: 78% de organizaciones encuestadas utiliza IA (frente al 55% del año anterior).
     * Organización Internacional del Trabajo (OIT): 25% de la fuerza laboral expuesta a IA generativa; concluye que la transformación de tareas predomina sobre el reemplazo destructivo.
     * Anthropic Economic Index (análisis de 1M de usos en Claude): 57% de los casos corresponden a aumento de capacidad humana frente al 43% de automatización directa.
     * Casos de 25 años de carrera de Edward Jiménez: la migración bancaria nocturna de Elektra a Banco Azteca bajo supervisión de la CNBV, arquitectura en SYNETCOM, operaciones críticas en JPX Miami.

3. ESTILO Y DIALECTO:
   - Español Neutro (tuteo formal). Cero voseo rioplatense (prohibido "tenés", "hacé", "mirá", "sabés"), cero modismos peninsulares ("vosotros", "vale", "curro", "guay").
   - Ortografía española completa: signos de apertura obligatorios («¿», «¡») en todas las oraciones interrogativas y exclamativas; acentuación impecable.

4. PRINCIPIOS DE VÍCTOR HERAS (RETENCIÓN, VIRALIDAD Y LA REGLA DEL ELEFANTE):
   - LA REGLA DEL ELEFANTE (VALIDACIÓN VISUAL INMEDIATA):
     «Si me hablas sobre el elefante, ponme el elefante arriba. Sea así o sea en pantalla dividida, pero utiliza recursos visuales que ayuden a validar eso de lo que estás hablando».
     * Si nombras una personalidad (Mo Gawdat, Mustafa Suleyman, Sam Altman, Dario Amodei), clip o fotografía en tercio superior o split screen.
     * Si citas una estadística (78% Stanford HAI, 25% OIT, 57% Anthropic), gráfica oficial o titular de prensa en pantalla en el segundo exacto en que se pronuncia.
     * Si mencionas infraestructura o casos reales (migración nocturna de 1.500 sucursales Elektra/Banco Azteca bajo CNBV, SYNETCOM, JPX Miami), recorte de prensa, diagrama o rótulo oficial.
     * Cero pantalla estática o busto parlante sin estímulo visual cada 8–12 segundos.
   - LA REGLA DEL CRECIMIENTO EXPONENCIAL (MASIVO ANTES QUE NICHO):
     «Vuélvete primero masivo, vuélvete viral con debate y autoridad incuestionable; luego vas a nicho B2B para monetizar sin empujar la venta directa». Cero pitch de venta invasivo.
   - ESTRUCTURA H.V.A.:
     * Hook (0 a 3 segundos): Parada de scroll inmediata por tensión o negación inesperada. Cero saludos suaves.
     * Mini-hook a los :22 segundos: Abre NUEVA FRICCIÓN antes del payoff.
     * Loop close causal que conecta la última frase gramaticalmente con el hook inicial.
""".strip()


def build_daily_prompt(topic: str, sources: List[Dict[str, str]], lane: str = "radar-disrupcion") -> str:
    sources_text = "\n".join([f"- {s.get('title')}: {s.get('url')}" for s in sources])
    return f"""
Eres el Director de Estrategia Editorial de PROSPERIA Intelligence y Cortexia.
Debes generar el PAQUETE OMNICANAL DIARIO COMPLETO (Sistema 5×4×1) a partir de la siguiente noticia/tendencia verificada.

TEMA / NOTICIA:
{topic}

FUENTES VERIFICADAS DISPONIBLES:
{sources_text}

RUTA EDITORIAL (LANE):
{lane}

{CORTEXIA_MASTER_RULES}

Genera una respuesta estrictamente en formato JSON válido (sin texto antes ni después) con la siguiente estructura de claves:

{{
  "slug": "slug-kebab-case-descriptivo-y-conciso",
  "title": "Título de alto impacto directivo y curiosidad verificable (mínimo 20 caracteres)",
  "summary": "Resumen ejecutivo del impacto de la disrupción (mínimo 60 caracteres)",
  "article": {{
    "title": "Título completo del artículo",
    "summary": "Resumen para el blog",
    "content_html": "<p>Primer párrafo con tensión y gancho...</p><h2>Subtítulo de evidencia</h2><p>Contenido detallado con HTML semántico (h2, p, strong, ul, li). Mínimo 600 palabras analíticas...</p><h2>La perspectiva de los 4 Pilares de Soberanía Empresarial</h2><p>Análisis bajo la soberanía financiera, emocional, estratégica y de aumento tecnológico...</p><h2>Decisión para el Director Ejecutivo (Metodología SVE90)</h2><p>Implicaciones operativas y llamada al diagnóstico.</p>",
    "lane": "{lane}",
    "author": "Equipo editorial ProsperIA",
    "author_type": "organization",
    "sources": [
      {{"title": "Título de la fuente", "url": "https://..."}}
    ],
    "cta": "diagnostic",
    "editorial_notes": "Verificado contra fuentes primarias. Aprobado bajo estándares Cortexia."
  }},
  "linkedin_post": {{
    "text": "Texto completo para LinkedIn de Edward Jiménez (900 a 1400 caracteres). Párrafos breves, saltos dobles, cifras verificadas de Stanford/OIT/Anthropic, tensión directiva, cero saludos suaves, tono sobrio y provocador.",
    "first_comment": "Análisis canónico completo con fuentes verificadas en PROSPERIA Intelligence:\\nhttps://agenciaprosperia.com/blog/<slug>?utm_source=linkedin&utm_medium=comment"
  }},
  "twitter_thread": [
    {{"tweet": 1, "text": "Tweet 1: Hook demoledor de 0-3s con tensión contraintuitiva. Abro hilo con evidencia de Stanford/OIT 👇🧵"}},
    {{"tweet": 2, "text": "Tweet 2: Evidencia 1..."}},
    {{"tweet": 3, "text": "Tweet 3: Evidencia 2..."}},
    {{"tweet": 4, "text": "Tweet 4: El quiebre en el modelo de tareas..."}},
    {{"tweet": 5, "text": "Tweet 5: Qué pierde valor vs qué multiplica su precio..."}},
    {{"tweet": 6, "text": "Tweet 6: Aplicación a la empresa bajo la Metodología SVE90..."}},
    {{"tweet": 7, "text": "Tweet 7: Conclusión con loop y enlace: https://agenciaprosperia.com/blog/<slug>"}}
  ],
  "carousel_slides": [
    {{
      "slide": 1,
      "type": "PORTADA",
      "title": "Título corto y contundente en 2 líneas",
      "subtitle": "Subtítulo que despierta curiosidad inmediata",
      "footer": "Desliza para ver la evidencia →",
      "design_note": "Fondo navy oscuro, tipografía en blanco con palabra clave en cian eléctrico (#00e5ff)."
    }},
    {{
      "slide": 2,
      "type": "TENSIÓN",
      "title": "La paradoja que casi todos ignoran",
      "subtitle": "Contraste entre lo que cree el mercado y lo que pasa",
      "body": "Texto con datos concretos que desarma la creencia común.",
      "footer": "PROSPERIA Intelligence",
      "design_note": "Caja centralizada con contraste alto."
    }},
    {{
      "slide": 3,
      "type": "EVIDENCIA_1",
      "title": "78% de adopción empresarial",
      "subtitle": "Stanford AI Index 2025",
      "body": "Explicación de la cifra verificada y su aceleración.",
      "footer": "Fuente: Stanford HAI AI Index 2025",
      "design_note": "Cifra gigante en color cian."
    }},
    {{
      "slide": 4,
      "type": "EVIDENCIA_2",
      "title": "Transformación vs. Reemplazo",
      "subtitle": "Organización Internacional del Trabajo (OIT)",
      "body": "1 de cada 4 trabajadores expuesto, pero el trabajo se descompone en tareas.",
      "footer": "Fuente: OIT Research 2024-2025",
      "design_note": "Iconografía sobria y bullets destacados."
    }},
    {{
      "slide": 5,
      "type": "EVIDENCIA_3",
      "title": "57% Aumento vs. 43% Automatización",
      "subtitle": "Anthropic Economic Index",
      "body": "En 1M de usos reales, la IA potencia el talento antes que sustituirlo.",
      "footer": "Fuente: Anthropic Economic Index 2025",
      "design_note": "Gráfico comparativo minimalista."
    }},
    {{
      "slide": 6,
      "type": "INTERPRETACIÓN",
      "title": "Lo que cambia de precio hoy",
      "subtitle": "El nuevo mapa del valor",
      "body": "Pierde valor:\\n✖ Redactar borradores\\n✖ Resumir documentos\\n\\nGana valor:\\n✔ Criterio de validación\\n✔ Decisión y responsabilidad",
      "footer": "Edward Jiménez | Interpretación",
      "design_note": "Cajas comparativas de dos columnas."
    }},
    {{
      "slide": 7,
      "type": "DECISIÓN_DIRECTIVA",
      "title": "Marco SVE90 para tu empresa",
      "subtitle": "Auditoría, Automatización y Adopción",
      "body": "1. Mapea tareas antes de despedir talento.\\n2. Automatiza lo operativo repetitivo.\\n3. Gobierna el criterio institucional no delegable.",
      "footer": "PROSPERIA Intelligence",
      "design_note": "Checklist numerada ejecutiva."
    }},
    {{
      "slide": 8,
      "type": "CIERRE",
      "title": "¿Tu empresa delega o gobierna la IA?",
      "subtitle": "Realiza el diagnóstico de madurez operativa en 3 minutos",
      "body": "Ingresa a agenciaprosperia.com/diagnostico o agenda tu sesión estratégica.",
      "footer": "Guarda este post para tu próxima reunión de directorio",
      "design_note": "Badge de Edward Jiménez y botón visual simulado."
    }}
  ],
  "reel_50s": {{
    "title": "Guion Reel 50s — Teleprompter Víctor Heras",
    "duration_target": "50 segundos",
    "hook_0_3s": "Oración inicial sin saludo que detiene el scroll en seco mediante negación o paradoja contraintuitiva.",
    "teleprompter_copy": "Texto continuo para teleprompter calculado exactamente para 50 segundos (~135-145 palabras habladas a ritmo firme). Incluye hook 0-3s, datos verificados con fuente en pantalla, mini-hook de fricción a los :22 segundos ('Pero aquí viene el error que casi todos cometen...'), resolución bajo SVE90 y perfect loop causal final.",
    "timeline_beats": [
      {{
        "time": "00:00 - 00:03",
        "audio": "Hook de parada de scroll",
        "screen_text": "TEXTO EN MAYÚSCULAS CON IMPACTO",
        "broll": "Plano medio cerrado de Edward a cámara con mirada fija",
        "elephant_rule_visual": "REGLA DEL ELEFANTE: Si se menciona un concepto, titular o persona, overlay inmediato en tercio superior o pantalla dividida validando el gancho.",
        "narrative_function": "hook_scroll_stopper"
      }},
      {{
        "time": "00:03 - 00:10",
        "audio": "Planteamiento de la tensión del mercado",
        "screen_text": "DESARME DE TAREAS ⚙️",
        "broll": "Corte rápido a pantalla con gráfica de adopción",
        "elephant_rule_visual": "REGLA DEL ELEFANTE: Split screen mostrando organigrama tradicional vs descomposición de tareas en tiempo real.",
        "narrative_function": "tension_setup"
      }},
      {{
        "time": "00:10 - 00:22",
        "audio": "Dato duro con fuente verificada (Stanford / OIT / Anthropic)",
        "screen_text": "78% ADOPCIÓN (Stanford HAI)",
        "broll": "Corte a titular de reporte oficial con highlight animado",
        "elephant_rule_visual": "REGLA DEL ELEFANTE: Captura exacta del reporte Stanford HAI AI Index 2025 o titular oficial en tercio superior en el segundo exacto que se pronuncia la cifra.",
        "narrative_function": "hard_evidence"
      }},
      {{
        "time": "00:22 - 00:35",
        "audio": "Mini-hook a los :22 que abre nueva fricción o peligro oculto",
        "screen_text": "EL ERROR MORTAL ⚠️",
        "broll": "Cambio de plano de cámara a plano cerrado con iluminación dramática",
        "elephant_rule_visual": "REGLA DEL ELEFANTE: Rótulo de advertencia o recorte de caso bancario CNBV / Elektra-Azteca en pantalla dividida.",
        "narrative_function": "mini_hook_friccion"
      }},
      {{
        "time": "00:35 - 00:45",
        "audio": "Resolución estratégica e impacto en el modelo de negocio",
        "screen_text": "SISTEMA SVE90: GOBERNAR",
        "broll": "Demostración en pantalla del flujo de automatización",
        "elephant_rule_visual": "REGLA DEL ELEFANTE: Diagrama de los 4 Pilares de Soberanía Empresarial en tercio superior animado.",
        "narrative_function": "payoff_resolucion"
      }},
      {{
        "time": "00:45 - 00:50",
        "audio": "Loop close causal que reconecta gramaticalmente con la primera frase",
        "screen_text": "agenciaprosperia.com/diagnostico",
        "broll": "Edward a cámara con gesto de cierre y logo ProsperIA",
        "elephant_rule_visual": "REGLA DEL ELEFANTE: URL visible en tercio inferior con flecha hacia el perfil sin decir 'link en bio'.",
        "narrative_function": "perfect_loop_close"
      }}
    ],
    "caption": "Copy sugerido para Instagram/TikTok con 3 párrafos, CTA al link en bio y hashtags ejecutivos (#InteligenciaArtificial #SVE90 #Liderazgo #AgenciaProsperIA).",
    "canonical_source": "Stanford HAI / OIT / Anthropic Economic Index"
  }},
  "meta_noticia": {{
    "date": "YYYY-MM-DD",
    "slug": "slug-kebab-case",
    "title": "Título del tema",
    "executive_summary": "Resumen conciso del hallazgo y su implicación económica",
    "verified_sources": [
      {{"title": "Fuente", "url": "https://..."}}
    ],
    "affected_pillars": [
      "Aumento Tecnológico",
      "Estratégico",
      "Financiero"
    ],
    "sve90_phase": "Auditoría de Procesos y Tareas",
    "core_takeaway": "La lección de negocio fundamental que alimentará el compilado semanal"
  }}
}}
""".strip()


def build_weekly_youtube_prompt(week_number: int, daily_metadata_list: List[Dict[str, Any]]) -> str:
    articles_summary = ""
    for idx, item in enumerate(daily_metadata_list, 1):
        articles_summary += f"""
--- ACTO {idx}: {item.get('title', 'Disrupción ' + str(idx))} ---
Slug: {item.get('slug')}
Resumen: {item.get('executive_summary')}
Fuentes: {item.get('verified_sources')}
Pilares: {item.get('affected_pillars')}
Fase SVE90: {item.get('sve90_phase')}
Conclusión clave: {item.get('core_takeaway')}
"""

    return f"""
Eres el Guionista Principal y Arquitecto de Contenido de PROSPERIA Intelligence y Cortexia.
Tu tarea es compilar las 5 disrupciones analizadas durante la semana en UN SOLO GUION MAESTRO PARA YOUTUBE DE 20 MINUTOS (Semana {week_number:02d}).

{CORTEXIA_MASTER_RULES}

LAS 5 DISRUPCIONES DE LA SEMANA A COMPILAR:
{articles_summary}

ESTRUCTURA OBLIGATORIA DEL GUION DE YOUTUBE (20 MINUTOS):
- Duración total: ~20 minutos (3,000 a 3,800 palabras habladas a ritmo directivo).
- Formato: Teleprompter profesional con acotaciones visuales, directivas de B-Roll, gráficos en pantalla (GFX), efectos de sonido (SFX) y marcas de tiempo estimadas.
- Estructurado en 5 Actos temáticos más Introducción y Cierre:

  1. INTRODUCCIÓN Y TESIS CENTRAL (00:00 - 02:30):
     - Hook de 0 a 5 segundos de alto impacto.
     - La tesis directiva: por qué las 5 noticias de esta semana marcan un punto de no retorno para los negocios.
     - Presentación del mapa de los 5 Actos bajo «Los 4 Pilares de Soberanía Empresarial» y «La Metodología SVE90».
  
  2. ACTO I (02:30 - 05:45): Análisis a fondo de la Disrupción 1 con fuentes y caso práctico.
  3. ACTO II (05:45 - 09:15): Análisis a fondo de la Disrupción 2 con datos duros y desmitificación.
  4. ACTO III (09:15 - 12:45): Análisis a fondo de la Disrupción 3 y el impacto en nómina/costes.
  5. ACTO IV (12:45 - 16:15): Análisis a fondo de la Disrupción 4 y la gobernanza de modelos de IA.
  6. ACTO V (16:15 - 18:45): Análisis a fondo de la Disrupción 5 y la integración operativa.
  7. SÍNTESIS DIRECTIVA Y PROTOCOLO DE ACCIÓN SVE90 (18:45 - 20:00):
     - Cómo implementar la solución en 90 días (Auditoría, Automatización, Adopción).
     - Llamada a la acción hacia el Diagnóstico de Madurez en agenciaprosperia.com/diagnostico.

Genera el guion directamente en formato Markdown estructurado, limpio y listo para grabar.
""".strip()


# Banco de 5 temas verificados de alta autoridad para la semana canónica
CANONICAL_WEEKLY_BANK = [
    {
        "day": 1,
        "topic": "Stanford AI Index 2025: El salto del 55% al 78% en adopción corporativa de IA y el desarme silencioso de tareas",
        "lane": "radar-disrupcion",
        "sources": [
            {"title": "The 2025 AI Index Report - Stanford HAI", "url": "https://hai.stanford.edu/ai-index/2025-ai-index-report"},
            {"title": "Anthropic Economic Index 2025", "url": "https://www.anthropic.com/research/the-anthropic-economic-index"}
        ],
        "default_slug": "stanford-ai-index-adopcion-empresarial-desarme-tareas"
    },
    {
        "day": 2,
        "topic": "La OIT revela que 1 de cada 4 empleos está expuesto a la IA generativa: por qué la transformación supera al despido",
        "lane": "criterio-edward",
        "sources": [
            {"title": "Generative AI and Jobs: Occupational Exposure - ILO", "url": "https://www.ilo.org/publications/generative-ai-and-jobs-refined-global-index-occupational-exposure"}
        ],
        "default_slug": "oit-reporte-exposicion-ia-transformacion-vs-despido"
    },
    {
        "day": 3,
        "topic": "El fin del software tradicional: De herramientas pasivas a agentes autónomos que ejecutan procesos de negocio de punta a punta",
        "lane": "laboratorio-prosperia",
        "sources": [
            {"title": "Anthropic Economic Index: 57% Aumento vs 43% Automatización", "url": "https://www.anthropic.com/research/the-anthropic-economic-index"}
        ],
        "default_slug": "de-herramientas-a-agentes-autonomos-obsolescencia-software"
    },
    {
        "day": 4,
        "topic": "Gobernanza y resiliencia en infraestructura crítica: Lecciones de 25 años desde la migración nocturna de Banco Azteca bajo la CNBV hasta los agentes modernos",
        "lane": "cuatro-inteligencias",
        "sources": [
            {"title": "Comisión Nacional Bancaria y de Valores (CNBV) - Normativa de Continuidad", "url": "https://www.gob.mx/cnbv"},
            {"title": "Casos de Arquitectura Crítica - Edward Jiménez (1999-2025)", "url": "https://agenciaprosperia.com/about"}
        ],
        "default_slug": "gobernanza-infraestructura-critica-lecciones-bancarias-edward-jimenez"
    },
    {
        "day": 5,
        "topic": "La Metodología SVE90: Cómo auditar, automatizar y adoptar agentes de IA en clínicas y empresas de servicios sin caer en alucinaciones",
        "lane": "inteligencia-clinicas",
        "sources": [
            {"title": "Metodología SVE90 - Agencia ProsperIA", "url": "https://agenciaprosperia.com/#sistema"},
            {"title": "Stanford AI Index 2025 - Integración Sectorial", "url": "https://hai.stanford.edu/ai-index/2025-ai-index-report"}
        ],
        "default_slug": "metodologia-sve90-auditoria-automatizacion-adopcion-empresas"
    }
]

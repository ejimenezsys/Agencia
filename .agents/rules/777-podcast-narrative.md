---
trigger: glob
name: 777-podcast-narrative
description: Reglas narrativas para source-docs de podcast NotebookLM (membership, eric speech, youtube). Path-scoped — se auto-carga al editar `<proyecto>/podcasts/**` o `DOCS/FRAMEWORKS/PODCAST_NOTEBOOKLM/**`.
globs: DOCS/CONTENIDO/PROYECTOS/**/podcasts/**,DOCS/FRAMEWORKS/PODCAST_NOTEBOOKLM/**,.agents/skills-manual/777-membership-podcast/**,.agents/skills-manual/777-author-speech-podcast/**,.agents/skills-manual/777-youtube-podcast/**
---

# 777 Podcast Narrative — Reglas de source-docs NotebookLM

Esta rule consolida los principios narrativos que aplican a cualquier source-doc producido por las skills de Capa A. Las skills NO duplican estas reglas en su SKILL.md — solo citan esta rule en STEP 0.

## 1. Framework compartido — referencias maestras

Toda skill de podcast lee al arrancar (en paralelo):

- `DOCS/FRAMEWORKS/PODCAST_NOTEBOOKLM/MASTER_STORYTELLING_TECHNIQUES.md`
- `DOCS/FRAMEWORKS/PODCAST_NOTEBOOKLM/MASTER_LOOP_ARCHITECTURE.md`
- `DOCS/FRAMEWORKS/PODCAST_NOTEBOOKLM/MASTER_HUMOR_INJECTION.md`
- `DOCS/FRAMEWORKS/PODCAST_NOTEBOOKLM/_archive/ERICISM.md`
- `DOCS/FRAMEWORKS/PODCAST_NOTEBOOKLM/PODCAST_INSTRUCTIONS.md`

Si alguna falta, reportar antes de avanzar (per `777-no-fabrication.md`).

## 2. Investigation framing — innegociable

Los hosts del podcast son insiders del equipo cercano de Eric, fundador del proyecto. Pasaron tiempo con él, investigaron juntos, tienen conversaciones directas y hablan del proyecto desde ese contacto. Todo source audience-facing debe presentar a Eric como fundador/creador cuando aporte contexto, sin escribir instrucciones gramaticales sobre punto de vista o persona narrativa.

**SIEMPRE:**
- "Eric nos contó..."
- "Después de hablar con Eric..."
- "Lo que descubrimos en nuestra investigación..."
- "Eric confirmó que esto cambia todo..."

**NUNCA:**
- "Según el documento..."
- "El video muestra..."
- "La fuente indica..."
- "El contenido dice..."
- Cualquier referencia a YouTube, transcript, doc de membresía, archivo, página de ventas.

Razón: el oyente debe sentir que está escuchando una conversación real con gente que vio a Eric en persona, no un análisis de material. Cualquier referencia a "fuente" rompe la inmersión.

## 3. Loop architecture — 2 modos (mapean a NotebookLM Length toggle)

NotebookLM solo expone `Short` o `Default` como controles de duración. La arquitectura de loops se ajusta a esos dos modos:

| Modo | NotebookLM Length | Source palabras | Audio resultante | Arch de loops | Loops abiertos máx simultáneos |
|---|---|---|---|---|---|
| **Short** | `Short` | 400-700 | ~3-5 min | 1 episode + 2 micro + 0-1 section | 2 |
| **Default (Long)** | `Default` | 1500-2500 | ~10-15 min | 1 episode + 1 medium + 2-3 section + micro density 2-3 por párrafo | 3 |

Reglas duras (heredadas de `MASTER_LOOP_ARCHITECTURE.md`):
- Cada loop que abre DEBE cerrar antes del final.
- Episode loop cierra en el último tercio, NO en la última oración.
- Cerrar al menos un loop antes del midpoint para construir confianza.

## 4. Eric quoted — reglas sagradas

Cuando una oración del source aparece **entre comillas** atribuida a Eric, NotebookLM la lee literal. Eso permite controlar la voz de Eric en el podcast a través de quotes precisas.

Reglas:
- 2-4 Eric quotes por episodio máximo (1-2 si el episodio es ≤3 min).
- Cada quote NUEVA en voz del autor declarado, no copy-paste del voice bank. Las frases firmadas son referencia de estilo (ritmo, repetición triple, metáforas vivas), no banco de frases para pegar.
- Ubicación: después de revelación grande, antes de cerrar un loop, durante la sección método/sistema. NUNCA en el bloque OPENING.
- Forma: 1-2 oraciones máximo, punchy, citables.
- Si el doc fuente YA tiene una quote literal de Eric (ej: membresía con cita declarada), preservarla verbatim — no reescribir.

## 5. Tono cortexia — humor herencia del proyecto

El tono de cada podcast hereda del rango declarado en `<proyecto>/01_reglas_negocio.md §3` (per `.agents/rules/777-tono-y-humor.md`). NO se elige episodio por episodio salvo override hacia abajo (más serio que el rango).

Para cortexia (rango actual: por verificar al arrancar) — el humor en hosts es contagioso de Eric: directo, sin corporativo, claims sin hedging, mezcla frases cortas y largas. Pero NUNCA copiar firmas exactas de Eric fuera de quotes.

## 6. Cierre obligatorio — siempre energía positiva

Cada episodio termina con sección "Stay close to Eric" en este orden:

1. **Pico emocional** — puede ser quote de Eric (incluso provocadora), pero NO la última línea.
2. **Empoderamiento** — "Tú puedes. Esto es para ti. No es para expertos. Es para ti, hoy."
3. **CTA claro** — exactamente qué hacer: mira la descripción, haz clic, asegura tu lugar.
4. **Línea de cierre cálida** — la ÚLTIMA frase debe levantar al oyente. "Nos vemos adentro." "Eres exactamente la persona para esto." "Te esperamos."

**RED FLAGS — reescribir si el episodio termina con:**
- Quote provocadora de Eric como última línea (moverla antes).
- Advertencia tipo "si no haces X vas a perder Y".
- Pregunta dudosa colgada.
- Línea factual plana sin levante emocional.
- Cualquier frase que haga sentir al oyente chico, tarde, excluido o inseguro.

## 7. Voz anónima vs Eric fundador presente — resolución

Tensión real con la regla universal de "voz anónima de autoridad" en outputs audience-facing. Resolución para podcasts:

- **Hosts son anónimos** — no se nombran ni se identifican como personas concretas. Son "el equipo cercano de Eric".
- **Eric SÍ se nombra explícito** — es el fundador, el ancla y la autoridad citada. Esto es por diseño del formato.
- **No exponer instrucciones de gramática narrativa** — el source debe explicar quién es Eric y por qué importa; no debe dejar frases operativas que NotebookLM pueda leer como parte del audio.
- **Cero referencia a fuente material** — los hosts hablan como si lo hubieran charlado con Eric, no como si lo hubieran leído de un doc.

Esto NO viola la regla de voz anónima — la regla aplica al CREADOR/CANAL del output, no a los actores de la narrativa interna.

## 8. Reglas 777 audience-facing — modo soft

El detector Pinterest de 12 checks de `777-human-to-human.md` está calibrado para video corto, NO para prosa de podcast 5-min (~700 palabras). Para podcasts aplican estos sub-principios:

- **Cero anglicismos sin glosario** — test DRAE + tía del pueblo. Anglicismos largos se traducen; siglas técnicas con paréntesis al primer uso.
- **Cero tells de IA** — vocabulario corporativo hueco prohibido (verbos pretenciosos, adjetivos huecos, sustantivos pretenciosos, frases enlatadas). Lista canónica en `777-human-to-human.md` §"Vocabulario corporativo hueco".
- **Tuteo neutro consistente** — hosts hablan en tuteo singular sin mezclar dialectos.
- **Test del Amigo cualitativo** — leer el source en voz alta antes de aprobar; si suena a anuncio de radio o a profesor dando cátedra, reescribir.
- **Cero auto-pregunta + auto-respuesta** retórica.
- **Cero paralelismos sintácticos de 3+ líneas consecutivas idénticas.**

NO aplican (porque no traducen 1:1 a prosa larga):
- C5 categories de Sec 1A (son para video corto).
- Cap de palabras por línea.
- Test "texto cabe en audio" (es de kinetic typography).

## 9. Output canónico de toda skill de Capa A

Toda skill de podcast guarda en:

```
DOCS/CONTENIDO/PROYECTOS/<proyecto>/podcasts/<slug>/
├── todo.md                    progreso
├── source_raw.md              input crudo (transcript, doc, speech) — copia inmutable
├── <intermedio>.md            (opcional) UNA pasada de limpieza específica del input — ver tabla abajo
├── clarifying_questions.md    preguntas + respuestas usuario
├── source_v1.md ... vN.md     borradores
├── source_approved.md         versión final con safeguards al final
└── host_instructions.md       contenido del Focus textarea NotebookLM (≤4,800 caracteres — ver §10)
```

`<slug>` = 2-5 palabras kebab-case que describan el episodio (auto-generado, usuario aprueba).

### Nombres de archivo — INNEGOCIABLE (vocabulario cerrado)

Los 6 nombres canónicos (`todo.md`, `source_raw.md`, `clarifying_questions.md`, `source_vN.md`, `source_approved.md`, `host_instructions.md`) son **idénticos en las 3 skills de Capa A**. Cero variantes (`raw_transcript.md`, `speech_clarifying_questions.md`, `source_vN`-como-aprobado están PROHIBIDOS). El archivo final aprobado SIEMPRE se llama `source_approved.md`, sin importar en qué `vN` quedó la aprobación — esto vuelve determinístico el encadenamiento de §10 (el `nlm source add` apunta siempre a `source_approved.md`).

**Único grado de libertad — el archivo intermedio de limpieza.** Cada skill PUEDE emitir UN solo archivo intermedio entre `source_raw.md` y `source_v1.md`, con nombre específico del tipo de input. Vocabulario cerrado:

| Skill | Archivo intermedio | Qué es |
|---|---|---|
| `777-author-speech-podcast` | `speech_verbatim.md` | verbatim del speech limpio al 95% (solo typos/autocorrect) |
| `777-youtube-podcast` | `clean_transcript.md` | transcript formateado, cero cambios de contenido |
| `777-membership-podcast` | — (ninguno) | el doc de membresía ya viene curado; va directo de `source_raw.md` a `source_v1.md` |

Si una skill futura necesita otro intermedio, se agrega a esta tabla con PR a esta rule — NO se inventa ad-hoc.

## 10. Encadenamiento con `777-notebooklm-podcast`

Cuando `source_approved.md` + `host_instructions.md` están listos, la skill de Capa A confirma el encadenamiento (decisión tomada en preguntas batched al inicio del flujo):

### `host_instructions.md` = Focus textarea NotebookLM

> **Innegociable.** El contenido de `host_instructions.md` se pega literal en el campo Focus de NotebookLM. Es el parámetro de entrada al modelo de podcast, NO un doc auxiliar.

**Cap duro NotebookLM:** 741 palabras / 5,000 caracteres.
**Target conservador del sistema 777:** ≤700 palabras / ≤4,800 caracteres (buffer de 200 chars contra rechazo).

### Parámetros bloqueados al wrapper

| Parámetro | Valor default 95% | Override |
|---|---|---|
| `format` | `Deep Dive` | Solo si usuario pide explícito |
| `language` | `es-419` (español Latinoamérica) | Solo si usuario pide explícito |
| `length` | `Short` (modo Short) · `Default` (modo Long) | Sale del modo elegido en preguntas batched |
| `focus` | contenido literal de `host_instructions.md` | — |
| `source_file` | path a `source_approved.md` | — |

Defaults bloqueados eliminan re-preguntas al usuario al pasar a Capa C.

**Innegociable.** Esta rule unifica la narrativa de las 3 skills de Capa A. Cualquier divergencia entre skills se resuelve modificando ESTA rule, no las skills individuales.

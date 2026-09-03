---
name: 777-notebooklm-podcast
category: notebooklm
cadence: skill
description: Genera un podcast de audio desde NotebookLM con proyecto explícito, notebook nuevo o existente, fuente controlada por episodio, persona opcional desde VOICE_CARD.md, instrucciones de apertura/cierre y descarga del MP3 al proyecto.
disable-model-invocation: false
argument-hint: "[project-slug, notebook-id, source-path, or brief]"
allowed-tools: "Bash Read Glob AskUserQuestion"
---

# Generar podcast de audio con NotebookLM

Wrapper operativo del CLI portable `777_tools/777_notebooklm/nlm` para crear audios de NotebookLM.

Este skill NO debe lanzar audio hasta haber confirmado:

1. Proyecto y destino.
2. Paquete limpio del episodio: fuente creativa + description operativa separada.
3. Notebook nuevo o existente.
4. Fuente exacta que alimentará este episodio.
5. Persona/voz opcional.
6. Objetivo del audio.
7. Apertura exacta de los dos locutores.
8. Cierre exacto con llamada a la acción si aplica.
9. Validador del paquete con salida `PASS`.

## STEP -1 — Referencias

Leer en paralelo antes del Paso 0:

1. `FLOWS/777-notebooklm-podcast.md` — mapa de touchpoints del wrapper.
2. `.agents/rules/777-agent-convention.md` — project picker, preguntas y español neutro.
3. `.agents/rules/777-no-fabrication.md` — no inventar precios, fechas, cupos ni resultados.
4. `.agents/rules/777-human-to-human.md` — core always: el audio debe sonar como una persona hablándole a otra persona.
5. `.agents/rules/777-viral-lessons-learned.md` — core always: archivo dorado de lessons learned verificadas antes de redactar.
6. `.agents/rules/777-viewer-reward.md` — core always: promesa concreta de qué gana el oyente por seguir y actuar.
7. `.agents/rules/777-tono-y-humor.md` — core always: respetar el rango de humor declarado por el proyecto.
8. `.agents/rules/777-podcast-narrative.md` — core always: reglas de inmersión, rol de hosts y referencias a Eric como fundador.

Registrar para carga on-demand al redactar el Paso 6:

9. `.agents/rules/777-edge-of-curiosity.md` — on-demand: llevar apertura y tensión al filo de la curiosidad sin inventar.
10. `.agents/rules/777-emotional-arc.md` — on-demand: usar movidas narrativas retentivas y evitar arranques blandos.
11. `.agents/rules/777-anti-formula.md` — on-demand: detectar repetición, fórmula y cierres que suenan a plantilla.
12. `.agents/rules/777-storytelling-manifesto.md` — on-demand: priorizar historia humana antes que matriz mecánica.
13. `.agents/rules/777-viewer-empathy.md` — on-demand: revisar que cada decisión premie la atención real del oyente.

Matiz de formato: estas reglas nacieron en video corto; en podcast Deep Dive (~5 min) aplican en espíritu, no tag-por-tag: antagonista temprano, cero paráfrasis circular, loops de curiosidad, consecuencia/eco en el cierre y reward claro para el oyente.

## Principios innegociables del audio

- **Proyecto explícito siempre.** Cero proyecto activo silencioso.
- **Persona opcional siempre preguntada.** Si el usuario dice que no, seguir natural.
- **Paquete limpio por episodio.** Separar siempre: fuente creativa que se sube, description operativa que se pega/pasa al audio y run log técnico. El source no debe contener IDs, comandos, rutas de salida, flags CLI ni bitácora de ejecución.
- **Source legible por NotebookLM sin metadata privada.** El source que se sube NO lleva YAML frontmatter. Su primera línea no vacía debe ser exactamente `Source starts here below.`. Metadata, IDs, número privado y rutas viven en el ledger, la task o el run log.
- **Número privado fuera del audio.** El número de episodio puede existir en filename, ledger y run log, pero nunca dentro del source subido ni dentro del bloque `text` de la description. Usar "este audio", "esta conversación" o el nombre de la caja.
- **Eric como fundador, no como instrucción gramatical.** En source y description basta decir que Eric es el fundador/creador y fuente de criterio cuando aporte contexto. No escribir instrucciones sobre persona narrativa o punto de vista; NotebookLM puede leerlas como frase de audio.
- **Notebook nuevo por episodio por defecto.** Para series, crear un notebook nuevo por episodio salvo que el dueño pida explícitamente reutilizar uno existente. Reusar notebook es excepción, no default.
- **Fuente controlada por episodio.** Por defecto, si se subió una fuente nueva para este audio, generar usando SOLO esa fuente (`-s <source-id>`). No usar todas las fuentes salvo que el usuario lo elija.
- **Duración estándar:** `short` para audios de aproximadamente 5 minutos, salvo que el usuario pida otra duración.
- **Instrucciones obligatorias:** el campo final `[DESCRIPTION]` de `nlm generate audio` debe contener objetivo, estilo, fuente, apertura exacta, cierre exacto y CTA si aplica.
- **Validador obligatorio:** antes de crear notebook, subir source o generar audio, correr `python3 bin/validate-podcast-package.py --source "$SOURCE_DOC" --description "$AUDIO_DESCRIPTION_DOC"`. Si falla, corregir el paquete. No pedir a NotebookLM que compense un paquete incompleto.
- **No inventar urgencia comercial.** Precio dinámico, cupos, demanda, fechas o aumentos solo se mencionan si el dueño lo declaró o lo confirmó en la sesión.
- **Matiz de formato:** estas reglas nacieron en video corto; en podcast Deep Dive (~5 min) aplican en espíritu, no tag-por-tag: antagonista temprano, cero paráfrasis circular, loops de curiosidad, consecuencia/eco en el cierre y reward claro para el oyente.

## Modos de invocación — standalone vs encadenado

| Invocación | Comportamiento |
|---|---|
| `/777-notebooklm-podcast` | Corre Steps 0-10 completos. |
| `/777-notebooklm-podcast <slug>` | Usa `<slug>` como proyecto propuesto, lo confirma con eco corto y sigue Steps 0.2-10. |
| `/777-notebooklm-podcast <source-path>` | Trata el path como fuente propuesta, pero igual pregunta proyecto, notebook, persona y estrategia de fuentes. |

## Paso 0 — Proyecto y destino

Si no hay slug explícito, mostrar project picker numerado según `.agents/rules/777-agent-convention.md`:

```text
¿Sobre cuál proyecto?

1. proyecto_reciente
2. otro_proyecto
3. _demo (demo)

Responde con el número, o pega el nombre exacto si no aparece arriba.
```

Después preguntar destino:

```text
¿Dónde debe quedar el MP3?

- A) Dentro del proyecto (Recomendado) — DOCS/CONTENIDO/PROYECTOS/<Project>/notebooklm/audio/
- B) Ruta personalizada — la escribes tú
```

Guardar:

- `$PROJECT`
- `$PROJECT_DIR=DOCS/CONTENIDO/PROYECTOS/$PROJECT`
- `$OUT_DIR`

Ejecutar antes de descargar:

```bash
mkdir -p "$OUT_DIR"
```

## Paso 0.1 — Paquete limpio del episodio

Antes de crear o reutilizar notebook, preparar o verificar dos archivos distintos:

1. **Fuente creativa** — `source-ep-<NN>-<slug>.md`
   - Es el único documento que se sube como fuente.
   - El nombre del archivo puede contener el número privado para trazabilidad local, pero el contenido subido no debe mencionarlo.
   - No lleva YAML frontmatter. La primera línea no vacía debe ser exactamente `Source starts here below.`.
   - Contiene la tesis, escenas, objeción, prosa-semilla, límites de claims y, si ayuda al resultado, una sección `DESCRIPTION creativa del audio`.
   - Debe contener una sección exacta `## Story/Humanization Gate` con estos campos:

     ```md
     ## Story/Humanization Gate

     - Human-to-human angle:
     - Cold listener objection:
     - Opening loop:
     - Emotional tension:
     - Listener reward:
     - Anti-formula check:
     - Closing echo:
     ```

   - Puede incluir la description como refuerzo editorial para los locutores.
   - No debe contener comandos, IDs remotos, rutas de salida, flags CLI, instrucciones de upload/download, bitácora técnica, número privado del episodio ni instrucciones gramaticales sobre Eric.
2. **Description operativa** — `audio-description-ep-<NN>-<slug>.md`
   - Contiene un único bloque `text` con lo que se pega en NotebookLM o se pasa como `[DESCRIPTION]` al CLI.
   - Debe repetir duración promedio, dos locutores, apertura exacta, cierre exacto, estilo, restricciones, CTA aprobado y las señales de humanización/storytelling: oyente frío, opening loop, tensión, reward del oyente, anti-fórmula y closing echo.
   - El frontmatter externo puede guardar metadata privada, pero el bloque `text` no debe mencionar el número privado ni instrucciones gramaticales sobre Eric.
   - No se sube como fuente salvo que el dueño lo pida explícitamente.

Guardar:

- `$SOURCE_DOC`
- `$AUDIO_DESCRIPTION_DOC`

Si el usuario trae un source ya escrito y está contaminado con mecánica de herramienta, corregirlo antes de subirlo. La mecánica técnica vive en `TASKS/<task>/` o en un run log, nunca en el source.

Validar antes de cualquier acción remota:

```bash
python3 bin/validate-podcast-package.py \
  --source "$SOURCE_DOC" \
  --description "$AUDIO_DESCRIPTION_DOC"
```

Si el validador falla, corregir el paquete y repetirlo. No crear notebook, no subir source y no generar audio hasta tener `PASS`.

## Paso 0.2 — Persona / tarjeta de voz

Preguntar siempre:

```text
¿Quieres usar una persona o tarjeta de voz para este podcast?

- A) Sí, elegir una persona desde DOCS/CONTENIDO/PERSONAS/ (Recomendado si existe una voz del proyecto)
- B) No, seguir natural
```

Si el usuario elige **B**, guardar:

- `$VOICE_CARD=""`
- `$VOICE_MODE="natural"`

Si el usuario elige **A**:

1. Verificar primero si existe `DOCS/CONTENIDO/PERSONAS/mentor-eric/VOICE_CARD.md`. Si existe, sugerirla nominalmente como opción recomendada con esa ruta. Si no existe, no inventar esa voz: seguir con las personas disponibles o continuar natural si el usuario lo aprueba.
2. Buscar:

   ```bash
   find DOCS/CONTENIDO/PERSONAS -path "*/VOICE_CARD.md" -type f
   ```

3. Si no aparece ninguna `VOICE_CARD.md`, DETENER y ofrecer solo estas dos salidas:

   - Crear voz con `/777-author-voice-extractor` en modo biblioteca.
   - Continuar natural (`$VOICE_MODE="natural"`) con aprobación explícita del usuario.

   No inventar voz y no usar `777-coach-create`.

4. Mostrar máximo seis opciones numeradas. Si existe `DOCS/CONTENIDO/PERSONAS/mentor-eric/VOICE_CARD.md`, ponerla primero como `mentor-eric` y marcarla recomendada. Si hay más de seis, mostrar las seis más relevantes por mtime descendente y agregar una línea: `Otro — pega la ruta exacta`.

   ```text
   ¿Qué persona quieres usar?

   1. mentor-eric — DOCS/CONTENIDO/PERSONAS/mentor-eric/VOICE_CARD.md (Recomendado si existe)
   2. persona-dos — DOCS/CONTENIDO/PERSONAS/persona-dos/VOICE_CARD.md
   3. persona-tres — DOCS/CONTENIDO/PERSONAS/persona-tres/VOICE_CARD.md
   4. persona-cuatro — DOCS/CONTENIDO/PERSONAS/persona-cuatro/VOICE_CARD.md
   5. persona-cinco — DOCS/CONTENIDO/PERSONAS/persona-cinco/VOICE_CARD.md
   6. persona-seis — DOCS/CONTENIDO/PERSONAS/persona-seis/VOICE_CARD.md

   Responde con el número, o pega la ruta exacta.
   ```

5. Leer el `VOICE_CARD.md` elegido.
6. Guardar:

   - `$VOICE_CARD=<ruta>`
   - `$VOICE_MODE=<slug de persona>`

La voz se usa como guía de energía, cosmovisión, léxico y restricciones. No se debe caricaturizar ni inventar datos biográficos fuera de la tarjeta.

## Paso 1 — Notebook nuevo o existente

Preguntar:

```text
¿Qué notebook quieres usar?

- A) Crear notebook nuevo y subir una fuente nueva (Recomendado para cada episodio)
- B) Usar notebook existente y subir una fuente nueva (solo si el dueño lo pide)
- C) Usar notebook existente sin subir fuente nueva
```

### 1A — Notebook nuevo + fuente nueva

1. Usar `$SOURCE_DOC` como fuente por defecto. Si no existe, pedir path o URL de la fuente.
2. Si es archivo local, leerlo para entender contenido y generar título descriptivo.
3. Crear notebook:

   ```bash
   bash 777_tools/777_notebooklm/nlm create "<título descriptivo>"
   ```

4. Subir fuente y capturar `source_id`:

   ```bash
   bash 777_tools/777_notebooklm/nlm source add \
     --notebook <notebook-id> \
     --title "<título de fuente>" \
     --json \
     "<source-path-or-url>"
   ```

5. Guardar:

   - `$NOTEBOOK_ID`
   - `$NEW_SOURCE_ID`
   - `$NEW_SOURCE_TITLE`

### 1B — Notebook existente + fuente nueva

1. Listar notebooks:

   ```bash
   bash 777_tools/777_notebooklm/nlm list
   ```

2. Mostrar los últimos seis si la salida incluye fecha/modificación; si la herramienta no expone fecha, mostrar los seis primeros devueltos y aclarar que es el orden de la herramienta.
3. El usuario responde con número, ID parcial o nombre.
4. Usar `$SOURCE_DOC` como fuente por defecto. Si no existe, pedir path o URL de la fuente nueva.
5. Subir fuente al notebook seleccionado con `source add --json`.
6. Guardar `$NEW_SOURCE_ID`.

### 1C — Notebook existente sin fuente nueva

1. Listar notebooks con `nlm list`.
2. Mostrar hasta seis opciones.
3. El usuario responde con número, ID parcial o nombre.
4. No guardar `$NEW_SOURCE_ID`.

## Paso 2 — Fuentes que alimentarán ESTE audio

Listar fuentes del notebook:

```bash
bash 777_tools/777_notebooklm/nlm source list --notebook <notebook-id>
```

Preguntar explícitamente:

```text
¿Qué fuentes debe usar este audio?

- A) Solo la fuente nueva subida para este episodio (Recomendado si existe)
- B) Elegir UNA fuente específica
- C) Elegir varias fuentes específicas
- D) Usar todas las fuentes del notebook
```

Reglas:

- Si `$NEW_SOURCE_ID` existe, **A es la opción recomendada por defecto**.
- Si `$NEW_SOURCE_ID` no existe, ocultar A y pedir B/C/D.
- Para B o C, mostrar lista numerada de sources y aceptar números.
- Para A/B/C, construir `$SOURCE_ARGS` con `-s <source-id>` por cada fuente seleccionada.
- Para D, dejar `$SOURCE_ARGS=""` para que NotebookLM use todas.
- Nunca usar todas las fuentes por omisión cuando se acaba de subir una fuente nueva.

## Paso 3 — Formato

Preguntar:

```text
¿Qué formato quieres?

- A) Deep Dive / conversación de dos locutores (Recomendado)
- B) Brief
- C) Critique
- D) Debate
```

Mapeo CLI:

- A → `deep-dive`
- B → `brief`
- C → `critique`
- D → `debate`

Guardar `$FORMAT`.

## Paso 4 — Duración

Preguntar:

```text
¿Qué duración quieres?

- A) Short / alrededor de 5 minutos (Recomendado)
- B) Duración por defecto de NotebookLM
- C) Long
```

Mapeo CLI:

- A → `short`
- B → `default`
- C → `long`

Guardar `$LENGTH`.

## Paso 5 — Idioma

Verificar códigos si hace falta:

```bash
bash 777_tools/777_notebooklm/nlm language list
```

Picker recomendado:

| code | label |
|---|---|
| `es_419` | Español Latinoamérica — Recomendado |
| `es` | Español de España |
| `en` | English |
| `es_MX` | Español de México |

Guardar `$LANGUAGE`.

## Paso 6 — Objetivo, apertura, cierre e instrucciones

Este paso reemplaza el viejo "foco general". El objetivo es construir el texto exacto que irá en el argumento `[DESCRIPTION]` de:

```bash
nlm generate audio ... "<AUDIO_DESCRIPTION>"
```

### 6A — Preguntar objetivo y CTA

Preguntar en texto libre:

```text
¿Cuál es el objetivo de este audio y qué llamada a la acción debe dejar?
```

Si el usuario está creando un podcast de venta/oferta y confirma que aplica precio dinámico, sugerir esta CTA base para que la apruebe o edite:

```text
Si sientes que esto es para ti, no esperes. Entra a la oferta mientras está disponible al precio actual. El precio puede subir sin aviso según la demanda; cuando sube, no hay vuelta atrás al precio anterior.
```

No mencionar montos, cupos exactos, fechas, "último día" ni capacidad máxima salvo que el dueño los confirme explícitamente.

### 6B — Redactar apertura obligatoria

Antes de generar audio, el agente debe proponer una apertura exacta con los dos primeros turnos:

```text
Apertura exacta:
Locutor A: "<1-2 frases iniciales con gancho fuerte>"
Locutor B: "<1-2 frases que refuerzan el loop y prometen la respuesta>"
```

Requisitos:

- Capturar atención en los primeros diez segundos.
- Abrir una pregunta, tensión u objeción real.
- El segundo locutor debe amplificar el loop, no cerrarlo.
- No empezar con saludo genérico.
- Aplicar `.agents/rules/777-viral-lessons-learned.md` como archivo dorado y cargar las on-demand del STEP -1 al redactar la apertura.

### 6C — Redactar cierre obligatorio

El agente debe proponer cierre exacto:

```text
Cierre exacto:
Locutor A: "<síntesis de la tesis + transición a decisión>"
Locutor B: "<CTA clara, honesta y urgente si aplica>"
```

Para ofertas con precio dinámico confirmado, el cierre debe comunicar:

- Entra mientras el precio actual esté disponible.
- El precio puede subir sin aviso según demanda.
- Cuando sube, no hay regreso al precio anterior.
- Sin prometer resultados automáticos.

Además, aplicar `.agents/rules/777-viral-lessons-learned.md` como archivo dorado y cargar las on-demand del STEP -1 al redactar el cierre.

### 6D — Construir `$AUDIO_DESCRIPTION`

Regla de limpieza:

- Si existe `$AUDIO_DESCRIPTION_DOC`, extraer de ahí el único bloque `text` y usarlo como `$AUDIO_DESCRIPTION`.
- Si no existe, crearlo antes de generar. No improvisar una description solo en la terminal.
- El source puede contener una `DESCRIPTION creativa del audio` como refuerzo, pero la copia operativa vive en `$AUDIO_DESCRIPTION_DOC`.
- No subir `$AUDIO_DESCRIPTION_DOC` como fuente salvo aprobación explícita del dueño.
- Después de crear o modificar `$AUDIO_DESCRIPTION_DOC`, repetir el validador del paquete antes de seguir.

El `[DESCRIPTION]` final debe incluir:

- Objetivo del audio.
- Fuente(s) seleccionada(s) y regla de no salirse del material.
- Persona/tarjeta de voz elegida, si aplica.
- Formato de dos locutores si `$FORMAT=deep-dive`.
- Apertura exacta de Locutor A y Locutor B.
- Cierre exacto de Locutor A y Locutor B.
- CTA aprobada.
- Resultado `PASS` del validador `bin/validate-podcast-package.py`.
- Prohibición de inventar cifras, fechas, cupos, ventas o promesas.
- Idioma y tono.
- Aplicar `.agents/rules/777-viral-lessons-learned.md` como archivo dorado y cargar las on-demand del STEP -1 antes de guardar `$AUDIO_DESCRIPTION`.

Guardar `$AUDIO_DESCRIPTION`.

## Paso 7 — Confirmación antes de generar

Mostrar resumen:

- Proyecto.
- Destino MP3.
- Notebook elegido o creado.
- Fuente creativa subida, si aplica.
- Description operativa usada.
- Fuente(s) seleccionada(s) para ESTE audio.
- Persona/tarjeta de voz, si aplica.
- Formato.
- Duración.
- Idioma.
- Apertura exacta.
- Cierre exacto.
- CTA.
- Validador del paquete: `PASS`.
- Comando que se ejecutará, sin secretos.

Preguntar:

```text
¿Listo para generar el audio?

- A) Sí, generar
- B) Ajustar instrucciones
- C) Cancelar
```

## Paso 8 — Generar audio

Ejecutar:

```bash
bash 777_tools/777_notebooklm/nlm generate audio \
  --notebook <notebook-id> \
  --format <deep-dive|brief|critique|debate> \
  --length <short|default|long> \
  --language <code> \
  <SOURCE_ARGS si aplica> \
  --json \
  "<AUDIO_DESCRIPTION>"
```

`<SOURCE_ARGS si aplica>` equivale a:

- Una fuente: `-s <source-id>`
- Varias fuentes: `-s <source-id-1> -s <source-id-2>`
- Todas: nada

Capturar `task_id` del JSON.

## Paso 9 — Espera en segundo plano + descarga

No bloquear la sesión. El audio puede tardar 5-15 minutos.

```bash
OUT_FILE="$OUT_DIR/<notebook-title>-podcast.mp3"

bash 777_tools/777_notebooklm/nlm artifact wait <task-id> \
  --notebook <notebook-id> --timeout 900 --interval 10 --json && \
mkdir -p "$OUT_DIR" && \
bash 777_tools/777_notebooklm/nlm download audio \
  --notebook <notebook-id> --latest \
  "$OUT_FILE"

if [ ! -s "$OUT_FILE" ]; then
  echo "ERROR: download reportó éxito pero no hay archivo no-vacío en $OUT_FILE" >&2
  exit 1
fi
```

Registrar en un run log técnico:

- notebook ID;
- source ID(s);
- task/artifact ID;
- formato, duración e idioma;
- path del source creativo;
- path de la description operativa;
- path del MP3 descargado;
- cualquier intento descartado.

El run log técnico no se sube a NotebookLM.

Avisar al usuario:

> Podcast generándose en segundo plano. Lo descargaré en `$OUT_DIR` cuando esté listo.

## Defaults si el usuario dice "rápido" / "usa defaults"

Incluso en modo rápido:

- Preguntar proyecto.
- Preguntar persona sí/no.
- Preparar/verificar paquete limpio: source creativo + description operativa separada.
- Preguntar notebook nuevo/existente; default recomendado: notebook nuevo por episodio.
- Si se sube fuente nueva, usar SOLO esa fuente por defecto.
- Formato: `deep-dive`.
- Duración: `short`.
- Idioma: `es_419`.
- Instrucciones: nunca `general`; construir `$AUDIO_DESCRIPTION` con objetivo, apertura, cierre y CTA aprobada.
- Destino: preguntar una vez; no saltar routing.

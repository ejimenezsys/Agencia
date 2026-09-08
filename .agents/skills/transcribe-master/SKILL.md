---
name: transcribe-master
description: Transcribe archivos de audio y video (MP3, WAV, M4A, MP4, MOV, WebM) y enlaces de YouTube a texto de alta precisión. Genera texto limpio formateado, transcripciones con marcas de tiempo y diarización de hablantes, subtítulos estándar (.srt, .vtt), alineación palabra por palabra (words.json) y resúmenes ejecutivos con puntos clave. Compatible con Whisper (local o API), Groq, ElevenLabs Scribe y extracción directa de YouTube.
category: production
---

# Transcribe Master — Skill Universal de Transcripción y Subtitulado

Este skill convierte cualquier archivo de audio, video o enlace web en transcripciones profesionales, estructuradas y utilizables en múltiples formatos: **texto de lectura continua**, **marcas de tiempo por bloque**, **subtítulos (.srt / .vtt)**, **sincronía palabra por palabra (words.json)** y **resumen ejecutivo de contenido**.

---

## Cuándo activar este skill

- "Transcribe este audio / video: [ruta o archivo]"
- "Saca el texto y los subtítulos SRT de esta grabación"
- "Extrae la transcripción de este video de YouTube: [URL]"
- "Necesito un words.json con timestamps por palabra para animación o kinetic text"
- "Diariza esta conversación y dime quién habla en cada minuto"
- "Genera un resumen y las notas clave a partir de este audio de reunión o podcast"

---

## Flujo de Trabajo en 4 Pasos

### Paso 1: Detección y Validación del Input

El skill recibe uno de los siguientes tipos de entrada:

1. **Archivo local de audio o video:**
   - Formatos soportados: `.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac`, `.mp4`, `.mov`, `.mkv`, `.webm`.
   - Verifica que el archivo exista en disco antes de procesar.
2. **Enlace web / YouTube:**
   - URL de YouTube (`youtube.com/watch?v=...` o `youtu.be/...`).
   - Archivo alojado en la nube con enlace directo descargable.
3. **Parámetros de configuración (opcionales):**
   - **Idioma:** Detección automática o código explícito (`es`, `en`, etc.).
   - **Diarización (Múltiples hablantes):** `true` / `false` (por defecto `auto`).
   - **Formato deseado:** Texto limpio, marcas de tiempo, subtítulos SRT/VTT, o `words.json`.

---

### Paso 2: Selección del Motor de Transcripción

El skill selecciona el motor más eficiente según las herramientas instaladas o credenciales disponibles:

| Motor | Tipo | Ventaja Principal | Ideal para |
|---|---|---|---|
| **YouTube Subtitle Extractor** | Directo (API/yt-dlp) | Instantáneo, sin consumo de tokens ni audio | URLs de YouTube públicas |
| **Whisper Local (faster-whisper / CLI)** | Local (Offline) | 100% privado, gratis, ilimitado | Archivos confidenciales o sin conexión |
| **Groq Whisper (whisper-large-v3)** | Nube (API) | Velocidad ultrarrápida (1h en 10s), costo ínfimo | Archivos largos con entrega inmediata |
| **ElevenLabs Scribe / Whisper API** | Nube (API) | Precisión fonética extrema y diarización perfecta | Videos profesionales, podcasts y kinetic text |

> *Si el proceso requiere subir el archivo a una API externa de pago, el agente confirma primero la acción y el destino con el usuario.*

---

### Paso 3: Procesamiento y Estructuración de Formatos

A partir de la transcripción cruda, el skill puede generar hasta 5 artefactos según lo solicitado:

1. **`transcripcion_limpia.md` (Lectura humana):**
   - Elimina muletillas excesivas (*"ehh"*, *"este"*), titubeos y falsos comienzos.
   - Organiza el contenido en párrafos lógicos de 3 a 5 líneas con puntuación y ortografía perfecta.
2. **`transcripcion_marcas_tiempo.md` (Diarización y bloques):**
   - Agrupa bloques de 30 a 60 segundos con formato:
     `[00:15] Hablante 1: Buenas tardes a todos...`
     `[00:42] Hablante 2: Gracias por la invitación...`
3. **`subtitulos.srt` / `subtitulos.vtt` (Subtitulado listo para video):**
   - Bloques estándar de 1 a 2 líneas por subtítulo (máximo 42 caracteres por línea).
   - Sincronización temporal estricta para Premiere Pro, DaVinci Resolve, CapCut o reproductores web.
4. **`words.json` (Timestamps palabra por palabra):**
   - Estructura JSON con milisegundos y hablante por cada palabra:
     ```json
     {
       "words": [
         {"text": "Hola", "start": 0.12, "end": 0.38, "speaker": "A"},
         {"text": "mundo", "start": 0.39, "end": 0.75, "speaker": "A"}
       ],
       "meta": {"duration_s": 120.5, "language": "es"}
     }
     ```
5. **`resumen_ejecutivo.md` (Puntos clave y notas):**
   - Resumen en 1 párrafo.
   - Principales temas tratados (viñetas).
   - Tareas o acuerdos concretos (Action Items).

---

### Paso 4: Entrega Organizada

Los archivos se guardan en la carpeta de transcripciones del proyecto:
```text
<proyecto>/transcripts/<nombre_archivo>/
├── transcripcion_limpia.md
├── transcripcion_marcas_tiempo.md
├── subtitulos.srt
├── subtitulos.vtt
├── words.json
└── resumen_ejecutivo.md
```

---

## Anti-patrones que Debes Evitar

- ❌ **Inventar palabras inaudibles:** Si hay un fragmento ininteligible debido al ruido, márcalo claramente como `[inaudible 03:14]` en lugar de alucinar texto.
- ❌ **Subtítulos con 4 líneas:** Un subtítulo no debe superar 2 líneas en pantalla; si es más largo, divídelo en dos entradas temporales consecutivas.
- ❌ **Perder los milisegundos en words.json:** El formato para video kinetic requiere precisión decimal exacta en segundos o milisegundos enteros; nunca redondees a segundos planos.
- ❌ **Ejecución ciega de uploads grandes:** Si el audio pesa más de 50 MB, usa compresión a mono/16kHz antes de enviarlo a cualquier API para evitar costos y tiempos muertos.

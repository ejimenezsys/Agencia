# Especificaciones de Formatos y Esquemas de Salida

Esta guía técnica estandariza los formatos de salida generados por el skill `transcribe-master`.

---

## 1. Texto Limpio Continuo (`transcripcion_limpia.md`)
Diseñado para artículos de blog, documentación, lectura humana o edición de libros.

```markdown
# Transcripción: [Título del Episodio / Reunión]

**Duración:** 45:12 | **Fecha:** 2026-09-06 | **Idioma:** Español

---

En los últimos cinco años, el mercado de la inteligencia artificial aplicada a negocios ha experimentado una transformación profunda. Las empresas ya no buscan herramientas aisladas; lo que demandan hoy son arquitecturas completas que automaticen sus flujos de ventas y operaciones.

Durante la sesión de hoy analizamos el impacto directo que tiene la velocidad de respuesta en la conversión de leads comerciales. Cuando una empresa responde en menos de cinco minutos a una consulta entrante por WhatsApp, la probabilidad de cerrar la venta aumenta de forma exponencial...
```

---

## 2. Transcripción con Diarización y Marcas de Tiempo (`transcripcion_marcas_tiempo.md`)
Diseñado para podcasts, entrevistas, testimonios y minutas de reuniones de equipo.

```markdown
# Registro Temporal: [Título de la Grabación]

**[00:00] Hablante 1 (Edward Jiménez):**
Bienvenidos a este nuevo episodio. Hoy vamos a desglosar cómo estructurar un departamento comercial gobernado por agentes de IA.

**[00:24] Hablante 2 (Invitado):**
Muchas gracias, Edward. Es un placer estar aquí. Creo que el primer punto crítico donde la mayoría de los directores se equivocan es intentar reemplazar personas en vez de desarmar tareas.

**[01:15] Hablante 1 (Edward Jiménez):**
Exacto. Cuando analizamos las 6 A's de nuestro método, el primer paso siempre es la auditoría del cuello de botella...
```

---

## 3. Subtítulos Estándar SubRip (`subtitulos.srt`)
Formato universal para editores de video (CapCut, Premiere, DaVinci) y reproductores (VLC, YouTube).

```text
1
00:00:01,250 --> 00:00:03,800
Bienvenidos a este nuevo episodio de Prosper IA.

2
00:00:03,900 --> 00:00:07,150
Hoy analizamos cómo automatizar tu equipo comercial.

3
00:00:07,300 --> 00:00:10,450
El factor clave no es el software, sino la metodología.
```

- **Reglas del formato SRT:**
  - Contador secuencial entero.
  - Formato de tiempo: `HH:MM:SS,mmm` (con coma para milisegundos).
  - Máximo 2 líneas por subtítulo (idealmente 1 línea para videos cortos 9:16).
  - Máximo 38 a 42 caracteres por línea.

---

## 4. Subtítulos WebVTT (`subtitulos.vtt`)
Formato nativo para navegadores web (`<track src="...">`), cursos online y reproductores modernos.

```text
WEBVTT - Transcripción Oficial

00:00:01.250 --> 00:00:03.800
<v Hablante 1>Bienvenidos a este nuevo episodio de Prosper IA.</v>

00:00:03.900 --> 00:00:07.150
<v Hablante 1>Hoy analizamos cómo automatizar tu equipo comercial.</v>
```

---

## 5. Esquema Canónico Palabra por Palabra (`words.json`)
Formato estricto requerido para tipografía cinética, Remotion, HyperFrames o alineación fonética.

```json
{
  "meta": {
    "filename": "audio_master.mp3",
    "duration_s": 45.28,
    "language": "es",
    "model": "scribe_v2",
    "generated_at": "2026-09-06T10:15:00Z"
  },
  "words": [
    {
      "text": "Bienvenidos",
      "start": 0.12,
      "end": 0.58,
      "speaker": "A",
      "confidence": 0.98
    },
    {
      "text": "al",
      "start": 0.59,
      "end": 0.72,
      "speaker": "A",
      "confidence": 0.99
    },
    {
      "text": "episodio.",
      "start": 0.73,
      "end": 1.25,
      "speaker": "A",
      "confidence": 0.96
    }
  ]
}
```

---

## 6. Resumen Ejecutivo y Tareas (`resumen_ejecutivo.md`)

```markdown
# Resumen Ejecutivo: [Tema del Audio]

## 📌 En 60 Segundos
[Párrafo de 3-4 oraciones sintetizando el mensaje central o la tesis del contenido].

## 🔑 Puntos Clave Tratados
- **Velocidad de respuesta:** Disminuir el tiempo de atención de 2 horas a menos de 5 minutos incrementa la tasa de cierre en un 391%.
- **Centralización omnicanal:** Centralizar WhatsApp, Instagram y correo en una sola bandeja evita la dispersión de prospectos.
- **Validación previa:** No agendar llamadas comerciales sin un formulario o agente de pre-cualificación.

## 📋 Tareas y Acciones Acordadas (Action Items)
- [ ] **Configurar** el webhook de alertas inmediatas en el CRM.
- [ ] **Auditar** las últimas 50 llamadas de ventas para extraer objeciones frecuentes.
- [ ] **Revisar** el guion de respuesta inicial antes del viernes.
```

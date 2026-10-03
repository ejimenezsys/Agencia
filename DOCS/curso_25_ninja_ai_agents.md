# Curso #25: Ninja AI AGENTS (Agentes Conversacionales en GoHighLevel)

* **Enfoque:** Arquitectura técnica, prompt engineering profesional, estructura de costos y base de conocimientos para bots conversacionales en GHL.
* **Archivo de Datos:** [`DOCS/curso_25_ninja_ai_agents.json`](file:///Users/ejimenezsys/Desktop/sitiosweb/agencia/DOCS/curso_25_ninja_ai_agents.json)
* **Relevancia para ProsperIA:** 🔥 **Núcleo Operativo.** La ingeniería exacta detrás del agente comercial que instalas a tus clientes.

---

## 1. Enlaces a Recursos y Herramientas Exclusivas

* **Custom GPTs de Creación Rápida:**
  * [Ninja Agent AI Basic (ChatGPT)](https://chatgpt.com/g/g-69b1bc952e308191a9910951d23f9f29-ninja-agent-ai-basic)
  * [Ninja Conversational AI Agent Builder (ChatGPT)](https://chatgpt.com/g/g-691f5c68132881918925648cdea5c024-ninja-conversational-ai-agent-builder)
* **Documentos Maestros de Trabajo (Google Docs):**
  * [Documento 01: PROMPTS](https://docs.google.com/document/d/1XQwt0QIwBQlS3ilo-hKVR32BUAKr9faAgApqEii0sPk/edit?usp=sharing)
  * [Documento 02: FORMATOS DE PROMPTS (Markdown vs Prosa vs JSON)](https://docs.google.com/document/d/15Yh-khHTmFkGjPLM6f9a6ehSWt75f2xwOjC0AcMQtNs/edit?usp=sharing)
  * [Documento 03: PROMPT STACK (Las 5 Capas)](https://docs.google.com/document/d/1IQO9B5Ef4vk_ll3VTqywwDkFIBtIIz6yseftYM1rWhI/edit?usp=sharing)
* **Plantilla de Base de Conocimientos (Knowledge Base):**
  * [Plantilla CSV para GHL (Descargar CSV)](https://cdn.courses.apisystem.tech/memberships/4PELThvbKruGE3Uxyzrt/courses/ghl-ai-employee-knowledge-base-example-lpha.csv)

---

## 2. La Metodología de las 5 Capas: "Prompt Stack"

El error que comete el 95% de personas es poner un solo bloque de texto desordenado. Un agente de grado comercial en GoHighLevel se diseña en 5 capas delimitadas en Markdown:

```markdown
# 1. SYSTEM PROMPT (Identidad y Propósito)
Eres Sofía, asistente virtual de [Nombre de la Clínica]. Tu misión es orientar a pacientes interesados en tratamientos dentales/estéticos y agendar su cita de valoración.

# 2. REGLAS DE COMPORTAMIENTO (Estilo y Tono)
- Respuestas de máximo 25 palabras.
- Tono cálido, profesional y cercano.
- Máximo 1 emoji por mensaje.
- Una sola pregunta por turno.
- Tiempo de respuesta configurado a 7 segundos.

# 3. BASE DE CONOCIMIENTOS (Knowledge Base RAG)
[Conexión a tabla CSV o URL de la clínica con preguntas frecuentes, precios aproximados y ubicación].

# 4. FLUJO CONVERSACIONAL (Pasos)
1. Saludar y preguntar el tratamiento de interés.
2. Identificar motivo de la consulta (dolor, estética, revisión).
3. Solicitar franja horaria preferida (mañana o tarde).
4. Enviar enlace de confirmación directa en calendario.

# 5. LÍMITES Y GUARDRAILS (Seguridad)
- NUNCA diagnosticar ni recetar medicamentos.
- NUNCA prometer resultados médicos exactos.
- Si preguntan por casos de urgencia grave: derivar de inmediato al teléfono de emergencias.
```

---

## 3. Economía y Márgenes de la IA en ProsperIA

* **El Mito del Costo Alto:** Usando los modelos optimizados de OpenAI integrados en GHL (`gpt-4o-mini`), el costo real por mensaje es de apenas **~$0.0004 USD**.
* **Impacto Financiero:** Con una recarga de **$10 USD**, tu cliente puede procesar más de **23,000 mensajes**.
* **Tu Margen en ProsperIA:** Cobras una mensualidad de **$497 a $997 USD/mes** por el sistema y el costo real de computación de la IA para la clínica es de menos de $5 a $10 USD al mes. ¡Margen del 98%!

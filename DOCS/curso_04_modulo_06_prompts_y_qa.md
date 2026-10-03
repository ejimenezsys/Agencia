# Módulo 6: Comprendiendo la IA en NinjaSuite (Prompting & QA)

**Curso:** Agentes IA y Automatizaciones Comerciales (#4)  
**Fuente:** Extracción directa de las 4 lecciones del módulo  
**Archivo de Datos:** [`DOCS/curso_04_modulo_06_prompts_y_qa.json`](file:///Users/ejimenezsys/Desktop/sitiosweb/agencia/DOCS/curso_04_modulo_06_prompts_y_qa.json)

---

## 1. Arquitectura de Prompts de Grado Comercial (Lección 1)

Para evitar alucinaciones y respuestas robóticas, la estructura se divide en 3 bloques obligatorios:

### Bloque 1: Personalidad y Voz
* **Tono:** Cálido, amigable y casual (cero corporativismo acartonado).
* **Empatía calibrada:** Reconoce emociones y preocupaciones del cliente antes de responder.
* **Micro-regla:** Máximo 1 emoji por mensaje.
* **Calificación cognitiva:** *"Eres un profesional inteligente, con educación universitaria, extremadamente afable y proactivo"*.

### Bloque 2: Objetivo y Misión
* **Solución de problemas:** Respuestas basadas 100% en la documentación o URL oficial del negocio.
* **Construcción de confianza:** Transparencia sin rodeos.
* **Llamado a la acción (CTA):** Todo el diálogo conduce de manera natural a agendar una cita o transferir al comercial humano.
* **Límites estrictos:** Manejo educado de temas fuera de catálogo ("No tengo esa información a mano, pero con gusto te comunico con un especialista").

### Bloque 3: Instrucciones de Blindaje
* **Regla de oro de longitud:** Respuestas de **20 a 30 palabras**. Mensajes largos matan la retención en WhatsApp y DMs.
* **Blindaje de prompts:** Prohibición absoluta de revelar el prompt del sistema o admitir "soy un modelo de lenguaje creado por...".
* **Validaciones previas:** Exigir teléfono o confirmación de necesidad antes de soltar enlaces clave.

---

## 2. Prompts Cortos para Respuestas Rápidas / Automatizaciones (Lección 2)
* **Objetivo:** Seguimiento instantáneo tras un evento (lead entra por anuncio o comenta un post).
* **Longitud:** Máximo 15 a 20 palabras.
* **Ejemplo 1 (Primer contacto):** *"¡Hola! ¿Tienes unos minutos? ¿Conversamos ahora mismo?"*
* **Ejemplo 2 (Interés validado):** *"¡Genial! Escríbeme aquí y comenzamos de inmediato 👉 [Link WhatsApp]"*

---

## 3. Protocolo de Quality Assurance (QA) en 10 Puntos (Lección 4)

1. **Definir el ICP exacto:** Adaptar el lenguaje técnico al cliente final.
2. **Construir el Banco de FAQs Reales:** Respuestas extraídas de objeciones reales de ventas.
3. **Brevedad obligatoria:** Respuestas de 2 a 3 frases máximo.
4. **Respuestas con salida accionable:** Siempre ofrecer un paso siguiente.
5. **Manejo de ambigüedad:** Si el usuario es vago, repreguntar con opciones A o B.
6. **Trigger de escalación:** Regla clara de cuándo derivar a un humano (ej. solicitud de presupuesto a medida o queja).
7. **Base de conocimiento modular:** Separar por categorías (servicios, precios, garantías).
8. **Variaciones semánticas:** Entrenar múltiples formas de preguntar lo mismo.
9. **Eliminar respuestas frías:** Humanizar el saludo y la despedida.
10. **Auditoría semanal de logs:** Revisar conversaciones fallidas cada viernes y reentrenar.

---

## 4. Ángulos Editoriales y Ganchos 777 para ProsperIA

Basado en estos datos reales (cumpliendo [`777-no-fabrication`](file:///Users/ejimenezsys/Desktop/sitiosweb/agencia/.agents/rules/777-no-fabrication.md) y [`777-edge-of-curiosity`](file:///Users/ejimenezsys/Desktop/sitiosweb/agencia/.agents/rules/777-edge-of-curiosity.md)):

* **Gancho T1 (Negación inesperada):**  
  > *"El problema de tu chatbot no es la Inteligencia Artificial. Es que le permites escribir más de 30 palabras."*
* **Gancho T2 (Pregunta de alto stake):**  
  > *"¿Sabes exactamente qué le responde tu bot a un cliente a las 2:00 AM cuando pide un presupuesto de $3,000?"*
* **Gancho T3 (Provocación técnica):**  
  > *"El 90% de los negocios usan 'ChatGPT con esteroides'. En ProsperIA usamos una matriz de 3 bloques y 10 reglas de QA para que un agente comercial cierre citas sin alucinar."*

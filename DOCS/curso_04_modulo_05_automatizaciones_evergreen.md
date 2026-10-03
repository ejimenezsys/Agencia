# Módulo 5: Automatizaciones para Funnels Evergreen (GHL / ProsperIA)

**Curso:** Agentes IA y Automatizaciones Comerciales (#4)  
**Entorno de Replicación:** GoHighLevel Marca Blanca (ProsperIA)  
**Vertical Inicial:** Clínicas Dentales, Estéticas y Capilares  
**Archivo de Datos:** [`DOCS/curso_04_modulo_05_automatizaciones_evergreen.json`](file:///Users/ejimenezsys/Desktop/sitiosweb/agencia/DOCS/curso_04_modulo_05_automatizaciones_evergreen.json)

---

## 1. La Arquitectura del Funnel Evergreen en 5 Workflows Clave

### Workflow 1: Activación y Desactivación Blindada del Agente IA
* **Punto de Entrada (Trigger):** Lead entra por anuncio de Meta, formulario o mensaje directo.
* **Acción:** Encender Agente IA + Tag `Agente-Activo` + crear Oportunidad en Pipeline `En Conversación`.
* **Regla de Desconexión (Kill-Switch):** 
  * En el momento exacto en que el paciente agenda en el calendario o un recepcionista humano escribe, el Agente IA **se apaga automáticamente** para evitar mensajes contradictorios.

### Workflow 2: Captura en Web y Secuencia Conversacional por WhatsApp
* **Problema que resuelve:** El 60% de los pacientes que llenan un formulario nunca contestan una llamada fría.
* **Flujo:** Al enviar formulario web -> Notificación interna a la clínica + WhatsApp inmediato:
  > *"Hola [Nombre], vimos que solicitaste información sobre el tratamiento de [Tratamiento]. ¿Te gustaría que revisemos los horarios disponibles para esta semana?"*
* **Bifurcación:** Si responde, entra el Agente IA. Si no responde, se envían toques a las 2h y al día siguiente.

### Workflow 3: El Protocolo Anti-Inasistencias (Crucial para Clínicas)
* **Trigger:** Cita confirmada en el calendario GHL.
* **Cadencia de Confirmación:**
  1. **Inmediato:** Confirmación con dirección, enlace de Google Maps y preparación básica para el tratamiento.
  2. **24 horas antes:** Recordatorio preventivo.
  3. **2 horas antes (Interactivo):** *"Hola [Nombre], el Dr. [Doctor] tiene reservado tu espacio a las 4:30 PM. Por favor responde 'CONFIRMO' para mantener tu turno o 'REPROGRAMAR' si necesitas cambiarlo."*
  4. **10 minutos antes:** Notificación de que la sala está lista.

### Workflow 4 & 5: Captación Automática por Comentarios en Redes (Instagram & Facebook)
* **Estrategia para Clínicas:** Publicar un Reel o Post de un caso de éxito (antes/después de ortodoncia invisible, armonización facial o trasplante capilar) con el CTA:
  * *"Comenta 'VALORACION' y te enviamos la guía de tratamiento y disponibilidad por mensaje privado."*
* **Automatización:** El sistema responde al comentario público y le manda un DM directo al instante, activando al Agente IA en la bandeja privada.

---

## 2. Ángulos de Contenido 777 para que ProsperIA Capte Clínicas

Con estos flujos documentados, tenemos la fórmula perfecta para crear piezas que vendan el servicio de ProsperIA a directores de clínicas sin parecer un vendedor novato:

* **Táctica T1 (Negación inesperada):**  
  > *"Tu clínica no necesita más anuncios de Facebook. Necesita responder en 45 segundos a los que ya te están escribiendo."*
* **Táctica T2 (Pregunta de alto stake / Dolor financiero):**  
  > *"¿Cuánto le cuesta a tu clínica que 3 pacientes de implantes o botox no se presenten a su cita esta semana? El protocolo de 4 toques de ProsperIA reduce el ausentismo del 35% a menos del 8%."*
* **Táctica T3 (Provocación técnica verificable):**  
  > *"El 90% de las recepcionistas están atendiendo a los pacientes en sala mientras el WhatsApp de la clínica acumula 14 consultas sin responder. Este es el sistema de 5 workflows con IA que instalamos para que tu clínica nunca duerma."*

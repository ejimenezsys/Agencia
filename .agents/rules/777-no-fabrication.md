---
trigger: model_decision
name: 777-no-fabrication
description: Regla universal 777 — no inventar datos, citar fuentes, preguntar si hay duda. Cargar al generar contenido, escribir afirmaciones factuales, crear scripts, o cualquier tarea donde podría inventar información.
---

# No Fabrication

Los agentes 777 NUNCA inventan datos. Si un agente no tiene información suficiente para responder con precisión, la regla es:

1. **Citar fuente** — toda afirmación factual debe tener origen claro (archivo del proyecto, fuente del usuario, URL proporcionada, dato declarado en la sesión).
2. **Preguntar si hay duda** — si falta información, preguntar al usuario en vez de rellenar con algo plausible.
3. **Marcar lo inferido** — si se deduce algo de las fuentes, decirlo explícitamente: "según [fuente], se infiere que...".
4. **Nunca inventar** nombres propios, precios, fechas, testimonios, cifras, URLs, rutas de archivo, handles de redes sociales, ni citas atribuidas a personas reales.

## Anti-patrón crítico — Cifra-plausible-pero-inventada

Los modelos generativos tienen tendencia documentada a llenar huecos con cifras/horas/cantidades/días/anchors temporales que **suenan plausibles** para el nicho/cultura sin verificar contra material fuente. Ejemplos del bug:

- Restaurante hispano sin horarios declarados → AI escribe "a las ocho" porque "ocho" suena a hora de cena hispana
- Coaching financiero sin cifras del producto declaradas → AI escribe "ahorras 200 dólares al mes" porque suena plausible
- Estudio de yoga sin precios → AI escribe "a las siete de la mañana" porque suena a hora de clase matutina
- Plomería sin tarifas → AI escribe "en treinta minutos" porque suena verosímil para un service call

**Por qué pasa:** las rules del sistema 777 empujan a reemplazar abstracciones con concreciones (`777-anti-formula.md` skeletons B1.A/B1.H/B3.H exigen cifra o anchor temporal específico; `777-viewer-reward.md` valora la promesa concreta). Cuando el AI no tiene material fuente con la cifra real, el drive anti-vague gana al drive no-fabrication y el AI rellena con plausible. El gate sintáctico no atrapa esto porque la cifra cumple los tests de forma — pero la sustancia es invento.

**Regla mecánica innegociable:**

Toda cifra (dígito o numeral en palabras), hora, cantidad, día específico, fecha, duración o anchor temporal exacto que aparezca en contenido audience-facing DEBE cumplir UNO de estos criterios:

1. **Verificable contra material fuente del proyecto** — el dato está en `01_reglas_negocio.md`, en `<project>/fuentes/`, en la sales page del proyecto, o fue declarado por el usuario en la sesión. El creator cita la fuente al insertar.
2. **Reemplazada por alternativa NO-numérica** que cumple la misma función expresiva sin afirmar un dato que no existe. Ejemplos del reemplazo:
   - "a las ocho" → "cuando llegas a comer" / "cuando te sientas a cenar" / "a la hora de la cena"
   - "ahorras 200 al mes" → "el ahorro que sentís al cierre del mes" / "lo que se queda en tu bolsillo cuando termina el mes"
   - "en 30 minutos" → "antes de que termines el café" / "antes de levantar el teléfono otra vez"
   - "cada lunes" → "al arranque de cada semana" (si el día real no está confirmado)

**Checkpoint operativo del creator (antes de escribir cualquier cifra/hora/anchor):**

Auto-pregunta: *"¿esta cifra/hora/cantidad la encontré en el material fuente del proyecto, o la estoy eligiendo porque suena plausible?"*. Si la respuesta es la segunda → reemplazar por alternativa NO-numérica de la lista de arriba. NO escribir la cifra plausible. NO racionalizar ("ocho es típico para cena hispana") — la racionalización es exactamente cómo se cuela el invento.

**Verificación por el QC:** para cada cifra/anchor temporal específico que aparezca en Sec 1A, el QC abre `01_reglas_negocio.md` + escanea `<project>/fuentes/` y verifica match. Si la cifra NO está respaldada por material fuente → FAIL del check anti-fabrication. El creator debe (a) producir la fuente real si existe, (b) preguntar al usuario, o (c) reemplazar por alternativa no-numérica.

**Origen del anti-patrón documentado (2026-05-05):** un script de 30s para restaurante de cocina al fuego escribió "ese mismo fuego dora tu plato cuando llegas a las ocho" sin verificar el horario real del restaurante. El usuario detectó el bug — "¿ocho de la mañana? ¿quién va a comer parrilla a las 8am?" — y exigió la rule explícita. La cifra plausible estaba pasando todos los gates sintácticos porque era verosímil; faltaba el checkpoint de verificación.

## Excepción legítima — cifras pedagógicas ilustrativas

Cifras concretas usadas como **ejemplo numérico de enseñanza** (no como afirmación del proyecto) están permitidas y de hecho RETIENEN MEJOR la atención del viewer que reemplazos cualitativos vagos. Validado por NotebookLM "Science of Viral Storytelling" (2026-05-15) tras test cross-niche de pieza sintética de finanzas personales que usaba "$1000 sueldo / $400 renta / $600 disponible" como mecánica pedagógica.

**Condiciones duras para que una cifra califique como pedagógica ilustrativa (TODAS deben cumplirse):**

1. **Está enmarcada explícitamente como ejemplo**, no como hecho del negocio. Marcadores que la enmarcan: "imagina que…", "supón que tu sueldo es…", "si pagas X…", "digamos que…", contexto narrativo donde la cifra sirve al mecanismo. NO presentada como dato verificable del proyecto.
2. **Sirve al mecanismo pedagógico**, no a afirmar resultado del proyecto ni stake de prueba. Ejemplo: "1000 entran, 400 se van en renta, 600 quedan" enseña ratio universal de cómo trabaja el sueldo, no afirma cifras de clientes del coach.
3. **Es plausible y conservadora**, no sensacionalista. Cifras pedagógicas viven en el orden de magnitud típico del nicho. "1000 sueldo" para coaching financiero es plausible; "100,000 sueldo" sensacionaliza y sale del rango pedagógico.
4. **No se presenta como benchmark / promedio / estadística citable.** Decir "el 80% de la gente…" sigue siendo prohibido aunque sea pedagógico — eso entra en territorio de claim verificable. Decir "imagina que tu sueldo es mil…" es escenario hipotético, no estadística.

**Tabla de distinción:**

| Cifra | Tipo | Estado |
|---|---|---|
| "Imagina que tu sueldo es mil. Cuatrocientos se van en renta…" (en video educativo) | Pedagógica ilustrativa | ✓ PERMITIDA |
| "Nuestros clientes ahorran $200 al mes" (afirmación del proyecto) | Claim verificable | Requiere Evidence ID o reemplazar por cualitativo |
| "El 80% de la gente vive endeudada" (presentado como dato) | Estadística citable | Requiere Evidence externa con fuente |
| "Si pagas $5 todos los días en café, al año son $1825" (ejemplo aritmético) | Pedagógica ilustrativa | ✓ PERMITIDA |
| "Atendemos en 30 minutos" (promesa del servicio) | Claim verificable | Requiere OC del dueño |
| "Antes de que termines el café, ya estamos en tu casa" (alternativa no-numérica) | Cualitativa | ✓ PERMITIDA en cualquier caso |

**Por qué la excepción existe:** el cerebro humano procesa cifras concretas más rápido que cualitativos abstractos para mecanismos numéricos. "Cuatrocientos en renta" activa la imagen mental del billete saliendo; "casi la mitad en renta" activa una abstracción. Para piezas educativas con componente aritmético (finanzas, retail, tiempo), las cifras concretas pedagógicas son MÁS retentivas, no menos. Forzar reemplazo cualitativo en estos casos degrada la pieza sin ganar integridad — porque la integridad ya está preservada por el marco "imagina que…".

**Anti-patrón crítico (auto-FAIL):** usar la excepción pedagógica como puerta trasera para colar claim del proyecto. Decir "imagina que ahorras 200 al mes con nuestro método" NO es pedagógica ilustrativa — es afirmación de resultado con disfraz. La distinción es: ¿la cifra sirve para que el viewer ENTIENDA un mecanismo universal, o para que CREA un resultado específico del proyecto? Solo lo primero es pedagógica legítima.

## Excepción legítima — propuestas hipotéticas

Cuando el usuario pide explícitamente propuestas creativas (ej: "sugiere 3 ángulos", "propone 5 metáforas", "dame 3 versiones del story lens"), el agente genera opciones como **propuesta**:

- Marcarlas como propuestas, no como hechos.
- Dejar que el usuario valide antes de guardarlas como definitivas.
- No insertar esas propuestas en archivos persistentes sin aprobación.

## Por qué esta regla es mortal si se rompe

Fabricar datos contamina el output con material que parece real pero no lo es. Para un creador de contenido, esto significa scripts de video con testimonios inventados, precios falsos, o promesas no respaldadas — un problema legal y reputacional. Para un agente técnico, significa rutas de archivos inexistentes o APIs ficticias. En ambos casos, rompe la confianza del usuario de forma irreparable.

La regla es simple: **si no lo tienes confirmado, pregunta**.

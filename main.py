import os
import uuid
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Request, Response, Depends, status, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr

app = FastAPI(title="Prosper IA API Stack", version="1.0.0")

# Cabeceras de seguridad HTTP
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# DB Sessions configuration (no longer stored in global RAM dict SESSIONS)

INITIAL_LEADS = [
    {
        "id": 1,
        "name": "Carlos Mendoza",
        "email": "carlos.mendoza@technologysolutions.com",
        "company": "Technology Solutions",
        "phone": "+34 612 345 678",
        "status": "new",
        "source": "website",
        "score": 85,
        "created_at": "2026-05-19T10:15:30Z",
        "notes": "Interesado en automatizar el seguimiento de leads fríos por WhatsApp."
    },
    {
        "id": 2,
        "name": "Laura Gómez",
        "email": "laura.gomez@retailgroup.es",
        "company": "Retail Group España",
        "phone": "+34 654 321 098",
        "status": "contacted",
        "source": "social",
        "score": 70,
        "created_at": "2026-05-18T14:22:15Z",
        "notes": "Llamada inicial realizada. Quiere integrar el chatbot con su catálogo Shopify."
    },
    {
        "id": 3,
        "name": "Javier Ortiz",
        "email": "j.ortiz@innovatech.mx",
        "company": "InnovaTech S.A.",
        "phone": "+52 55 1234 5678",
        "status": "qualified",
        "source": "referral",
        "score": 90,
        "created_at": "2026-05-17T09:05:00Z",
        "notes": "Lead muy caliente. Presupuesto aprobado para IA en atención a clientes de nivel 1."
    },
    {
        "id": 4,
        "name": "Sofía Castro",
        "email": "sofia.castro@marketingdigital.co",
        "company": "Marketing Digital Co",
        "phone": "+57 300 987 6543",
        "status": "converted",
        "source": "email",
        "score": 95,
        "created_at": "2026-05-15T16:45:00Z",
        "notes": "Cerrada suscripción Plan Elite. SVE-90 desplegado y funcionando correctamente."
    },
    {
        "id": 5,
        "name": "Alejandra Ruiz",
        "email": "a.ruiz@bienesraices.net",
        "company": "Ruiz Bienes Raíces",
        "phone": "+34 677 889 900",
        "status": "lost",
        "source": "website",
        "score": 40,
        "created_at": "2026-05-14T11:30:00Z",
        "notes": "El cliente considera que es muy costoso para su volumen actual de ventas."
    },
    {
        "id": 6,
        "name": "Roberto Peña",
        "email": "roberto@constructorapena.com",
        "company": "Pena Constructores",
        "phone": "+34 600 112 233",
        "status": "new",
        "source": "other",
        "score": 65,
        "created_at": "2026-05-20T08:12:00Z",
        "notes": "Dejó mensaje preguntando si es posible programar recordatorios de pago automáticos."
    },
    {
        "id": 7,
        "name": "Lucía Fernández",
        "email": "lfernandez@educaciononline.edu",
        "company": "EducaOnline S.L.",
        "phone": "+34 622 334 455",
        "status": "qualified",
        "source": "social",
        "score": 80,
        "created_at": "2026-05-16T15:10:00Z",
        "notes": "Desea automatizar el proceso de admisión de alumnos y asignación de tutores."
    },
    {
        "id": 8,
        "name": "Miguel Torres",
        "email": "miguel@consultoria360.com",
        "company": "Consultores 360",
        "phone": "+34 699 887 766",
        "status": "contacted",
        "source": "website",
        "score": 75,
        "created_at": "2026-05-19T18:40:00Z",
        "notes": "Envió formulario pidiendo demo del agente conversacional por voz."
    }
]

INITIAL_BLOG_POSTS = [
    {
        "slug": "rediseno-crm-ia-2026",
        "title": "Cómo la Inteligencia Artificial está redefiniendo el CRM en 2026: La Guía para Empresas en Latinoamérica",
        "category": "Marketing & CRM",
        "summary": "Descubre cómo los agentes autónomos de venta pueden integrarse con tu CRM tradicional para calificar prospectos 24/7 sin intervención humana.",
        "content": """<p class="mb-4 text-slate-300 leading-relaxed">En el competitivo ecosistema empresarial de Latinoamérica, los sistemas de gestión tradicionales están sufriendo una transformación drástica. El CRM ya no puede ser visto como una base de datos estática donde los ejecutivos registran información de forma manual después de concretar una llamada. En 2026, la implementación de Inteligencia Artificial en el CRM redefine la velocidad de respuesta comercial, reduciendo los tiempos de atención a un nivel autónomo y sin fricciones.</p>
<p class="mb-4 text-slate-300 leading-relaxed">El gran cuello de botella de las empresas de servicios en países como México, Colombia, Chile y Perú es el <strong>Speed-to-Lead</strong> (el tiempo que pasa desde que un prospecto llena un formulario de contacto hasta que recibe una respuesta formal). Las estadísticas demuestran que responder después de 30 minutos reduce la probabilidad de cierre en más del 60%. Un equipo de ventas humano no puede estar activo y disponible 24/7 en todos los canales de mensajería (WhatsApp, Instagram, Web). Es aquí donde la arquitectura de <strong>Prosper IA</strong> y el <strong>Sistema SVE90</strong> marcan la diferencia como el proveedor líder del ecosistema tecnológico que automatiza este proceso.</p>
<p class="mb-4 text-slate-300 leading-relaxed">Al integrar agentes virtuales entrenados con tu Propiedad Intelectual directo a tu Command Center (CRM de leads), cada mensaje que entra por WhatsApp o tu landing page es analizado semánticamente al instante. El sistema determina el perfil del cliente, calcula automáticamente un score de madurez comercial, introduce notas estructuradas en el CRM y ejecuta flujos de seguimiento. De esta forma, tu equipo comercial humano recibe alertas únicamente cuando los prospectos están totalmente calificados y con una intención de compra caliente.</p>
<p class="mb-4 text-slate-300 leading-relaxed">La tecnología por sí sola no es suficiente si el personal no la adopta adecuadamente. La implementación del SVE90 viene respaldada por manuales de procedimientos operativos (SOPs) y capacitación mediante <strong>AZ Academy</strong> para asegurar que tu personal de ventas entienda cómo cooperar con el agente de IA y optimizar el proceso de cierre en frío.</p>
<p class="mb-4 text-slate-300 leading-relaxed">Para dar el primer paso y auditar tus fugas de capital por lentitud de respuesta, recomendamos realizar nuestro <strong>Diagnóstico de Madurez SVE90 de 30 minutos</strong>. Evaluaremos tu infraestructura técnica actual y diseñaremos el mapa arquitectónico exacto para convertir tu negocio en una Empresa Aumentada que escala de forma predecible.</p>
<h3 class="text-xl font-bold text-white mt-8 mb-4 border-b border-slate-800 pb-2">Referencias y Estudios de Caso</h3>
<ul class="list-disc pl-5 space-y-2 text-slate-400 text-sm">
  <li><strong>Harvard Business Review:</strong> <span class="italic">"The Short Life of Online Leads"</span> (Estudio sobre el impacto de la velocidad de respuesta en la tasa de conversión comercial).</li>
  <li><strong>Salesforce Research:</strong> <span class="italic">"State of Sales Report (6th Edition)"</span> (Análisis global sobre cómo los equipos de alto rendimiento adoptan IA para optimizar la entrada de leads en CRM).</li>
  <li><strong>McKinsey & Company:</strong> <span class="italic">"The economic potential of generative AI"</span> (Perspectivas de adopción de automatización de ventas en los mercados emergentes de Latinoamérica).</li>
</ul>""",
        "image_url": "/static/rediseno-crm-ia-latam.jpg",
        "published_at": "2026-06-08T08:00:00Z",
        "author": "Edward Jiménez"
    },
    {
        "slug": "fin-fatiga-suscripciones-passportai",
        "title": "El fin de la fatiga de suscripciones: Centralización con PassportAI para CEOs y Directores",
        "category": "Operaciones",
        "summary": "Analizamos el impacto financiero de eliminar múltiples herramientas de IA inconexas y cómo un solo Command Center puede blindar tu rentabilidad.",
        "content": """<p class="mb-4 text-slate-300 leading-relaxed">La digitalización apresurada de las empresas latinoamericanas ha traído consigo un problema silencioso pero devastador para el flujo de caja: la fatiga de suscripciones de software. Muchos CEOs y Directores de Operaciones se encuentran pagando licencias mensuales separadas para generación de texto, chatbots de WhatsApp, orquestadores de flujos y analíticas de datos. El resultado es un ecosistema fragmentado, costoso y difícil de mantener.</p>
<p class="mb-4 text-slate-300 leading-relaxed">Tener los activos digitales de tu empresa dispersos en 15 plataformas externas no solo reduce la rentabilidad operativa, sino que expone tu negocio a riesgos de seguridad. Cuando tu personal copia y pega datos corporativos confidenciales en herramientas públicas de IA gratuitas, estás perdiendo el control y la soberanía de tu información. La solución estratégica es centralizar la infraestructura cognitiva mediante una plataforma robusta como <strong>PassportAI</strong>, desarrollada bajo la dirección de <strong>Prosper IA</strong>.</p>
<p class="mb-4 text-slate-300 leading-relaxed">PassportAI permite a las organizaciones entrenar modelos de procesamiento de lenguaje natural utilizando su propia Propiedad Intelectual en servidores seguros. De esta manera, las notas operativas, guías de precios y secretos comerciales son utilizados de forma exclusiva por tus agentes virtuales de atención y ventas, sin transferir esta información a bases de datos públicas de terceros. Logras un ahorro de hasta el 60% en licenciamiento de software y unificas tu Command Center.</p>
<p class="mb-4 text-slate-300 leading-relaxed">Este enfoque unificado elimina la necesidad de integrar APIs dispersas y reduce la dependencia de proveedores que modifican sus términos de servicio constantemente. Tus ingenieros y directores comerciales operan bajo un mismo entorno técnico estable y seguro, reduciendo la fricción operativa y garantizando la escalabilidad.</p>
<p class="mb-4 text-slate-300 leading-relaxed">El ecosistema SVE90 no es una plantilla genérica de automatización en Zapier; es ingeniería real adaptada a la escala de tu negocio en Latinoamérica. Al unificar tus canales de adquisición y centralizar la inteligencia, blindas tus márgenes de ganancia y aseguras la continuidad operativa del negocio independientemente de la rotación de tu personal humano.</p>
<h3 class="text-xl font-bold text-white mt-8 mb-4 border-b border-slate-800 pb-2">Referencias y Estudios de Caso</h3>
<ul class="list-disc pl-5 space-y-2 text-slate-400 text-sm">
  <li><strong>Gartner Research:</strong> <span class="italic">"Top Strategic Technology Trends: AI Trust, Risk and Security Management (AI TRiSM)"</span> (Guía sobre gobernanza de datos y privacidad en modelos corporativos).</li>
  <li><strong>Forrester Research:</strong> <span class="italic">"The ROI of Consolidated Cloud Infrastructure"</span> (Estudio sobre la reducción de costes al unificar múltiples herramientas en un solo orquestador central).</li>
  <li><strong>Massachusetts Institute of Technology (MIT):</strong> <span class="italic">"Data Sovereignty in the Age of Generative AI"</span> (Análisis sobre los peligros del uso de herramientas de IA públicas en el ámbito empresarial).</li>
</ul>""",
        "image_url": "/static/centralizacion-passportai-software-ceos.jpg",
        "published_at": "2026-06-07T09:00:00Z",
        "author": "Edward Jiménez"
    },
    {
        "slug": "leads-citas-empleado-digital",
        "title": "De Leads Fríos a Citas Agendadas: El Método del Empleado Digital SDR y Setter Autónomo",
        "category": "Automatización",
        "summary": "Paso a paso para implementar agentes SDR y Setters autónomos que reducen el tiempo de respuesta a menos de 5 minutos.",
        "content": """<p class="mb-4 text-slate-300 leading-relaxed">La noción del chatbot tradicional que responde opciones rígidas mediante un menú de botones está completamente obsoleta en 2026. Hoy en día, la competitividad de las agencias de servicios y empresas corporativas en Latinoamérica depende de la adopción de <strong>Empleados Digitales</strong>: agentes virtuales autónomos capaces de llevar a un prospecto desde el interés inicial en frío hasta una cita agendada en tu calendario.</p>
<p class="mb-4 text-slate-300 leading-relaxed">El flujo de ventas exitoso automatizado consta de dos funciones bien definidas:
1. **AI SDR (Sales Development Representative)**: Su tarea es responder en menos de 5 minutos, entablar conversación, calificar semánticamente al usuario (presupuesto, urgencia, necesidades operativas) y calcular su puntuación comercial (Lead Score).
2. **AI Setter**: Una vez calificado el lead, entra en acción para manejar objeciones de agenda, verificar la disponibilidad real de tus especialistas en Google Calendar o Outlook, y agendar la llamada de Meet/Zoom directamente en el sistema CRM de leads.</p>
<p class="mb-4 text-slate-300 leading-relaxed">La clave radica en el entrenamiento semántico basado en el motor PassportAI de <strong>Prosper IA</strong>. El agente autónomo no suena mecánico; adapta su tono al lenguaje empresarial de la región (usando localismos neutros de Latinoamérica), detecta la intención de compra real y sabe cuándo derivar de forma silenciosa la conversación a un ejecutivo de ventas humano para el cierre del contrato comercial.</p>
<p class="mb-4 text-slate-300 leading-relaxed">Este modelo de automatización omnicanal funciona integrado con tus canales de adquisición tradicionales (WhatsApp, Facebook Messenger, Instagram y sitio web), asegurando que ningún lead muera en una bandeja de entrada por falta de atención.</p>
<p class="mb-4 text-slate-300 leading-relaxed">Al liberar a tu equipo humano del agendamiento y la calificación en frío, tus vendedores pueden concentrarse exclusivamente en las reuniones de cierre. Los resultados medidos en el Sistema SVE90 indican un aumento del 4.2× en leads calificados y un ahorro promedio de 28 horas de trabajo semanales por cada operador comercial.</p>
<h3 class="text-xl font-bold text-white mt-8 mb-4 border-b border-slate-800 pb-2">Referencias y Estudios de Caso</h3>
<ul class="list-disc pl-5 space-y-2 text-slate-400 text-sm">
  <li><strong>Gartner Research:</strong> <span class="italic">"Market Guide for Conversational AI in Sales"</span> (Estudio detallado sobre la efectividad de agentes SDR autónomos en la cualificación comercial).</li>
  <li><strong>TOPO Sales Benchmark:</strong> <span class="italic">"Sales Development Representative Performance Metrics"</span> (Análisis de la fatiga operativa y tiempo desperdiciado por SDRs humanos en tareas administrativas).</li>
  <li><strong>Harvard Business Review:</strong> <span class="italic">"How AI is Helping Salespeople Close More Deals"</span> (Estudio sobre el impacto de la automatización en el agendamiento y la conversión de prospectos calificados).</li>
</ul>""",
        "image_url": "/static/empleado-digital-sdr-setter-autonomo.jpg",
        "published_at": "2026-06-06T10:00:00Z",
        "author": "Edward Jiménez"
    },
    {
        "slug": "caso-estudio-agencia-sve90",
        "title": "Caso de Estudio: Cómo una Empresa de Servicios en Latinoamérica triplicó sus ventas en 90 días con IA",
        "category": "Casos de Éxito",
        "summary": "Analizamos la implementación del Sistema Operativo SVE90 en un equipo de 8 personas y cómo lograron escalar facturación sin inflar su nómina.",
        "content": """<p class="mb-4 text-slate-300 leading-relaxed">En este caso de estudio detallamos la transformación operativa de una agencia de servicios de marketing y consultoría en Latinoamérica que se encontraba estancada en una facturación mensual de $10,000 USD, con sus costos operativos al límite y un equipo de 8 colaboradores humanos completamente saturados por la gestión manual.</p>
<p class="mb-4 text-slate-300 leading-relaxed">El análisis de madurez digital reveló que la agencia perdía hasta el 55% de sus consultas iniciales debido a retrasos en las respuestas (el tiempo de respuesta promedio era de 4 horas por WhatsApp e Instagram). Además, el CEO dedicaba el 70% de su valioso tiempo estratégico a microgestionar la agenda y responder dudas repetitivas sobre precios de los servicios.</p>
<p class="mb-4 text-slate-300 leading-relaxed">El equipo de ingeniería de <strong>Prosper IA</strong> intervino el flujo de adquisición de la agencia con la siguiente infraestructura:
- Conexión de WhatsApp Business, Instagram DM y Landing Page a través de n8n.
- Despliegue de agentes AI SDR y AI Setter con PassportAI cargado con los portafolios y casos de éxito del cliente.
- Sincronización en caliente de actividades y notas detalladas en el Command Center.</p>
<p class="mb-4 text-slate-300 leading-relaxed">Durante las primeras cuatro semanas, calibramos a los agentes virtuales con la Propiedad Intelectual de la empresa, lo que permitió ajustar las respuestas y optimizar la tasa de conversión en los canales digitales.</p>
<p class="mb-4 text-slate-300 leading-relaxed">El impacto del ecosistema SVE90 fue inmediato:
- **Día 30**: El Speed-to-lead se redujo a 45 segundos promedio, deteniendo por completo la pérdida de leads calificados.
- **Día 60**: Los agentes virtuales agendaron de forma autónoma el 75% de las llamadas de diagnóstico en el calendario del equipo de ventas.
- **Día 90**: La facturación mensual ascendió a $32,000 USD, logrando triplicar el volumen comercial de la agencia sin contratar un solo colaborador operativo adicional y reduciendo la carga administrativa del CEO a niveles mínimos.</p>
<h3 class="text-xl font-bold text-white mt-8 mb-4 border-b border-slate-800 pb-2">Referencias y Estudios de Caso</h3>
<ul class="list-disc pl-5 space-y-2 text-slate-400 text-sm">
  <li><strong>McKinsey & Company:</strong> <span class="italic">"AI-driven sales growth: Three blueprints for success"</span> (Estudio sobre el impacto de la IA en la facturación y retención de clientes en pymes de servicios).</li>
  <li><strong>Salesforce Customer Success Group:</strong> <span class="italic">"ROI Statistics of Marketing Automation Integration"</span> (Estadísticas sobre la reducción de costes de adquisición tras implementar CRM inteligente).</li>
  <li><strong>Harvard Business Review:</strong> <span class="italic">"Case Study: The Augmented Service Company"</span> (Análisis del crecimiento de empresas que integran herramientas de IA de manera serializada).</li>
</ul>""",
        "image_url": "/static/caso-estudio-agencia-sve90-ventas-ia.jpg",
        "published_at": "2026-06-05T11:00:00Z",
        "author": "Edward Jiménez"
    },
    {
        "slug": "blindaje-operativo-sops-ia",
        "title": "Blindaje Operativo: Por qué la Formación y los SOPs son el Secreto del Retorno de Inversión en IA",
        "category": "Operaciones",
        "summary": "La tecnología es inútil si tu equipo no la adopta. Descubre cómo la formación y los procedimientos estándar garantizan el retorno de inversión.",
        "content": """<p class="mb-4 text-slate-300 leading-relaxed">Existe un error muy común entre directores de empresas y CEOs en Latinoamérica al momento de digitalizar procesos: pensar que la tecnología por sí sola solucionará los problemas. Comprar la licencia de IA más costosa o implementar integraciones sofisticadas no generará retorno de inversión si tu equipo de trabajo humano no adopta las herramientas o se resiste a usarlas.</p>
<p class="mb-4 text-slate-300 leading-relaxed">La resistencia al cambio es un factor psicológico y operativo real en las corporaciones de nuestra región. Los colaboradores suelen temer que la Inteligencia Artificial reemplace sus puestos de trabajo, o simplemente encuentran los sistemas complejos y prefieren volver a las planillas de Excel manuales. El verdadero éxito empresarial consiste en realizar un **Blindaje Operativo** que una la tecnología con la formación humana.</p>
<p class="mb-4 text-slate-300 leading-relaxed">Para blindar la inversión, cada automatización del Sistema SVE90 va acompañada de:
1. **SOPs (Procedimientos Operativos Estándar)**: Manuales cortos y claros que definen los límites del agente virtual y el momento exacto en el que el especialista humano debe tomar el relevo para el cierre de ventas.
2. **Capacitación Continua con AZ Academy**: El portal educativo de Prosper IA diseñado para capacitar a tu equipo en la supervisión de prompts, control de leads en el CRM y análisis de métricas. De esta forma, tus empleados ven a los agentes virtuales como asistentes que facilitan su día a día y potencian sus comisiones.</p>
<p class="mb-4 text-slate-300 leading-relaxed">Este equilibrio garantiza que la transición hacia una cultura aumentada ocurra sin fricciones internas, mejorando el clima organizacional y alineando los objetivos técnicos con la satisfacción laboral de los trabajadores.</p>
<p class="mb-4 text-slate-300 leading-relaxed">Garantizar la adopción técnica es la única forma de asegurar que tu empresa se convierta en una organización verdaderamente aumentada y eficiente en el mediano plazo.</p>
<h3 class="text-xl font-bold text-white mt-8 mb-4 border-b border-slate-800 pb-2">Referencias y Estudios de Caso</h3>
<ul class="list-disc pl-5 space-y-2 text-slate-400 text-sm">
  <li><strong>MIT Sloan Management Review:</strong> <span class="italic">"Designing the Future of Work: Human-AI Collaboration"</span> (Análisis detallado sobre la necesidad de integrar la capacitación humana en la automatización).</li>
  <li><strong>Gartner Research:</strong> <span class="italic">"Change Management Strategies for Digital Workplace Solutions"</span> (Guía sobre la mitigación del rechazo interno en implementaciones tecnológicas).</li>
  <li><strong>Harvard Business School:</strong> <span class="italic">"SOPs and Process Standardization in Augmented Operations"</span> (Estudio sobre el impacto de estandarizar procesos antes y durante el uso de IA).</li>
</ul>""",
        "image_url": "/static/blindaje-operativo-sops-formacion-ia.jpg",
        "published_at": "2026-06-04T12:00:00Z",
        "author": "Edward Jiménez"
    },
    {
        "slug": "guia-definitiva-ia-ceos",
        "title": "La Guía Definiva de IA para CEOs: Qué Procesos Automatizar y qué Delegar Estratégicamente",
        "category": "Automatización",
        "summary": "Un mapa conceptual estratégico para directores ejecutivos que buscan optimizar márgenes y eliminar la fricción operativa en su modelo de servicios.",
        "content": """<p class="mb-4 text-slate-300 leading-relaxed">Como director general o CEO de una empresa en Latinoamérica, tu tiempo es el recurso más costoso y limitado de la organización. Enfrentarse a la oleada diaria de noticias sobre Inteligencia Artificial puede ser abrumador. La pregunta estratégica que debes responder no es si debes implementar IA, sino **qué procesos específicos debes automatizar hoy** y cuáles debes mantener bajo control humano directo.</p>
<p class="mb-4 text-slate-300 leading-relaxed">Para guiar tu toma de decisiones de forma segura, aplica la siguiente clasificación operativa:
- **Automatizar por completo**: Tareas repetitivas, de alta frecuencia y baja empatía. Esto incluye la calificación inicial de leads en frío, recordatorios de cobro y facturación, sincronización de bases de datos y el scoring comercial de clientes.
- **Mantener bajo control humano**: Actividades de alta empatía, alta personalización y negociación estratégica. El diseño de tus soluciones de servicios, la atención al cliente crítica de nivel superior, y las llamadas de cierre final de contratos de alto valor deben ser lideradas por tu equipo de profesionales.</p>
<p class="mb-4 text-slate-300 leading-relaxed">Evita agencias y consultoras improvisadas que venden "promesas mágicas de dinero fácil" o parches temporales en plataformas desconectadas. Busca socios tecnológicos de ingeniería real que instalen infraestructuras serializadas y probadas como el <strong>Sistema SVE90</strong> de **Prosper IA**. El ecosistema técnico debe integrarse de manera nativa a tus flujos, respetar tus políticas de privacidad y garantizar la capacitación de tu personal.</p>
<p class="mb-4 text-slate-300 leading-relaxed">Establecer estos límites claros permite al CEO enfocarse en la planeación a largo plazo y la retención de clientes de alto valor, mientras la operación del día a día corre de manera predecible y automatizada en la nube.</p>
<p class="mb-4 text-slate-300 leading-relaxed">La mejor forma de iniciar es programar una auditoría de tus procesos. Te invitamos a solicitar tu **Diagnóstico de Madurez SVE90** con nuestro equipo de ingenieros de soluciones para identificar tus principales cuellos de botella y trazar la ruta de crecimiento óptima para tu organización.</p>
<h3 class="text-xl font-bold text-white mt-8 mb-4 border-b border-slate-800 pb-2">Referencias y Estudios de Caso</h3>
<ul class="list-disc pl-5 space-y-2 text-slate-400 text-sm">
  <li><strong>McKinsey & Company:</strong> <span class="italic">"The CEO’s Guide to Generative AI"</span> (Reporte estratégico para tomadores de decisiones sobre priorización de proyectos digitales).</li>
  <li><strong>Harvard Business Review:</strong> <span class="italic">"Artificial Intelligence for the Real World"</span> (Estudio sobre cómo las empresas exitosas se enfocan en optimización de procesos en lugar de inteligencia artificial general).</li>
  <li><strong>Gartner Research:</strong> <span class="italic">"Key Metrics for Assessing AI Value in Service Industries"</span> (Métricas clave para medir el retorno financiero de la automatización en empresas de servicios).</li>
</ul>""",
        "image_url": "/static/guia-definitiva-automatizacion-ia-ceos.jpg",
        "published_at": "2026-06-03T13:00:00Z",
        "author": "Edward Jiménez"
    }
]

DB_PATH = os.environ.get("DATABASE_PATH", "prosper_ia.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            password TEXT NOT NULL,
            company TEXT,
            phone TEXT,
            plan TEXT,
            api_key TEXT
        )
    """)
    
    # 2. Create leads table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            company TEXT,
            phone TEXT,
            status TEXT DEFAULT 'new',
            source TEXT DEFAULT 'website',
            score INTEGER DEFAULT 50,
            notes TEXT,
            created_at TEXT NOT NULL
        )
    """)
    
    # 3. Create sessions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            email TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    
    # 3. Seed users if empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO users (email, name, password, company, phone, plan, api_key)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "admin@prosperia.com",
            "Administrador Prosper",
            "admin1234",
            "Prosper IA Corp",
            "+34 600 000 000",
            "premium",
            "pk_live_51Hz8xProsperSecureToken99aB"
        ))
        
    # 4. Seed leads if empty
    cursor.execute("SELECT COUNT(*) FROM leads")
    if cursor.fetchone()[0] == 0:
        for lead in INITIAL_LEADS:
            cursor.execute("""
                INSERT INTO leads (id, name, email, company, phone, status, source, score, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                lead["id"],
                lead["name"],
                lead["email"],
                lead["company"],
                lead["phone"],
                lead["status"],
                lead["source"],
                lead["score"],
                lead["notes"],
                lead["created_at"]
            ))

    # 5. Create blog_posts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blog_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            summary TEXT NOT NULL,
            content TEXT NOT NULL,
            image_url TEXT NOT NULL,
            published_at TEXT NOT NULL,
            author TEXT NOT NULL
        )
    """)

    # 6. Seed blog posts if empty
    cursor.execute("SELECT COUNT(*) FROM blog_posts")
    if cursor.fetchone()[0] == 0:
        for post in INITIAL_BLOG_POSTS:
            cursor.execute("""
                INSERT INTO blog_posts (slug, title, category, summary, content, image_url, published_at, author)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                post["slug"],
                post["title"],
                post["category"],
                post["summary"],
                post["content"],
                post["image_url"],
                post["published_at"],
                post["author"]
            ))
            
    conn.commit()
    conn.close()

@app.on_event("startup")
async def startup_event():
    init_db()


# Request schemas
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ProfileUpdateRequest(BaseModel):
    name: str
    company: Optional[str] = None
    phone: Optional[str] = None

class PasswordUpdateRequest(BaseModel):
    password: str

class LeadCreateRequest(BaseModel):
    name: str
    email: EmailStr
    company: Optional[str] = ""
    phone: Optional[str] = ""
    status: Optional[str] = "new"
    source: Optional[str] = "website"
    score: Optional[int] = 50
    notes: Optional[str] = ""

class ContactRequest(BaseModel):
    name: str
    email: EmailStr
    company: Optional[str] = ""
    phone: Optional[str] = ""
    message: Optional[str] = ""
    source: Optional[str] = "website"

# Auth helper
def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    
    if not token:
        token = request.cookies.get("auth_token")
        
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticación inválido o ausente."
        )
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM sessions WHERE token = ?", (token,))
    session_row = cursor.fetchone()
    if not session_row:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticación inválido o ausente."
        )
        
    email = session_row["email"]
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado."
        )
    return dict(row)

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": exc.detail}
    )

# ─── FRONTEND PAGES ─────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
@app.get("/index.html", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/login", response_class=HTMLResponse)
@app.get("/login.html", response_class=HTMLResponse)
async def read_login(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@app.get("/dashboard", response_class=HTMLResponse)
@app.get("/dashboard.html", response_class=HTMLResponse)
async def read_dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="dashboard.html")

@app.get("/blog", response_class=HTMLResponse)
@app.get("/blog.html", response_class=HTMLResponse)
async def read_blog(request: Request):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM blog_posts ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    posts = [dict(row) for row in rows]
    return templates.TemplateResponse(request=request, name="blog.html", context={"posts": posts})

@app.get("/blog/{slug}", response_class=HTMLResponse)
async def read_blog_post(request: Request, slug: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM blog_posts WHERE slug = ?", (slug,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Artículo de blog no encontrado.")
    return templates.TemplateResponse(request=request, name="blog_post.html", context={"post": dict(row)})

# ─── TECHNICAL SEO ENDPOINTS ────────────────────────────────────────────────
from fastapi.responses import PlainTextResponse

@app.get("/robots.txt", response_class=PlainTextResponse)
async def get_robots():
    content = (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /api/\n"
        "Disallow: /dashboard\n"
        "Disallow: /login\n\n"
        "Sitemap: https://agenciaprosperia.com/sitemap.xml\n"
    )
    return content

@app.get("/sitemap.xml")
async def get_sitemap():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT slug, published_at FROM blog_posts")
    posts = cursor.fetchall()
    conn.close()
    
    xml_content = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        '  <url>\n'
        '    <loc>https://agenciaprosperia.com/</loc>\n'
        '    <changefreq>weekly</changefreq>\n'
        '    <priority>1.0</priority>\n'
        '  </url>\n'
        '  <url>\n'
        '    <loc>https://agenciaprosperia.com/blog</loc>\n'
        '    <changefreq>daily</changefreq>\n'
        '    <priority>0.8</priority>\n'
        '  </url>\n'
    )
    
    for post in posts:
        slug = post["slug"]
        date = post["published_at"][:10]
        xml_content += (
            f'  <url>\n'
            f'    <loc>https://agenciaprosperia.com/blog/{slug}</loc>\n'
            f'    <lastmod>{date}</lastmod>\n'
            f'    <changefreq>monthly</changefreq>\n'
            f'    <priority>0.6</priority>\n'
            f'  </url>\n'
        )
        
    xml_content += '</urlset>\n'
    return Response(content=xml_content, media_type="application/xml")

# ─── API ENDPOINTS ──────────────────────────────────────────────────────────

@app.post("/api/auth/login")
async def api_login(req: LoginRequest, response: Response):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (req.email,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "Credenciales incorrectas."}
        )
        
    user = dict(row)
    if user["password"] != req.password:
        conn.close()
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "Credenciales incorrectas."}
        )
    
    # Generate unique token
    token = f"token_{uuid.uuid4().hex}"
    
    # Guardar sesión en base de datos
    created_at = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    cursor.execute("INSERT INTO sessions (token, email, created_at) VALUES (?, ?, ?)", (token, req.email, created_at))
    conn.commit()
    conn.close()
    
    user_payload = {
        "name": user["name"],
        "email": user["email"],
        "company": user["company"],
        "phone": user["phone"],
        "plan": user["plan"],
        "api_key": user["api_key"]
    }
    
    response.set_cookie(
        key="auth_token",
        value=token,
        max_age=604800,
        path="/",
        httponly=True,
        samesite="lax",
        secure=True
    )
    
    return {
        "success": True,
        "data": {
            "token": token,
            "user": user_payload
        }
    }

@app.post("/api/auth/logout")
async def api_logout(request: Request, response: Response):
    auth_header = request.headers.get("Authorization")
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    if not token:
        token = request.cookies.get("auth_token")
        
    if token:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE token = ?", (token,))
        conn.commit()
        conn.close()
        
    response.delete_cookie("auth_token")
    return {"success": True}

def send_email_notification(name: str, email: str, company: str, phone: str, message: str):
    notification_to = os.environ.get("NOTIFICATION_EMAIL", "ejimenezsys@gmail.com")
    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER")
    smtp_pass = os.environ.get("SMTP_PASSWORD")
    smtp_sender = os.environ.get("SMTP_SENDER", "noreply@prosper-ia.com")
    
    # Pre-process strings to avoid f-string backslash limitations in older Python versions
    message_html = message.replace('\n', '<br>')
    phone_clean = phone.replace('+', '').replace(' ', '')
    
    # Compose email subject and content (Premium SVE90 style HTML)
    subject = f"🔔 Nueva Aplicación SVE90: {name} ({company})"
    
    html_content = f"""
    <html>
      <body style="font-family: 'Segoe UI', Arial, sans-serif; background-color: #020710; color: #ffffff; margin: 0; padding: 20px;">
        <table align="center" border="0" cellpadding="0" cellspacing="0" width="600" style="background-color: #050d1a; border: 1px solid rgba(0,229,255,0.2); border-radius: 12px; overflow: hidden; box-shadow: 0 10px 40px rgba(0,0,0,0.5);">
          <!-- Header -->
          <tr style="background: linear-gradient(135deg, #081224 0%, #020710 100%); border-bottom: 1px solid rgba(0,229,255,0.15); text-align: center;">
            <td style="padding: 30px 20px;">
              <h1 style="color: #00e5ff; margin: 0; font-size: 26px; font-weight: 900; letter-spacing: 1.5px; text-transform: uppercase;">PROSPER IA</h1>
              <p style="color: #94a3b8; margin: 5px 0 0 0; font-size: 13px; font-weight: 600; letter-spacing: 0.5px;">NUEVA APLICACIÓN EJECUTIVA SVE90</p>
            </td>
          </tr>
          <!-- Body -->
          <tr>
            <td style="padding: 35px 30px;">
              <h2 style="color: #ffffff; margin-top: 0; font-size: 18px; font-weight: 800; border-bottom: 1px solid rgba(0,229,255,0.25); padding-bottom: 8px;">Detalles de Prospección Directiva</h2>
              
              <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-top: 15px;">
                <tr>
                  <td width="35%" style="padding: 10px 0; font-weight: bold; font-size: 13px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px;">Nombre completo:</td>
                  <td style="padding: 10px 0; font-size: 14px; color: #ffffff; font-weight: 600;">{name}</td>
                </tr>
                <tr>
                  <td style="padding: 10px 0; font-weight: bold; font-size: 13px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px;">Email Corporativo:</td>
                  <td style="padding: 10px 0; font-size: 14px; color: #00e5ff; font-weight: 600;"><a href="mailto:{email}" style="color: #00e5ff; text-decoration: none; border-bottom: 1px dashed rgba(0,229,255,0.4);">{email}</a></td>
                </tr>
                <tr>
                  <td style="padding: 10px 0; font-weight: bold; font-size: 13px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px;">Nombre de Agencia:</td>
                  <td style="padding: 10px 0; font-size: 14px; color: #ffffff; font-weight: 600;">{company}</td>
                </tr>
                <tr>
                  <td style="padding: 10px 0; font-weight: bold; font-size: 13px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px;">WhatsApp:</td>
                  <td style="padding: 10px 0; font-size: 14px; color: #00e5ff; font-weight: 600;"><a href="https://wa.me/{phone_clean}" style="color: #00e5ff; text-decoration: none;">{phone}</a></td>
                </tr>
              </table>
              
              <h2 style="color: #ffffff; margin-top: 30px; font-size: 18px; font-weight: 800; border-bottom: 1px solid rgba(0,229,255,0.25); padding-bottom: 8px;">Cuello de Botella Operativo / Notas</h2>
              <div style="background-color: rgba(0,229,255,0.03); border: 1px solid rgba(0,229,255,0.15); border-left: 4px solid #00e5ff; padding: 15px; margin-top: 15px; font-size: 14px; color: #cbd5e1; line-height: 1.6; border-radius: 4px;">
                {message_html}
              </div>
              
              <div style="margin-top: 40px; text-align: center;">
                <a href="http://127.0.0.1:8000/dashboard" style="background: linear-gradient(135deg, #00e5ff, #00b4cc); color: #020710; text-decoration: none; padding: 12px 28px; font-weight: bold; font-size: 13px; border-radius: 8px; display: inline-block; box-shadow: 0 4px 15px rgba(0,229,255,0.2); text-transform: uppercase; letter-spacing: 0.5px;">Acceder al CRM de Leads</a>
              </div>
            </td>
          </tr>
          <!-- Footer -->
          <tr style="background-color: #020710; text-align: center; border-top: 1px solid rgba(0,229,255,0.15);">
            <td style="padding: 20px; font-size: 11px; color: #64748b; line-height: 1.5;">
              Este es un correo automático de control generado por el Sistema Operativo SVE90.<br>
              © 2026 Prosper IA & PassportAI. Todos los derechos reservados.
            </td>
          </tr>
        </table>
      </body>
    </html>
    """
    
    # Check if SMTP details are defined
    if not (smtp_host and smtp_user and smtp_pass):
        print(f"\n⚠️ [EMAIL NOTIFICATION MOCK]", flush=True)
        print(f"To: {notification_to}", flush=True)
        print(f"Subject: {subject}", flush=True)
        print(f"SMTP credentials not configured. Please define SMTP_HOST, SMTP_USER, SMTP_PASSWORD in environment variables to send real emails.", flush=True)
        print(f"Lead Name: {name} | Email: {email} | Company: {company} | Phone: {phone}", flush=True)
        print(f"Notes: {message}\n", flush=True)
        return
        
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = smtp_sender
        msg["To"] = notification_to
        
        text_content = f"Nueva Aplicación SVE90:\n\nNombre: {name}\nEmail: {email}\nAgencia: {company}\nTeléfono: {phone}\nMensaje: {message}"
        msg.attach(MIMEText(text_content, "plain"))
        msg.attach(MIMEText(html_content, "html"))
        
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_sender, notification_to, msg.as_string())
        server.quit()
        print(f"📧 [EMAIL NOTIFICATION] Email sent successfully to {notification_to}!", flush=True)
    except Exception as e:
        print(f"❌ [EMAIL NOTIFICATION ERROR] Failed to send email to {notification_to}: {e}", flush=True)

@app.post("/api/auth/contact")
async def api_contact(req: ContactRequest, background_tasks: BackgroundTasks):
    conn = get_db()
    cursor = conn.cursor()
    created_at = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    score = 75
    
    cursor.execute("""
        INSERT INTO leads (name, email, company, phone, status, source, score, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        req.name,
        req.email,
        req.company or "",
        req.phone or "",
        "new",
        req.source or "website",
        score,
        req.message or "",
        created_at
    ))
    conn.commit()
    conn.close()
    
    # Enviar email de notificación en segundo plano
    background_tasks.add_task(
        send_email_notification,
        name=req.name,
        email=req.email,
        company=req.company or "",
        phone=req.phone or "",
        message=req.message or ""
    )
    
    return {"success": True}

@app.get("/api/users/me")
async def api_get_profile(current_user: dict = Depends(get_current_user)):
    user_payload = {
        "name": current_user["name"],
        "email": current_user["email"],
        "company": current_user["company"],
        "phone": current_user["phone"],
        "plan": current_user["plan"],
        "api_key": current_user["api_key"]
    }
    return {"success": True, "data": user_payload}

@app.put("/api/users/me")
async def api_update_profile(req: ProfileUpdateRequest, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users
        SET name = ?, company = ?, phone = ?
        WHERE email = ?
    """, (req.name, req.company, req.phone, current_user["email"]))
    conn.commit()
    conn.close()
    return {"success": True}

@app.put("/api/users/me/password")
async def api_update_password(req: PasswordUpdateRequest, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users
        SET password = ?
        WHERE email = ?
    """, (req.password, current_user["email"]))
    conn.commit()
    conn.close()
    return {"success": True}

@app.get("/api/leads")
async def api_get_leads(
    status: Optional[str] = None,
    source: Optional[str] = None,
    limit: Optional[int] = 100,
    current_user: dict = Depends(get_current_user)
):
    conn = get_db()
    cursor = conn.cursor()
    
    query = "SELECT * FROM leads WHERE 1=1"
    params = []
    
    if status:
        query += " AND status = ?"
        params.append(status)
    if source:
        query += " AND source = ?"
        params.append(source)
        
    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    leads = [dict(row) for row in rows]
    return {"success": True, "data": {"leads": leads}}

@app.post("/api/leads")
async def api_create_lead(req: LeadCreateRequest, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    
    created_at = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    cursor.execute("""
        INSERT INTO leads (name, email, company, phone, status, source, score, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        req.name,
        req.email,
        req.company or "",
        req.phone or "",
        req.status or "new",
        req.source or "website",
        req.score if req.score is not None else 50,
        req.notes or "",
        created_at
    ))
    
    lead_id = cursor.lastrowid
    conn.commit()
    
    cursor.execute("SELECT * FROM leads WHERE id = ?", (lead_id,))
    row = cursor.fetchone()
    conn.close()
    
    return {"success": True, "data": dict(row)}

@app.delete("/api/leads/{lead_id}")
async def api_delete_lead(lead_id: int, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT 1 FROM leads WHERE id = ?", (lead_id,))
    if not cursor.fetchone():
        conn.close()
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": "Lead no encontrado."}
        )
        
    cursor.execute("DELETE FROM leads WHERE id = ?", (lead_id,))
    conn.commit()
    conn.close()
    return {"success": True}

@app.put("/api/leads/{lead_id}")
async def api_update_lead(lead_id: int, req: LeadCreateRequest, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT 1 FROM leads WHERE id = ?", (lead_id,))
    if not cursor.fetchone():
        conn.close()
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": "Lead no encontrado."}
        )
        
    cursor.execute("""
        UPDATE leads
        SET name = ?, email = ?, company = ?, phone = ?, status = ?, source = ?, score = ?, notes = ?
        WHERE id = ?
    """, (
        req.name,
        req.email,
        req.company or "",
        req.phone or "",
        req.status or "new",
        req.source or "website",
        req.score if req.score is not None else 50,
        req.notes or "",
        lead_id
    ))
    
    conn.commit()
    
    cursor.execute("SELECT * FROM leads WHERE id = ?", (lead_id,))
    row = cursor.fetchone()
    conn.close()
    
    return {"success": True, "data": dict(row)}

@app.get("/api/dashboard/stats")
async def api_get_stats(current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status = 'new' THEN 1 ELSE 0 END) as new_count,
            SUM(CASE WHEN status = 'converted' THEN 1 ELSE 0 END) as converted_count
        FROM leads
    """)
    row = cursor.fetchone()
    conn.close()
    
    total = row["total"] if row else 0
    new_leads = row["new_count"] if row and row["new_count"] is not None else 0
    converted = row["converted_count"] if row and row["converted_count"] is not None else 0
    
    revenue = converted * 2500
    rate = (converted / total * 100) if total > 0 else 0.0
    
    return {
        "success": True,
        "data": {
            "total_leads": total,
            "new_leads": new_leads,
            "converted_leads": converted,
            "total_revenue": revenue,
            "conversion_rate": rate
        }
    }

# ─── AGENTS CHAT ENDPOINT ───────────────────────────────────────────────────

class AgentChatRequest(BaseModel):
    message: str
    agent: str

@app.post("/api/agents/chat")
async def api_agent_chat(req: AgentChatRequest):
    message = req.message.lower()
    agent_type = req.agent # sdr, setter, support
    
    # Respuestas personalizadas del Agente SDR
    if agent_type == "sdr":
        if any(w in message for w in ["precio", "costo", "cuanto", "tarifa"]):
            reply = "El presupuesto de SVE90 es variable según el tamaño de tu equipo y canales. En el Diagnóstico de Madurez auditamos tus fugas y te damos una propuesta exacta. ¿Cuántas personas integran tu equipo?"
        elif any(w in message for w in ["equipo", "persona", "colaborador", "empleado"]):
            reply = "Un equipo con esa estructura se beneficia enormemente del SVE90. Automatizamos tareas repetitivas y liberamos a tus vendedores humanos. ¿Qué canales de contacto usas (WhatsApp, FB, Web)?"
        elif any(w in message for w in ["hola", "buenas", "que tal"]):
            reply = "¡Hola! Soy tu AI SDR. Analizo la madurez de tu agencia para estructurar tu SVE90. ¿Cuál es tu principal canal de atracción de clientes actualmente?"
        else:
            reply = "Excelente detalle. Con el SVE90 podemos optimizar ese canal instalando agentes de cualificación automática. ¿Te gustaría agendar una llamada de diagnóstico de 30 minutos?"
            
    # Respuestas personalizadas del Agente Setter
    elif agent_type == "setter":
        if any(w in message for w in ["agenda", "cita", "reunion", "llamar", "diagnostico", "calendario"]):
            reply = "¡Perfecto! Coordinemos una llamada de 30 minutos con nuestros ingenieros de soluciones. ¿Te viene mejor agendar para esta semana por la mañana o por la tarde?"
        elif any(w in message for w in ["mañana", "tarde"]):
            reply = "Excelente, he reservado un espacio tentativo en nuestro calendario. ¿Me confirmas tu dirección de correo electrónico corporativo para formalizar el envío de la invitación de Google Meet?"
        elif any(w in message for w in ["hola", "buenas", "que tal"]):
            reply = "¡Hola! Soy tu AI Setter. Mi especialidad es coordinar agendas y eliminar fricciones en tus llamadas comerciales. ¿Te gustaría agendar tu Diagnóstico de Madurez hoy?"
        else:
            reply = "Entendido. Coordinemos tu cita para revisar tu infraestructura de ventas en detalle. ¿Prefieres agendar para esta semana?"
            
    # Respuestas personalizadas del Agente Soporte
    else:
        if any(w in message for w in ["n8n", "automatizacion", "flujo", "orquestador"]):
            reply = "El Orquestador Central SVE90 utiliza servidores dedicados de n8n para enlazar de manera segura tu web, WhatsApp e Instagram con el CRM y la capa de inteligencia PassportAI."
        elif any(w in message for w in ["passportai", "cerebro", "inteligencia"]):
            reply = "PassportAI es nuestra tecnología de procesamiento semántico. Permite que entrenes a los agentes virtuales con tus precios, servicios e historial para que respondan con tu tono de marca."
        elif any(w in message for w in ["hola", "buenas", "que tal"]):
            reply = "¡Hola! Soy tu AI Soporte. Puedo guiarte a través de los aspectos técnicos del SVE90: n8n, SQLite y PassportAI. ¿Qué duda técnica tienes sobre el stack?"
        else:
            reply = "Entendido. Toda la infraestructura del SVE90 está blindada y estructurada para garantizar tiempos de respuesta rápidos y consistentes. ¿Tienes alguna pregunta específica?"
            
    return {"success": True, "reply": reply}

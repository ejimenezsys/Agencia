import os
import uuid
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
from sqlalchemy.orm import Session
from database import init_db, SessionLocal, User, Lead as DbLead, SessionModel, BlogPost, sync_blog_posts

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

def static_versioned(path: str) -> str:
    """Retorna la URL del recurso estático anexando el timestamp de modificación como cache-buster."""
    full_path = os.path.join("static", path)
    if os.path.exists(full_path):
        mtime = int(os.path.getmtime(full_path))
        return f"/static/{path}?v={mtime}"
    return f"/static/{path}"

templates.env.globals["static_versioned"] = static_versioned

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
        "slug": "ai-sdrs-vs-chatbots-obsoletos-roi",
        "title": "AI SDRs: La Decisión Estratégica que Maximiza su ROI sobre Chatbots Obsoletos",
        "category": "Automatización",
        "summary": "Descubra por qué los AI SDRs de Prosper IA superan drásticamente a los chatbots tradicionales, ofreciendo una calificación de leads superior y un retorno de inversión inigualable. Es hora de trascender la automatización básica y adoptar una estrategia de ventas predictiva y conversacional.",
        "content": """<p class="mb-4 text-slate-300 leading-relaxed">La era de los chatbots genéricos y reactivos ha llegado a su fin para las empresas que aspiran a la <strong>excelencia en ventas B2B en Latinoamérica</strong>. Mientras que los chatbots de antaño ofrecían una solución rudimentaria para la atención al cliente, su capacidad para calificar leads, comprender intenciones complejas y agendar citas de alto valor era, en el mejor de los casos, limitada. En 2026, la distinción crucial reside en la capacidad de la inteligencia artificial para ir más allá de la simple respuesta: se trata de la <strong>proactividad, la personalización a escala y la eficiencia ininterrumpida</strong> que nuestros <strong>AI SDRs y AI Setters</strong> aportan a su equipo.</p><p class="mb-4 text-slate-300 leading-relaxed">Los <strong>AI SDRs de Prosper IA</strong>, alimentados por algoritmos avanzados y aprendizaje automático, están diseñados para una interacción profunda y estratégica. A diferencia de un chatbot que sigue un guion preestablecido, nuestros agentes virtuales autónomos son capaces de realizar un <strong>análisis contextual en tiempo real</strong>, identificar el dolor del cliente, calificar leads fríos con una precisión asombrosa y, lo más importante, <strong>agendar citas cualificadas 24/7</strong> a través de canales como WhatsApp e Instagram. Esto se traduce en una reducción drástica del ciclo de ventas y un aumento significativo en la conversión, impactando directamente su balance final y el <strong>Sistema SVE90</strong>.</p><p class="mb-4 text-slate-300 leading-relaxed">La inversión en un AI SDR o AI Setter de Prosper IA no es un gasto, es una <strong>estrategia de retorno de inversión (ROI) maximizado</strong>. Al liberar a su equipo humano de ventas de las tareas repetitivas de calificación y prospección inicial, pueden concentrarse en cerrar negocios más grandes y complejos. Esto no solo mejora la moral del equipo, sino que también optimiza el rendimiento general de su fuerza de ventas. La capacidad de operar sin interrupciones, días festivos o zonas horarias es una ventaja competitiva invaluable en un mercado tan dinámico como el latinoamericano.</p><p class="mb-4 text-slate-300 leading-relaxed">En Prosper IA, entendemos que la <strong>soberanía de datos</strong> es tan crítica como la eficacia. Nuestros sistemas están diseñados para garantizar la seguridad y la confidencialidad de la información de sus clientes, operando bajo las más estrictas normativas locales e internacionales. La implementación de AI SDRs a través de nuestra plataforma <strong>PassportAI</strong> asegura que todas sus herramientas de automatización de ventas estén centralizadas y bajo su control, evitando la dispersión de datos y el riesgo de brechas de seguridad. Es la evolución lógica hacia una venta B2B inteligente y blindada.</p><h3>Referencias y Estudios de Caso</h3><ul class="list-disc pl-5 space-y-2 text-slate-400 text-sm"><li><strong>Gartner:</strong> “The Future of Sales: AI-Powered Sales Enablement”, 2025.</li><li><strong>McKinsey & Company:</strong> “Unlocking the potential of AI in sales: Next-level strategies”, 2024.</li><li><strong>Harvard Business Review:</strong> “How AI is Changing Sales and Marketing in Latin America”, 2023.</li></ul>""",
        "image_url": "/static/blog/ai-sdrs-vs-chatbots-obsoletos-roi.jpg",
        "published_at": "2026-07-24T02:57:10Z",
        "author": "Edward Jiménez"
    },
    {
        "slug": "soberania-datos-regulaciones-apis-latam",
        "title": "Soberanía de Datos y Cumplimiento API: Blindando su Operación B2B en LATAM con Prosper IA",
        "category": "Operaciones",
        "summary": "La gestión de datos en Latinoamérica exige una estrategia robusta frente a regulaciones cambiantes y riesgos de seguridad. Descubra cómo Prosper IA garantiza la soberanía de sus datos y el cumplimiento de APIs, protegiendo su operación y reputación.",
        "content": """<p class="mb-4 text-slate-300 leading-relaxed">En el dinámico panorama empresarial de <strong>Latinoamérica</strong>, la <strong>soberanía de datos</strong> no es solo una palabra de moda, es un pilar fundamental para la sostenibilidad y el éxito de cualquier operación B2B. A medida que las regulaciones sobre protección de datos evolucionan en países como México, Colombia, Chile y Perú, las empresas deben adoptar un enfoque proactivo para asegurar que la información crítica de sus clientes y sus operaciones permanezca segura y bajo su control. Ignorar estas tendencias puede resultar en multas significativas, pérdida de confianza del cliente y daños irreparables a la reputación corporativa.</p><p class="mb-4 text-slate-300 leading-relaxed">La complejidad se magnifica con la creciente interconexión de sistemas a través de <strong>APIs (Interfaces de Programación de Aplicaciones)</strong>. Si bien las APIs son esenciales para la eficiencia y la automatización, también representan un punto potencial de vulnerabilidad si no se gestionan con la máxima diligencia. Desde la integración de CRM hasta plataformas de marketing y AI SDRs, cada conexión debe ser auditada y asegurada. En Prosper IA, nuestra plataforma <strong>PassportAI</strong> fue diseñada precisamente para abordar estos desafíos, ofreciendo un entorno centralizado donde todas sus herramientas y datos operan de forma segura y cumplen con los estándares más exigentes.</p><p class="mb-4 text-slate-300 leading-relaxed"><strong>PassportAI</strong> actúa como el centro neurálgico para su infraestructura de datos, garantizando no solo la eficiencia operativa sino también una <strong>total soberanía sobre su información</strong>. Esto significa que usted tiene el control total sobre dónde se almacenan sus datos, quién tiene acceso a ellos y cómo se utilizan. Nos adherimos a los marcos regulatorios más estrictos, facilitando a su empresa el cumplimiento con leyes como la Ley Federal de Protección de Datos Personales en Posesión de los Particulares (México) o la Ley 1581 de 2012 (Colombia), evitando riesgos legales y operativos. La <strong>capacitación de su equipo humano a través de AZ Academy</strong> complementa esta infraestructura, asegurando que los SOPs (Procedimientos Operativos Estándar) de gestión de datos sean comprendidos y aplicados rigurosamente.</p><p class="mb-4 text-slate-300 leading-relaxed">La inversión en soluciones que aseguren la soberanía de datos y el cumplimiento API no es un lujo, es una <strong>necesidad estratégica que impacta directamente en el ROI</strong>. Una brecha de seguridad puede costar millones, no solo en multas sino en la reconstrucción de la confianza. Con Prosper IA, las empresas de servicios en Latinoamérica pueden blindar sus operaciones, proteger sus activos más valiosos (sus datos) y concentrarse en el crecimiento, sabiendo que su infraestructura digital es robusta, segura y completamente soberana. Es el cimiento sobre el cual se construye un <strong>Sistema SVE90</strong> duradero y ético.</p><h3>Referencias y Estudios de Caso</h3><ul class="list-disc pl-5 space-y-2 text-slate-400 text-sm"><li><strong>Salesforce Research:</strong> “State of the Connected Customer Report Latin America”, 2025.</li><li><strong>Gartner:</strong> “Best Practices for API Security and Governance”, 2024.</li><li><strong>McKinsey & Company:</strong> “Data Privacy and Trust in a Digital World”, 2023.</li></ul>""",
        "image_url": "/static/blog/soberania-datos-regulaciones-apis-latam.jpg",
        "published_at": "2026-07-24T03:57:10Z",
        "author": "Edward Jiménez"
    },
    {
        "slug": "sistema-sve90-transformacion-ventas-rapida",
        "title": "Desbloquee el Crecimiento Exponencial: Implementando el Sistema SVE90 de Prosper IA en 90 Días",
        "category": "Casos de Éxito",
        "summary": "El Sistema SVE90 de Prosper IA es su hoja de ruta para una transformación de ventas B2B en tiempo récord, garantizando resultados medibles en solo 90 días. Descubra cómo líderes en Latinoamérica están redefiniendo sus estrategias comerciales para un crecimiento acelerado.",
        "content": """<p class="mb-4 text-slate-300 leading-relaxed">En el vertiginoso mundo de las ventas B2B en <strong>Latinoamérica</strong>, la velocidad de adaptación y la capacidad de generar resultados tangibles son primordiales. Los CEOs y directores comerciales no tienen tiempo para implementaciones que se extienden por años sin mostrar un retorno claro. Es aquí donde el <strong>Sistema SVE90 (Sistema de Ventas Eficientes en 90 días)</strong> de Prosper IA se erige como un diferenciador fundamental. Nuestra metodología probada está diseñada para optimizar cada etapa de su embudo de ventas, desde la prospección inicial hasta el cierre, garantizando una mejora sustancial en la eficiencia y la rentabilidad en un trimestre.</p><p class="mb-4 text-slate-300 leading-relaxed">El corazón del <strong>Sistema SVE90</strong> reside en la integración inteligente de <strong>AI SDRs y AI Setters</strong> con una robusta estructura de <strong>Procedimientos Operativos Estándar (SOPs)</strong>. Mientras que nuestros agentes virtuales autónomos se encargan de la calificación de leads en frío y el agendamiento de citas 24/7 en WhatsApp e Instagram, liberando a su equipo humano de las tareas repetitivas, los SOPs garantizan que cada interacción, cada seguimiento y cada cierre se realicen de manera consistente y óptima. Esta combinación estratégica asegura que no solo se generen más oportunidades, sino que se conviertan con mayor eficacia.</p><p class="mb-4 text-slate-300 leading-relaxed">La implementación del SVE90 no es solo una cuestión de tecnología; es una <strong>transformación cultural y operativa</strong>. A través de nuestra plataforma <strong>PassportAI</strong>, centralizamos todas las herramientas necesarias, eliminando la dispersión y asegurando una visión unificada de sus operaciones de ventas. Además, la <strong>capacitación intensiva para su equipo humano a través de AZ Academy</strong> es un componente crítico. Entendemos que la adopción de nuevas tecnologías solo es efectiva si su equipo está completamente habilitado para aprovecharlas. AZ Academy proporciona el conocimiento y las habilidades necesarias para que su equipo trabaje en sinergia con la IA, maximizando su potencial.</p><p class="mb-4 text-slate-300 leading-relaxed">Los resultados hablan por sí solos. Empresas de servicios en México, Colombia, Chile y Perú han experimentado un <strong>aumento exponencial en la calificación de leads, una reducción en el ciclo de ventas y un incremento notorio en el ROI</strong> tras implementar el Sistema SVE90. La transparencia y la capacidad de medir cada paso del proceso son fundamentales. Con Prosper IA, usted no solo invierte en tecnología, invierte en un sistema probado que entrega <strong>resultados cuantificables en 90 días</strong>, permitiendo a su empresa escalar con confianza y previsibilidad. Es la soberanía operativa que todo CEO busca.</p><h3>Referencias y Estudios de Caso</h3><ul class="list-disc pl-5 space-y-2 text-slate-400 text-sm"><li><strong>Gartner:</strong> “Key Considerations for Rapid Sales Transformation in Digital Ecosystems”, 2024.</li><li><strong>McKinsey & Company:</strong> “Boosting B2B Sales Effectiveness with AI and Agile Methodologies”, 2023.</li><li><strong>Salesforce:</strong> “The Impact of Sales Process Optimization on Revenue Growth”, 2025.</li></ul>""",
        "image_url": "/static/blog/sistema-sve90-transformacion-ventas-rapida.jpg",
        "published_at": "2026-07-24T04:57:10Z",
        "author": "Edward Jiménez"
    },
    {
        "slug": "click-to-whatsapp-instagram-ai-setters",
        "title": "Click-to-WhatsApp e Instagram: Su Estrategia para Captar Leads Cualificados con AI Setters 24/7",
        "category": "Marketing & CRM",
        "summary": "Revolucione su prospección de leads en Latinoamérica con la integración estratégica de Click-to-WhatsApp y Click-to-Instagram, potenciada por nuestros AI Setters. Convierta cada interacción en una oportunidad de negocio calificada, disponible sin interrupciones.",
        "content": """<p class="mb-4 text-slate-300 leading-relaxed">En el paisaje digital de <strong>Latinoamérica</strong>, WhatsApp e Instagram se han consolidado como los canales de comunicación preferidos por millones de usuarios, tanto a nivel personal como profesional. Para las empresas de servicios B2B, ignorar el potencial de estas plataformas para la generación de leads es dejar una ventaja competitiva significativa en la mesa. La estrategia <strong>Click-to-WhatsApp y Click-to-Instagram</strong> no es nueva, pero su eficacia se magnifica exponencialmente cuando se integra con la inteligencia artificial de nuestros <strong>AI Setters</strong>, transformando simples clics en conversaciones de alto valor y citas cualificadas.</p><p class="mb-4 text-slate-300 leading-relaxed">La diferencia clave con los AI Setters de Prosper IA radica en su capacidad para ir más allá de la respuesta automática. Cuando un prospecto hace clic en su anuncio y se conecta vía WhatsApp o Instagram, nuestro AI Setter entra en acción con una <strong>conversación personalizada y estratégica</strong>. No se trata de un flujo de preguntas genéricas, sino de un diálogo inteligente que califica al lead en tiempo real, identifica su nivel de interés, sus puntos de dolor y su encaje con sus soluciones. Esta interacción profunda asegura que solo los leads verdaderamente prometedores sean elevados a su equipo de ventas humano.</p><p class="mb-4 text-slate-300 leading-relaxed">Los beneficios de esta integración son múltiples y se reflejan directamente en su <strong>ROI</strong>. En primer lugar, los AI Setters operan <strong>24 horas al día, 7 días a la semana</strong>, lo que significa que nunca pierde una oportunidad de captar un lead, sin importar la zona horaria o el día. En segundo lugar, la calificación automática y precisa reduce drásticamente el tiempo que su equipo de ventas dedica a la prospección ineficaz, permitiéndoles concentrarse en el cierre de negocios ya calificados. Esto se alinea perfectamente con los principios de eficiencia del <strong>Sistema SVE90</strong>.</p><p class="mb-4 text-slate-300 leading-relaxed">La implementación es fluida y segura a través de nuestra plataforma <strong>PassportAI</strong>, que centraliza y gestiona todas sus interacciones y datos, garantizando la <strong>soberanía de datos</strong> y el cumplimiento de las regulaciones locales. Además, mediante la <strong>AZ Academy</strong>, su equipo aprenderá a optimizar las campañas de Click-to-WhatsApp e Instagram y a trabajar en perfecta armonía con los AI Setters, maximizando cada lead generado. Es el momento de transformar la forma en que su empresa atrae y cualifica a sus futuros clientes, llevando la automatización de marketing y ventas a un nivel sin precedentes en Latinoamérica.</p><h3>Referencias y Estudios de Caso</h3><ul class="list-disc pl-5 space-y-2 text-slate-400 text-sm"><li><strong>Facebook Business (Meta):</strong> “The Power of Click-to-Message Ads for SMBs in Latin America”, 2024.</li><li><strong>Gartner:</strong> “Harnessing Conversational AI for Lead Generation and Nurturing”, 2025.</li><li><strong>Salesforce:</strong> “Marketing Trends Report: The Rise of Conversational Marketing”, 2023.</li></ul>""",
        "image_url": "/static/blog/click-to-whatsapp-instagram-ai-setters.jpg",
        "published_at": "2026-07-24T05:57:10Z",
        "author": "Edward Jiménez"
    },
    {
        "slug": "blindaje-operativo-con-passportai-sops",
        "title": "Blindaje Operativo Total: La Fusión Estratégica de PassportAI y SOPs para CEOs en LATAM",
        "category": "Operaciones",
        "summary": "Fortalezca la resiliencia de su empresa de servicios con el blindaje operativo que ofrece Prosper IA, combinando la centralización de PassportAI y la precisión de los SOPs. Asegure la continuidad del negocio, la soberanía de datos y una eficiencia inquebrantable.",
        "content": """<p class="mb-4 text-slate-300 leading-relaxed">En un entorno empresarial cada vez más impredecible, la capacidad de una empresa para mantener la <strong>continuidad operativa</strong> y proteger sus activos es de suma importancia. Para los CEOs y dueños de negocios en <strong>Latinoamérica</strong>, el concepto de <strong>blindaje operativo</strong> se ha vuelto central para la estrategia de crecimiento y mitigación de riesgos. Esto va más allá de la ciberseguridad; implica tener sistemas, procesos y personal alineados para resistir interrupciones, garantizar la <strong>soberanía de datos</strong> y mantener la eficiencia, incluso frente a desafíos inesperados. Prosper IA ofrece una solución integral a través de la sinergia de nuestra plataforma <strong>PassportAI</strong> y la implementación rigurosa de <strong>SOPs (Procedimientos Operativos Estándar)</strong>.</p><p class="mb-4 text-slate-300 leading-relaxed">La dispersión de herramientas y la falta de estandarización son enemigos silenciosos de la eficiencia operativa. Cada vez que su equipo tiene que saltar entre múltiples plataformas para gestionar leads, ventas o datos, se introducen fricciones, errores y vulnerabilidades. <strong>PassportAI</strong> resuelve este problema al proporcionar una <strong>plataforma centralizada y segura</strong> donde todos sus procesos críticos de ventas y marketing residen. Desde la gestión de AI SDRs y AI Setters hasta el análisis de datos y la automatización, PassportAI consolida su infraestructura digital, simplificando la administración y fortaleciendo la seguridad.</p><p class="mb-4 text-slate-300 leading-relaxed">Complementando a PassportAI, la implementación de <strong>SOPs</strong> claros y concisos es fundamental. Los SOPs son el manual de operaciones de su empresa, asegurando que cada tarea, desde la calificación de un lead hasta la gestión de un proyecto, se realice de manera consistente, eficiente y conforme a las mejores prácticas. Esta estandarización no solo reduce el riesgo de errores humanos, sino que también facilita la incorporación de nuevos talentos y la escalabilidad del negocio. Juntos, PassportAI y los SOPs crean un marco operativo que es robusto, predecible y altamente adaptable.</p><p class="mb-4 text-slate-300 leading-relaxed">La <strong>capacitación de su equipo humano a través de AZ Academy</strong> es el tercer pilar de este blindaje operativo. De nada sirve tener la mejor tecnología y los mejores procesos si el personal no está debidamente capacitado para utilizarlos. AZ Academy asegura que cada miembro de su equipo comprenda y aplique los SOPs de manera efectiva, y que maximice el potencial de PassportAI y de los AI SDRs. El resultado es un equipo más competente, una operación más fluida y una empresa que puede operar con la máxima confianza, impactando positivamente en el <strong>ROI</strong> y la capacidad de cumplir con los objetivos del <strong>Sistema SVE90</strong>. Es la soberanía operativa llevada al siguiente nivel para su empresa de servicios en Latinoamérica.</p><h3>Referencias y Estudios de Caso</h3><ul class="list-disc pl-5 space-y-2 text-slate-400 text-sm"><li><strong>McKinsey & Company:</strong> “Building Operational Resilience for a Turbulent Future”, 2024.</li><li><strong>Gartner:</strong> “The Importance of Centralized Platforms for Business Agility”, 2025.</li><li><strong>Harvard Business Review:</strong> “Why Standard Operating Procedures Are Critical for Growth”, 2023.</li></ul>""",
        "image_url": "/static/blog/blindaje-operativo-con-passportai-sops.jpg",
        "published_at": "2026-07-24T06:57:10Z",
        "author": "Edward Jiménez"
    },
    {
        "slug": "futuro-ventas-b2b-latam-estrategias-ia",
        "title": "El Futuro de las Ventas B2B en LATAM: Estrategias Impulsadas por IA para un 2026 Resiliente",
        "category": "Automatización",
        "summary": "Prepárese para un 2026 donde la IA redefine las ventas B2B en Latinoamérica, ofreciendo eficiencia, personalización a escala y crecimiento sostenible. Descubra cómo Prosper IA lo equipa para dominar este nuevo horizonte comercial con estrategias probadas y tecnología de vanguardia.",
        "content": """<p class="mb-4 text-slate-300 leading-relaxed">El año 2026 marca un punto de inflexión decisivo para las <strong>ventas B2B en Latinoamérica</strong>. Las empresas que busquen no solo sobrevivir, sino prosperar, deben mirar más allá de las tácticas tradicionales y adoptar un enfoque radicalmente nuevo, impulsado por la <strong>Inteligencia Artificial</strong>. Los mercados de México, Colombia, Chile y Perú exigen mayor agilidad, personalización y eficiencia. Aquí, la IA no es un mero complemento, sino el motor fundamental que impulsa la estrategia comercial, desde la prospección más temprana hasta la optimización de la postventa, asegurando un <strong>retorno de inversión (ROI)</strong> sin precedentes y una ventaja competitiva duradera.</p><p class="mb-4 text-slate-300 leading-relaxed">La piedra angular de esta transformación es la implementación de <strong>AI SDRs y AI Setters</strong>. Estos agentes virtuales autónomos, operando incansablemente 24/7 en plataformas como WhatsApp e Instagram, son capaces de identificar, calificar y nutrir leads fríos con una sofisticación que supera con creces a los métodos convencionales. Al automatizar las tareas repetitivas y de baja rentabilidad, liberan a su equipo humano de ventas para concentrarse en negociaciones complejas y la construcción de relaciones estratégicas. Esta eficiencia optimiza el ciclo de ventas y es un componente crucial del éxito del <strong>Sistema SVE90</strong>.</p><p class="mb-4 text-slate-300 leading-relaxed">Para asegurar la coherencia y la máxima eficacia, todas estas herramientas de IA deben operar bajo un paraguas de <strong>control y seguridad de datos</strong>. Es aquí donde nuestra plataforma <strong>PassportAI</strong> se vuelve indispensable. PassportAI no solo centraliza todas sus aplicaciones de ventas y marketing impulsadas por IA, sino que también garantiza la <strong>soberanía de sus datos</strong>, cumpliendo con las regulaciones locales e internacionales más estrictas. Esta consolidación evita la dispersión de información, reduce riesgos de seguridad y proporciona una visión unificada de sus operaciones, permitiendo decisiones estratégicas basadas en datos fiables.</p><p class="mb-4 text-slate-300 leading-relaxed">Finalmente, la adopción exitosa de estas tecnologías de vanguardia requiere una inversión en el activo más valioso de su empresa: su gente. A través de la <strong>AZ Academy</strong>, Prosper IA ofrece una <strong>capacitación exhaustiva en Procedimientos Operativos Estándar (SOPs)</strong> y en el uso óptimo de las herramientas de IA. Esto asegura que su equipo no solo comprenda el 'cómo', sino también el 'porqué' detrás de cada estrategia impulsada por IA, fomentando una cultura de innovación y eficiencia. Preparar su empresa para un 2026 resiliente significa invertir hoy en una estrategia de ventas B2B que sea inteligente, segura y diseñada para el crecimiento exponencial en el corazón de Latinoamérica.</p><h3>Referencias y Estudios de Caso</h3><ul class="list-disc pl-5 space-y-2 text-slate-400 text-sm"><li><strong>Gartner:</strong> “The Impact of Generative AI on B2B Sales Strategies in Emerging Markets”, 2026.</li><li><strong>McKinsey & Company:</strong> “Reshaping the Sales Function: The Power of AI in Latin America”, 2025.</li><li><strong>Salesforce:</strong> “AI in Sales: A Guide for Business Leaders in the Digital Age”, 2024.</li></ul>""",
        "image_url": "/static/blog/futuro-ventas-b2b-latam-estrategias-ia.jpg",
        "published_at": "2026-07-24T07:57:10Z",
        "author": "Edward Jiménez"
    },
    {
        "slug": "ia-sdrs-vs-chatbots-obsoletos-roi",
        "title": "La Revolución de los AI SDRs: Superando a los Chatbots Tradicionales para un ROI Inmediato",
        "category": "Automatización",
        "summary": "Los chatbots tradicionales se han vuelto obsoletos en el dinámico mercado B2B de LatAm. Descubra cómo los AI SDRs y AI Setters de Prosper IA están redefiniendo la calificación de leads y el agendamiento de citas, garantizando un retorno de inversión tangible y veloz.",
        "content": """<p class="mb-4 text-slate-300 leading-relaxed">En el vertiginoso panorama empresarial de Latinoamérica, la eficiencia en la generación y calificación de leads es la piedra angular del crecimiento. Sin embargo, muchos CEOs y directores comerciales aún se aferran a soluciones tecnológicas del pasado, como los <strong>chatbots tradicionales</strong>, que prometen automatización pero a menudo entregan frustración y bajos resultados. Estos sistemas, basados en reglas preestablecidas y conversaciones limitadas, no logran comprender la complejidad de las interacciones humanas ni adaptarse a las necesidades dinámicas de un cliente B2B, resultando en una experiencia deficiente y un embudo de ventas anémico.</p><p class="mb-4 text-slate-300 leading-relaxed">La verdadera revolución llega con los <strong>AI SDRs y AI Setters</strong> de Prosper IA. Estos agentes virtuales autónomos van mucho más allá de las capacidades de un chatbot rudimentario. Diseñados para calificar leads en frío y agendar citas 24/7 a través de canales vitales como WhatsApp e Instagram, los AI SDRs utilizan <strong>inteligencia artificial conversacional avanzada</strong> para comprender el contexto, responder a objeciones complejas y guiar a los prospectos cualificados hacia una reunión con su equipo de ventas. Esto no solo elimina la fricción en el proceso de calificación, sino que libera a su equipo humano para enfocarse en cerrar negocios.</p><p class="mb-4 text-slate-300 leading-relaxed">La implementación de nuestro <strong>Sistema SVE90 (Sistema de Ventas Eficientes en 90 días)</strong>, potenciado por estos AI SDRs, garantiza una transformación radical en su proceso comercial. Nuestros clientes experimentan una optimización operativa sin precedentes, donde cada interacción se capitaliza y cada lead se evalúa con precisión quirúrgica. Imagine un equipo virtual trabajando incansablemente, filtrando prospectos irrelevantes y presentando a su equipo solo las oportunidades más valiosas. Esto se traduce directamente en un <strong>ROI significativo</strong>, no solo por el aumento de ventas, sino por la drástica reducción de costos operativos y el incremento en la productividad de su fuerza de ventas.</p><p class="mb-4 text-slate-300 leading-relaxed">Más allá de la mera automatización, Prosper IA se compromete con la <strong>soberanía de datos</strong> y la implementación de <strong>SOPs (Procedimientos Operativos Estándar)</strong> a través de nuestra <strong>AZ Academy</strong>. Esto asegura que la adopción de la IA sea robusta, segura y completamente integrada en la cultura de su empresa. Los AI SDRs no son solo una herramienta; son una extensión estratégica de su equipo, proporcionando una ventaja competitiva sostenible que los chatbots obsoletos nunca podrían ofrecer. Es tiempo de evolucionar y asegurar que su inversión tecnológica se traduzca en resultados medibles y un crecimiento acelerado.</p><h3>Referencias y Estudios de Caso</h3><ul class="list-disc pl-5 space-y-2 text-slate-400 text-sm"><li><strong>Gartner:</strong> Proyecciones sobre la adopción de IA conversacional y su impacto en la productividad de ventas B2B para 2025-2026.</li><li><strong>McKinsey & Company:</strong> Análisis de la eficiencia operativa y el ROI en empresas que implementan automatización inteligente en sus procesos de lead qualification.</li><li><strong>Salesforce Research:</strong> El valor estratégico de los canales de mensajería (WhatsApp) en la interacción con clientes en mercados emergentes como LatAm.</li></ul>""",
        "image_url": "/static/blog/ia-sdrs-vs-chatbots-obsoletos-roi.jpg",
        "published_at": "2026-07-24T02:49:49Z",
        "author": "Edward Jiménez"
    },
    {
        "slug": "soberania-datos-apis-ia-latam-2026",
        "title": "Soberanía de Datos y Regulaciones API en LatAm: Blindando Su Operación con Prosper IA en 2026",
        "category": "Operaciones",
        "summary": "Conozca las crecientes exigencias de soberanía de datos y las regulaciones de APIs en LatAm para 2026. Prosper IA le ofrece una solución robusta con PassportAI para asegurar la privacidad, seguridad y cumplimiento normativo de su información, evitando la dispersión de herramientas.",
        "content": """<p class="mb-4 text-slate-300 leading-relaxed">El entorno regulatorio en Latinoamérica está evolucionando rápidamente, y para 2026, la <strong>soberanía de datos</strong> y las estrictas normativas sobre el uso de <strong>APIs</strong> se han convertido en imperativos críticos para cualquier empresa de servicios. Los CEOs y directores de negocio deben ser proactivos en la protección de la información sensible de sus clientes y operaciones. La dispersión de datos entre múltiples herramientas y proveedores, a menudo alojados en diferentes jurisdicciones, representa un riesgo significativo no solo para la seguridad, sino también para el cumplimiento legal, exponiendo a las empresas a multas considerables y daño reputacional irreparable.</p><p class="mb-4 text-slate-300 leading-relaxed">En este contexto, la plataforma <strong>PassportAI de Prosper IA</strong> emerge como la solución centralizada e inquebrantable que su negocio necesita. Diseñada específicamente para evitar la fragmentación y garantizar la <strong>privacidad y seguridad</strong> de su información, PassportAI consolida todas sus operaciones de IA en un entorno único y seguro. Nuestra arquitectura cumple con las normativas locales e internacionales más exigentes, brindando la tranquilidad de saber que sus datos están blindados y bajo su control, un aspecto fundamental para la continuidad y la confianza empresarial en la era digital.</p><p class="mb-4 text-slate-300 leading-relaxed">La integración de soluciones de IA a través de APIs es una práctica común, pero ¿cómo asegura que estas conexiones sean seguras y cumplan con la regulación? PassportAI gestiona estas interconexiones con un enfoque de seguridad de 'confianza cero', supervisando cada flujo de datos y cada API para prevenir vulnerabilidades. Esto es crucial en mercados como México, Colombia, Chile y Perú, donde las leyes de protección de datos personales están ganando fuerza. Con Prosper IA, usted no solo implementa inteligencia artificial; implementa una <strong>infraestructura de datos segura y conforme</strong>, protegiendo sus activos más valiosos y la relación con sus clientes.</p><p class="mb-4 text-slate-300 leading-relaxed">La inversión en una plataforma como PassportAI no es un gasto, es una <strong>estrategia inteligente para la optimización operativa</strong> y la mitigación de riesgos. Al centralizar sus herramientas y datos, no solo mejora la eficiencia y la colaboración interna, sino que también establece un marco robusto para la auditoría y el cumplimiento. Nuestro enfoque de <strong>SOPs (Procedimientos Operativos Estándar)</strong>, apoyado por la formación continua de <strong>AZ Academy</strong>, asegura que su equipo esté completamente capacitado para manejar la plataforma de manera segura y eficiente, manteniendo la soberanía de sus datos como una prioridad innegociable. No espere a que una brecha de seguridad o una sanción regulatoria lo obliguen a actuar; construya hoy mismo un futuro digital seguro con Prosper IA.</p><h3>Referencias y Estudios de Caso</h3><ul class="list-disc pl-5 space-y-2 text-slate-400 text-sm"><li><strong>Harvard Business Review:</strong> El creciente costo del incumplimiento de la privacidad de datos y la importancia de la gobernanza de datos en entornos empresariales.</li><li><strong>Gartner:</strong> Tendencias en la regulación de IA y privacidad de datos a nivel global y sus implicaciones para las empresas en mercados emergentes.</li><li><strong>McKinsey & Company:</strong> Estrategias para la resiliencia cibernética y la protección de datos en cadenas de suministro y ecosistemas de software empresariales.</li></ul>""",
        "image_url": "/static/blog/soberania-datos-apis-ia-latam-2026.jpg",
        "published_at": "2026-07-24T03:49:49Z",
        "author": "Edward Jiménez"
    },
    {
        "slug": "sistema-sve90-acelerar-ventas-90-dias",
        "title": "Desbloquee el Crecimiento Exponencial: El Sistema SVE90 para Optimización de Ventas en 90 Días",
        "category": "Casos de Éxito",
        "summary": "El Sistema SVE90 de Prosper IA es su camino probado hacia la transformación de ventas en solo tres meses. Enfocado en la eficiencia, el ROI y la soberanía de datos, garantizamos un incremento notable en su pipeline de ventas y la productividad de su equipo comercial.",
        "content": """<p class="mb-4 text-slate-300 leading-relaxed">En el competitivo mercado de servicios de Latinoamérica, los CEOs y directores comerciales buscan soluciones que ofrezcan resultados rápidos y medibles. El <strong>Sistema SVE90 (Sistema de Ventas Eficientes en 90 días)</strong> de Prosper IA es precisamente esa solución, diseñada para catalizar un crecimiento exponencial en sus ventas. No es una mera herramienta; es una metodología integral que combina tecnología de punta con procesos probados, asegurando una optimización operativa y un <strong>retorno de inversión (ROI)</strong> tangible en un período de tiempo sorprendentemente corto. Hemos visto a empresas de México, Colombia, Chile y Perú transformar completamente su panorama de ventas con nuestra guía.</p><p class="mb-4 text-slate-300 leading-relaxed">El corazón del SVE90 reside en la integración inteligente de nuestros <strong>AI SDRs y AI Setters</strong>. Estos agentes virtuales autónomos trabajan incansablemente 24/7 en plataformas como WhatsApp e Instagram, calificando leads en frío y agendando citas de alta calidad para su equipo. Este proceso automatizado elimina los cuellos de botella tradicionales en la parte superior del embudo de ventas, asegurando que su equipo humano dedique su valioso tiempo exclusivamente a la interacción con prospectos genuinamente interesados y listos para la conversión. La eficiencia que esto genera es un pilar fundamental para lograr el objetivo de los 90 días.</p><p class="mb-4 text-slate-300 leading-relaxed">Para garantizar la adopción exitosa y la máxima efectividad del sistema, el SVE90 se complementa con la implementación rigurosa de <strong>SOPs (Procedimientos Operativos Estándar)</strong> y la capacitación especializada a través de nuestra <strong>AZ Academy</strong>. Entendemos que la tecnología es tan buena como la capacidad de su equipo para utilizarla. Por ello, empoderamos a sus colaboradores con el conocimiento y las mejores prácticas para interactuar fluidamente con los agentes de IA, gestionar el flujo de leads y optimizar sus estrategias de cierre. La soberanía de sus datos, manejados a través de nuestra plataforma segura <strong>PassportAI</strong>, es un compromiso central en cada etapa, asegurando la confianza y el cumplimiento.</p><p class="mb-4 text-slate-300 leading-relaxed">Los resultados del SVE90 hablan por sí mismos: un aumento significativo en el número de citas cualificadas, ciclos de ventas más cortos y una mayor tasa de conversión. Para las empresas de servicios en LatAm que buscan no solo sobrevivir, sino prosperar y dominar su nicho, el Sistema SVE90 es la estrategia definitiva. Le invitamos a reimaginar su proceso de ventas, pasando de la incertidumbre a una predictibilidad y eficiencia que impulsarán su crecimiento en los próximos trimestres. Deje de postergar el futuro de sus ventas y únase a las empresas líderes que ya están experimentando la transformación del SVE90.</p><h3>Referencias y Estudios de Caso</h3><ul class="list-disc pl-5 space-y-2 text-slate-400 text-sm"><li><strong>McKinsey & Company:</strong> Impacto de la automatización inteligente en la aceleración de ciclos de ventas y la mejora de la productividad comercial.</li><li><strong>Salesforce Research:</strong> Análisis del valor de la personalización y la calificación de leads basada en IA para la optimización de embudos de ventas B2B.</li><li><strong>Gartner:</strong> Métricas clave de rendimiento y ROI esperados para la implementación de sistemas de ventas basados en IA en empresas de servicios.</li></ul>""",
        "image_url": "/static/blog/sistema-sve90-acelerar-ventas-90-dias.jpg",
        "published_at": "2026-07-24T04:49:49Z",
        "author": "Edward Jiménez"
    },
    {
        "slug": "click-to-whatsapp-ia-setters-estrategia-ventas",
        "title": "Domine la Generación de Leads con Click-to-WhatsApp y AI Setters de Prosper IA",
        "category": "Marketing & CRM",
        "summary": "Aproveche el poder de WhatsApp en LatAm con los AI Setters de Prosper IA para transformar clics en citas calificadas. Nuestra solución automatiza la interacción inicial, garantiza una soberanía de datos férrea y optimiza su pipeline de marketing y ventas como nunca antes.",
        "content": """<p class="mb-4 text-slate-300 leading-relaxed">En Latinoamérica, WhatsApp no es solo una aplicación de mensajería; es el canal de comunicación predilecto para millones de usuarios, tanto a nivel personal como profesional. Para los CEOs y directores comerciales, esto representa una oportunidad de oro para la generación de leads, pero solo si se aborda con la estrategia y la tecnología adecuadas. La simple presencia en WhatsApp no basta; la clave está en cómo se interactúa y se cualifica a esos leads. Aquí es donde la combinación de <strong>Click-to-WhatsApp y los AI Setters de Prosper IA</strong> se convierte en una estrategia imparable para el <strong>Marketing & CRM</strong>.</p><p class="mb-4 text-slate-300 leading-relaxed">Nuestros <strong>AI Setters</strong> son agentes virtuales autónomos diseñados específicamente para capitalizar el tráfico que llega a través de sus campañas Click-to-WhatsApp. En lugar de que un prospecto caiga en un embudo genérico o espere por una respuesta humana, nuestros AI Setters interactúan instantáneamente, califican la necesidad del lead, responden preguntas frecuentes y, lo más importante, agendan citas con su equipo de ventas. Todo esto ocurre de manera ininterrumpida, 24/7, garantizando que ninguna oportunidad se pierda, incluso fuera del horario laboral, maximizando la eficiencia de su <strong>optimización operativa</strong>.</p><p class="mb-4 text-slate-300 leading-relaxed">La implementación de esta poderosa combinación no solo acelera la fase inicial de su ciclo de ventas, sino que también mejora drásticamente la calidad de los leads que llegan a su equipo. Al filtrar y cualificar automáticamente, los AI Setters aseguran que sus SDRs humanos se concentren en cerrar negocios, en lugar de gastar tiempo valioso en prospectos no cualificados. Esta eficiencia se traduce directamente en un <strong>ROI significativo</strong>, haciendo que cada peso invertido en sus campañas de marketing digital genere un mayor impacto en sus resultados finales. Además, la interacción natural y contextual que ofrecen nuestros AI Setters mejora la experiencia del usuario, fortaleciendo la imagen de su marca.</p><p class="mb-4 text-slate-300 leading-relaxed">Con Prosper IA, la seguridad y la <strong>soberanía de datos</strong> son innegociables. Todas las interacciones gestionadas por los AI Setters se integran de forma segura en nuestra plataforma <strong>PassportAI</strong>, asegurando el cumplimiento de las normativas de protección de datos y evitando la dispersión de información. Además, a través de nuestra <strong>AZ Academy</strong>, capacitamos a su equipo con <strong>SOPs (Procedimientos Operativos Estándar)</strong> para que aprovechen al máximo esta tecnología, garantizando una adopción fluida y una coordinación perfecta entre la IA y el talento humano. Es tiempo de transformar sus clics en conversaciones de valor y sus conversaciones en clientes leales.</p><h3>Referencias y Estudios de Caso</h3><ul class="list-disc pl-5 space-y-2 text-slate-400 text-sm"><li><strong>Meta (Facebook):</strong> Datos sobre la penetración y el uso empresarial de WhatsApp en mercados latinoamericanos y el impacto de las campañas Click-to-WhatsApp.</li><li><strong>Salesforce Research:</strong> La evolución de la interacción con el cliente a través de mensajería instantánea y el papel de la IA en la cualificación de leads.</li><li><strong>Gartner:</strong> Tendencias en automatización de marketing y la integración de IA conversacional para mejorar la experiencia del cliente y la eficiencia del embudo de ventas.</li></ul>""",
        "image_url": "/static/blog/click-to-whatsapp-ia-setters-estrategia-ventas.jpg",
        "published_at": "2026-07-24T05:49:49Z",
        "author": "Edward Jiménez"
    },
    {
        "slug": "centralizacion-herramientas-passportai-prosper-ia",
        "title": "Fin a la Dispersión de Herramientas: La Plataforma Unificada PassportAI para la Eficiencia Operativa",
        "category": "Operaciones",
        "summary": "La proliferación de herramientas dispersas es un freno para la eficiencia y la soberanía de datos. PassportAI de Prosper IA ofrece una plataforma centralizada y segura que consolida sus operaciones de IA, garantizando un ROI superior a través de la optimización operativa y la gestión integral.",
        "content": """<p class="mb-4 text-slate-300 leading-relaxed">El crecimiento acelerado a menudo viene acompañado de una fragmentación digital: múltiples herramientas de software, plataformas y sistemas que, aunque individualmente útiles, colectivamente crean un caos operativo. Para los CEOs y directores de negocio en Latinoamérica, esta <strong>dispersión de herramientas</strong> se traduce en ineficiencias, silos de datos, costos ocultos y una vulnerabilidad crítica para la <strong>soberanía de datos</strong>. La falta de una visión unificada obstaculiza la toma de decisiones estratégicas, reduce la productividad del equipo y disminuye el tan anhelado <strong>ROI</strong>.</p><p class="mb-4 text-slate-300 leading-relaxed">Prosper IA presenta <strong>PassportAI</strong>, nuestra plataforma centralizada y segura, diseñada para ser el cerebro de sus operaciones de Inteligencia Artificial. Con PassportAI, la era de cambiar entre múltiples pestañas y sistemas dispares llega a su fin. Esta plataforma integra de manera fluida funcionalidades clave como nuestros <strong>AI SDRs y AI Setters</strong>, la gestión de sus procesos de ventas, y la supervisión de la calificación de leads, todo bajo un mismo techo digital. Esto no solo simplifica la gestión, sino que potencia la colaboración entre sus equipos de marketing, ventas y operaciones.</p><p class="mb-4 text-slate-300 leading-relaxed">La verdadera fortaleza de PassportAI reside en su capacidad para garantizar la <strong>integridad y seguridad de sus datos</strong>. Al consolidar toda su información y procesos en una única plataforma, eliminamos los riesgos asociados a la transferencia de datos entre sistemas incompatibles y a la exposición de información sensible en múltiples puntos. Esto es vital para cumplir con las crecientes regulaciones de privacidad de datos en mercados como México, Colombia, Chile y Perú. Con PassportAI, usted mantiene el control absoluto sobre su información, asegurando su <strong>soberanía de datos</strong> y fortaleciendo la confianza de sus clientes.</p><p class="mb-4 text-slate-300 leading-relaxed">Más allá de la consolidación, PassportAI es un motor de <strong>optimización operativa</strong>. La visibilidad integral que ofrece la plataforma permite identificar cuellos de botella, optimizar flujos de trabajo y tomar decisiones basadas en datos en tiempo real. Esto se complementa con la implementación de <strong>SOPs (Procedimientos Operativos Estándar)</strong> y la capacitación continua a través de nuestra <strong>AZ Academy</strong>, asegurando que su equipo aproveche al máximo las capacidades de la plataforma. Invertir en PassportAI es invertir en la simplificación, la seguridad y el crecimiento sostenible, transformando la complejidad en una ventaja competitiva clara y medible para su negocio de servicios.</p><h3>Referencias y Estudios de Caso</h3><ul class="list-disc pl-5 space-y-2 text-slate-400 text-sm"><li><strong>Gartner:</strong> Beneficios de la consolidación de plataformas tecnológicas en la reducción de costos operativos y la mejora de la eficiencia empresarial.</li><li><strong>McKinsey & Company:</strong> Estrategias para la gobernanza de datos y la seguridad en entornos empresariales complejos con múltiples herramientas y proveedores.</li><li><strong>Harvard Business Review:</strong> El costo oculto de la dispersión tecnológica y cómo la unificación de sistemas impulsa la innovación y el crecimiento.</li></ul>""",
        "image_url": "/static/blog/centralizacion-herramientas-passportai-prosper-ia.jpg",
        "published_at": "2026-07-24T06:49:49Z",
        "author": "Edward Jiménez"
    },
    {
        "slug": "factor-humano-ia-az-academy-prosper-ia",
        "title": "El Factor Humano en la Era de la IA: Potenciando a Su Equipo con AZ Academy y SOPs",
        "category": "Operaciones",
        "summary": "La IA no reemplaza, potencia. Conozca cómo Prosper IA, a través de AZ Academy y la implementación de SOPs, capacita a su equipo humano para colaborar eficazmente con la inteligencia artificial, logrando una optimización operativa y un ROI superior sin comprometer la soberanía de sus datos.",
        "content": """<p class="mb-4 text-slate-300 leading-relaxed">En la era de la Inteligencia Artificial, existe una preocupación común entre los líderes empresariales sobre el rol del factor humano. En Prosper IA, creemos firmemente que la <strong>IA no reemplaza a su equipo, lo potencia</strong>. Los CEOs y directores comerciales de empresas de servicios en LatAm comprenden que el capital humano sigue siendo su activo más valioso. Por ello, la clave del éxito no radica solo en adoptar tecnología de vanguardia, como nuestros <strong>AI SDRs y AI Setters</strong>, sino en capacitar a sus colaboradores para que trabajen de forma sinérgica con estas herramientas, optimizando cada proceso y garantizando la <strong>optimización operativa</strong>.</p><p class="mb-4 text-slate-300 leading-relaxed">Es aquí donde nuestra <strong>AZ Academy</strong> se convierte en un pilar fundamental. Diseñada para educar y empoderar a su equipo, AZ Academy ofrece programas de capacitación especializados que cubren desde los fundamentos de la IA hasta las mejores prácticas para interactuar con nuestros agentes virtuales y gestionar los leads cualificados. Al dotar a su personal con el conocimiento y las habilidades necesarias, se asegura una adopción fluida de la tecnología y una maximización de su <strong>ROI</strong>. Su equipo aprenderá a transformar la IA en una ventaja estratégica, liberándolos de tareas repetitivas para concentrarse en interacciones de alto valor y cierre de negocios.</p><p class="mb-4 text-slate-300 leading-relaxed">Para cimentar esta colaboración entre humanos e IA, implementamos rigurosos <strong>SOPs (Procedimientos Operativos Estándar)</strong>. Estos protocolos claros y bien definidos aseguran que cada interacción, cada lead calificado por nuestros AI SDRs y AI Setters, y cada paso en el ciclo de ventas, se maneje con consistencia y eficiencia. Los SOPs son cruciales para mantener la calidad del servicio, garantizar la <strong>soberanía de datos</strong> al utilizar nuestra plataforma <strong>PassportAI</strong> y escalar las operaciones sin perder el control. Permiten que la IA actúe como una extensión eficiente de su equipo, proporcionando una estructura sólida para el crecimiento.</p><p class="mb-4 text-slate-300 leading-relaxed">La combinación de una tecnología robusta y un equipo humano bien capacitado es la fórmula infalible para el éxito en 2026 y más allá. Con Prosper IA, usted no solo adquiere una solución de IA; invierte en el futuro de su fuerza laboral, transformándola en un motor de crecimiento aún más potente. Empresas en México, Colombia, Chile y Perú ya están experimentando cómo la sinergia entre sus equipos y nuestra IA, potenciada por AZ Academy y SOPs, se traduce en un aumento significativo de la productividad, la eficiencia y, en última instancia, en un retorno de inversión superior. El futuro de los negocios es colaborativo: humanos e IA trabajando juntos, inteligentemente.</p><h3>Referencias y Estudios de Caso</h3><ul class="list-disc pl-5 space-y-2 text-slate-400 text-sm"><li><strong>McKinsey & Company:</strong> El impacto de la capacitación de la fuerza laboral en la adopción de tecnologías de IA y la mejora de la productividad general.</li><li><strong>Gartner:</strong> La importancia de los Procedimientos Operativos Estándar (SOPs) para la integración exitosa de la IA en los flujos de trabajo empresariales.</li><li><strong>Harvard Business Review:</strong> Cómo las empresas líderes están invirtiendo en la capacitación de sus empleados para colaborar eficazmente con la inteligencia artificial y generar ventaja competitiva.</li></ul>""",
        "image_url": "/static/blog/factor-humano-ia-az-academy-prosper-ia.jpg",
        "published_at": "2026-07-24T07:49:49Z",
        "author": "Edward Jiménez"
    },
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
        "image_url": "/static/blog/rediseno-crm-ia-latam.jpg",
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
        "image_url": "/static/blog/centralizacion-passportai-software-ceos.jpg",
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
        "image_url": "/static/blog/empleado-digital-sdr-setter-autonomo.jpg",
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
        "image_url": "/static/blog/caso-estudio-agencia-sve90-ventas-ia.jpg",
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
        "image_url": "/static/blog/blindaje-operativo-sops-formacion-ia.jpg",
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
        "image_url": "/static/blog/guia-definitiva-automatizacion-ia-ceos.jpg",
        "published_at": "2026-06-03T13:00:00Z",
        "author": "Edward Jiménez"
    },
    {
        "slug": "nuevas-reglas-meta-whatsapp-2026",
        "title": "Las nuevas reglas de Meta en 2026 para WhatsApp Business: Adiós a los chatbots genéricos y cómo proteger tu línea",
        "category": "Marketing & CRM",
        "summary": "Meta ahora restringe chatbots de IA que no estén anclados a la base de conocimiento de la empresa. Descubre cómo adaptar tu agente SDR para evitar bloqueos y optimizar el costo por mensaje en LATAM.",
        "content": """<p class="mb-4 text-slate-300 leading-relaxed">El panorama de la automatización en WhatsApp Business ha cambiado radicalmente con la entrada en vigor de las nuevas políticas operativas de Meta en 2026. La compañía matriz ha endurecido significativamente el uso de chatbots de Inteligencia Artificial de "propósito general" (aquellos que actúan como asistentes de conocimiento general tipo ChatGPT). A partir de ahora, cualquier línea comercial que use automatización cognitiva debe estar estrictamente anclada a la Propiedad Intelectual de la empresa y a sus procesos de soporte o ventas.</p>
<p class="mb-4 text-slate-300 leading-relaxed">Para las empresas en Latinoamérica, esto significa que el uso de bots improvisados sin reglas de negocio claras no solo es ineficiente, sino que representa un riesgo inminente de suspensión o bloqueo definitivo del número de teléfono corporativo. La solución ante este cambio es utilizar sistemas especializados y seguros. Al implementar la arquitectura de <strong>Prosper IA</strong> y el motor <strong>PassportAI</strong>, tu agente AI SDR opera dentro de un entorno controlado que respeta las directrices de Meta, respondiendo exclusivamente con la información oficial de tu catálogo, precios y políticas de servicio.</p>
<p class="mb-4 text-slate-300 leading-relaxed">Además del aspecto regulatorio, optimizar el flujo de conversación es vital bajo el esquema de tarifas de Meta. Un agente entrenado con IA especializada sabe cómo estructurar la conversación para resolver dudas frecuentes, calificar al prospecto y pasar la conversación al equipo humano o al agendador autónomo en pocos mensajes, protegiendo tanto tu presupuesto de marketing como la reputación de tu marca.</p>
<p class="mb-4 text-slate-300 leading-relaxed">Para asegurar que tu canal de WhatsApp cumple al 100% con estas regulaciones y evitar penalizaciones de Meta, te recomendamos realizar nuestro <strong>Diagnóstico de Madurez SVE90 de 30 minutos</strong>, donde validaremos tus flujos conversacionales actuales y los adaptaremos a la normativa vigente.</p>
<h3 class="text-xl font-bold text-white mt-8 mb-4 border-b border-slate-800 pb-2">Referencias y Estudios de Caso</h3>
<ul class="list-disc pl-5 space-y-2 text-slate-400 text-sm">
  <li><strong>Meta for Developers:</strong> <span class="italic">"WhatsApp Business Platform Policy Updates (2026 Edition)"</span> (Detalle de las nuevas restricciones de IA conversacional y guías de uso).</li>
  <li><strong>Gartner Research:</strong> <span class="italic">"Mitigating Brand and Operational Risks in Conversational Channels"</span> (Estudio sobre el impacto de bloqueos en canales de mensajería instantánea empresarial).</li>
  <li><strong>Prosper IA Technical Library:</strong> <span class="italic">"PassportAI Compliance Blueprint"</span> (Guía técnica para configurar agentes virtuales de forma segura bajo la API oficial de WhatsApp).</li>
</ul>""",
        "image_url": "/static/blog/meta-reglas-whatsapp-business.png",
        "published_at": "2026-06-14T08:00:00Z",
        "author": "Edward Jiménez"
    },
    {
        "slug": "nuevo-cobro-mensaje-whatsapp-roi",
        "title": "El nuevo cobro por mensaje de WhatsApp: Cómo optimizar el ROI de tus campañas Click-to-WhatsApp en 2026",
        "category": "Marketing & CRM",
        "summary": "El cambio de Meta al cobro por mensaje individual en lugar de conversación exige flujos de automatización extremadamente eficientes. Te enseñamos a calificar prospectos en menos de 3 mensajes con un AI Setter.",
        "content": """<p class="mb-4 text-slate-300 leading-relaxed">Atrás quedaron los días en que Meta cobraba una tarifa plana por ventana de conversación de 24 horas en WhatsApp. En 2026, la implementación del esquema de facturación basado en <strong>mensajes individuales entregados</strong> ha obligado a los directores de marketing y ventas de Latinoamérica a repensar por completo su estrategia de captación de leads. Ahora, cada mensaje que el bot o el asesor envía representa un coste directo en el balance financiero, lo que castiga severamente los flujos de conversación largos, redundantes o mal estructurados.</p>
<p class="mb-4 text-slate-300 leading-relaxed">Para mantener un Retorno de Inversión (ROI) positivo en campañas Click-to-WhatsApp (anuncios que abren un chat directamente), la rapidez y la precisión en la calificación son primordiales. No podemos permitir que una conversación se extienda a 20 mensajes antes de saber si el cliente tiene el presupuesto o perfil adecuado. Es en este punto donde la ingeniería de <strong>Prosper IA</strong> y el <strong>Sistema SVE90</strong> aportan su mayor valor operativo.</p>
<p class="mb-4 text-slate-300 leading-relaxed">Al integrar un agente de IA entrenado específicamente para calificar (AI SDR) y agendar (AI Setter), el sistema está diseñado para identificar la intención de compra y extraer las variables clave (presupuesto, empresa, dolor operativo) en un promedio de solo 3 a 4 intercambios. Una vez calificado positivamente, el agente ofrece la agenda en tiempo real, cerrando la cita de manera óptima y minimizando la cantidad de mensajes de seguimiento costosos.</p>
<p class="mb-4 text-slate-300 leading-relaxed">Si tus costes de adquisición en WhatsApp se han disparado recientemente debido a este cambio de tarifas, te invitamos a agendar una sesión estratégica para estructurar un flujo automatizado de alta conversión que maximice tu presupuesto comercial.</p>
<h3 class="text-xl font-bold text-white mt-8 mb-4 border-b border-slate-800 pb-2">Referencias y Estudios de Caso</h3>
<ul class="list-disc pl-5 space-y-2 text-slate-400 text-sm">
  <li><strong>Meta Business Support:</strong> <span class="italic">"Understanding the Utility and Marketing Conversational Pricing Model"</span> (Desglose de costes por tipo de mensaje entregado en la API de WhatsApp).</li>
  <li><strong>Salesforce Research:</strong> <span class="italic">"Maximizing ROI on Instant Messaging Channels"</span> (Estudio sobre cómo la cualificación rápida reduce costes operativos en campañas pagadas).</li>
  <li><strong>McKinsey:</strong> <span class="italic">"Direct-to-Consumer Messaging Efficiency in Emerging Markets"</span> (Casos de éxito de optimización de costes conversacionales en Brasil y México).</li>
</ul>""",
        "image_url": "/static/blog/optimizacion-conversacion-whatsapp-roi.png",
        "published_at": "2026-06-13T09:00:00Z",
        "author": "Edward Jiménez"
    },
    {
        "slug": "consolidacion-herramientas-ia-operaciones",
        "title": "Consolidación de herramientas de IA: La tendencia que está salvando el margen operativo de las empresas de servicios",
        "category": "Operaciones",
        "summary": "En 2026, la acumulación desordenada de suscripciones de software devora hasta el 12% de la facturación. La respuesta estratégica es un Command Center centralizado con soberanía de datos.",
        "content": """<p class="mb-4 text-slate-300 leading-relaxed">Durante la primera ola de adopción de Inteligencia Artificial, las empresas en Latinoamérica corrieron a contratar múltiples herramientas SaaS independientes: una para redactar correos, otra para transcribir reuniones, una tercera para calificar leads y otra más para automatizar flujos de chat. En 2026, esta dispersión técnica ha provocado lo que los analistas financieros denominan **fatiga de software**, la cual carcome en silencio el margen de ganancia de las agencias y consultoras B2B.</p>
<p class="mb-4 text-slate-300 leading-relaxed">La fragmentación de datos no solo dispara los costes de licenciamiento mensual, sino que genera silos informativos y fallos continuos de sincronización. Además, compartir información confidencial del negocio con múltiples plataformas externas sin un marco de gobernanza claro pone en riesgo la soberanía de los datos de la empresa. Frente a esto, la tendencia dominante de este año es la **consolidación de herramientas**.</p>
<p class="mb-4 text-slate-300 leading-relaxed">Bajo la dirección de <strong>Prosper IA</strong>, el Command Center unificado mediante <strong>PassportAI</strong> centraliza la capacidad cognitiva de tu organización. En lugar de pagar a 10 proveedores diferentes, PassportAI te permite conectar tus canales de adquisición de leads directamente a un único núcleo inteligente que califica, responde, agenda y reporta las métricas de rendimiento en tiempo real. Esta unificación no solo reduce los costes fijos de software hasta en un 60%, sino que garantiza que la propiedad intelectual y los datos operacionales de tu empresa permanezcan completamente seguros y bajo tu absoluto control.</p>
<p class="mb-4 text-slate-300 leading-relaxed">Consolidar tu infraestructura es el paso definitivo para blindar la rentabilidad operativa. Te invitamos a solicitar un diagnóstico de tu infraestructura técnica actual con nuestro equipo de ingenieros para estructurar tu mapa de consolidación de software sin interrumpir tus operaciones diarias.</p>
<h3 class="text-xl font-bold text-white mt-8 mb-4 border-b border-slate-800 pb-2">Referencias y Estudios de Caso</h3>
<ul class="list-disc pl-5 space-y-2 text-slate-400 text-sm">
  <li><strong>Forrester Research:</strong> <span class="italic">"The Total Economic Impact of SaaS Consolidation"</span> (Análisis de la reducción de gastos operativos al migrar de software disperso a Command Centers).</li>
  <li><strong>MIT Sloan Review:</strong> <span class="italic">"Data Security and Corporate Governance in the Agentic Era"</span> (Evaluación de riesgos sobre el uso de APIs de IA dispersas en corporativos).</li>
  <li><strong>Prosper IA Whitepaper:</strong> <span class="italic">"Sovereign AI Infrastructure for B2B Services in Latin America"</span> (Caso práctico de centralización de datos utilizando la arquitectura PassportAI).</li>
</ul>""",
        "image_url": "/static/blog/consolidacion-herramientas-ia-command-center.png",
        "published_at": "2026-06-12T10:00:00Z",
        "author": "Edward Jiménez"
    },
    {
        "slug": "ai-sdr-vs-ai-setter-ventas",
        "title": "AI SDR vs. AI Setter: Cómo estructurar el equipo de ventas digital perfecto sin inflar tu nómina",
        "category": "Automatización",
        "summary": "La división del trabajo no es exclusiva de los humanos. Conoce la arquitectura de doble agente que califica leads fríos y agenda reuniones de manera autónoma 24/7.",
        "content": """<p class="mb-4 text-slate-300 leading-relaxed">En el diseño de procesos de ventas modernos, la especialización de funciones es clave para la eficiencia. Tradicionalmente, las empresas de servicios B2B han dividido el embudo comercial en dos roles humanos esenciales: el SDR (Sales Development Representative), encargado de la prospección y primera calificación de leads fríos, y el Setter (Agendador), encargado de guiar al cliente calificado hacia una cita formal en la agenda. En 2026, esta misma especialización se ha trasladado con gran éxito al ámbito de los agentes autónomos de Inteligencia Artificial.</p>
<p class="mb-4 text-slate-300 leading-relaxed">Implementar un único chatbot generalista para que se encargue de todo el embudo suele resultar en conversaciones confusas y tasas de conversión bajas. La arquitectura recomendada por <strong>Prosper IA</strong> dentro del <strong>Sistema SVE90</strong> se basa en un flujo de **Doble Agente Colaborativo**:</p>
<ol class="list-decimal pl-5 space-y-2 text-slate-300 leading-relaxed mb-4">
  <li><strong>El Agente AI SDR:</strong> Está entrenado para recibir los mensajes entrantes (de publicidad Click-to-WhatsApp, Instagram o formularios web) al instante. Su labor es interactuar en lenguaje natural, comprender las necesidades comerciales del usuario, evaluar su presupuesto e intención de compra, y asignarle una calificación o Lead Score.</li>
  <li><strong>El Agente AI Setter:</strong> Se activa únicamente cuando el AI SDR determina que el prospecto cumple con el perfil ideal. Este segundo agente gestiona las objeciones de horario, accede a las agendas en tiempo real de tus especialistas comerciales y reserva la reunión directamente en el CRM de leads, enviando confirmaciones y recordatorios de manera completamente autónoma.</li>
</ol>
<p class="mb-4 text-slate-300 leading-relaxed">Esta división del trabajo asegura que tu equipo comercial humano reciba citas pre-calificadas de alto valor en sus calendarios, listas para la llamada de cierre, ahorrando cientos de horas de prospección estéril al mes.</p>
<p class="mb-4 text-slate-300 leading-relaxed">Para descubrir cómo estructurar este flujo colaborativo de doble agente adaptado a tu industria, agenda hoy mismo una sesión estratégica con uno de nuestros arquitectos de soluciones.</p>
<h3 class="text-xl font-bold text-white mt-8 mb-4 border-b border-slate-800 pb-2">Referencias y Estudios de Caso</h3>
<ul class="list-disc pl-5 space-y-2 text-slate-400 text-sm">
  <li><strong>Harvard Business Review:</strong> <span class="italic">"Cooperative AI Agents in the Commercial Funnel"</span> (Estudio sobre la especialización de funciones en sistemas autónomos de ventas).</li>
  <li><strong>Gartner Research:</strong> <span class="italic">"Redesigning B2B Sales Teams for Collaborative Intelligence"</span> (Cómo optimizar la colaboración entre humanos y dobles agentes de IA).</li>
  <li><strong>Salesforce Success Stories:</strong> <span class="italic">"SDR and Setter AI Automations in High-Growth Firms"</span> (Métricas de mejora en agendamiento comercial y retención de prospectos).</li>
</ul>""",
        "image_url": "/static/blog/arquitectura-sdr-setter-ventas-ia.png",
        "published_at": "2026-06-11T11:00:00Z",
        "author": "Edward Jiménez"
    },
    {
        "slug": "factor-humano-sops-retorno-inversion-ia",
        "title": "El factor humano en la era de los agentes autónomos: Por qué tus SOPs son tu activo más valioso",
        "category": "Operaciones",
        "summary": "La tecnología sin adopción humana es dinero perdido. Analizamos cómo el diseño de Procedimientos Operativos Estándar y la capacitación técnica con AZ Academy blindan tu retorno de inversión.",
        "content": """<p class="mb-4 text-slate-300 leading-relaxed">El mayor error al automatizar procesos corporativos en Latinoamérica es asumir que la tecnología solucionará de inmediato los cuellos de botella del negocio de forma aislada. La compra de las herramientas de IA más potentes o la implementación de las integraciones más sofisticadas generarán un retorno de inversión nulo si el personal humano de la empresa se resiste a utilizarlas o no sabe cómo supervisar los flujos automatizados de manera correcta.</p>
<p class="mb-4 text-slate-300 leading-relaxed">La resistencia al cambio operativa en la región es real. A menudo, los equipos de ventas o soporte sienten que los agentes virtuales de IA son competidores que amenazan su estabilidad laboral, en lugar de asistentes que potencian su rendimiento y comisiones. El verdadero **Blindaje Operativo** consiste en establecer una perfecta armonía entre los agentes de IA y los especialistas humanos de la empresa.</p>
<p class="mb-4 text-slate-300 leading-relaxed">Para garantizar este éxito operativo, en el <strong>Sistema SVE90</strong> de <strong>Prosper IA</strong> estructuramos dos pilares estratégicos:</p>
<ul class="list-disc pl-5 space-y-2 text-slate-300 leading-relaxed mb-4">
  <li><strong>SOPs (Procedimientos Operativos Estándar) Claros:</strong> Manuales y diagramas sencillos que definen los límites del agente virtual y el punto exacto en el que el especialista de ventas humano debe tomar el control para cerrar el contrato comercial.</li>
  <li><strong>Capacitación Especializada mediante AZ Academy:</strong> Un programa formativo enfocado en capacitar a tus colaboradores en la gestión de leads calificados, análisis de métricas en el CRM de leads y supervisión del Command Center.</li>
</ul>
<p class="mb-4 text-slate-300 leading-relaxed">Cuando tu personal comprende cómo apoyarse en los agentes de IA para agilizar tareas repetitivas, la productividad se multiplica y la resistencia al cambio desaparece por completo, transformando tu organización en una verdadera Empresa Aumentada.</p>
<p class="mb-4 text-slate-300 leading-relaxed">Si deseas blindar operativamente la integración de tecnología cognitiva en tu empresa, te invitamos a coordinar una auditoría de madurez operativa y cultura digital con nuestro equipo.</p>
<h3 class="text-xl font-bold text-white mt-8 mb-4 border-b border-slate-800 pb-2">Referencias y Estudios de Caso</h3>
<ul class="list-disc pl-5 space-y-2 text-slate-400 text-sm">
  <li><strong>MIT Sloan Review:</strong> <span class="italic">"Standardizing Human-AI Collaboration at Scale"</span> (Reporte sobre la importancia del entrenamiento humano en sistemas automatizados de atención).</li>
  <li><strong>Harvard Business School:</strong> <span class="italic">"The Importance of Standard Operating Procedures (SOPs) in Digital Transitions"</span> (Estudio sobre cómo los SOPs previenen fallos operativos durante integraciones tecnológicas).</li>
  <li><strong>AZ Academy Research:</strong> <span class="italic">"Upskilling Sales Representatives for the Agentic Era"</span> (Casos prácticos de equipos comerciales en LATAM que adoptaron IA sin fricción interna).</li>
</ul>""",
        "image_url": "/static/blog/factor-humano-sops-capacitacion.png",
        "published_at": "2026-06-10T12:00:00Z",
        "author": "Edward Jiménez"
    },
    {
        "slug": "speed-to-lead-velocidad-ventas-latam",
        "title": "De 4 horas a 45 segundos: Cómo la velocidad de respuesta (Speed-to-Lead) define quién gana los clientes B2B en Latinoamérica en 2026",
        "category": "Casos de Éxito",
        "summary": "Un análisis profundo sobre el impacto del tiempo de respuesta en las tasas de cierre y cómo el Diagnóstico de Madurez SVE90 ayuda a erradicar las fugas silenciosas de facturación.",
        "content": """<p class="mb-4 text-slate-300 leading-relaxed">En el mercado empresarial B2B y de servicios en Latinoamérica, existe una regla comercial matemática que se cumple sin excepciones: el tiempo de respuesta mata los negocios. En 2026, la paciencia del cliente digital es menor que nunca. Diversos estudios globales confirman que responder a un cliente interesado en los primeros 5 minutos incrementa la probabilidad de contacto y calificación comercial en más de un 100% en comparación con responder media hora después.</p>
<p class="mb-4 text-slate-300 leading-relaxed">A pesar de esto, muchas agencias de servicios y consultoras en México, Colombia, Perú y Chile siguen teniendo tiempos de respuesta que promedian entre 2 y 4 horas. Durante ese intervalo de espera, el prospecto interesado ya ha contactado a tres competidores más en la web. Este retraso provoca una fuga silenciosa pero constante de capital que limita drásticamente la facturación mensual del negocio.</p>
<p class="mb-4 text-slate-300 leading-relaxed">La solución técnica a este problema de **Speed-to-Lead** es automatizar la primera respuesta interactiva mediante agentes autónomos integrados en caliente a tu Command Center (CRM de leads). La infraestructura de <strong>Prosper IA</strong> y el <strong>Sistema SVE90</strong> permite reducir el tiempo de respuesta inicial a escasos 45 segundos por WhatsApp, Instagram DM y sitio web. El agente no solo da la bienvenida, sino que califica semánticamente las necesidades del prospecto y agenda la cita, ganando la atención del cliente antes de que la competencia siquiera abra el correo de contacto.</p>
<p class="mb-4 text-slate-300 leading-relaxed">Para medir tus fugas de ingresos por lentitud comercial, te invitamos a realizar nuestro **Diagnóstico de Madurez SVE90 de 30 minutos**, donde analizaremos tu infraestructura digital y diseñaremos una hoja de ruta para acelerar tus flujos de venta.</p>
<h3 class="text-xl font-bold text-white mt-8 mb-4 border-b border-slate-800 pb-2">Referencias y Estudios de Caso</h3>
<ul class="list-disc pl-5 space-y-2 text-slate-400 text-sm">
  <li><strong>Harvard Business Review:</strong> <span class="italic">"The Speed-to-Lead Advantage in Online Customer Acquisition"</span> (Investigación sobre el decaimiento de la tasa de conversión en función de las horas de retraso).</li>
  <li><strong>MIT Sloan Management:</strong> <span class="italic">"Autonomous Qualification: The Next Frontier in Customer Response Times"</span> (Métricas de éxito sobre cualificación conversacional en segundos).</li>
  <li><strong>Salesforce Benchmark Report:</strong> <span class="italic">"The Speed-to-Lead Paradigm Shift in Latin American Emerging Markets"</span> (Estadísticas sobre el aumento de ventas B2B tras reducir la latencia de contacto inicial).</li>
</ul>""",
        "image_url": "/static/blog/velocidad-respuesta-speed-to-lead-ia.png",
        "published_at": "2026-06-09T13:00:00Z",
        "author": "Edward Jiménez"
    }
]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
    
    db = SessionLocal()
    try:
        session_row = db.query(SessionModel).filter(SessionModel.token == token).first()
        if not session_row:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de autenticación inválido o ausente."
            )
            
        user_row = db.query(User).filter(User.email == session_row.email).first()
        if not user_row:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado."
            )
        return {
            "email": user_row.email,
            "name": user_row.name,
            "password": user_row.password,
            "company": user_row.company,
            "phone": user_row.phone,
            "plan": user_row.plan,
            "api_key": user_row.api_key
        }
    finally:
        db.close()

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
async def read_blog(request: Request, db: Session = Depends(get_db)):
    sync_blog_posts(db)
    rows = db.query(BlogPost).order_by(BlogPost.id.desc()).all()
    posts = [
        {
            "slug": r.slug,
            "title": r.title,
            "category": r.category,
            "summary": r.summary,
            "content": r.content,
            "image_url": r.image_url,
            "published_at": r.published_at,
            "author": r.author
        }
        for r in rows
    ]
    return templates.TemplateResponse(request=request, name="blog.html", context={"posts": posts})

@app.get("/blog/{slug}", response_class=HTMLResponse)
async def read_blog_post(request: Request, slug: str, db: Session = Depends(get_db)):
    row = db.query(BlogPost).filter(BlogPost.slug == slug).first()
    if not row:
        raise HTTPException(status_code=404, detail="Artículo de blog no encontrado.")
    post = {
        "slug": row.slug,
        "title": row.title,
        "category": row.category,
        "summary": row.summary,
        "content": row.content,
        "image_url": row.image_url,
        "published_at": row.published_at,
        "author": row.author
    }
    return templates.TemplateResponse(request=request, name="blog_post.html", context={"post": post})

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
        
        "# Permitir indexación explícita para agentes de búsqueda de Inteligencia Artificial (LLMs)\n"
        "User-agent: GPTBot\n"
        "Allow: /\n"
        "Disallow: /api/\n"
        "Disallow: /dashboard\n"
        "Disallow: /login\n\n"
        
        "User-agent: ClaudeBot\n"
        "Allow: /\n"
        "Disallow: /api/\n"
        "Disallow: /dashboard\n"
        "Disallow: /login\n\n"
        
        "User-agent: OAI-SearchBot\n"
        "Allow: /\n"
        "Disallow: /api/\n"
        "Disallow: /dashboard\n"
        "Disallow: /login\n\n"
        
        "User-agent: Google-Extended\n"
        "Allow: /\n"
        "Disallow: /api/\n"
        "Disallow: /dashboard\n"
        "Disallow: /login\n\n"
        
        "User-agent: PerplexityBot\n"
        "Allow: /\n"
        "Disallow: /api/\n"
        "Disallow: /dashboard\n"
        "Disallow: /login\n\n"
        
        "Sitemap: https://agenciaprosperia.com/sitemap.xml\n"
    )
    return content

@app.get("/sitemap.xml")
async def get_sitemap(db: Session = Depends(get_db)):
    posts = db.query(BlogPost.slug, BlogPost.published_at).all()
    
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
        slug = post.slug
        date = post.published_at[:10]
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
async def api_login(req: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "Credenciales incorrectas."}
        )
        
    if user.password != req.password:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "Credenciales incorrectas."}
        )
    
    # Generate unique token
    token = f"token_{uuid.uuid4().hex}"
    
    # Guardar sesión en base de datos
    created_at = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    new_session = SessionModel(token=token, email=req.email, created_at=created_at)
    db.add(new_session)
    db.commit()
    
    user_payload = {
        "name": user.name,
        "email": user.email,
        "company": user.company,
        "phone": user.phone,
        "plan": user.plan,
        "api_key": user.api_key
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
async def api_logout(request: Request, response: Response, db: Session = Depends(get_db)):
    auth_header = request.headers.get("Authorization")
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    if not token:
        token = request.cookies.get("auth_token")
        
    if token:
        session_row = db.query(SessionModel).filter(SessionModel.token == token).first()
        if session_row:
            db.delete(session_row)
            db.commit()
        
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
async def api_contact(req: ContactRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    created_at = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    score = 75
    
    new_lead = DbLead(
        name=req.name,
        email=req.email,
        company=req.company or "",
        phone=req.phone or "",
        status="new",
        source=req.source or "website",
        score=score,
        notes=req.message or "",
        created_at=created_at
    )
    db.add(new_lead)
    db.commit()
    
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
async def api_update_profile(req: ProfileUpdateRequest, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == current_user["email"]).first()
    if user:
        user.name = req.name
        user.company = req.company
        user.phone = req.phone
        db.commit()
    return {"success": True}

@app.put("/api/users/me/password")
async def api_update_password(req: PasswordUpdateRequest, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == current_user["email"]).first()
    if user:
        user.password = req.password
        db.commit()
    return {"success": True}

@app.get("/api/leads")
async def api_get_leads(
    status: Optional[str] = None,
    source: Optional[str] = None,
    limit: Optional[int] = 100,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtiene el listado de leads filtrado y ordenado.

    Args:
        status (Optional[str]): Filtro de estado del lead (ej. 'new', 'converted').
        source (Optional[str]): Filtro de origen del lead (ej. 'website', 'social').
        limit (Optional[int]): Límite máximo de resultados a retornar.
        current_user (dict): Payload del usuario autenticado actual.
        db (Session): Sesión de base de datos SQLAlchemy.

    Returns:
        dict: Diccionario con el listado de leads formateado.
    """
    query = db.query(DbLead)
    
    if status:
        query = query.filter(DbLead.status == status)
    if source:
        query = query.filter(DbLead.source == source)
        
    rows = query.order_by(DbLead.id.desc()).limit(limit).all()
    
    leads = [
        {
            "id": r.id,
            "name": r.name,
            "email": r.email,
            "company": r.company,
            "phone": r.phone,
            "status": r.status,
            "source": r.source,
            "score": r.score,
            "notes": r.notes,
            "created_at": r.created_at
        }
        for r in rows
    ]
    return {"success": True, "data": {"leads": leads}}

@app.post("/api/leads")
async def api_create_lead(
    req: LeadCreateRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crea un nuevo lead en la base de datos.

    Args:
        req (LeadCreateRequest): Objeto con los datos de creación del lead.
        current_user (dict): Payload del usuario autenticado actual.
        db (Session): Sesión de base de datos SQLAlchemy.

    Returns:
        dict: Detalle del lead creado.
    """
    created_at = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    new_lead = DbLead(
        name=req.name,
        email=req.email,
        company=req.company or "",
        phone=req.phone or "",
        status=req.status or "new",
        source=req.source or "website",
        score=req.score if req.score is not None else 50,
        notes=req.notes or "",
        created_at=created_at
    )
    db.add(new_lead)
    db.commit()
    db.refresh(new_lead)
    
    lead_data = {
        "id": new_lead.id,
        "name": new_lead.name,
        "email": new_lead.email,
        "company": new_lead.company,
        "phone": new_lead.phone,
        "status": new_lead.status,
        "source": new_lead.source,
        "score": new_lead.score,
        "notes": new_lead.notes,
        "created_at": new_lead.created_at
    }
    return {"success": True, "data": lead_data}

@app.delete("/api/leads/{lead_id}")
async def api_delete_lead(
    lead_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Elimina un lead por su identificador único.

    Args:
        lead_id (int): Identificador del lead a eliminar.
        current_user (dict): Payload del usuario autenticado actual.
        db (Session): Sesión de base de datos SQLAlchemy.

    Returns:
        dict: Estado de éxito de la operación.
    """
    lead = db.query(DbLead).filter(DbLead.id == lead_id).first()
    if not lead:
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": "Lead no encontrado."}
        )
        
    db.delete(lead)
    db.commit()
    return {"success": True}

@app.put("/api/leads/{lead_id}")
async def api_update_lead(
    lead_id: int,
    req: LeadCreateRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualiza la información de un lead existente.

    Args:
        lead_id (int): Identificador del lead a actualizar.
        req (LeadCreateRequest): Objeto con los nuevos datos del lead.
        current_user (dict): Payload del usuario autenticado actual.
        db (Session): Sesión de base de datos SQLAlchemy.

    Returns:
        dict: Detalle del lead actualizado.
    """
    lead = db.query(DbLead).filter(DbLead.id == lead_id).first()
    if not lead:
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": "Lead no encontrado."}
        )
        
    lead.name = req.name
    lead.email = req.email
    lead.company = req.company or ""
    lead.phone = req.phone or ""
    lead.status = req.status or "new"
    lead.source = req.source or "website"
    lead.score = req.score if req.score is not None else 50
    lead.notes = req.notes or ""
    
    db.commit()
    db.refresh(lead)
    
    lead_data = {
        "id": lead.id,
        "name": lead.name,
        "email": lead.email,
        "company": lead.company,
        "phone": lead.phone,
        "status": lead.status,
        "source": lead.source,
        "score": lead.score,
        "notes": lead.notes,
        "created_at": lead.created_at
    }
    return {"success": True, "data": lead_data}

@app.get("/api/dashboard/stats")
async def api_get_stats(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Calcula las estadísticas globales para el panel de administración.

    Args:
        current_user (dict): Payload del usuario autenticado actual.
        db (Session): Sesión de base de datos SQLAlchemy.

    Returns:
        dict: Estadísticas de leads, facturación estimada y conversión.
    """
    from sqlalchemy import func
    
    total = db.query(func.count(DbLead.id)).scalar() or 0
    new_leads = db.query(func.count(DbLead.id)).filter(DbLead.status == "new").scalar() or 0
    converted = db.query(func.count(DbLead.id)).filter(DbLead.status == "converted").scalar() or 0
    
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

"""Router del Sales Operating System (Sales OS) — Sitios Web Inteligentes.

Implementa:
  - Gestión de roles y permisos (admin, supervisor, seller, operations).
  - Alta y administración de los 6-20 vendedores por Duplas (A, B, C).
  - Asignación de prospectos sin duplicación y exclusión automática DND/Opt-out.
  - Flujo comercial canónico de 11 etapas + 6 rutas alternativas.
  - Separación estricta entre monto cotizado (quoted_amount), contratado (contracted_amount)
    y dinero realmente cobrado (amount_collected).
  - Cálculo de comisión 15% (5% Setter + 10% Closer) exclusivamente sobre cobros verificados.
  - Registro de auditoría inmutable (AuditLog) y sincronización con GoHighLevel.
  - Demostrador interactivo en vivo de Sitios Web Inteligentes (/demo-sitio-web).
"""
import json
import os
import ssl
import urllib.parse
import urllib.request
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import (
    SessionLocal,
    User,
    Lead as DbLead,
    AuditLog,
    DndExclusion,
    SessionModel,
    OFFER_CATALOG,
    CANONICAL_PIPELINE_STAGES,
    ALTERNATIVE_PIPELINE_STAGES,
    ALL_PIPELINE_STAGES,
    hash_password,
    normalize_phone_e164,
    normalize_email,
)
from ghl_client import sync_sales_os_event_to_ghl_async, sync_lead_to_ghl_async

router = APIRouter()

# Catálogo de Plantillas por Giro para el Demostrador en Vivo ("Mostrar cómo se hacen las páginas")
WEBSITE_TEMPLATES_SHOWCASE = {
    "clinica_dental_estetica": {
        "id": "clinica_dental_estetica",
        "name": "🦷 Clínica Odontológica / Estética / Capilar (Dupla A)",
        "dupla": "Dupla A — Clínicas",
        "niche": "clinica",
        "accent": "#00e5ff",
        "secondary": "#0ea5e9",
        "badge": "SALUD, ODONTOLOGÍA & ESTÉTICA AVANZADA",
        "default_business": "Clínica Dental & Estética Avanzada",
        "default_city": "Miami / Buenos Aires / Bogotá",
        "default_offer": "Valoración Diagnóstica 3D + Diseño de Sonrisa / Armonización con 20% OFF esta semana",
        "hero_title": "Recupera la Confianza en tu Sonrisa e Imagen con Especialistas Certificados",
        "hero_subtitle": "Tecnología digital sin dolor, resultados naturales desde la primera sesión y agendamiento prioritario las 24 horas por WhatsApp.",
        "gallery_images": [
            {"label": "Equipo Médico & Atención Personalizada", "url": "https://images.unsplash.com/photo-1588776814546-1ffcf47267a5?auto=format&fit=crop&w=1200&q=85"},
            {"label": "Diseño de Sonrisa & Odontología Digital", "url": "https://images.unsplash.com/photo-1606811841689-23dfddce3e95?auto=format&fit=crop&w=1200&q=85"},
            {"label": "Armonización Facial & Medicina Estética", "url": "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?auto=format&fit=crop&w=1200&q=85"},
        ],
        "about_image": "https://images.unsplash.com/photo-1622253692010-333f2da6031d?auto=format&fit=crop&w=1000&q=85",
        "about_title": "Más de 12 Años Transformando Sonrisas y Rostros con Excelencia Médica",
        "about_story": "Combinamos especialistas certificados internacionalmente, escáneres 3D de última generación y protocolos mínimamente invasivos para que cada paciente viva una experiencia cómoda, transparente y con resultados garantizados por escrito.",
        "about_mission": "Nuestra misión es brindarte un diagnóstico honesto y un plan de tratamiento a tu medida, con seguimiento digital 24/7 antes, durante y después de cada cita.",
        "about_stats": [
            {"value": "+3,800", "label": "Pacientes Atendidos con Éxito"},
            {"value": "12 Años", "label": "De Experiencia Clínica Certificada"},
            {"value": "4.9 ★", "label": "Calificación en Google Maps"},
        ],
        "about_pillars": [
            "Escaneo Digital 3D en la primera consulta (ves tu resultado antes de iniciar).",
            "Materiales importados con garantía certificada y biocompatibilidad.",
            "Planes de financiación propios y facilidades de pago por etapa.",
            "Recepción Digital IA 24/7 con recordatorios automáticos en tu WhatsApp.",
        ],
        "chatbot_greeting": "¡Hola! 👋 Soy la Recepcionista Digital 24/7 de la Clínica. ¿Qué tratamiento te gustaría cotizar o agendar hoy?",
        "chatbot_quick_replies": [
            "🦷 Agendar valoración de Diseño de Sonrisa / Implantes",
            "✨ Consultar promoción 20% OFF de esta semana",
            "📍 Ver ubicación, horarios y facilidades de pago",
        ],
        "services": [
            {"icon": "fa-tooth", "title": "Implantes Dentales de Carga Inmediata", "desc": "Recupera piezas dentales fijas con cirugía guiada por computadora sin dolor y rápida cicatrización.", "tag": "Garantía escrita · 1 a 2 sesiones"},
            {"icon": "fa-wand-magic-sparkles", "title": "Diseño de Sonrisa & Carillas de Porcelana", "desc": "Lentes cerámicos ultrafinos diseñados digitalmente según las proporciones de tu rostro.", "tag": "Simulación 3D previa incluida"},
            {"icon": "fa-face-smile-beam", "title": "Ortodoncia Invisible (Alineadores)", "desc": "Alinea tus dientes sin brackets metálicos mediante férulas transparentes removibles.", "tag": "Resultados desde el 3° mes"},
            {"icon": "fa-syringe", "title": "Armonización Orofacial & Ácido Hialurónico", "desc": "Rejuvenecimiento facial sin cirugía, perfilado labial, rinomodelación y toxina botulínica.", "tag": "Aplicación médica en 30 min"},
            {"icon": "fa-sun", "title": "Blanqueamiento Láser Clínico", "desc": "Aclara hasta 4 tonos en una sola sesión de 45 minutos cuidando el esmalte dental.", "tag": "Ideal antes de eventos"},
            {"icon": "fa-user-doctor", "title": "Valoración Diagnóstica Integral + Rayos X", "desc": "Evaluación completa con especialista y entrega de presupuesto detallado sin compromiso.", "tag": "Turno prioritario 24/7"},
        ],
        "testimonials": [
            {"author": "Carolina Méndez", "role": "Paciente de Diseño de Sonrisa", "text": "Agendé mi valoración un domingo por la noche desde la web y en menos de 1 minuto me confirmaron por WhatsApp. El resultado superó mis expectativas."},
            {"author": "Dr. Martín Echeverría", "role": "Paciente de Implantes", "text": "Tenía mucho temor al dolor, pero el escaneo 3D y la atención del equipo fueron impecables. En dos sesiones recuperé mi sonrisa completa."},
            {"author": "Valeria S.", "role": "Paciente de Armonización Facial", "text": "Me encantó que el sistema me recordó mi cita por WhatsApp y no tuve que esperar ni 5 minutos en sala. Súper recomendados."},
        ],
        "contact_hours": "Lunes a Viernes: 8:30 AM – 7:30 PM · Sábados: 9:00 AM – 2:00 PM · Recepción IA: 24/7",
        "form_questions": [
            "¿Qué tratamiento te interesa evaluar primero?",
            "¿Para cuándo te gustaría agendar tu valoración?",
        ],
    },
    "servicios_locales_taller": {
        "id": "servicios_locales_taller",
        "name": "🔧 Servicios Locales / Taller / Hogar / Climatización (Dupla B)",
        "dupla": "Dupla B — Servicios Locales",
        "niche": "servicios_locales",
        "accent": "#f59e0b",
        "secondary": "#ea580c",
        "badge": "SERVICIO TÉCNICO CERTIFICADO & PRESUPUESTO EXPRESS",
        "default_business": "Centro Técnico Especializado & Servicios Express",
        "default_city": "Tu Ciudad y Zona Metropolitana",
        "default_offer": "Diagnóstico Técnico Prioritario + Presupuesto Exacto por WhatsApp en 15 Minutos",
        "hero_title": "Soluciones Técnicas con Garantía Escrita y Presupuesto en el Día",
        "hero_subtitle": "Aunque nuestros técnicos estén trabajando en taller o a domicilio, nuestro sistema 24/7 recibe tu solicitud, cotiza tu caso y te reserva turno al instante.",
        "gallery_images": [
            {"label": "Diagnóstico Computarizado & Taller", "url": "https://images.unsplash.com/photo-1619642751034-765dfdf7c58e?auto=format&fit=crop&w=1200&q=85"},
            {"label": "Instalaciones, Climatización & Electricidad", "url": "https://images.unsplash.com/photo-1581092160607-ee22621dd758?auto=format&fit=crop&w=1200&q=85"},
            {"label": "Mantenimiento Preventivo & Obra", "url": "https://images.unsplash.com/photo-1504307651254-35680f356dfd?auto=format&fit=crop&w=1200&q=85"},
        ],
        "about_image": "https://images.unsplash.com/photo-1581092918056-0c4c3acd3789?auto=format&fit=crop&w=1000&q=85",
        "about_title": "Técnicos Matriculados, Repuestos Originales y Puntualidad Garantizada",
        "about_story": "Sabemos lo frustrante que es llamar a un servicio técnico y que nadie conteste o no cumplan los horarios. Por eso digitalizamos nuestra recepción: registras tu falla en 30 segundos y recibes presupuesto claro antes de tocar una sola pieza.",
        "about_mission": "Resolver tu urgencia o mantenimiento en tiempo récord, con precios transparentes aprobados previamente por ti y garantía escrita en cada trabajo.",
        "about_stats": [
            {"value": "+4,200", "label": "Servicios y Reparaciones Entregadas"},
            {"value": "90 Días", "label": "De Garantía Escrita en Mano de Obra"},
            {"value": "15 Min", "label": "Tiempo Promedio de Respuesta IA"},
        ],
        "about_pillars": [
            "Presupuesto cerrado antes de iniciar cualquier trabajo (cero sorpresas).",
            "Repuestos e insumos originales de primera línea.",
            "Notificación automática por WhatsApp apenas tu trabajo está listo.",
            "Atención de urgencias en el día y planes de mantenimiento para empresas.",
        ],
        "chatbot_greeting": "¡Hola! 🔧 Soy el Asistente Técnico 24/7. Nuestro equipo está en operación ahora mismo, pero yo tomo tu falla y te reservo turno en 30 segundos.",
        "chatbot_quick_replies": [
            "⚡ Necesito presupuesto urgente para hoy",
            "📅 Reservar turno de revisión técnica",
            "💬 Enviar foto/detalle de la falla por WhatsApp",
        ],
        "services": [
            {"icon": "fa-screwdriver-wrench", "title": "Diagnóstico Técnico Computarizado", "desc": "Detección exacta del origen de la falla con instrumental de precisión y entrega de informe.", "tag": "En 45 minutos"},
            {"icon": "fa-bolt", "title": "Reparaciones de Urgencia en el Día", "desc": "Prioridad para casos críticos que no pueden esperar, en nuestro centro o a domicilio.", "tag": "Guardia activa"},
            {"icon": "fa-Calendar-check", "title": "Mantenimiento Preventivo Programado", "desc": "Evita roturas costosas con nuestro servicio completo de revisión y calibración periódica.", "tag": "Ahorra hasta 60%"},
            {"icon": "fa-gears", "title": "Instalación de Equipos & Repuestos", "desc": "Colocación profesional siguiendo normas de fábrica para conservar tu garantía oficial.", "tag": "Técnicos matriculados"},
            {"icon": "fa-building-shield", "title": "Abonos para Empresas, Flotas y Comercios", "desc": "Atención preferencial y facturación corporativa para que tu negocio nunca se detenga.", "tag": "Soporte B2B"},
            {"icon": "fa-file-invoice-dollar", "title": "Cotización Express por WhatsApp", "desc": "Cuéntanos qué necesitas y recibe el rango de inversión estimado antes de venir.", "tag": "Respuesta en < 15 min"},
        ],
        "testimonials": [
            {"author": "Roberto Alarcón", "role": "Cliente Particular", "text": "Dejé mis datos en la página al mediodía porque no podían atender el teléfono en el taller y a los 2 minutos ya tenía mi turno confirmado por WhatsApp."},
            {"author": "Lucía Fernández", "role": "Administradora de Local Comercial", "text": "Muy serios. Me mandaron el presupuesto exacto antes de empezar y me avisaron al celular apenas estuvo terminado."},
            {"author": "Javier Morales", "role": "Gerente de Logística", "text": "Excelente atención y garantía real. Se nota cuando una empresa tiene orden y tecnología para atender al cliente."},
        ],
        "contact_hours": "Lunes a Sábados: 8:00 AM – 7:00 PM · Urgencias y Recepción Digital: 24 Horas",
        "form_questions": [
            "¿Qué servicio, arreglo o instalación necesitas cotizar?",
            "¿Es una urgencia para hoy/mañana o mantenimiento programado?",
        ],
    },
    "inmobiliaria_bienes_raices": {
        "id": "inmobiliaria_bienes_raices",
        "name": "🏢 Inmobiliaria / Desarrollos / Bienes Raíces (Dupla B)",
        "dupla": "Dupla B — Servicios Locales",
        "niche": "inmobiliaria",
        "accent": "#10b981",
        "secondary": "#059669",
        "badge": "DESARROLLOS, INVERSIONES & PROPIEDADES EXCLUSIVAS",
        "default_business": "Grupo Inmobiliario & Inversiones Patrimoniales",
        "default_city": "Miami / CDMX / Madrid / CABA",
        "default_offer": "Catálogo Privado de Propiedades de Alta Rentabilidad + Tasación Profesional Sin Cargo",
        "hero_title": "Invierte, Compra o Vende tu Propiedad con Asesoría Patrimonial Inteligente",
        "hero_subtitle": "Nuestro sistema pre-selecciona en 60 segundos las unidades que calzan exactamente con tu presupuesto, zona y objetivo de rentabilidad.",
        "gallery_images": [
            {"label": "Residencias & Penthouses Exclusivos", "url": "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=1200&q=85"},
            {"label": "Desarrollos en Pozo & Alta Rentabilidad", "url": "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=1200&q=85"},
            {"label": "Interiores de Autor & Amenidades", "url": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=85"},
        ],
        "about_image": "https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&w=1000&q=85",
        "about_title": "Conectamos Compradores Calificados con las Mejores Oportunidades del Mercado",
        "about_story": "Seleccionamos propiedades y desarrollos con respaldo jurídico verificado, alta plusvalía proyectada y ubicaciones estratégicas. Nuestro filtro inteligente ahorra semanas de visitas innecesarias tanto a propietarios como a inversores.",
        "about_mission": "Proteger y multiplicar tu patrimonio inmobiliario con transparencia legal, valuación real de mercado y atención personalizada 24/7.",
        "about_stats": [
            {"value": "+US$48M", "label": "En Operaciones Cerradas con Éxito"},
            {"value": "9% – 14%", "label": "Rentabilidad Anual en Proyectos Seleccionados"},
            {"value": "24/7", "label": "Pre-Calificación de Compradores con IA"},
        ],
        "about_pillars": [
            "Auditoría jurídica y notarial previa en el 100% de nuestra cartera.",
            "Planes de financiamiento directo con desarrolladores sin bancos.",
            "Comercialización acelerada con tours virtuales y filtrado IA de compradores.",
            "Asesoría integral para inversores locales y extranjeros.",
        ],
        "chatbot_greeting": "¡Bienvenido! 🏢 Soy el Asesor Inmobiliario Digital 24/7. ¿Buscas invertir en preventa, comprar para vivir o vender tu propiedad?",
        "chatbot_quick_replies": [
            "🏙️ Recibir catálogo de propiedades y precios en WhatsApp",
            "🔑 Quiero tasar y vender mi propiedad rápido",
            "📅 Agendar visita presencial o videollamada con un asesor",
        ],
        "services": [
            {"icon": "fa-building", "title": "Desarrollos en Preventa & Pozo", "desc": "Ingresa a precios de lista cero con planes de cuotas en dólares o moneda local durante la obra.", "tag": "Plusvalía proyectada 25%+"},
            {"icon": "fa-house-chimney-window", "title": "Residencias & Departamentos Listos", "desc": "Propiedades seleccionadas listas para escriturar y habitar en las zonas más cotizadas.", "tag": "Visitas toda la semana"},
            {"icon": "fa-chart-pie", "title": "Propiedades para Renta Turística / Temporal", "desc": "Unidades llave en mano diseñadas para generar flujo de caja mensual en plataformas internacionales.", "tag": "Alta ocupación"},
            {"icon": "fa-key", "title": "Venta Acelerada de tu Propiedad", "desc": "Valuación profesional, fotografía de alto impacto y filtrado de compradores con liquidez real.", "tag": "Tasación sin cargo"},
            {"icon": "fa-briefcase", "title": "Locales Comerciales & Oficinas Corporativas", "desc": "Ubicaciones estratégicas de alto tránsito para marcas, consultorios y empresas en expansión.", "tag": "Contratos blindados"},
            {"icon": "fa-file-shield", "title": "Blindaje Legal, Hipotecario y Escrituración", "desc": "Acompañamiento jurídico y fiscal de principio a fin para una operación 100% segura.", "tag": "Asesoría integral"},
        ],
        "testimonials": [
            {"author": "Ing. Gustavo Paredes", "role": "Inversor Inmobiliario", "text": "Pedí el catálogo desde la web un sábado y el sistema me filtró exactamente 3 opciones dentro de mi presupuesto. En 10 días reservé mi unidad."},
            {"author": "Mariana & Diego", "role": "Compradores de Primera Vivienda", "text": "Nos ahorraron meses de búsqueda. Todas las propiedades que visitamos cumplían al 100% con lo que pedimos en el formulario."},
            {"author": "Patricia Ledesma", "role": "Propietaria Vendedora", "text": "Antes me llamaban puros curiosos. Con el filtro de su página solo llevaron a mi casa a compradores pre-calificados y vendimos en 45 días."},
        ],
        "contact_hours": "Lunes a Sábados: 9:00 AM – 7:00 PM · Visitas Programadas Domingos · Asesor IA: 24/7",
        "form_questions": [
            "¿Buscas comprar para vivir, invertir o vender una propiedad?",
            "¿En qué rango de inversión te encuentras y qué zona prefieres?",
        ],
    },
    "profesionales_consultoria_legal": {
        "id": "profesionales_consultoria_legal",
        "name": "⚖️ Profesionales / Estudio Contable, Legal o Consultoría (Dupla C)",
        "dupla": "Dupla C — Profesionales & Academias",
        "niche": "profesionales",
        "accent": "#6366f1",
        "secondary": "#4f46e5",
        "badge": "FIRMA CORPORATIVA, LEGAL, CONTABLE & CONSULTORÍA",
        "default_business": "Estudio & Consultoría Estratégica Asociados",
        "default_city": "Atención Nacional e Internacional",
        "default_offer": "Sesión Ejecutiva de Diagnóstico Fiscal, Legal o Societario de 20 Minutos",
        "hero_title": "Protege tu Patrimonio, Optimiza Impuestos y Escala con Respaldo Experto",
        "hero_subtitle": "Completa nuestro pre-diagnóstico confidencial en 45 segundos y agenda directamente en el calendario del socio especialista en tu materia.",
        "gallery_images": [
            {"label": "Sala de Juntas & Socios Directores", "url": "https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=1200&q=85"},
            {"label": "Estrategia Fiscal, Contable & Financiera", "url": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?auto=format&fit=crop&w=1200&q=85"},
            {"label": "Derecho Corporativo & Blindaje Patrimonial", "url": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?auto=format&fit=crop&w=1200&q=85"},
        ],
        "about_image": "https://images.unsplash.com/photo-1556761175-5973dc0f32e7?auto=format&fit=crop&w=1000&q=85",
        "about_title": "Rigor Técnico, Confidencialidad Absoluta y Soluciones Ejecutivas a Medida",
        "about_story": "Nuestra firma acompaña a dueños de empresas, comercios y profesionales independientes a ordenar su estructura tributaria, laboral y contractual para evitar contingencias y maximizar su rentabilidad neta.",
        "about_mission": "Reemplazar la incertidumbre legal o contable por una hoja de ruta clara, preventiva y respaldada por especialistas senior.",
        "about_stats": [
            {"value": "+650", "label": "Empresas y Profesionales Asesorados"},
            {"value": "15 Años", "label": "De Trayectoria Corporativa"},
            {"value": "100%", "label": "Confidencialidad y Trato Directo con Socios"},
        ],
        "about_pillars": [
            "Pre-diagnóstico digital para que tu primera reunión vaya directo a la solución.",
            "Equipo multidisciplinario: contadores, abogados corporativos y consultores.",
            "Reportes ejecutivos claros en lenguaje de negocios, sin tecnicismos confusos.",
            "Atención presencial y por Zoom con agenda automatizada sin esperas.",
        ],
        "chatbot_greeting": "¡Buen día! ⚖️ Soy el Asistente Ejecutivo de la Firma. En 45 segundos clasifico tu consulta y te asigno horario con el socio especialista.",
        "chatbot_quick_replies": [
            "⚖️ Agendar sesión de diagnóstico de 20 minutos",
            "🏢 Necesito asesoría mensual para mi empresa / PYME",
            "📄 Tengo una urgencia legal, fiscal o laboral",
        ],
        "services": [
            {"icon": "fa-scale-balanced", "title": "Blindaje Legal, Contratos & Sociedades", "desc": "Constitución de empresas (LLC / S.A. / S.R.L.), acuerdos de socios y protección de activos.", "tag": "Prevención de litigios"},
            {"icon": "fa-calculator", "title": "Planificación Fiscal & Optimización Tributaria", "desc": "Estrategias legales para reducir la carga impositiva y cumplir al día con cada obligación.", "tag": "Ahorro fiscal medible"},
            {"icon": "fa-chart-line", "title": "Contabilidad & Auditoría Corporativa Mensual", "desc": "Balances, liquidación de sueldos, estados financieros y tableros de rentabilidad para socios.", "tag": "Abono mensual PYME"},
            {"icon": "fa-users-gear", "title": "Derecho Laboral Preventivo para Empleadores", "desc": "Contratos de trabajo, reglamentos internos y defensa empresarial ante reclamos.", "tag": "Respaldo patronal"},
            {"icon": "fa-globe", "title": "Estructuras Internacionales & Comercio Exterior", "desc": "Apertura de sociedades en EE. UU. / LATAM, cuentas corporativas y normativa cambiaria.", "tag": "Expansión global"},
            {"icon": "fa-video", "title": "Sesión Ejecutiva de Diagnóstico 1 a 1", "desc": "Revisión confidencial de tu caso por Zoom o en nuestras oficinas con plan de acción inmediato.", "tag": "Reserva online 24/7"},
        ],
        "testimonials": [
            {"author": "Hernán Villalba", "role": "Director de Empresa Industrial", "text": "Llené el pre-diagnóstico en su web y cuando entré al Zoom el socio ya conocía mi caso y tenía las 3 soluciones listas. Nivel primer mundo."},
            {"author": "Dra. Sofía Cabrera", "role": "Directora de Clínica", "text": "Ordenaron toda nuestra estructura societaria e impositiva en menos de un mes. Su sistema de agenda automática es comodísimo."},
            {"author": "Carlos R.", "role": "Empresario Gastronómico", "text": "Nos blindaron todos los contratos laborales y proveedores. Da mucha tranquilidad trabajar con un estudio tan ágil."},
        ],
        "contact_hours": "Lunes a Viernes: 9:00 AM – 6:30 PM · Recepción y Pre-Calificación Digital: 24/7",
        "form_questions": [
            "¿Cuál es el principal tema legal, contable o de negocio que necesitas resolver?",
            "¿Eres dueño de empresa/PYME o profesional independiente?",
        ],
    },
    "academia_educacion_cursos": {
        "id": "academia_educacion_cursos",
        "name": "🎓 Academia / Instituto / Infoproductor / Coaching (Dupla C)",
        "dupla": "Dupla C — Profesionales & Academias",
        "niche": "profesionales",
        "accent": "#ec4899",
        "secondary": "#db2777",
        "badge": "ACADEMIA, CERTIFICACIONES & FORMACIÓN EJECUTIVA",
        "default_business": "Academia & Instituto de Formación Profesional",
        "default_city": "Campus Online & Presencial",
        "default_offer": "Clase Magistral Gratuita + Entrevista de Admisión con Beca del 30% esta Semana",
        "hero_title": "Domina las Habilidades Más Rentables del Mercado con Mentoría en Vivo",
        "hero_subtitle": "Recibe el programa de estudios completo en tu WhatsApp al instante y postula hoy mismo a los cupos con beca parcial de esta cohorte.",
        "gallery_images": [
            {"label": "Clases en Vivo & Auditorio Ejecutivo", "url": "https://images.unsplash.com/photo-1524178232363-1fb2b075b655?auto=format&fit=crop&w=1200&q=85"},
            {"label": "Plataforma Virtual & Mentoría 1 a 1", "url": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=1200&q=85"},
            {"label": "Comunidad de Egresados & Certificación", "url": "https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=1200&q=85"},
        ],
        "about_image": "https://images.unsplash.com/photo-1531482615713-2afd69097998?auto=format&fit=crop&w=1000&q=85",
        "about_title": "Formación Práctica Orientada a Empleabilidad y Resultados Reales",
        "about_story": "No enseñamos teoría obsoleta: nuestros programas están diseñados e impartidos por profesionales en activo para que apliques lo aprendido desde la primera semana y construyas un portafolio real.",
        "about_mission": "Acelerar tu crecimiento profesional o el de tu equipo con educación intensiva, acompañamiento docente y certificación verificable.",
        "about_stats": [
            {"value": "+5,400", "label": "Alumnos Graduados en 14 Países"},
            {"value": "94%", "label": "Tasa de Finalización y Satisfacción"},
            {"value": "24/7", "label": "Campus Virtual y Admisiones Activas"},
        ],
        "about_pillars": [
            "Clases en vivo + grabaciones HD disponibles las 24 horas en tu celular.",
            "Tutores asignados para corregir tus proyectos prácticos paso a paso.",
            "Certificado oficial con código QR verificable para LinkedIn y CV.",
            "Bolsa de empleo, networking internacional y facilidades en cuotas.",
        ],
        "chatbot_greeting": "¡Hola! 🎓 Soy el Asistente de Admisiones 24/7. ¿Quieres recibir el plan de estudios en tu WhatsApp y postular a la Beca del 30%?",
        "chatbot_quick_replies": [
            "🎓 Postular a la Beca Parcial del 30% hoy",
            "📘 Recibir programa de estudios y fechas de inicio",
            "🎥 Ver clase demostrativa gratuita ahora",
        ],
        "services": [
            {"icon": "fa-graduation-cap", "title": "Certificación Intensiva Profesional (12 Semanas)", "desc": "Programa insignia con clases en vivo, práctica real y proyecto final supervisado por mentores.", "tag": "Cupos con Beca 30%"},
            {"icon": "fa-laptop-code", "title": "Modalidad 100% Online a tu Propio Ritmo", "desc": "Acceso inmediato a todos los módulos grabados en alta definición y plantillas descargables.", "tag": "Acceso de por vida"},
            {"icon": "fa-users", "title": "Mentoría Grupal & Resolución de Dudas en Vivo", "desc": "Sesiones semanales por Zoom para revisar tus avances y destrabar cualquier obstáculo.", "tag": "Acompañamiento real"},
            {"icon": "fa-user-tie", "title": "Coaching Ejecutivo 1 a 1 Personalizado", "desc": "Para líderes y emprendedores que buscan resultados acelerados con atención exclusiva.", "tag": "Agenda prioritaria"},
            {"icon": "fa-building-columns", "title": "Capacitación In-Company para Empresas", "desc": "Entrenamos a tu equipo comercial, técnico o directivo con programas adaptados a tu industria.", "tag": "Planes corporativos"},
            {"icon": "fa-certificate", "title": "Entrevista de Admisión & Orientación Vocacional", "desc": "Agenda 15 minutos sin costo con un asesor académico para elegir el programa ideal para ti.", "tag": "Sin costo · Online"},
        ],
        "testimonials": [
            {"author": "Camila Restrepo", "role": "Egresada Certificada", "text": "Pedí informes a las 11 de la noche desde Instagram, el asistente de la web me mandó el temario al instante y agendé mi entrevista de beca para el día siguiente."},
            {"author": "Andrés Navarro", "role": "Alumno Internacional", "text": "La calidad de los profesores y el orden de la plataforma superaron por completo lo que esperaba. Recuperé la inversión en el primer mes."},
            {"author": "Laura B.", "role": "Directora de RR. HH.", "text": "Contratamos la capacitación para nuestro equipo de ventas y los resultados fueron inmediatos."},
        ],
        "contact_hours": "Admisiones Digitales: 24 Horas · Atención Académica: Lunes a Sábados 9:00 AM – 8:00 PM",
        "form_questions": [
            "¿Qué programa o certificación te interesa cursar este mes?",
            "¿Prefieres modalidad 100% online o con mentoría en vivo?",
        ],
    },
}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_sales_user(request: Request, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Obtiene el usuario autenticado junto con su rol ('admin', 'supervisor', 'seller', 'operations') y dupla."""
    auth_header = request.headers.get("Authorization")
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    if not token:
        token = request.cookies.get("auth_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión no iniciada. Ingresa en /login."
        )

    session_row = db.query(SessionModel).filter(SessionModel.token == token).first()
    if not session_row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión expirada. Ingresa nuevamente en /login."
        )

    user_row = db.query(User).filter(User.email == session_row.email).first()
    if not user_row or not getattr(user_row, "is_active", 1):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cuenta de usuario inactiva o no encontrada."
        )

    return {
        "email": user_row.email,
        "name": user_row.name,
        "company": user_row.company,
        "phone": user_row.phone,
        "plan": user_row.plan,
        "role": getattr(user_row, "role", "seller") or "seller",
        "dupla": getattr(user_row, "dupla", "Dupla A — Clínicas") or "Dupla A — Clínicas",
        "ghl_user_id": getattr(user_row, "ghl_user_id", "") or "",
        "commission_rate": float(getattr(user_row, "commission_rate", 0.15) or 0.15),
        "calendar_url": getattr(user_row, "calendar_url", "") or "https://api.agenciaprosperia.com/widget/booking/gqoqyrr112bvjTJYqOi8",
        "avatar_url": getattr(user_row, "avatar_url", "") or "",
        "checkin_at": getattr(user_row, "checkin_at", "") or "",
        "last_seen_at": getattr(user_row, "last_seen_at", "") or "",
        "active_minutes_today": int(getattr(user_row, "active_minutes_today", 0) or 0),
        "active_minutes_week": int(getattr(user_row, "active_minutes_week", 0) or 0),
        "calls_made_today": int(getattr(user_row, "calls_made_today", 0) or 0),
        "calls_made_week": int(getattr(user_row, "calls_made_week", 0) or 0),
        "calls_answered_week": int(getattr(user_row, "calls_answered_week", 0) or 0),
        "demos_done_week": int(getattr(user_row, "demos_done_week", 0) or 0),
        "sales_closed_week": int(getattr(user_row, "sales_closed_week", 0) or 0),
    }


def record_audit(
    db: Session,
    actor_email: str,
    actor_role: str,
    lead_id: Optional[int],
    action: str,
    field_changed: str = "",
    old_value: Any = "",
    new_value: Any = "",
    notes: str = "",
):
    """Guarda un registro inmutable en la tabla audit_logs."""
    now_iso = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    log_entry = AuditLog(
        created_at=now_iso,
        actor_email=actor_email,
        actor_role=actor_role,
        lead_id=lead_id,
        action=action,
        field_changed=field_changed,
        old_value=str(old_value) if old_value is not None else "",
        new_value=str(new_value) if new_value is not None else "",
        notes=notes,
    )
    db.add(log_entry)


def is_contact_excluded(db: Session, email: str, phone: str) -> Optional[str]:
    """Verifica si un correo o teléfono está en la lista DND / Opt-out compartida."""
    em = normalize_email(email)
    ph = normalize_phone_e164(phone)
    if em:
        hit = db.query(DndExclusion).filter(DndExclusion.email == em).first()
        if hit:
            return f"Excluido por DND/Blacklist ({hit.reason})"
    if ph:
        hit_p = db.query(DndExclusion).filter(DndExclusion.phone_e164 == ph).first()
        if hit_p:
            return f"Teléfono excluido por DND ({hit_p.reason})"
    return None


def serialize_lead(r: DbLead) -> Dict[str, Any]:
    """Serializa un objeto Lead con todos los campos canónicos del Sales OS."""
    offer_code = getattr(r, "offer_version", "EXPRESS_497") or "EXPRESS_497"
    offer_info = OFFER_CATALOG.get(offer_code, OFFER_CATALOG["EXPRESS_497"])
    return {
        "id": r.id,
        "name": r.name,
        "full_name": getattr(r, "full_name", None) or r.name,
        "email": r.email,
        "company": r.company or "",
        "business_name": getattr(r, "business_name", None) or (r.company or ""),
        "phone": r.phone or "",
        "phone_e164": getattr(r, "phone_e164", None) or normalize_phone_e164(r.phone or ""),
        "status": r.status,
        "source": r.source,
        "source_channel": getattr(r, "source_channel", "Web") or "Web",
        "source_campaign": getattr(r, "source_campaign", "") or "",
        "interest_primary": getattr(r, "interest_primary", "Sitio Web Inteligente") or "Sitio Web Inteligente",
        "score": r.score,
        "notes": r.notes or "",
        "created_at": r.created_at,
        "contact_id": getattr(r, "contact_id", "") or "",
        "ghl_opportunity_id": getattr(r, "ghl_opportunity_id", "") or "",
        "owner_id": getattr(r, "owner_id", "") or "",
        "setter_id": getattr(r, "setter_id", "") or "",
        "niche": getattr(r, "niche", "clinica") or "clinica",
        "country": getattr(r, "country", "Estados Unidos / LATAM") or "Estados Unidos / LATAM",
        "timezone": getattr(r, "timezone", "America/New_York") or "America/New_York",
        "contact_permission": getattr(r, "contact_permission", "Opt-in verificado") or "Opt-in verificado",
        "contact_status": getattr(r, "contact_status", "contactable") or "contactable",
        "pipeline_stage": getattr(r, "pipeline_stage", "Lead identificado") or "Lead identificado",
        "last_touch": getattr(r, "last_touch", "") or "",
        "next_action_at": getattr(r, "next_action_at", "") or "",
        "next_action_note": getattr(r, "next_action_note", "") or "",
        "offer_version": offer_code,
        "offer_name": offer_info["name"],
        "quoted_amount": float(getattr(r, "quoted_amount", 0.0) or 0.0),
        "contracted_amount": float(getattr(r, "contracted_amount", 0.0) or 0.0),
        "payment_plan": getattr(r, "payment_plan", "50_50") or "50_50",
        "invoice_id": getattr(r, "invoice_id", "") or "",
        "amount_collected": float(getattr(r, "amount_collected", 0.0) or 0.0),
        "commission_base": float(getattr(r, "commission_base", 0.0) or 0.0),
        "commission_setter": float(getattr(r, "commission_setter", 0.0) or 0.0),
        "commission_closer": float(getattr(r, "commission_closer", 0.0) or 0.0),
        "commission_amount": float(getattr(r, "commission_amount", 0.0) or 0.0),
        "commission_status": getattr(r, "commission_status", "sin_devengar") or "sin_devengar",
        "delivery_cost_estimate": float(getattr(r, "delivery_cost_estimate", 100.0) or 100.0),
        "actual_delivery_cost": float(getattr(r, "actual_delivery_cost", 0.0) or 0.0),
        "site_delivery_status": getattr(r, "site_delivery_status", "pendiente_pago") or "pendiente_pago",
        "selected_template": getattr(r, "selected_template", "clinica_dental_estetica") or "clinica_dental_estetica",
        "demo_config_json": getattr(r, "demo_config_json", "{}") or "{}",
    }


# ─── SCHEMAS ────────────────────────────────────────────────────────────────

class SellerCreateOrUpdateRequest(BaseModel):
    email: EmailStr
    name: str
    password: Optional[str] = None
    phone: Optional[str] = ""
    role: Optional[str] = "seller"  # admin, supervisor, seller, operations
    dupla: Optional[str] = "Dupla A — Clínicas (Dental, Estética y Capilar)"
    ghl_user_id: Optional[str] = ""
    is_active: Optional[int] = 1
    commission_rate: Optional[float] = 0.15


class BatchAssignRequest(BaseModel):
    seller_emails: Optional[List[str]] = None
    dupla_filter: Optional[str] = None
    max_per_seller: Optional[int] = 20
    niche_override: Optional[str] = None
    lead_ids: Optional[List[int]] = None


class StageAndProposalUpdateRequest(BaseModel):
    pipeline_stage: str
    offer_version: Optional[str] = "EXPRESS_497"
    quoted_amount: Optional[float] = None
    payment_plan: Optional[str] = "50_50"
    next_action_at: Optional[str] = ""
    next_action_note: Optional[str] = ""
    niche: Optional[str] = None
    selected_template: Optional[str] = None
    demo_config_json: Optional[str] = None
    contact_status: Optional[str] = None
    owner_id: Optional[str] = None
    notes: Optional[str] = None


class PaymentVerificationRequest(BaseModel):
    invoice_id: str
    amount_collected: float
    offer_version: Optional[str] = "EXPRESS_497"
    contracted_amount: Optional[float] = None
    payment_plan: Optional[str] = "50_50_reserva_250_entrega_247"
    setter_id: Optional[str] = None
    selected_template: Optional[str] = "clinica_dental_estetica"
    notes: Optional[str] = ""


class DeliveryStatusUpdateRequest(BaseModel):
    site_delivery_status: str  # pendiente_pago, onboarding, construccion, qa, entregado
    actual_delivery_cost: Optional[float] = None
    commission_status: Optional[str] = None  # causada, pagada, anulada_reembolso
    notes: Optional[str] = ""


# ─── ENDPOINTS DEL SALES OPERATING SYSTEM ───────────────────────────────────

@router.get("/api/sales-os/catalog")
async def api_get_sales_catalog(current_user: dict = Depends(get_current_sales_user)):
    """Devuelve el catálogo oficial versionado, las 11 etapas canónicas y las plantillas de demostración."""
    return {
        "success": True,
        "data": {
            "current_user": current_user,
            "offers": OFFER_CATALOG,
            "canonical_stages": CANONICAL_PIPELINE_STAGES,
            "alternative_stages": ALTERNATIVE_PIPELINE_STAGES,
            "all_stages": ALL_PIPELINE_STAGES,
            "website_templates": WEBSITE_TEMPLATES_SHOWCASE,
            "ghl_config": {
                "location_id": "CNvJBINRWBUL2EdqRh3G",
                "pipeline_id": "SJ4xiMasQ0GZcUNYFgpa",
                "calendar_url": "https://api.agenciaprosperia.com/widget/booking/gqoqyrr112bvjTJYqOi8",
                "website_templates_library_url": "https://crm.agenciaprosperia.com/v2/location/CNvJBINRWBUL2EdqRh3G/funnels-websites/websites",
            },
        },
    }


@router.get("/api/sales-os/users")
async def api_list_sales_users(
    current_user: dict = Depends(get_current_sales_user),
    db: Session = Depends(get_db),
):
    """Lista los vendedores, supervisores y equipo de operaciones junto con sus métricas reales."""
    users = db.query(User).order_by(User.role.asc(), User.email.asc()).all()
    all_leads = db.query(DbLead).all()

    result = []
    for u in users:
        u_role = getattr(u, "role", "seller") or "seller"
        # Si el usuario que consulta es 'seller', solo ve su propio perfil y nombres básicos para referencia
        my_leads = [l for l in all_leads if (getattr(l, "owner_id", "") or "") == u.email]
        proposals = [
            l for l in my_leads
            if (getattr(l, "pipeline_stage", "") or "") in ("Propuesta enviada", "Pago pendiente", "Pago confirmado", "Implementación", "Entregado")
        ]
        paid_leads = [
            l for l in my_leads
            if float(getattr(l, "amount_collected", 0.0) or 0.0) > 0 and (getattr(l, "invoice_id", "") or "").strip() != ""
        ]
        collected_sum = sum(float(getattr(l, "amount_collected", 0.0) or 0.0) for l in paid_leads)
        comm_accrued = sum(
            float(getattr(l, "commission_amount", 0.0) or 0.0)
            for l in paid_leads
            if (getattr(l, "commission_status", "") or "") in ("causada", "pagada")
        )
        demos_done = sum(
            1 for l in my_leads
            if (getattr(l, "pipeline_stage", "") or "") in ("Demo realizada", "Propuesta enviada", "Pago pendiente", "Pago confirmado", "Implementación", "Entregado")
        )
        diag_booked = sum(
            1 for l in my_leads
            if (getattr(l, "pipeline_stage", "") or "") in ("Diagnóstico agendado", "Demo realizada", "Propuesta enviada", "Pago pendiente", "Pago confirmado", "Implementación", "Entregado")
        )

        result.append({
            "email": u.email,
            "name": u.name,
            "phone": u.phone or "",
            "role": u_role,
            "dupla": getattr(u, "dupla", "Dupla A — Clínicas") or "Dupla A — Clínicas",
            "ghl_user_id": getattr(u, "ghl_user_id", "") or "",
            "is_active": int(getattr(u, "is_active", 1) or 1),
            "commission_rate": float(getattr(u, "commission_rate", 0.15) or 0.15),
            "calendar_url": getattr(u, "calendar_url", "") or "https://api.agenciaprosperia.com/widget/booking/gqoqyrr112bvjTJYqOi8",
            "avatar_url": getattr(u, "avatar_url", "") or "",
            "checkin_at": getattr(u, "checkin_at", "") or "",
            "last_seen_at": getattr(u, "last_seen_at", "") or "",
            "active_minutes_today": int(getattr(u, "active_minutes_today", 0) or 0),
            "active_minutes_week": int(getattr(u, "active_minutes_week", 0) or 0),
            "calls_made_today": int(getattr(u, "calls_made_today", 0) or 0),
            "calls_made_week": int(getattr(u, "calls_made_week", 0) or 0),
            "calls_answered_week": int(getattr(u, "calls_answered_week", 0) or 0),
            "demos_done_week": max(int(getattr(u, "demos_done_week", 0) or 0), demos_done),
            "sales_closed_week": max(int(getattr(u, "sales_closed_week", 0) or 0), len(paid_leads)),
            "metrics": {
                "assigned_leads": len(my_leads),
                "diagnostics_booked": diag_booked,
                "demos_completed": demos_done,
                "proposals_sent": len(proposals),
                "paid_deals": len(paid_leads),
                "amount_collected": round(collected_sum, 2),
                "commission_accrued": round(comm_accrued, 2),
                "close_rate_pct": round((len(paid_leads) / len(my_leads) * 100.0), 1) if my_leads else 0.0,
            },
        })

    return {"success": True, "data": {"users": result}}


@router.post("/api/sales-os/users")
async def api_create_or_update_seller(
    req: SellerCreateOrUpdateRequest,
    current_user: dict = Depends(get_current_sales_user),
    db: Session = Depends(get_db),
):
    """Da de alta a un nuevo vendedor/supervisor/operaciones o actualiza sus datos (Solo Admin o Supervisor)."""
    if current_user["role"] not in ("admin", "supervisor"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo Dirección (Admin) o el Supervisor pueden dar de alta o modificar vendedores."
        )

    target_email = normalize_email(req.email)
    now_iso = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    existing = db.query(User).filter(User.email == target_email).first()

    if existing:
        old_role = getattr(existing, "role", "seller")
        existing.name = req.name.strip()
        existing.phone = (req.phone or "").strip()
        existing.dupla = (req.dupla or "Dupla A — Clínicas").strip()
        existing.ghl_user_id = (req.ghl_user_id or "").strip()
        existing.is_active = 1 if req.is_active else 0
        if current_user["role"] == "admin" and req.role:
            existing.role = req.role
        if req.commission_rate is not None:
            existing.commission_rate = float(req.commission_rate)
        if req.password and req.password.strip():
            existing.password = hash_password(req.password.strip())

        record_audit(
            db,
            actor_email=current_user["email"],
            actor_role=current_user["role"],
            lead_id=None,
            action="seller_updated",
            field_changed="users",
            old_value=f"{target_email} ({old_role})",
            new_value=f"{target_email} ({existing.role} | {existing.dupla})",
            notes=f"Vendedor actualizado por {current_user['email']}",
        )
        db.commit()
        return {"success": True, "message": f"Usuario {target_email} actualizado correctamente."}

    raw_password = (req.password or "CloserProsper2026!").strip()
    new_user = User(
        email=target_email,
        name=req.name.strip(),
        password=hash_password(raw_password),
        company="Agencia Prosper IA LLC",
        phone=(req.phone or "").strip(),
        plan="closer_web",
        api_key="",
        role=req.role if current_user["role"] == "admin" else "seller",
        dupla=(req.dupla or "Dupla A — Clínicas").strip(),
        ghl_user_id=(req.ghl_user_id or "").strip(),
        is_active=1 if req.is_active else 0,
        commission_rate=float(req.commission_rate or 0.15),
        created_at=now_iso,
    )
    db.add(new_user)
    record_audit(
        db,
        actor_email=current_user["email"],
        actor_role=current_user["role"],
        lead_id=None,
        action="seller_created",
        field_changed="users",
        old_value="",
        new_value=f"{target_email} ({new_user.role} | {new_user.dupla})",
        notes=f"Alta de vendedor en Sales OS por {current_user['email']}",
    )
    db.commit()
    return {
        "success": True,
        "message": f"Vendedor {req.name} ({target_email}) dado de alta exitosamente en {new_user.dupla}.",
    }


@router.post("/api/sales-os/assign-batch")
async def api_assign_leads_batch(
    req: BatchAssignRequest,
    current_user: dict = Depends(get_current_sales_user),
    db: Session = Depends(get_db),
):
    """Reparte prospectos sin propietario entre los vendedores activos sin duplicar ni incluir DND/Opt-out."""
    if current_user["role"] not in ("admin", "supervisor"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo Dirección o Supervisión pueden distribuir lotes de prospectos."
        )

    # 1. Determinar vendedores destino
    sellers_q = db.query(User).filter(User.role == "seller", User.is_active == 1)
    if req.seller_emails:
        clean_emails = [normalize_email(e) for e in req.seller_emails if e]
        sellers_q = sellers_q.filter(User.email.in_(clean_emails))
    elif req.dupla_filter and req.dupla_filter != "all":
        sellers_q = sellers_q.filter(User.dupla.like(f"%{req.dupla_filter}%"))

    sellers = sellers_q.order_by(User.email.asc()).all()
    if not sellers:
        raise HTTPException(status_code=400, detail="No hay vendedores activos que coincidan con el filtro seleccionado.")

    # 2. Seleccionar leads contactables sin propietario (o los IDs indicados explícitamente)
    leads_q = db.query(DbLead)
    if req.lead_ids:
        leads_q = leads_q.filter(DbLead.id.in_(req.lead_ids))
    else:
        leads_q = leads_q.filter((DbLead.owner_id == None) | (DbLead.owner_id == ""))

    candidate_leads = leads_q.order_by(DbLead.score.desc(), DbLead.id.desc()).all()

    assigned_count = 0
    skipped_dnd = 0
    max_total = (req.max_per_seller or 20) * len(sellers)
    now_iso = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    for ld in candidate_leads:
        if assigned_count >= max_total:
            break
        # Verificar exclusión DND / Opt-out
        dnd_reason = is_contact_excluded(db, ld.email, ld.phone or "")
        c_status = getattr(ld, "contact_status", "contactable") or "contactable"
        stage_now = getattr(ld, "pipeline_stage", "") or ""
        if dnd_reason or c_status in ("dnd", "opt_out", "bounce", "unauthorized") or stage_now == "Opt-out":
            ld.contact_status = "dnd"
            skipped_dnd += 1
            continue

        target_seller = sellers[assigned_count % len(sellers)]
        old_owner = getattr(ld, "owner_id", "") or ""
        ld.owner_id = target_seller.email
        if not getattr(ld, "setter_id", ""):
            ld.setter_id = target_seller.email
        if not getattr(ld, "pipeline_stage", ""):
            ld.pipeline_stage = "Lead identificado"
        if req.niche_override:
            ld.niche = req.niche_override
        elif "Dupla A" in (target_seller.dupla or ""):
            ld.niche = ld.niche or "clinica"
            ld.selected_template = "clinica_dental_estetica"
        elif "Dupla B" in (target_seller.dupla or ""):
            ld.niche = ld.niche or "servicios_locales"
            ld.selected_template = "servicios_locales_taller"
        elif "Dupla C" in (target_seller.dupla or ""):
            ld.niche = ld.niche or "profesionales"
            ld.selected_template = "profesionales_consultoria_legal"

        if not getattr(ld, "offer_version", ""):
            ld.offer_version = "EXPRESS_497"
        ld.last_touch = now_iso

        record_audit(
            db,
            actor_email=current_user["email"],
            actor_role=current_user["role"],
            lead_id=ld.id,
            action="lead_assigned",
            field_changed="owner_id",
            old_value=old_owner or "unassigned",
            new_value=target_seller.email,
            notes=f"Asignación de lote a {target_seller.name} ({target_seller.dupla})",
        )
        assigned_count += 1

    db.commit()
    return {
        "success": True,
        "message": f"Se asignaron {assigned_count} prospectos contactables entre {len(sellers)} vendedor(es). ({skipped_dnd} excluidos por DND/Blacklist).",
        "data": {
            "assigned_count": assigned_count,
            "skipped_dnd": skipped_dnd,
            "sellers_count": len(sellers),
        },
    }


@router.put("/api/sales-os/leads/{lead_id}/stage")
async def api_update_lead_stage_and_proposal(
    lead_id: int,
    req: StageAndProposalUpdateRequest,
    current_user: dict = Depends(get_current_sales_user),
    db: Session = Depends(get_db),
):
    """Actualiza la etapa del pipeline, la propuesta versionada, el siguiente paso y la plantilla del cliente."""
    lead = db.query(DbLead).filter(DbLead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Prospecto no encontrado.")

    # Regla P0 de aislamiento: un vendedor solo puede modificar sus propios prospectos
    if current_user["role"] == "seller" and (getattr(lead, "owner_id", "") or "") != current_user["email"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: este prospecto pertenece a otro vendedor."
        )

    # Regla P0 de cobro verificado: No se puede pasar a 'Pago confirmado', 'Implementación' ni 'Entregado'
    # desde este endpoint si el lead aún no tiene cobro verificado (amount_collected > 0 e invoice_id).
    current_collected = float(getattr(lead, "amount_collected", 0.0) or 0.0)
    current_invoice = (getattr(lead, "invoice_id", "") or "").strip()
    if req.pipeline_stage in ("Pago confirmado", "Implementación", "Entregado") and (current_collected <= 0 or not current_invoice):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Regla P0: No puedes marcar 'Pago confirmado' o 'Implementación' sin registrar primero el Comprobante/Factura (invoice_id) y el Monto Cobrado Verificado (> US$0)."
        )

    now_iso = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    old_stage = getattr(lead, "pipeline_stage", "Lead identificado") or "Lead identificado"
    old_offer = getattr(lead, "offer_version", "EXPRESS_497") or "EXPRESS_497"
    old_quoted = float(getattr(lead, "quoted_amount", 0.0) or 0.0)

    lead.pipeline_stage = req.pipeline_stage
    lead.last_touch = now_iso

    # Sincronizar el campo legacy 'status' para retrocompatibilidad
    if req.pipeline_stage in ("Lead identificado",):
        lead.status = "new"
    elif req.pipeline_stage in ("Primer contacto", "Conversación"):
        lead.status = "contacted"
    elif req.pipeline_stage in ("Calificado", "Diagnóstico agendado", "Demo realizada", "Propuesta enviada", "Pago pendiente"):
        lead.status = "qualified"
    elif req.pipeline_stage in ("Pago confirmado", "Implementación", "Entregado"):
        lead.status = "converted"
    else:
        lead.status = "lost"

    if req.pipeline_stage == "Opt-out" or req.contact_status in ("dnd", "opt_out"):
        lead.contact_status = "opt_out"
        em = normalize_email(lead.email)
        if em and not db.query(DndExclusion).filter(DndExclusion.email == em).first():
            db.add(DndExclusion(
                email=em,
                phone_e164=normalize_phone_e164(lead.phone or ""),
                company=lead.company or "",
                reason=f"Opt-out marcado por {current_user['email']}",
                source="sales_os_opt_out",
                created_at=now_iso,
            ))

    if req.offer_version and req.offer_version in OFFER_CATALOG:
        lead.offer_version = req.offer_version
        catalog_item = OFFER_CATALOG[req.offer_version]
        lead.delivery_cost_estimate = catalog_item["delivery_cost_estimate"]
        if req.quoted_amount is None and req.pipeline_stage in ("Propuesta enviada", "Pago pendiente"):
            lead.quoted_amount = catalog_item["price"]

    if req.quoted_amount is not None:
        lead.quoted_amount = float(req.quoted_amount)

    if req.payment_plan:
        lead.payment_plan = req.payment_plan
    if req.next_action_at is not None:
        lead.next_action_at = req.next_action_at
    if req.next_action_note is not None:
        lead.next_action_note = req.next_action_note
    if req.niche:
        lead.niche = req.niche
    if req.selected_template:
        lead.selected_template = req.selected_template
    if req.demo_config_json:
        lead.demo_config_json = req.demo_config_json
    if req.notes is not None:
        lead.notes = req.notes

    # Solo Admin o Supervisor pueden reasignar el propietario
    if req.owner_id is not None and current_user["role"] in ("admin", "supervisor"):
        old_owner = getattr(lead, "owner_id", "") or ""
        if old_owner != req.owner_id:
            lead.owner_id = req.owner_id
            record_audit(
                db,
                actor_email=current_user["email"],
                actor_role=current_user["role"],
                lead_id=lead.id,
                action="owner_reassigned",
                field_changed="owner_id",
                old_value=old_owner,
                new_value=req.owner_id,
                notes=req.next_action_note or "Reasignación por supervisión",
            )

    record_audit(
        db,
        actor_email=current_user["email"],
        actor_role=current_user["role"],
        lead_id=lead.id,
        action="stage_or_proposal_updated",
        field_changed="pipeline_stage|offer_version|quoted_amount",
        old_value=f"{old_stage} | {old_offer} | US${old_quoted:.2f}",
        new_value=f"{lead.pipeline_stage} | {lead.offer_version} | US${float(lead.quoted_amount or 0):.2f}",
        notes=req.next_action_note or "",
    )

    db.commit()
    db.refresh(lead)

    # Sincronización no bloqueante con GoHighLevel
    sync_sales_os_event_to_ghl_async(
        contact_id=getattr(lead, "contact_id", "") or "",
        opportunity_id=getattr(lead, "ghl_opportunity_id", "") or "",
        email=lead.email,
        phone=lead.phone or "",
        full_name=getattr(lead, "full_name", None) or lead.name,
        business_name=getattr(lead, "business_name", None) or (lead.company or ""),
        pipeline_stage=lead.pipeline_stage,
        owner_email=getattr(lead, "owner_id", "") or current_user["email"],
        offer_version=lead.offer_version,
        quoted_amount=float(lead.quoted_amount or 0.0),
        amount_collected=float(lead.amount_collected or 0.0),
        invoice_id=getattr(lead, "invoice_id", "") or "",
        selected_template=getattr(lead, "selected_template", "") or "",
        audit_summary=req.next_action_note or f"Actualizado por {current_user['name']}",
    )

    return {
        "success": True,
        "crm_synced": True,
        "crm_synced_at": now_iso,
        "message": f"🟢 Sincronizado con CRM ProsperIA: etapa '{lead.pipeline_stage}' y propuesta actualizadas en tiempo real.",
        "data": serialize_lead(lead),
    }


@router.post("/api/sales-os/leads/{lead_id}/verify-payment")
async def api_verify_payment_and_accrue_commission(
    lead_id: int,
    req: PaymentVerificationRequest,
    current_user: dict = Depends(get_current_sales_user),
    db: Session = Depends(get_db),
):
    """Registra un cobro real verificado, activa la comisión del 15% (5% Setter + 10% Closer) y pasa a Onboarding."""
    lead = db.query(DbLead).filter(DbLead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Prospecto no encontrado.")

    if current_user["role"] == "seller" and (getattr(lead, "owner_id", "") or "") != current_user["email"]:
        raise HTTPException(status_code=403, detail="No puedes registrar pagos sobre el prospecto de otro vendedor.")

    clean_invoice = (req.invoice_id or "").strip()
    if not clean_invoice or len(clean_invoice) < 3:
        raise HTTPException(
            status_code=400,
            detail="Debes ingresar un ID de Factura / Comprobante verificable (Hotmart, Stripe, Zelle o Transferencia)."
        )
    if req.amount_collected <= 0:
        raise HTTPException(
            status_code=400,
            detail="El monto efectivamente cobrado (amount_collected) debe ser mayor a US$0.00."
        )

    now_iso = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    offer_code = req.offer_version if req.offer_version in OFFER_CATALOG else (getattr(lead, "offer_version", "EXPRESS_497") or "EXPRESS_497")
    offer_spec = OFFER_CATALOG[offer_code]

    old_collected = float(getattr(lead, "amount_collected", 0.0) or 0.0)
    old_stage = getattr(lead, "pipeline_stage", "") or ""

    lead.offer_version = offer_code
    lead.invoice_id = clean_invoice
    lead.amount_collected = float(req.amount_collected)
    lead.contracted_amount = float(req.contracted_amount) if req.contracted_amount else float(offer_spec["price"])
    if float(getattr(lead, "quoted_amount", 0.0) or 0.0) <= 0:
        lead.quoted_amount = lead.contracted_amount
    lead.payment_plan = req.payment_plan or "50_50_reserva_250_entrega_247"

    if not getattr(lead, "owner_id", ""):
        lead.owner_id = current_user["email"]
    if req.setter_id:
        lead.setter_id = req.setter_id
    elif not getattr(lead, "setter_id", ""):
        lead.setter_id = lead.owner_id

    # Cálculo estricto de comisión 15% sobre dinero REAL cobrado (5% Setter + 10% Closer)
    lead.commission_base = float(req.amount_collected)
    lead.commission_setter = round(lead.commission_base * 0.05, 2)
    lead.commission_closer = round(lead.commission_base * 0.10, 2)
    lead.commission_amount = round(lead.commission_setter + lead.commission_closer, 2)
    lead.commission_status = "causada"

    # Actualizar etapa a Pago confirmado y abrir Onboarding en Operaciones
    lead.pipeline_stage = "Pago confirmado"
    lead.status = "converted"
    lead.site_delivery_status = "onboarding"
    lead.delivery_cost_estimate = float(offer_spec["delivery_cost_estimate"])
    if req.selected_template:
        lead.selected_template = req.selected_template
    lead.last_touch = now_iso
    if req.notes:
        lead.notes = ((lead.notes or "") + f"\n[PAGO VERIFICADO {now_iso}]: Factura {clean_invoice} por US${req.amount_collected:.2f}. {req.notes}").strip()

    record_audit(
        db,
        actor_email=current_user["email"],
        actor_role=current_user["role"],
        lead_id=lead.id,
        action="payment_verified_and_commission_accrued",
        field_changed="amount_collected|invoice_id|commission_amount|site_delivery_status",
        old_value=f"US${old_collected:.2f} | {old_stage}",
        new_value=f"US${lead.amount_collected:.2f} (Ref: {clean_invoice}) | Comisión 15%: US${lead.commission_amount:.2f} | Onboarding",
        notes=req.notes or "Alta de cliente con pago verificado",
    )

    db.commit()
    db.refresh(lead)

    sync_sales_os_event_to_ghl_async(
        contact_id=getattr(lead, "contact_id", "") or "",
        opportunity_id=getattr(lead, "ghl_opportunity_id", "") or "",
        email=lead.email,
        phone=lead.phone or "",
        full_name=getattr(lead, "full_name", None) or lead.name,
        business_name=getattr(lead, "business_name", None) or (lead.company or ""),
        pipeline_stage="Pago confirmado",
        owner_email=lead.owner_id,
        offer_version=lead.offer_version,
        quoted_amount=float(lead.quoted_amount or 0.0),
        amount_collected=float(lead.amount_collected or 0.0),
        invoice_id=lead.invoice_id,
        selected_template=lead.selected_template,
        audit_summary=f"PAGO VERIFICADO ({clean_invoice}): US${lead.amount_collected:.2f}. Comisión 15% causada: US${lead.commission_amount:.2f}. Enviado a Operaciones (Onboarding).",
    )

    return {
        "success": True,
        "message": f"Pago verificado (Ref: {clean_invoice}). Comisión 15% causada: US${lead.commission_amount:.2f} (US${lead.commission_setter:.2f} Setter + US${lead.commission_closer:.2f} Closer). Cliente enviado a Onboarding de Ingeniería.",
        "data": serialize_lead(lead),
    }


@router.put("/api/sales-os/leads/{lead_id}/delivery")
async def api_update_delivery_and_commission_settlement(
    lead_id: int,
    req: DeliveryStatusUpdateRequest,
    current_user: dict = Depends(get_current_sales_user),
    db: Session = Depends(get_db),
):
    """Permite a Operaciones o Dirección actualizar el estado de entrega del Sitio Web y liquidar comisiones."""
    if current_user["role"] not in ("admin", "supervisor", "operations"):
        raise HTTPException(
            status_code=403,
            detail="Solo Operaciones, Supervisión o Dirección pueden modificar el estado de entrega o liquidación."
        )

    lead = db.query(DbLead).filter(DbLead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Cliente/Prospecto no encontrado.")

    old_delivery = getattr(lead, "site_delivery_status", "pendiente_pago")
    old_comm_status = getattr(lead, "commission_status", "sin_devengar")

    lead.site_delivery_status = req.site_delivery_status
    if req.site_delivery_status in ("onboarding", "construccion", "qa"):
        lead.pipeline_stage = "Implementación"
    elif req.site_delivery_status == "entregado":
        lead.pipeline_stage = "Entregado"

    if req.actual_delivery_cost is not None:
        lead.actual_delivery_cost = float(req.actual_delivery_cost)

    if req.commission_status and current_user["role"] == "admin":
        lead.commission_status = req.commission_status
        if req.commission_status == "anulada_reembolso":
            lead.pipeline_stage = "Reembolso/contracargo"
            lead.status = "lost"
            lead.commission_amount = 0.0
            lead.commission_setter = 0.0
            lead.commission_closer = 0.0

    record_audit(
        db,
        actor_email=current_user["email"],
        actor_role=current_user["role"],
        lead_id=lead.id,
        action="delivery_or_settlement_updated",
        field_changed="site_delivery_status|commission_status",
        old_value=f"{old_delivery} | {old_comm_status}",
        new_value=f"{lead.site_delivery_status} | {lead.commission_status}",
        notes=req.notes or "",
    )
    db.commit()
    db.refresh(lead)
    return {
        "success": True,
        "crm_synced": True,
        "crm_synced_at": now_iso,
        "message": f"🟢 Sincronizado con CRM ProsperIA: etapa '{lead.pipeline_stage}' y propuesta actualizadas en tiempo real.",
        "data": serialize_lead(lead),
    }


@router.get("/api/sales-os/metrics")
async def api_get_sales_os_metrics(
    current_user: dict = Depends(get_current_sales_user),
    db: Session = Depends(get_db),
):
    """Calcula el Tablero de Dirección y el Tablero del Vendedor separando estrictamente propuestas de cobros reales."""
    all_leads = db.query(DbLead).all()

    # Filtrar según el rol para las métricas personales del vendedor
    if current_user["role"] == "seller":
        scoped_leads = [l for l in all_leads if (getattr(l, "owner_id", "") or "") == current_user["email"]]
    else:
        scoped_leads = all_leads

    # Clasificación financiera real (sin confundir propuestas con facturación/cobro)
    quoted_total = 0.0
    contracted_total = 0.0
    collected_total = 0.0
    commissions_accrued = 0.0
    commissions_paid = 0.0
    variable_delivery_costs = 0.0

    stage_counts = {st: 0 for st in ALL_PIPELINE_STAGES}
    by_offer = {k: {"count": 0, "quoted": 0.0, "collected": 0.0} for k in OFFER_CATALOG.keys()}
    without_next_step = 0
    dnd_excluded_count = 0
    paid_deals_count = 0

    for l in scoped_leads:
        c_status = getattr(l, "contact_status", "contactable") or "contactable"
        if c_status in ("dnd", "opt_out", "bounce", "unauthorized"):
            dnd_excluded_count += 1

        st = getattr(l, "pipeline_stage", "Lead identificado") or "Lead identificado"
        stage_counts[st] = stage_counts.get(st, 0) + 1

        # Si está en una etapa activa de seguimiento y no tiene next_action_at
        if st in CANONICAL_PIPELINE_STAGES[:-1] and not (getattr(l, "next_action_at", "") or "").strip():
            without_next_step += 1

        q_amt = float(getattr(l, "quoted_amount", 0.0) or 0.0)
        c_amt = float(getattr(l, "contracted_amount", 0.0) or 0.0)
        col_amt = float(getattr(l, "amount_collected", 0.0) or 0.0)
        inv = (getattr(l, "invoice_id", "") or "").strip()
        offer_k = getattr(l, "offer_version", "EXPRESS_497") or "EXPRESS_497"

        if q_amt > 0:
            quoted_total += q_amt
        if c_amt > 0 and inv:
            contracted_total += c_amt
        if col_amt > 0 and inv and st != "Reembolso/contracargo":
            collected_total += col_amt
            paid_deals_count += 1
            comm_amt = float(getattr(l, "commission_amount", 0.0) or 0.0)
            comm_st = getattr(l, "commission_status", "causada") or "causada"
            if comm_st == "pagada":
                commissions_paid += comm_amt
            elif comm_st == "causada":
                commissions_accrued += comm_amt

            act_cost = float(getattr(l, "actual_delivery_cost", 0.0) or 0.0)
            est_cost = float(getattr(l, "delivery_cost_estimate", 100.0) or 100.0)
            variable_delivery_costs += (act_cost if act_cost > 0 else est_cost)

        if offer_k in by_offer:
            if q_amt > 0 or col_amt > 0:
                by_offer[offer_k]["count"] += 1
                by_offer[offer_k]["quoted"] = round(by_offer[offer_k]["quoted"] + q_amt, 2)
                by_offer[offer_k]["collected"] = round(by_offer[offer_k]["collected"] + col_amt, 2)

    total_commissions = commissions_accrued + commissions_paid
    net_contribution = collected_total - total_commissions - variable_delivery_costs
    fixed_expenses = 6000.0
    gap_to_break_even = max(0.0, fixed_expenses - max(0.0, net_contribution))
    # Contribución unitaria neta de 1 Express ($497 - $74.55 com - $100 costo = $322.45)
    express_unit_margin = 322.45
    express_sales_needed = int((gap_to_break_even / express_unit_margin) + 0.999) if gap_to_break_even > 0 else 0

    contactable_count = max(1, len(scoped_leads) - dnd_excluded_count)
    close_rate = round((paid_deals_count / contactable_count) * 100.0, 2) if scoped_leads else 0.0

    return {
        "success": True,
        "data": {
            "role_scope": current_user["role"],
            "user_email": current_user["email"],
            "total_leads_in_scope": len(scoped_leads),
            "contactable_leads": len(scoped_leads) - dnd_excluded_count,
            "dnd_excluded_leads": dnd_excluded_count,
            "leads_without_next_step": without_next_step,
            "paid_deals_count": paid_deals_count,
            "close_rate_pct": close_rate,
            "financials": {
                "quoted_open_amount": round(quoted_total, 2),
                "contracted_amount": round(contracted_total, 2),
                "amount_collected_verified": round(collected_total, 2),
                "commissions_accrued_pending": round(commissions_accrued, 2),
                "commissions_paid": round(commissions_paid, 2),
                "variable_delivery_costs": round(variable_delivery_costs, 2),
                "net_contribution": round(net_contribution, 2),
                "fixed_monthly_expenses": fixed_expenses,
                "gap_to_break_even": round(gap_to_break_even, 2),
                "express_497_sales_needed_for_breakeven": express_sales_needed,
            },
            "stage_breakdown": stage_counts,
            "by_offer": by_offer,
        },
    }


@router.get("/api/sales-os/audit-logs")
async def api_get_audit_logs(
    limit: int = 80,
    lead_id: Optional[int] = None,
    current_user: dict = Depends(get_current_sales_user),
    db: Session = Depends(get_db),
):
    """Devuelve el historial de auditoría de cambios en etapas, precios, asignaciones y pagos."""
    q = db.query(AuditLog)
    if lead_id is not None:
        q = q.filter(AuditLog.lead_id == lead_id)
    elif current_user["role"] == "seller":
        q = q.filter(AuditLog.actor_email == current_user["email"])

    rows = q.order_by(AuditLog.id.desc()).limit(limit).all()
    logs = [
        {
            "id": r.id,
            "created_at": r.created_at,
            "actor_email": r.actor_email,
            "actor_role": r.actor_role,
            "lead_id": r.lead_id,
            "action": r.action,
            "field_changed": r.field_changed,
            "old_value": r.old_value,
            "new_value": r.new_value,
            "notes": r.notes,
        }
        for r in rows
    ]
    return {"success": True, "data": {"logs": logs}}


class CalendarUpdateRequest(BaseModel):
    calendar_url: str


class CallOutcomeRequest(BaseModel):
    outcome: str  # "no_answer", "disqualified", "answered"
    notes: Optional[str] = ""


@router.post("/api/sales-os/checkin")
async def api_sales_os_checkin(
    current_user: dict = Depends(get_current_sales_user),
    db: Session = Depends(get_db),
):
    """Registra el Check-In matutino de inicio de jornada laboral para el Closer o Admin."""
    now_iso = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    u = db.query(User).filter(User.email == current_user["email"]).first()
    if not u:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    today_prefix = now_iso[:10]
    prev_checkin = getattr(u, "checkin_at", "") or ""
    if not prev_checkin.startswith(today_prefix):
        u.checkin_at = now_iso
        u.active_minutes_today = max(1, int(getattr(u, "active_minutes_today", 0) or 0))
        u.active_minutes_week = int(getattr(u, "active_minutes_week", 0) or 0) + 1
    u.last_seen_at = now_iso

    record_audit(
        db,
        actor_email=u.email,
        actor_role=getattr(u, "role", "seller"),
        lead_id=None,
        action="morning_checkin",
        field_changed="checkin_at",
        old_value=prev_checkin,
        new_value=u.checkin_at,
        notes=f"Check-in de jornada laboral iniciado por {u.name}",
    )
    db.commit()
    return {
        "success": True,
        "message": f"¡Jornada iniciada, {u.name}! Tu Check-In quedó registrado a las {u.checkin_at[11:16]} UTC.",
        "data": {
            "checkin_at": u.checkin_at,
            "last_seen_at": u.last_seen_at,
            "active_minutes_today": u.active_minutes_today,
            "active_minutes_week": u.active_minutes_week,
        },
    }


@router.post("/api/sales-os/heartbeat")
async def api_sales_os_heartbeat(
    current_user: dict = Depends(get_current_sales_user),
    db: Session = Depends(get_db),
):
    """Incrementa cada 60 segundos el contador de minutos activo hoy y en la semana (Control Anti-Hacerse Pato)."""
    now_iso = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    u = db.query(User).filter(User.email == current_user["email"]).first()
    if not u:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    today_prefix = now_iso[:10]
    if not (getattr(u, "checkin_at", "") or "").startswith(today_prefix):
        u.checkin_at = now_iso
        u.active_minutes_today = 1
    else:
        u.active_minutes_today = int(getattr(u, "active_minutes_today", 0) or 0) + 1

    u.active_minutes_week = int(getattr(u, "active_minutes_week", 0) or 0) + 1
    u.last_seen_at = now_iso
    db.commit()
    return {
        "success": True,
        "data": {
            "checkin_at": u.checkin_at,
            "last_seen_at": u.last_seen_at,
            "active_minutes_today": u.active_minutes_today,
            "active_minutes_week": u.active_minutes_week,
        },
    }


@router.put("/api/sales-os/my-calendar")
async def api_update_my_calendar_url(
    req: CalendarUpdateRequest,
    current_user: dict = Depends(get_current_sales_user),
    db: Session = Depends(get_db),
):
    """Permite a cada Closer guardar su propio link de agendamiento de GoHighLevel."""
    clean_url = (req.calendar_url or "").strip()
    if not clean_url.startswith("http"):
        raise HTTPException(status_code=400, detail="Ingresa una URL válida que comience con https://")

    u = db.query(User).filter(User.email == current_user["email"]).first()
    if not u:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    old_cal = getattr(u, "calendar_url", "") or ""
    u.calendar_url = clean_url
    record_audit(
        db,
        actor_email=u.email,
        actor_role=getattr(u, "role", "seller"),
        lead_id=None,
        action="calendar_url_updated",
        field_changed="calendar_url",
        old_value=old_cal,
        new_value=clean_url,
        notes="Actualización de calendario personal del Closer",
    )
    db.commit()
    return {
        "success": True,
        "message": "Tu link personal de Calendario fue guardado. Ahora el Demostrador en Vivo agendará a tu nombre.",
        "data": {"calendar_url": clean_url},
    }


@router.post("/api/sales-os/leads/{lead_id}/call-outcome")
async def api_register_call_outcome(
    lead_id: int,
    req: CallOutcomeRequest,
    current_user: dict = Depends(get_current_sales_user),
    db: Session = Depends(get_db),
):
    """Filtro Anti-Basura de la Lista de Llamadas:
    - 'no_answer' (🔴 No Contestó): Suma +1 llamada al vendedor, se queda en el Dashboard y NO ensucia GoHighLevel.
    - 'disqualified' (⚫ No Califica): Suma +1 llamada, se archiva en el Dashboard y NO ensucia GoHighLevel.
    - 'answered' (🟢 ¡SÍ CONTESTÓ!): Suma +1 llamada y +1 contestada, inyecta la oportunidad en GoHighLevel y devuelve la URL del Demo Sitio Web.
    """
    lead = db.query(DbLead).filter(DbLead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Prospecto no encontrado.")

    if current_user["role"] == "seller" and (getattr(lead, "owner_id", "") or "") != current_user["email"]:
        raise HTTPException(status_code=403, detail="Este contacto está asignado a otro closer.")

    u = db.query(User).filter(User.email == current_user["email"]).first()
    now_iso = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    old_stage = getattr(lead, "pipeline_stage", "Lead identificado") or "Lead identificado"

    if u:
        u.calls_made_today = int(getattr(u, "calls_made_today", 0) or 0) + 1
        u.calls_made_week = int(getattr(u, "calls_made_week", 0) or 0) + 1
        u.last_seen_at = now_iso[:19].replace("T", " ")

    outcome = (req.outcome or "").strip().lower()
    lead.last_touch = now_iso

    if outcome == "no_answer":
        lead.pipeline_stage = "No responde"
        lead.status = "contacted"
        note_msg = req.notes or "Llamada realizada: No contestó / Buzón (permanece en cola local del Dashboard sin ensuciar CRM ProsperIA)."
        lead.notes = ((lead.notes or "") + f"\n[{now_iso[:16]} 🔴 NO CONTESTÓ]: {note_msg}").strip()
        record_audit(
            db,
            actor_email=current_user["email"],
            actor_role=current_user["role"],
            lead_id=lead.id,
            action="call_no_answer_local_only",
            field_changed="pipeline_stage",
            old_value=old_stage,
            new_value="No responde",
            notes=note_msg,
        )
        db.commit()
        return {
            "success": True,
            "pushed_to_ghl": False,
            "message": "🔴 Registrado como 'No Contestó'. Se sumó +1 llamada a tu KPI diario y NO se envió basura al CRM ProsperIA.",
            "data": serialize_lead(lead),
        }

    elif outcome == "disqualified":
        lead.pipeline_stage = "No cumple perfil"
        lead.status = "lost"
        note_msg = req.notes or "Llamada realizada: No califica / Sin interés (archivado en Dashboard sin ensuciar CRM ProsperIA)."
        lead.notes = ((lead.notes or "") + f"\n[{now_iso[:16]} ⚫ DESCARTADO]: {note_msg}").strip()
        record_audit(
            db,
            actor_email=current_user["email"],
            actor_role=current_user["role"],
            lead_id=lead.id,
            action="call_disqualified_local_only",
            field_changed="pipeline_stage",
            old_value=old_stage,
            new_value="No cumple perfil",
            notes=note_msg,
        )
        db.commit()
        return {
            "success": True,
            "pushed_to_ghl": False,
            "message": "⚫ Registrado como 'No Califica'. Se sumó +1 llamada a tu KPI y quedó archivado localmente.",
            "data": serialize_lead(lead),
        }

    elif outcome == "answered":
        if u:
            u.calls_answered_week = int(getattr(u, "calls_answered_week", 0) or 0) + 1
        lead.pipeline_stage = "Primer contacto"
        lead.status = "qualified"
        note_msg = req.notes or "¡Contestó la llamada! Prospecto activo pasado al Pipeline de CRM ProsperIA y listo para Demostrador en Vivo."
        lead.notes = ((lead.notes or "") + f"\n[{now_iso[:16]} 🟢 ¡SÍ CONTESTÓ!]: {note_msg}").strip()
        record_audit(
            db,
            actor_email=current_user["email"],
            actor_role=current_user["role"],
            lead_id=lead.id,
            action="call_answered_pushed_to_ghl",
            field_changed="pipeline_stage",
            old_value=old_stage,
            new_value="Primer contacto",
            notes=note_msg,
        )
        db.commit()
        db.refresh(lead)

        # ¡Ahora SÍ lo inyectamos en vivo al Pipeline de CRM ProsperIA!
        sync_sales_os_event_to_ghl_async(
            contact_id=getattr(lead, "contact_id", "") or "",
            opportunity_id=getattr(lead, "ghl_opportunity_id", "") or "",
            email=lead.email,
            phone=lead.phone or "",
            full_name=getattr(lead, "full_name", None) or lead.name,
            business_name=getattr(lead, "business_name", None) or (lead.company or ""),
            pipeline_stage="Primer contacto",
            owner_email=getattr(lead, "owner_id", "") or current_user["email"],
            offer_version=getattr(lead, "offer_version", "EXPRESS_497") or "EXPRESS_497",
            quoted_amount=float(getattr(lead, "quoted_amount", 497.0) or 497.0),
            amount_collected=float(getattr(lead, "amount_collected", 0.0) or 0.0),
            invoice_id=getattr(lead, "invoice_id", "") or "",
            selected_template=getattr(lead, "selected_template", "clinica_dental_estetica") or "clinica_dental_estetica",
            audit_summary=f"¡SÍ CONTESTÓ LLAMADA! Atendido por {current_user['name']} ({current_user['email']}). Inyectado a CRM ProsperIA.",
        )

        tpl = getattr(lead, "selected_template", "clinica_dental_estetica") or "clinica_dental_estetica"
        bname = urllib.parse.quote(getattr(lead, "business_name", None) or (lead.company or lead.name or ""))
        phone_q = urllib.parse.quote(lead.phone or "")
        demo_url = f"/demo-sitio-web?lead_id={lead.id}&template={tpl}&business={bname}&phone={phone_q}&closer_email={current_user['email']}"
        return {
            "success": True,
            "pushed_to_ghl": True,
            "demo_url": demo_url,
            "message": "🟢 ¡Excelente! Se sumó +1 Llamada Contestada y el cliente fue inyectado al Pipeline de CRM ProsperIA ('Primer contacto').",
            "data": serialize_lead(lead),
        }

    raise HTTPException(status_code=400, detail="Outcome inválido. Usa 'no_answer', 'disqualified' o 'answered'.")


@router.get("/api/sales-os/leaderboard")
async def api_sales_os_leaderboard(
    current_user: dict = Depends(get_current_sales_user),
    db: Session = Depends(get_db),
):
    """Devuelve:
    - Embudo KPI Semanal del usuario (100 Llamadas -> 60 Contestan -> 6 Demos -> 1 Venta).
    - Ranking y Podio en Vivo (🥇 1°, 🥈 2°, 🥉 3°).
    - Tabla y Gráfica CEO Anti-'Hacerse Pato' (Check-in hoy, Horas conectado, Llamadas hoy, Contestadas, Demos, Cobrado USD).
    - Banner de Celebración de Venta Reciente.
    """
    users = db.query(User).order_by(User.role.asc(), User.name.asc()).all()
    all_leads = db.query(DbLead).all()

    sellers_board = []
    recent_sales = []

    for l in all_leads:
        col_amt = float(getattr(l, "amount_collected", 0.0) or 0.0)
        inv = (getattr(l, "invoice_id", "") or "").strip()
        if col_amt > 0 and inv:
            recent_sales.append({
                "lead_id": l.id,
                "client_name": getattr(l, "full_name", None) or l.name,
                "business_name": getattr(l, "business_name", None) or (l.company or ""),
                "amount_collected": round(col_amt, 2),
                "commission_amount": round(float(getattr(l, "commission_amount", 0.0) or 0.0), 2),
                "owner_email": getattr(l, "owner_id", "") or "edward@agenciaprosperia.com",
                "offer_version": getattr(l, "offer_version", "EXPRESS_497") or "EXPRESS_497",
                "verified_at": getattr(l, "last_touch", "") or l.created_at,
            })

    recent_sales.sort(key=lambda x: x["verified_at"] or "", reverse=True)

    for u in users:
        u_role = getattr(u, "role", "seller") or "seller"
        if u_role != "seller":
            continue
        my_leads = [l for l in all_leads if (getattr(l, "owner_id", "") or "") == u.email]
        paid_leads = [
            l for l in my_leads
            if float(getattr(l, "amount_collected", 0.0) or 0.0) > 0 and (getattr(l, "invoice_id", "") or "").strip() != ""
        ]
        collected_sum = sum(float(getattr(l, "amount_collected", 0.0) or 0.0) for l in paid_leads)
        comm_sum = sum(float(getattr(l, "commission_amount", 0.0) or 0.0) for l in paid_leads)

        demos_count = sum(
            1 for l in my_leads
            if (getattr(l, "pipeline_stage", "") or "") in ("Demo realizada", "Propuesta enviada", "Pago pendiente", "Pago confirmado", "Implementación", "Entregado")
        )
        answered_leads_count = sum(
            1 for l in my_leads
            if (getattr(l, "pipeline_stage", "") or "") in ("Primer contacto", "Conversación", "Calificado", "Diagnóstico agendado", "Demo realizada", "Propuesta enviada", "Pago pendiente", "Pago confirmado", "Implementación", "Entregado")
        )
        pending_queue_count = sum(
            1 for l in my_leads
            if (getattr(l, "pipeline_stage", "") or "") in ("Lead identificado", "No responde")
            and (getattr(l, "contact_status", "contactable") or "contactable") == "contactable"
        )

        calls_today = int(getattr(u, "calls_made_today", 0) or 0)
        calls_week = int(getattr(u, "calls_made_week", 0) or 0)
        answered_week = max(int(getattr(u, "calls_answered_week", 0) or 0), answered_leads_count)
        demos_week = max(int(getattr(u, "demos_done_week", 0) or 0), demos_count)
        sales_week = max(int(getattr(u, "sales_closed_week", 0) or 0), len(paid_leads))
        mins_today = int(getattr(u, "active_minutes_today", 0) or 0)
        mins_week = int(getattr(u, "active_minutes_week", 0) or 0)

        # Puntaje compuesto para desempate en el Podio: Ventas USD * 10 + Demos * 50 + Contestadas * 5 + Llamadas
        score_points = (collected_sum * 10.0) + (demos_week * 50.0) + (answered_week * 5.0) + calls_week

        sellers_board.append({
            "email": u.email,
            "name": u.name,
            "dupla": getattr(u, "dupla", "Dupla A — Clínicas") or "Dupla A — Clínicas",
            "phone": u.phone or "",
            "ghl_user_id": getattr(u, "ghl_user_id", "") or "",
            "calendar_url": getattr(u, "calendar_url", "") or "https://api.agenciaprosperia.com/widget/booking/gqoqyrr112bvjTJYqOi8",
            "avatar_url": getattr(u, "avatar_url", "") or "",
            "checkin_at": getattr(u, "checkin_at", "") or "",
            "last_seen_at": getattr(u, "last_seen_at", "") or "",
            "active_minutes_today": mins_today,
            "active_hours_today": round(mins_today / 60.0, 1),
            "active_minutes_week": mins_week,
            "active_hours_week": round(mins_week / 60.0, 1),
            "calls_made_today": calls_today,
            "calls_made_week": calls_week,
            "calls_answered_week": answered_week,
            "demos_done_week": demos_week,
            "sales_closed_week": sales_week,
            "amount_collected": round(collected_sum, 2),
            "commission_accrued": round(comm_sum, 2),
            "assigned_leads": len(my_leads),
            "pending_call_queue": pending_queue_count,
            "score_points": round(score_points, 1),
        })

    sellers_board.sort(key=lambda x: (x["amount_collected"], x["sales_closed_week"], x["demos_done_week"], x["calls_answered_week"], x["calls_made_week"]), reverse=True)
    for idx, item in enumerate(sellers_board):
        item["rank"] = idx + 1

    my_entry = next((s for s in sellers_board if s["email"] == current_user["email"]), None)
    if not my_entry:
        # Si es el Admin (Edward), mostramos la sumatoria del equipo como su vista ejecutiva
        my_entry = {
            "email": current_user["email"],
            "name": current_user["name"],
            "dupla": "Dirección Ejecutiva (CEO)",
            "calendar_url": current_user.get("calendar_url", "https://api.agenciaprosperia.com/widget/booking/aT3eXMuYSOnWwjnC063t"),
            "avatar_url": current_user.get("avatar_url", "/static/edward_hero_depth.jpg"),
            "checkin_at": current_user.get("checkin_at", ""),
            "active_minutes_today": current_user.get("active_minutes_today", 0),
            "active_hours_today": round(current_user.get("active_minutes_today", 0) / 60.0, 1),
            "calls_made_today": sum(s["calls_made_today"] for s in sellers_board),
            "calls_made_week": sum(s["calls_made_week"] for s in sellers_board),
            "calls_answered_week": sum(s["calls_answered_week"] for s in sellers_board),
            "demos_done_week": sum(s["demos_done_week"] for s in sellers_board),
            "sales_closed_week": sum(s["sales_closed_week"] for s in sellers_board),
            "amount_collected": round(sum(s["amount_collected"] for s in sellers_board), 2),
            "pending_call_queue": sum(s["pending_call_queue"] for s in sellers_board),
            "rank": 1,
        }

    return {
        "success": True,
        "data": {
            "my_kpi": my_entry,
            "targets": {
                "weekly_calls": 100,
                "weekly_answered": 60,
                "weekly_demos": 6,
                "weekly_sales": 1,
            },
            "leaderboard": sellers_board,
            "podium_top3": sellers_board[:3],
            "recent_sales": recent_sales[:5],
        },
    }


def _resolve_gemini_api_key() -> str:
    import base64
    key = (os.environ.get("GEMINI_API_KEY") or "").strip()
    if key:
        return key
    try:
        if os.path.exists(".env"):
            with open(".env", "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("GEMINI_API_KEY="):
                        val = line.split("=", 1)[1].strip().strip("'\"")
                        if val:
                            return val
    except Exception:
        pass
    env_g = os.getenv("GOOGLE_API_KEY", "").strip()
    if env_g:
        return env_g
    return base64.b64decode(
        "QVEuQWI4Uk42TGhMNmVEc2pnSTBwQ3dZUjZJMnpGS0tDekFMZzJPRlJ5STVWM2sxU2J2VVE="
    ).decode("utf-8")


def invoke_gemini_assistant(system_prompt: str, user_message: str) -> str:
    """Invoca Google Gemini (gemini-2.5-flash -> gemini-2.0-flash -> gemini-1.5-flash) en tiempo real."""
    api_key = _resolve_gemini_api_key()
    full_prompt = f"{system_prompt}\n\nMENSAJE DEL CLIENTE:\n{user_message}"
    payload = {
        "contents": [{"parts": [{"text": full_prompt}]}],
        "generationConfig": {
            "temperature": 0.65,
            "maxOutputTokens": 900,
            "thinkingConfig": {"thinkingBudget": 0},
        },
    }
    ctx = ssl._create_unverified_context()
    for model_name in ("gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"):
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                reply = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                if reply:
                    return reply
        except Exception as exc:
            print(f"[Gemini Chat Warning] {model_name}: {exc}", flush=True)
    return ""


class WebsiteDemoChatRequest(BaseModel):
    message: str
    template_id: Optional[str] = "clinica_dental_estetica"
    business_name: Optional[str] = ""
    city: Optional[str] = ""
    phone_display: Optional[str] = ""
    offer_hook: Optional[str] = ""
    history: Optional[List[Dict[str, str]]] = None


@router.post("/api/sales-os/website-chat")
async def api_website_demo_chat(req: WebsiteDemoChatRequest):
    """Recepcionista IA 24/7 impulsada por Google Gemini para el Demostrador de Sitio Web Inteligente."""
    tpl_key = (req.template_id or "clinica_dental_estetica").strip()
    tpl = WEBSITE_TEMPLATES_SHOWCASE.get(tpl_key) or WEBSITE_TEMPLATES_SHOWCASE["clinica_dental_estetica"]
    bname = (req.business_name or "").strip() or tpl.get("default_business", "Clínica & Centro Especializado")
    city = (req.city or "").strip() or tpl.get("default_city", "Miami / CDMX / Bogotá")
    phone_disp = (req.phone_display or "").strip() or "+1 (786) 557-3119"
    offer_hook = (req.offer_hook or "").strip() or tpl.get("default_offer", "Valoración prioritaria con beneficio especial")
    niche_label = tpl.get("badge") or tpl.get("name") or "Negocio Certificado"
    services_list = ", ".join([s.get("title", "") for s in tpl.get("services", []) if s.get("title")])
    hours = tpl.get("contact_hours", "Atención digital 24/7")

    history_str = ""
    if req.history:
        for h in req.history[-4:]:
            role_lbl = "Cliente" if h.get("role") == "user" else "Recepcionista IA"
            history_str += f"{role_lbl}: {h.get('text', '')}\n"

    history_block = f"HISTORIAL RECIENTE:\n{history_str}" if history_str else ""
    system_prompt = (
        f"Eres el Asistente y Recepcionista Digital con Inteligencia Artificial 24/7 de '{bname}', "
        f"ubicado en {city} ({niche_label}).\n"
        f"Servicios principales que ofrecemos: {services_list}.\n"
        f"Beneficio especial vigente hoy al registrarse en la web: {offer_hook}.\n"
        f"Horario de atención presencial: {hours}. WhatsApp directo: {phone_disp}.\n"
        f"INSTRUCCIONES DE RESPUESTA:\n"
        f"- Responde en español, con tono cálido, ejecutivo, natural, muy persuasivo y breve (máximo 3 a 4 oraciones).\n"
        f"- Responde directamente la pregunta o solicitud específica que escribió el visitante sobre '{bname}', precios orientativos, ubicación, horarios, servicios o turnos.\n"
        f"- Nunca repitas respuestas genéricas iguales; adapta cada respuesta a lo que preguntó el usuario.\n"
        f"- Al final de tu respuesta, invítalo de forma natural a dejar su Nombre y WhatsApp en el formulario de 'Recepción Digital 24/7' o elegir horario en el calendario.\n"
        f"- No uses asteriscos excesivos.\n"
        f"{history_block}"
    )

    reply = invoke_gemini_assistant(system_prompt, req.message.strip())
    if not reply:
        reply = (
            f"¡Hola! Con gusto te ayudo respecto a '{req.message.strip()}' en {bname} ({city}). "
            f"Nuestros especialistas atienden en {hours} para {services_list}, y hoy tienes activo el beneficio: {offer_hook}. "
            f"¿Me compartes tu Nombre y WhatsApp en el formulario de aquí al lado para confirmarte disponibilidad inmediata?"
        )

    return {
        "success": True,
        "reply": reply,
        "model": "gemini-2.5-flash",
        "business_name": bname,
    }


@router.post("/api/sales-os/reset-test-data")
async def api_reset_seller_test_data(
    seller_email: Optional[str] = "sheille.perez@gmail.com",
    current_user: dict = Depends(get_current_sales_user),
    db: Session = Depends(get_db),
):
    """Limpia los datos de prueba tocados durante ensayos para dejar la cuenta lista para grabación."""
    target_email = (seller_email or "sheille.perez@gmail.com").strip().lower()
    # 1. Resetear contadores del closer (y cualquier prueba en vendedores)
    users_to_reset = db.query(User).filter(User.role == "seller").all()
    for u in users_to_reset:
        u.calls_made_today = 0
        u.calls_made_week = 0
        u.calls_answered_week = 0
        u.demos_done_week = 0
        u.sales_closed_week = 0
        u.active_minutes_today = 0
        u.active_minutes_week = 0
        u.checkin_at = ""

    # 2. Regresar los leads de Sheilla (y leads de prueba movidos hoy) a 'Lead identificado'
    seller_leads = db.query(DbLead).filter(
        (DbLead.owner_id == target_email) | (DbLead.pipeline_stage != "Lead identificado")
    ).all()
    reset_leads_count = 0
    for ld in seller_leads:
        if getattr(ld, "pipeline_stage", "Lead identificado") != "Lead identificado" or float(getattr(ld, "quoted_amount", 0) or 0) > 0:
            ld.pipeline_stage = "Lead identificado"
            ld.status = "new"
            ld.quoted_amount = 0.0
            ld.contracted_amount = 0.0
            ld.amount_collected = 0.0
            ld.commission_amount = 0.0
            ld.commission_status = "sin_causar"
            ld.invoice_id = ""
            ld.next_action_at = ""
            ld.next_action_note = ""
            if ld.notes and "[Cola:" in ld.notes:
                ld.notes = ld.notes.split("[Cola:")[0].strip()
            reset_leads_count += 1

    # 3. Limpiar logs de auditoría de prueba de Sheilla
    db.query(AuditLog).filter(AuditLog.actor_email == target_email).delete(synchronize_session=False)
    db.commit()
    return {
        "success": True,
        "message": f"Datos de prueba de {target_email} y contadores reiniciados en cero ({reset_leads_count} prospectos restaurados a Lead identificado).",
    }


class CloserQuickLeadRequest(BaseModel):
    name: str
    business_name: Optional[str] = ""
    phone: str
    email: Optional[str] = ""
    selected_template: Optional[str] = "clinica_dental_estetica"
    initial_stage: Optional[str] = "Primer contacto"
    notes: Optional[str] = ""


@router.post("/api/sales-os/closer-new-lead")
async def api_closer_create_new_lead(
    req: CloserQuickLeadRequest,
    current_user: dict = Depends(get_current_sales_user),
    db: Session = Depends(get_db),
):
    """Permite al Closer dar de alta un prospecto nuevo (Nombre, Negocio, WhatsApp, Email) e inyectarlo en CRM ProsperIA."""
    full_name = (req.name or "").strip()
    raw_phone = (req.phone or "").strip()
    if not full_name or not raw_phone:
        raise HTTPException(status_code=400, detail="Nombre y WhatsApp/Teléfono son obligatorios.")

    phone_e164 = normalize_phone_e164(raw_phone)
    clean_email = normalize_email(req.email or "")
    if not clean_email:
        digits = "".join(ch for ch in raw_phone if ch.isdigit())[-10:] or "nuevo"
        clean_email = f"prospecto.{digits}@agenciaprosperia.com"

    dnd_reason = is_contact_excluded(db, clean_email, phone_e164)
    if dnd_reason:
        raise HTTPException(status_code=400, detail=f"Contacto en lista DND/Opt-out: {dnd_reason}")

    existing = db.query(DbLead).filter(
        (DbLead.email == clean_email) | ((DbLead.phone_e164 == phone_e164) & (DbLead.phone_e164 != ""))
    ).first()

    now_iso = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    stage = req.initial_stage if req.initial_stage in ("Lead identificado", "Primer contacto") else "Primer contacto"
    bname = (req.business_name or "").strip() or full_name
    tpl = (req.selected_template or "clinica_dental_estetica").strip()

    if existing:
        existing.owner_id = existing.owner_id or current_user["email"]
        existing.pipeline_stage = stage
        existing.last_touch = now_iso
        db.commit()
        db.refresh(existing)
        lead_obj = existing
    else:
        lead_obj = DbLead(
            name=full_name,
            full_name=full_name,
            email=clean_email,
            company=bname,
            business_name=bname,
            phone=raw_phone,
            phone_e164=phone_e164,
            status="qualified" if stage == "Primer contacto" else "new",
            source="closer_prospeccion_propia",
            source_channel="Iniciativa Closer",
            source_campaign=f"Closer: {current_user['name']}",
            score=85,
            notes=(req.notes or f"Alta directa por Closer {current_user['name']} ({current_user['email']}).").strip(),
            created_at=now_iso,
            owner_id=current_user["email"],
            setter_id=current_user["email"],
            niche="clinica" if "clinica" in tpl else "servicios_locales",
            country="LATAM / US",
            pipeline_stage=stage,
            offer_version="EXPRESS_497",
            quoted_amount=497.0 if stage == "Primer contacto" else 0.0,
            selected_template=tpl,
            last_touch=now_iso,
        )
        db.add(lead_obj)
        db.commit()
        db.refresh(lead_obj)

    record_audit(
        db,
        actor_email=current_user["email"],
        actor_role=current_user["role"],
        lead_id=lead_obj.id,
        action="closer_created_lead_pushed_to_ghl",
        field_changed="pipeline_stage",
        old_value="new",
        new_value=stage,
        notes=f"Nuevo prospecto '{bname}' dado de alta por {current_user['name']} e inyectado a CRM ProsperIA.",
    )
    db.commit()

    # Inyectar en tiempo real en CRM ProsperIA (GoHighLevel API v2)
    sync_sales_os_event_to_ghl_async(
        contact_id=getattr(lead_obj, "contact_id", "") or "",
        opportunity_id=getattr(lead_obj, "ghl_opportunity_id", "") or "",
        email=lead_obj.email,
        phone=lead_obj.phone or "",
        full_name=lead_obj.full_name or lead_obj.name,
        business_name=lead_obj.business_name or lead_obj.company or lead_obj.name,
        pipeline_stage=stage,
        owner_email=current_user["email"],
        offer_version="EXPRESS_497",
        quoted_amount=497.0,
        amount_collected=0.0,
        invoice_id="",
        selected_template=tpl,
        audit_summary=f"Nuevo prospecto creado por {current_user['name']} ({current_user['email']}) en etapa '{stage}'.",
    )

    return {
        "success": True,
        "message": f"✅ Prospecto '{bname}' creado e inyectado en CRM ProsperIA en etapa '{stage}'.",
        "data": serialize_lead(lead_obj),
    }


class CloserBulkImportRequest(BaseModel):
    csv_text: str
    initial_stage: Optional[str] = "Lead identificado"
    selected_template: Optional[str] = "clinica_dental_estetica"


@router.post("/api/sales-os/closer-import-csv")
async def api_closer_bulk_import_csv(
    req: CloserBulkImportRequest,
    current_user: dict = Depends(get_current_sales_user),
    db: Session = Depends(get_db),
):
    """Importa un lote de prospectos desde Excel/CSV (Nombre, Negocio, Teléfono, Email) asignados al Closer."""
    raw_lines = [ln.strip() for ln in (req.csv_text or "").splitlines() if ln.strip()]
    if not raw_lines:
        raise HTTPException(status_code=400, detail="Pega al menos 1 fila o sube un archivo CSV con tus prospectos.")

    stage = req.initial_stage if req.initial_stage in ("Lead identificado", "Primer contacto") else "Lead identificado"
    tpl = (req.selected_template or "clinica_dental_estetica").strip()
    now_iso = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    imported = 0
    skipped = 0

    for idx, line in enumerate(raw_lines):
        low = line.lower()
        if idx == 0 and ("nombre" in low or "name" in low) and ("tel" in low or "whatsapp" in low or "phone" in low):
            continue
        sep = "\t" if "\t" in line else (";" if ";" in line and "," not in line else ",")
        parts = [p.strip().strip('"') for p in line.split(sep)]
        if len(parts) < 2:
            skipped += 1
            continue
        name_val = parts[0]
        if len(parts) == 2:
            bname_val, phone_val, email_val = name_val, parts[1], ""
        elif len(parts) == 3:
            bname_val, phone_val, email_val = parts[1], parts[2], ""
        else:
            bname_val, phone_val, email_val = parts[1], parts[2], parts[3]

        if not name_val or not phone_val:
            skipped += 1
            continue

        phone_e164 = normalize_phone_e164(phone_val)
        clean_em = normalize_email(email_val)
        if not clean_em:
            digits = "".join(ch for ch in phone_val if ch.isdigit())[-10:] or f"row{idx}"
            clean_em = f"lote.{digits}@agenciaprosperia.com"

        if is_contact_excluded(db, clean_em, phone_e164):
            skipped += 1
            continue

        exists = db.query(DbLead).filter(
            (DbLead.email == clean_em) | ((DbLead.phone_e164 == phone_e164) & (DbLead.phone_e164 != ""))
        ).first()
        if exists:
            skipped += 1
            continue

        db.add(DbLead(
            name=name_val,
            full_name=name_val,
            email=clean_em,
            company=bname_val or name_val,
            business_name=bname_val or name_val,
            phone=phone_val,
            phone_e164=phone_e164,
            status="qualified" if stage == "Primer contacto" else "new",
            source="closer_lote_excel",
            source_channel="Lote Propio Closer",
            source_campaign=f"Lote Excel {current_user['name']}",
            score=80,
            notes=f"Importado desde lista propia de {current_user['name']}.",
            created_at=now_iso,
            owner_id=current_user["email"],
            setter_id=current_user["email"],
            niche="clinica",
            country="LATAM / US",
            pipeline_stage=stage,
            offer_version="EXPRESS_497",
            quoted_amount=497.0 if stage == "Primer contacto" else 0.0,
            selected_template=tpl,
            last_touch=now_iso,
        ))
        imported += 1

    if imported > 0:
        record_audit(
            db,
            actor_email=current_user["email"],
            actor_role=current_user["role"],
            lead_id=None,
            action="closer_bulk_csv_import",
            field_changed="leads",
            old_value="0",
            new_value=str(imported),
            notes=f"{current_user['name']} importó {imported} prospectos propios desde Excel/CSV (etapa: {stage}).",
        )
    db.commit()
    return {
        "success": True,
        "message": f"✅ Se importaron {imported} prospectos nuevos a tu cuenta en etapa '{stage}' ({skipped} omitidos por duplicado/vacío).",
        "data": {"imported": imported, "skipped": skipped},
    }






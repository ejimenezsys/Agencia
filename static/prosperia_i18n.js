/**
 * Motor Bilingüe Universal (ES | EN) — Agencia Prosper IA LLC
 * Capa 1: Diccionario ejecutivo B2B / Venture Capital para navegación, footer y páginas clave.
 * Capa 2: Motor de traducción contextual de frases y encabezados para cobertura completa del portal.
 */
(function () {
  'use strict';

  var STORAGE_KEY = 'prosperia_lang';
  var ATTR_MARK = 'data-pia-i18n-bound';

  var origTextNodes = new WeakMap();
  var origBlocks = new WeakMap();
  var trackedTextNodes = [];
  var trackedBlocks = [];
  var currentLang = 'es';
  var observerPaused = false;

  // Marcas protegidas que no deben alterarse al traducir frases
  var PROTECTED_TERMS = [
    'Agencia Prosper IA LLC',
    'Agencia ProsperIA LLC',
    'Agencia Prosper IA',
    'Agencia ProsperIA',
    'PassportAI.app',
    'PassportAI',
    'ProsperIA CRM',
    'ProsperIAStack',
    'Prosper IA',
    'Las 4 Inteligencias',
    'SVE90',
    'GoHighLevel',
    'FIUBA',
    'Edward Jiménez',
    'Idol Jose Group Corp',
    'IDOL JOSE GROUP CORP',
    'Idol Jose Official',
    'Doral Fashion Week',
    'Doral Business City',
    'EXMA Miami',
    'CNBV',
    'Banco Azteca',
    'Elektra',
    'WhatsApp',
    'Apple App Store',
    'Google Play Store',
    'LCCN 2026970390',
    'edward@agenciaprosperia.com'
  ];

  // Traducciones exactas de alta precisión (texto normalizado -> inglés ejecutivo)
  var EXACT_MAP = {
    // Topbar & Navbar Global
    'AGENCIA PROSPERIA LLC · MIAMI, FL · EE. UU. & LATAM · ES / EN': 'AGENCIA PROSPERIA LLC · MIAMI, FL · USA & LATAM · ES / EN',
    'Azul': 'Blue',
    'Blanco': 'Light',
    'Oscuro': 'Dark',
    'Acceso Closers': 'Closers Portal',
    'Inicio': 'Home',
    'Páginas Web': 'Smart Websites',
    'Agentes de IA': 'AI Agents',
    'Equipo IA': 'AI Workforce',
    'Tarjeta': 'Digital Card',
    'Recursos': 'Resources',
    'Nosotros': 'About Us',
    'Diagnóstico': 'Diagnostics',
    'Menú': 'Menu',
    'Planes CRM SaaS ($97) & Tu Agencia GHL': 'CRM SaaS Plans ($97) & Your GHL Agency',
    'Activa tu subcuenta en 1 clic o llévate 3 Bonos VIP': 'Activate your sub-account in 1 click or get 3 VIP Bonuses',
    'PassportAI.app · Simulador, CRM & Seed US$1M': 'PassportAI.app · Simulator, CRM & $1M Seed',
    '+740 negocios activos · Meta 100K usuarios': '740+ active businesses · Roadmap to 100K+ users',
    'Explorar Plantillas en Vivo por Giro': 'Explore Live Industry Templates',
    'Recorre 12 industrias interactivas': 'Browse 12 interactive industries',
    'Consultoría IA & SVE90': 'AI Consulting & SVE90',
    'Arquitectura B2B y RAG privado': 'B2B Architecture & Private RAG',
    'El Arsenal (+5,000 Prompts)': 'The Arsenal (5,000+ Prompts)',
    'Biblioteca de video, fotos y agentes': 'Library of video, photo & agent workflows',
    '200 Códigos Creativos': '200 Creative Codes',
    'Guías y prompts descargables': 'Downloadable guides & prompts',
    'Test de Madurez IA': 'AI Maturity Assessment',
    'Evalúa tu negocio en 90 segundos': 'Evaluate your business in 90 seconds',
    'Libro: Las 4 Inteligencias': 'Book: Las 4 Inteligencias',
    'Autor: Edward Jiménez': 'Author: Edward Jiménez',
    'Artículos y Podcast Hub': 'Articles & Podcast Hub',

    // Footer Global
    'Agencia ProsperIA LLC. Firma de consultoría en inteligencia artificial: diseñamos e implementamos sistemas que conectan IA, ventas, automatización, CRM y datos para que las empresas operen y crezcan con menos fricción.':
      'Agencia Prosper IA LLC. Enterprise AI engineering & consulting firm in Miami, FL: we design and deploy autonomous 24/7 AI Agents, vertical CRM, Smart Websites, and custom SaaS powered by PassportAI.app.',
    'Soluciones': 'Solutions',
    'Páginas Web & Tiendas Online': 'Smart Websites & Online Stores',
    'CRM por Industria + 23 Micro-Apps IA': 'Vertical CRM + 23 AI Micro-Apps',
    'Planes CRM SaaS ($97–$497) & Alianza Agencias GHL': 'CRM SaaS Plans ($97–$497) & GHL Agency Partnership',
    'Asistente IA 24/7 (Chat, Voz & Back-Office)': '24/7 AI Assistant (Chat, Voice & Back-Office)',
    'Tus 4 Empleados Digitales (SDR, Setter, Closer y Soporte)': 'Your 4 Digital Employees (SDR, Setter, Closer & Support)',
    'Marketing, Meta Ads & Reels IA': 'Marketing, Meta Ads & Viral AI Reels',
    'Tarjeta Digital Interactiva & QR Google': 'Interactive Digital Card & Google Reviews QR',
    'Consultoría en IA & SVE90 Enterprise': 'AI Consulting & SVE90 Enterprise',
    'PassportAI (Prueba 5 Días)': 'PassportAI (5-Day Trial)',
    'El Arsenal (+5,000 Prompts)': 'The Arsenal (5,000+ Prompts)',
    '200 Códigos Creativos & PDFs': '200 Creative Codes & PDFs',
    'Test de Madurez IA (90s)': 'AI Maturity Test (90s)',
    'Diagnóstico Comercial': 'Commercial Diagnostics',
    'Registro PassportAI (5 Días Gratis)': 'PassportAI Signup (5 Days Free)',
    'Acceso al CRM Interno': 'Internal CRM Login',
    'Contacto Directo': 'Direct Contact',
    'Sede:': 'Headquarters:',
    'Liderazgo:': 'Leadership:',
    'Teléfono:': 'Phone:',
    '© 2026 AGENCIA PROSPERIA LLC. Todos los derechos reservados.': '© 2026 AGENCIA PROSPER IA LLC. All rights reserved.',
    'Política de Privacidad': 'Privacy Policy',
    'Términos de Servicio': 'Terms of Service',
    'CRM Privado': 'Private CRM',

    // /passportai & /inversionistas Flagship
    'Agencia Prosper IA': 'Agencia Prosper IA',
    'Consultoría IA & SVE90': 'AI Consulting & SVE90',
    'Casos de Éxito': 'Case Studies',
    'Ronda Seed US$1M': '$1M Seed Round',
    'Todos los Enlaces (/links)': 'All Official Links (/links)',
    'Plataforma SaaS Propietaria · Powered by PassportAI.app': 'Proprietary SaaS Platform · Powered by PassportAI.app',
    'PassportAI.app: La Infraestructura de IA que Conecta Agentes 24/7 + CRM para Escalar Latinoamérica':
      'PassportAI.app: The AI Infrastructure Connecting 24/7 Autonomous Agents + CRM Across Latin America & US SMBs',
    'Entrar a PassportAI.app': 'Launch PassportAI.app',
    'Probar Agente IA en Vivo (WhatsApp)': 'Test Live AI Agent (WhatsApp)',
    'Tesis Capital de Riesgo (Seed US$1M)': 'Venture Capital Thesis ($1M Seed)',
    '+US$130K USD': '$130K+ USD',
    'Capital propio invertido en 18 meses de I+D': 'Founder equity invested across 18 months of R&D',
    '+740 Negocios': '740+ Businesses',
    'Base activa (~17 eventos por usuario/semana)': 'Active user base (~17 events per user/week)',
    '10 Verticales CRM': '10 CRM Verticals',
    'ProsperIAStack: CRM instalado en minutos': 'ProsperIAStack: CRM deployed in minutes',
    'US$19 / mes': '$19 / mo Entry',
    'Meta de evangelización: rumbo a 1M de usuarios': 'LATAM evangelization tier toward 100K–1M users',
    'PassportAI en Acción: Conversación + Ejecución Real en el Sistema':
      'PassportAI in Action: Live Conversation + Real System Execution',
    'WhatsApp 24/7': 'WhatsApp 24/7',
    'Agente de Voz': 'Voice AI Agent',
    'Chat Web + RAG': 'Web Chat + Private RAG',
    'Reactivación CRM': 'CRM Reactivation',
    'Fuera de horario (21:47 PM)': 'After-Hours (9:47 PM)',
    'Horario laboral (11:15 AM)': 'Business Hours (11:15 AM)',
    'QUÉ EJECUTÓ PASSPORTAI EN PROSPERIA CRM': 'WHAT PASSPORTAI EXECUTED IN PROSPERIA CRM',
    'PROSPECTO': 'PROSPECT',
    'PASSPORTAI SETTER IA (en 3.2 seg)': 'PASSPORTAI AI SETTER (in 3.2 sec)',
    'CALENDARIO SINCRONIZADO': 'CALENDAR SYNCED',
    'WORKFLOW ANTI NO-SHOW': 'ANTI NO-SHOW WORKFLOW',
    'PACIENTE / CLIENTE': 'CLIENT / PATIENT',
    'AGENTE DE VOZ IA': 'AI VOICE AGENT',
    'AGENDA ACTUALIZADA': 'SCHEDULE UPDATED',
    'AUDITORÍA RAG & QA': 'RAG & QA AUDIT',
    'VISITANTE B2B': 'B2B VISITOR',
    'CEREBRO RAG PRIVADO': 'PRIVATE RAG BRAIN',
    'BASE DE CONOCIMIENTO PRIVADA': 'PRIVATE KNOWLEDGE BASE',
    'CALIFICACIÓN ENTERPRISE': 'ENTERPRISE QUALIFICATION',
    'DISPARO INMEDIATO': 'INSTANT ROUTING',
    'ANTIGUO PROSPECTO': 'DORMANT PROSPECT',
    'OPORTUNIDAD REACTIVADA': 'OPPORTUNITY REACTIVATED',
    'TAREA AL CLOSER': 'CLOSER ALERT',
    'RETENCIÓN DIARIA': 'DAILY RETENTION MOAT',
    '¿Por qué los usuarios regresan todos los días? El Ancla PassportAI + ProsperIA CRM':
      'Why Users Return Every Single Day: The PassportAI + ProsperIA CRM Stickiness Moat',
    '↑ +45.0% CRECIMIENTO SEMANAL': '↑ +45.0% WEEKLY GROWTH',
    '1. Chatbots Autónomos 24/7': '1. 24/7 Autonomous Chatbots',
    '↑ +42.4% CRECIMIENTO SEMANAL': '↑ +42.4% WEEKLY GROWTH',
    '2. AI Playground Multi-Modelo': '2. Multi-Model AI Playground',
    'RETENCIÓN DIARIA B2B': 'DAILY B2B RETENTION',
    '3. Vínculo Nativo GoHighLevel / CRM': '3. Native GoHighLevel / CRM Hook',
    '17 EVENTOS / USUARIO': '17 EVENTS / USER',
    '4. Constructores Empresariales': '4. Business AI Builders',
    'Calculadora de Retorno de Inversión en Dólares (USD $)': 'ROI Savings Calculator in USD ($)',
    'Tamaño del equipo (personas que responden, capturan o hacen seguimiento)': 'Team size (staff handling inquiries, quotes, or CRM follow-up)',
    'Horas trabajadas por semana (por persona)': 'Hours worked per week (per team member)',
    '% del tiempo en tareas repetitivas (WhatsApp, cotizar básico, agenda, CRM)': '% of time spent on repetitive ops (WhatsApp, quotes, scheduling, CRM entry)',
    'Costo empresa por hora en USD ($ incluyendo cargas)': 'Loaded hourly cost in USD ($ employer cost)',
    'RESULTADO CONSERVADOR EN VIVO': 'LIVE CONSERVATIVE ESTIMATE',
    'Ahorro mensual estimado con PassportAI + CRM': 'Estimated monthly savings with PassportAI + CRM',
    'Costo repetitivo sin IA': 'Current repetitive ops cost',
    'Horas recuperadas al equipo': 'Monthly hours reclaimed',
    'Solicitar Diagnóstico con Este Cálculo →': 'Book Executive Assessment with This ROI →',
    'Fórmula: 4.33 semanas/mes · Supuesto conservador del 75% de carga repetitiva automatizada. No incluye ventas extra recuperadas por responder en <5 seg.':
      'Formula: 4.33 weeks/month · Conservative assumption of 75% repetitive workload automated. Excludes incremental revenue captured via <5 sec WhatsApp response.',
    // Simulator Dialogues, CRM Side-Effects & Cards in /passportai
    'Hola, vi su publicación. ¿Tienen disponibilidad mañana para una valoración o demo con mi equipo?':
      'Hi, I saw your post. Do you have availability tomorrow for a quick assessment or demo with my team?',
    '¡Hola! Claro que sí. Mañana tenemos espacio libre a las 11:00 AM o 4:00 PM hora Miami. ¿Cuál te queda mejor y cuál es tu nombre y correo para apartarte el espacio en calendario?':
      'Hello! Yes, we have openings tomorrow at 11:00 AM or 4:00 PM EST (Miami). Which works best, and what is your name and email to lock it into the calendar?',
    'A las 11:00 AM, soy Carlos Mendoza (cmendoza@grupoatlas.com).':
      '11:00 AM works great — Carlos Mendoza (cmendoza@grupoatlas.com).',
    'Contacto creado, etiquetado por industria y asignado vía Round-Robin al Closer disponible.':
      'Contact created, tagged by industry, and assigned via Round-Robin to the next available Closer.',
    'Cita confirmada para mañana 11:00 AM (horario bloqueado al instante).':
      'Appointment confirmed for tomorrow at 11:00 AM (calendar slot locked instantly).',
    'Recordatorio automático programado 24h y 2h antes por WhatsApp + correo.':
      'Automated 24h & 2h anti no-show reminders scheduled via WhatsApp + email.',
    '✓ Prospecto cerrado en calendario a las 21:47 PM sin equipo conectado':
      '✓ Prospect booked into calendar at 9:47 PM with zero staff online',
    '✓ Resuelto a las 21:47 PM sin intervención humana del equipo':
      '✓ Resolved at 9:47 PM with zero human team intervention',
    '✓ Atendido en < 4 seg liberando a tu equipo comercial para cerrar ventas':
      '✓ Answered in < 4 sec freeing your sales team to close high-value deals',
    'Buenas noches, llamaba porque necesito reagendar mi cita del martes para el jueves por la tarde.':
      'Good evening, I am calling to reschedule my Tuesday appointment to Thursday afternoon.',
    'Con gusto te ayudo. Veo tu cita del martes a las 10:00 AM. El jueves tengo disponible a las 2:30 PM o a las 4:15 PM. ¿Te confirmo el jueves a las 2:30 PM?':
      'Happy to help. I see your Tuesday 10:00 AM visit. I have Thursday open at 2:30 PM or 4:15 PM — should I confirm 2:30 PM on Thursday?',
    'Sí, 2:30 PM perfecto. ¡Gracias!': 'Yes, 2:30 PM is perfect. Thank you!',
    'Cita movida de mar 10:00 AM → jue 2:30 PM; horario del martes liberado.':
      'Appointment moved from Tue 10:00 AM → Thu 2:30 PM; Tuesday slot freed immediately.',
    'Confirmación enviada al instante al teléfono del cliente.':
      'Instant confirmation texted directly to the client’s mobile phone.',
    'Resumen de llamada guardado automáticamente en la ficha del CRM.':
      'Call summary and transcript logged automatically inside the CRM record.',
    'Somos una clínica con 3 sucursales y 28 empleados. ¿Cómo protegen los datos y cuánto tarda integrarlo?':
      'We are a 3-location clinic with 28 staff. How do you protect private data and how fast is deployment?',
    'Operamos con bases de conocimiento privadas aisladas por cliente y sin entrenamiento público. Para 3 sucursales implementamos la ruta SVE90: agentes 24/7 activos en 10 días y ecosistema completo en 30–90 días. ¿Deseas recibir el caso de éxito y agendar diagnóstico?':
      'We run isolated private knowledge bases with zero public model training. For 3 locations we deploy SVE90: 24/7 agents live in 10 days and full integration in 30–90 days. Would you like our case study and an assessment slot?',
    'Respondió 100% basado en documentos oficiales sin inventar precios ni cláusulas.':
      'Answered 100% strictly from official company docs with zero price or policy hallucinations.',
    'Etiquetado automático como oportunidad Multi-Sucursal (SVE90) para dirección comercial.':
      'Automatically tagged as a Multi-Location SVE90 opportunity for senior leadership.',
    'Envió resumen al Director Comercial para llamada prioritaria.':
      'Dispatched instant deal brief to the Commercial Director for priority follow-up.',
    'Hola Sofía, vimos que hace 4 meses cotizaste tu automatización con nosotros. Abrimos 3 espacios de implementación para diciembre. ¿Te envío tu enlace actualizado?':
      'Hi Sofia, we saw you requested an automation quote 4 months ago. We opened 3 onboarding slots for December — want me to send your updated link?',
    '¡Justo lo estábamos hablando hoy! Mándame el link para verlo mañana.':
      'We were literally discussing it today! Send over the link so we can review tomorrow.',
    'Lead dormido movido en automático a etapa "Calificado Caliente".':
      'Dormant lead automatically promoted to "Hot Qualified" pipeline stage.',
    'Alarma en tiempo real para seguimiento en menos de 2 minutos.':
      'Real-time task alert triggered for closer follow-up under 2 minutes.',
    'El equipo comercial regresa cada mañana porque sus ventas viven aquí.':
      'Sales reps log in every morning because all active deals and conversations live here.',
    '✓ Llamada resuelta punta a punta a las 21:47 PM en 48 segundos':
      '✓ Voice call resolved end-to-end at 9:47 PM in 48 seconds',
    '✓ Lead B2B calificado e indexado con cero intervención humana':
      '✓ B2B lead qualified and synced to CRM with zero human intervention',
    '✓ Ingresos recuperados sobre base de datos que ya estaba olvidada':
      '✓ Revenue recovered automatically from dormant CRM leads',
    'Agentes entrenados con reglas de negocio que operan directo sobre WhatsApp, Instagram y Web integrados vía API al CRM.':
      'Rule-governed AI agents operating directly on WhatsApp, Instagram, and Web with live API CRM sync.',
    'Acceso centralizado a múltiples modelos líderes y comparación ejecutiva en un entorno corporativo sin fugas de datos.':
      'Centralized multi-model execution and executive benchmarking inside an isolated enterprise environment.',
    'Canal estratégico hacia los millones de negocios y agencias que ya operan en el ecosistema CRM líder, sumándoles el cerebro de PassportAI.':
      'Direct white-label distribution channel to millions of SMBs & agencies already running on GoHighLevel CRM.',
    'Arquitecto de ofertas, sprint de contenido viral de 30 días, guiones y SOPs operativos listos para equipos no técnicos.':
      'Offer architect, 30-day viral content sprint, video scripts, and operational SOPs built for non-technical teams.',
    'Consolidar los +740 usuarios activos actuales, escalar nuevas comunidades mediante las estrategias de marketing de Agencia Prosper IA y el onboarding instantáneo de ProsperIAStack con cuentas de US$99/mes + Pack Anual US$990.':
      'Consolidate 740+ active users, scale new business communities via Agencia Prosper IA growth strategies and instant ProsperIAStack CRM onboarding across $99/mo + $990 Annual accounts.',
    'Crecimiento vía conector marca blanca y aprovisionamiento automático ProsperIAStack sobre el ecosistema CRM GoHighLevel con planes híbridos ($19 / $49 / $99 CRM Starter).':
      'Scale via white-label connector and automated ProsperIAStack provisioning into the GoHighLevel ecosystem across hybrid $19 / $49 / $99 tiers.',
    'Con la ronda Seed US$1M lanzamos apps nativas en Apple App Store y Google Play Store. Sostener 100,000 usuarios recurrentes mes tras mes ya representa potencia financiera de nivel internacional.':
      '$1M Seed funding accelerates native iOS (Apple App Store) and Android (Google Play Store) apps. Sustaining 100,000 active paying users delivers $1.9M–$4.9M+ MRR.',
    'Escala masiva a US$19/mes desde Miami para toda Latinoamérica, combinando educación, creación de comunidades, retención CRM diaria y operación móvil nativa.':
      'Continental scale from $19/mo out of Miami across Latin America, combining education, community building, daily CRM lock-in, and mobile AI agents.',
    'Proyección anual: $81,900 USD/año': 'Annual projection: $81,900 USD/yr',
    'Venture Capital & Alianzas · Ronda Seed US$1,000,000 USD': 'Venture Capital & Strategic Partnerships · $1,000,000 Seed Round',
    'Tesis de Capital de Riesgo: Evangelizar Latinoamérica hacia 1,000,000 de Usuarios a US$19/mes':
      'Venture Thesis: Democratizing Applied AI Across Latin America at $19–$99/mo Toward 100K–1M Users',
    '1. Ventaja Injusta de Origen: Ingeniería FIUBA + Tracción de Comunidades':
      '1. Structural Unfair Advantage: FIUBA Engineering + Community Growth Engine',
    '2. Puente Corporativo y Narrativa Pública (Libro Oficial EXMA Miami)':
      '2. Executive Authority & Organic Distribution (Official Book at EXMA Miami)',
    'Escalera de Monetización Actual y Escalamiento (US$19 · US$49 · US$99/mes CRM · US$990 Anual)':
      'Current Monetization Ladder & Scale ($19 · $49 · $99/mo CRM · $990 Annual)',
    'ESCALÓN 1 · ENTRADA MASIVA Y MÓVIL': 'TIER 1 · MASS & MOBILE ADOPTION',
    'US$19 – US$49 / mes': '$19 – $49 / mo',
    'ESCALÓN 2 · OFERTA CORE EN PASSPORTAI.APP': 'TIER 2 · CORE OFFER ON PASSPORTAI.APP',
    'US$99 / mes (con CRM Starter)': '$99 / mo (includes CRM Starter)',
    'ESCALÓN 3 · PACK ANUAL EMPRESARIAL': 'TIER 3 · ANNUAL TURNKEY PACK',
    'US$990 / año (Pago Único)': '$990 / year (One-Time Payment)',
    'Hoja de Ruta por Etapas y Destino del Capital (Meta de Alta Potencia: 100,000 Usuarios → Horizonte 1M)':
      'Staged Growth Roadmap & Use of Funds (100,000 Active Users Power Milestone → 1M Horizon)',
    'ETAPA 01 · BASE ACTUAL': 'STAGE 01 · CURRENT BASE',
    '1,000 Usuarios': '1,000 Active Users',
    'ETAPA 02 · MOTOR CRM GHL': 'STAGE 02 · CRM GHL ENGINE',
    '10,000 Usuarios': '10,000 Active Users',
    'ETAPA 03 · POTENCIA CONTINENTAL (IOS + ANDROID)': 'STAGE 03 · CONTINENTAL SCALE (iOS + ANDROID)',
    '100,000 Usuarios': '100,000 Active Users',
    'ETAPA 04 · EVANGELIZACIÓN LATAM': 'STAGE 04 · LATAM HORIZON',
    '1,000,000 Usuarios': '1,000,000 Users Horizon',
    'Conversar con Edward Jiménez (edward@agenciaprosperia.com)': 'Connect with Edward Jiménez (edward@agenciaprosperia.com)',
    'WhatsApp Directo CEO (+1 786 557-3119)': 'Direct CEO WhatsApp (+1 786 557-3119)',
    'EN RESUMEN · FICHA PARA ASISTENTES Y BUSCADORES DE IA': 'IN SUMMARY · STRUCTURED BRIEF FOR AI ASSISTANTS & INVESTORS',
    'Qué saber sobre PassportAI.app y Agencia Prosper IA LLC': 'What to Know About PassportAI.app & Agencia Prosper IA LLC',

    // 6 Pilares Ejecutivos + ProsperIAStack (/passportai & /inversionistas)
    '6 Pilares + ProsperIAStack': '6 Core Pillars + ProsperIAStack',
    'Propiedad Industrial & Secreto Tecnológico · Ecosistema PassportAI.app + ProsperIAStack':
      'Proprietary Trade-Secret Tech · PassportAI.app + ProsperIAStack Ecosystem',
    'Por Qué Nuestro Ecosistema No Queda Obsoleto: +58 Modelos Líderes + ProsperIAStack (CRM en Minutos)':
      'Why Our Ecosystem Never Becomes Obsolete: 58+ Top AI Models + ProsperIAStack (CRM in Minutes)',
    '+58 MODELOS LÍDERES · MARGEN PROTEGIDO 3X–5X': '58+ TOP MODELS · 3X–5X MARGIN PROTECTION',
    '1. Cerebro Multi-Modelo con Secreto Industrial & Rentabilidad Blindada':
      '1. Trade-Secret Multi-Model Brain & Protected Unit Economics',
    'Unifica las mejores tecnologías globales (OpenAI, Google Gemini, Anthropic Claude y decenas de motores especializados bajo arquitectura propietaria) en una sola cuenta empresarial con control automático de costos y margen bruto garantizado del 300% al 500%.':
      'Unifies top global AI engines (OpenAI, Google Gemini, Anthropic Claude, plus dozens of specialized trade-secret models under proprietary orchestration) in one enterprise workspace with automated cost controls and 300%–500% gross margin protection.',
    'OpenAI · Gemini · Claude': 'OpenAI · Gemini · Claude',
    '+58 Modelos Activos': '58+ Active Models',
    'Margen 3x–5x Blindado': '3x–5x Protected Margin',
    'PROSPERIASTACK · DE 2 MESES A 5 MINUTOS': 'PROSPERIASTACK · FROM 2 MONTHS TO 5 MINUTES',
    '2. ProsperIAStack: Onboarding & Aprovisionamiento Automático de CRM':
      '2. ProsperIAStack: Automated CRM Onboarding & One-Click Provisioning',
    'Conectado directamente dentro de PassportAI.app: el cliente sube sus documentos o completa un diagnóstico guiado por IA y el sistema instala de un solo golpe su embudo, más de 140 variables personalizadas, calendarios, flujos de seguimiento y 10 plantillas verticales listas por industria en minutos.':
      'Directly linked inside PassportAI.app: businesses upload their docs or complete an AI-guided intake and the system provisions their entire funnel, 140+ custom variables, calendars, follow-up workflows, and 10 ready-to-launch industry verticals in minutes.',
    '10 Verticales CRM': '10 CRM Verticals',
    '+140 Variables Auto-IA': '140+ AI Auto-Variables',
    'Despliegue en Minutos': 'Minutes-Fast Deploy',
    'CONEXIÓN QR & API · ATENCIÓN 24/7': 'QR & API CONNECT · 24/7 RESPONSE',
    '3. Agentes Autónomos de WhatsApp, Voz y Web Conectados al CRM':
      '3. Autonomous WhatsApp, Voice & Web Agents Synced to CRM',
    'Asistentes inteligentes que se vinculan escaneando un código QR de WhatsApp o por API oficial, aprenden de la documentación privada de cada negocio y agendan citas directamente dentro de ProsperIA CRM (ecosistema GoHighLevel).':
      'Smart assistants activated via a quick WhatsApp QR scan or official API, trained on each company’s private documents to qualify leads and book appointments directly into ProsperIA CRM (GoHighLevel ecosystem).',
    'WhatsApp QR + API': 'WhatsApp QR + API',
    'Base Privada RAG': 'Private RAG Brain',
    'Agenda Directa CRM': 'Direct CRM Booking',
    'ESTUDIO AUDIOVISUAL · REELS 9:16 & AVATARES': 'MEDIA STUDIO · 9:16 REELS & AVATARS',
    '4. Fábrica de Contenido Viral, Reels 9:16, Motion Graphics y Voz IA':
      '4. Viral Content Factory: 9:16 Reels, Motion Graphics & AI Voice',
    'Produce Reels verticales listos para publicar, videos con avatares hiperrealistas, clonación de voz profesional y subtítulos automáticos combinando tecnologías líderes como Runway y ElevenLabs con motores audiovisuales propietarios.':
      'Produces publish-ready vertical Reels, hyper-realistic avatar videos, studio-grade voice cloning, and dynamic captions by combining flagship providers like Runway and ElevenLabs with proprietary video pipelines.',
    'Reels 9:16 + Motion': '9:16 Reels + Motion',
    'Avatares & Voz IA': 'AI Avatars & Voice',
    'Runway · ElevenLabs': 'Runway · ElevenLabs',
    'CRECIMIENTO B2B · LINKEDIN, EMAIL & RADAR': 'B2B GROWTH · LINKEDIN, EMAIL & RADAR',
    '5. Prospección Multicanal Automática & Analista de Mercado':
      '5. Automated Omnichannel Prospecting & Market Radar',
    'Detecta lo que los clientes reales están pidiendo en internet, prospecta tomadores de decisión por LinkedIn y correo electrónico con aprobaciones asistidas por IA, reactiva clientes antiguos dormidos y genera campañas publicitarias completas.':
      'Monitors real market demand signals, reaches decision-makers via AI-assisted LinkedIn and email outreach, reactivates dormant CRM contacts, and compiles ready-to-run ad campaigns.',
    'LinkedIn + Email': 'LinkedIn + Email',
    'Radar de Mercado IA': 'AI Market Radar',
    'Reactivación Dormidos': 'Dormant Lead Rescue',
    '5 CONSTRUCTORES · ALTA DISPONIBILIDAD 24/7': '5 AI BUILDERS · 24/7 HIGH AVAILABILITY',
    '6. Constructores de Negocio, Investigación Profunda & Plataforma Trilingüe':
      '6. Business Builders Suite, Deep Research & Trilingual Platform',
    'Incluye 5 constructores estratégicos de ofertas y embudos, investigación documental avanzada sobre archivos propios del cliente, tutor interactivo, arquitectura cloud de alta disponibilidad 24/7 y operación nativa en Español, Inglés y Portugués.':
      'Includes 5 strategic offer and funnel builders, custom-source deep document research, interactive tutoring, 24/7 high-availability cloud infrastructure, and native Spanish, English & Portuguese operation.',
    '5 Constructores IA': '5 AI Builders',
    'Investigación Fuentes': 'Custom Source Research',
    'ES / EN / PT Nativo': 'Native ES / EN / PT',

    // /links Hub
    'Mostrar QR': 'Show QR',
    'Agencia Prosper IA LLC · Miami, Florida': 'Agencia Prosper IA LLC · Miami, Florida',
    'Ingeniero (+25 años en infraestructura crítica), Autor del libro «Las 4 Inteligencias» (Library of Congress LCCN 2026970390) y Fundador de Agencia Prosper IA LLC & PassportAI.app.':
      'Enterprise Systems Architect (25+ yrs in mission-critical infrastructure), Author of "Las 4 Inteligencias" (Library of Congress LCCN 2026970390), and Founder of Agencia Prosper IA LLC & PassportAI.app.',
    'Guardar Contacto': 'Save Contact',
    'WhatsApp Directo': 'Direct WhatsApp',
    'Copiar': 'Copy',
    'Ecosistema, Agencia y Libro Oficial': 'Ecosystem, AI Agency & Official Book',
    'PassportAI.app · Simulador, CRM & Visión Seed US$1M': 'PassportAI.app · Simulator, CRM & $1M Seed Vision',
    '+740 negocios · +58 Modelos IA · ProsperIAStack (CRM en minutos) · /passportai':
      '740+ SMBs · 58+ AI Models · ProsperIAStack (CRM in minutes) · /passportai',
    'Entrar Directo a la App · PassportAI.app': 'Launch SaaS Platform · PassportAI.app',
    'Chatbots WhatsApp QR, Reels 9:16, Estudio Visual & ProsperIAStack CRM · passportai.app':
      'WhatsApp QR Chatbots, 9:16 Reels, Visual Studio & ProsperIAStack CRM · passportai.app',
    'Agencia Prosper IA · Agentes IA 24/7 y Consultoría': 'Agencia Prosper IA · 24/7 AI Agents & Enterprise Consulting',
    'Automatización comercial, CRM, RAG privado y SVE90 · agenciaprosperia.com/ia': 'Commercial Automation, Vertical CRM, Private RAG & SVE90 · agenciaprosperia.com/ia',
    'Libro «Las 4 Inteligencias» en Amazon': 'Official Book "Las 4 Inteligencias" on Amazon',
    'Edición Kindle, Tapa Blanda y Pasta Dura VIP · Prólogo Fernando Anzures': 'Kindle, Paperback & Hardcover Editions · Foreword by Fernando Anzures',
    'Web del Libro + Test Gratuito de las 4 Inteligencias': 'Book Website + Free 4 Intelligences Assessment',
    'Validador de Oportunidades IA sobre 100 pts · agenciaprosperia.com/libro': '100-pt AI Opportunity Validator · agenciaprosperia.com/libro',
    'EXMA Miami · 4 y 5 de Diciembre 2026': 'EXMA Miami · Dec 4–5, 2026',
    'Lanzamiento oficial del libro ante 2,500 empresarios · agenciaprosperia.com/exmaboletos': 'Official book launch before 2,500 entrepreneurs · agenciaprosperia.com/exmaboletos',
    'Redes Oficiales (Agencia y Personales)': 'Official Social Profiles (Agency & Founder)',
    'Sortlist · Perfil B2B Verificado': 'Sortlist · Verified B2B Agency Profile',
    'Correo Directo CEO y Agencia · edward@agenciaprosperia.com': 'Direct CEO & Agency Email · edward@agenciaprosperia.com',
    'QR Oficial · agenciaprosperia.com/links': 'Official QR · agenciaprosperia.com/links',
    'Copiar URL /links': 'Copy URL /links',
    'Descargar QR': 'Download QR',

    // /casos-de-exito/idol-jose-group
    'Portafolio Web & IA': 'Web & AI Portfolio',
    'Hub Oficial /links': 'Official Hub /links',
    'Case Study / Caso de Éxito Oficial · Clutch Portfolio Ready': 'Official Case Study · Clutch Portfolio Ready',
    'IDOL JOSE GROUP CORP: Ecosistema Digital de 4 Portales, Revistas, Pasarelas Mensuales e IA 24/7':
      'IDOL JOSE GROUP CORP: 4-Portal Luxury Digital Ecosystem, Interactive Magazines, Runways & 24/7 AI Concierge',
    '4 Portales en Vivo': '4 Live Web Platforms',
    '5 Flujos de Registro': '5 Registration Workflows',
    '14+ Ediciones': '14+ Magazine Editions',
    'Ficha Técnica del Proyecto (Project Overview)': 'Project Overview & Technical Metadata',
    '1. Antecedentes del Cliente (Client Background)': '1. Client Background',
    '2. El Desafío (The Challenge)': '2. The Challenge',
    '3. Solución y Entregables (Solution & Deliverables)': '3. Solution & Deliverables',
    '4. Resultados y Métricas (Results & Impact)': '4. Results & Measurable Impact',
    '5. Galería de Evidencias del Portafolio (500×350 px — Clutch Ready)': '5. Portfolio Evidence Gallery (500×350 px — Clutch Ready)',
    'Descargar ↗': 'Download ↗',
    'Solicitar Diagnóstico Corporativo IA →': 'Request Corporate AI Assessment →',
    'Ver Más Proyectos en Vivo': 'View More Live Projects',

    // Home, Libro, Consultoría IA & Vertical Pages
    'Haz que tu negocio venda y agende citas todos los días , sin vivir esclavizado a tu celular':
      'Make Your Business Sell and Book Appointments Daily — Powered by AI & Vertical CRM',
    '¿Qué merece tu tiempo en la era de la Inteligencia Artificial ?':
      'What Truly Deserves Your Time in the Age of Artificial Intelligence?',
    'Páginas Web Inteligentes para Negocios que Quieren Vender y Agendar 24/7':
      'Smart High-Converting Websites Built to Sell & Book 24/7',
    'Tu Subcuenta CRM Lista en 1 Clic o Tu Propia Agencia de IA con GoHighLevel':
      'Your Ready-to-Launch CRM Sub-Account in 1 Click or Your Own GoHighLevel AI Agency',
    'Tu Recepcionista SDR IA & Setter IA Contesta Chats y Llamadas en Segundos 24/7':
      'Your 24/7 AI SDR & Setter Answers WhatsApp, Web Chats & Voice Calls in Seconds',
    'Tus 4 Empleados Digitales Trabajando Contigo 24/7 + 10 Ingenieros Reales Detrás':
      'Your 4 Autonomous AI Employees Working 24/7 + Real Systems Engineering Behind Them',
    '¿Quieres probar el Agente IA, Simulador 24/7 y Calculadora USD en Vivo?':
      'Want to Test the Live 24/7 AI Agent, System Simulator & USD ROI Calculator?',
    'Ver Simulador & Calculadora USD →': 'Launch Simulator & USD Calculator →',
    'Tesis Inversionistas (Seed US$1M)': 'Investor Thesis ($1M Seed Round)',
    '5 Preguntas Clave antes de Agendar': '5 Key Questions Before Booking',
    'Agendar mi Diagnóstico Ejecutivo (45 Min)': 'Schedule My 45-Min Executive Assessment',
    'Solicita tu Diagnóstico de Arquitectura IA & ROI': 'Request Your AI Architecture & ROI Assessment',
    'Explorar por perspectiva': 'Browse by Perspective'
  };

  // Reglas de reemplazo multi-palabra para párrafos HTML complejos o páginas secundarias en Capa 2
  var PHRASE_RULES = [
    [/Agendar Diagnóstico/gi, 'Book Assessment'],
    [/Agenda tu Diagnóstico/gi, 'Book Your Assessment'],
    [/Diagnóstico Gratuito/gi, 'Free Assessment'],
    [/Solicitar Diagnóstico/gi, 'Request Assessment'],
    [/Solicita tu /gi, 'Request Your '],
    [/Ver Plantillas/gi, 'View Templates'],
    [/Ver Demo/gi, 'View Demo'],
    [/Preguntas Frecuentes/gi, 'Frequently Asked Questions'],
    [/Todos los derechos reservados/gi, 'All rights reserved'],
    [/Política de Privacidad/gi, 'Privacy Policy'],
    [/Términos de Servicio/gi, 'Terms of Service'],
    [/Sitio Web Inteligente/gi, 'Smart AI Website'],
    [/Sitios Web Inteligentes/gi, 'Smart AI Websites'],
    [/Agentes de IA Autónomos 24\/7/gi, '24/7 Autonomous AI Agents'],
    [/Agentes de IA 24\/7/gi, '24/7 AI Agents'],
    [/Agente de IA 24\/7/gi, '24/7 AI Agent'],
    [/Agentes IA/gi, 'AI Agents'],
    [/Inteligencia Artificial/gi, 'Artificial Intelligence'],
    [/Transformación Empresarial/gi, 'Enterprise Transformation'],
    [/Automatización de Procesos/gi, 'Process Automation'],
    [/Automatización/gi, 'Automation'],
    [/Consultoría en IA/gi, 'AI Consulting'],
    [/Consultoría Corporativa/gi, 'Corporate Consulting'],
    [/Base de Conocimiento Privada/gi, 'Private Knowledge Base'],
    [/Cerebro Corporativo Privado/gi, 'Private Corporate AI Brain'],
    [/Sin intervenciones manuales/gi, 'Zero manual intervention'],
    [/pago único anual/gi, 'one-time annual payment'],
    [/pago único/gi, 'one-time payment'],
    [/Estados Unidos y Latinoamérica/gi, 'United States and Latin America'],
    [/EE\.?\s*UU\.?\s*y Latinoamérica/gi, 'USA & Latin America'],
    [/EE\.?\s*UU\.?/gi, 'USA'],
    [/Latinoamérica/gi, 'Latin America'],
    [/Copiar /gi, 'Copy '],
    [/Descargar /gi, 'Download ']
  ];

  // Bloque contextual completo para elementos clave con markup interno (strong/em/span) en /passportai y páginas clave
  var RICH_BLOCK_EN = {
    'Built Hero': true
  };

  function norm(s) {
    return (s || '').replace(/\s+/g, ' ').trim();
  }

  function restoreProtected(str, tokens) {
    return str.replace(/__PIA_TOK_(\d+)__/g, function (_, idx) {
      return tokens[Number(idx)] || '';
    });
  }

  function translateTextString(raw) {
    if (!raw || !raw.trim()) return raw;
    var key = norm(raw);
    if (EXACT_MAP[key]) {
      return raw.replace(raw.trim(), EXACT_MAP[key]);
    }
    var trimmed = raw.trim();
    var tokens = [];
    var safe = trimmed;
    for (var i = 0; i < PROTECTED_TERMS.length; i++) {
      var term = PROTECTED_TERMS[i];
      if (safe.indexOf(term) !== -1) {
        var placeholder = '__PIA_TOK_' + tokens.length + '__';
        tokens.push(term);
        safe = safe.split(term).join(placeholder);
      }
    }
    var changed = safe;
    for (var r = 0; r < PHRASE_RULES.length; r++) {
      changed = changed.replace(PHRASE_RULES[r][0], PHRASE_RULES[r][1]);
    }
    if (changed !== safe) {
      var finalStr = restoreProtected(changed, tokens);
      var lead = raw.match(/^\s*/)[0];
      var trail = raw.match(/\s*$/)[0];
      return lead + finalStr + trail;
    }
    return null;
  }

  function applyRichTranslations(lang) {
    // Rich mixed-HTML blocks keyed by element selector / heading relationship
    var pairs = [
      {
        sel: 'header.hero h1',
        en: '<span class="hl-cyan">PassportAI.app:</span> The AI Infrastructure Connecting <span class="hl-gold">24/7 AI Agents + CRM</span> to Scale Latin America &amp; US SMBs'
      },
      {
        sel: 'header.hero .hero-sub',
        en: 'Built over <strong>18 months of R&amp;D alongside engineers from FIUBA (University of Buenos Aires)</strong> and <strong>$130,000+ USD in founder equity</strong> invested by Edward Jiménez. Operating today with <strong>740+ active businesses and users</strong>, uniting Autonomous Chatbots, Multi-Model AI Playground, and direct integration with <strong>ProsperIA CRM</strong> (white-label <strong>GoHighLevel</strong> ecosystem) so AI becomes an essential daily habit.'
      },
      {
        sel: '#sim-title + .sec-lead',
        en: 'An isolated chatbot only outputs generic replies. A system powered by <strong>PassportAI.app + ProsperIA CRM</strong> reads real business context, books the appointment, and updates your sales pipeline in seconds — during work hours or late at night.'
      },
      {
        sel: '#moat-title + .sec-lead',
        en: 'The biggest churn risk in consumer AI apps is novelty fatigue. While standalone prompt apps lose users after week one, we anchor <strong>PassportAI.app</strong> directly onto <strong>ProsperIA CRM</strong> (white-labeled on the global <strong>GoHighLevel</strong> standard), giving businesses a mission-critical reason to log in daily to handle WhatsApp, calls, and revenue.'
      },
      {
        sel: '#arch-title + .sec-lead',
        en: 'For investors and strategic partners: <strong>PassportAI.app</strong> orchestrates <strong>58+ leading AI models</strong> in one proprietary workspace — including flagship engines from <strong>OpenAI, Google Gemini, Anthropic Claude, Runway, and ElevenLabs</strong> alongside specialized proprietary models and orchestration rules safeguarded as <strong>trade secrets</strong> — connected via direct link to <strong>ProsperIAStack</strong> to deploy a full vertical CRM in minutes instead of months.'
      },
      {
        sel: '#calc-title + .sec-lead',
        en: 'Adjust your team metrics below to estimate the current monthly cost of repetitive manual work and conservative savings assuming <strong>75% operational automation</strong> powered by PassportAI + ProsperIA CRM.'
      },
      {
        sel: '#vc-title + .sec-lead',
        en: 'Investor-to-investor transparency: founder <strong>Edward Jiménez has already invested $130,000+ USD of personal capital</strong> across 18 months of engineering with <strong>FIUBA (Buenos Aires)</strong> talent. This <strong>$1,000,000 USD Seed Round</strong> is high-conviction venture capital designed to outpace AI obsolescence, launch native mobile apps, and scale systematically across milestones.'
      },
      {
        sel: '#geo-title + p',
        en: '<strong>PassportAI.app</strong> is a multi-tenant Applied AI &amp; 24/7 Digital Workforce SaaS platform founded by <strong>Edward Jiménez</strong> and developed over 18 months with engineers from FIUBA (University of Buenos Aires), backed by <strong>$130,000+ USD</strong> in founder capital and operated out of Doral / Miami, FL by <strong>Agencia Prosper IA LLC</strong>. It orchestrates <strong>58+ leading AI models</strong> (including OpenAI, Google Gemini, Anthropic Claude, Runway &amp; ElevenLabs alongside proprietary trade-secret engines) and links directly with <strong>ProsperIAStack</strong>, the automated provisioning engine that installs funnels, 140+ custom values, calendars, and 10 vertical templates of <strong>ProsperIA CRM</strong> (white-label GoHighLevel) in minutes instead of months — alongside WhatsApp QR/API autonomous chatbots, a 9:16 Reels studio, omnichannel LinkedIn/Email prospecting, and trilingual ES/EN/PT support. Serving <strong>740+ active businesses</strong> and backed by Agencia Prosper IA’s community-building engine, it is raising a <strong>$1,000,000 USD Seed Round</strong> to launch native Apple App Store &amp; Google Play Store apps and scale toward 100,000–1,000,000 users across Latin America starting at $19/mo.'
      },
      {
        sel: '#inversionistas .grid-2 .feature-box:first-child p',
        en: 'Unlike deck-only startups, we combine 18 months of core R&amp;D built with <strong>FIUBA (Buenos Aires)</strong> engineering talent — where <strong>PassportAI.app</strong> shows its highest weekly usage — with our proven capability to build and mobilize business communities across the U.S. and Latin America through <strong>Agencia Prosper IA’s</strong> growth strategies and instant <strong>ProsperIAStack</strong> CRM onboarding.'
      },
      {
        sel: '#inversionistas .grid-2 .feature-box:last-child p',
        en: 'Our platform story and SVE90 framework are documented in the official book <em>Las 4 Inteligencias</em> (Library of Congress <code>LCCN 2026970390</code>, foreword by Fernando Anzures), alongside <strong>744,000+ organic views</strong> and <strong>19,160+ business followers</strong> driving organic demand.'
      },
      {
        sel: 'section[aria-labelledby="powered-passport-title"] p',
        en: '<strong>In Summary — About Agencia Prosper IA LLC &amp; PassportAI.app:</strong> Headquartered in Doral / Miami, Florida and founded by <strong>Edward Jiménez</strong> (25+ years in mission-critical banking &amp; telecom infrastructure; author of <em>Las 4 Inteligencias</em>, LCCN 2026970390), our firm deploys 24/7 Autonomous AI Agents (WhatsApp QR/API, Voice, Web), Smart Websites, Private RAG Brains, and SVE90 Transformation powered by <strong>PassportAI.app</strong> ($130,000+ USD founder R&amp;D over 18 months with FIUBA engineering and 740+ active businesses) connected to <strong>ProsperIAStack</strong> to deploy <strong>ProsperIA CRM</strong> across 10 industry verticals in minutes.'
      },
      {
        sel: '.hero-box h1',
        en: '<span>IDOL JOSE GROUP CORP:</span> 4-Portal Luxury Digital Ecosystem, Magazines, Monthly Runways &amp; 24/7 AI Concierge'
      },
      {
        sel: '.hero-box .hero-lead',
        en: 'End-to-end digital architecture designed and deployed by <strong>Agencia Prosper IA LLC</strong> (Edward Jiménez, Miami / Doral, FL) for the international Haute Couture, Editorial Media &amp; Runway conglomerate spanning Doral, Miami, and New York Fashion Week (NYFW).'
      }
    ];

    var grids = document.querySelectorAll('#inversionistas .grid-4');
    if (grids.length >= 2) {
      var tier2P = grids[0].querySelector('.stage-card:nth-child(2) p');
      if (tier2P) {
        if (!origBlocks.has(tier2P)) { origBlocks.set(tier2P, tier2P.innerHTML); trackedBlocks.push(tier2P); }
        tier2P.innerHTML = lang === 'en'
          ? 'Active core offer on <strong>passportai.app</strong>: pairs PassportAI + ProsperIA CRM Starter (GoHighLevel ecosystem), anchoring daily operational habits for SMBs.'
          : origBlocks.get(tier2P);
      }
      var stage3P = grids[1].querySelector('.stage-card:nth-child(3) p');
      if (stage3P) {
        if (!origBlocks.has(stage3P)) { origBlocks.set(stage3P, stage3P.innerHTML); trackedBlocks.push(stage3P); }
        stage3P.innerHTML = lang === 'en'
          ? '$1M Seed funding accelerates native apps on <strong>Apple App Store</strong> and <strong>Google Play Store</strong>. Sustaining 100,000 active paying users delivers enterprise-grade international cash flow.'
          : origBlocks.get(stage3P);
      }
    }

    pairs.forEach(function (item) {
      var el = document.querySelector(item.sel);
      if (!el) return;
      if (!origBlocks.has(el)) {
        origBlocks.set(el, el.innerHTML);
        trackedBlocks.push(el);
      }
      el.innerHTML = lang === 'en' ? item.en : origBlocks.get(el);
    });
  }

  function walkAndTranslate(lang) {
    observerPaused = true;
    try {
      applyRichTranslations(lang);

      var walker = document.createTreeWalker(
        document.body,
        NodeFilter.SHOW_TEXT,
        {
          acceptNode: function (node) {
            if (!node.parentElement) return NodeFilter.FILTER_REJECT;
            var tag = node.parentElement.tagName;
            if (tag === 'SCRIPT' || tag === 'STYLE' || tag === 'NOSCRIPT' || tag === 'CODE' || tag === 'PRE') {
              return NodeFilter.FILTER_REJECT;
            }
            if (node.parentElement.closest('[data-pia-lang-switcher], [translate="no"]')) {
              return NodeFilter.FILTER_REJECT;
            }
            if (!node.nodeValue || !node.nodeValue.trim()) {
              return NodeFilter.FILTER_REJECT;
            }
            return NodeFilter.FILTER_ACCEPT;
          }
        }
      );

      var nodes = [];
      var cur;
      while ((cur = walker.nextNode())) {
        nodes.push(cur);
      }

      if (lang === 'en') {
        nodes.forEach(function (n) {
          if (!origTextNodes.has(n)) {
            origTextNodes.set(n, n.nodeValue);
            trackedTextNodes.push(n);
          }
          var base = origTextNodes.get(n);
          var translated = translateTextString(base);
          if (translated && translated !== n.nodeValue) {
            n.nodeValue = translated;
          }
        });
      } else {
        trackedTextNodes.forEach(function (n) {
          if (origTextNodes.has(n)) {
            n.nodeValue = origTextNodes.get(n);
          }
        });
      }
    } finally {
      observerPaused = false;
    }
  }

  function injectStyles() {
    if (document.getElementById('pia-i18n-style')) return;
    var css = [
      '.pia-lang-switcher{display:inline-flex;align-items:center;gap:2px;padding:2px;border-radius:999px;background:rgba(15,23,42,.88);border:1px solid rgba(34,211,238,.38);backdrop-filter:blur(8px);vertical-align:middle}',
      '.pia-lang-btn{border:0;background:transparent;color:#cbd5e1;font-family:Inter,-apple-system,BlinkMacSystemFont,sans-serif;font-size:11px;font-weight:800;letter-spacing:.03em;padding:4px 9px;border-radius:999px;cursor:pointer;line-height:1.25;white-space:nowrap;transition:background .15s ease,color .15s ease}',
      '.pia-lang-btn:hover{color:#ffffff}',
      '.pia-lang-btn[aria-pressed="true"]{background:linear-gradient(135deg,#22d3ee 0%,#0ea5e9 100%);color:#020617}',
      '.pia-lang-floating{position:fixed;inset-block-end:1rem;inset-inline-start:1rem;z-index:9998;box-shadow:0 12px 28px rgba(0,0,0,.55)}',
      'html[data-theme="light"] .pia-lang-switcher{background:#e2e8f0;border-color:#94a3b8}',
      'html[data-theme="light"] .pia-lang-btn{color:#334155}',
      'html[data-theme="light"] .pia-lang-btn[aria-pressed="true"]{background:#0284c7;color:#ffffff}',
      '.pia-lang-btn:focus-visible{outline:2px solid #f0c975;outline-offset:2px}'
    ].join('');
    var st = document.createElement('style');
    st.id = 'pia-i18n-style';
    st.textContent = css;
    document.head.appendChild(st);
  }

  function createSwitcherEl(isFloating) {
    var wrap = document.createElement('div');
    wrap.className = 'pia-lang-switcher' + (isFloating ? ' pia-lang-floating' : '');
    wrap.setAttribute('data-pia-lang-switcher', '1');
    wrap.setAttribute('role', 'group');
    wrap.setAttribute('aria-label', 'Idioma / Language');
    wrap.setAttribute('translate', 'no');

    var btnEs = document.createElement('button');
    btnEs.type = 'button';
    btnEs.className = 'pia-lang-btn';
    btnEs.setAttribute('data-lang-opt', 'es');
    btnEs.textContent = '🇪🇸 ES';

    var btnEn = document.createElement('button');
    btnEn.type = 'button';
    btnEn.className = 'pia-lang-btn';
    btnEn.setAttribute('data-lang-opt', 'en');
    btnEn.textContent = '🇺🇸 EN';

    btnEs.addEventListener('click', function () { setLanguage('es'); });
    btnEn.addEventListener('click', function () { setLanguage('en'); });

    wrap.appendChild(btnEs);
    wrap.appendChild(btnEn);
    return wrap;
  }

  function syncSwitcherButtons(lang) {
    var btns = document.querySelectorAll('[data-pia-lang-switcher] [data-lang-opt]');
    btns.forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.getAttribute('data-lang-opt') === lang));
    });
  }

  function mountSwitchers() {
    var slots = document.querySelectorAll('[data-pia-lang-slot]');
    if (slots.length > 0) {
      slots.forEach(function (slot) {
        if (slot.getAttribute(ATTR_MARK) === '1') return;
        slot.setAttribute(ATTR_MARK, '1');
        slot.appendChild(createSwitcherEl(false));
      });
    } else if (!document.querySelector('[data-pia-lang-switcher]')) {
      document.body.appendChild(createSwitcherEl(true));
    }
    syncSwitcherButtons(currentLang);
  }

  function setLanguage(lang) {
    currentLang = (lang === 'en') ? 'en' : 'es';
    try {
      localStorage.setItem(STORAGE_KEY, currentLang);
    } catch (e) {}
    document.documentElement.lang = currentLang;
    syncSwitcherButtons(currentLang);
    walkAndTranslate(currentLang);
    document.dispatchEvent(new CustomEvent('prosperia:langchange', { detail: { lang: currentLang } }));
  }

  function getInitialLang() {
    try {
      var params = new URLSearchParams(window.location.search);
      var qLang = (params.get('lang') || '').toLowerCase();
      if (qLang === 'en' || qLang === 'es') {
        localStorage.setItem(STORAGE_KEY, qLang);
        return qLang;
      }
      var saved = (localStorage.getItem(STORAGE_KEY) || '').toLowerCase();
      if (saved === 'en' || saved === 'es') return saved;
    } catch (e) {}
    return 'es';
  }

  function init() {
    if (!document.body) return;
    injectStyles();
    currentLang = getInitialLang();
    mountSwitchers();
    if (currentLang === 'en') {
      setLanguage('en');
    } else {
      syncSwitcherButtons('es');
    }

    // Si algún componente dinámico añade bloques nuevos en inglés activo, reaplicar suavemente con debounce
    if (typeof MutationObserver !== 'undefined') {
      var moTimer = null;
      var mo = new MutationObserver(function (mutations) {
        if (observerPaused || currentLang !== 'en') return;
        var hasElements = false;
        for (var i = 0; i < mutations.length; i++) {
          if (mutations[i].addedNodes && mutations[i].addedNodes.length > 0) {
            hasElements = true;
            break;
          }
        }
        if (!hasElements) return;
        clearTimeout(moTimer);
        moTimer = setTimeout(function () {
          if (!observerPaused && currentLang === 'en') {
            walkAndTranslate('en');
          }
        }, 120);
      });
      mo.observe(document.body, { childList: true, subtree: true });
    }
  }

  window.setProsperiaLang = setLanguage;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

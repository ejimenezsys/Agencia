/**
 * PROSPERIA ENTERPRISE ADVISORY - CONTROLLER
 * Dynamic ROI Calculator, Interactive Assessment Engine (5 Questions x 4 Options),
 * Accessible Dialog, Tab Switching, Real-time Validation
 */

document.addEventListener('DOMContentLoaded', () => {
  initCineTunnel();
  initTabs();
  initROI();
  initModal();
  initHeaderScroll();
  initQuiz();
});

/* ---------------- Segment Tab Switching (PYMES vs Corporativos) ---------------- */
function switchSegmentTab(segment) {
  const pymeBtn = document.getElementById('tab-btn-pyme');
  const corpBtn = document.getElementById('tab-btn-corp');
  const pymePane = document.getElementById('tab-content-pyme');
  const corpPane = document.getElementById('tab-content-corp');

  if (!pymeBtn || !corpBtn || !pymePane || !corpPane) return;

  if (segment === 'pyme') {
    pymeBtn.classList.add('active');
    pymeBtn.setAttribute('aria-selected', 'true');
    corpBtn.classList.remove('active');
    corpBtn.setAttribute('aria-selected', 'false');

    pymePane.classList.add('active');
    pymePane.removeAttribute('hidden');
    corpPane.classList.remove('active');
    corpPane.setAttribute('hidden', 'true');
  } else {
    corpBtn.classList.add('active');
    corpBtn.setAttribute('aria-selected', 'true');
    pymeBtn.classList.remove('active');
    pymeBtn.setAttribute('aria-selected', 'false');

    corpPane.classList.add('active');
    corpPane.removeAttribute('hidden');
    pymePane.classList.remove('active');
    pymePane.setAttribute('hidden', 'true');
  }
}
window.switchSegmentTab = switchSegmentTab;

function initTabs() {
  const tabButtons = document.querySelectorAll('.tab-btn');
  tabButtons.forEach(btn => {
    btn.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {
        const isPyme = btn.id === 'tab-btn-pyme';
        switchSegmentTab(isPyme ? 'corp' : 'pyme');
        const targetBtn = document.getElementById(isPyme ? 'tab-btn-corp' : 'tab-btn-pyme');
        if (targetBtn) targetBtn.focus();
      }
    });
  });
}

/* ---------------- Dynamic ROI Calculator ---------------- */
function calculateROI() {
  const leadsSlider = document.getElementById('range-leads');
  const ticketSlider = document.getElementById('range-ticket');
  const payrollSlider = document.getElementById('range-payroll');

  if (!leadsSlider || !ticketSlider || !payrollSlider) return;

  const leads = parseInt(leadsSlider.value, 10);
  const ticket = parseInt(ticketSlider.value, 10);
  const payroll = parseInt(payrollSlider.value, 10);

  // Update slider badges
  const leadsBadge = document.getElementById('val-leads');
  const ticketBadge = document.getElementById('val-ticket');
  const payrollBadge = document.getElementById('val-payroll');

  if (leadsBadge) leadsBadge.textContent = `${leads.toLocaleString()} ops/leads`;
  if (ticketBadge) ticketBadge.textContent = `$${ticket.toLocaleString()} USD`;
  if (payrollBadge) payrollBadge.textContent = `$${payroll.toLocaleString()} USD`;

  // Financial impact formula:
  // - Speed-to-lead & autonomous closing recovers ~7.5% of total opportunities into closed revenue
  const extraClients = Math.max(1, Math.round(leads * 0.075));
  const extraRevenue = extraClients * ticket;

  // - AI automation of routine manual administrative/operations saves ~35% of operational payroll
  const payrollSavings = Math.round(payroll * 0.35);

  const monthlyImpact = extraRevenue + payrollSavings;
  const annualImpact = monthlyImpact * 12;

  // Update Results
  const resRevenue = document.getElementById('res-extra-revenue');
  const resSavings = document.getElementById('res-payroll-savings');
  const resAnnual = document.getElementById('res-annual-impact');

  if (resRevenue) resRevenue.textContent = `+$${extraRevenue.toLocaleString()} USD / mes`;
  if (resSavings) resSavings.textContent = `$${payrollSavings.toLocaleString()} USD / mes`;
  if (resAnnual) resAnnual.textContent = `+$${annualImpact.toLocaleString()} USD`;
}
window.calculateROI = calculateROI;

function initROI() {
  calculateROI();
}

/* ==========================================================================
   INTERACTIVE ASSESSMENT ENGINE: MADUREZ EN SUPER INTELIGENCIA (SI & AI)
   5 Strategic Questions · 4 Rich Dynamic Choices per Question
   ========================================================================== */

const quizData = [
  {
    category: "VELOCIDAD & ATENCIÓN COMERCIAL",
    question: "1. ¿Cuánto tarda hoy tu empresa en cotizar o responder a un prospecto calificado?",
    options: [
      {
        letter: "A",
        title: "Más de 24 a 48 horas hábiles",
        desc: "Dependemos de que un asesor o el dueño revise el correo, prepare la propuesta a mano y la envíe. Si escriben en fin de semana, esperan al lunes.",
        score: 1
      },
      {
        letter: "B",
        title: "Entre 2 y 6 horas durante horario laboral",
        desc: "Contamos con recepcionistas o vendedores, pero si están ocupados en llamadas o reuniones el prospecto tiene que esperar en fila.",
        score: 2
      },
      {
        letter: "C",
        title: "Menos de 30 minutos con plantillas básicas",
        desc: "Usamos respuestas rápidas de WhatsApp Business o un chatbot básico con botones estáticos, pero no cotiza productos complejos.",
        score: 3
      },
      {
        letter: "D",
        title: "Menos de 15 segundos con Agentes Autónomos 24/7",
        desc: "Un agente de IA califica al prospecto, cotiza en tiempo real conectado a nuestro sistema y agenda directamente en calendario.",
        score: 4
      }
    ]
  },
  {
    category: "ACCESO AL CONOCIMIENTO & SILOS",
    question: "2. ¿Dónde viven hoy los procedimientos, tarifas, contratos y datos clave de tu empresa?",
    options: [
      {
        letter: "A",
        title: "En la cabeza del dueño y colaboradores clave",
        desc: "Casi nada está documentado. Si alguien se enferma o renuncia, la operación se frena porque nadie más sabe cómo resolver el proceso.",
        score: 1
      },
      {
        letter: "B",
        title: "Dispersos en carpetas compartidas de Google Drive o Excel",
        desc: "Hay cientos de archivos desactualizados. Los empleados pasan horas preguntando en chats internos '¿dónde está la última versión?'.",
        score: 2
      },
      {
        letter: "C",
        title: "En un ERP o CRM tradicional (SAP, Salesforce, etc.)",
        desc: "La información está registrada, pero extraer un análisis cruzado para la Dirección toma días de trabajo de analistas de datos.",
        score: 3
      },
      {
        letter: "D",
        title: "En un Cerebro Corporativo Privado (RAG Enterprise)",
        desc: "Cualquier director o empleado autorizado consulta en lenguaje natural y recibe respuestas auditadas sobre contratos o ERPs en 3 segundos.",
        score: 4
      }
    ]
  },
  {
    category: "USO DE HERRAMIENTAS & AUTOMATIZACIÓN",
    question: "3. ¿Cómo utiliza hoy la Inteligencia Artificial tu equipo de trabajo?",
    options: [
      {
        letter: "A",
        title: "No la utilizamos formalmente en la empresa",
        desc: "Seguimos operando de manera 100% artesanal y manual por desconfianza o falta de guía técnica especializada.",
        score: 1
      },
      {
        letter: "B",
        title: "Cuentas individuales de ChatGPT / Copilot para redactar textos",
        desc: "Cada quien usa herramientas sueltas para corregir correos o hacer resúmenes, pero ningún proceso de negocio está automatizado.",
        score: 2
      },
      {
        letter: "C",
        title: "Automatizaciones aisladas en Zapier o Make",
        desc: "Conectamos formularios con hojas de cálculo o correos, pero no hay agentes autónomos tomando decisiones operativas ni razonamiento profundo.",
        score: 3
      },
      {
        letter: "D",
        title: "Redes de Agentes Autónomos con Supervisión Dual",
        desc: "Orquestamos modelos de frontera (Claude 3.7, GPT-5) que ejecutan tareas completas de compras, cotizaciones y atención con control de calidad.",
        score: 4
      }
    ]
  },
  {
    category: "DEPENDENCIA OPERATIVA DEL LIDERAZGO",
    question: "4. Si el dueño o los directores clave se desconectan 15 días, ¿qué le ocurre a la operación?",
    options: [
      {
        letter: "A",
        title: "La empresa entra en crisis inmediata",
        desc: "Las decisiones se paralizan, los pagos se frenan y los clientes reclaman. El negocio no puede operar sin la presencia física del líder.",
        score: 1
      },
      {
        letter: "B",
        title: "La operación sobrevive a duras penas con errores",
        desc: "Los mandos medios resuelven emergencias como pueden, pero la facturación cae y se acumula un cuello de botella masivo al regresar.",
        score: 2
      },
      {
        letter: "C",
        title: "Funciona pero se detiene la captación de nuevos clientes",
        desc: "El equipo entrega los servicios actuales, pero nadie vende ni cierra proyectos nuevos porque el proceso comercial depende del director.",
        score: 3
      },
      {
        letter: "D",
        title: "Opera y escala de manera totalmente predecible",
        desc: "Los flujos están sistematizados y los agentes autónomos atienden, cotizan y coordinan la operación bajo reglas y guardrails claros.",
        score: 4
      }
    ]
  },
  {
    category: "CIBERSEGURIDAD & SOBERANÍA DE DATOS",
    question: "5. ¿Qué control tiene la empresa sobre la información confidencial que el personal ingresa a IAs?",
    options: [
      {
        letter: "A",
        title: "Cero control (Shadow AI generalizado)",
        desc: "Los colaboradores pegan balances, contratos con clientes, listas de precios y datos sensibles en herramientas gratuitas sin supervisión.",
        score: 1
      },
      {
        letter: "B",
        title: "Hemos prohibido el uso de IA o dado advertencias verbales",
        desc: "Sabemos que el personal sigue usándola a escondidas en sus teléfonos porque la prohibición frena su velocidad de trabajo.",
        score: 2
      },
      {
        letter: "C",
        title: "Póliza básica de TI o suscripciones empresariales estándar",
        desc: "Contamos con cuentas de pago, pero no tenemos servidores privados, control de roles por departamento ni auditoría de fugas.",
        score: 3
      },
      {
        letter: "D",
        title: "Soberanía Total con Zero-Data Retention y RBAC",
        desc: "Nuestra infraestructura RAG opera en servidores privados aislados; ningún dato confidencial se utiliza para entrenar modelos públicos.",
        score: 4
      }
    ]
  }
];

let currentQuestionIndex = 0;
let userAnswers = {};

function initQuiz() {
  currentQuestionIndex = 0;
  userAnswers = {};
  renderQuestion();
}

function renderQuestion() {
  const currentQ = quizData[currentQuestionIndex];
  if (!currentQ) return;

  // Update progress
  const stepText = document.getElementById('quiz-question-counter');
  const catBadge = document.getElementById('quiz-category-badge');
  const progressBar = document.getElementById('quiz-progress-fill');
  const questionTitle = document.getElementById('quiz-question-text');
  const optionsGrid = document.getElementById('quiz-options-grid');
  const prevBtn = document.getElementById('quiz-prev-btn');
  const nextBtn = document.getElementById('quiz-next-btn');

  const progressPercent = ((currentQuestionIndex + 1) / quizData.length) * 100;
  if (stepText) stepText.textContent = `Pregunta ${currentQuestionIndex + 1} de ${quizData.length}`;
  if (catBadge) catBadge.textContent = currentQ.category;
  if (progressBar) progressBar.style.width = `${progressPercent}%`;
  if (questionTitle) questionTitle.textContent = currentQ.question;

  // Enable/disable previous
  if (prevBtn) prevBtn.disabled = currentQuestionIndex === 0;

  // Check if answer already exists
  const selectedScore = userAnswers[currentQuestionIndex];
  if (nextBtn) {
    nextBtn.disabled = selectedScore === undefined;
    nextBtn.textContent = (currentQuestionIndex === quizData.length - 1) ? 'Ver Diagnóstico Completo &rarr;' : 'Siguiente Pregunta &rarr;';
  }

  // Render 4 options
  if (optionsGrid) {
    optionsGrid.innerHTML = '';
    currentQ.options.forEach((opt, idx) => {
      const isSelected = selectedScore === opt.score;
      const optBtn = document.createElement('div');
      optBtn.className = `quiz-option-btn ${isSelected ? 'selected' : ''}`;
      optBtn.setAttribute('role', 'button');
      optBtn.setAttribute('tabindex', '0');
      optBtn.onclick = () => selectOption(opt.score);

      optBtn.innerHTML = `
        <div class="quiz-option-letter">${opt.letter}</div>
        <div class="quiz-option-content">
          <span class="quiz-option-title">${opt.title}</span>
          <span class="quiz-option-desc">${opt.desc}</span>
        </div>
      `;

      optionsGrid.appendChild(optBtn);
    });
  }
}

function selectOption(score) {
  userAnswers[currentQuestionIndex] = score;
  const nextBtn = document.getElementById('quiz-next-btn');
  if (nextBtn) nextBtn.disabled = false;

  // Re-render options to show highlight
  const currentQ = quizData[currentQuestionIndex];
  const optionsGrid = document.getElementById('quiz-options-grid');
  if (optionsGrid && currentQ) {
    const buttons = optionsGrid.querySelectorAll('.quiz-option-btn');
    buttons.forEach((btn, idx) => {
      if (currentQ.options[idx].score === score) {
        btn.classList.add('selected');
      } else {
        btn.classList.remove('selected');
      }
    });
  }
}

function handleQuizNext() {
  if (userAnswers[currentQuestionIndex] === undefined) return;

  if (currentQuestionIndex < quizData.length - 1) {
    currentQuestionIndex++;
    renderQuestion();
  } else {
    showQuizResults();
  }
}
window.handleQuizNext = handleQuizNext;

function handleQuizPrev() {
  if (currentQuestionIndex > 0) {
    currentQuestionIndex--;
    renderQuestion();
  }
}
window.handleQuizPrev = handleQuizPrev;

function showQuizResults() {
  let totalScore = 0;
  Object.values(userAnswers).forEach(val => totalScore += val);

  const card = document.getElementById('quiz-interactive-card');
  const resultView = document.getElementById('quiz-result-view');
  if (card) card.style.display = 'none';
  if (resultView) resultView.removeAttribute('hidden');

  const badgeLevel = document.getElementById('result-badge-level');
  const headlineTitle = document.getElementById('result-headline-title');
  const paragraphDesc = document.getElementById('result-paragraph-desc');
  const statHours = document.getElementById('result-stat-hours');
  const statMoney = document.getElementById('result-stat-money');
  const actionPlan = document.getElementById('result-action-plan');

  if (totalScore <= 8) {
    // Nivel 1: Caos Manual
    if (badgeLevel) badgeLevel.textContent = 'NIVEL 1: CAOS MANUAL & ALTA DEPENDENCIA (RIESGO CRÍTICO)';
    if (headlineTitle) headlineTitle.textContent = 'Su Empresa Depende Excesivamente de Personas Clave y Procesos Manuales Lentos';
    if (paragraphDesc) paragraphDesc.textContent = 'Su operación tiene cuellos de botella severos en cotizaciones y operaciones. Si el dueño o directores no están presentes, la facturación se detiene. Sus competidores automatizados están capturando a sus clientes en minutos.';
    if (statHours) statHours.textContent = '40 a 60 Horas / semana';
    if (statMoney) statMoney.textContent = '$12,000 - $30,000 USD / mes';
    if (actionPlan) actionPlan.textContent = 'Urgente: Desplegar el Sistema de Cotización y Atención Comercial con agentes de IA 24/7 y documentar los procesos centrales en ProsperIA CRM con control móvil.';
  } else if (totalScore <= 12) {
    // Nivel 2: Juguetes Aislados
    if (badgeLevel) badgeLevel.textContent = 'NIVEL 2: JUGUETES DE IA AISLADOS (PARÁLISIS POR HERRAMIENTAS)';
    if (headlineTitle) headlineTitle.textContent = 'Su Equipo Experimenta con Prompts, Pero Sus Procesos Centrales Siguen Siendo Manuales';
    if (paragraphDesc) paragraphDesc.textContent = 'Pagan cuentas de ChatGPT sueltas pero no hay impacto en el balance contable. Tienen silos de información y riesgo latente de fuga de datos corporativos (Shadow AI). Necesitan pasar de la curiosidad a una arquitectura de IA dirigida por consultoría.';
    if (statHours) statHours.textContent = '25 a 45 Horas / semana';
    if (statMoney) statMoney.textContent = '$8,000 - $22,000 USD / mes';
    if (actionPlan) actionPlan.textContent = 'Sustituir las suscripciones dispersas por un Cerebro Corporativo Privado (RAG) y conectar agentes autónomos a sus ERPs o flujos comerciales clave.';
  } else if (totalScore <= 16) {
    // Nivel 3: Automatización Parcial
    if (badgeLevel) badgeLevel.textContent = 'NIVEL 3: AUTOMATIZACIÓN EN SILOS (LISTO PARA ESCALAR)';
    if (headlineTitle) headlineTitle.textContent = 'Tienen Buena Eficiencia Básica, Pero Falta Orquestación Central y RAG Privado';
    if (paragraphDesc) paragraphDesc.textContent = 'Cuentan con flujos de trabajo funcionales, pero sus departamentos no están sincronizados por un cerebro central de IA. Hay duplicidad de esfuerzos analíticos y costo excesivo en horas de mandos medios.';
    if (statHours) statHours.textContent = '15 a 30 Horas / semana';
    if (statMoney) statMoney.textContent = '$15,000 - $45,000 USD / mes';
    if (actionPlan) actionPlan.textContent = 'Implementar RAG Privado Enterprise multi-modelo, agentes de IA con supervisión humana dual y gobernanza con Zero-Data Retention para reducir el OPEX departamental.';
  } else {
    // Nivel 4: Super Inteligencia Avanzada
    if (badgeLevel) badgeLevel.textContent = 'NIVEL 4: MADUREZ ALTA · LISTOS PARA GOBERNANZA Y ESCALA';
    if (headlineTitle) headlineTitle.textContent = 'Su Organización Tiene Cultura Digital Sólida: Es Momento de Consolidar Liderazgo';
    if (paragraphDesc) paragraphDesc.textContent = 'Cuentan con infraestructura avanzada. El siguiente paso estratégico es la optimización de costos de modelos, el enrutamiento híbrido local/cloud y la dirección de un Fractional Chief AI Officer.';
    if (statHours) statHours.textContent = 'Optimización Continua';
    if (statMoney) statMoney.textContent = 'Se calcula en el diagnóstico';
    if (actionPlan) actionPlan.textContent = 'Advisory mensual con ProsperIA para auditar modelos, adoptar como referencia las cuatro capas de control del White House Accord on Super Intelligence y liderar su sector.';
  }

  // Preload test results in lead form for seamless booking
  const bottleneckField = document.getElementById('lead-bottleneck');
  if (bottleneckField) {
    bottleneckField.value = `Resultado del Test de Madurez en IA: ${badgeLevel ? badgeLevel.textContent : ''}. Buscamos auditar y automatizar nuestros procesos para capturar el retorno estimado.`;
  }
}
window.showQuizResults = showQuizResults;

function restartQuiz() {
  const card = document.getElementById('quiz-interactive-card');
  const resultView = document.getElementById('quiz-result-view');
  if (card) card.style.display = 'flex';
  if (resultView) resultView.setAttribute('hidden', 'true');
  initQuiz();
}
window.restartQuiz = restartQuiz;

/* ---------------- Modal Dialog Controller ---------------- */
let diagnosticDialog = null;

function initModal() {
  diagnosticDialog = document.getElementById('diagnostic-modal');
  const openBtn = document.getElementById('btn-open-diagnostic');
  const closeBtn = document.getElementById('modal-close-btn');

  if (openBtn && diagnosticDialog) {
    openBtn.addEventListener('click', () => openDiagnosticModal('Navbar'));
  }

  if (closeBtn && diagnosticDialog) {
    closeBtn.addEventListener('click', closeDiagnosticModal);
  }

  // Close when clicking on backdrop
  if (diagnosticDialog) {
    diagnosticDialog.addEventListener('click', (e) => {
      const rect = diagnosticDialog.getBoundingClientRect();
      const isInDialog = (
        rect.top <= e.clientY &&
        e.clientY <= rect.top + rect.height &&
        rect.left <= e.clientX &&
        e.clientX <= rect.left + rect.width
      );
      if (!isInDialog) {
        closeDiagnosticModal();
      }
    });
  }
}

function openDiagnosticModal(context = 'General') {
  if (!diagnosticDialog) diagnosticDialog = document.getElementById('diagnostic-modal');
  if (!diagnosticDialog) return;

  const verticalSelect = document.getElementById('lead-vertical');
  if (verticalSelect) {
    if (context === 'PYMES' || context === 'Ruta1_Vertical') {
      verticalSelect.value = 'PymeMediana';
    } else if (context === 'Corporativo' || context === 'Ruta2_SVE90') {
      verticalSelect.value = 'Corporativo';
    } else if (context === 'Clinicas') {
      verticalSelect.value = 'ClinicaEspecializada';
    }
  }

  // Reset form views
  const form = document.getElementById('lead-form');
  const successBox = document.getElementById('form-success-message');
  if (form) {
    form.style.display = 'flex';
    form.removeAttribute('hidden');
  }
  if (successBox) {
    successBox.style.display = 'none';
    successBox.setAttribute('hidden', 'true');
  }

  diagnosticDialog.showModal();
}
window.openDiagnosticModal = openDiagnosticModal;

function closeDiagnosticModal() {
  if (diagnosticDialog) {
    diagnosticDialog.close();
  }
}
window.closeDiagnosticModal = closeDiagnosticModal;

/* ---------------- FAQ Accordion Toggle Control ---------------- */
let allFaqsExpanded = false;
function toggleAllFaqs() {
  const items = document.querySelectorAll('.faq-item');
  const btn = document.getElementById('btn-toggle-all-faqs');
  allFaqsExpanded = !allFaqsExpanded;
  
  items.forEach(item => {
    if (allFaqsExpanded) {
      item.setAttribute('open', '');
    } else {
      item.removeAttribute('open');
    }
  });

  if (btn) {
    btn.innerHTML = allFaqsExpanded 
      ? '<span>🔼 Replegar Todas las Preguntas</span>' 
      : '<span>🔽 Desplegar Todas las Preguntas</span>';
  }
}
window.toggleAllFaqs = toggleAllFaqs;

/* ---------------- Form Submission Handler (Sincronizado con GHL) ---------------- */
async function handleLeadSubmit(event, formType = 'modal') {
  event.preventDefault();
  const form = event.target;
  const submitBtn = form.querySelector('button[type="submit"]');
  const originalBtnHtml = submitBtn ? submitBtn.innerHTML : '';
  
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<span><i class="fas fa-spinner fa-spin"></i> Conectando con CRM y agendando...</span>`;
  }

  const name = (form.elements['name']?.value || '').trim();
  const role = (form.elements['role']?.value || '').trim();
  const company = (form.elements['company']?.value || '').trim();
  const website = (form.elements['website']?.value || '').trim();
  const email = (form.elements['email']?.value || '').trim();
  const phone = (form.elements['phone']?.value || '').trim();
  const revenue = form.elements['revenue']?.value || '';
  const employees = form.elements['employees']?.value || '';
  const selectedInterest = form.querySelector('input[name="modal_servicio_opcion"]:checked')?.value || form.elements['vertical']?.value || 'DiagnosticoGeneral';
  const bottleneck = (form.elements['bottleneck']?.value || '').trim();

  const parts = name.split(' ');
  const firstName = parts[0] || name;
  const lastName = parts.slice(1).join(' ') || '';

  try {
    sessionStorage.setItem('pia_name', name);
    sessionStorage.setItem('pia_email', email);
    sessionStorage.setItem('pia_phone', phone);
    sessionStorage.setItem('pia_company', company);
  } catch (e) {}

  let interestLabel = 'Diagnóstico Estratégico General (45 Min)';
  if (selectedInterest === 'Ruta1_Vertical' || selectedInterest === 'PymeMediana') {
    interestLabel = 'Ruta 1: Activación Vertical en 10 Días (Ventas & WhatsApp 24/7)';
  } else if (selectedInterest === 'Ruta2_SVE90' || selectedInterest === 'Corporativo') {
    interestLabel = 'Ruta 2: Transformación SVE90 (RAG Privado, ERPs y Empleados Digitales)';
  } else if (selectedInterest === 'FractionalCAIO') {
    interestLabel = 'Fractional Chief AI Officer (Dirección Externa para Directorio)';
  } else if (selectedInterest === 'ClinicaEspecializada') {
    interestLabel = 'Sector Salud: Sistema Paciente 360™';
  }

  const notes = `[DIAGNÓSTICO EN INTELIGENCIA ARTIFICIAL - TRÁFICO YOUTUBE]\nNombre: ${name}\nCargo: ${role}\nEmpresa: ${company}\nEmail: ${email}\nWhatsApp: ${phone}\nSitio Web: ${website}\nInterés Principal: ${interestLabel}\nFacturación: ${revenue}\nColaboradores: ${employees}\nMayor Cuello de Botella: ${bottleneck}`;

  const payload = {
    first_name: firstName,
    last_name: lastName,
    name: name,
    email: email,
    phone: phone,
    company: company || 'Empresa Privada',
    industry: 'Consultoría / Implementación de IA',
    team_size: employees || '',
    message: notes,
    source: "landing_youtube_consultoria",
    sms_consent: true
  };

  try {
    // Sincronización automática con FastAPI, SQLite, GoHighLevel y notificaciones automáticas
    const res = await fetch('/api/auth/contact', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    console.log('Lead sincronizado con GHL y Agencia ProsperIA:', res.status);
  } catch (err) {
    console.warn('Backend contact api offline o local:', err);
  }

  // Transición al Paso 2: Mensaje de Éxito y WhatsApp VIP directo
  const successBoxId = formType === 'inline' ? 'inline-form-success' : 'form-success-message';
  const successBox = document.getElementById(successBoxId);
  const waMsg = encodeURIComponent(`Hola Edward / ProsperIA, completé mi solicitud de Diagnóstico Ejecutivo de IA desde el canal de YouTube.\n\nNombre: ${name} (${role || 'Director'})\nEmpresa: ${company || 'Mi Empresa'}\nInterés: ${interestLabel}\nObjetivo: ${bottleneck}`);
  const waLink = `https://wa.me/17865573119?text=${waMsg}`;
  
  if (successBox) {
    successBox.innerHTML = `
      <div class="success-icon-badge" style="animation: bounce 1s infinite;">✓</div>
      <h4 style="font-size: 1.6rem; font-weight: 800; color: #ffffff; margin-bottom: 0.5rem;">🎉 ¡Diagnóstico Solicitado con Éxito!</h4>
      <p style="margin-bottom: 1.25rem; color: #cbd5e1; font-size: 0.95rem; line-height: 1.6; max-width: 520px; margin-inline: auto;">
        Estimado/a <strong>${name}</strong>, hemos registrado los antecedentes de <strong>${company || 'tu empresa'}</strong> y sincronizado tu solicitud en nuestro CRM comercial.
      </p>
      
      <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.35); border-radius: 16px; padding: 1.25rem; margin-bottom: 1.5rem; text-align: left;">
        <div style="font-weight: 700; color: #10b981; font-size: 0.85rem; text-transform: uppercase; margin-bottom: 0.3rem;">Paso 2 Obligatorio para Prioridad:</div>
        <p style="font-size: 0.85rem; color: #e2e8f0; line-height: 1.5; margin: 0;">
          Para agendar tu sesión de 45 minutos sin lista de espera, confirma directamente con Edward Jiménez en su WhatsApp comercial.
        </p>
      </div>

      <div style="display: flex; flex-direction: column; gap: 0.85rem; max-width: 440px; margin-inline: auto;">
        <a href="${waLink}" target="_blank" rel="noopener" class="btn btn-primary btn-block glow-btn" style="text-decoration:none; display: inline-flex; align-items: center; justify-content: center; gap: 0.65rem; background: #25D366; color: #052e16; font-weight: 800; padding: 1rem 1.5rem; border-radius: 12px; font-size: 1rem;">
          <i class="fab fa-whatsapp" style="font-size: 1.35rem;"></i>
          <span>📲 Coordinar Cita por WhatsApp Directo</span>
        </a>
        <a href="https://www.youtube.com/@AgenciaProsper_IA" target="_blank" rel="noopener" class="btn btn-secondary btn-sm" style="text-decoration:none; display: inline-flex; align-items: center; justify-content: center; gap: 0.5rem;">
          <i class="fab fa-youtube" style="color: #ef4444;"></i>
          <span>Seguir el Canal de YouTube @AgenciaProsper_IA</span>
        </a>
        ${formType === 'modal' ? '<button class="btn btn-secondary btn-sm" onclick="closeDiagnosticModal()" style="margin-top: 0.5rem;">Cerrar Ventana</button>' : ''}
      </div>
    `;
    form.style.display = 'none';
    successBox.style.display = 'block';
    successBox.removeAttribute('hidden');
  }

  form.reset();
  if (submitBtn) {
    submitBtn.disabled = false;
    submitBtn.innerHTML = originalBtnHtml;
  }
}
window.handleLeadSubmit = handleLeadSubmit;

/* ---------------- Header Blur on Scroll ---------------- */
function initHeaderScroll() {
  const header = document.getElementById('main-header');
  if (!header) return;

  window.addEventListener('scroll', () => {
    if (window.scrollY > 40) {
      header.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.6)';
      header.style.borderBottomColor = 'rgba(0, 240, 255, 0.2)';
    } else {
      header.style.boxShadow = 'none';
      header.style.borderBottomColor = 'rgba(255, 255, 255, 0.08)';
    }
  });
}

/* ==========================================================================
   3D Z-AXIS TUNNEL & EYE-PORTAL ENGINE (Ulises Aldana Architecture for ProsperIA)
   - Exact Eye Pupil Target: (52.97%, 24.64%) on edward_hero_depth.webp
   - Spring Physics (stiffness: 85, damping: 26, mass: 0.25)
   - CSS3D Perspective 1500px Chapters (-10500px -> 0px -> +760px)
   - Warp Speed Radial Particle Canvas & Floating Hero Particles
   ========================================================================== */

const EYE_ORIGIN = [0.5297, 0.2464]; // Exact centroid of Edward's viewer-right pupil
const QS_START_Z = -10500;
const XS_END_Z = 760;

// Chapter weights & offsets (exact formula from ulisesaldana.com: Eg=0.08, 0.92^a)
const CHAPTER_LEAD = 0.08;
const CHAPTER_WEIGHTS = (() => {
  const raw = Array.from({ length: 7 }, (_, a) => Math.pow(0.92, a));
  const sum = raw.reduce((s, a) => s + a, 0);
  return raw.map(s => s * (1 - CHAPTER_LEAD) / sum);
})();
const CHAPTER_STARTS = CHAPTER_WEIGHTS.reduce((acc, _, idx) => {
  acc.push(idx ? acc[idx - 1] + CHAPTER_WEIGHTS[idx - 1] : CHAPTER_LEAD);
  return acc;
}, []);

function clamp01(n) {
  return n < 0 ? 0 : n > 1 ? 1 : n;
}

// Piecewise linear interpolation (matches Framer Motion useTransform `G(val, inArr, outArr)`)
function mapRange(val, inArr, outArr) {
  if (val <= inArr[0]) return outArr[0];
  const last = inArr.length - 1;
  if (val >= inArr[last]) return outArr[last];
  for (let i = 1; i <= last; i++) {
    if (val <= inArr[i]) {
      const t = (val - inArr[i - 1]) / (inArr[i] - inArr[i - 1] || 1);
      return outArr[i - 1] + t * (outArr[i] - outArr[i - 1]);
    }
  }
  return outArr[last];
}

function getActiveChapterIndex(qProg) {
  let bestIdx = 0;
  let bestDist = Infinity;
  for (let a = 0; a < 6; a++) {
    const d = Math.abs(qProg - (CHAPTER_STARTS[a] + CHAPTER_WEIGHTS[a] * 0.65));
    if (d < bestDist) {
      bestDist = d;
      bestIdx = a;
    }
  }
  return bestIdx;
}

function scrollToTunnelPhase(normProgress) {
  const track = document.getElementById('cine-track');
  if (!track) return;
  const trackTop = track.getBoundingClientRect().top + window.scrollY;
  const scrollable = Math.max(1, track.offsetHeight - window.innerHeight);
  window.scrollTo({
    top: trackTop + clamp01(normProgress) * scrollable,
    behavior: 'smooth'
  });
}
window.scrollToTunnelPhase = scrollToTunnelPhase;

function scrollToChapter(chapterIdx) {
  const idx = Math.max(0, Math.min(5, chapterIdx));
  // Center of visibility of chapter `idx` is at ~48% of its [f, h] window
  const f = CHAPTER_STARTS[idx];
  const h = f + CHAPTER_WEIGHTS[idx] + CHAPTER_WEIGHTS[idx + 1];
  const qTarget = f + (h - f) * 0.48;
  // q maps from overall progress [0.34, 0.96]
  const overallTarget = 0.34 + qTarget * (0.96 - 0.34);
  scrollToTunnelPhase(overallTarget);
}
window.scrollToChapter = scrollToChapter;

function initCineTunnel() {
  const track = document.getElementById('cine-track');
  const sticky = document.getElementById('cine-sticky');
  if (!track || !sticky) return;

  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (prefersReduced) return;

  // DOM References
  const globalScrollLine = document.getElementById('global-scroll-line');
  const heroCapas = document.getElementById('hero-capas');
  const heroBokeh = document.getElementById('hero-bokeh');
  const heroPartWrap = document.getElementById('hero-particulas-wrap');
  const heroFigura = document.getElementById('hero-figura');
  const heroFiguraZoom = document.getElementById('hero-figura-zoom');
  const heroReticle = document.getElementById('hero-eye-reticle');
  const heroVelo = document.getElementById('hero-velo');
  const heroTunel = document.getElementById('hero-tunel');
  const heroTitulos = document.getElementById('hero-titulos');
  const heroTitulosBlur = document.getElementById('hero-titulos-blur');
  const heroCredenciales = document.getElementById('hero-credenciales');

  const warpWrap = document.getElementById('cine-particulas-wrap');
  const vueloOrigen = document.getElementById('vuelo-origen');
  const vueloCifras = document.getElementById('vuelo-cifras');
  const counterNodes = vueloCifras ? Array.from(vueloCifras.querySelectorAll('b[data-counter-target]')) : [];
  const ascensoMetodo = document.getElementById('ascenso-metodo');

  const capaEscape = document.getElementById('cine-capa-escape');
  const journeyIntro = document.getElementById('journey-intro');
  const chapterEls = Array.from(document.querySelectorAll('.journey-chapter')).map(el => ({
    root: el,
    copy: el.querySelector('.journey-copy'),
    letter: el.querySelector('.journey-letter'),
    visual: el.querySelector('.journey-visual')
  }));
  const journeySalida = document.getElementById('journey-salida');
  const stepBtns = Array.from(document.querySelectorAll('#journey-step-list .journey-step-btn'));
  const journeyProgBar = document.getElementById('journey-progress-bar');
  const journeyHint = document.getElementById('journey-scroll-hint');

  const cineCromo = document.getElementById('cine-cromo');
  const cineVelVal = document.getElementById('cine-vel-val');
  const cineBarraFill = document.getElementById('cine-barra-fill');

  let isMobile = window.matchMedia('(max-width: 860px)').matches;
  window.matchMedia('(max-width: 860px)').addEventListener('change', e => {
    isMobile = e.matches;
    measureEyeTransform();
  });

  // Dynamic Eye Target Measurement (exact math from `fE` in ulisesaldana.com)
  const eyeMetrics = { ox: '52.97%', oy: '24.64%', k: 16.5, dx: 0, dy: 0 };
  function measureEyeTransform() {
    if (!heroFigura || !sticky) return;
    const figW = heroFigura.offsetWidth;
    const figH = heroFigura.offsetHeight;
    const stW = sticky.clientWidth;
    const stH = sticky.clientHeight;
    if (!figW || !figH || !stW || !stH) return;

    const eyeX = heroFigura.offsetLeft + EYE_ORIGIN[0] * figW;
    const eyeY = heroFigura.offsetTop + EYE_ORIGIN[1] * figH;

    eyeMetrics.ox = (EYE_ORIGIN[0] * figW).toFixed(1) + 'px';
    eyeMetrics.oy = (EYE_ORIGIN[1] * figH).toFixed(1) + 'px';
    eyeMetrics.k = isMobile ? 13.5 : 17.5;
    eyeMetrics.dx = stW / 2 - eyeX;
    eyeMetrics.dy = stH / 2 - eyeY;

    if (heroFiguraZoom) {
      heroFiguraZoom.style.transformOrigin = `${eyeMetrics.ox} ${eyeMetrics.oy}`;
    }
  }
  measureEyeTransform();
  const ro = new ResizeObserver(measureEyeTransform);
  if (heroFigura) ro.observe(heroFigura);
  ro.observe(sticky);

  // Subtle Pointer Parallax on Hero Portrait
  let mouseX = 0;
  let mouseY = 0;
  window.addEventListener('pointermove', e => {
    if (isMobile) return;
    mouseX = (e.clientX / window.innerWidth - 0.5) * 2;
    mouseY = (e.clientY / window.innerHeight - 0.5) * 2;
  }, { passive: true });

  // Spring State (stiffness: 85, damping: 26, mass: 0.25)
  let targetProgress = 0;
  let smoothProgress = 0;
  let velocity = 0;
  let currentActiveChap = -1;
  const warpProgressRef = { current: 0 };

  function computeRawProgress() {
    const rect = track.getBoundingClientRect();
    const scrollable = Math.max(1, track.offsetHeight - window.innerHeight);
    targetProgress = clamp01(-rect.top / scrollable);

    // Global page progress line
    if (globalScrollLine) {
      const docMax = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
      globalScrollLine.style.height = (clamp01(window.scrollY / docMax) * 100).toFixed(1) + '%';
    }
  }
  computeRawProgress();
  window.addEventListener('scroll', computeRawProgress, { passive: true });
  window.addEventListener('resize', computeRawProgress, { passive: true });

  // Render Frame at 60fps
  function applyTunnelFrame(O) {
    // Phase 1: Hero & Eye Zoom [0.00 -> 0.23]
    const K = clamp01(O / 0.34); // Normalized pre-chapter progress [0..1]
    const Zn = 0.055; // Eye zoom start inside K
    const an = 0.58;  // Eye zoom end inside K

    const bokehScale = mapRange(K, [0, an], [1.04, 1.34]);
    const bokehOp = mapRange(K, [0, Zn, 0.45], [1, 1, 0]);
    const veloOp = mapRange(K, [0, 0.16, 0.38], [1, 1, 0]);
    const tunelOp = mapRange(K, [0.18, 0.42, an + 0.04, an + 0.16], [0, 1, 1, 0]);
    const partOp = mapRange(K, [0, 0.06, 0.26, 0.45], [0.4, 1, 0.7, 0]);

    const zoomLinear = clamp01((K - Zn) / (an - Zn));
    const zoomScale = 1 + (eyeMetrics.k - 1) * Math.pow(zoomLinear, 2.5);
    const zoomDx = eyeMetrics.dx * Math.pow(zoomLinear, 1.55);
    const zoomDy = eyeMetrics.dy * Math.pow(zoomLinear, 1.55);
    const figOp = mapRange(K, [an - 0.08, an + 0.02], [1, 0]);
    const heroCapasOp = mapRange(O, [0.22, 0.26], [1, 0]);

    const parallaxFade = mapRange(K, [0, Zn * 1.4], [1, 0]);
    const px = mouseX * 8 * parallaxFade;
    const py = mouseY * 5 * parallaxFade;

    if (heroCapas) heroCapas.style.opacity = heroCapasOp.toFixed(3);
    if (heroBokeh) {
      heroBokeh.style.opacity = bokehOp.toFixed(3);
      heroBokeh.style.transform = `translate3d(${(mouseX * -14).toFixed(1)}px, ${(mouseY * -9).toFixed(1)}px, 0) scale(${bokehScale.toFixed(3)})`;
    }
    if (heroPartWrap) {
      heroPartWrap.style.opacity = partOp.toFixed(3);
    }
    if (heroVelo) heroVelo.style.opacity = veloOp.toFixed(3);
    if (heroTunel) heroTunel.style.opacity = tunelOp.toFixed(3);

    if (heroFigura) {
      heroFigura.style.opacity = figOp.toFixed(3);
      heroFigura.style.transform = `translate3d(${px.toFixed(1)}px, ${py.toFixed(1)}px, 0)`;
    }
    if (heroFiguraZoom) {
      heroFiguraZoom.style.transform = `translate3d(${zoomDx.toFixed(1)}px, ${zoomDy.toFixed(1)}px, 0) scale(${zoomScale.toFixed(3)})`;
    }
    if (heroReticle) {
      const retOp = mapRange(zoomLinear, [0, 0.08, 0.42, 0.65], [0.75, 1, 0.9, 0]);
      heroReticle.style.opacity = retOp.toFixed(3);
    }

    // Hero Titles fade & upward glide
    const titOp = mapRange(K, [0, 0.03, 0.15, 0.25], [1, 1, 1, 0]);
    const titY = mapRange(K, [0, 0.28], [0, -48]);
    const titBlurOp = mapRange(K, [0.16, 0.21, 0.27], [0, 0.55, 0]);
    if (heroTitulos) {
      heroTitulos.style.opacity = titOp.toFixed(3);
      heroTitulos.style.transform = isMobile
        ? `translate3d(0, ${titY.toFixed(1)}px, 0)`
        : `translate3d(0, calc(-50% + ${titY.toFixed(1)}px), 0)`;
      heroTitulos.style.pointerEvents = titOp > 0.25 ? 'auto' : 'none';
    }
    if (heroTitulosBlur) {
      heroTitulosBlur.style.opacity = titBlurOp.toFixed(3);
      heroTitulosBlur.style.transform = isMobile
        ? `translate3d(0, ${titY.toFixed(1)}px, 0)`
        : `translate3d(0, calc(-50% + ${titY.toFixed(1)}px), 0)`;
    }
    if (heroCredenciales) {
      heroCredenciales.style.opacity = titOp.toFixed(3);
    }

    // Phase 2: Mid-Tunnel Flight Statements & Animated Counters [0.17 -> 0.35]
    const origenWin = [0.50, 0.56, 0.72, 0.78];
    const cifrasWin = [0.56, 0.62, 0.78, 0.84];
    const metodoWin = [0.83, 0.88, 0.96, 1.0];

    const origenOp = mapRange(K, origenWin, [0, 1, 1, 0]);
    const origenY = mapRange(K, [origenWin[0], origenWin[3]], [26, -26]);
    if (vueloOrigen) {
      vueloOrigen.style.opacity = origenOp.toFixed(3);
      vueloOrigen.style.transform = `translate3d(0, ${origenY.toFixed(1)}px, 0)`;
    }

    const cifrasOp = mapRange(K, cifrasWin, [0, 1, 1, 0]);
    const cifrasY = mapRange(K, [cifrasWin[0], cifrasWin[3]], [28, -28]);
    if (vueloCifras) {
      vueloCifras.style.opacity = cifrasOp.toFixed(3);
      vueloCifras.style.transform = `translate3d(0, ${cifrasY.toFixed(1)}px, 0)`;
    }

    if (cifrasOp > 0.01 && counterNodes.length) {
      const cProg = clamp01((K - cifrasWin[0]) / (cifrasWin[2] - cifrasWin[0]));
      const eased = 1 - Math.pow(1 - cProg, 2.4);
      counterNodes.forEach(node => {
        const target = parseInt(node.getAttribute('data-counter-target') || '0', 10);
        const prefix = node.getAttribute('data-prefix') || '';
        const suffix = node.getAttribute('data-suffix') || '';
        node.textContent = prefix + Math.round(target * eased) + suffix;
      });
    }

    const metodoOp = mapRange(K, metodoWin, [0, 1, 1, 0]);
    const metodoY = mapRange(K, [metodoWin[0], metodoWin[3]], [30, -30]);
    if (ascensoMetodo) {
      ascensoMetodo.style.opacity = metodoOp.toFixed(3);
      ascensoMetodo.style.transform = `translate3d(0, ${metodoY.toFixed(1)}px, 0)`;
    }

    // Phase 3: 6-Chapter 3D Z-Axis Tunnel [0.33 -> 0.98]
    const q = clamp01((O - 0.34) / (0.96 - 0.34));
    warpProgressRef.current = clamp01((O - 0.14) / 0.84);

    const warpOp = mapRange(O, [0.12, 0.20, 0.94, 0.995], [0, 1, 1, 0]);
    if (warpWrap) warpWrap.style.opacity = warpOp.toFixed(3);

    const escapeLayerOp = mapRange(O, [0.325, 0.345, 0.965, 0.992], [0, 1, 1, 0]);
    if (capaEscape) {
      capaEscape.style.opacity = escapeLayerOp.toFixed(3);
      capaEscape.style.pointerEvents = escapeLayerOp > 0.2 ? 'auto' : 'none';
    }

    const introOp = mapRange(q, [0.0, 0.06, 0.12], [1, 1, 0]);
    if (journeyIntro) journeyIntro.style.opacity = introOp.toFixed(3);

    // Update each of the 6 3D Chapters (exact `tE` math from ulisesaldana.com)
    chapterEls.forEach((ch, r) => {
      const f = CHAPTER_STARTS[r];
      const h = f + CHAPTER_WEIGHTS[r] + CHAPTER_WEIGHTS[r + 1];
      const m = QS_START_Z - r * 1200;
      const y = XS_END_Z + r * 220;
      const v = clamp01((q - f) / (h - f));

      const zPos = mapRange(v, [0, 0.17, 0.30, 0.37, 0.62, 0.70, 0.84, 1], [m, m * 0.52, -1500, 0, 60, 320, 620, y]);
      const op = mapRange(v, [0, 0.12, 0.20, 0.34, 0.64, 0.76, 0.86], [0, 0, 0.34, 1, 1, 0.3, 0]);
      const blurVal = mapRange(v, [0, 0.30, 0.37, 0.62, 0.72, 1], [10, 4, 0, 0, 5.5, 12]);
      const splitL = clamp01((v - 0.62) / (1 - 0.62));

      ch.root.style.opacity = op.toFixed(3);
      if (op <= 0.005) {
        ch.root.style.visibility = 'hidden';
        return;
      }
      ch.root.style.visibility = 'visible';
      ch.root.style.transform = `translate3d(0px, 0px, ${zPos.toFixed(1)}px)`;

      const copyX = isMobile ? '0vw' : (-splitL * 74).toFixed(2) + 'vw';
      const copyY = isMobile ? (-splitL * 30).toFixed(2) + 'vh' : '0vh';
      const visX = isMobile ? '0vw' : (splitL * 70).toFixed(2) + 'vw';
      const visY = isMobile ? (splitL * 34).toFixed(2) + 'vh' : '0vh';

      const copyBlur = blurVal * 0.6 < 0.1 ? 'none' : `blur(${(blurVal * 0.6).toFixed(2)}px)`;
      const visBlur = blurVal < 0.06 ? 'none' : `blur(${blurVal.toFixed(2)}px)`;

      if (ch.copy) {
        ch.copy.style.transform = `translate3d(${copyX}, ${copyY}, -70px)`;
        ch.copy.style.filter = copyBlur;
      }
      if (ch.visual) {
        ch.visual.style.transform = `translate3d(${visX}, ${visY}, 150px)`;
        ch.visual.style.filter = visBlur;
      }
      if (ch.letter) {
        const clipPct = mapRange(v, [0.18, 0.40], [100, 0]);
        ch.letter.style.clipPath = `inset(0 0 0 ${clipPct.toFixed(1)}%)`;
      }
    });

    // Exit CTA button at end of tunnel
    const salidaOp = mapRange(q, [0.92, 0.96], [0, 1]);
    const salidaY = mapRange(q, [0.92, 0.98], [26, 0]);
    if (journeySalida) {
      journeySalida.style.opacity = salidaOp.toFixed(3);
      journeySalida.style.transform = `translate3d(0, calc(-50% + ${salidaY.toFixed(1)}px), 0)`;
      journeySalida.style.pointerEvents = salidaOp > 0.4 ? 'auto' : 'none';
    }

    // Step indicator & progress bar
    const activeChap = getActiveChapterIndex(q);
    if (activeChap !== currentActiveChap) {
      currentActiveChap = activeChap;
      stepBtns.forEach((btn, idx) => {
        btn.classList.toggle('is-active', idx === activeChap);
      });
    }
    if (journeyProgBar) {
      journeyProgBar.style.width = (q * 100).toFixed(1) + '%';
    }
    if (journeyHint) {
      journeyHint.style.opacity = mapRange(q, [0.08, 0.20], [1, 0]).toFixed(2);
    }

    // HUD Chrome & Speedometer
    const cromoOp = mapRange(O, [0.005, 0.025, 0.965, 0.998], [0, 1, 1, 0]);
    if (cineCromo) cineCromo.style.opacity = cromoOp.toFixed(3);
    if (cineBarraFill) cineBarraFill.style.transform = `scaleX(${O.toFixed(4)})`;
    if (cineVelVal) {
      const velNum = 1 + clamp01(O / 0.94) * 9.0;
      cineVelVal.textContent = velNum.toFixed(1);
    }
  }

  // Spring Physics Loop (stiffness: 85, damping: 26, mass: 0.25)
  let lastTime = performance.now();
  function tickSpring(now) {
    const dt = Math.min(0.04, (now - lastTime) / 1000);
    lastTime = now;

    const stiffness = 85;
    const damping = 26;
    const mass = 0.25;
    const force = -stiffness * (smoothProgress - targetProgress) - damping * velocity;
    const accel = force / mass;
    velocity += accel * dt;
    smoothProgress += velocity * dt;

    if (Math.abs(targetProgress - smoothProgress) < 0.00005 && Math.abs(velocity) < 0.00005) {
      smoothProgress = targetProgress;
      velocity = 0;
    }

    applyTunnelFrame(clamp01(smoothProgress));
    requestAnimationFrame(tickSpring);
  }
  requestAnimationFrame(tickSpring);

  // Initialize Canvases
  initHeroParticlesCanvas(isMobile);
  initWarpParticlesCanvas(warpProgressRef, isMobile);
}

/* ---------------- Floating Hero Neural Particles Canvas (`dE`) ---------------- */
function initHeroParticlesCanvas(isMobile) {
  const canvas = document.getElementById('hero-particulas-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  const count = isMobile ? 32 : 58;

  const spawn = () => ({
    x: Math.random(),
    y: Math.random(),
    r: Math.random() * 2.1 + 0.7,
    vx: (Math.random() - 0.5) * 0.012,
    vy: -(Math.random() * 0.015 + 0.004),
    a: Math.random() * 0.5 + 0.2,
    f: Math.random() * Math.PI * 2,
    capa: Math.random() < 0.4 ? 0.55 : 1,
    cyan: Math.random() > 0.35
  });

  const particles = Array.from({ length: count }, spawn);

  function resize() {
    const r = canvas.getBoundingClientRect();
    canvas.width = Math.max(1, Math.round(r.width * dpr));
    canvas.height = Math.max(1, Math.round(r.height * dpr));
  }
  resize();
  new ResizeObserver(resize).observe(canvas);

  let prev = performance.now();
  function draw(now) {
    const dt = Math.min(0.05, (now - prev) / 1000);
    prev = now;
    const W = canvas.width;
    const H = canvas.height;
    ctx.clearRect(0, 0, W, H);

    for (const p of particles) {
      p.x += p.vx * dt;
      p.y += p.vy * dt;
      p.f += dt * 1.1;
      if (p.y < -0.05) {
        Object.assign(p, spawn(), { y: 1.05 });
      }
      const alpha = p.a * (0.55 + 0.45 * Math.sin(p.f));
      const rad = p.r * dpr * p.capa;
      const gx = p.x * W;
      const gy = p.y * H;
      const grad = ctx.createRadialGradient(gx, gy, 0, gx, gy, rad * 4);
      const rgb = p.cyan ? '0, 240, 255' : '168, 85, 247';
      grad.addColorStop(0, `rgba(${rgb}, ${(alpha * 0.85).toFixed(3)})`);
      grad.addColorStop(1, `rgba(${rgb}, 0)`);
      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.arc(gx, gy, rad * 4, 0, Math.PI * 2);
      ctx.fill();
    }
    requestAnimationFrame(draw);
  }
  requestAnimationFrame(draw);
}

/* ---------------- Warp Speed Z-Tunnel Canvas (`uE` from ulisesaldana.com) ---------------- */
function initWarpParticlesCanvas(progressRef, isMobile) {
  const canvas = document.getElementById('cine-warp-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  const count = isMobile ? 68 : 138;

  const spawn = () => {
    const R = Math.random();
    return {
      a: Math.random() * Math.PI * 2,
      r: Math.random() * 0.16 + 0.02,
      v: 0.3 + R * 1.35,
      b: (0.22 + R * 0.78) * (Math.random() * 0.4 + 0.6),
      capa: R,
      hue: Math.random() > 0.28 ? '0, 240, 255' : '168, 85, 247'
    };
  };

  const streaks = Array.from({ length: count }, spawn);

  function resize() {
    const r = canvas.getBoundingClientRect();
    canvas.width = Math.max(1, Math.round(r.width * dpr));
    canvas.height = Math.max(1, Math.round(r.height * dpr));
  }
  resize();
  new ResizeObserver(resize).observe(canvas);

  let prev = performance.now();
  function draw(now) {
    const dt = Math.min(0.05, (now - prev) / 1000);
    prev = now;
    const V = clamp01(progressRef.current);
    const P = 0.06 + V * 0.32;
    const A = clamp01((V - 0.8) / 0.2);

    const W = canvas.width;
    const H = canvas.height;
    const cx = W / 2;
    const cy = H * 0.5;
    const maxR = Math.hypot(W, H) / 2;

    ctx.clearRect(0, 0, W, H);
    ctx.lineCap = 'round';

    for (const s of streaks) {
      s.r += dt * P * s.v * (1 + A * 3.4);
      if (s.r > 1.25) {
        Object.assign(s, spawn());
      }
      const tailLen = (0.008 + V * 0.052 + A * 0.15) * (0.35 + s.capa);
      const r0 = Math.max(0, s.r - tailLen);
      const x0 = cx + Math.cos(s.a) * r0 * maxR;
      const y0 = cy + Math.sin(s.a) * r0 * maxR;
      const x1 = cx + Math.cos(s.a) * s.r * maxR;
      const y1 = cy + Math.sin(s.a) * s.r * maxR;
      const fade = Math.min(1, s.r * 3.2) * (1 - clamp01((s.r - 0.95) / 0.3));
      const alpha = (fade * s.b * (0.36 + A * 0.6)).toFixed(3);

      ctx.strokeStyle = `rgba(${s.hue}, ${alpha})`;
      ctx.lineWidth = (0.55 + s.capa * 1.75 + A * 0.9) * dpr;
      ctx.beginPath();
      ctx.moveTo(x0, y0);
      ctx.lineTo(x1, y1);
      ctx.stroke();
    }
    requestAnimationFrame(draw);
  }
  requestAnimationFrame(draw);
}

/* ---------------- Interactive Tool Tab Switcher (ROI vs Test) ---------------- */
function switchInteractiveTool(tool = 'roi') {
  const roiPanel = document.getElementById('tool-panel-roi');
  const quizPanel = document.getElementById('test-madurez');
  const btnRoi = document.getElementById('tab-btn-roi');
  const btnQuiz = document.getElementById('tab-btn-quiz');

  if (tool === 'quiz') {
    if (roiPanel) roiPanel.setAttribute('hidden', 'true');
    if (quizPanel) quizPanel.removeAttribute('hidden');
    if (btnRoi) {
      btnRoi.classList.remove('is-active');
      btnRoi.setAttribute('aria-selected', 'false');
    }
    if (btnQuiz) {
      btnQuiz.classList.add('is-active');
      btnQuiz.setAttribute('aria-selected', 'true');
    }
  } else {
    if (quizPanel) quizPanel.setAttribute('hidden', 'true');
    if (roiPanel) roiPanel.removeAttribute('hidden');
    if (btnQuiz) {
      btnQuiz.classList.remove('is-active');
      btnQuiz.setAttribute('aria-selected', 'false');
    }
    if (btnRoi) {
      btnRoi.classList.add('is-active');
      btnRoi.setAttribute('aria-selected', 'true');
    }
  }
}
window.switchInteractiveTool = switchInteractiveTool;



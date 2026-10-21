/**
 * PROSPERIA ENTERPRISE ADVISORY - CONTROLLER
 * Dynamic ROI Calculator, Interactive Assessment Engine (5 Questions x 4 Options),
 * Accessible Dialog, Tab Switching, Real-time Validation
 */

document.addEventListener('DOMContentLoaded', () => {
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

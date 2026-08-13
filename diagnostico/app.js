document.addEventListener('DOMContentLoaded', () => {
  // State variables
  let currentStep = 1;
  const totalSteps = 4;
  
  const state = {
    leadsVolume: 100,
    speedToLead: null,
    storage: null,
    auditing: null
  };

  // DOM Elements
  const steps = document.querySelectorAll('.step');
  const progressBar = document.getElementById('progress-bar');
  const btnPrev = document.getElementById('btn-prev');
  const btnNext = document.getElementById('btn-next');
  
  // Step 1: Range controls
  const rangeInput = document.getElementById('leads-range');
  const rangeDisplay = document.getElementById('range-display');
  
  if (rangeInput) {
    rangeInput.addEventListener('input', (e) => {
      state.leadsVolume = parseInt(e.target.value, 10);
      if (rangeDisplay) rangeDisplay.textContent = state.leadsVolume;
    });
  }

  // Option selection logic (Steps 2, 3, 4)
  const optionButtons = document.querySelectorAll('.option-btn');
  optionButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const stepName = btn.dataset.step;
      const optionValue = btn.dataset.value;
      
      // Deselect siblings in the same step
      const siblings = document.querySelectorAll(`.option-btn[data-step="${stepName}"]`);
      siblings.forEach(s => s.classList.remove('selected'));
      
      // Select clicked
      btn.classList.add('selected');
      state[stepName] = optionValue;
      
      // Enable NEXT button
      btnNext.disabled = false;
    });
  });

  // Navigation Logic
  btnPrev.addEventListener('click', () => {
    if (currentStep > 1) {
      navigateStep(currentStep - 1);
    }
  });

  btnNext.addEventListener('click', () => {
    if (currentStep < totalSteps) {
      navigateStep(currentStep + 1);
    } else {
      // Calculate and show results
      generateDiagnostic();
    }
  });

  function navigateStep(targetStep) {
    steps.forEach(step => step.classList.remove('active'));
    document.getElementById(`step-${targetStep}`).classList.add('active');
    
    currentStep = targetStep;
    
    // Update progress bar
    const progressPercent = (currentStep / totalSteps) * 100;
    progressBar.style.width = `${progressPercent}%`;
    
    // Toggle prev button
    btnPrev.style.visibility = (currentStep === 1) ? 'hidden' : 'visible';
    
    // Toggle next button label and state
    if (currentStep === totalSteps) {
      btnNext.textContent = 'Generar Diagnóstico';
    } else {
      btnNext.textContent = 'Siguiente';
    }
    
    // Check if step requires input selection to proceed
    validateStepState();
  }

  function validateStepState() {
    if (currentStep === 1) {
      btnNext.disabled = false; // Range is pre-set
    } else if (currentStep === 2) {
      btnNext.disabled = (state.speedToLead === null);
    } else if (currentStep === 3) {
      btnNext.disabled = (state.storage === null);
    } else if (currentStep === 4) {
      btnNext.disabled = (state.auditing === null);
    }
  }

  // Diagnostic generation and rendering
  function generateDiagnostic() {
    // Hide form & header
    document.getElementById('form-card').style.display = 'none';
    const brandHeader = document.querySelector('.brand-header');
    if (brandHeader) brandHeader.style.display = 'none';
    
    // Show results dashboard
    const resultsDashboard = document.getElementById('results-dashboard');
    resultsDashboard.classList.add('active');
    resultsDashboard.style.display = 'block';
    
    // Calculate values
    let speedLeak = 5;
    if (state.speedToLead === '15min') speedLeak = 15;
    else if (state.speedToLead === '1hour') speedLeak = 30;
    else if (state.speedToLead === '4hours') speedLeak = 55;
    
    let storageLeak = 5;
    if (state.storage === 'excels') storageLeak = 27;
    else if (state.storage === 'papers') storageLeak = 40;
    else if (state.storage === 'mind') storageLeak = 50;
    
    let auditingBonus = 0;
    if (state.auditing === 'none') auditingBonus = 10;
    else if (state.auditing === 'some') auditingBonus = 5;
    
    // Leak formula calculations
    const leakPercent = Math.min(95, speedLeak + storageLeak + auditingBonus);
    const scoreVal = 100 - leakPercent;
    
    const leadsLost = Math.round(state.leadsVolume * (leakPercent / 100));
    const revenueLost = leadsLost * 150; // $150 USD per B2B lead ticket
    
    // Animate score value counter
    animateCounter('score-val', scoreVal, '%');
    
    // Apply score color coding
    const scoreElement = document.getElementById('score-val');
    scoreElement.className = 'score-num'; // Reset
    if (scoreVal < 40) scoreElement.classList.add('score-critical');
    else if (scoreVal < 70) scoreElement.classList.add('score-warning');
    else scoreElement.classList.add('score-good');
    
    // Animate metrics counters
    animateCounter('metric-lost-leads', leadsLost, '');
    animateCounter('metric-revenue', revenueLost, ' USD', true);
    
    // Render dynamic SVG funnel values
    updateSvgFunnel(state.leadsVolume, leadsLost);
    
    // Render contextual recommendations
    renderRecommendations(leakPercent);
  }

  function animateCounter(id, targetVal, suffix = '', isCurrency = false) {
    const el = document.getElementById(id);
    if (!el) return;
    
    let currentVal = 0;
    const duration = 1200; // ms
    const frameRate = 1000 / 60; // 60fps
    const totalFrames = duration / frameRate;
    const increment = targetVal / totalFrames;
    
    const timer = setInterval(() => {
      currentVal += increment;
      if (currentVal >= targetVal) {
        currentVal = targetVal;
        clearInterval(timer);
      }
      
      let displayVal = Math.round(currentVal);
      if (isCurrency) {
        displayVal = displayVal.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).replace('$', '$ ');
      }
      el.textContent = `${displayVal}${suffix}`;
    }, frameRate);
  }

  function updateSvgFunnel(total, lost) {
    const wins = total - lost;
    const lostPercent = (lost / total) * 100;
    
    // Update SVG heights / scales
    const lostText = document.getElementById('funnel-lost-text');
    const winText = document.getElementById('funnel-win-text');
    
    if (lostText) lostText.textContent = `${Math.round(lostPercent)}% leads perdidos`;
    if (winText) winText.textContent = `${100 - Math.round(lostPercent)}% leads retenidos`;
  }

  function renderRecommendations(leakPercent) {
    const container = document.getElementById('rec-list-container');
    if (!container) return;
    
    let recs = [];
    
    // Condition 1: Speed-to-Lead issues
    if (state.speedToLead === '1hour' || state.speedToLead === '4hours') {
      recs.push({
        title: "Automatización de Speed-to-Lead con WhatsApp IA",
        desc: "Implementa el Empleado Digital de Prosper IA. Responde y cualifica leads en menos de 5 minutos directamente en WhatsApp, salvando hasta el 40% de leads perdidos."
      });
    }
    
    // Condition 2: Storage system issues
    if (state.storage === 'excels' || state.storage === 'papers') {
      recs.push({
        title: "Migración de Hojas de Cálculo a CRM Centralizado",
        desc: "Migrar tus Excels sueltos a un CRM unificado evita la pérdida del 27% de las oportunidades comerciales y da visibilidad total al forecast."
      });
    }
    
    // Condition 3: Audit issues
    if (state.auditing === 'none' || state.auditing === 'some') {
      recs.push({
        title: "Auditoría de Conversaciones con PassportAI",
        desc: "Graba y transcribe llamadas de forma automatizada. PassportAI analiza el desempeño de tus vendedores para asegurar el pitch comercial óptimo."
      });
    }
    
    // Default fallback if everything is optimal
    if (recs.length === 0) {
      recs.push({
        title: "Evolución a Empresa Aumentada",
        desc: "Tu estructura básica es buena. Agenda una sesión para integrar PassportAI en tu flujo y comenzar a escalar el volumen de leads mediante segmentación predictiva."
      });
    }
    
    container.innerHTML = recs.map((r, i) => `
      <div class="rec-item">
        <div class="rec-icon">${i + 1}</div>
        <div class="rec-text">
          <h4>${r.title}</h4>
          <p>${r.desc}</p>
        </div>
      </div>
    `).join('');
  }

  // Initialize
  navigateStep(1);
});

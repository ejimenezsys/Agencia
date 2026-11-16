/**
 * Asistente Oficial Fusión Total (Chat + Voz en Vivo) — Agencia Prosper IA LLC
 * Conectado vía API a PassportAI (bot: asesor-comercial-prosper-ia-25-1 + Extractor CRM en Vivo)
 * con respaldo automático en Gemini 2.5 Flash + Base de Conocimientos oficial.
 */
(function () {
  if (window.__PROSPERIA_ASSISTANT_LOADED__) return;
  window.__PROSPERIA_ASSISTANT_LOADED__ = true;

  const API_URL = '/api/prosperia/assistant';
  const CONFIG_URL = '/api/prosperia/assistant/config';
  const BOT_SLUG = 'asesor-comercial-prosper-ia-25-1';
  const SESSION_KEY = 'passport_bot_' + BOT_SLUG + '_session';
  const HISTORY_KEY = 'pbot_fusion_history_' + BOT_SLUG;
  const WA_URL = 'https://wa.me/17868336964?text=Hola%20Agencia%20Prosper%20IA,%20vengo%20del%20asistente%20en%20l%C3%ADnea%20y%20quiero%20agendar%20mi%20demostraci%C3%B3n';
  const AVATAR_URL = '/static/empleados_digitales/setter_ia_pixar.png';

  const DEFAULT_GREETING =
    '¡Hola! Bienvenido a Agencia Prosper IA 🚀. Soy tu Asesor Digital y estoy aquí para ayudarte a que tu negocio venda y agende citas 24/7 con tu Sitio Web Inteligente, Empleados Digitales, CRM y Reels. Cuéntame, ¿a qué se dedica tu negocio?';

  const historyStore = [];

  function createSessionId() {
    return 'sess_' + Math.random().toString(36).substring(2, 11) + '_' + Date.now().toString(36);
  }

  function getSessionId() {
    try {
      let sid = sessionStorage.getItem(SESSION_KEY);
      if (!sid) {
        sid = createSessionId();
        sessionStorage.setItem(SESSION_KEY, sid);
      }
      return sid;
    } catch (e) {
      return createSessionId();
    }
  }

  let sessionId = getSessionId();
  let liveBotConfig = {
    name: 'Setter IA · Agencia Prosper IA',
    business_name: 'AGENCIA PROSPER IA LLC',
    greeting_message: DEFAULT_GREETING
  };

  function injectStyles() {
    if (document.getElementById('pia-assistant-styles')) return;
    const st = document.createElement('style');
    st.id = 'pia-assistant-styles';
    st.textContent = `
      #pia-chat-launcher {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 9990;
        display: inline-flex;
        align-items: center;
        gap: 10px;
        padding: 10px 16px 10px 10px;
        border-radius: 999px;
        border: 1px solid rgba(52, 211, 153, 0.55);
        background: linear-gradient(135deg, #065f46 0%, #0f172a 100%);
        color: #ffffff;
        font-family: 'Inter', system-ui, sans-serif;
        font-size: 13.5px;
        font-weight: 800;
        cursor: pointer;
        box-shadow: 0 14px 35px rgba(0, 0, 0, 0.55), 0 0 22px rgba(16, 185, 129, 0.25);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
      }
      #pia-chat-launcher:hover { transform: translateY(-2px); box-shadow: 0 18px 40px rgba(0,0,0,0.65), 0 0 28px rgba(16,185,129,0.4); }
      .pia-launcher-avatar {
        width: 34px;
        height: 34px;
        border-radius: 50%;
        object-fit: cover;
        object-position: center top;
        border: 1.5px solid #34d399;
        flex-shrink: 0;
      }
      #pia-chat-dot {
        width: 9px;
        height: 9px;
        border-radius: 50%;
        background: #34d399;
        box-shadow: 0 0 10px #34d399;
      }
      #pia-chat-panel {
        position: fixed;
        bottom: 80px;
        right: 20px;
        width: min(400px, calc(100vw - 24px));
        max-height: min(620px, calc(100vh - 105px));
        z-index: 9995;
        display: none;
        flex-direction: column;
        border-radius: 20px;
        overflow: hidden;
        background: #070d1a;
        border: 1px solid rgba(251, 191, 36, 0.42);
        box-shadow: 0 28px 65px rgba(0, 0, 0, 0.8);
        font-family: 'Inter', system-ui, sans-serif;
        color: #f8fafc;
      }
      #pia-chat-panel.is-open { display: flex; }
      .pia-cp-head {
        padding: 12px 14px;
        background: linear-gradient(135deg, #0f172a 0%, #064e3b 100%);
        border-bottom: 1px solid rgba(255,255,255,0.12);
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 8px;
      }
      .pia-cp-brand {
        display: flex;
        align-items: center;
        gap: 10px;
        min-width: 0;
      }
      .pia-cp-avatar {
        width: 38px;
        height: 38px;
        border-radius: 50%;
        object-fit: cover;
        object-position: center top;
        border: 2px solid #34d399;
        flex-shrink: 0;
      }
      .pia-cp-iconbtn {
        background: rgba(255,255,255,0.1);
        border: 0;
        color: #fff;
        width: 30px;
        height: 30px;
        border-radius: 8px;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        justify-content: center;
      }
      .pia-cp-iconbtn:hover { background: rgba(255,255,255,0.2); }
      .pia-cp-messages {
        flex: 1 1 auto;
        overflow-y: auto;
        padding: 14px;
        display: flex;
        flex-direction: column;
        gap: 10px;
        min-height: 230px;
      }
      .pia-msg-bot {
        align-self: flex-start;
        background: #111b31;
        border: 1px solid rgba(52, 211, 153, 0.3);
        color: #f1f5f9;
        padding: 10px 13px;
        border-radius: 14px 14px 14px 4px;
        font-size: 13px;
        line-height: 1.5;
        max-width: 88%;
        word-break: break-word;
      }
      .pia-msg-user {
        align-self: flex-end;
        background: #065f46;
        color: #ecfdf5;
        padding: 9px 13px;
        border-radius: 14px 14px 4px 14px;
        font-size: 13px;
        line-height: 1.45;
        max-width: 85%;
        word-break: break-word;
      }
      .pia-ctas-wrap {
        display: flex;
        flex-direction: column;
        gap: 6px;
        margin-top: 8px;
      }
      .pia-cta-pill {
        display: inline-flex;
        align-items: center;
        justify-content: space-between;
        gap: 8px;
        padding: 7px 11px;
        border-radius: 9px;
        background: rgba(0, 229, 255, 0.14);
        border: 1px solid rgba(0, 229, 255, 0.4);
        color: #67e8f9;
        font-size: 12px;
        font-weight: 700;
        text-decoration: none;
      }
      .pia-cta-pill:hover {
        background: #00e5ff;
        color: #03131d;
      }
      .pia-cp-quick {
        padding: 8px 12px;
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        border-top: 1px solid rgba(255,255,255,0.07);
        background: rgba(15, 23, 42, 0.7);
      }
      .pia-qbtn {
        border: 1px solid rgba(251, 191, 36, 0.35);
        background: rgba(245, 158, 11, 0.12);
        color: #fde68a;
        padding: 5px 9px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 700;
        cursor: pointer;
      }
      .pia-cp-inputrow {
        padding: 10px 12px;
        display: flex;
        align-items: center;
        gap: 6px;
        border-top: 1px solid rgba(255,255,255,0.1);
        background: #040812;
      }
      .pia-cp-inputrow input {
        flex: 1 1 auto;
        min-width: 0;
        background: #0f172a;
        border: 1px solid rgba(148,163,184,0.35);
        border-radius: 10px;
        padding: 9px 11px;
        color: #ffffff;
        font-size: 13px;
      }
      #pia-cp-mic {
        background: rgba(16, 185, 129, 0.18);
        color: #34d399;
        border: 1px solid rgba(52, 211, 153, 0.45);
        border-radius: 10px;
        padding: 9px 11px;
        font-weight: 800;
        cursor: pointer;
        flex-shrink: 0;
      }
      #pia-cp-mic.is-listening {
        background: #f43f5e;
        color: #fff;
        border-color: #fda4af;
      }
      .pia-cp-actions {
        padding: 8px 12px;
        display: flex;
        gap: 8px;
        background: #050a14;
        border-top: 1px solid rgba(255,255,255,0.06);
      }
      .pia-cp-actions a {
        flex: 1 1 50%;
        text-align: center;
        padding: 7px 8px;
        border-radius: 9px;
        font-size: 11.5px;
        font-weight: 800;
        text-decoration: none;
      }
      .aura-stage-box {
        padding: 1.25rem;
        border-radius: 18px;
        background: rgba(4, 9, 20, 0.94);
        border: 1px solid rgba(52, 211, 153, 0.4);
        text-align: left;
      }
      .aura-wave-bars {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        height: 22px;
      }
      .aura-wave-bars span {
        display: block;
        width: 4px;
        height: 8px;
        border-radius: 99px;
        background: #34d399;
        transition: height 0.2s ease;
      }
      .aura-stage-box.is-speaking .aura-wave-bars span,
      .aura-stage-box.is-listening .aura-wave-bars span {
        animation: auraPulseBar 0.7s infinite ease-in-out alternate;
      }
      .aura-stage-box.is-speaking .aura-wave-bars span:nth-child(2) { animation-delay: 0.15s; }
      .aura-stage-box.is-speaking .aura-wave-bars span:nth-child(3) { animation-delay: 0.3s; }
      .aura-stage-box.is-speaking .aura-wave-bars span:nth-child(4) { animation-delay: 0.45s; }
      @keyframes auraPulseBar {
        from { height: 6px; }
        to { height: 21px; }
      }
      @media (prefers-reduced-motion: reduce) {
        .aura-stage-box.is-speaking .aura-wave-bars span,
        .aura-stage-box.is-listening .aura-wave-bars span { animation: none !important; height: 14px; }
      }
    `;
    document.head.appendChild(st);
  }

  function isInternalProsperiaUrl(url) {
    if (!url) return false;
    if (url.startsWith('/')) return true;
    try {
      const parsed = new URL(url, window.location.origin);
      return parsed.hostname === 'agenciaprosperia.com' || parsed.hostname === 'www.agenciaprosperia.com' || parsed.hostname === window.location.hostname;
    } catch (e) {
      return false;
    }
  }

  function formatRichHtml(text) {
    if (!text) return '';
    const d = document.createElement('div');
    d.textContent = String(text);
    let safe = d.innerHTML;
    safe = safe.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    safe = safe.replace(/\[([^\]]+)\]\((https?:\/\/[^\s\)]+)\)/g, function (_, label, url) {
      const targetAttr = isInternalProsperiaUrl(url) ? '' : ' target="_blank" rel="noopener"';
      return `<a href="${url}"${targetAttr} style="color:#38bdf8;text-decoration:underline;font-weight:700;">${label}</a>`;
    });
    safe = safe.replace(/(^|[\s(>])(https?:\/\/[^\s<)]+)/g, function (_, prefix, url) {
      const targetAttr = isInternalProsperiaUrl(url) ? '' : ' target="_blank" rel="noopener"';
      return `${prefix}<a href="${url}"${targetAttr} style="color:#38bdf8;text-decoration:underline;font-weight:700;">${url}</a>`;
    });
    safe = safe.replace(/\n/g, '<br>');
    return safe;
  }

  function buildCtasHtml(ctas) {
    if (!ctas || typeof ctas !== 'object') return '';
    const sourceObj = (ctas.temas && typeof ctas.temas === 'object') ? ctas.temas : ctas;
    const seen = new Set();
    const links = [];

    Object.keys(sourceObj).forEach((key) => {
      const val = sourceObj[key];
      if (typeof val === 'string' && (val.startsWith('http://') || val.startsWith('https://') || val.startsWith('/'))) {
        if (key !== 'default' && key !== 'temas' && !seen.has(val)) {
          seen.add(val);
          const label = key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' ');
          const targetAttr = isInternalProsperiaUrl(val) ? '' : ' target="_blank" rel="noopener"';
          links.push(`<a class="pia-cta-pill" href="${val}"${targetAttr}><span>${label}</span><span>→</span></a>`);
        }
      }
    });

    if (!links.length) return '';
    return `<div class="pia-ctas-wrap">${links.join('')}</div>`;
  }

  function saveFusionHistory(role, text, ctas) {
    try {
      const raw = sessionStorage.getItem(HISTORY_KEY);
      const list = raw ? JSON.parse(raw) : [];
      list.push({ role, text, ctas: ctas || null });
      sessionStorage.setItem(HISTORY_KEY, JSON.stringify(list.slice(-30)));
    } catch (e) {}
  }

  async function loadBotConfig() {
    try {
      const res = await fetch(CONFIG_URL);
      if (!res.ok) return liveBotConfig;
      const data = await res.json();
      if (data && data.ok) {
        liveBotConfig = {
          name: data.name || liveBotConfig.name,
          business_name: data.business_name || liveBotConfig.business_name,
          greeting_message: data.greeting_message || liveBotConfig.greeting_message
        };
      }
    } catch (e) {}
    return liveBotConfig;
  }

  async function askAssistant(message, mode) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 14000);
    try {
      const res = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        signal: controller.signal,
        body: JSON.stringify({
          message,
          mode: mode || 'chat',
          session_id: sessionId,
          history: historyStore.slice(-6)
        })
      });
      clearTimeout(timer);
      const data = await res.json();
      if (data && data.session_id) sessionId = data.session_id;
      const reply = (data && data.reply) || 'Con gusto te ayudo. Puedes elegir tu solución en el formulario o escribirnos directo por WhatsApp.';
      const replySpeech = (data && data.reply_speech) || reply;
      const ctas = (data && data.ctas) || {};
      historyStore.push({ role: 'user', text: message });
      historyStore.push({ role: 'assistant', text: reply });
      return { reply, replySpeech, ctas, datosCompletos: Boolean(data && data.datos_completos) };
    } catch (e) {
      clearTimeout(timer);
      const fallback = 'Te recomiendo agendar tu demostración en /sitiosweb o escribirnos directo por WhatsApp al +1 786 833 6964 para mostrarte ejemplos de tu rubro.';
      return { reply: fallback, replySpeech: fallback, ctas: {}, datosCompletos: false };
    }
  }

  function speakText(text, onStart, onEnd) {
    try {
      if (!('speechSynthesis' in window)) {
        if (onEnd) onEnd();
        return;
      }
      window.speechSynthesis.cancel();
      const utter = new SpeechSynthesisUtterance(text);
      utter.lang = 'es-MX';
      utter.rate = 1.02;
      utter.pitch = 1.02;
      const voices = window.speechSynthesis.getVoices() || [];
      const esVoice = voices.find(v => /es[-_](mx|us|419|es)/i.test(v.lang) && /paulina|monica|sabina|google|helena|dalia/i.test(v.name))
        || voices.find(v => /^es/i.test(v.lang));
      if (esVoice) utter.voice = esVoice;
      if (onStart) utter.onstart = onStart;
      if (onEnd) {
        utter.onend = onEnd;
        utter.onerror = onEnd;
      }
      window.speechSynthesis.speak(utter);
    } catch (e) {
      if (onEnd) onEnd();
    }
  }

  function mountVoiceStage() {
    const stageEl = document.getElementById('aura-voice-stage');
    if (!stageEl) return;

    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    stageEl.innerHTML = `
      <div class="aura-stage-box" id="aura-stage-card">
        <div style="display:flex; flex-wrap:wrap; justify-content:space-between; align-items:center; gap:0.75rem; margin-bottom:0.85rem;">
          <div style="display:flex; align-items:center; gap:0.65rem;">
            <div class="aura-wave-bars" aria-hidden="true"><span></span><span></span><span></span><span></span></div>
            <div>
              <div style="font-size:0.88rem; font-weight:800; color:#ffffff;">Setter IA · Asistente de Voz en Vivo</div>
              <div id="aura-stage-status" style="font-size:0.76rem; color:#34d399;">Conectado al CRM · Listo para escucharte</div>
            </div>
          </div>
          <div style="display:flex; gap:0.5rem;">
            <button type="button" id="aura-mic-btn" class="hm-btn-emerald pia-btn-emerald" style="padding:0.65rem 1.1rem; font-size:0.86rem; border-radius:12px;">
              <i class="fas fa-microphone" aria-hidden="true"></i>
              <span>${SpeechRec ? 'Hablar por Voz Ahora' : 'Escuchar Saludo en Vivo'}</span>
            </button>
            <button type="button" id="aura-stop-btn" class="hm-btn-outline pia-btn-ghost" style="padding:0.65rem 0.9rem; font-size:0.82rem; border-radius:12px;" hidden>
              <i class="fas fa-stop" aria-hidden="true"></i>
              <span>Detener</span>
            </button>
          </div>
        </div>

        <div id="aura-stage-transcript" aria-live="polite" style="padding:0.85rem 1rem; border-radius:12px; background:rgba(15,23,42,0.85); border:1px solid rgba(255,255,255,0.08); font-size:0.88rem; color:#e2e8f0; min-height:66px; margin-bottom:0.85rem;">
          💬 «Hola, soy tu <strong>Setter IA</strong> de Agencia Prosper IA. Toca el micrófono para preguntarme con tu voz sobre páginas web, nuestros 4 Empleados Digitales, CRM o Reels.»
        </div>

        <div style="display:flex; flex-wrap:wrap; gap:0.45rem; margin-bottom:0.85rem;">
          <button type="button" class="pia-qbtn aura-voice-pill" data-q="¿Qué hacen los 4 Empleados Digitales (SDR IA, Setter IA, Closer IA y Soporte IA)?">Los 4 Empleados Digitales</button>
          <button type="button" class="pia-qbtn aura-voice-pill" data-q="¿Cuáles son los paquetes o cajas que ofrecen para mi negocio?">Ver Opciones</button>
          <button type="button" class="pia-qbtn aura-voice-pill" data-q="¿En cuántos días me entregan todo funcionando?">Tiempo de entrega</button>
          <button type="button" class="pia-qbtn aura-voice-pill" data-q="Quiero agendar una demostración en vivo">Agendar Demo</button>
        </div>

        <form id="aura-voice-text-form" style="display:flex; gap:0.5rem;">
          <label for="aura-voice-text-in" class="pia-visually-hidden">Escribe tu pregunta para que el Empleado Digital responda por voz</label>
          <input type="text" id="aura-voice-text-in" placeholder="O escribe aquí tu duda para escucharlo en vivo..." style="flex:1 1 auto; padding:0.7rem 0.9rem; border-radius:10px; background:#020617; border:1px solid rgba(148,163,184,0.35); color:#fff; font-size:0.88rem;">
          <button type="submit" class="hm-btn-gold pia-btn-primary" style="padding:0.65rem 1rem; font-size:0.86rem; border-radius:10px;">
            <i class="fas fa-volume-high" aria-hidden="true"></i> <span>Preguntar</span>
          </button>
        </form>
      </div>
    `;

    const card = document.getElementById('aura-stage-card');
    const statusTxt = document.getElementById('aura-stage-status');
    const transcript = document.getElementById('aura-stage-transcript');
    const micBtn = document.getElementById('aura-mic-btn');
    const stopBtn = document.getElementById('aura-stop-btn');
    const textForm = document.getElementById('aura-voice-text-form');
    const textIn = document.getElementById('aura-voice-text-in');
    let recInstance = null;

    async function runVoiceQuery(questionText) {
      if (!questionText) return;
      card.classList.remove('is-listening');
      statusTxt.textContent = 'Consultando al Asesor Comercial conectado al CRM...';
      transcript.innerHTML = `<div style="color:#93c5fd; margin-bottom:4px;"><strong>Tú:</strong> ${formatRichHtml(questionText)}</div><div><em>Escribiendo respuesta...</em></div>`;

      const res = await askAssistant(questionText, 'voice');
      transcript.innerHTML =
        `<div style="color:#93c5fd; margin-bottom:4px;"><strong>Tú:</strong> ${formatRichHtml(questionText)}</div>` +
        `<div style="color:#ecfdf5;"><strong>Asistente IA:</strong> ${formatRichHtml(res.reply)}</div>` +
        buildCtasHtml(res.ctas);
      statusTxt.textContent = 'Respondiendo en vivo...';
      stopBtn.hidden = false;
      card.classList.add('is-speaking');

      speakText(res.replySpeech, () => {
        card.classList.add('is-speaking');
      }, () => {
        card.classList.remove('is-speaking');
        statusTxt.textContent = 'Listo para tu siguiente pregunta';
        stopBtn.hidden = true;
      });
    }

    stopBtn.addEventListener('click', () => {
      try { if (recInstance) recInstance.stop(); } catch (e) {}
      try { if ('speechSynthesis' in window) window.speechSynthesis.cancel(); } catch (e) {}
      card.classList.remove('is-speaking', 'is-listening');
      statusTxt.textContent = 'Audio detenido';
      stopBtn.hidden = true;
    });

    micBtn.addEventListener('click', () => {
      if (!SpeechRec) {
        runVoiceQuery('Hola, explícame brevemente cómo ayudan a un dueño de negocio con web, WhatsApp 24/7 y calendario.');
        return;
      }
      try {
        if ('speechSynthesis' in window) window.speechSynthesis.cancel();
        recInstance = new SpeechRec();
        recInstance.lang = 'es-MX';
        recInstance.interimResults = false;
        recInstance.maxAlternatives = 1;

        card.classList.add('is-listening');
        stopBtn.hidden = false;
        statusTxt.textContent = 'Escuchando tu voz... habla ahora';

        recInstance.onresult = (ev) => {
          const spoken = ev.results && ev.results[0] && ev.results[0][0] ? ev.results[0][0].transcript : '';
          card.classList.remove('is-listening');
          if (spoken) runVoiceQuery(spoken);
        };
        recInstance.onerror = () => {
          card.classList.remove('is-listening');
          stopBtn.hidden = true;
          statusTxt.textContent = 'No se detectó micrófono; puedes tocar una pregunta rápida o escribir abajo.';
        };
        recInstance.onend = () => {
          card.classList.remove('is-listening');
        };
        recInstance.start();
      } catch (e) {
        statusTxt.textContent = 'Usa el campo de texto o los botones de abajo para escuchar al asistente.';
      }
    });

    document.querySelectorAll('.aura-voice-pill').forEach(btn => {
      btn.addEventListener('click', () => runVoiceQuery(btn.getAttribute('data-q') || ''));
    });

    if (textForm && textIn) {
      textForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const q = textIn.value.trim();
        if (!q) return;
        textIn.value = '';
        runVoiceQuery(q);
      });
    }
  }

  async function mountFloatingChat() {
    if (document.getElementById('pia-chat-launcher')) return;
    await loadBotConfig();

    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;

    const btn = document.createElement('button');
    btn.id = 'pia-chat-launcher';
    btn.type = 'button';
    btn.setAttribute('aria-expanded', 'false');
    btn.setAttribute('aria-controls', 'pia-chat-panel');
    btn.innerHTML = `<img src="${AVATAR_URL}" alt="" class="pia-launcher-avatar"><span id="pia-chat-dot" aria-hidden="true"></span><span>Asistente Digital 24/7</span>`;

    const panel = document.createElement('section');
    panel.id = 'pia-chat-panel';
    panel.setAttribute('role', 'dialog');
    panel.setAttribute('aria-label', 'Chat y Voz con Asesor Comercial Agencia Prosper IA');
    panel.innerHTML = `
      <div class="pia-cp-head">
        <div class="pia-cp-brand">
          <img src="${AVATAR_URL}" alt="Setter IA" class="pia-cp-avatar">
          <div style="min-width:0;">
            <div id="pia-cp-title" style="font-weight:800; font-size:13.5px; color:#fff; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${formatRichHtml(liveBotConfig.name)}</div>
            <div id="pia-cp-subtitle" style="font-size:11px; color:#6ee7b7;">${formatRichHtml(liveBotConfig.business_name)} · Chat &amp; Voz CRM</div>
          </div>
        </div>
        <div style="display:flex; align-items:center; gap:5px; flex-shrink:0;">
          <button type="button" id="pia-cp-reset" class="pia-cp-iconbtn" title="Reiniciar conversación" aria-label="Reiniciar conversación"><i class="fas fa-rotate-left" aria-hidden="true"></i></button>
          <button type="button" id="pia-cp-close" class="pia-cp-iconbtn" title="Cerrar asistente" aria-label="Cerrar asistente">✕</button>
        </div>
      </div>
      <div class="pia-cp-messages" id="pia-cp-messages"></div>
      <div class="pia-cp-quick">
        <button type="button" class="pia-qbtn pia-cp-q" data-q="Quiero información de páginas web y 4 Empleados Digitales">Web + IA 24/7</button>
        <button type="button" class="pia-qbtn pia-cp-q" data-q="Quiero ver el embudo de Reels y agendar demo">Reels &amp; Agenda</button>
        <button type="button" class="pia-qbtn pia-cp-q" data-q="¿Qué paquetes manejan para mi negocio?">Ver Opciones</button>
      </div>
      <form class="pia-cp-inputrow" id="pia-cp-form">
        <input type="text" id="pia-cp-input" placeholder="Escribe o habla por micrófono..." autocomplete="off">
        ${SpeechRec ? '<button type="button" id="pia-cp-mic" title="Hablar por Voz" aria-label="Hablar por voz"><i class="fas fa-microphone" aria-hidden="true"></i></button>' : ''}
        <button type="submit" aria-label="Enviar mensaje" style="background:#f59e0b; color:#090d16; border:0; border-radius:10px; padding:9px 13px; font-weight:800; cursor:pointer; flex-shrink:0;">Enviar</button>
      </form>
      <div class="pia-cp-actions">
        <a href="/sitiosweb" id="pia-cp-cal-link" style="background:rgba(245,158,11,0.16); border:1px solid rgba(251,191,36,0.45); color:#fde68a;">📅 Agendar Cita</a>
        <a href="${WA_URL}" target="_blank" rel="noopener" style="background:rgba(16,185,129,0.18); border:1px solid rgba(52,211,153,0.45); color:#d1fae5;">💬 WhatsApp Directo</a>
      </div>
    `;

    document.body.appendChild(btn);
    document.body.appendChild(panel);

    const msgsBox = document.getElementById('pia-cp-messages');
    const closeBtn = document.getElementById('pia-cp-close');
    const resetBtn = document.getElementById('pia-cp-reset');
    const cpForm = document.getElementById('pia-cp-form');
    const cpInput = document.getElementById('pia-cp-input');
    const cpMic = document.getElementById('pia-cp-mic');
    const calLink = document.getElementById('pia-cp-cal-link');

    function appendBubble(role, text, ctas) {
      const div = document.createElement('div');
      div.className = role === 'user' ? 'pia-msg-user' : 'pia-msg-bot';
      div.innerHTML = formatRichHtml(text) + (role === 'bot' ? buildCtasHtml(ctas) : '');
      msgsBox.appendChild(div);
      msgsBox.scrollTop = msgsBox.scrollHeight;
      return div;
    }

    function restoreOrGreet() {
      msgsBox.innerHTML = '';
      try {
        const raw = sessionStorage.getItem(HISTORY_KEY);
        const list = raw ? JSON.parse(raw) : [];
        if (Array.isArray(list) && list.length > 0) {
          list.forEach((m) => appendBubble(m.role, m.text, m.ctas));
          return;
        }
      } catch (e) {}
      appendBubble('bot', liveBotConfig.greeting_message);
    }

    restoreOrGreet();

    function setOpen(open) {
      panel.classList.toggle('is-open', open);
      btn.setAttribute('aria-expanded', String(open));
      if (open && cpInput) setTimeout(() => cpInput.focus(), 120);
    }

    btn.addEventListener('click', () => setOpen(!panel.classList.contains('is-open')));
    closeBtn.addEventListener('click', () => setOpen(false));
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && panel.classList.contains('is-open')) setOpen(false);
    });
    if (calLink) {
      calLink.addEventListener('click', () => setOpen(false));
    }

    resetBtn.addEventListener('click', () => {
      try {
        if ('speechSynthesis' in window) window.speechSynthesis.cancel();
        sessionStorage.removeItem(HISTORY_KEY);
        sessionId = createSessionId();
        sessionStorage.setItem(SESSION_KEY, sessionId);
      } catch (e) {}
      historyStore.length = 0;
      restoreOrGreet();
    });

    async function sendChatMsg(txt, speakReply = false) {
      if (!txt) return;
      appendBubble('user', txt);
      saveFusionHistory('user', txt);

      const bDiv = appendBubble('bot', 'Escribiendo...');
      const res = await askAssistant(txt, speakReply ? 'voice' : 'chat');
      bDiv.innerHTML = formatRichHtml(res.reply) + buildCtasHtml(res.ctas);
      msgsBox.scrollTop = msgsBox.scrollHeight;
      saveFusionHistory('bot', res.reply, res.ctas);

      if (speakReply) {
        speakText(res.replySpeech);
      }
    }

    cpForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const val = cpInput.value.trim();
      if (!val) return;
      cpInput.value = '';
      sendChatMsg(val, false);
    });

    if (cpMic && SpeechRec) {
      let chatRec = null;
      cpMic.addEventListener('click', () => {
        if (cpMic.classList.contains('is-listening')) {
          try { if (chatRec) chatRec.stop(); } catch (e) {}
          cpMic.classList.remove('is-listening');
          return;
        }
        try {
          if ('speechSynthesis' in window) window.speechSynthesis.cancel();
          chatRec = new SpeechRec();
          chatRec.lang = 'es-MX';
          chatRec.interimResults = false;
          chatRec.maxAlternatives = 1;
          cpMic.classList.add('is-listening');
          chatRec.onresult = (ev) => {
            cpMic.classList.remove('is-listening');
            const spoken = ev.results && ev.results[0] && ev.results[0][0] ? ev.results[0][0].transcript : '';
            if (spoken) sendChatMsg(spoken, true);
          };
          chatRec.onerror = () => cpMic.classList.remove('is-listening');
          chatRec.onend = () => cpMic.classList.remove('is-listening');
          chatRec.start();
        } catch (e) {
          cpMic.classList.remove('is-listening');
        }
      });
    }

    panel.querySelectorAll('.pia-cp-q').forEach(qb => {
      qb.addEventListener('click', () => sendChatMsg(qb.getAttribute('data-q') || '', false));
    });

    window.openProsperChat = function (e) {
      if (e && e.preventDefault) e.preventDefault();
      setOpen(true);
      return false;
    };
  }

  function init() {
    injectStyles();
    mountVoiceStage();
    mountFloatingChat();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

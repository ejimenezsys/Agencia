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
  const LEAD_DRAFT_KEY = 'pbot_fusion_lead_' + BOT_SLUG;
  const CAL_DIAGNOSTICO_URL = 'https://api.agenciaprosperia.com/widget/booking/gqoqyrr112bvjTJYqOi8';
  const CAL_EDWARD_URL = 'https://api.agenciaprosperia.com/widget/booking/aT3eXMuYSOnWwjnC063t';
  const WA_BASE_URL = 'https://wa.me/17869828707';
  const WA_URL = WA_BASE_URL + '?text=' + encodeURIComponent('Hola Agencia Prosper IA, vengo del asistente en línea y quiero agendar mi demostración');
  const AVATAR_URL = '/static/empleados_digitales/setter_ia_pixar.png';

  const DEFAULT_GREETING =
    '¡Hola! Bienvenido a Agencia Prosper IA 🚀. Soy tu Asesor Digital y estoy aquí para ayudarte a que tu negocio venda y agende citas 24/7 con tu Sitio Web Inteligente, Empleados Digitales, CRM y Reels. Cuéntame, ¿a qué se dedica tu negocio?';

  const historyStore = [];
  const leadDraft = (() => {
    try {
      const raw = sessionStorage.getItem(LEAD_DRAFT_KEY);
      if (raw) {
        const parsed = JSON.parse(raw);
        if (parsed && typeof parsed === 'object') {
          return {
            name: String(parsed.name || ''),
            email: String(parsed.email || ''),
            phone: String(parsed.phone || ''),
            company: String(parsed.company || ''),
            lastMsg: String(parsed.lastMsg || '')
          };
        }
      }
    } catch (e) {}
    return { name: '', email: '', phone: '', company: '', lastMsg: '' };
  })();

  function saveLeadDraft() {
    try {
      sessionStorage.setItem(LEAD_DRAFT_KEY, JSON.stringify(leadDraft));
    } catch (e) {}
  }

  function syncDirectWaUrl() {
    const waEl = document.getElementById('pia-cp-wa-link');
    if (!waEl) return;
    const parts = ['Hola Agencia Prosper IA, vengo del asistente en línea'];
    if (leadDraft.name) parts.push('(soy ' + leadDraft.name + ')');
    if (leadDraft.company) parts.push('de ' + leadDraft.company);
    if (leadDraft.lastMsg) parts.push('sobre: "' + leadDraft.lastMsg.slice(0, 90) + '"');
    parts.push('y quiero agendar mi demostración.');
    waEl.href = WA_BASE_URL + '?text=' + encodeURIComponent(parts.join(' '));
  }

  function captureLeadContext(txt) {
    const raw = String(txt || '').trim();
    if (!raw) return;
    leadDraft.lastMsg = raw;

    const emMatch = raw.match(/[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}/);
    if (emMatch) leadDraft.email = emMatch[0].trim();

    const phMatch = raw.match(/(?:\+?\d[\d\s\-\(\)]{7,}\d)/);
    if (phMatch) {
      const digits = phMatch[0].replace(/\D/g, '');
      if (digits.length >= 8 && digits !== '17869828707' && digits !== '7869828707') {
        leadDraft.phone = phMatch[0].trim();
      }
    }

    const nameMatch = raw.match(/(?:me llamo|mi nombre es|soy)\s+([A-ZÁÉÍÓÚÑa-záéíóúñ][A-ZÁÉÍÓÚÑa-záéíóúñ\s]{1,36}?)(?:[,.!;\n]|$|\s+(?:mi|de|y|en|tengo|para)\b)/i);
    if (nameMatch && nameMatch[1]) {
      const cand = nameMatch[1].trim();
      if (cand.length >= 2 && cand.split(/\s+/).length <= 4) {
        leadDraft.name = cand;
      }
    }

    const bizMatch = raw.match(/(?:mi negocio es|tengo una?|empresa es|se dedica a)\s+([A-ZÁÉÍÓÚÑa-záéíóúñ0-9&\-\s]{2,45}?)(?:[,.!;\n]|$)/i);
    if (bizMatch && bizMatch[1]) {
      leadDraft.company = bizMatch[1].trim();
    }

    saveLeadDraft();
    syncDirectWaUrl();
  }

  function buildCalendarBookingUrl(baseUrl) {
    const target = (baseUrl && /^https?:\/\//i.test(baseUrl)) ? baseUrl : CAL_DIAGNOSTICO_URL;
    try {
      const urlObj = new URL(target);
      if (leadDraft.name) {
        const firstName = leadDraft.name.split(/\s+/)[0] || leadDraft.name;
        if (!urlObj.searchParams.has('first_name')) urlObj.searchParams.set('first_name', firstName);
        if (!urlObj.searchParams.has('name')) urlObj.searchParams.set('name', leadDraft.name);
      }
      if (leadDraft.email && !urlObj.searchParams.has('email')) {
        urlObj.searchParams.set('email', leadDraft.email);
      }
      if (leadDraft.phone && !urlObj.searchParams.has('phone')) {
        urlObj.searchParams.set('phone', leadDraft.phone);
      }
      return urlObj.toString();
    } catch (e) {
      return target;
    }
  }

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
        min-width: 40px;
        min-height: 40px;
        padding: 9px 11px;
        font-weight: 800;
        cursor: pointer;
        flex-shrink: 0;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 5px;
      }
      #pia-cp-mic.is-listening,
      #aura-mic-btn.is-listening {
        background: #e11d48 !important;
        color: #ffffff !important;
        border-color: #fda4af !important;
        box-shadow: 0 0 18px rgba(244, 63, 94, 0.45);
      }
      .pia-cp-status {
        display: none;
        padding: 6px 12px;
        font-size: 11.5px;
        line-height: 1.35;
        font-weight: 600;
        color: #a7f3d0;
        background: rgba(6, 78, 59, 0.45);
        border-top: 1px solid rgba(52, 211, 153, 0.28);
      }
      .pia-cp-status.is-visible { display: block; }
      .pia-cp-status.is-error {
        color: #fecdd3;
        background: rgba(136, 19, 55, 0.55);
        border-top-color: rgba(251, 113, 133, 0.35);
      }
      .pia-msg-bot-tools {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        margin-top: 6px;
        gap: 6px;
      }
      .pia-speak-btn {
        background: rgba(56, 189, 248, 0.12);
        border: 1px solid rgba(56, 189, 248, 0.32);
        color: #7dd3fc;
        border-radius: 999px;
        padding: 3px 9px;
        font-size: 11px;
        font-weight: 700;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        gap: 4px;
      }
      .pia-speak-btn:hover { background: rgba(56, 189, 248, 0.25); color: #ffffff; }
      .pia-cp-iconbtn.is-active {
        background: rgba(16, 185, 129, 0.32);
        border: 1px solid rgba(52, 211, 153, 0.55);
        color: #6ee7b7;
      }
      .pia-visually-hidden:where(:not(:focus-within, :active)) {
        position: absolute !important;
        clip-path: inset(50%) !important;
        overflow: hidden !important;
        width: 1px !important;
        height: 1px !important;
        margin: -1px !important;
        padding: 0 !important;
        border: 0 !important;
        white-space: nowrap !important;
      }
      :where(#pia-chat-launcher, #pia-chat-panel button, #pia-chat-panel a, #aura-voice-stage button, #aura-voice-stage input):focus-visible {
        outline: 2px solid #fbbf24;
        outline-offset: 2px;
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
      #pia-calendar-dialog {
        margin: auto;
        padding: 0;
        width: min(880px, calc(100vw - 24px));
        max-height: min(90vh, 840px);
        border: 1px solid rgba(251, 191, 36, 0.52);
        border-radius: 20px;
        background: #070d1a;
        color: #f8fafc;
        box-shadow: 0 30px 70px rgba(0, 0, 0, 0.85);
        font-family: 'Inter', system-ui, sans-serif;
      }
      #pia-calendar-dialog[open] {
        display: flex;
        flex-direction: column;
      }
      #pia-calendar-dialog:modal {
        overscroll-behavior: contain;
      }
      #pia-calendar-dialog::backdrop {
        overflow: hidden;
        overscroll-behavior: contain;
        background-color: rgba(2, 6, 23, 0.78);
        backdrop-filter: blur(4px);
      }
      .pia-cal-head {
        padding: 14px 18px;
        background: linear-gradient(135deg, #0f172a 0%, #064e3b 100%);
        border-bottom: 1px solid rgba(255, 255, 255, 0.12);
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
      }
      .pia-cal-tabs {
        padding: 10px 18px;
        background: #0b1325;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 8px;
      }
      .pia-cal-tab {
        border: 1px solid rgba(251, 191, 36, 0.4);
        background: rgba(245, 158, 11, 0.12);
        color: #fde68a;
        padding: 6px 12px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 700;
        cursor: pointer;
        text-decoration: none;
      }
      .pia-cal-tab.is-active {
        background: #f59e0b;
        color: #090d16;
        border-color: #fbbf24;
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

  function ensureCalendarDialog() {
    let dlg = document.getElementById('pia-calendar-dialog');
    if (dlg) return dlg;

    dlg = document.createElement('dialog');
    dlg.id = 'pia-calendar-dialog';
    dlg.setAttribute('closedby', 'any');
    dlg.setAttribute('aria-labelledby', 'pia-cal-modal-title');
    dlg.innerHTML = `
      <div class="pia-cal-head">
        <div>
          <h2 id="pia-cal-modal-title" style="margin:0; font-size:16px; font-weight:800; color:#ffffff;">
            📅 Agendar Demostración en Vivo · Agencia Prosper IA
          </h2>
          <div style="font-size:12px; color:#6ee7b7; margin-top:2px;">
            Disponibilidad Lunes a Viernes · Recordatorios automáticos 24 h y 2 h antes
          </div>
        </div>
        <button type="button" id="pia-cal-close-btn" autofocus class="pia-cp-iconbtn" aria-label="Cerrar calendario">✕</button>
      </div>
      <div class="pia-cal-tabs">
        <button type="button" class="pia-cal-tab is-active" data-cal-url="${CAL_DIAGNOSTICO_URL}">Diagnóstico Round-Robin (15 min)</button>
        <button type="button" class="pia-cal-tab" data-cal-url="${CAL_EDWARD_URL}">Agenda Directa · Edward Jiménez</button>
        <a href="/sitioweb#agendar" class="pia-cal-tab" style="margin-left:auto; border-color:rgba(56,189,248,0.45); color:#bae6fd; background:rgba(56,189,248,0.12);">Sitio Web Inicial Gratis →</a>
      </div>
      <div style="flex:1 1 auto; min-height:480px; background:#ffffff; overflow:auto;">
        <iframe
          id="pia-cal-iframe"
          title="Calendario de Citas Agencia Prosper IA"
          style="width:100%; height:min(68vh, 660px); border:0; display:block; background:#ffffff;"
          allow="camera; microphone; autoplay">
        </iframe>
      </div>
    `;
    document.body.appendChild(dlg);

    const closeBtn = document.getElementById('pia-cal-close-btn');
    const frameEl = document.getElementById('pia-cal-iframe');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => dlg.close());
    }
    dlg.addEventListener('close', () => {
      dlg.returnValue = '';
    });

    dlg.querySelectorAll('button[data-cal-url]').forEach((tabBtn) => {
      tabBtn.addEventListener('click', () => {
        dlg.querySelectorAll('button[data-cal-url]').forEach((b) => b.classList.remove('is-active'));
        tabBtn.classList.add('is-active');
        if (frameEl) {
          frameEl.src = buildCalendarBookingUrl(tabBtn.getAttribute('data-cal-url') || CAL_DIAGNOSTICO_URL);
        }
      });
    });

    if (!('closedBy' in HTMLDialogElement.prototype)) {
      const outside = (e) => {
        const r = dlg.getBoundingClientRect();
        return e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom;
      };
      let pressedOutside = false;
      dlg.addEventListener('pointerdown', (e) => { pressedOutside = outside(e); });
      dlg.addEventListener('pointerup', (e) => { if (pressedOutside && outside(e)) dlg.close(); });
    }

    return dlg;
  }

  function openInlineCalendarModal(presetUrl) {
    const dlg = ensureCalendarDialog();
    const frameEl = document.getElementById('pia-cal-iframe');
    const resolvedBase = (presetUrl && presetUrl.indexOf('widget/booking') !== -1) ? presetUrl : CAL_DIAGNOSTICO_URL;
    if (frameEl) {
      frameEl.src = buildCalendarBookingUrl(resolvedBase);
    }
    dlg.querySelectorAll('button[data-cal-url]').forEach((b) => {
      const isMatch = b.getAttribute('data-cal-url') === resolvedBase;
      b.classList.toggle('is-active', isMatch);
    });
    if (typeof dlg.showModal === 'function' && !dlg.open) {
      dlg.showModal();
    }
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
          let label = key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' ').trim();
          if (label.length > 48 || /caja\s*1:/i.test(label)) {
            label = '📅 Agendar Demostración en Vivo';
          }
          const isBookingModal = val.indexOf('widget/booking') !== -1 || val.indexOf('/#contacto') !== -1;
          const modalCls = isBookingModal ? ' pia-cta-booking' : '';
          const targetAttr = (!isBookingModal && !isInternalProsperiaUrl(val)) ? ' target="_blank" rel="noopener"' : '';
          links.push(`<a class="pia-cta-pill${modalCls}" href="${val}"${targetAttr}><span>${label}</span><span>→</span></a>`);
        }
      }
    });

    if (!links.length) return '';
    return `<div class="pia-ctas-wrap">${links.join('')}</div>`;
  }

  function bindBookingCtaHandlers(containerEl, onBeforeOpen) {
    if (!containerEl) return;
    containerEl.querySelectorAll('.pia-cta-booking').forEach((aEl) => {
      aEl.addEventListener('click', (ev) => {
        ev.preventDefault();
        if (typeof onBeforeOpen === 'function') onBeforeOpen();
        openInlineCalendarModal(aEl.getAttribute('href') || '');
      });
    });
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
      const fallback = 'Te recomiendo agendar tu demostración en /sitioweb o escribirnos directo por WhatsApp al +1 786 982 8707 para mostrarte ejemplos de tu rubro.';
      return { reply: fallback, replySpeech: fallback, ctas: {}, datosCompletos: false };
    }
  }

  const TRANSCRIBE_URL = '/api/prosperia/voice-transcribe';
  let preferRecorderFallback = false;
  let speechKeepAliveTimer = null;

  function unlockSpeechSynthesis() {
    try {
      if (!('speechSynthesis' in window)) return;
      if (typeof window.speechSynthesis.resume === 'function') {
        window.speechSynthesis.resume();
      }
      const warm = new SpeechSynthesisUtterance(' ');
      warm.volume = 0;
      warm.rate = 10;
      window.speechSynthesis.speak(warm);
    } catch (e) {}
  }

  function stopSpeaking() {
    try {
      if (speechKeepAliveTimer) {
        clearInterval(speechKeepAliveTimer);
        speechKeepAliveTimer = null;
      }
      if ('speechSynthesis' in window) window.speechSynthesis.cancel();
    } catch (e) {}
  }

  function speakText(text, onStart, onEnd) {
    try {
      if (!('speechSynthesis' in window) || !text) {
        if (onEnd) onEnd();
        return;
      }
      stopSpeaking();
      const utter = new SpeechSynthesisUtterance(text);
      utter.lang = 'es-MX';
      utter.rate = 1.02;
      utter.pitch = 1.02;
      const voices = window.speechSynthesis.getVoices() || [];
      const esVoice = voices.find(v => /es[-_](mx|us|419|es)/i.test(v.lang) && /paulina|monica|sabina|google|helena|dalia/i.test(v.name))
        || voices.find(v => /^es/i.test(v.lang));
      if (esVoice) utter.voice = esVoice;

      let finished = false;
      const finishOnce = () => {
        if (finished) return;
        finished = true;
        if (speechKeepAliveTimer) {
          clearInterval(speechKeepAliveTimer);
          speechKeepAliveTimer = null;
        }
        if (onEnd) onEnd();
      };

      utter.onstart = () => {
        if (onStart) onStart();
        speechKeepAliveTimer = setInterval(() => {
          try {
            if (window.speechSynthesis.speaking && !window.speechSynthesis.paused) {
              window.speechSynthesis.resume();
            } else if (!window.speechSynthesis.speaking) {
              clearInterval(speechKeepAliveTimer);
              speechKeepAliveTimer = null;
            }
          } catch (e) {}
        }, 4500);
      };
      utter.onend = finishOnce;
      utter.onerror = finishOnce;

      if (typeof window.speechSynthesis.resume === 'function') {
        window.speechSynthesis.resume();
      }
      window.speechSynthesis.speak(utter);
    } catch (e) {
      if (onEnd) onEnd();
    }
  }

  function supportsVoiceCapture() {
    const hasSpeechRec = Boolean(window.SpeechRecognition || window.webkitSpeechRecognition);
    const hasMediaRec = Boolean(
      navigator.mediaDevices &&
      typeof navigator.mediaDevices.getUserMedia === 'function' &&
      typeof MediaRecorder !== 'undefined'
    );
    return hasSpeechRec || hasMediaRec;
  }

  function pickRecorderMimeType() {
    if (typeof MediaRecorder === 'undefined') return '';
    if (typeof MediaRecorder.isTypeSupported !== 'function') return '';
    const candidates = ['audio/webm;codecs=opus', 'audio/webm', 'audio/mp4', 'audio/ogg;codecs=opus', 'audio/ogg'];
    for (const c of candidates) {
      if (MediaRecorder.isTypeSupported(c)) return c;
    }
    return '';
  }

  function blobToBase64(blob) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        const res = String(reader.result || '');
        const commaIdx = res.indexOf(',');
        resolve(commaIdx !== -1 ? res.slice(commaIdx + 1) : res);
      };
      reader.onerror = () => reject(new Error('Error leyendo audio'));
      reader.readAsDataURL(blob);
    });
  }

  function formatMicErrorMessage(code) {
    if (code === 'permission-denied') {
      return '🔒 Micrófono bloqueado en el navegador: toca el ícono de ajustes/candado junto a agenciaprosperia.com → Micrófono → Permitir (o revisa Ajustes del Sistema de tu equipo).';
    }
    if (code === 'no-device') {
      return '🎙️ No se encontró un micrófono activo en este dispositivo; puedes usar una pregunta rápida o escribir abajo.';
    }
    if (code === 'mic-busy') {
      return '🎙️ Otra aplicación (Zoom, Meet u otra pestaña) está usando el micrófono en este momento.';
    }
    if (code === 'insecure') {
      return '🔒 El micrófono requiere conexión segura HTTPS.';
    }
    if (code === 'no-speech') {
      return '🎙️ No escuché palabras claras. Toca el micrófono de nuevo y habla cerca, o escribe abajo.';
    }
    return '🎙️ No se pudo completar la captura de voz; toca el micrófono de nuevo o escribe tu consulta abajo.';
  }

  function createSmartVoiceSession(callbacks) {
    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    const hasMediaRec = Boolean(
      navigator.mediaDevices &&
      typeof navigator.mediaDevices.getUserMedia === 'function' &&
      typeof MediaRecorder !== 'undefined'
    );
    let activeRec = null;
    let activeMediaRecorder = null;
    let activeStream = null;
    let activeAudioCtx = null;
    let silenceTimer = null;
    let maxDurationTimer = null;
    let cancelled = false;
    let settled = false;

    function cleanupMedia() {
      if (silenceTimer) { clearInterval(silenceTimer); silenceTimer = null; }
      if (maxDurationTimer) { clearTimeout(maxDurationTimer); maxDurationTimer = null; }
      if (activeStream) {
        try { activeStream.getTracks().forEach(t => t.stop()); } catch (e) {}
        activeStream = null;
      }
      if (activeAudioCtx) {
        try { activeAudioCtx.close(); } catch (e) {}
        activeAudioCtx = null;
      }
    }

    function finishError(code) {
      if (settled) return;
      settled = true;
      cleanupMedia();
      if (callbacks.onError) callbacks.onError(code, formatMicErrorMessage(code));
    }

    function finishSuccess(text) {
      if (settled) return;
      settled = true;
      cleanupMedia();
      const clean = String(text || '').trim();
      if (!clean) {
        if (callbacks.onError) callbacks.onError('no-speech', formatMicErrorMessage('no-speech'));
        return;
      }
      if (callbacks.onResult) callbacks.onResult(clean);
    }

    async function startMediaRecorderFlow() {
      if (!hasMediaRec) {
        finishError('no-device');
        return;
      }
      if (!window.isSecureContext) {
        finishError('insecure');
        return;
      }
      try {
        if (callbacks.onStatus) callbacks.onStatus('🎙️ Solicitando permiso de micrófono...');
        activeStream = await navigator.mediaDevices.getUserMedia({
          audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true }
        });
      } catch (err) {
        const name = (err && err.name) || '';
        if (name === 'NotAllowedError' || name === 'PermissionDeniedError' || name === 'SecurityError') {
          finishError('permission-denied');
        } else if (name === 'NotFoundError' || name === 'DevicesNotFoundError') {
          finishError('no-device');
        } else if (name === 'NotReadableError' || name === 'TrackStartError') {
          finishError('mic-busy');
        } else {
          finishError('unavailable');
        }
        return;
      }

      if (cancelled || settled) {
        cleanupMedia();
        return;
      }

      const chunks = [];
      const chosenMime = pickRecorderMimeType();
      try {
        activeMediaRecorder = chosenMime
          ? new MediaRecorder(activeStream, { mimeType: chosenMime })
          : new MediaRecorder(activeStream);
      } catch (e) {
        cleanupMedia();
        finishError('unavailable');
        return;
      }

      const recMime = activeMediaRecorder.mimeType || chosenMime || 'audio/webm';
      activeMediaRecorder.ondataavailable = (ev) => {
        if (ev.data && ev.data.size > 0) chunks.push(ev.data);
      };

      activeMediaRecorder.onstop = async () => {
        cleanupMedia();
        if (cancelled || settled) return;
        const blob = new Blob(chunks, { type: recMime });
        if (!blob || blob.size < 600) {
          finishError('no-speech');
          return;
        }
        if (callbacks.onTranscribing) callbacks.onTranscribing();
        if (callbacks.onStatus) callbacks.onStatus('⏳ Procesando tu voz...');
        try {
          const b64 = await blobToBase64(blob);
          const signal = (typeof AbortSignal !== 'undefined' && typeof AbortSignal.timeout === 'function')
            ? AbortSignal.timeout(15000)
            : undefined;
          const resp = await fetch(TRANSCRIBE_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            signal,
            body: JSON.stringify({
              audio_base64: b64,
              mime_type: recMime,
              lang: document.documentElement.lang || 'es'
            })
          });
          const data = await resp.json();
          const spoken = data && data.transcript ? String(data.transcript).trim() : '';
          finishSuccess(spoken);
        } catch (err) {
          finishError('unavailable');
        }
      };

      if (callbacks.onListeningStart) callbacks.onListeningStart('recorder');
      if (callbacks.onStatus) callbacks.onStatus('🎙️ Grabando tu voz... habla ahora (toca otra vez para enviar)');
      activeMediaRecorder.start(250);

      // Detección de silencio tras hablar para enviar automáticamente sin exigir otro clic
      try {
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        if (AudioCtx) {
          activeAudioCtx = new AudioCtx();
          const src = activeAudioCtx.createMediaStreamSource(activeStream);
          const analyser = activeAudioCtx.createAnalyser();
          analyser.fftSize = 1024;
          src.connect(analyser);
          const buf = new Uint8Array(analyser.fftSize);
          let heardVoice = false;
          let silentSince = 0;
          const startedAt = Date.now();
          silenceTimer = setInterval(() => {
            if (!activeMediaRecorder || activeMediaRecorder.state !== 'recording') return;
            analyser.getByteTimeDomainData(buf);
            let sum = 0;
            for (let i = 0; i < buf.length; i++) {
              const v = (buf[i] - 128) / 128;
              sum += v * v;
            }
            const rms = Math.sqrt(sum / buf.length);
            const now = Date.now();
            if (rms > 0.022) {
              heardVoice = true;
              silentSince = 0;
            } else if (heardVoice && now - startedAt > 1200) {
              if (!silentSince) silentSince = now;
              if (now - silentSince >= 1500) {
                try { activeMediaRecorder.stop(); } catch (e) {}
              }
            }
          }, 150);
        }
      } catch (e) {}

      maxDurationTimer = setTimeout(() => {
        try {
          if (activeMediaRecorder && activeMediaRecorder.state === 'recording') {
            activeMediaRecorder.stop();
          }
        } catch (e) {}
      }, 8500);
    }

    function start() {
      if (!window.isSecureContext) {
        finishError('insecure');
        return;
      }
      if (!SpeechRec || preferRecorderFallback) {
        startMediaRecorderFlow();
        return;
      }

      let latestTranscript = '';
      let fallbackTriggered = false;
      try {
        activeRec = new SpeechRec();
        activeRec.lang = 'es-MX';
        activeRec.interimResults = true;
        activeRec.continuous = false;
        activeRec.maxAlternatives = 1;

        if (callbacks.onListeningStart) callbacks.onListeningStart('speech');
        if (callbacks.onStatus) callbacks.onStatus('🎙️ Escuchando tu voz... habla ahora');

        activeRec.onresult = (ev) => {
          if (cancelled || settled) return;
          let combined = '';
          let hasFinal = false;
          for (let i = 0; i < ev.results.length; i++) {
            const res = ev.results[i];
            if (res && res[0] && res[0].transcript) {
              combined += res[0].transcript;
              if (res.isFinal) hasFinal = true;
            }
          }
          combined = combined.trim();
          if (combined) {
            latestTranscript = combined;
            if (callbacks.onInterim) callbacks.onInterim(combined);
          }
          if (hasFinal && combined) {
            try { activeRec.stop(); } catch (e) {}
            finishSuccess(combined);
          }
        };

        activeRec.onerror = (ev) => {
          if (cancelled || settled) return;
          const errCode = (ev && ev.error) || '';
          if (latestTranscript) {
            finishSuccess(latestTranscript);
            return;
          }
          if (
            hasMediaRec &&
            (errCode === 'network' || errCode === 'service-not-allowed' || errCode === 'audio-capture' || errCode === 'not-allowed' || errCode === 'aborted' || !errCode)
          ) {
            preferRecorderFallback = true;
            fallbackTriggered = true;
            try { activeRec.abort(); } catch (e) {}
            startMediaRecorderFlow();
            return;
          }
          if (errCode === 'not-allowed' || errCode === 'service-not-allowed') {
            finishError('permission-denied');
          } else if (errCode === 'audio-capture') {
            finishError('no-device');
          } else if (errCode === 'no-speech') {
            finishError('no-speech');
          } else {
            finishError('unavailable');
          }
        };

        activeRec.onend = () => {
          if (cancelled || settled || fallbackTriggered) return;
          if (latestTranscript) {
            finishSuccess(latestTranscript);
          } else if (hasMediaRec && !preferRecorderFallback) {
            // Algunas versiones de Chrome desktop cierran SpeechRecognition al instante sin evento onerror útil
            preferRecorderFallback = true;
            startMediaRecorderFlow();
          } else {
            finishError('no-speech');
          }
        };

        activeRec.start();
      } catch (e) {
        if (hasMediaRec) {
          preferRecorderFallback = true;
          startMediaRecorderFlow();
        } else {
          finishError('unavailable');
        }
      }
    }

    function stopAndSubmit() {
      if (activeMediaRecorder && activeMediaRecorder.state === 'recording') {
        try { activeMediaRecorder.stop(); } catch (e) {}
        return;
      }
      if (activeRec) {
        try { activeRec.stop(); } catch (e) {}
        return;
      }
      cancelled = true;
      finishError('no-speech');
    }

    function cancel() {
      cancelled = true;
      settled = true;
      if (activeRec) {
        try { activeRec.abort(); } catch (e) {}
      }
      if (activeMediaRecorder && activeMediaRecorder.state === 'recording') {
        try { activeMediaRecorder.stop(); } catch (e) {}
      }
      cleanupMedia();
    }

    return { start, stopAndSubmit, cancel };
  }

  function mountVoiceStage() {
    const stageEl = document.getElementById('aura-voice-stage');
    if (!stageEl) return;

    const voiceSupported = supportsVoiceCapture();
    stageEl.innerHTML = `
      <div class="aura-stage-box" id="aura-stage-card">
        <div style="display:flex; flex-wrap:wrap; justify-content:space-between; align-items:center; gap:0.75rem; margin-bottom:0.85rem;">
          <div style="display:flex; align-items:center; gap:0.65rem;">
            <div class="aura-wave-bars" aria-hidden="true"><span></span><span></span><span></span><span></span></div>
            <div>
              <div style="font-size:0.88rem; font-weight:800; color:#ffffff;">Setter IA · Asistente de Voz en Vivo</div>
              <div id="aura-stage-status" role="status" aria-live="polite" style="font-size:0.78rem; color:#34d399;">Conectado al CRM · Listo para escucharte</div>
            </div>
          </div>
          <div style="display:flex; gap:0.5rem;">
            <button type="button" id="aura-mic-btn" class="hm-btn-emerald pia-btn-emerald" aria-pressed="false" style="padding:0.65rem 1.1rem; font-size:0.86rem; border-radius:12px;">
              <i class="fas fa-microphone" aria-hidden="true"></i>
              <span id="aura-mic-label">${voiceSupported ? 'Hablar por Voz Ahora' : 'Escuchar Saludo en Vivo'}</span>
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
          <button type="button" class="pia-qbtn aura-voice-pill" data-q="¿Cuáles son los paquetes, precios y horarios que manejan?">Ver Opciones</button>
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
    const micLabel = document.getElementById('aura-mic-label');
    const stopBtn = document.getElementById('aura-stop-btn');
    const textForm = document.getElementById('aura-voice-text-form');
    const textIn = document.getElementById('aura-voice-text-in');
    let voiceSession = null;

    function resetMicUi() {
      card.classList.remove('is-listening');
      micBtn.classList.remove('is-listening');
      micBtn.setAttribute('aria-pressed', 'false');
      if (micLabel) micLabel.textContent = voiceSupported ? 'Hablar por Voz Ahora' : 'Escuchar Saludo en Vivo';
    }

    async function runVoiceQuery(questionText) {
      if (!questionText) return;
      captureLeadContext(questionText);
      resetMicUi();
      statusTxt.style.color = '#34d399';
      statusTxt.textContent = 'Consultando al Asesor Comercial conectado al CRM...';
      transcript.innerHTML = `<div style="color:#93c5fd; margin-bottom:4px;"><strong>Tú:</strong> ${formatRichHtml(questionText)}</div><div><em>Escribiendo y preparando respuesta por voz...</em></div>`;

      const res = await askAssistant(questionText, 'voice');
      transcript.innerHTML =
        `<div style="color:#93c5fd; margin-bottom:4px;"><strong>Tú:</strong> ${formatRichHtml(questionText)}</div>` +
        `<div style="color:#ecfdf5;"><strong>Asistente IA:</strong> ${formatRichHtml(res.reply)}</div>` +
        `<div style="margin-top:8px; display:flex; align-items:center; justify-content:flex-start; gap:8px;">` +
        `<button type="button" class="pia-speak-btn aura-replay-btn"><i class="fas fa-volume-high" aria-hidden="true"></i> <span>Escuchar Respuesta</span></button>` +
        `</div>` +
        buildCtasHtml(res.ctas);
      bindBookingCtaHandlers(transcript);
      const replayBtn = transcript.querySelector('.aura-replay-btn');
      if (replayBtn) {
        replayBtn.addEventListener('click', () => {
          unlockSpeechSynthesis();
          stopBtn.hidden = false;
          card.classList.add('is-speaking');
          statusTxt.textContent = 'Reproduciendo respuesta en vivo...';
          speakText(res.replySpeech, () => card.classList.add('is-speaking'), () => {
            card.classList.remove('is-speaking');
            statusTxt.textContent = 'Listo para tu siguiente pregunta';
            stopBtn.hidden = true;
          });
        });
      }

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
      if (voiceSession) {
        voiceSession.cancel();
        voiceSession = null;
      }
      stopSpeaking();
      resetMicUi();
      card.classList.remove('is-speaking');
      statusTxt.style.color = '#34d399';
      statusTxt.textContent = 'Audio detenido';
      stopBtn.hidden = true;
    });

    micBtn.addEventListener('click', () => {
      unlockSpeechSynthesis();
      if (!voiceSupported) {
        runVoiceQuery('Hola, explícame brevemente cómo ayudan a un dueño de negocio con web, WhatsApp 24/7 y calendario.');
        return;
      }
      if (micBtn.classList.contains('is-listening') && voiceSession) {
        statusTxt.textContent = '⏳ Enviando tu audio...';
        voiceSession.stopAndSubmit();
        return;
      }
      stopSpeaking();
      voiceSession = createSmartVoiceSession({
        onListeningStart: () => {
          card.classList.add('is-listening');
          micBtn.classList.add('is-listening');
          micBtn.setAttribute('aria-pressed', 'true');
          if (micLabel) micLabel.textContent = 'Enviar Voz Ahora';
          stopBtn.hidden = false;
          statusTxt.style.color = '#fbbf24';
        },
        onStatus: (msg) => {
          statusTxt.textContent = msg;
        },
        onInterim: (partial) => {
          if (textIn) textIn.value = partial;
          transcript.innerHTML = `<div style="color:#93c5fd;"><strong>Escuchando:</strong> ${formatRichHtml(partial)}</div>`;
        },
        onTranscribing: () => {
          resetMicUi();
          statusTxt.style.color = '#38bdf8';
        },
        onResult: (spoken) => {
          voiceSession = null;
          if (textIn) textIn.value = '';
          runVoiceQuery(spoken);
        },
        onError: (_code, userMsg) => {
          voiceSession = null;
          resetMicUi();
          stopBtn.hidden = true;
          statusTxt.style.color = '#fda4af';
          statusTxt.textContent = userMsg;
        }
      });
      voiceSession.start();
    });

    document.querySelectorAll('.aura-voice-pill').forEach(btn => {
      btn.addEventListener('click', () => {
        unlockSpeechSynthesis();
        runVoiceQuery(btn.getAttribute('data-q') || '');
      });
    });

    if (textForm && textIn) {
      textForm.addEventListener('submit', (e) => {
        e.preventDefault();
        unlockSpeechSynthesis();
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

    const voiceSupported = supportsVoiceCapture();

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
          <button type="button" id="pia-cp-tts-toggle" class="pia-cp-iconbtn is-active" aria-pressed="true" title="Leer respuestas en voz alta" aria-label="Leer respuestas en voz alta"><i class="fas fa-volume-high" aria-hidden="true"></i></button>
          <button type="button" id="pia-cp-reset" class="pia-cp-iconbtn" title="Reiniciar conversación" aria-label="Reiniciar conversación"><i class="fas fa-rotate-left" aria-hidden="true"></i></button>
          <button type="button" id="pia-cp-close" class="pia-cp-iconbtn" title="Cerrar asistente" aria-label="Cerrar asistente">✕</button>
        </div>
      </div>
      <div class="pia-cp-messages" id="pia-cp-messages"></div>
      <div class="pia-cp-quick">
        <button type="button" class="pia-qbtn pia-cp-q" data-q="Quiero información de páginas web y 4 Empleados Digitales">Web + IA 24/7</button>
        <button type="button" class="pia-qbtn pia-cp-q" data-q="Quiero ver el embudo de Reels y agendar demo">Reels &amp; Agenda</button>
        <button type="button" class="pia-qbtn pia-cp-q" data-q="¿Qué paquetes, precios y horarios manejan para mi negocio?">Ver Opciones</button>
      </div>
      <div id="pia-cp-status" class="pia-cp-status" role="status" aria-live="polite"></div>
      <form class="pia-cp-inputrow" id="pia-cp-form">
        <label for="pia-cp-input" class="pia-visually-hidden">Escribe o dicta tu consulta para el Asesor Comercial</label>
        <input type="text" id="pia-cp-input" placeholder="Escribe o habla por micrófono..." autocomplete="off">
        ${voiceSupported ? '<button type="button" id="pia-cp-mic" aria-pressed="false" title="Hablar por Voz" aria-label="Hablar por voz"><i class="fas fa-microphone" aria-hidden="true"></i></button>' : ''}
        <button type="submit" aria-label="Enviar mensaje" style="background:#f59e0b; color:#090d16; border:0; border-radius:10px; padding:9px 13px; font-weight:800; cursor:pointer; flex-shrink:0;">Enviar</button>
      </form>
      <div class="pia-cp-actions">
        <a href="${CAL_DIAGNOSTICO_URL}" id="pia-cp-cal-link" style="background:rgba(245,158,11,0.16); border:1px solid rgba(251,191,36,0.45); color:#fde68a;">📅 Agendar Cita</a>
        <a href="${WA_URL}" id="pia-cp-wa-link" target="_blank" rel="noopener" style="background:rgba(16,185,129,0.18); border:1px solid rgba(52,211,153,0.45); color:#d1fae5;">💬 WhatsApp Directo</a>
      </div>
    `;

    document.body.appendChild(btn);
    document.body.appendChild(panel);
    syncDirectWaUrl();

    const msgsBox = document.getElementById('pia-cp-messages');
    const closeBtn = document.getElementById('pia-cp-close');
    const resetBtn = document.getElementById('pia-cp-reset');
    const ttsToggleBtn = document.getElementById('pia-cp-tts-toggle');
    const cpStatus = document.getElementById('pia-cp-status');
    const cpForm = document.getElementById('pia-cp-form');
    const cpInput = document.getElementById('pia-cp-input');
    const cpMic = document.getElementById('pia-cp-mic');
    const calLink = document.getElementById('pia-cp-cal-link');

    let autoSpeakVoiceReplies = true;
    let usedKeyboardDictation = false;
    let wasPasted = false;
    let lastInputLength = 0;
    let chatVoiceSession = null;

    function setChatStatus(msg, isError) {
      if (!cpStatus) return;
      if (!msg) {
        cpStatus.textContent = '';
        cpStatus.classList.remove('is-visible', 'is-error');
        return;
      }
      cpStatus.textContent = msg;
      cpStatus.classList.add('is-visible');
      cpStatus.classList.toggle('is-error', Boolean(isError));
    }

    function attachSpeakButton(botBubbleDiv, plainSpeech) {
      if (!botBubbleDiv || !plainSpeech) return;
      const tools = document.createElement('div');
      tools.className = 'pia-msg-bot-tools';
      const spBtn = document.createElement('button');
      spBtn.type = 'button';
      spBtn.className = 'pia-speak-btn';
      spBtn.innerHTML = '<i class="fas fa-volume-high" aria-hidden="true"></i><span>Escuchar</span>';
      spBtn.addEventListener('click', () => {
        unlockSpeechSynthesis();
        speakText(plainSpeech, () => {
          spBtn.innerHTML = '<i class="fas fa-stop" aria-hidden="true"></i><span>Reproduciendo...</span>';
        }, () => {
          spBtn.innerHTML = '<i class="fas fa-volume-high" aria-hidden="true"></i><span>Escuchar</span>';
        });
      });
      tools.appendChild(spBtn);
      botBubbleDiv.appendChild(tools);
    }

    function appendBubble(role, text, ctas) {
      const div = document.createElement('div');
      div.className = role === 'user' ? 'pia-msg-user' : 'pia-msg-bot';
      div.innerHTML = formatRichHtml(text) + (role === 'bot' ? buildCtasHtml(ctas) : '');
      if (role === 'bot' && text && text !== 'Escribiendo...') {
        attachSpeakButton(div, text.replace(/https?:\/\/\S+/g, '').replace(/\*\*/g, '').trim());
      }
      bindBookingCtaHandlers(div, () => setOpen(false));
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
    closeBtn.addEventListener('click', () => {
      if (chatVoiceSession) {
        chatVoiceSession.cancel();
        chatVoiceSession = null;
      }
      if (cpMic) {
        cpMic.classList.remove('is-listening');
        cpMic.setAttribute('aria-pressed', 'false');
      }
      setOpen(false);
    });
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && panel.classList.contains('is-open')) setOpen(false);
    });
    if (calLink) {
      calLink.addEventListener('click', (e) => {
        e.preventDefault();
        setOpen(false);
        openInlineCalendarModal(CAL_DIAGNOSTICO_URL);
      });
    }

    if (ttsToggleBtn) {
      ttsToggleBtn.addEventListener('click', () => {
        autoSpeakVoiceReplies = !autoSpeakVoiceReplies;
        ttsToggleBtn.classList.toggle('is-active', autoSpeakVoiceReplies);
        ttsToggleBtn.setAttribute('aria-pressed', String(autoSpeakVoiceReplies));
        const icon = ttsToggleBtn.querySelector('i');
        if (icon) icon.className = autoSpeakVoiceReplies ? 'fas fa-volume-high' : 'fas fa-volume-xmark';
        if (!autoSpeakVoiceReplies) {
          stopSpeaking();
          setChatStatus('🔇 Respuesta hablada silenciada (solo texto).', false);
          setTimeout(() => setChatStatus('', false), 2200);
        } else {
          unlockSpeechSynthesis();
          setChatStatus('🔊 Voz activada: leeré en voz alta tus respuestas por micrófono.', false);
          setTimeout(() => setChatStatus('', false), 2400);
        }
      });
    }

    resetBtn.addEventListener('click', () => {
      try {
        stopSpeaking();
        if (chatVoiceSession) {
          chatVoiceSession.cancel();
          chatVoiceSession = null;
        }
        setChatStatus('', false);
        sessionStorage.removeItem(HISTORY_KEY);
        sessionStorage.removeItem(LEAD_DRAFT_KEY);
        leadDraft.name = '';
        leadDraft.email = '';
        leadDraft.phone = '';
        leadDraft.company = '';
        leadDraft.lastMsg = '';
        syncDirectWaUrl();
        sessionId = createSessionId();
        sessionStorage.setItem(SESSION_KEY, sessionId);
      } catch (e) {}
      historyStore.length = 0;
      restoreOrGreet();
    });

    async function sendChatMsg(txt, speakReply = false) {
      if (!txt) return;
      captureLeadContext(txt);
      appendBubble('user', txt);
      saveFusionHistory('user', txt);

      const bDiv = appendBubble('bot', 'Escribiendo...');
      const res = await askAssistant(txt, speakReply ? 'voice' : 'chat');
      bDiv.innerHTML = formatRichHtml(res.reply) + buildCtasHtml(res.ctas);
      attachSpeakButton(bDiv, res.replySpeech);
      bindBookingCtaHandlers(bDiv, () => setOpen(false));
      msgsBox.scrollTop = msgsBox.scrollHeight;
      saveFusionHistory('bot', res.reply, res.ctas);

      if (speakReply && autoSpeakVoiceReplies) {
        speakText(res.replySpeech);
      }
    }

    if (cpInput) {
      cpInput.addEventListener('paste', () => {
        wasPasted = true;
      });
      // Detecta dictado del teclado nativo de iOS/Android sin confundirlo con Ctrl+V/pegar
      cpInput.addEventListener('input', (ev) => {
        const curLen = cpInput.value.length;
        const inputType = ev && ev.inputType ? ev.inputType : '';
        if (wasPasted) {
          wasPasted = false;
        } else if (inputType === 'insertFromDictation' || (curLen - lastInputLength > 4)) {
          usedKeyboardDictation = true;
        } else if (curLen === 0) {
          usedKeyboardDictation = false;
        }
        lastInputLength = curLen;
      });
    }

    cpForm.addEventListener('submit', (e) => {
      e.preventDefault();
      unlockSpeechSynthesis();
      const val = cpInput.value.trim();
      if (!val) return;
      const shouldSpeak = usedKeyboardDictation && autoSpeakVoiceReplies;
      cpInput.value = '';
      lastInputLength = 0;
      usedKeyboardDictation = false;
      setChatStatus('', false);
      sendChatMsg(val, shouldSpeak);
    });

    if (cpMic && voiceSupported) {
      cpMic.addEventListener('click', () => {
        unlockSpeechSynthesis();
        if (cpMic.classList.contains('is-listening') && chatVoiceSession) {
          setChatStatus('⏳ Enviando tu audio...', false);
          chatVoiceSession.stopAndSubmit();
          return;
        }
        stopSpeaking();
        chatVoiceSession = createSmartVoiceSession({
          onListeningStart: () => {
            cpMic.classList.add('is-listening');
            cpMic.setAttribute('aria-pressed', 'true');
            const ic = cpMic.querySelector('i');
            if (ic) ic.className = 'fas fa-stop';
          },
          onStatus: (msg) => setChatStatus(msg, false),
          onInterim: (partial) => {
            if (cpInput) cpInput.value = partial;
          },
          onTranscribing: () => {
            cpMic.classList.remove('is-listening');
            cpMic.setAttribute('aria-pressed', 'false');
            const ic = cpMic.querySelector('i');
            if (ic) ic.className = 'fas fa-microphone';
          },
          onResult: (spoken) => {
            chatVoiceSession = null;
            cpMic.classList.remove('is-listening');
            cpMic.setAttribute('aria-pressed', 'false');
            const ic = cpMic.querySelector('i');
            if (ic) ic.className = 'fas fa-microphone';
            if (cpInput) cpInput.value = '';
            lastInputLength = 0;
            usedKeyboardDictation = false;
            setChatStatus('', false);
            sendChatMsg(spoken, true);
          },
          onError: (_code, userMsg) => {
            chatVoiceSession = null;
            cpMic.classList.remove('is-listening');
            cpMic.setAttribute('aria-pressed', 'false');
            const ic = cpMic.querySelector('i');
            if (ic) ic.className = 'fas fa-microphone';
            setChatStatus(userMsg, true);
          }
        });
        chatVoiceSession.start();
      });
    }

    panel.querySelectorAll('.pia-cp-q').forEach(qb => {
      qb.addEventListener('click', () => {
        unlockSpeechSynthesis();
        setChatStatus('', false);
        sendChatMsg(qb.getAttribute('data-q') || '', false);
      });
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

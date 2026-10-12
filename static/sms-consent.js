/**
 * Consentimiento SMS (A2P 10DLC) — Agencia ProsperIA LLC
 *
 * Los formularios web son la ÚNICA fuente de suscripción SMS del sitio.
 * Cada formulario con teléfono incluye una casilla opcional `.sms-consent-input`
 * (desmarcada por defecto). Este script añade `sms_consent: true|false` a todo
 * envío hacia /api/auth/contact, leyendo la casilla del formulario que se envía.
 */
(function () {
  if (window.__smsConsentPatched || typeof window.fetch !== 'function') return;
  window.__smsConsentPatched = true;

  function readConsent() {
    var active = document.activeElement;
    var form = active && active.closest ? active.closest('form') : null;
    var box = form ? form.querySelector('.sms-consent-input') : null;
    if (box) return !!box.checked;
    return !!document.querySelector('.sms-consent-input:checked');
  }

  var originalFetch = window.fetch;
  window.fetch = function (input, init) {
    try {
      var url = typeof input === 'string' ? input : (input && input.url) || '';
      if (url.indexOf('/api/auth/contact') !== -1 && init && typeof init.body === 'string') {
        var data = JSON.parse(init.body);
        if (data && typeof data === 'object' && !('sms_consent' in data)) {
          data.sms_consent = readConsent();
          init = Object.assign({}, init, { body: JSON.stringify(data) });
        }
      }
    } catch (e) { /* si algo falla, se envía el formulario tal cual */ }
    return originalFetch.call(this, input, init);
  };
})();

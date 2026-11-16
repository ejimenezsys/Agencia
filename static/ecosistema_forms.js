/**
 * Helper compartido para formularios de solicitud/cotización en los menús del ecosistema ProsperIA.
 */
(function () {
  window.initEcosystemLeadForm = function (formId, sourceTag, redirectToThanks = false) {
    const form = document.getElementById(formId);
    if (!form) return;

    const statusEl = form.querySelector('[data-form-status]');
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalBtnHtml = submitBtn ? submitBtn.innerHTML : '';

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (!form.reportValidity()) return;

      const hp = form.querySelector('[name="website_hp"]');
      if (hp && hp.value.trim()) return;

      const fd = new FormData(form);
      const name = String(fd.get('name') || '').trim();
      const email = String(fd.get('email') || '').trim();
      const phone = String(fd.get('phone') || '').trim();
      const company = String(fd.get('company') || '').trim();
      const industry = String(fd.get('industry') || '').trim();
      const message = String(fd.get('message') || '').trim();
      const smsConsent = Boolean(fd.get('sms_consent'));

      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin" aria-hidden="true"></i><span>Enviando solicitud...</span>';
      }
      if (statusEl) statusEl.style.display = 'none';

      try {
        const res = await fetch('/api/auth/contact', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name,
            email,
            phone,
            company,
            industry,
            message: message || `Solicitud desde ${sourceTag}`,
            source: sourceTag,
            sms_consent: smsConsent
          })
        });
        const data = await res.json();
        if (!res.ok || !data.success) {
          throw new Error(data.error || 'No se pudo procesar tu solicitud.');
        }

        if (statusEl) {
          statusEl.style.display = 'block';
          statusEl.style.background = 'rgba(16, 185, 129, 0.14)';
          statusEl.style.border = '1px solid rgba(16, 185, 129, 0.45)';
          statusEl.style.color = '#6ee7b7';
          statusEl.innerHTML = '✅ ¡Solicitud registrada! Un especialista de ProsperIA ya tiene tus datos y puedes continuar directo por WhatsApp si deseas atención inmediata.';
        }

        if (redirectToThanks) {
          const qs = new URLSearchParams({ name, email, phone, company });
          setTimeout(() => { window.location.href = `/gracias?${qs.toString()}`; }, 700);
        } else if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerHTML = originalBtnHtml;
        }
      } catch (err) {
        if (statusEl) {
          statusEl.style.display = 'block';
          statusEl.style.background = 'rgba(244, 63, 94, 0.14)';
          statusEl.style.border = '1px solid rgba(244, 63, 94, 0.45)';
          statusEl.style.color = '#fda4af';
          statusEl.textContent = err.message || 'Error de conexión. Intenta nuevamente o escríbenos por WhatsApp.';
        }
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerHTML = originalBtnHtml;
        }
      }
    });
  };
})();

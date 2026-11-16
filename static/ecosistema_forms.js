/**
 * Helper unificado para formularios comerciales de Agencia Prosper IA LLC.
 * Registra el prospecto en el CRM, asigna Closer en Round-Robin y despliega el Calendario en vivo.
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
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin" aria-hidden="true"></i><span>Asignando especialista y abriendo calendario...</span>';
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

        if (typeof window.trackEvent === 'function') {
          window.trackEvent('generate_lead', { source: sourceTag, solution: industry });
        }

        const closerName = data.closer_name || 'Especialista Agencia Prosper IA';
        const calendarUrl = data.calendar_url || 'https://api.agenciaprosperia.com/widget/booking/gqoqyrr112bvjTJYqOi8';

        if (redirectToThanks) {
          const qs = new URLSearchParams({ name, email, phone, company });
          setTimeout(() => { window.location.href = `/gracias?${qs.toString()}`; }, 500);
          return;
        }

        // Desplegar confirmación + Calendario Round-Robin embebido en vivo
        let calHost = document.getElementById(`${formId}-calendar-host`);
        if (!calHost) {
          calHost = document.createElement('div');
          calHost.id = `${formId}-calendar-host`;
          calHost.style.marginTop = '1.25rem';
          form.insertAdjacentElement('afterend', calHost);
        }

        if (statusEl) {
          statusEl.style.display = 'block';
          statusEl.style.background = 'rgba(16, 185, 129, 0.14)';
          statusEl.style.border = '1px solid rgba(16, 185, 129, 0.45)';
          statusEl.style.color = '#d1fae5';
          statusEl.innerHTML = `✅ <strong>¡Listo, ${name}!</strong> Tu solicitud quedó registrada en el CRM con <strong>${closerName}</strong> (asignación automática Round-Robin). Elige tu día y hora aquí abajo:`;
        }

        calHost.innerHTML = `
          <div style="border-radius:18px; overflow:hidden; border:1px solid rgba(251,191,36,0.45); background:#040813; box-shadow:0 20px 45px rgba(0,0,0,0.45);">
            <div style="padding:0.9rem 1.2rem; background:rgba(15,23,42,0.95); border-bottom:1px solid rgba(255,255,255,0.1); display:flex; flex-wrap:wrap; justify-content:space-between; align-items:center; gap:0.65rem;">
              <div style="font-size:0.86rem; font-weight:800; color:#fbbf24;">
                <i class="fas fa-calendar-check" aria-hidden="true"></i> Agenda asignada con ${closerName}
              </div>
              <a href="${calendarUrl}" target="_blank" rel="noopener" style="font-size:0.8rem; font-weight:700; color:#67e8f9; text-decoration:underline;">Abrir calendario en nueva pestaña ↗</a>
            </div>
            <iframe
              src="${calendarUrl}"
              title="Calendario de citas Agencia Prosper IA"
              style="width:100%; min-height:720px; border:0; display:block; background:#ffffff;"
              loading="lazy"
              allow="camera; microphone; autoplay">
            </iframe>
          </div>
        `;
        calHost.scrollIntoView({ behavior: 'smooth', block: 'start' });

        if (submitBtn) {
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

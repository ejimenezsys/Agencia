/**
 * Su Notaria USA - Lógica del Cliente (main.js)
 * Controla la interactividad del menú móvil, modal de búsqueda, acordeón y formulario.
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. CONTROL DEL MENÚ MÓVIL RESPONSIVE
    const navToggle = document.getElementById('nav-toggle');
    const navMenu = document.getElementById('nav-menu');

    if (navToggle && navMenu) {
        navToggle.addEventListener('click', () => {
            const isExpanded = navToggle.getAttribute('aria-expanded') === 'true';
            navToggle.setAttribute('aria-expanded', !isExpanded);
            navToggle.classList.toggle('active');
            navMenu.classList.toggle('active');
        });

        // Cerrar menú al hacer clic en un enlace móvil
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                navToggle.setAttribute('aria-expanded', 'false');
                navToggle.classList.remove('active');
                navMenu.classList.remove('active');
            });
        });
    }

    // 2. MODAL DE BÚSQUEDA
    const searchBtn = document.getElementById('search-btn');
    const searchModal = document.getElementById('search-modal');
    const searchModalClose = document.getElementById('search-modal-close');
    const searchInput = document.getElementById('search-input');

    if (searchBtn && searchModal && searchModalClose) {
        searchBtn.addEventListener('click', () => {
            searchModal.classList.add('active');
            searchModal.setAttribute('aria-hidden', 'false');
            searchModal.setAttribute('tabindex', '0');
            if (searchInput) {
                setTimeout(() => searchInput.focus(), 100);
            }
        });

        const cerrarModalBusqueda = () => {
            searchModal.classList.remove('active');
            searchModal.setAttribute('aria-hidden', 'true');
            searchModal.setAttribute('tabindex', '-1');
            if (searchInput) {
                searchInput.value = '';
            }
        };

        searchModalClose.addEventListener('click', cerrarModalBusqueda);

        // Cerrar modal al hacer clic fuera del contenido
        searchModal.addEventListener('click', (e) => {
            if (e.target === searchModal) {
                cerrarModalBusqueda();
            }
        });

        // Cerrar con tecla Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && searchModal.classList.contains('active')) {
                cerrarModalBusqueda();
            }
        });
    }

    // 3. ACORDEÓN DE LA SECCIÓN ¿POR QUÉ NOSOTROS?
    const accordionHeaders = document.querySelectorAll('.accordion-header');

    accordionHeaders.forEach(header => {
        header.addEventListener('click', () => {
            const item = header.parentElement;
            const isActive = item.classList.contains('active');

            // Cerrar todos los demás elementos del acordeón (comportamiento exclusivo)
            const activeItems = document.querySelectorAll('.accordion-item.active');
            activeItems.forEach(activeItem => {
                if (activeItem !== item) {
                    activeItem.classList.remove('active');
                    activeItem.querySelector('.accordion-header').setAttribute('aria-expanded', 'false');
                }
            });

            // Conmutar el elemento clickeado
            if (isActive) {
                item.classList.remove('active');
                header.setAttribute('aria-expanded', 'false');
            } else {
                item.classList.add('active');
                header.setAttribute('aria-expanded', 'true');
            }
        });
    });

    // 4. FORMULARIO DE CONTACTO E INTEGRACIÓN CON LA API CRM
    const contactForm = document.getElementById('notary-contact-form');
    const submitBtn = document.getElementById('submit-btn');
    const btnText = document.getElementById('btn-text');
    const btnSpinner = document.getElementById('btn-spinner');
    const alertSuccess = document.getElementById('form-alert-success');
    const alertError = document.getElementById('form-alert-error');
    const alertSuccessText = document.getElementById('form-alert-success-text');
    const alertErrorText = document.getElementById('form-alert-error-text');

    if (contactForm) {
        contactForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            // Restablecer alertas
            alertSuccess.style.display = 'none';
            alertError.style.display = 'none';

            // Capturar datos del formulario
            const nombre = document.getElementById('nombre');
            const email = document.getElementById('email');
            const telefono = document.getElementById('telefono');
            const tipoServicio = document.getElementById('tipo_servicio');
            const mensaje = document.getElementById('mensaje');

            let formValido = true;

            // Validador de expresión regular de email
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

            // Limpiar estados de error previos
            const inputs = [nombre, email, telefono, tipoServicio, mensaje];
            inputs.forEach(input => {
                if (input) input.classList.remove('field-invalid');
            });

            // Validar Nombre
            if (!nombre.value.trim()) {
                nombre.classList.add('field-invalid');
                formValido = false;
            }

            // Validar Correo
            if (!email.value.trim() || !emailRegex.test(email.value.trim())) {
                email.classList.add('field-invalid');
                formValido = false;
            }

            // Validar Teléfono
            if (!telefono.value.trim()) {
                telefono.classList.add('field-invalid');
                formValido = false;
            }

            // Validar Tipo de Servicio
            if (!tipoServicio.value) {
                tipoServicio.classList.add('field-invalid');
                formValido = false;
            }

            // Validar Mensaje
            if (!mensaje.value.trim()) {
                mensaje.classList.add('field-invalid');
                formValido = false;
            }

            if (!formValido) {
                // Desplazarse al primer campo inválido para mejorar UX
                const primerInvalido = document.querySelector('.field-invalid');
                if (primerInvalido) {
                    primerInvalido.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    primerInvalido.focus();
                }
                return;
            }

            // Si el formulario es válido, procesar el envío
            const datosPayload = {
                nombre: nombre.value.trim(),
                email: email.value.trim(),
                telefono: telefono.value.trim(),
                tipo_servicio: tipoServicio.value,
                mensaje: mensaje.value.trim()
            };

            // Mostrar estado de carga (Spinner)
            submitBtn.disabled = true;
            btnText.style.display = 'none';
            btnSpinner.style.display = 'inline-block';

            try {
                const response = await fetch('/api/contacto', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(datosPayload)
                });

                const data = await response.json();

                if (response.status === 201 && data.status === 'success') {
                    // Limpiar formulario al tener éxito
                    contactForm.reset();
                    const successMsg = document.documentElement.lang === 'en'
                        ? "We have received your request and a specialist will review your case shortly! A confirmation has been sent to your email."
                        : "¡Hemos recibido su solicitud y un especialista revisará su caso en breve! Se ha enviado una confirmación a su correo electrónico.";
                    alertSuccessText.textContent = successMsg;
                    alertSuccess.style.display = 'flex';
                    alertSuccess.scrollIntoView({ behavior: 'smooth', block: 'center' });
                } else {
                    // Error del servidor (ej. validaciones o BD)
                    const errorMsgFallback = document.documentElement.lang === 'en'
                        ? "There was an error processing your message. Please try again."
                        : "Hubo un error al procesar el mensaje. Intente de nuevo.";
                    const errorDetail = data.detail || errorMsgFallback;
                    alertErrorText.textContent = Array.isArray(errorDetail) ? errorDetail[0].msg : errorDetail;
                    alertError.style.display = 'flex';
                    alertError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            } catch (err) {
                console.error("Error en petición de formulario:", err);
                const connectErrMsg = document.documentElement.lang === 'en'
                    ? "Could not connect to the server. Please check your network connection and try again later."
                    : "No se pudo conectar con el servidor. Verifique su conexión de red e intente más tarde.";
                alertErrorText.textContent = connectErrMsg;
                alertError.style.display = 'flex';
                alertError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            } finally {
                // Restablecer botón
                submitBtn.disabled = false;
                btnText.style.display = 'inline-block';
                btnSpinner.style.display = 'none';
            }
        });
    }
});

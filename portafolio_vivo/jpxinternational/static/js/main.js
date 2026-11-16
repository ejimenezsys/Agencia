/**
 * JPX International Investments Inc.
 * Script del Cliente Principal (main.js)
 * Manejo de navegación responsiva, carrusel de testimonios y validaciones B2B.
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Menú de Navegación Móvil
    const navToggle = document.getElementById('nav-toggle');
    const navMenu = document.getElementById('nav-menu');
    
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', () => {
            const expanded = navToggle.getAttribute('aria-expanded') === 'true';
            navToggle.setAttribute('aria-expanded', !expanded);
            navMenu.classList.toggle('active');
            navToggle.classList.toggle('active');
        });
    }

    // 2. Carrusel de Testimonios
    const slides = document.querySelectorAll('.testimonial-slide');
    const dots = document.querySelectorAll('.testimonial-dot');
    let currentSlide = 0;
    let slideInterval;

    function showSlide(index) {
        if (slides.length === 0) return;
        
        slides.forEach(slide => slide.classList.remove('active'));
        dots.forEach(dot => dot.classList.remove('active'));
        
        slides[index].classList.add('active');
        dots[index].classList.add('active');
        currentSlide = index;
    }

    function nextSlide() {
        let next = (currentSlide + 1) % slides.length;
        showSlide(next);
    }

    if (slides.length > 0) {
        // Inicializar intervalo automático (cada 6 segundos)
        slideInterval = setInterval(nextSlide, 6000);
        
        dots.forEach((dot, index) => {
            dot.addEventListener('click', () => {
                clearInterval(slideInterval);
                showSlide(index);
                // Reiniciar el auto-play tras la interacción del usuario
                slideInterval = setInterval(nextSlide, 6000);
            });
        });
    }

    // 3. Validaciones B2B y Envío AJAX del Formulario de Contacto
    const contactForm = document.getElementById('contact-form');
    
    if (contactForm) {
        const genericDomains = [
            'gmail.com', 'yahoo.com', 'hotmail.com', 'live.com', 
            'outlook.com', 'aol.com', 'zoho.com', 'proton.me', 
            'protonmail.com', 'yandex.com', 'mail.com', 'icloud.com'
        ];

        contactForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            // Ocultar alertas
            const alertSuccess = document.getElementById('alert-success');
            const alertError = document.getElementById('alert-error');
            alertSuccess.style.display = 'none';
            alertError.style.display = 'none';
            
            // Resetear errores visuales
            const inputs = contactForm.querySelectorAll('.form-control');
            inputs.forEach(input => {
                input.classList.remove('error');
                const errorSpan = document.getElementById(`error-${input.id}`);
                if (errorSpan) errorSpan.style.display = 'none';
            });

            let isValid = true;
            
            // Campos a validar
            const nombreCorp = document.getElementById('nombre_corporacion');
            const nombreExec = document.getElementById('nombre_ejecutivo');
            const emailInst = document.getElementById('email_institucional');
            const areaInteres = document.getElementById('area_operativa_interes');
            const rangoCapital = document.getElementById('rango_capital_usd');

            // Validar Nombre Corporación
            if (!nombreCorp.value.trim() || /<|>|"|'/.test(nombreCorp.value)) {
                showInputError(nombreCorp);
                isValid = false;
            }

            // Validar Nombre Ejecutivo
            if (!nombreExec.value.trim() || /<|>|"|'/.test(nombreExec.value)) {
                showInputError(nombreExec);
                isValid = false;
            }

            // Validar Email B2B (Corporativo)
            const emailVal = emailInst.value.trim().toLowerCase();
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            
            if (!emailRegex.test(emailVal)) {
                showInputError(emailInst);
                isValid = false;
            } else {
                const domain = emailVal.split('@')[1];
                if (genericDomains.includes(domain)) {
                    showInputError(emailInst);
                    isValid = false;
                }
            }

            // Validar Selector de Área
            if (!areaInteres.value) {
                showInputError(areaInteres);
                isValid = false;
            }

            // Validar Rango de Capital
            if (!rangoCapital.value) {
                showInputError(rangoCapital);
                isValid = false;
            }

            if (!isValid) {
                alertError.style.display = 'block';
                alertError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                return;
            }

            // Envío de Datos mediante Fetch API
            const submitBtn = document.getElementById('submit-btn');
            submitBtn.disabled = true;

            // Detección de idioma y traducción de mensajes de procesamiento/error
            const lang = document.cookie.split('; ').find(row => row.startsWith('lang='))?.split('=')[1] || 'es';
            const translations = {
                es: {
                    processing: 'Procesando Calificación Fiduciaria...',
                    submit: 'Enviar Formulario Fiduciario',
                    serverError: 'Ocurrió un error en el servidor.',
                    connError: 'Error de conexión. Intente más tarde.',
                    duplicateEmail: 'La dirección de correo institucional ya se encuentra registrada en nuestro CRM fiduciario.'
                },
                en: {
                    processing: 'Processing Fiduciary Qualification...',
                    submit: 'Submit Fiduciary Form',
                    serverError: 'An error occurred on the server.',
                    connError: 'Connection error. Please try again later.',
                    duplicateEmail: 'The institutional email address is already registered in our fiduciary CRM.'
                },
                pt: {
                    processing: 'Processando Qualificação Fiduciária...',
                    submit: 'Enviar Formulário Fiduciário',
                    serverError: 'Ocorreu um erro no servidor.',
                    connError: 'Erro de conexão. Tente novamente mais tarde.',
                    duplicateEmail: 'O endereço de e-mail institucional já está registrado em nosso CRM fiduciário.'
                }
            };
            const t = translations[lang] || translations.es;

            submitBtn.textContent = t.processing;

            const payload = {
                nombre_corporacion: nombreCorp.value.trim(),
                nombre_ejecutivo: nombreExec.value.trim(),
                email_institucional: emailVal,
                area_operativa_interes: areaInteres.value,
                rango_capital_usd: parseFloat(rangoCapital.value)
            };

            try {
                const response = await fetch('/contacto', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload)
                });

                const data = await response.json();

                if (response.ok) {
                    alertSuccess.style.display = 'block';
                    contactForm.reset();
                    alertSuccess.scrollIntoView({ behavior: 'smooth', block: 'center' });
                } else {
                    let errorMsg = data.detail || t.serverError;
                    if (data.detail === "La dirección de correo institucional ya se encuentra registrada en nuestro CRM fiduciario.") {
                        errorMsg = t.duplicateEmail;
                    }
                    alertError.textContent = errorMsg;
                    alertError.style.display = 'block';
                    alertError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            } catch (err) {
                console.error(err);
                alertError.textContent = t.connError;
                alertError.style.display = 'block';
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = t.submit;
            }
        });
    }

    function showInputError(inputElement) {
        inputElement.classList.add('error');
        const errorSpan = document.getElementById(`error-${inputElement.id}`);
        if (errorSpan) {
            errorSpan.style.display = 'block';
        }
    }
});

// Función global para cambiar el idioma
window.changeLanguage = function(lang) {
    document.cookie = "lang=" + lang + "; path=/; max-age=31536000";
    // Si la URL contiene un parámetro ?lang=, lo eliminamos para mantener la URL limpia con cookies
    const url = new URL(window.location.href);
    if (url.searchParams.has('lang')) {
        url.searchParams.delete('lang');
        window.location.href = url.pathname + url.search;
    } else {
        window.location.reload();
    }
};

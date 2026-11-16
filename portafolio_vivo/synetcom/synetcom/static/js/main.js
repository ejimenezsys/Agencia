/* =============================================
   SYNETCOM — Main JS (Futuristic Theme)
   ============================================= */

document.addEventListener('DOMContentLoaded', function () {

  /* --- Navbar toggle (mobile) --- */
  const toggle = document.getElementById('navToggle');
  const menu   = document.getElementById('navMenu');
  if (toggle && menu) {
    toggle.addEventListener('click', function () {
      menu.classList.toggle('open');
      toggle.classList.toggle('active');
    });
    // Dropdown toggle on mobile
    document.querySelectorAll('.nav-dropdown > a').forEach(link => {
      link.addEventListener('click', function (e) {
        if (window.innerWidth <= 768) {
          e.preventDefault();
          this.parentElement.classList.toggle('open');
        }
      });
    });
    // Close menu on outside click
    document.addEventListener('click', function (e) {
      if (!menu.contains(e.target) && !toggle.contains(e.target)) {
        menu.classList.remove('open');
        toggle.classList.remove('active');
      }
    });
  }

  /* --- Hamburger animation --- */
  const navToggle = document.getElementById('navToggle');
  if (navToggle) {
    navToggle.addEventListener('click', function () {
      this.classList.toggle('open');
    });
  }

  /* --- Scroll Reveal (IntersectionObserver) --- */
  const revealEls = document.querySelectorAll('.animate-up');
  if ('IntersectionObserver' in window && revealEls.length) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.style.opacity = '1';
          entry.target.style.transform = 'translateY(0)';
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });

    revealEls.forEach(el => {
      el.style.opacity = '0';
      el.style.transform = 'translateY(30px)';
      el.style.transition = 'opacity 0.7s ease, transform 0.7s ease';
      observer.observe(el);
    });
  }

  /* --- Counter animation --- */
  function animateCounter(el, target, duration, suffix) {
    let start = 0;
    const step = target / (duration / 16);
    const timer = setInterval(() => {
      start += step;
      if (start >= target) { start = target; clearInterval(timer); }
      el.textContent = Math.floor(start) + suffix;
    }, 16);
  }

  const counters = document.querySelectorAll('.stat-item .num');
  if (counters.length) {
    const obs = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const el = entry.target;
          const raw = el.textContent.trim();
          const suffix = raw.replace(/[0-9]/g, '');
          const num    = parseInt(raw.replace(/\D/g, ''));
          if (!isNaN(num)) animateCounter(el, num, 1800, suffix);
          obs.unobserve(el);
        }
      });
    }, { threshold: 0.5 });
    counters.forEach(c => obs.observe(c));
  }

  /* --- Navbar sticky style change --- */
  const navbar = document.querySelector('.navbar');
  if (navbar) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 50) {
        navbar.style.background = 'rgba(2,8,18,0.98)';
        navbar.style.boxShadow = '0 4px 30px rgba(0,0,0,0.8), 0 1px 0 rgba(0,212,255,0.2)';
      } else {
        navbar.style.background = 'rgba(2,8,18,0.92)';
        navbar.style.boxShadow = '0 4px 30px rgba(0,0,0,0.5), 0 1px 0 rgba(0,212,255,0.2)';
      }
    });
  }

  /* --- Glitch effect on logo hover --- */
  const logo = document.querySelector('.navbar-logo img');
  if (logo) {
    logo.addEventListener('mouseenter', () => {
      logo.style.filter = 'drop-shadow(0 0 20px rgba(0,212,255,0.8)) hue-rotate(20deg)';
    });
    logo.addEventListener('mouseleave', () => {
      logo.style.filter = 'drop-shadow(0 0 10px rgba(0,212,255,0.5))';
    });
  }

});

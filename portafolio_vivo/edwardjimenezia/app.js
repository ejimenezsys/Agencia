/* ==========================================================================
   1. 3D Z-AXIS TUNNEL & EYE-PORTAL ENGINE WITH HIGH-CONTRAST NEON WARP RAYS
   ========================================================================== */
const EYE_ORIGIN = [0.5297, 0.2464];
const QS_START_Z = -10500;
const XS_END_Z = 760;

const CHAPTER_LEAD = 0.08;
const CHAPTER_WEIGHTS = (() => {
  const raw = Array.from({ length: 7 }, (_, a) => Math.pow(0.92, a));
  const sum = raw.reduce((s, a) => s + a, 0);
  return raw.map(s => s * (1 - CHAPTER_LEAD) / sum);
})();
const CHAPTER_STARTS = CHAPTER_WEIGHTS.reduce((acc, _, idx) => {
  acc.push(idx ? acc[idx - 1] + CHAPTER_WEIGHTS[idx - 1] : CHAPTER_LEAD);
  return acc;
}, []);

function clamp01(n) {
  return n < 0 ? 0 : n > 1 ? 1 : n;
}

function mapRange(val, inArr, outArr) {
  if (val <= inArr[0]) return outArr[0];
  const last = inArr.length - 1;
  if (val >= inArr[last]) return outArr[last];
  for (let i = 1; i <= last; i++) {
    if (val <= inArr[i]) {
      const t = (val - inArr[i - 1]) / (inArr[i] - inArr[i - 1] || 1);
      return outArr[i - 1] + t * (outArr[i] - outArr[i - 1]);
    }
  }
  return outArr[last];
}

function getActiveChapterIndex(qProg) {
  let bestIdx = 0;
  let bestDist = Infinity;
  for (let a = 0; a < 6; a++) {
    const d = Math.abs(qProg - (CHAPTER_STARTS[a] + CHAPTER_WEIGHTS[a] * 0.65));
    if (d < bestDist) {
      bestDist = d;
      bestIdx = a;
    }
  }
  return bestIdx;
}

function scrollToTunnelPhase(normProgress) {
  const track = document.getElementById('cine-track');
  if (!track) return;
  const trackTop = track.getBoundingClientRect().top + window.scrollY;
  const scrollable = Math.max(1, track.offsetHeight - window.innerHeight);
  window.scrollTo({
    top: trackTop + clamp01(normProgress) * scrollable,
    behavior: 'smooth'
  });
}
window.scrollToTunnelPhase = scrollToTunnelPhase;

function scrollToChapter(chapterIdx) {
  const idx = Math.max(0, Math.min(5, chapterIdx));
  const f = CHAPTER_STARTS[idx];
  const h = f + CHAPTER_WEIGHTS[idx] + CHAPTER_WEIGHTS[idx + 1];
  const qTarget = f + (h - f) * 0.48;
  const overallTarget = 0.34 + qTarget * (0.96 - 0.34);
  scrollToTunnelPhase(overallTarget);
}
window.scrollToChapter = scrollToChapter;

function initCineTunnel() {
  const track = document.getElementById('cine-track');
  const sticky = document.getElementById('cine-sticky');
  if (!track || !sticky) return;

  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (prefersReduced) return;

  const globalScrollLine = document.getElementById('global-scroll-line');
  const heroCapas = document.getElementById('hero-capas');
  const heroBokeh = document.getElementById('hero-bokeh');
  const heroPartWrap = document.getElementById('hero-particulas-wrap');
  const heroFigura = document.getElementById('hero-figura');
  const heroFiguraZoom = document.getElementById('hero-figura-zoom');
  const heroReticle = document.getElementById('hero-eye-reticle');
  const heroVelo = document.getElementById('hero-velo');
  const heroTunel = document.getElementById('hero-tunel');
  const heroTitulos = document.getElementById('hero-titulos');
  const heroTitulosBlur = document.getElementById('hero-titulos-blur');
  const heroCredenciales = document.getElementById('hero-credenciales');

  const warpWrap = document.getElementById('cine-particulas-wrap');
  const vueloOrigen = document.getElementById('vuelo-origen');
  const vueloCifras = document.getElementById('vuelo-cifras');
  const counterNodes = vueloCifras ? Array.from(vueloCifras.querySelectorAll('b[data-counter-target]')) : [];
  const ascensoMetodo = document.getElementById('ascenso-metodo');

  const capaEscape = document.getElementById('cine-capa-escape');
  const journeyIntro = document.getElementById('journey-intro');
  const chapterEls = Array.from(document.querySelectorAll('.journey-chapter')).map(el => ({
    root: el,
    copy: el.querySelector('.journey-copy'),
    letter: el.querySelector('.journey-letter'),
    visual: el.querySelector('.journey-visual')
  }));
  const journeySalida = document.getElementById('journey-salida');
  const stepBtns = Array.from(document.querySelectorAll('#journey-step-list .journey-step-btn'));
  const journeyProgBar = document.getElementById('journey-progress-bar');
  const journeyHint = document.getElementById('journey-scroll-hint');

  const cineCromo = document.getElementById('cine-cromo');
  const cineVelVal = document.getElementById('cine-vel-val');
  const cineBarraFill = document.getElementById('cine-barra-fill');

  let isMobile = window.matchMedia('(max-width: 940px)').matches;
  window.matchMedia('(max-width: 940px)').addEventListener('change', e => {
    isMobile = e.matches;
    measureEyeTransform();
  });

  const eyeMetrics = { ox: '52.97%', oy: '24.64%', k: 16.5, dx: 0, dy: 0 };
  function measureEyeTransform() {
    if (!heroFigura || !sticky) return;
    const figW = heroFigura.offsetWidth;
    const figH = heroFigura.offsetHeight;
    const stW = sticky.clientWidth;
    const stH = sticky.clientHeight;
    if (!figW || !figH || !stW || !stH) return;

    const eyeX = heroFigura.offsetLeft + EYE_ORIGIN[0] * figW;
    const eyeY = heroFigura.offsetTop + EYE_ORIGIN[1] * figH;

    eyeMetrics.ox = (EYE_ORIGIN[0] * figW).toFixed(1) + 'px';
    eyeMetrics.oy = (EYE_ORIGIN[1] * figH).toFixed(1) + 'px';
    eyeMetrics.k = isMobile ? 13.5 : 17.5;
    eyeMetrics.dx = stW / 2 - eyeX;
    eyeMetrics.dy = stH / 2 - eyeY;

    if (heroFiguraZoom) {
      heroFiguraZoom.style.transformOrigin = `${eyeMetrics.ox} ${eyeMetrics.oy}`;
    }
  }
  measureEyeTransform();
  const ro = new ResizeObserver(measureEyeTransform);
  if (heroFigura) ro.observe(heroFigura);
  ro.observe(sticky);

  let mouseX = 0;
  let mouseY = 0;
  window.addEventListener('pointermove', e => {
    if (isMobile) return;
    mouseX = (e.clientX / window.innerWidth - 0.5) * 2;
    mouseY = (e.clientY / window.innerHeight - 0.5) * 2;
  }, { passive: true });

  let targetProgress = 0;
  let smoothProgress = 0;
  let velocity = 0;
  let currentActiveChap = -1;
  const warpProgressRef = { current: 0 };

  function computeRawProgress() {
    const rect = track.getBoundingClientRect();
    const scrollable = Math.max(1, track.offsetHeight - window.innerHeight);
    targetProgress = clamp01(-rect.top / scrollable);

    if (globalScrollLine) {
      const docMax = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
      globalScrollLine.style.height = (clamp01(window.scrollY / docMax) * 100).toFixed(1) + '%';
    }
  }
  computeRawProgress();
  window.addEventListener('scroll', computeRawProgress, { passive: true });
  window.addEventListener('resize', computeRawProgress, { passive: true });

  function applyTunnelFrame(O) {
    const K = clamp01(O / 0.34);
    const Zn = 0.055;
    const an = 0.58;

    const bokehScale = mapRange(K, [0, an], [1.04, 1.34]);
    const bokehOp = mapRange(K, [0, Zn, 0.45], [1, 1, 0]);
    const veloOp = mapRange(K, [0, 0.16, 0.38], [1, 1, 0]);
    const tunelOp = mapRange(K, [0.18, 0.42, an + 0.04, an + 0.16], [0, 1, 1, 0]);
    const partOp = mapRange(K, [0, 0.06, 0.26, 0.45], [0.75, 1, 0.85, 0]);

    const zoomLinear = clamp01((K - Zn) / (an - Zn));
    const zoomScale = 1 + (eyeMetrics.k - 1) * Math.pow(zoomLinear, 2.5);
    const zoomDx = eyeMetrics.dx * Math.pow(zoomLinear, 1.55);
    const zoomDy = eyeMetrics.dy * Math.pow(zoomLinear, 1.55);
    const figOp = mapRange(K, [an - 0.08, an + 0.02], [1, 0]);
    const heroCapasOp = mapRange(O, [0.22, 0.26], [1, 0]);

    const parallaxFade = mapRange(K, [0, Zn * 1.4], [1, 0]);
    const px = mouseX * 8 * parallaxFade;
    const py = mouseY * 5 * parallaxFade;

    if (heroCapas) heroCapas.style.opacity = heroCapasOp.toFixed(3);
    if (heroBokeh) {
      heroBokeh.style.opacity = bokehOp.toFixed(3);
      heroBokeh.style.transform = `translate3d(${(mouseX * -14).toFixed(1)}px, ${(mouseY * -9).toFixed(1)}px, 0) scale(${bokehScale.toFixed(3)})`;
    }
    if (heroPartWrap) heroPartWrap.style.opacity = partOp.toFixed(3);
    if (heroVelo) heroVelo.style.opacity = veloOp.toFixed(3);
    if (heroTunel) heroTunel.style.opacity = tunelOp.toFixed(3);

    if (heroFigura) {
      heroFigura.style.opacity = figOp.toFixed(3);
      heroFigura.style.transform = `translate3d(${px.toFixed(1)}px, ${py.toFixed(1)}px, 0)`;
    }
    if (heroFiguraZoom) {
      heroFiguraZoom.style.transform = `translate3d(${zoomDx.toFixed(1)}px, ${zoomDy.toFixed(1)}px, 0) scale(${zoomScale.toFixed(3)})`;
    }
    if (heroReticle) {
      const retOp = mapRange(zoomLinear, [0, 0.08, 0.42, 0.65], [0.85, 1, 0.9, 0]);
      heroReticle.style.opacity = retOp.toFixed(3);
    }

    const titOp = mapRange(K, [0, 0.03, 0.15, 0.25], [1, 1, 1, 0]);
    const titY = mapRange(K, [0, 0.28], [0, -48]);
    const titBlurOp = mapRange(K, [0.16, 0.21, 0.27], [0, 0.55, 0]);
    if (heroTitulos) {
      heroTitulos.style.opacity = titOp.toFixed(3);
      heroTitulos.style.transform = isMobile
        ? `translate3d(0, ${titY.toFixed(1)}px, 0)`
        : `translate3d(0, calc(-50% + ${titY.toFixed(1)}px), 0)`;
      heroTitulos.style.pointerEvents = titOp > 0.25 ? 'auto' : 'none';
    }
    if (heroTitulosBlur) {
      heroTitulosBlur.style.opacity = titBlurOp.toFixed(3);
      heroTitulosBlur.style.transform = isMobile
        ? `translate3d(0, ${titY.toFixed(1)}px, 0)`
        : `translate3d(0, calc(-50% + ${titY.toFixed(1)}px), 0)`;
    }
    if (heroCredenciales) heroCredenciales.style.opacity = titOp.toFixed(3);

    const origenWin = [0.50, 0.56, 0.72, 0.78];
    const cifrasWin = [0.56, 0.62, 0.78, 0.84];
    const metodoWin = [0.83, 0.88, 0.96, 1.0];

    const origenOp = mapRange(K, origenWin, [0, 1, 1, 0]);
    const origenY = mapRange(K, [origenWin[0], origenWin[3]], [26, -26]);
    if (vueloOrigen) {
      vueloOrigen.style.opacity = origenOp.toFixed(3);
      vueloOrigen.style.transform = `translate3d(0, ${origenY.toFixed(1)}px, 0)`;
    }

    const cifrasOp = mapRange(K, cifrasWin, [0, 1, 1, 0]);
    const cifrasY = mapRange(K, [cifrasWin[0], cifrasWin[3]], [28, -28]);
    if (vueloCifras) {
      vueloCifras.style.opacity = cifrasOp.toFixed(3);
      vueloCifras.style.transform = `translate3d(0, ${cifrasY.toFixed(1)}px, 0)`;
    }

    if (cifrasOp > 0.01 && counterNodes.length) {
      const cProg = clamp01((K - cifrasWin[0]) / (cifrasWin[2] - cifrasWin[0]));
      const eased = 1 - Math.pow(1 - cProg, 2.4);
      counterNodes.forEach(node => {
        const target = parseInt(node.getAttribute('data-counter-target') || '0', 10);
        const prefix = node.getAttribute('data-prefix') || '';
        const suffix = node.getAttribute('data-suffix') || '';
        node.textContent = prefix + Math.round(target * eased) + suffix;
      });
    }

    const metodoOp = mapRange(K, metodoWin, [0, 1, 1, 0]);
    const metodoY = mapRange(K, [metodoWin[0], metodoWin[3]], [30, -30]);
    if (ascensoMetodo) {
      ascensoMetodo.style.opacity = metodoOp.toFixed(3);
      ascensoMetodo.style.transform = `translate3d(0, ${metodoY.toFixed(1)}px, 0)`;
    }

    // Phase 3: 6-Chapter 3D Z-Axis Tunnel + Refined Warp Rays
    const q = clamp01((O - 0.34) / (0.96 - 0.34));
    warpProgressRef.current = clamp01(O / 0.96);

    // Subtle warp rays on Hero (0.18) scaling smoothly to 0.72 inside the tunnel
    const warpOp = mapRange(O, [0.0, 0.10, 0.22, 0.94, 0.995], [0.18, 0.45, 0.72, 0.72, 0]);
    if (warpWrap) warpWrap.style.opacity = warpOp.toFixed(3);

    const escapeLayerOp = mapRange(O, [0.325, 0.345, 0.965, 0.992], [0, 1, 1, 0]);
    if (capaEscape) {
      capaEscape.style.opacity = escapeLayerOp.toFixed(3);
      capaEscape.style.pointerEvents = escapeLayerOp > 0.2 ? 'auto' : 'none';
    }

    const introOp = mapRange(q, [0.0, 0.06, 0.12], [1, 1, 0]);
    if (journeyIntro) journeyIntro.style.opacity = introOp.toFixed(3);

    chapterEls.forEach((ch, r) => {
      const f = CHAPTER_STARTS[r];
      const h = f + CHAPTER_WEIGHTS[r] + CHAPTER_WEIGHTS[r + 1];
      const m = QS_START_Z - r * 1200;
      const y = XS_END_Z + r * 220;
      const v = clamp01((q - f) / (h - f));

      const zPos = mapRange(v, [0, 0.17, 0.30, 0.37, 0.62, 0.70, 0.84, 1], [m, m * 0.52, -1500, 0, 60, 320, 620, y]);
      const op = mapRange(v, [0, 0.12, 0.20, 0.34, 0.64, 0.76, 0.86], [0, 0, 0.34, 1, 1, 0.3, 0]);
      const blurVal = mapRange(v, [0, 0.30, 0.37, 0.62, 0.72, 1], [10, 4, 0, 0, 5.5, 12]);
      const splitL = clamp01((v - 0.62) / (1 - 0.62));

      ch.root.style.opacity = op.toFixed(3);
      if (op <= 0.005) {
        ch.root.style.visibility = 'hidden';
        return;
      }
      ch.root.style.visibility = 'visible';
      ch.root.style.transform = `translate3d(0px, 0px, ${zPos.toFixed(1)}px)`;

      const copyX = isMobile ? '0vw' : (-splitL * 74).toFixed(2) + 'vw';
      const copyY = isMobile ? (-splitL * 30).toFixed(2) + 'vh' : '0vh';
      const visX = isMobile ? '0vw' : (splitL * 70).toFixed(2) + 'vw';
      const visY = isMobile ? (splitL * 34).toFixed(2) + 'vh' : '0vh';

      const copyBlur = blurVal * 0.6 < 0.1 ? 'none' : `blur(${(blurVal * 0.6).toFixed(2)}px)`;
      const visBlur = blurVal < 0.06 ? 'none' : `blur(${blurVal.toFixed(2)}px)`;

      if (ch.copy) {
        ch.copy.style.transform = `translate3d(${copyX}, ${copyY}, -70px)`;
        ch.copy.style.filter = copyBlur;
      }
      if (ch.visual) {
        ch.visual.style.transform = `translate3d(${visX}, ${visY}, 150px)`;
        ch.visual.style.filter = visBlur;
      }
      if (ch.letter) {
        const clipPct = mapRange(v, [0.18, 0.40], [100, 0]);
        ch.letter.style.clipPath = `inset(0 0 0 ${clipPct.toFixed(1)}%)`;
      }
    });

    const salidaOp = mapRange(q, [0.92, 0.96], [0, 1]);
    const salidaY = mapRange(q, [0.92, 0.98], [26, 0]);
    if (journeySalida) {
      journeySalida.style.opacity = salidaOp.toFixed(3);
      journeySalida.style.transform = `translate3d(0, calc(-50% + ${salidaY.toFixed(1)}px), 0)`;
      journeySalida.style.pointerEvents = salidaOp > 0.4 ? 'auto' : 'none';
    }

    const activeChap = getActiveChapterIndex(q);
    if (activeChap !== currentActiveChap) {
      currentActiveChap = activeChap;
      stepBtns.forEach((btn, idx) => {
        btn.classList.toggle('is-active', idx === activeChap);
      });
    }
    if (journeyProgBar) {
      journeyProgBar.style.width = (q * 100).toFixed(1) + '%';
    }
    if (journeyHint) {
      journeyHint.style.opacity = mapRange(q, [0.08, 0.20], [1, 0]).toFixed(2);
    }

    const cromoOp = mapRange(O, [0.005, 0.025, 0.965, 0.998], [0, 1, 1, 0]);
    if (cineCromo) cineCromo.style.opacity = cromoOp.toFixed(3);
    if (cineBarraFill) cineBarraFill.style.transform = `scaleX(${O.toFixed(4)})`;
    if (cineVelVal) {
      const velNum = 1 + clamp01(O / 0.94) * 9.0;
      cineVelVal.textContent = velNum.toFixed(1);
    }
  }

  let lastTime = performance.now();
  function tickSpring(now) {
    const dt = Math.min(0.04, (now - lastTime) / 1000);
    lastTime = now;

    const stiffness = 85;
    const damping = 26;
    const mass = 0.25;
    const force = -stiffness * (smoothProgress - targetProgress) - damping * velocity;
    const accel = force / mass;
    velocity += accel * dt;
    smoothProgress += velocity * dt;

    if (Math.abs(targetProgress - smoothProgress) < 0.00005 && Math.abs(velocity) < 0.00005) {
      smoothProgress = targetProgress;
      velocity = 0;
    }

    applyTunnelFrame(clamp01(smoothProgress));
    requestAnimationFrame(tickSpring);
  }
  requestAnimationFrame(tickSpring);

  initHeroParticlesCanvas(isMobile);
  initWarpParticlesCanvas(warpProgressRef, isMobile);
}

/* ---------------- Floating Hero Neural Particles Canvas ---------------- */
function initHeroParticlesCanvas(isMobile) {
  const canvas = document.getElementById('hero-particulas-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  const count = isMobile ? 42 : 76;

  const palettes = ['0, 240, 255', '240, 211, 162', '168, 85, 247'];
  const spawn = () => ({
    x: Math.random(),
    y: Math.random(),
    r: Math.random() * 2.5 + 0.9,
    vx: (Math.random() - 0.5) * 0.014,
    vy: -(Math.random() * 0.018 + 0.005),
    a: Math.random() * 0.55 + 0.35,
    f: Math.random() * Math.PI * 2,
    capa: Math.random() < 0.35 ? 0.65 : 1.15,
    rgb: palettes[Math.floor(Math.random() * palettes.length)]
  });

  const particles = Array.from({ length: count }, spawn);

  function resize() {
    const r = canvas.getBoundingClientRect();
    canvas.width = Math.max(1, Math.round(r.width * dpr));
    canvas.height = Math.max(1, Math.round(r.height * dpr));
  }
  resize();
  new ResizeObserver(resize).observe(canvas);

  let prev = performance.now();
  function draw(now) {
    const dt = Math.min(0.05, (now - prev) / 1000);
    prev = now;
    const W = canvas.width;
    const H = canvas.height;
    ctx.clearRect(0, 0, W, H);
    ctx.globalCompositeOperation = 'lighter';

    for (const p of particles) {
      p.x += p.vx * dt;
      p.y += p.vy * dt;
      p.f += dt * 1.25;
      if (p.y < -0.05) {
        Object.assign(p, spawn(), { y: 1.05 });
      }
      const alpha = p.a * (0.65 + 0.35 * Math.sin(p.f));
      const rad = p.r * dpr * p.capa;
      const gx = p.x * W;
      const gy = p.y * H;
      const grad = ctx.createRadialGradient(gx, gy, 0, gx, gy, rad * 4.5);
      grad.addColorStop(0, `rgba(255, 255, 255, ${(alpha * 0.95).toFixed(3)})`);
      grad.addColorStop(0.28, `rgba(${p.rgb}, ${(alpha * 0.88).toFixed(3)})`);
      grad.addColorStop(1, `rgba(${p.rgb}, 0)`);
      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.arc(gx, gy, rad * 4.5, 0, Math.PI * 2);
      ctx.fill();
    }
    requestAnimationFrame(draw);
  }
  requestAnimationFrame(draw);
}

/* ---------------- Refined Elegant Warp Rays Canvas ---------------- */
function initWarpParticlesCanvas(progressRef, isMobile) {
  const canvas = document.getElementById('cine-warp-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  const count = isMobile ? 38 : 68;

  // Clean Neon Cyan, Royal Gold, and Subtle Violet so rays are visible without cluttering
  const rayColors = [
    { main: '0, 240, 255', tip: '224, 252, 255' },   // Electric Cyan
    { main: '240, 211, 162', tip: '255, 248, 225' }, // Royal Gold
    { main: '56, 189, 248', tip: '224, 242, 254' },  // Sky Laser Blue
    { main: '192, 132, 252', tip: '243, 232, 255' }  // Neon Violet
  ];

  const spawn = () => {
    const R = Math.random();
    const colorObj = rayColors[Math.floor(Math.random() * rayColors.length)];
    return {
      a: Math.random() * Math.PI * 2,
      r: Math.random() * 0.25 + 0.04,
      v: 0.32 + R * 1.15,
      b: 0.48 + R * 0.38,
      capa: 0.35 + R * 0.65,
      color: colorObj
    };
  };

  const streaks = Array.from({ length: count }, spawn);

  function resize() {
    const r = canvas.getBoundingClientRect();
    canvas.width = Math.max(1, Math.round(r.width * dpr));
    canvas.height = Math.max(1, Math.round(r.height * dpr));
  }
  resize();
  new ResizeObserver(resize).observe(canvas);

  let prev = performance.now();
  function draw(now) {
    const dt = Math.min(0.05, (now - prev) / 1000);
    prev = now;
    const V = clamp01(progressRef.current);
    const P = 0.10 + V * 0.32;
    const A = clamp01((V - 0.75) / 0.25);

    const W = canvas.width;
    const H = canvas.height;
    const cx = W / 2;
    const cy = H * 0.5;
    const maxR = Math.hypot(W, H) / 2;

    ctx.clearRect(0, 0, W, H);
    ctx.globalCompositeOperation = 'lighter';
    ctx.lineCap = 'round';

    for (const s of streaks) {
      s.r += dt * P * s.v * (1 + A * 2.4);
      if (s.r > 1.22) {
        Object.assign(s, spawn());
      }
      // Sleek, balanced ray tails
      const tailLen = (0.016 + V * 0.045 + A * 0.08) * (0.45 + s.capa);
      const r0 = Math.max(0, s.r - tailLen);
      const x0 = cx + Math.cos(s.a) * r0 * maxR;
      const y0 = cy + Math.sin(s.a) * r0 * maxR;
      const x1 = cx + Math.cos(s.a) * s.r * maxR;
      const y1 = cy + Math.sin(s.a) * s.r * maxR;

      const fade = Math.min(1, s.r * 3.4) * (1 - clamp01((s.r - 0.94) / 0.28));
      const alpha = Math.min(0.82, fade * s.b * (0.58 + V * 0.24));

      // Draw fine neon gradient trail
      const lineGrad = ctx.createLinearGradient(x0, y0, x1, y1);
      lineGrad.addColorStop(0, `rgba(${s.color.main}, 0)`);
      lineGrad.addColorStop(0.65, `rgba(${s.color.main}, ${(alpha * 0.65).toFixed(3)})`);
      lineGrad.addColorStop(1, `rgba(${s.color.tip}, ${alpha.toFixed(3)})`);

      ctx.strokeStyle = lineGrad;
      ctx.lineWidth = (0.75 + s.capa * 1.15 + A * 0.5) * dpr;
      ctx.beginPath();
      ctx.moveTo(x0, y0);
      ctx.lineTo(x1, y1);
      ctx.stroke();

      // Subtle pinpoint head at (x1, y1)
      ctx.fillStyle = `rgba(${s.color.tip}, ${(alpha * 0.85).toFixed(3)})`;
      ctx.beginPath();
      ctx.arc(x1, y1, (0.65 + s.capa * 0.65) * dpr, 0, Math.PI * 2);
      ctx.fill();
    }
    requestAnimationFrame(draw);
  }
  requestAnimationFrame(draw);
}

document.addEventListener('DOMContentLoaded', () => {
  initCineTunnel();
});

// 2. Interactive PassportAI Semantic Router + Executive Prompt Lab
const missions = {
  closer: {
    model: 'Claude 4.6 Sonnet + Semantic Router',
    savings: '-72% Costo Operativo ($200 → $29/mes)',
    security: 'Prompt Firewall Activo · Cero Fuga de Datos',
    title: 'Misión: Cerrar Ventas High-Ticket y Agendar Citas en Automático',
    why: 'Para ventas consultivas en español e inglés, combinamos empatía conversacional con manejo estricto de objeciones. Este prompt transforma tu IA en un Closer Senior que filtra curiosos y solo agenda prospectos calificados.',
    prompt: `Actúa como un Closer Senior de Ventas Consultivas B2B entrenado bajo la metodología de Agencia Prosper IA.
Tu objetivo es atender en menos de 15 segundos a cada prospecto que llega por WhatsApp o Web, diagnosticar su dolor principal y agendar una sesión estratégica solo si cumple calificación.

REGLAS DE EJECUCIÓN:
1. Nunca hagas más de UNA pregunta por mensaje. Mantén mensajes cortos (máximo 3 líneas).
2. Aplica la secuencia de 4 pasos: (a) Apertura empática contextual, (b) Diagnóstico de volumen actual y cuello de botella, (c) Cuantificación del costo de no resolverlo hoy, (d) Cierre directo a calendario con 2 opciones de horario.
3. Si el prospecto pregunta precio antes del diagnóstico, responde con valor y devuelve una pregunta de calificación para personalizar la propuesta.

Mi negocio vende: [INSERTA TU SERVICIO/PRODUCTO]
Ticket promedio: [INSERTA PRECIO USD]
Objeción más común: [INSERTA OBJECIÓN]
Genera ahora el flujo exacto de 5 mensajes y las respuestas a las 3 objeciones principales.`
  },
  finanzas: {
    model: 'GPT-5.4 Reasoning + DeepSeek R1 Audit',
    savings: '-68% Tiempo de Análisis Financiero',
    security: 'Anonimización Automática de Estados Financieros',
    title: 'Misión: Auditoría de Margen Real y Fugas de Caja (1.ª Inteligencia)',
    why: 'Facturar no es ganar. Este modelo de razonamiento profundo analiza tus costos ocultos, detecta productos "vampiro" que drenan tu tiempo y rediseña tu estructura de precios para multiplicar utilidad neta.',
    prompt: `Actúa como un CFO Estratégico experto en el Pilar 1 (Inteligencia Financiera: "¿Qué vale?") del libro Las 4 Inteligencias de Edward Jiménez.
Analiza los siguientes datos de mi negocio y realiza un diagnóstico implacable de rentabilidad:

1. Calcula el margen de contribución real por línea de producto/servicio descontando horas operativas del dueño.
2. Identifica las 3 fugas silenciosas de flujo de caja (suscripciones redundantes, clientes de bajo margen que consumen el 80% del soporte, demora en cobranza).
3. Propón una escalera de valor con una oferta High-Ticket o recurrente que eleve el LTV/CAC por encima de 5x en los próximos 60 días.

Ingresos mensuales actuales: [INSERTA MONTO USD]
Costos fijos y variables: [INSERTA COSTOS]
Productos/Servicios actuales: [LISTA TUS OFERTAS]`
  },
  estrategia: {
    model: 'Gemini 3.1 Pro + Claude 4.6 Sonnet',
    savings: '+15 Horas Directivas Libres por Semana',
    security: 'Bóveda Estratégica Privada en PassportAI',
    title: 'Misión: Plan SVE90 para Salir de la Trampa del «Dueño-Pulpo»',
    why: 'El Sistema de Visión y Ejecución a 90 Días (SVE90) convierte objetivos dispersos en 3 rocas trimestrales medibles, definiendo qué tareas debes eliminar, cuáles delegar a tu equipo y cuáles automatizar con IA.',
    prompt: `Actúa como un Consultor Ejecutivo certificado en el método SVE90 (Sistema de Visión y Ejecución a 90 Días) del libro Las 4 Inteligencias de Edward Jiménez.
Hoy me siento atrapado como "Dueño-Pulpo" operando incendios diarios.

Diseña mi hoja de ruta de 90 días dividida en:
1. MATRIZ DE LIBERACIÓN DIRECTIVA: Clasifica mis actividades actuales en (a) Automatizar con Empleados Digitales IA esta semana, (b) Delegar con SOPs, (c) Eliminar de inmediato, (d) Conservar como Arquitecto (solo alto valor).
2. LAS 3 ROCAS DEL TRIMESTRE: Define 3 objetivos medibles con KPI semanal para duplicar margen sin aumentar mis horas de trabajo.
3. RITUAL DE GOBERNANZA SEMANAL: Estructura de revisión de 30 minutos cada lunes.

Mi rol actual y tareas que más tiempo me quitan: [DESCRIBE TU DÍA A DÍA]
Meta principal a 90 días: [INSERTA TU META]`
  },
  contenido: {
    model: 'Claude 4.6 Sonnet + Grok Trend Radar',
    savings: '10 Guiones Virales en 4 Minutos',
    security: 'Voz de Marca Personalizada',
    title: 'Misión: Ingeniería de Guiones Virales 9:16 para Reels y TikTok',
    why: 'Combina detección de tendencias en tiempo real con la estructura de retención de 7 beats que llevó a @edwardjimenezia a superar +109,000 reproducciones orgánicas por Reel y +643,000 en Facebook.',
    prompt: `Actúa como el Director de Contenido Viral de @edwardjimenezia.
Necesito 5 guiones verticales (formato 9:16 de 45 segundos) diseñados para retener la atención de dueños de negocio y ejecutivos y convertirlos en prospectos calificados por DM.

Para cada guion entrega:
1. GANCHO VISUAL Y VERBAL (0–3 seg): Una afirmación contraintuitiva o dolor directo que detenga el scroll.
2. AGITACIÓN DEL PROBLEMA (3–12 seg): El error silencioso que les está costando dinero o tiempo hoy.
3. REVELACIÓN DEL SISTEMA (12–35 seg): Explicación clara en 3 pasos accionables.
4. LLAMADO A LA ACCIÓN DE PALABRA CLAVE (35–45 seg): Invitación a comentar una palabra clave para recibir el recurso por automatización en DM.

Mi nicho o especialidad: [INSERTA TU INDUSTRIA]
Recurso gratuito o imán de leads: [INSERTA TU RECURSO]`
  },
  codigo: {
    model: 'Claude 4.6 Sonnet + GPT-5.4 Codex',
    savings: 'Despliegue 5x más Rápido sin Deuda Técnica',
    security: 'Auditoría OWASP & Sandbox Seguro',
    title: 'Misión: Arquitectura de Agentes de Voz, WhatsApp y CRM',
    why: 'Diseña la arquitectura técnica completa (webhooks, estados de conversación, manejo de errores y conexión a calendario/CRM) lista para poner en producción un Empleado Digital 24/7.',
    prompt: `Actúa como el Arquitecto Principal de Soluciones IA de Agencia Prosper IA.
Diseña la especificación técnica lista para producción de un Empleado Digital omnicanal (WhatsApp + Web + Voz) conectado a CRM y Calendario.

Incluye en tu respuesta:
1. Diagrama de flujo de estados de la conversación (Nuevo Lead -> Calificación -> Manejo de Objeciones -> Reserva de Cita -> Recordatorios WhatsApp).
2. Estructura del payload JSON para el webhook hacia el CRM y validación de disponibilidad de calendario.
3. Guardrails de seguridad (Prompt Firewall) para impedir alucinaciones de precios o descuentos no autorizados.

Stack actual o CRM de mi empresa: [EJ: GHL / HubSpot / Custom Python FastAPI]`
  }
};

const routerTabs = document.querySelectorAll('.router-tab');
const routerModelName = document.getElementById('routerModelName');
const routerSavings = document.getElementById('routerSavings');
const routerSecurity = document.getElementById('routerSecurity');
const routerTitle = document.getElementById('routerTitle');
const routerWhy = document.getElementById('routerWhy');
const routerPromptText = document.getElementById('routerPromptText');
const copyPromptBtn = document.getElementById('copyPromptBtn');

routerTabs.forEach((tab) => {
  tab.addEventListener('click', () => {
    routerTabs.forEach((t) => t.classList.remove('active'));
    tab.classList.add('active');
    const key = tab.getAttribute('data-mission');
    const data = missions[key];
    if (!data) return;
    routerModelName.textContent = data.model;
    routerSavings.textContent = data.savings;
    routerSecurity.textContent = data.security;
    routerTitle.textContent = data.title;
    routerWhy.textContent = data.why;
    routerPromptText.textContent = data.prompt;
    if (copyPromptBtn) copyPromptBtn.textContent = '📋 Copiar Prompt Maestro';
  });
});

if (copyPromptBtn && routerPromptText) {
  copyPromptBtn.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(routerPromptText.textContent);
      copyPromptBtn.textContent = '✅ ¡Prompt Copiado!';
      setTimeout(() => {
        copyPromptBtn.textContent = '📋 Copiar Prompt Maestro';
      }, 2200);
    } catch {
      copyPromptBtn.textContent = 'Selecciona y copia (Cmd+C)';
    }
  });
}

// 3. Interactive Digital Employees ROI Calculator
const roiLeads = document.getElementById('roiLeads');
const roiTicket = document.getElementById('roiTicket');
const roiDelay = document.getElementById('roiDelay');

const updateRoiCalculator = () => {
  if (!roiLeads || !roiTicket || !roiDelay) return;
  const leads = Number(roiLeads.value);
  const ticket = Number(roiTicket.value);
  const delay = Number(roiDelay.value);

  document.getElementById('roiLeadsLabel').textContent = `${leads.toLocaleString('es-US')} leads / mes`;
  document.getElementById('roiTicketLabel').textContent = `$${ticket.toLocaleString('es-US')} USD`;
  document.getElementById('roiDelayLabel').textContent = `${delay} minutos`;

  const delayFactor = Math.min(0.09, 0.02 + (delay / 240) * 0.07);
  const extraDeals = Math.max(1, Math.round(leads * delayFactor));
  const recoveredMoney = extraDeals * ticket;
  const hoursSaved = Math.round((leads * 15) / 60);

  document.getElementById('roiMoneyOutput').textContent = `+$${recoveredMoney.toLocaleString('es-US')} USD`;
  document.getElementById('roiHoursSaved').textContent = `${hoursSaved} hrs / mes`;
};

[roiLeads, roiTicket, roiDelay].forEach((el) => {
  if (el) el.addEventListener('input', updateRoiCalculator);
});

// 4. Interactive 4 Intelligences Validator
const sliders = ['valFin', 'valEmo', 'valEst', 'valIa'];
const updateValidator = () => {
  const vals = sliders.map((id) => {
    const el = document.getElementById(id);
    const v = Number(el.value);
    document.getElementById(id + 'Label').textContent = `${v} / 25`;
    return v;
  });
  const total = vals.reduce((a, b) => a + b, 0);
  const circle = document.getElementById('totalScoreCircle');
  const verdict = document.getElementById('scoreVerdict');
  const desc = document.getElementById('scoreDesc');

  circle.textContent = String(total);
  if (total >= 80) {
    circle.style.borderColor = '#34d399';
    verdict.textContent = 'PROYECTO DE ALTO APALANCAMIENTO (80–100)';
    desc.textContent = 'Luz verde ejecutiva: combina retorno financiero, paz directiva, foco de 90 días y alta delegación en empleados digitales.';
  } else if (total >= 60) {
    circle.style.borderColor = '#d2ae77';
    verdict.textContent = 'OPORTUNIDAD VIABLE CON AJUSTES (60–79)';
    desc.textContent = 'Refuerza la inteligencia más baja o delega la carga operativa con sistemas de IA antes de escalar.';
  } else {
    circle.style.borderColor = '#f87171';
    verdict.textContent = 'ALERTA: TRAMPA DE DUEÑO-PULPO (< 60)';
    desc.textContent = 'Alto riesgo de desgaste personal o bajo margen. Rediseña el modelo antes de invertir tu tiempo.';
  }
};
sliders.forEach((id) => {
  const el = document.getElementById(id);
  if (el) el.addEventListener('input', updateValidator);
});

// 5. Excerpt Dialog with mandatory light-dismiss fallback (per modern-web-guidance `light-dismiss-a-dialog`)
const excerptDialog = document.getElementById('excerptDialog');
const openExcerptBtn = document.getElementById('openExcerptBtn');
if (openExcerptBtn && excerptDialog) {
  openExcerptBtn.addEventListener('click', () => {
    excerptDialog.showModal();
  });
}

if (excerptDialog && !('closedBy' in HTMLDialogElement.prototype)) {
  excerptDialog.addEventListener('click', (event) => {
    if (event.target !== excerptDialog) return;
    const rect = excerptDialog.getBoundingClientRect();
    const isDialogContent = (
      rect.top <= event.clientY &&
      event.clientY <= rect.top + rect.height &&
      rect.left <= event.clientX &&
      event.clientX <= rect.left + rect.width
    );
    if (isDialogContent) return;
    excerptDialog.close();
  });
}

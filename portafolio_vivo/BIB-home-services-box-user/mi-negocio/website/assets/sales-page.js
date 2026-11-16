/* ============================================================
   Página de venta · "El día amanece ordenado"
   Un solo archivo, sin librerías. Todo honra prefers-reduced-motion,
   usa IntersectionObserver (no listeners de scroll pesados) y solo
   anima transform/opacity. Familia de la squeeze. Esta mecánica es
   AGNÓSTICA de oficio: no se edita al vestir la página de otra marca.
   ============================================================ */
(function () {
  var rm = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var smallScreen = window.matchMedia('(max-width: 760px)').matches;

  /* ---------- Nav: menú móvil + fondo sólido al bajar ---------- */
  var nav = document.getElementById('nav');
  var burger = document.getElementById('burger');
  var links = document.getElementById('navlinks');
  var scrim = document.getElementById('navscrim');
  if (burger && links) {
    function setMenu(open) {
      links.classList.toggle('open', open);
      burger.classList.toggle('open', open);
      if (scrim) scrim.classList.toggle('open', open);
      document.body.classList.toggle('menu-open', open);
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
      burger.setAttribute('aria-label', open ? 'Cerrar menú' : 'Abrir menú');
    }
    burger.addEventListener('click', function () { setMenu(!links.classList.contains('open')); });
    if (scrim) scrim.addEventListener('click', function () { setMenu(false); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') setMenu(false); });
    links.querySelectorAll('a').forEach(function (a) { a.addEventListener('click', function () { setMenu(false); }); });
  }

  /* ---------- Envolver en palabras un elemento (titular y statement) ---------- */
  function wrapWords(node, cls, counter) {
    var kids = Array.prototype.slice.call(node.childNodes);
    kids.forEach(function (n) {
      if (n.nodeType === 3) {
        var frag = document.createDocumentFragment();
        n.textContent.split(/(\s+)/).forEach(function (part) {
          if (!part) return;
          if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(' ')); return; }
          var w = document.createElement('span'); w.className = cls;
          if (counter) w.style.setProperty('--i', counter.i++);
          w.textContent = part;
          frag.appendChild(w);
        });
        node.replaceChild(frag, n);
      } else if (n.nodeType === 1 && !n.classList.contains('rem')) {
        wrapWords(n, cls, counter);
      }
    });
  }

  /* ---------- Titular del héroe: palabras que suben una a una ---------- */
  var h1 = document.getElementById('titular');
  if (h1 && !rm) {
    // envolver por líneas para que el overflow:hidden recorte bien
    var counter = { i: 0 };
    (function lines(node) {
      var kids = Array.prototype.slice.call(node.childNodes);
      kids.forEach(function (n) {
        if (n.nodeType === 3) {
          var frag = document.createDocumentFragment();
          n.textContent.split(/(\s+)/).forEach(function (part) {
            if (!part) return;
            if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(' ')); return; }
            var line = document.createElement('span'); line.className = 'line'; line.style.display = 'inline-block';
            var w = document.createElement('span'); w.className = 'w'; w.style.setProperty('--i', counter.i++); w.textContent = part;
            line.appendChild(w); frag.appendChild(line);
          });
          node.replaceChild(frag, n);
        } else if (n.nodeType === 1) { lines(n); }
      });
    })(h1);
  }
  requestAnimationFrame(function () { requestAnimationFrame(function () { document.body.classList.add('ready'); }); });

  /* ---------- Revelados al entrar (secciones, tarjetas, cine, cita, por-fin) ---------- */
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { threshold: 0.14, rootMargin: '0px 0px -6% 0px' });
    document.querySelectorAll('[data-r],[data-rs]').forEach(function (el) { io.observe(el); });
  } else {
    document.querySelectorAll('[data-r],[data-rs]').forEach(function (el) { el.classList.add('in'); });
  }

  /* ---------- Luz que amanece ligada al scroll (--dawn global) ---------- */
  var ticking = false;
  function scrollTick() {
    var doc = document.documentElement;
    var max = doc.scrollHeight - window.innerHeight;
    var p = max > 0 ? Math.min(1, Math.max(0, window.scrollY / max)) : 0;
    doc.style.setProperty('--dawn', p.toFixed(3));
    if (nav) nav.classList.toggle('solid', window.scrollY > 40);
    porfinScrub();
    rioTick();
    ticking = false;
  }
  window.addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(scrollTick); } }, { passive: true });

  /* ---------- POR FIN: el texto se enciende con el scroll ---------- */
  var stmt = document.getElementById('stmt');
  var stmtWords = [];
  if (stmt) {
    var rem = stmt.querySelector('.rem');
    wrapWords(stmt, 'w', null);
    stmtWords = Array.prototype.slice.call(stmt.querySelectorAll('.w'));
    if (rm) { stmtWords.forEach(function (w) { w.classList.add('lit'); }); if (rem) rem.classList.add('lit'); }
  }
  function porfinScrub() {
    if (!stmt || rm || !stmtWords.length) return;
    var r = stmt.getBoundingClientRect();
    var vh = window.innerHeight;
    // progreso: 0 cuando el bloque entra por abajo, 1 cuando su medio pasa el centro-alto
    var prog = (vh * 0.85 - r.top) / (vh * 0.5 + r.height * 0.5);
    prog = Math.min(1, Math.max(0, prog));
    var lit = Math.round(prog * stmtWords.length);
    stmtWords.forEach(function (w, i) { w.classList.toggle('lit', i < lit); });
    var rem2 = stmt.querySelector('.rem');
    if (rem2) rem2.classList.toggle('lit', prog > 0.92);
  }

  /* ---------- Portal: inclinación 3D suave siguiendo el cursor ---------- */
  var mock = document.getElementById('portalmock');
  if (mock && !rm && !smallScreen) {
    mock.addEventListener('mousemove', function (e) {
      var r = mock.getBoundingClientRect();
      var dx = (e.clientX - r.left) / r.width - 0.5;
      var dy = (e.clientY - r.top) / r.height - 0.5;
      mock.style.setProperty('--ry', (dx * 6).toFixed(2) + 'deg');
      mock.style.setProperty('--rx', (-dy * 5).toFixed(2) + 'deg');
    });
    mock.addEventListener('mouseleave', function () { mock.style.setProperty('--ry', '0deg'); mock.style.setProperty('--rx', '0deg'); });
  }

  /* ---------- Tarjetas del vivero: linterna que sigue el cursor ---------- */
  if (!rm && !smallScreen) {
    document.querySelectorAll('.tool').forEach(function (t) {
      t.addEventListener('mousemove', function (e) {
        var r = t.getBoundingClientRect();
        t.style.setProperty('--mx', ((e.clientX - r.left) / r.width * 100).toFixed(1) + '%');
        t.style.setProperty('--my', ((e.clientY - r.top) / r.height * 100).toFixed(1) + '%');
      });
    });
  }

  /* ---------- ⭐ EL RÍO: los prospectos viajan con el scroll ---------- */
  var rio = document.getElementById('rio');
  var riopath = document.getElementById('riopath');
  var riodots = document.getElementById('riodots');
  var estaciones = rio ? rio.querySelectorAll('.rio-est') : [];
  var nodos = rio ? rio.querySelectorAll('.rio-nodo') : [];
  var COLORS = ['var(--primary-soft)', 'var(--lime)', 'var(--amber)', 'var(--accent-soft)'];
  var SEG = [0.20, 0.50, 0.78];         // fronteras de color a lo largo del cauce
  var ESTFRAC = [0.06, 0.40, 0.68, 0.96]; // dónde se "prende" cada estación
  var dots = [];
  if (rio && riopath && riodots) {
    var L = riopath.getTotalLength();
    var N = 16;
    for (var i = 0; i < N; i++) {
      var c = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      c.setAttribute('r', (i % 3 === 0 ? 3.4 : 2.6).toString());
      riodots.appendChild(c);
      // embudo honesto: muchos arriba, pocos abajo (unos se apagan antes de llegar)
      var maxFrac = i % 5 === 0 ? 0.52 : (i % 3 === 0 ? 0.80 : 1.0);
      dots.push({ el: c, offset: i / N, maxFrac: maxFrac });
    }
  }
  function segColor(f) {
    if (f < SEG[0]) return COLORS[0];
    if (f < SEG[1]) return COLORS[1];
    if (f < SEG[2]) return COLORS[2];
    return COLORS[3];
  }
  function placeDot(d, frac) {
    var pt = riopath.getPointAtLength(frac * L);
    d.el.setAttribute('cx', pt.x.toFixed(1));
    d.el.setAttribute('cy', pt.y.toFixed(1));
    d.el.setAttribute('fill', segColor(frac));
    var fade = 1;
    if (frac < 0.04) fade = frac / 0.04;
    else if (frac > 0.96) fade = (1 - frac) / 0.04;
    if (frac > d.maxFrac) fade = 0;
    d.el.setAttribute('opacity', Math.max(0, fade).toFixed(2));
  }
  function lightStations(p) {
    estaciones.forEach(function (est, k) { est.classList.toggle('on', p >= ESTFRAC[k] - 0.05); });
    nodos.forEach(function (n, k) { n.setAttribute('opacity', p >= ESTFRAC[k] - 0.05 ? '1' : '.5'); });
  }
  function rioTick() {
    if (!rio || !dots.length) return;
    if (rm || smallScreen) return; // estático: se resuelve una vez abajo
    var r = rio.getBoundingClientRect();
    var range = r.height - window.innerHeight;
    var p = range > 0 ? Math.min(1, Math.max(0, -r.top / range)) : 0;
    dots.forEach(function (d) {
      var frac = (d.offset + p * 1.1) % 1;
      placeDot(d, frac);
    });
    lightStations(p);
  }
  if (rio && dots.length && (rm || smallScreen)) {
    // versión quieta: puntos repartidos y estaciones encendidas
    rio.style.height = 'auto';
    dots.forEach(function (d) { placeDot(d, d.offset * (d.maxFrac)); });
    estaciones.forEach(function (est) { est.classList.add('on'); });
    nodos.forEach(function (n) { n.setAttribute('opacity', '1'); });
  } else {
    rioTick();
  }

  /* ---------- Antes / después: arrastrar la manija ---------- */
  var ba = document.getElementById('ba');
  var bahandle = document.getElementById('bahandle');
  if (ba && bahandle) {
    var dragging = false;
    function setSplit(clientX) {
      var r = ba.getBoundingClientRect();
      var x = Math.min(r.width, Math.max(0, clientX - r.left));
      ba.style.setProperty('--sx', (x / r.width * 100).toFixed(1) + '%');
    }
    bahandle.addEventListener('pointerdown', function (e) { dragging = true; bahandle.setPointerCapture(e.pointerId); });
    window.addEventListener('pointermove', function (e) { if (dragging) setSplit(e.clientX); });
    window.addEventListener('pointerup', function () { dragging = false; });
    ba.addEventListener('pointerdown', function (e) { if (e.target !== bahandle && !bahandle.contains(e.target)) setSplit(e.clientX); });
  }

  /* ---------- Contador de cifras en los planes (pieza reusada de la squeeze) ---------- */
  function countUp(el) {
    var t = el.childNodes[0]; // primer nodo de texto ("US$39 ")
    if (!t || t.nodeType !== 3) return;
    var txt = t.textContent;
    var m = txt.match(/\d[\d.,]*/);
    if (!m) return;
    var meta = parseInt(m[0].replace(/[.,]/g, ''), 10);
    if (!isFinite(meta) || meta <= 0) return;
    var pre = txt.slice(0, m.index), post = txt.slice(m.index + m[0].length), t0 = null;
    function step(ts) {
      if (!t0) t0 = ts;
      var p = Math.min(1, (ts - t0) / 900); p = 1 - Math.pow(1 - p, 3);
      t.textContent = pre + (p < 1 ? Math.round(meta * p) : m[0]) + post;
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
  if ('IntersectionObserver' in window && !rm) {
    var cio = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { countUp(e.target); cio.unobserve(e.target); } });
    }, { threshold: 0.6 });
    document.querySelectorAll('[data-count]').forEach(function (el) { cio.observe(el); });
  }

  /* ---------- Botón imán + aplauso al clic ---------- */
  document.querySelectorAll('[data-imandata]').forEach(function (btn) {
    if (!rm && !smallScreen) {
      btn.addEventListener('mousemove', function (e) {
        var r = btn.getBoundingClientRect();
        var dx = (e.clientX - r.left - r.width / 2) / r.width;
        var dy = (e.clientY - r.top - r.height / 2) / r.height;
        btn.style.transform = 'translate(' + (dx * 6).toFixed(1) + 'px,' + (dy * 5).toFixed(1) + 'px)';
      });
      btn.addEventListener('mouseleave', function () { btn.style.transform = ''; });
    }
  });
  document.querySelectorAll('.btn').forEach(function (btn) {
    btn.addEventListener('click', function () { btn.classList.remove('clap'); void btn.offsetWidth; btn.classList.add('clap'); });
  });
})();

/**
 * Motor Bilingüe Universal (ES | EN) — Agencia Prosper IA LLC
 * Capa 1: Diccionario ejecutivo B2B / Venture Capital para navegación, footer y páginas clave.
 * Capa 2: Motor de traducción contextual de frases y encabezados para cobertura completa del portal.
 */
(function () {
  'use strict';

  var STORAGE_KEY = 'prosperia_lang';
  var ATTR_MARK = 'data-pia-i18n-bound';

  var DYN_CACHE_KEY = 'prosperia_i18n_dyn_cache_v1';
  var origTextNodes = new WeakMap();
  var appliedEnText = new WeakMap();
  var origBlocks = new WeakMap();
  var origAttrs = new WeakMap();
  var origDocTitle = null;
  var trackedTextNodes = [];
  var trackedBlocks = [];
  var trackedAttrEls = [];
  var inflightDyn = {};
  var currentLang = 'es';
  var observerPaused = false;
  var activeMo = null;

  // Marcas protegidas que no deben alterarse al traducir frases
  var PROTECTED_TERMS = [
    'Agencia Prosper IA LLC',
    'Agencia ProsperIA LLC',
    'Agencia Prosper IA',
    'Agencia ProsperIA',
    'PassportAI.app',
    'PassportAI',
    'ProsperIA CRM',
    'Prosper IA',
    'Las 4 Inteligencias',
    'SVE90',
    'GoHighLevel',
    'FIUBA',
    'Edward Jiménez',
    'Idol Jose Group Corp',
    'IDOL JOSE GROUP CORP',
    'Idol Jose Official',
    'Doral Fashion Week',
    'Doral Business City',
    'EXMA Miami',
    'CNBV',
    'Banco Azteca',
    'Elektra',
    'WhatsApp',
    'Apple App Store',
    'Google Play Store',
    'LCCN 2026970390',
    'edward@agenciaprosperia.com'
  ];

  // Traducciones exactas de alta precisión (texto normalizado -> inglés ejecutivo)
  var DICT_URL = '/static/prosperia_i18n_dict.json';
  try {
    var sc = document.querySelector('script[src*="prosperia_i18n.js"]');
    if (sc && sc.src) {
      var qp = sc.src.split('?v=')[1];
      if (qp) DICT_URL += '?v=' + encodeURIComponent(qp);
    }
  } catch (e) {}
  var dictLoaded = false;
  var dictPromise = null;
  var EXACT_MAP = {};

  function ensureDictLoaded() {
    if (dictLoaded) return Promise.resolve();
    if (dictPromise) return dictPromise;
    dictPromise = fetch(DICT_URL)
      .then(function (r) { return r.ok ? r.json() : {}; })
      .then(function (data) {
        if (data && typeof data === 'object') {
          Object.keys(data).forEach(function (k) {
            var nk = norm(k);
            var nv = data[k];
            if (nk && nv && nk !== nv && !EXACT_MAP[nk]) {
              EXACT_MAP[nk] = nv;
            }
          });
        }
        dictLoaded = true;
      })
      .catch(function () { dictLoaded = true; });
    return dictPromise;
  }
  var PHRASE_RULES = [
    [/Agendar Diagnóstico/gi, 'Book Assessment'],
    [/Agenda tu Diagnóstico/gi, 'Book Your Assessment'],
    [/Diagnóstico Gratuito/gi, 'Free Assessment'],
    [/Solicitar Diagnóstico/gi, 'Request Assessment'],
    [/Solicita tu /gi, 'Request Your '],
    [/Ver Plantillas/gi, 'View Templates'],
    [/Ver Demo/gi, 'View Demo'],
    [/Preguntas Frecuentes/gi, 'Frequently Asked Questions'],
    [/Todos los derechos reservados/gi, 'All rights reserved'],
    [/Política de Privacidad/gi, 'Privacy Policy'],
    [/Términos de Servicio/gi, 'Terms of Service'],
    [/Sitio Web Inteligente/gi, 'Smart AI Website'],
    [/Sitios Web Inteligentes/gi, 'Smart AI Websites'],
    [/Agentes de IA Autónomos 24\/7/gi, '24/7 Autonomous AI Agents'],
    [/Agentes de IA 24\/7/gi, '24/7 AI Agents'],
    [/Agente de IA 24\/7/gi, '24/7 AI Agent'],
    [/Agentes IA/gi, 'AI Agents'],
    [/Inteligencia Artificial/gi, 'Artificial Intelligence'],
    [/Transformación Empresarial/gi, 'Enterprise Transformation'],
    [/Automatización de Procesos/gi, 'Process Automation'],
    [/Automatización/gi, 'Automation'],
    [/Consultoría en IA/gi, 'AI Consulting'],
    [/Consultoría Corporativa/gi, 'Corporate Consulting'],
    [/Base de Conocimiento Privada/gi, 'Private Knowledge Base'],
    [/Cerebro Corporativo Privado/gi, 'Private Corporate AI Brain'],
    [/Sin intervenciones manuales/gi, 'Zero manual intervention'],
    [/pago único anual/gi, 'one-time annual payment'],
    [/pago único/gi, 'one-time payment'],
    [/Estados Unidos y Latinoamérica/gi, 'United States and Latin America'],
    [/EE\.?\s*UU\.?\s*y Latinoamérica/gi, 'USA & Latin America'],
    [/EE\.?\s*UU\.?/gi, 'USA'],
    [/Latinoamérica/gi, 'Latin America'],
    [/\bUSD\s*\/\s*mes\b/gi, 'USD / mo'],
    [/\/\s*mes\b/gi, '/ mo'],
    [/Copiar /gi, 'Copy '],
    [/Descargar /gi, 'Download ']
  ];

  // Hidratar caché dinámica previa si existe
  try {
    var savedDyn = JSON.parse(localStorage.getItem(DYN_CACHE_KEY) || '{}');
    if (savedDyn && typeof savedDyn === 'object') {
      Object.keys(savedDyn).forEach(function (dk) {
        if (dk && savedDyn[dk] && !EXACT_MAP[dk]) EXACT_MAP[dk] = savedDyn[dk];
      });
    }
  } catch (e) {}

  function norm(s) {
    return (s || '').replace(/\s+/g, ' ').trim();
  }

  function restoreProtected(str, tokens) {
    return str.replace(/__PIA_TOK_(\d+)__/g, function (_, idx) {
      return tokens[Number(idx)] || '';
    });
  }

  function lookupExactFlexible(trimmed) {
    var key = norm(trimmed);
    if (EXACT_MAP[key]) return EXACT_MAP[key];

    // Stripping de viñetas/puntuación/flechas en los bordes preservando prefijo y sufijo exactos
    var mEdge = trimmed.match(/^([\s•·→↗←✓✔✕✗▸►★:;\-–—"'«»()\[\]]*)(.+?)([\s•·→↗←✓✔:;'\"«»()\[\]]*)$/);
    if (mEdge && mEdge[2]) {
      var coreKey = norm(mEdge[2]);
      if (EXACT_MAP[coreKey]) {
        return mEdge[1] + EXACT_MAP[coreKey] + mEdge[3];
      }
    }

    // Segmentación por separadores frecuentes (' · ', ' | ', ' — ')
    var seps = [' · ', ' | ', ' — '];
    for (var si = 0; si < seps.length; si++) {
      var sep = seps[si];
      if (key.indexOf(sep) !== -1) {
        var parts = key.split(sep);
        var translatedCount = 0;
        var mappedParts = parts.map(function (pt) {
          var pk = norm(pt);
          if (EXACT_MAP[pk]) {
            translatedCount++;
            return EXACT_MAP[pk];
          }
          return pt;
        });
        if (translatedCount > 0) {
          return mappedParts.join(sep);
        }
      }
    }
    return null;
  }

  function looksSpanish(str) {
    var s = norm(str);
    if (!s || s.length < 3 || !/[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]/.test(s)) return false;
    if (/^[+\d\s.,$%\-–—/:@#()]+$/.test(s)) return false;
    if (/^(https?:\/\/|www\.|[\w.+-]+@[\w.-]+\.\w+)/i.test(s)) return false;
    if (/[áéíóúñÁÉÍÓÚÑ¿¡]/.test(s)) return true;
    return /\b(para|con|los|las|una|unos|unas|que|del|por|como|sobre|entre|todo|todos|todas|nuestro|nuestra|nuestros|nuestras|empresa|empresas|negocio|negocios|cliente|clientes|ventas|sistema|sistemas|agente|agentes|inteligencia|gratis|solicitar|agenda|agendar|sitio|sitios|precio|precios|tiempo|sin|cada|desde|hasta|hacia|citas|pasos|guía|diagnostico)\b/i.test(s);
  }

  function translateTextString(raw) {
    if (!raw || !raw.trim()) return raw;
    var hit = lookupExactFlexible(raw.trim());
    if (hit) {
      return raw.replace(raw.trim(), hit);
    }

    var trimmed = raw.trim();
    var tokens = [];
    var safe = trimmed;
    for (var i = 0; i < PROTECTED_TERMS.length; i++) {
      var term = PROTECTED_TERMS[i];
      if (safe.indexOf(term) !== -1) {
        var placeholder = '__PIA_TOK_' + tokens.length + '__';
        tokens.push(term);
        safe = safe.split(term).join(placeholder);
      }
    }
    var changed = safe;
    for (var r = 0; r < PHRASE_RULES.length; r++) {
      changed = changed.replace(PHRASE_RULES[r][0], PHRASE_RULES[r][1]);
    }
    if (changed !== safe) {
      var finalStr = restoreProtected(changed, tokens);
      var lead = raw.match(/^\s*/)[0];
      var trail = raw.match(/\s*$/)[0];
      return lead + finalStr + trail;
    }
    return null;
  }

  function translateMissingDynamically(unmatchedNodes, unmatchedAttrs) {
    if (currentLang !== 'en') return;
    var textQueue = [];
    var seen = {};
    unmatchedNodes.forEach(function (item) {
      var k = norm(item.base);
      if (k && !seen[k] && !inflightDyn[k] && looksSpanish(k)) {
        seen[k] = true;
        inflightDyn[k] = true;
        textQueue.push(k);
      }
    });
    unmatchedAttrs.forEach(function (item) {
      var k = norm(item.base);
      if (k && !seen[k] && !inflightDyn[k] && looksSpanish(k)) {
        seen[k] = true;
        inflightDyn[k] = true;
        textQueue.push(k);
      }
    });
    if (!textQueue.length) return;

    for (var offset = 0; offset < textQueue.length; offset += 50) {
      (function (chunk) {
        fetch('/api/i18n/translate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ texts: chunk })
        })
          .then(function (r) { return r.ok ? r.json() : null; })
          .then(function (data) {
            if (!data || !data.translations) return;
            var map = data.translations;
            try {
              var dyn = JSON.parse(localStorage.getItem(DYN_CACHE_KEY) || '{}');
              Object.keys(map).forEach(function (srcK) {
                EXACT_MAP[srcK] = map[srcK];
                dyn[srcK] = map[srcK];
              });
              localStorage.setItem(DYN_CACHE_KEY, JSON.stringify(dyn));
            } catch (e) {
              Object.keys(map).forEach(function (srcK) {
                EXACT_MAP[srcK] = map[srcK];
              });
            }
            if (currentLang !== 'en') return;
            observerPaused = true;
            try {
              unmatchedNodes.forEach(function (item) {
                var k = norm(item.base);
                if (map[k]) {
                  var nextVal = item.base.replace(item.base.trim(), map[k]);
                  appliedEnText.set(item.node, nextVal);
                  item.node.nodeValue = nextVal;
                }
              });
              unmatchedAttrs.forEach(function (item) {
                var k = norm(item.base);
                if (map[k]) {
                  item.el.setAttribute(item.attr, map[k]);
                }
              });
            } finally {
              if (activeMo && typeof activeMo.takeRecords === 'function') activeMo.takeRecords();
              observerPaused = false;
            }
          })
          .catch(function () {});
      })(textQueue.slice(offset, offset + 50));
    }
  }

  function applyRichTranslations(lang) {
    // Rich mixed-HTML blocks keyed by element selector / heading relationship
    var pairs = [
      {
        sel: 'header.hero h1',
        en: '<span class="hl-cyan">PassportAI.app:</span> The AI Infrastructure Connecting <span class="hl-gold">24/7 AI Agents + CRM</span> to Scale Latin America &amp; US SMBs'
      },
      {
        sel: 'header.hero .hero-sub',
        en: 'Built over <strong>18 months of R&amp;D alongside engineers from FIUBA (University of Buenos Aires)</strong> and <strong>$130,000+ USD in founder equity</strong> invested by Edward Jiménez. Operating today with <strong>740+ active businesses and users</strong>, uniting Autonomous Chatbots, Multi-Model AI Playground, and direct integration with <strong>ProsperIA CRM</strong> (white-label <strong>GoHighLevel</strong> ecosystem) so AI becomes an essential daily habit.'
      },
      {
        sel: '#sim-title + .sec-lead',
        en: 'An isolated chatbot only outputs generic replies. A system powered by <strong>PassportAI.app + ProsperIA CRM</strong> reads real business context, books the appointment, and updates your sales pipeline in seconds — during work hours or late at night.'
      },
      {
        sel: '#moat-title + .sec-lead',
        en: 'The biggest churn risk in consumer AI apps is novelty fatigue. While standalone prompt apps lose users after week one, we anchor <strong>PassportAI.app</strong> directly onto <strong>ProsperIA CRM</strong> (white-labeled on the global <strong>GoHighLevel</strong> standard), giving businesses a mission-critical reason to log in daily to handle WhatsApp, calls, and revenue.'
      },
      {
        sel: '#arch-title + .sec-lead',
        en: 'For investors and strategic partners: <strong>PassportAI.app</strong> orchestrates <strong>58+ leading AI models</strong> in one proprietary workspace — including flagship engines from <strong>OpenAI, Google Gemini, Anthropic Claude, Runway, and ElevenLabs</strong> alongside specialized proprietary models and orchestration rules safeguarded as <strong>trade secrets</strong> — connected via direct link to <strong>Agencia Prosper IA CRM</strong> to deploy a full vertical CRM in minutes instead of months.'
      },
      {
        sel: '#calc-title + .sec-lead',
        en: 'Adjust your team metrics below to estimate the current monthly cost of repetitive manual work and conservative savings assuming <strong>75% operational automation</strong> powered by PassportAI + ProsperIA CRM.'
      },
      {
        sel: '#vc-title + .sec-lead',
        en: 'Investor-to-investor transparency: founder <strong>Edward Jiménez has already invested $130,000+ USD of personal capital</strong> across 18 months of engineering with <strong>FIUBA (Buenos Aires)</strong> talent. This <strong>$1,000,000 USD Seed Round</strong> is high-conviction venture capital designed to outpace AI obsolescence, launch native mobile apps, and scale systematically across milestones.'
      },
      {
        sel: '#geo-title + p',
        en: '<strong>PassportAI.app</strong> is a multi-tenant Applied AI &amp; 24/7 Digital Workforce SaaS platform founded by <strong>Edward Jiménez</strong> and developed over 18 months with engineers from FIUBA (University of Buenos Aires), backed by <strong>$130,000+ USD</strong> in founder capital and operated out of Doral / Miami, FL by <strong>Agencia Prosper IA LLC</strong>. It orchestrates <strong>58+ leading AI models</strong> (including OpenAI, Google Gemini, Anthropic Claude, Runway &amp; ElevenLabs alongside proprietary trade-secret engines) and links directly with <strong>Agencia Prosper IA CRM</strong> (<strong>ProsperIA CRM</strong> on GoHighLevel), installing funnels, 140+ custom values, calendars, and 10 vertical templates in minutes instead of months — alongside WhatsApp QR/API autonomous chatbots, a 9:16 Reels studio, omnichannel LinkedIn/Email prospecting, and trilingual ES/EN/PT support. Serving <strong>740+ active businesses</strong> and backed by Agencia Prosper IA’s community-building engine, it is raising a <strong>$1,000,000 USD Seed Round</strong> to launch native Apple App Store &amp; Google Play Store apps and scale toward 100,000–1,000,000 users across Latin America starting at $19/mo.'
      },
      {
        sel: '#inversionistas .grid-2 .feature-box:first-child p',
        en: 'Unlike deck-only startups, we combine 18 months of core R&amp;D built with <strong>FIUBA (Buenos Aires)</strong> engineering talent — where <strong>PassportAI.app</strong> shows its highest weekly usage — with our proven capability to build and mobilize business communities across the U.S. and Latin America through <strong>Agencia Prosper IA’s</strong> growth strategies and instant <strong>ProsperIA CRM</strong> onboarding.'
      },
      {
        sel: '#inversionistas .grid-2 .feature-box:last-child p',
        en: 'Our platform story and SVE90 framework are documented in the official book <em>Las 4 Inteligencias</em> (Library of Congress <code>LCCN 2026970390</code>, foreword by Fernando Anzures), alongside <strong>744,000+ organic views</strong> and <strong>19,160+ business followers</strong> driving organic demand.'
      },
      {
        sel: 'section[aria-labelledby="powered-passport-title"] p',
        en: '<strong>In Summary — About Agencia Prosper IA LLC &amp; PassportAI.app:</strong> Headquartered in Doral / Miami, Florida and founded by <strong>Edward Jiménez</strong> (25+ years in mission-critical banking &amp; telecom infrastructure; author of <em>Las 4 Inteligencias</em>, LCCN 2026970390), our firm deploys 24/7 Autonomous AI Agents (WhatsApp QR/API, Voice, Web), Smart Websites, Private RAG Brains, and SVE90 Transformation powered by <strong>PassportAI.app</strong> ($130,000+ USD founder R&amp;D over 18 months with FIUBA engineering and 740+ active businesses) connected to <strong>Agencia Prosper IA CRM</strong> across 10 industry verticals in minutes.'
      },
      {
        sel: '.hero-box h1',
        en: '<span>IDOL JOSE GROUP CORP:</span> 4-Portal Luxury Digital Ecosystem, Magazines, Monthly Runways &amp; 24/7 AI Concierge'
      },
      {
        sel: '.hero-box .hero-lead',
        en: 'End-to-end digital architecture designed and deployed by <strong>Agencia Prosper IA LLC</strong> (Edward Jiménez, Miami / Doral, FL) for the international Haute Couture, Editorial Media &amp; Runway conglomerate spanning Doral, Miami, and New York Fashion Week (NYFW).'
      },
      {
        sel: '#aura-stage-transcript',
        en: '💬 «Hi, I am your <strong>AI Setter</strong> at Agencia Prosper IA. Tap the microphone to ask me out loud about Smart Websites, our 4 Digital Employees, CRM, or Reels.»'
      },
      {
        sel: '.kb-hero-grid > div > p',
        en: 'Explore proven production playbooks for <strong style="color:#fff;">Clinics SVE90 &amp; Beauty Growth</strong>, <strong style="color:#fff;">Professionals &amp; 82 Trades</strong>, and <strong style="color:#fff;">CRM-SaaS Agencies + Faceless Creators</strong>. Preview your smart website live for free, register in the official directory, or activate your system in 1 click via Stripe without waiting for quotes.'
      },
      {
        sel: '#pricing-glance .pia-shell > div:first-child > p',
        en: 'No delays or endless quotes. Choose your billing cycle (<strong style="color:#fff;">Monthly</strong>, <strong style="color:#34d399;">Annual with 2 months free</strong>, or <strong style="color:#fbbf24;">Turnkey One-Time Payment</strong>), preview your business live, and activate today with Stripe.'
      },
      {
        sel: '.kb-agency-bridge > div > p',
        en: 'Instead of relying on fragmented external consultants or slow manual setups, <strong style="color:#fff;">CRM-SaaS (/crm-saas)</strong> + <strong style="color:#34d399;">Agencia Prosper IA CRM</strong> + <strong style="color:#67e8f9;">PassportAI.app</strong> deliver automatically: your preconfigured GoHighLevel subaccount starting at US$97/mo, your 16-template Smart Website, your 5-minute WhatsApp AI Receptionist, and your monthly factory of 9:16 Reels and SEO articles.'
      },
      {
        sel: 'body.hm-page .hm-hero h1',
        en: 'Make Your Company <span class="hm-gold-text">Sell, Serve, and Book Appointments 24/7</span> with Smart AI Websites, WhatsApp AI Agents, and 5-Minute CRM'
      },
      {
        sel: 'body.hm-page .hm-hero .hm-lead',
        en: 'We empower clinics, local professionals, and agencies with <strong>High-Converting Smart Websites</strong>, <strong>4 Digital Employees on WhatsApp &amp; Voice</strong>, and <strong>PassportAI.app™ (+58 leading AI models)</strong> connected to <strong>Agencia Prosper IA CRM</strong> — with <strong>740+ active businesses</strong> operating without being glued to their phone.'
      },
      {
        sel: '#ecosistema-3-verticales .hm-verticals-grid > article:nth-child(1) p',
        en: '24/7 AI WhatsApp Receptionist, anti-no-show medical scheduling, and a <strong>5-minute</strong> setup by uploading your clinic PDF brochure into <strong>Agencia Prosper IA CRM</strong> (141 variables + 9 workflows).'
      },
      {
        sel: '#ecosistema-3-verticales .hm-verticals-grid > article:nth-child(2) p',
        en: 'Smart AI Website + Digital QR Card + 24/7 AI Bot live in <strong>7 to 10 days</strong>. Preview your industry template today and activate from <strong>US$197 (Rescue)</strong> or <strong>US$497 (50/50)</strong>.'
      },
      {
        sel: '#ecosistema-3-verticales .hm-verticals-grid > article:nth-child(3) p',
        en: 'Ready-made CRM subaccounts from <strong>US$97/mo</strong> via Stripe, GoHighLevel master agency account with <strong>3 VIP Bonuses</strong>, 10 verticals deployed in 5 minutes, and a 9:16 Reels studio with <strong>+58 AI models</strong>.'
      },
      {
        sel: '#ecosistema-3-verticales .hm-trademarks-grid > div:nth-child(1) p',
        en: 'Applied AI engineering consultancy (<strong>Agencia Prosper IA LLC</strong>, Miami, FL). Smart AI Websites, 4 Digital Employees, the <strong>SVE90</strong> framework, and verified directory in active US &amp; LATAM commerce.'
      },
      {
        sel: '#ecosistema-3-verticales .hm-trademarks-grid > div:nth-child(2) p',
        en: 'Multi-model SaaS suite (<code>passportai.app</code>) unifying <strong>+58 leading AI models</strong> (OpenAI, Google Gemini, Anthropic Claude, Runway, ElevenLabs + proprietary trade-secret engines) and 5-minute CRM deployment.'
      },
      {
        sel: '#ecosistema-3-verticales .hm-trademarks-grid > div:nth-child(3) p',
        en: 'Official book and strategic framework by <strong>Edward Jiménez</strong> with a foreword by <strong>Fernando Anzures</strong>. Registered <strong>LCCN 2026970390</strong> · <strong>Copyright #1-15304798691</strong> · <strong>ISBN 979-8-9824777-0-5</strong> (EXMA Miami).'
      }
    ];

    var grids = document.querySelectorAll('#inversionistas .grid-4');
    if (grids.length >= 2) {
      var tier2P = grids[0].querySelector('.stage-card:nth-child(2) p');
      if (tier2P) {
        if (!origBlocks.has(tier2P)) { origBlocks.set(tier2P, tier2P.innerHTML); trackedBlocks.push(tier2P); }
        tier2P.innerHTML = lang === 'en'
          ? 'Active core offer on <strong>passportai.app</strong>: pairs PassportAI + ProsperIA CRM Starter (GoHighLevel ecosystem), anchoring daily operational habits for SMBs.'
          : origBlocks.get(tier2P);
      }
      var stage3P = grids[1].querySelector('.stage-card:nth-child(3) p');
      if (stage3P) {
        if (!origBlocks.has(stage3P)) { origBlocks.set(stage3P, stage3P.innerHTML); trackedBlocks.push(stage3P); }
        stage3P.innerHTML = lang === 'en'
          ? '$1M Seed funding accelerates native apps on <strong>Apple App Store</strong> and <strong>Google Play Store</strong>. Sustaining 100,000 active paying users delivers enterprise-grade international cash flow.'
          : origBlocks.get(stage3P);
      }
    }

    pairs.forEach(function (item) {
      var el = document.querySelector(item.sel);
      if (!el) return;
      if (!origBlocks.has(el)) {
        origBlocks.set(el, el.innerHTML);
        trackedBlocks.push(el);
      }
      el.innerHTML = lang === 'en' ? item.en : origBlocks.get(el);
    });
  }

  function walkAndTranslate(lang) {
    observerPaused = true;
    var unmatchedNodes = [];
    var unmatchedAttrs = [];
    try {
      applyRichTranslations(lang);

      // 1. Document title
      if (origDocTitle === null) {
        origDocTitle = document.title || '';
      }
      if (lang === 'en') {
        var titleHit = lookupExactFlexible(origDocTitle) || translateTextString(origDocTitle);
        if (titleHit) document.title = norm(titleHit);
      } else if (origDocTitle) {
        document.title = origDocTitle;
      }

      // 2. DOM Text nodes
      var walker = document.createTreeWalker(
        document.body,
        NodeFilter.SHOW_TEXT,
        {
          acceptNode: function (node) {
            if (!node.parentElement) return NodeFilter.FILTER_REJECT;
            var tag = node.parentElement.tagName;
            if (tag === 'SCRIPT' || tag === 'STYLE' || tag === 'NOSCRIPT' || tag === 'CODE' || tag === 'PRE') {
              return NodeFilter.FILTER_REJECT;
            }
            if (node.parentElement.closest('[data-pia-lang-switcher], [translate="no"]')) {
              return NodeFilter.FILTER_REJECT;
            }
            if (!node.nodeValue || !node.nodeValue.trim()) {
              return NodeFilter.FILTER_REJECT;
            }
            return NodeFilter.FILTER_ACCEPT;
          }
        }
      );

      var nodes = [];
      var cur;
      while ((cur = walker.nextNode())) {
        nodes.push(cur);
      }

      if (lang === 'en') {
        nodes.forEach(function (n) {
          if (!origTextNodes.has(n)) {
            origTextNodes.set(n, n.nodeValue);
            trackedTextNodes.push(n);
          }
          var base = origTextNodes.get(n);
          var translated = translateTextString(base);
          if (translated && translated !== n.nodeValue) {
            appliedEnText.set(n, translated);
            n.nodeValue = translated;
          } else if (!translated && looksSpanish(base)) {
            unmatchedNodes.push({ node: n, base: base });
          }
        });
      } else {
        trackedTextNodes.forEach(function (n) {
          if (origTextNodes.has(n)) {
            n.nodeValue = origTextNodes.get(n);
          }
        });
      }

      // 3. Attributes (placeholder, title, aria-label, submit/button input values)
      var attrEls = document.querySelectorAll('[placeholder], [title], [aria-label], input[type="submit"], input[type="button"]');
      attrEls.forEach(function (el) {
        if (el.closest('[data-pia-lang-switcher], [translate="no"]')) return;
        if (!origAttrs.has(el)) {
          var snap = {};
          ['placeholder', 'title', 'aria-label'].forEach(function (a) {
            if (el.hasAttribute(a)) snap[a] = el.getAttribute(a);
          });
          if (el.tagName === 'INPUT' && (el.type === 'submit' || el.type === 'button') && el.hasAttribute('value')) {
            snap.value = el.getAttribute('value');
          }
          origAttrs.set(el, snap);
          trackedAttrEls.push(el);
        }
        var stored = origAttrs.get(el);
        Object.keys(stored).forEach(function (attrName) {
          var origVal = stored[attrName];
          if (lang === 'en') {
            var tr = translateTextString(origVal);
            if (tr) {
              el.setAttribute(attrName, norm(tr));
            } else if (looksSpanish(origVal)) {
              unmatchedAttrs.push({ el: el, attr: attrName, base: origVal });
            }
          } else {
            el.setAttribute(attrName, origVal);
          }
        });
      });
    } finally {
      if (activeMo && typeof activeMo.takeRecords === 'function') activeMo.takeRecords();
      observerPaused = false;
    }

    if (lang === 'en' && (unmatchedNodes.length || unmatchedAttrs.length)) {
      translateMissingDynamically(unmatchedNodes, unmatchedAttrs);
    }
  }

  function injectStyles() {
    if (document.getElementById('pia-i18n-style')) return;
    var css = [
      '.pia-lang-switcher{display:inline-flex;align-items:center;gap:2px;padding:2px;border-radius:999px;background:rgba(15,23,42,.88);border:1px solid rgba(34,211,238,.38);backdrop-filter:blur(8px);vertical-align:middle}',
      '.pia-lang-btn{border:0;background:transparent;color:#cbd5e1;font-family:Inter,-apple-system,BlinkMacSystemFont,sans-serif;font-size:11px;font-weight:800;letter-spacing:.03em;padding:4px 9px;min-height:24px;min-width:24px;border-radius:999px;cursor:pointer;line-height:1.25;white-space:nowrap;transition:background .15s ease,color .15s ease}',
      '.pia-lang-btn:hover{color:#ffffff}',
      '.pia-lang-btn[aria-pressed="true"]{background:linear-gradient(135deg,#22d3ee 0%,#0ea5e9 100%);color:#020617}',
      '.pia-lang-floating{position:fixed;inset-block-end:1rem;inset-inline-start:1rem;z-index:9998;box-shadow:0 12px 28px rgba(0,0,0,.55)}',
      'html[data-theme="light"] .pia-lang-switcher{background:#e2e8f0;border-color:#94a3b8}',
      'html[data-theme="light"] .pia-lang-btn{color:#334155}',
      'html[data-theme="light"] .pia-lang-btn[aria-pressed="true"]{background:#0284c7;color:#ffffff}',
      '.pia-lang-btn:focus-visible{outline:2px solid #f0c975;outline-offset:2px}'
    ].join('');
    var st = document.createElement('style');
    st.id = 'pia-i18n-style';
    st.textContent = css;
    document.head.appendChild(st);
  }

  function createSwitcherEl(isFloating) {
    var wrap = document.createElement('div');
    wrap.className = 'pia-lang-switcher' + (isFloating ? ' pia-lang-floating' : '');
    wrap.setAttribute('data-pia-lang-switcher', '1');
    wrap.setAttribute('role', 'group');
    wrap.setAttribute('aria-label', 'Idioma / Language');
    wrap.setAttribute('translate', 'no');

    var btnEs = document.createElement('button');
    btnEs.type = 'button';
    btnEs.className = 'pia-lang-btn';
    btnEs.setAttribute('data-lang-opt', 'es');
    btnEs.textContent = '🇪🇸 ES';

    var btnEn = document.createElement('button');
    btnEn.type = 'button';
    btnEn.className = 'pia-lang-btn';
    btnEn.setAttribute('data-lang-opt', 'en');
    btnEn.textContent = '🇺🇸 EN';

    btnEs.addEventListener('click', function () { setLanguage('es'); });
    btnEn.addEventListener('click', function () { setLanguage('en'); });

    wrap.appendChild(btnEs);
    wrap.appendChild(btnEn);
    return wrap;
  }

  function syncSwitcherButtons(lang) {
    var btns = document.querySelectorAll('[data-pia-lang-switcher] [data-lang-opt]');
    btns.forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.getAttribute('data-lang-opt') === lang));
    });
  }

  function mountSwitchers() {
    var slots = document.querySelectorAll('[data-pia-lang-slot]');
    if (slots.length > 0) {
      slots.forEach(function (slot) {
        if (slot.getAttribute(ATTR_MARK) === '1') return;
        slot.setAttribute(ATTR_MARK, '1');
        slot.appendChild(createSwitcherEl(false));
      });
    } else if (!document.querySelector('[data-pia-lang-switcher]')) {
      document.body.appendChild(createSwitcherEl(true));
    }
    syncSwitcherButtons(currentLang);
  }

  function setLanguage(lang) {
    currentLang = (lang === 'en') ? 'en' : 'es';
    try {
      localStorage.setItem(STORAGE_KEY, currentLang);
    } catch (e) {}
    document.documentElement.lang = currentLang;
    syncSwitcherButtons(currentLang);
    if (currentLang === 'en') {
      ensureDictLoaded().then(function () {
        if (currentLang !== 'en') return;
        walkAndTranslate('en');
        document.dispatchEvent(new CustomEvent('prosperia:langchange', { detail: { lang: 'en' } }));
      });
      return;
    }
    walkAndTranslate('es');
    document.dispatchEvent(new CustomEvent('prosperia:langchange', { detail: { lang: 'es' } }));
  }

  function getInitialLang() {
    try {
      var params = new URLSearchParams(window.location.search);
      var qLang = (params.get('lang') || '').toLowerCase();
      if (qLang === 'en' || qLang === 'es') {
        localStorage.setItem(STORAGE_KEY, qLang);
        return qLang;
      }
      var saved = (localStorage.getItem(STORAGE_KEY) || '').toLowerCase();
      if (saved === 'en' || saved === 'es') return saved;
    } catch (e) {}
    return 'es';
  }

  function init() {
    if (!document.body) return;
    injectStyles();
    currentLang = getInitialLang();
    mountSwitchers();
    if (currentLang === 'en') {
      setLanguage('en');
    } else {
      syncSwitcherButtons('es');
    }

    // Si algún componente dinámico añade bloques o actualiza contadores (ROI, asistente voz/chat) en inglés activo, reaplicar suavemente con debounce
    if (typeof MutationObserver !== 'undefined') {
      var moTimer = null;
      activeMo = new MutationObserver(function (mutations) {
        if (observerPaused || currentLang !== 'en') return;
        var needsPass = false;
        for (var i = 0; i < mutations.length; i++) {
          var m = mutations[i];
          if (m.addedNodes && m.addedNodes.length > 0) {
            needsPass = true;
          } else if (m.type === 'characterData' && m.target && m.target.nodeValue) {
            var pEl = m.target.parentElement;
            if (!pEl || !pEl.closest('[data-pia-lang-switcher], [translate="no"]')) {
              if (appliedEnText.get(m.target) !== m.target.nodeValue && origTextNodes.get(m.target) !== m.target.nodeValue) {
                origTextNodes.set(m.target, m.target.nodeValue);
                needsPass = true;
              }
            }
          }
        }
        if (!needsPass) return;
        clearTimeout(moTimer);
        moTimer = setTimeout(function () {
          if (!observerPaused && currentLang === 'en' && dictLoaded) {
            walkAndTranslate('en');
          }
        }, 90);
      });
      activeMo.observe(document.body, { childList: true, subtree: true, characterData: true });
    }
  }

  window.setProsperiaLang = setLanguage;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

/* Doral Fashion Week — Power Upgrade Module (Agencia Prosper IA Ecosystem) */
(function () {
  "use strict";

  var API_SUBMIT = "https://agenciaprosperia.com/api/doralfashionweek/forms/submit";
  var WA_NUMBER = "17866475982";

  var I18N = {
    en: {
      toggle: '<span class="dfw-active-lang">EN</span> | <span>ES</span>',
      nav: {
        home: "Home",
        about: "About",
        applications: "Applications",
        editions: "Editions",
        magazine: "Magazine",
        sponsors: "Sponsors",
      },
      heroH1: "The most prominent<br/>and innovative EVENT",
      hAbout: "About Us",
      hApps: "Applications",
      hEditions: "Editions",
      hNewsletter: "Newsletter",
      eyebrow: "PARTNERSHIPS · RUNWAY ACCESS · VIP HOSPITALITY",
      spTitle: "Sponsors, Designers & VIP Access",
      spSub:
        "Connect your luxury brand, international fashion house, or corporate group with South Florida’s most exclusive runway platform and DFW Magazine.",
      c1Num: "01 · CORPORATE BRANDING",
      c1Title: "Official Corporate Sponsorship",
      c1Desc:
        "Position your brand across our Miami/Doral runway, VIP lounge, step-and-repeat media wall, and DFW Magazine print & digital editions.",
      c1Items: [
        "Title Sponsor & Runway Gold Branding",
        "VIP Lounge & Product Placement Activation",
        "Full-Page Editorial in DFW Magazine",
        "Direct Leads & VIP Guest List Access",
      ],
      c1Btn: "Request Sponsor Deck ↗",
      c2Num: "02 · COUTURE & COLLECTIONS",
      c2Title: "Designer Runway Package",
      c2Desc:
        "Showcase your new collection in front of buyers, press, influencers, and luxury guests with full turnkey runway production.",
      c2Items: [
        "Complete Runway Production & Lighting",
        "Curated Models & Backstage MUA Team",
        "Official Runway Photography & Reels",
        "Direct Feature in DFW Magazine",
      ],
      c2Btn1: "Apply as Designer →",
      c2Btn2: "Request Designer Info ↗",
      c3Num: "03 · HOSPITALITY & MEDIA",
      c3Title: "VIP Front Row & Press Passes",
      c3Desc:
        "Reserve priority Front Row seating, private cocktail hospitality, or press accreditation for our upcoming Doral / Miami showcase.",
      c3Items: [
        "Front Row VIP Runway Seating",
        "Private Reception & Networking Lounge",
        "Backstage Press & Red Carpet Credentials",
        "Direct WhatsApp VIP Concierge Support",
      ],
      c3Btn: "Reserve VIP / Press Access ↗",
      modalTitle: "Partnership & VIP Concierge Desk",
      modalSub: "Leave your details and our Executive Producer Team will reply immediately.",
      lblName: "Full Name",
      lblBrand: "Brand / Company / Fashion House",
      lblEmail: "Corporate Email",
      lblPhone: "WhatsApp / Direct Phone",
      lblTier: "Interest Tier",
      lblNotes: "Brief Note (Optional)",
      btnSubmit: "Send Request Now →",
      sending: "Sending...",
      modalOk:
        "Request received! Our Executive Team has registered your priority inquiry. You can also connect immediately on WhatsApp:",
      waTextBtn: "Chat on VIP WhatsApp (+1 786-647-5982) ↗",
      fabWa: "WhatsApp VIP",
      fabAi: "Concierge IA 24/7",
      aiTitle: "DFW AI Concierge 24/7",
      aiSub: "Runway · Sponsors · Casting · VIP",
      aiWelcome:
        "Welcome to Doral Fashion Week. How can I assist you today? Choose an option below or talk directly with our VIP team:",
      q1: "💎 Corporate Sponsorship / Brand Activation",
      q2: "👗 Designer Runway Showcase Application",
      q3: "🎟️ VIP Front Row & Press Accreditation",
      q4: "📸 Talent Casting (Models, MUA, Photo, Staff)",
      aiQuickHead: "Fast Direct Inquiry",
      aiQuickBtn: "Send to Producer Desk →",
      newsOk: "Subscribed! Your email has been registered with Doral Fashion Week VIP Desk.",
      waContractBtn: "💬 Confirm Contract on WhatsApp (+1 786-647-5982)",
      printContractBtn: "🖨️ Print / Save Contract Receipt",
      ecoTitle: "Idol Jose Group Corp · Ecosystem:",
      powered:
        'AI Concierge & Digital Ecosystem by <a href="https://agenciaprosperia.com" target="_blank" rel="noopener">Agencia Prosper IA</a>',
    },
    es: {
      toggle: '<span>EN</span> | <span class="dfw-active-lang">ES</span>',
      nav: {
        home: "Inicio",
        about: "Nosotros",
        applications: "Aplicaciones",
        editions: "Ediciones",
        magazine: "Revista",
        sponsors: "Patrocinadores",
      },
      heroH1: "El EVENTO de moda<br/>más prominente e innovador",
      hAbout: "Sobre Nosotros",
      hApps: "Aplicaciones Oficiales",
      hEditions: "Ediciones",
      hNewsletter: "Boletín VIP",
      eyebrow: "ALIANZAS · PASARELA · ACCESO VIP",
      spTitle: "Patrocinadores, Diseñadores y Acceso VIP",
      spSub:
        "Conecta tu marca, casa de moda o grupo corporativo con la pasarela más exclusiva del Sur de Florida y DFW Magazine.",
      c1Num: "01 · MARCAS Y PATROCINIO",
      c1Title: "Patrocinio Corporativo Oficial",
      c1Desc:
        "Posiciona tu marca en nuestra pasarela de Miami/Doral, Lounge VIP, muro oficial de prensa y ediciones de DFW Magazine.",
      c1Items: [
        "Presencia como Title Sponsor o Runway Gold",
        "Activación de Marca en Lounge VIP y Backstage",
        "Página Editorial en DFW Magazine",
        "Acceso Directo a Lista VIP y Empresarios",
      ],
      c1Btn: "Solicitar Dossier de Patrocinio ↗",
      c2Num: "02 · COLECCIONES Y PASARELA",
      c2Title: "Paquete de Pasarela para Diseñadores",
      c2Desc:
        "Presenta tu colección frente a compradores, prensa, celebridades e invitados VIP con producción llave en mano.",
      c2Items: [
        "Producción Completa de Pasarela e Iluminación",
        "Modelos Seleccionadas, Maquillaje y Peinado",
        "Fotografía Oficial y Reels de Pasarela",
        "Cobertura y Entrevista en DFW Magazine",
      ],
      c2Btn1: "Aplicar como Diseñador →",
      c2Btn2: "Pedir Información de Pasarela ↗",
      c3Num: "03 · HOSPITALIDAD Y PRENSA",
      c3Title: "Boletos VIP Front Row y Prensa",
      c3Desc:
        "Asegura asientos prioritarios Front Row, acceso a cóctel VIP o acreditación oficial de medios para la próxima edición.",
      c3Items: [
        "Asientos Preferenciales Front Row",
        "Recepción Privada y Networking VIP",
        "Acreditación Oficial de Prensa y Alfombra Roja",
        "Atención Directa por WhatsApp VIP 24/7",
      ],
      c3Btn: "Reservar Acceso VIP / Prensa ↗",
      modalTitle: "Mesa Ejecutiva de Patrocinios y VIP",
      modalSub: "Deja tus datos y nuestro equipo de Producción Ejecutiva te contactará de inmediato.",
      lblName: "Nombre Completo",
      lblBrand: "Marca / Empresa / Casa de Moda",
      lblEmail: "Correo Corporativo",
      lblPhone: "WhatsApp / Teléfono Directo",
      lblTier: "Categoría de Interés",
      lblNotes: "Mensaje Breve (Opcional)",
      btnSubmit: "Enviar Solicitud Ahora →",
      sending: "Enviando...",
      modalOk:
        "¡Solicitud recibida! Tu registro ya quedó en nuestra Mesa Ejecutiva. También puedes escribirnos directo por WhatsApp:",
      waTextBtn: "Hablar por WhatsApp VIP (+1 786-647-5982) ↗",
      fabWa: "WhatsApp VIP",
      fabAi: "Concierge IA 24/7",
      aiTitle: "DFW Concierge IA 24/7",
      aiSub: "Pasarela · Sponsors · Casting · VIP",
      aiWelcome:
        "Bienvenido a Doral Fashion Week. ¿En qué podemos ayudarte hoy? Elige una opción o habla directo con nuestro equipo VIP:",
      q1: "💎 Patrocinio Corporativo / Activación de Marca",
      q2: "👗 Presentar Colección como Diseñador",
      q3: "🎟️ Boletos VIP Front Row y Prensa",
      q4: "📸 Casting y Talento (Modelos, MUA, Foto, Staff)",
      aiQuickHead: "Registro Rápido Directo",
      aiQuickBtn: "Enviar a Producción →",
      newsOk: "¡Suscrito! Tu correo ya quedó registrado en la mesa VIP de Doral Fashion Week.",
      waContractBtn: "💬 Confirmar Contrato por WhatsApp (+1 786-647-5982)",
      printContractBtn: "🖨️ Imprimir / Guardar Comprobante",
      ecoTitle: "Ecosistema Idol Jose Group Corp:",
      powered:
        'Concierge IA y Ecosistema Digital por <a href="https://agenciaprosperia.com" target="_blank" rel="noopener">Agencia Prosper IA</a>',
    },
  };

  function getLang() {
    try {
      var saved = localStorage.getItem("dfw_lang");
      if (saved === "es" || saved === "en") return saved;
    } catch (e) {}
    return "en";
  }

  function setLang(lang) {
    try {
      localStorage.setItem("dfw_lang", lang);
    } catch (e) {}
    applyLanguage(lang);
  }

  function waUrl(message) {
    return "https://wa.me/" + WA_NUMBER + "?text=" + encodeURIComponent(message);
  }

  function postForm(payload) {
    return fetch(API_SUBMIT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  }

  function isPortfolioMode() {
    return window.location.pathname.indexOf("/portafolio-vivo/doralfashionweek") === 0;
  }

  function routeHref(path) {
    var clean = path === "/" ? "/" : path + "/";
    return isPortfolioMode() ? "/portafolio-vivo/doralfashionweek" + clean : clean;
  }

  /* ── 1. Language Switcher & Nav Sponsors Anchor Fix ───────────────────── */
  function wireNavAndToggle() {
    var nav = document.querySelector("nav");
    if (!nav) return;

    var links = nav.querySelectorAll("a");
    links.forEach(function (a) {
      var txt = (a.textContent || "").trim().toLowerCase();
      if (txt === "sponsors" || txt === "patrocinadores") {
        a.setAttribute("href", "#sponsors");
        a.setAttribute("data-dfw-nav", "sponsors");
      } else if (txt === "home" || txt === "inicio") {
        a.setAttribute("data-dfw-nav", "home");
      } else if (txt === "about" || txt === "nosotros") {
        a.setAttribute("data-dfw-nav", "about");
      } else if (txt === "applications" || txt === "aplicaciones") {
        a.setAttribute("data-dfw-nav", "applications");
      } else if (txt === "editions" || txt === "ediciones") {
        a.setAttribute("data-dfw-nav", "editions");
      } else if (txt === "magazine" || txt === "revista") {
        a.setAttribute("data-dfw-nav", "magazine");
      }
    });

    // Also fix footer "Sponsors" link
    document.querySelectorAll("footer a").forEach(function (a) {
      var txt = (a.textContent || "").trim().toLowerCase();
      if (txt === "sponsors" || txt === "patrocinadores") {
        a.setAttribute("href", "#sponsors");
        a.setAttribute("data-dfw-nav", "sponsors");
      }
    });

    if (!document.getElementById("dfw-lang-switcher")) {
      var rightCol = nav.querySelector(".nav-col-right") || nav;
      var btn = document.createElement("button");
      btn.type = "button";
      btn.id = "dfw-lang-switcher";
      btn.className = "dfw-lang-btn";
      btn.setAttribute("aria-label", "Switch language English / Español");
      btn.addEventListener("click", function () {
        setLang(getLang() === "en" ? "es" : "en");
      });
      rightCol.appendChild(btn);
    }
  }

  /* ── 2. High-Ticket Sponsors Section & B2B Dialog Modal ───────────────── */
  function ensureSponsorsSection() {
    var path = window.location.pathname || "/";
    if (path !== "/" && path !== "/portafolio-vivo/doralfashionweek/") return;
    if (document.getElementById("sponsors")) return;

    var newsletter = document.getElementById("newsletter");
    var parent = (newsletter && newsletter.parentNode) || document.querySelector("main");
    if (!parent) return;

    var sec = document.createElement("section");
    sec.id = "sponsors";
    sec.className = "dfw-sponsors-section";
    sec.innerHTML =
      '<div class="dfw-sponsors-head">' +
      '  <div class="dfw-eyebrow" data-dfw-i18n="eyebrow"></div>' +
      '  <h2 data-dfw-i18n="spTitle"></h2>' +
      '  <p data-dfw-i18n="spSub"></p>' +
      "</div>" +
      '<div class="dfw-sponsors-grid">' +
      '  <article class="dfw-sponsor-card featured">' +
      "    <div>" +
      '      <div class="dfw-sponsor-num" data-dfw-i18n="c1Num"></div>' +
      '      <h3 data-dfw-i18n="c1Title"></h3>' +
      '      <p data-dfw-i18n="c1Desc"></p>' +
      '      <ul class="dfw-sponsor-list" id="dfw-c1-list"></ul>' +
      "    </div>" +
      '    <button type="button" class="dfw-btn-gold" data-dfw-open-modal="Corporate Sponsorship" data-dfw-i18n="c1Btn"></button>' +
      "  </article>" +
      '  <article class="dfw-sponsor-card">' +
      "    <div>" +
      '      <div class="dfw-sponsor-num" data-dfw-i18n="c2Num"></div>' +
      '      <h3 data-dfw-i18n="c2Title"></h3>' +
      '      <p data-dfw-i18n="c2Desc"></p>' +
      '      <ul class="dfw-sponsor-list" id="dfw-c2-list"></ul>' +
      "    </div>" +
      '    <div style="display:grid;gap:8px;">' +
      '      <a class="dfw-btn-gold" href="' + routeHref("/apply/designer") + '" data-dfw-i18n="c2Btn1"></a>' +
      '      <button type="button" class="dfw-btn-outline" data-dfw-open-modal="Designer Runway Package" data-dfw-i18n="c2Btn2"></button>' +
      "    </div>" +
      "  </article>" +
      '  <article class="dfw-sponsor-card">' +
      "    <div>" +
      '      <div class="dfw-sponsor-num" data-dfw-i18n="c3Num"></div>' +
      '      <h3 data-dfw-i18n="c3Title"></h3>' +
      '      <p data-dfw-i18n="c3Desc"></p>' +
      '      <ul class="dfw-sponsor-list" id="dfw-c3-list"></ul>' +
      "    </div>" +
      '    <button type="button" class="dfw-btn-outline" data-dfw-open-modal="VIP Front Row & Press Access" data-dfw-i18n="c3Btn"></button>' +
      "  </article>" +
      "</div>";

    if (newsletter) {
      parent.insertBefore(sec, newsletter);
    } else {
      parent.appendChild(sec);
    }

    sec.querySelectorAll("[data-dfw-open-modal]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        openSponsorModal(btn.getAttribute("data-dfw-open-modal"));
      });
    });
  }

  function ensureSponsorModal() {
    if (document.getElementById("dfwSponsorModal")) return;
    var dlg = document.createElement("dialog");
    dlg.id = "dfwSponsorModal";
    dlg.setAttribute("closedby", "any");
    dlg.setAttribute("aria-labelledby", "dfwSponsorModalTitle");
    dlg.innerHTML =
      '<div class="dfw-modal-head">' +
      "  <div>" +
      '    <div class="dfw-eyebrow" style="margin-bottom:8px;">DORAL FASHION WEEK</div>' +
      '    <h3 id="dfwSponsorModalTitle" style="font-size:1.35rem;font-weight:700;margin-bottom:4px;" data-dfw-i18n="modalTitle"></h3>' +
      '    <p style="font-size:0.85rem;color:rgba(255,255,255,0.68);" data-dfw-i18n="modalSub"></p>' +
      "  </div>" +
      '  <button type="button" class="dfw-modal-close" id="dfwModalCloseBtn" aria-label="Close">✕</button>' +
      "</div>" +
      '<form id="dfwSponsorForm">' +
      '  <div class="dfw-field"><label for="dfwName" data-dfw-i18n="lblName"></label><input id="dfwName" required placeholder="Ej. Sofía Mendoza"></div>' +
      '  <div class="dfw-field"><label for="dfwBrand" data-dfw-i18n="lblBrand"></label><input id="dfwBrand" required placeholder="Ej. Atelier / Empresa"></div>' +
      '  <div class="dfw-field"><label for="dfwEmail" data-dfw-i18n="lblEmail"></label><input id="dfwEmail" type="email" required placeholder="brand@company.com"></div>' +
      '  <div class="dfw-field"><label for="dfwPhone" data-dfw-i18n="lblPhone"></label><input id="dfwPhone" required placeholder="+1 (305) ..."></div>' +
      '  <div class="dfw-field"><label for="dfwTier" data-dfw-i18n="lblTier"></label>' +
      '    <select id="dfwTier">' +
      '      <option value="Corporate Sponsorship">01. Official Corporate Sponsorship</option>' +
      '      <option value="Designer Runway Package">02. Designer Runway Showcase</option>' +
      '      <option value="VIP Front Row & Press Access">03. VIP Front Row & Press Access</option>' +
      "    </select>" +
      "  </div>" +
      '  <div class="dfw-field"><label for="dfwNotes" data-dfw-i18n="lblNotes"></label><textarea id="dfwNotes" rows="2"></textarea></div>' +
      '  <button type="submit" id="dfwSponsorSubmit" class="dfw-btn-gold" data-dfw-i18n="btnSubmit"></button>' +
      "</form>" +
      '<div id="dfwSponsorResult" style="display:none;margin-top:1rem;">' +
      '  <p style="color:#f3dc92;font-size:0.95rem;line-height:1.55;margin-bottom:1rem;" data-dfw-i18n="modalOk"></p>' +
      '  <a id="dfwModalWaBtn" class="dfw-fab-wa" style="width:100%;justify-content:center;" target="_blank" rel="noopener" data-dfw-i18n="waTextBtn"></a>' +
      "</div>";

    document.body.appendChild(dlg);

    document.getElementById("dfwModalCloseBtn").addEventListener("click", function () {
      dlg.close();
    });

    // Mandatory light-dismiss fallback for browsers without closedBy (e.g. Safari)
    if (!("closedBy" in HTMLDialogElement.prototype)) {
      dlg.addEventListener("click", function (event) {
        if (event.target !== dlg) return;
        var rect = dlg.getBoundingClientRect();
        var inside =
          rect.top <= event.clientY &&
          event.clientY <= rect.top + rect.height &&
          rect.left <= event.clientX &&
          event.clientX <= rect.left + rect.width;
        if (!inside) dlg.close();
      });
    }

    document.getElementById("dfwSponsorForm").addEventListener("submit", function (ev) {
      ev.preventDefault();
      var lang = getLang();
      var t = I18N[lang];
      var btn = document.getElementById("dfwSponsorSubmit");
      btn.disabled = true;
      btn.textContent = t.sending;

      var name = document.getElementById("dfwName").value.trim();
      var brand = document.getElementById("dfwBrand").value.trim();
      var email = document.getElementById("dfwEmail").value.trim();
      var phone = document.getElementById("dfwPhone").value.trim();
      var tier = document.getElementById("dfwTier").value;
      var notes = document.getElementById("dfwNotes").value.trim();
      var contractId = "DFW-VIP-" + Math.floor(1000 + Math.random() * 9000);

      postForm({
        fullName: name,
        email: email,
        phone: phone,
        portfolio: brand,
        experienceDetails: "[" + tier + "] " + notes,
        role: tier,
        contractId: contractId,
      })
        .catch(function () {})
        .finally(function () {
          document.getElementById("dfwSponsorForm").style.display = "none";
          var resBox = document.getElementById("dfwSponsorResult");
          resBox.style.display = "block";
          var msg =
            "Hola Doral Fashion Week / Idol Jose, soy " +
            name +
            " (" +
            brand +
            "). Me interesa: " +
            tier +
            " [Ref: " +
            contractId +
            "].";
          document.getElementById("dfwModalWaBtn").href = waUrl(msg);
          btn.disabled = false;
        });
    });
  }

  function openSponsorModal(tier) {
    ensureSponsorModal();
    var dlg = document.getElementById("dfwSponsorModal");
    var form = document.getElementById("dfwSponsorForm");
    var res = document.getElementById("dfwSponsorResult");
    form.style.display = "block";
    res.style.display = "none";
    var sel = document.getElementById("dfwTier");
    if (tier && sel) sel.value = tier;
    applyLanguage(getLang());
    dlg.showModal();
  }

  /* ── 3. Floating AI Concierge 24/7 + WhatsApp VIP ─────────────────────── */
  function ensureFloatingConcierge() {
    if (document.getElementById("dfw-fab-wrap")) return;

    var wrap = document.createElement("div");
    wrap.id = "dfw-fab-wrap";
    wrap.className = "dfw-fab-wrap";
    wrap.innerHTML =
      '<div id="dfw-concierge-panel" class="dfw-concierge-panel" role="dialog" aria-label="DFW Concierge">' +
      '  <div class="dfw-concierge-head">' +
      "    <div>" +
      '      <div style="font-size:13px;font-weight:800;color:#f3dc92;" data-dfw-i18n="aiTitle"></div>' +
      '      <div style="font-size:11px;color:rgba(255,255,255,0.65);" data-dfw-i18n="aiSub"></div>' +
      "    </div>" +
      '    <button type="button" id="dfw-ai-close" class="dfw-modal-close" aria-label="Close">✕</button>' +
      "  </div>" +
      '  <div class="dfw-concierge-body" id="dfw-ai-body">' +
      '    <div class="dfw-msg-ai" data-dfw-i18n="aiWelcome"></div>' +
      '    <div class="dfw-quick-grid">' +
      '      <button type="button" class="dfw-quick-btn" data-dfw-q="sponsor" data-dfw-i18n="q1"></button>' +
      '      <button type="button" class="dfw-quick-btn" data-dfw-q="designer" data-dfw-i18n="q2"></button>' +
      '      <button type="button" class="dfw-quick-btn" data-dfw-q="vip" data-dfw-i18n="q3"></button>' +
      '      <button type="button" class="dfw-quick-btn" data-dfw-q="casting" data-dfw-i18n="q4"></button>' +
      "    </div>" +
      '    <form id="dfw-ai-quick-form" style="margin-top:6px;padding-top:10px;border-top:1px solid rgba(255,255,255,0.1);display:grid;gap:7px;">' +
      '      <div style="font-size:11px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:#d4af37;" data-dfw-i18n="aiQuickHead"></div>' +
      '      <input id="dfwAiName" required placeholder="Name / Nombre" style="padding:8px 10px;border-radius:8px;border:1px solid rgba(255,255,255,0.18);background:rgba(255,255,255,0.05);color:#fff;font-size:12px;">' +
      '      <input id="dfwAiContact" required placeholder="WhatsApp or Email" style="padding:8px 10px;border-radius:8px;border:1px solid rgba(255,255,255,0.18);background:rgba(255,255,255,0.05);color:#fff;font-size:12px;">' +
      '      <button type="submit" id="dfwAiSubmit" class="dfw-btn-gold" style="padding:9px 12px;font-size:11px;" data-dfw-i18n="aiQuickBtn"></button>' +
      "    </form>" +
      "  </div>" +
      "</div>" +
      '<div class="dfw-fab-row">' +
      '  <a id="dfw-fab-wa" class="dfw-fab-wa" target="_blank" rel="noopener" href="' +
      waUrl("Hola Doral Fashion Week / Idol Jose, me gustaría información sobre pasarela, patrocinios o boletos VIP.") +
      '"><span data-dfw-i18n="fabWa"></span></a>' +
      '  <button type="button" id="dfw-fab-ai" class="dfw-fab-ai">💎 <span data-dfw-i18n="fabAi"></span></button>' +
      "</div>";

    document.body.appendChild(wrap);

    var panel = document.getElementById("dfw-concierge-panel");
    document.getElementById("dfw-fab-ai").addEventListener("click", function () {
      panel.classList.toggle("open");
    });
    document.getElementById("dfw-ai-close").addEventListener("click", function () {
      panel.classList.remove("open");
    });

    wrap.querySelectorAll("[data-dfw-q]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var q = btn.getAttribute("data-dfw-q");
        var es = getLang() === "es";
        var body = document.getElementById("dfw-ai-body");
        var u = document.createElement("div");
        u.className = "dfw-msg-user";
        u.textContent = btn.textContent;
        body.insertBefore(u, document.getElementById("dfw-ai-quick-form"));

        var reply = document.createElement("div");
        reply.className = "dfw-msg-ai";
        if (q === "sponsor") {
          reply.innerHTML = es
            ? "Excelente. Ofrecemos presencia como <strong>Title Sponsor, Runway Gold y DFW Magazine</strong>. Abriendo la solicitud B2B..."
            : "Excellent. We offer <strong>Title Sponsor, Runway Gold, and DFW Magazine</strong> activations. Opening the B2B inquiry...";
          body.insertBefore(reply, document.getElementById("dfw-ai-quick-form"));
          setTimeout(function () {
            openSponsorModal("Corporate Sponsorship");
          }, 350);
        } else if (q === "designer") {
          reply.innerHTML = es
            ? 'Nuestros paquetes de diseñador incluyen producción, modelos y DFW Magazine. <a href="' +
              routeHref("/apply/designer") +
              '" style="color:#f3dc92;text-decoration:underline;font-weight:700;">Ir al portal de Diseñadores →</a>'
            : 'Our Designer Showcase includes full production, curated models & DFW Magazine press. <a href="' +
              routeHref("/apply/designer") +
              '" style="color:#f3dc92;text-decoration:underline;font-weight:700;">Open Designer Application →</a>';
          body.insertBefore(reply, document.getElementById("dfw-ai-quick-form"));
        } else if (q === "vip") {
          reply.innerHTML = es
            ? "Perfecto, reservemos tus asientos <strong>VIP Front Row o Pase de Prensa</strong>..."
            : "Great, let’s reserve your <strong>VIP Front Row Seating or Press Access</strong>...";
          body.insertBefore(reply, document.getElementById("dfw-ai-quick-form"));
          setTimeout(function () {
            openSponsorModal("VIP Front Row & Press Access");
          }, 350);
        } else {
          reply.innerHTML = es
            ? 'Elige tu portal oficial con contrato digital:<br><a href="' +
              routeHref("/apply/model") +
              '" style="color:#f3dc92;">• Modelos</a> &nbsp; <a href="' +
              routeHref("/apply/makeup") +
              '" style="color:#f3dc92;">• Makeup</a> &nbsp; <a href="' +
              routeHref("/apply/photographer") +
              '" style="color:#f3dc92;">• Fotógrafos</a> &nbsp; <a href="' +
              routeHref("/apply/staff") +
              '" style="color:#f3dc92;">• Staff</a>'
            : 'Select your official portal:<br><a href="' +
              routeHref("/apply/model") +
              '" style="color:#f3dc92;">• Models</a> &nbsp; <a href="' +
              routeHref("/apply/makeup") +
              '" style="color:#f3dc92;">• Makeup</a> &nbsp; <a href="' +
              routeHref("/apply/photographer") +
              '" style="color:#f3dc92;">• Photographers</a> &nbsp; <a href="' +
              routeHref("/apply/staff") +
              '" style="color:#f3dc92;">• Staff</a>';
          body.insertBefore(reply, document.getElementById("dfw-ai-quick-form"));
        }
        body.scrollTop = body.scrollHeight;
      });
    });

    document.getElementById("dfw-ai-quick-form").addEventListener("submit", function (ev) {
      ev.preventDefault();
      var es = getLang() === "es";
      var nm = document.getElementById("dfwAiName").value.trim();
      var ct = document.getElementById("dfwAiContact").value.trim();
      var btn = document.getElementById("dfwAiSubmit");
      btn.disabled = true;
      postForm({
        fullName: nm,
        email: ct.indexOf("@") !== -1 ? ct : "",
        phone: ct.indexOf("@") === -1 ? ct : "",
        role: "concierge_vip",
        contractId: "DFW-AI-" + Math.floor(1000 + Math.random() * 9000),
        experienceDetails: "Consulta rápida vía Concierge IA 24/7",
      })
        .catch(function () {})
        .finally(function () {
          btn.disabled = false;
          var body = document.getElementById("dfw-ai-body");
          var done = document.createElement("div");
          done.className = "dfw-msg-ai";
          done.innerHTML = es
            ? '✅ Recibido, <strong>' + nm + '</strong>. <a href="' + waUrl("Hola Doral Fashion Week, soy " + nm + " (" + ct + ").") + '" target="_blank" rel="noopener" style="color:#34d399;text-decoration:underline;">Abrir WhatsApp directo ↗</a>'
            : '✅ Received, <strong>' + nm + '</strong>. <a href="' + waUrl("Hi Doral Fashion Week, I am " + nm + " (" + ct + ").") + '" target="_blank" rel="noopener" style="color:#34d399;text-decoration:underline;">Open WhatsApp now ↗</a>';
          body.insertBefore(done, document.getElementById("dfw-ai-quick-form"));
          document.getElementById("dfw-ai-quick-form").reset();
          body.scrollTop = body.scrollHeight;
        });
    });
  }

  /* ── 4. Real Newsletter Hook & Post-Contract Actions ──────────────────── */
  function wireNewsletterCapture() {
    if (window.__dfwNewsWired) return;
    window.__dfwNewsWired = true;
    document.addEventListener(
      "submit",
      function (ev) {
        var form = ev.target;
        if (!form || !form.classList || !form.classList.contains("newsletter-form")) return;
        ev.preventDefault();
        ev.stopPropagation();

        var input = form.querySelector('input[type="email"]');
        var btn = form.querySelector('button[type="submit"]');
        var email = input ? input.value.trim() : "";
        if (!email) return;

        var lang = getLang();
        if (btn) btn.disabled = true;

        postForm({
          fullName: email.split("@")[0],
          email: email,
          role: "newsletter",
          contractId: "DFW-NEWS-" + Math.floor(1000 + Math.random() * 9000),
          experienceDetails: "Suscripción Newsletter doralfashionweek.com",
        })
          .catch(function () {})
          .finally(function () {
            if (btn) btn.disabled = false;
            var oldStatus = form.querySelector(".dfw-newsletter-status");
            if (oldStatus) oldStatus.remove();
            var st = document.createElement("div");
            st.className = "dfw-newsletter-status";
            st.textContent = I18N[lang].newsOk;
            form.appendChild(st);
            form.reset();
          });
      },
      true
    );
  }

  function trackSubmittedContractsAndUpgradeDoneScreen() {
    if (!window.__dfwContractFetchHooked && typeof window.fetch === "function") {
      window.__dfwContractFetchHooked = true;
      var curFetch = window.fetch;
      window.fetch = function (input, init) {
        var url = typeof input === "string" ? input : (input && input.url ? input.url : "");
        if (url && url.indexOf("forms/submit") !== -1 && init && init.body) {
          try {
            var parsed = JSON.parse(init.body);
            if (parsed && parsed.contractId) {
              window.__dfwLastContract = parsed;
            }
          } catch (e) {}
        }
        return curFetch.apply(this, arguments);
      };
    }

    if (document.getElementById("dfw-contract-actions")) return;
    var titles = document.querySelectorAll("h4");
    for (var i = 0; i < titles.length; i++) {
      if ((titles[i].textContent || "").trim().toLowerCase() === "protocol complete") {
        var box = titles[i].parentElement;
        if (!box) continue;
        var info = window.__dfwLastContract || {};
        var cid = info.contractId || "DFW-2026";
        var cname = info.fullName || "";
        var crole = info.role || "";
        var lang = getLang();

        var actions = document.createElement("div");
        actions.id = "dfw-contract-actions";
        actions.className = "dfw-contract-actions";
        var waMsg =
          "Hola Doral Fashion Week / Idol Jose, acabo de firmar mi aplicación (" +
          crole +
          ") " +
          (cname ? "- " + cname + " " : "") +
          "con Contract ID: " +
          cid +
          ".";
        actions.innerHTML =
          '<a href="' +
          waUrl(waMsg) +
          '" target="_blank" rel="noopener" style="background:#10b981;color:#03150e;border:1px solid #34d399;" data-dfw-i18n="waContractBtn">' +
          I18N[lang].waContractBtn +
          "</a>" +
          '<button type="button" onclick="window.print()" style="background:rgba(255,255,255,0.08);color:#fff;border:1px solid rgba(255,255,255,0.25);" data-dfw-i18n="printContractBtn">' +
          I18N[lang].printContractBtn +
          "</button>";
        box.appendChild(actions);
        break;
      }
    }
  }

  /* ── 5. Footer Ecosystem Bar ──────────────────────────────────────────── */
  function ensureFooterEcosystemBar() {
    var footer = document.querySelector("footer");
    if (!footer || document.getElementById("dfw-ecosystem-bar")) return;

    var bar = document.createElement("div");
    bar.id = "dfw-ecosystem-bar";
    bar.className = "dfw-ecosystem-bar";
    bar.innerHTML =
      '<div class="dfw-ecosystem-links">' +
      '  <strong style="font-size:11px;letter-spacing:0.16em;text-transform:uppercase;color:#d4af37;" data-dfw-i18n="ecoTitle"></strong>' +
      '  <a href="https://idoljoseofficial.com" target="_blank" rel="noopener">Idol Jose Official ↗</a>' +
      '  <a href="https://idoljosegroupcorp.com" target="_blank" rel="noopener">Idol Jose Group Corp ↗</a>' +
      '  <a href="https://doralbusinesscity.com" target="_blank" rel="noopener">Doral Business City ↗</a>' +
      '  <a href="https://www.doralfashionweekmagazine.com" target="_blank" rel="noopener">DFW Magazine ↗</a>' +
      "</div>" +
      '<div class="dfw-powered" data-dfw-i18n-html="powered"></div>';

    var bottom = footer.querySelector(".footer-bottom");
    if (bottom && bottom.parentNode === footer) {
      footer.insertBefore(bar, bottom);
    } else {
      footer.appendChild(bar);
    }
  }

  /* ── Apply Language Across UI ─────────────────────────────────────────── */
  function applyLanguage(lang) {
    var t = I18N[lang] || I18N.en;
    var sw = document.getElementById("dfw-lang-switcher");
    if (sw) sw.innerHTML = t.toggle;

    document.querySelectorAll("[data-dfw-nav]").forEach(function (el) {
      var key = el.getAttribute("data-dfw-nav");
      if (t.nav[key]) el.textContent = t.nav[key];
    });

    document.querySelectorAll("[data-dfw-i18n]").forEach(function (el) {
      var k = el.getAttribute("data-dfw-i18n");
      if (t[k]) el.textContent = t[k];
    });
    document.querySelectorAll("[data-dfw-i18n-html]").forEach(function (el) {
      var k = el.getAttribute("data-dfw-i18n-html");
      if (t[k]) el.innerHTML = t[k];
    });

    var h1 = document.querySelector("h1");
    if (h1 && !h1.hasAttribute("data-dfw-fixed-h")) h1.setAttribute("data-dfw-fixed-h", "heroH1");
    document.querySelectorAll("h2").forEach(function (h2) {
      if (h2.hasAttribute("data-dfw-i18n") || h2.hasAttribute("data-dfw-fixed-h")) return;
      var txt = (h2.textContent || "").trim().toLowerCase();
      if (txt === "about us" || txt === "sobre nosotros") h2.setAttribute("data-dfw-fixed-h", "hAbout");
      else if (txt === "applications" || txt === "aplicaciones oficiales") h2.setAttribute("data-dfw-fixed-h", "hApps");
      else if (txt === "editions" || txt === "ediciones") h2.setAttribute("data-dfw-fixed-h", "hEditions");
      else if (txt === "newsletter" || txt === "boletín vip") h2.setAttribute("data-dfw-fixed-h", "hNewsletter");
    });
    document.querySelectorAll("[data-dfw-fixed-h]").forEach(function (el) {
      var k = el.getAttribute("data-dfw-fixed-h");
      if (!t[k]) return;
      if (lang === "es") {
        el.setAttribute("data-dfw-lang-dirty", "1");
        if (el.innerHTML !== t[k]) el.innerHTML = t[k];
      } else if (el.hasAttribute("data-dfw-lang-dirty")) {
        el.removeAttribute("data-dfw-lang-dirty");
        el.innerHTML = t[k];
      }
    });

    var lists = [
      ["dfw-c1-list", t.c1Items],
      ["dfw-c2-list", t.c2Items],
      ["dfw-c3-list", t.c3Items],
    ];
    lists.forEach(function (pair) {
      var ul = document.getElementById(pair[0]);
      if (!ul) return;
      ul.innerHTML = pair[1]
        .map(function (item) {
          return "<li>" + item + "</li>";
        })
        .join("");
    });
  }

  function syncUpgrades() {
    wireNavAndToggle();
    ensureSponsorsSection();
    ensureFloatingConcierge();
    ensureFooterEcosystemBar();
    wireNewsletterCapture();
    trackSubmittedContractsAndUpgradeDoneScreen();
    applyLanguage(getLang());
  }

  function boot() {
    syncUpgrades();
    // Next.js hydrates right after load; keep upgrades mounted cleanly
    var checks = 0;
    var iv = setInterval(function () {
      syncUpgrades();
      checks += 1;
      if (checks >= 16) clearInterval(iv);
    }, 350);
    var obs = new MutationObserver(function () {
      var isApply = (window.location.pathname || "").indexOf("/apply/") !== -1;
      var needCore =
        !document.getElementById("dfw-lang-switcher") ||
        !document.getElementById("dfw-ecosystem-bar");
      if (needCore) {
        syncUpgrades();
      } else if (isApply && !document.getElementById("dfw-contract-actions")) {
        trackSubmittedContractsAndUpgradeDoneScreen();
      }
    });
    obs.observe(document.body || document.documentElement, { childList: true, subtree: true });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();

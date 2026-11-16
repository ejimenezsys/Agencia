/* ==========================================================================
   IDOL JOSE OFFICIAL — INTERACTIVE ENGINE, CMS, TIMELINE & LOGISTICS
   ========================================================================== */

const IDOL_JOSE_CONFIG = {
  brandName: "IDOL JOSE GROUP",
  instagramHandle: "@doralfashionweekoficial",
  whatsappConcierge: "17866475982", // WhatsApp Oficial IDOL JOSE: +1 (786) 647-5982
  stripeCheckoutWebhook: "", // URL opcional de Stripe Payment Link / API
  instagramAutomationWebhook: "" // URL de Make / Zapier / n8n para auto-post en Instagram
};

/* --------------------------------------------------------------------------
   1. TIMELINE DATA (2017 – 2026 PRESENT)
   -------------------------------------------------------------------------- */
const TIMELINE_DATA = [
  {
    year: "2017",
    collection: "Génesis Sartorial & Precisión Anatómica",
    location: "Caracas · Miami",
    tags: ["Fundación", "Sastrería de Autor", "The Fashion Doctors"],
    summary: "Los Dres. Idolfredo Hernández y Juan Francisco Cabello consolidan la transición multidisciplinaria de la cirugía y la anatomía médica hacia la arquitectura textil de alta gama, dando vida al sello IDOL JOSE.",
    highlights: [
      "Lanzamiento de la primera cápsula de sastrería arquitectónica y draping experimental.",
      "Desarrollo del patronaje anatómico propio que define la silueta IDOL JOSE.",
      "Primeros editoriales de moda y vestuario para personalidades en Latinoamérica y Miami."
    ],
    pressQuote: "“La precisión del bisturí trasladada al corte de la seda y el brocado.” — Editorial Debut",
    youtubeUrl: "https://www.youtube.com/results?search_query=Idol+Jose+Fashion+Designer+Runway",
    image: "https://images.unsplash.com/photo-1509631179647-0177331693ae?auto=format&fit=crop&w=1200&q=85"
  },
  {
    year: "2018",
    collection: "Opulencia Estructural",
    location: "Miami · Latinoamérica",
    tags: ["Expansión Internacional", "Resort Couture", "Brocados"],
    summary: "Expansión hacia pasarelas internacionales en Estados Unidos y el Caribe, fusionando texturas teatrales con sastrería contemporánea sin género.",
    highlights: [
      "Presentación en plataformas internacionales de diseño latinoamericano en Florida.",
      "Consolidación de la línea de capas estructuradas y piezas de Talla Universal con caída orgánica.",
      "Cobertura en revistas especializadas de lujo y alfombras rojas en Miami."
    ],
    pressQuote: "“Un lenguaje visual audaz que desafía las fronteras entre arte escénico y alta costura.”",
    youtubeUrl: "https://www.youtube.com/results?search_query=Idol+Jose+FDLA+NYFW",
    image: "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=1200&q=85"
  },
  {
    year: "2019",
    collection: "L'Éclat Avant-Garde — Debut consagratorio en NYFW",
    location: "New York Fashion Week (NYFW)",
    tags: ["NYFW Septiembre 2019", "FDLA", "Prensa Global"],
    summary: "Consagración en la Semana de la Moda de Nueva York (Septiembre 2019), captando la atención de la crítica europea, estadounidense y rusa por su vanguardismo.",
    highlights: [
      "Desfile oficial en Manhattan junto a Fashion Designers of Latin America (FDLA).",
      "Destacado por la prensa internacional (incluyendo Nezavisimaya Gazeta y medios de NY) como talento global imprescindible.",
      "Incorporación de hombreras escultóricas, sedas plisadas y dramatismo cromático."
    ],
    pressQuote: "“Idol José emerge en Nueva York como una de las propuestas más magnéticas de la temporada.” — Crítica NYFW 2019",
    youtubeUrl: "https://www.youtube.com/results?search_query=Idol+Jose+NYFW+2019+FDLA",
    image: "https://images.unsplash.com/photo-1539109136881-3be0616acf4b?auto=format&fit=crop&w=1200&q=85"
  },
  {
    year: "2020",
    collection: "Attraction 2020 — Manifiesto Multirracial",
    location: "NYFW Digital Platform · FDLA",
    tags: ["Attraction 2020", "Fashion Film", "NYFW Oficial"],
    summary: "Durante la transformación digital global, IDOL JOSE presenta 'Attraction 2020' a través de la plataforma oficial de FDLA en NYFW: una colección multirracial, inclusiva y profundamente escultórica.",
    highlights: [
      "Estreno mundial del Fashion Film 'Attraction 2020' en el calendario oficial de FDLA NYFW.",
      "Manifiesto de diversidad cultural e identidad latinoamericana en alta costura.",
      "Récord de alcance digital y difusión en portales de moda de Nueva York."
    ],
    pressQuote: "“Attraction 2020 celebra la riqueza multirracial con una puesta en escena cinematográfica impecable.” — FDLA Official",
    youtubeUrl: "https://www.youtube.com/results?search_query=Idol+Jose+Attraction+2020+FDLA",
    image: "https://images.unsplash.com/photo-1469334031218-e382a71b716b?auto=format&fit=crop&w=1200&q=85"
  },
  {
    year: "2021",
    collection: "Renaissance & Phased Return",
    location: "Nueva York · Miami",
    tags: ["Retorno a Pasarela", "Resort & Couture", "FDLA Showcase"],
    summary: "El regreso físico y sensorial a las pasarelas neoyorquinas con una propuesta que exalta la libertad de movimiento, el draping fluido y la sastrería de autor.",
    highlights: [
      "Participación híbrida y presencial en los showcases curados de FDLA en Manhattan.",
      "Lanzamiento de siluetas fluidas unisex de alta gama adaptables a múltiples fisonomías.",
      "Colaboraciones editoriales con fotógrafos de moda en Nueva York y Miami."
    ],
    pressQuote: "“El renacimiento del lujo dramático sobre la pasarela neoyorquina.”",
    youtubeUrl: "https://www.youtube.com/results?search_query=Idol+Jose+NYFW+2021+FDLA",
    image: "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?auto=format&fit=crop&w=1200&q=85"
  },
  {
    year: "2022",
    collection: "Metamorphosis Couture",
    location: "New York Fashion Week · Art Hearts Fashion",
    tags: ["NYFW SS/FW", "Art Hearts Fashion", "FDLA"],
    summary: "IDOL JOSE afianza su presencia doble en Nueva York desfilando en los escenarios de FDLA y Art Hearts Fashion con piezas de alto contraste y dramatismo teatral.",
    highlights: [
      "Pasarela estelar en Manhattan compartiendo cartel con los grandes exponentes del diseño internacional.",
      "Uso magistral de textiles metálicos, organzas estructuradas y capas imperiales.",
      "Cobertura destacada en Gotham Geek Girl, SavFaire y medios especializados de EE. UU."
    ],
    pressQuote: "“Cada salida de Idol José es una obra de arte performática que electrifica la sala.” — NYFW Review",
    youtubeUrl: "https://www.youtube.com/results?search_query=Idol+Jose+NYFW+2022",
    image: "https://images.unsplash.com/photo-1558769132-cb1aea458c5e?auto=format&fit=crop&w=1200&q=85"
  },
  {
    year: "2023",
    collection: "Sovereign Draping & West Coast Expansion",
    location: "New York Fashion Week · Los Angeles Fashion Week (LAFW)",
    tags: ["LAFW", "NYFW", "Gender-Fluid Couture"],
    summary: "La firma conquista la Costa Oeste en Los Angeles Fashion Week (LAFW) mientras mantiene su trono en NYFW, vistiendo a celebridades y redefiniendo la etiqueta de alfombra roja.",
    highlights: [
      "Debut triunfal en Los Angeles Fashion Week junto a Art Hearts Fashion.",
      "Evolución del concepto 'Universal Couture Fit': prendas envolventes que se ajustan con caída perfecta.",
      "Sesiones editoriales en Beverly Hills y el Distrito de la Moda de Manhattan."
    ],
    pressQuote: "“De Nueva York a Los Ángeles, los 'Fashion Doctors' imponen una estética imperial inconfundible.”",
    youtubeUrl: "https://www.youtube.com/results?search_query=Idol+Jose+LAFW+NYFW+2023",
    image: "https://images.unsplash.com/photo-1483985988355-763728e1935b?auto=format&fit=crop&w=1200&q=85"
  },
  {
    year: "2024",
    collection: "Anatomía del Lujo — Couture & Ready-to-Wear",
    location: "Manhattan, NY · Miami Design District",
    tags: ["Haute Couture", "SavFaire Feature", "Casting Inclusivo"],
    summary: "Aclamación crítica por la fusión entre Ready-to-Wear de lujo y Alta Costura dramática, destacando por su casting diverso, siluetas sin género y maestría artesanal.",
    highlights: [
      "Reportajes de fondo en SavFaire Magazine y Apparel Textile Sourcing.",
      "Presentación de colecciones Primavera/Verano y Otoño/Invierno en el corazón de Manhattan.",
      "Apertura de experiencias privadas de Atelier y Bootcamps de pasarela."
    ],
    pressQuote: "“Idol José desdibuja la línea entre la alta costura, el arte performático y el lujo contemporáneo.” — SavFaire",
    youtubeUrl: "https://www.youtube.com/results?search_query=Idol+Jose+NYFW+2024+Art+Hearts+Fashion",
    image: "https://images.unsplash.com/photo-1502716119720-b23a93e5fe1b?auto=format&fit=crop&w=1200&q=85"
  },
  {
    year: "2025",
    collection: "Monolith & Silk Architecture",
    location: "New York · Los Angeles · París / Miami",
    tags: ["Década de Legado", "Colección Cápsula", "Atelier Privado"],
    summary: "Celebrando casi una década de trayectoria internacional, la firma perfecciona su línea de piezas de autor listas para envío global con logística automatizada desde Estados Unidos.",
    highlights: [
      "Consolidación de IDOL JOSE GROUP como ecosistema de moda, dirección creativa y formación.",
      "Nuevas cápsulas de draping escultural diseñadas para compra directa e inmediata.",
      "Participación estelar en las galas de moda más exclusivas del continente."
    ],
    pressQuote: "“Madurez creativa absoluta: minimalismo monumental y opulencia medida al milímetro.”",
    youtubeUrl: "https://www.youtube.com/results?search_query=Idol+Jose+Fashion+Week+2025",
    image: "https://images.unsplash.com/photo-1512436991641-6745cdb1723f?auto=format&fit=crop&w=1200&q=85"
  },
  {
    year: "2026",
    collection: "L'Ère Souveraine — Digital Flagship & Global Atelier",
    location: "Global Flagship · NYFW · Miami",
    tags: ["Colección Actual 2026", "E-Commerce de Autor", "Runway Bootcamps"],
    summary: "Lanzamiento de la nueva casa digital oficial idoljoseofficial.com junto a la colección 2026: siluetas arquitectónicas, tejidos de caída hipnótica y conexión directa entre la pasarela y el coleccionista.",
    highlights: [
      "Inauguración de la Boutique Digital de Alta Gama con piezas en Talla Universal y Sastrería de Autor.",
      "Calendario oficial de desfiles 2026/2027 y Bootcamps intensivos de pasarela y estilismo.",
      "Integración multimedia de alta velocidad para prensa, compradores VIP y seguidores globales."
    ],
    pressQuote: "“El futuro de la alta costura latinoamericana tiene nombre propio: IDOL JOSE.”",
    youtubeUrl: "https://www.youtube.com/results?search_query=Idol+Jose+Official+Runway",
    image: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=1200&q=85"
  }
];

/* --------------------------------------------------------------------------
   2. INITIAL EDITORIAL GALLERY DATA (MODULE 2)
   -------------------------------------------------------------------------- */
const DEFAULT_GALLERY_ITEMS = [
  {
    id: "ed-dfwm-14",
    title: "Doral Fashion Week Magazine — Portada Oficial Sthefany Gutiérrez",
    category: "press",
    categoryLabel: "Prensa & Revista Oficial",
    season: "Gran Lanzamiento Oficial · Doral, FL",
    photographer: "Doral Fashion Week Magazine (@doralfwmagazine)",
    image: "assets/dfwm-portada-sthefany.jpg",
    description: "Gala y pasarela oficial de Doral Fashion Week Magazine con portada de Sthefany Gutiérrez, rueda de prensa y desfiles exclusivos en Doral, Florida."
  },
  {
    id: "ed-1",
    title: "Silueta Imperial en Seda Obsidiana",
    category: "runway",
    categoryLabel: "NYFW Runway",
    season: "NYFW Autumn/Winter · Manhattan",
    photographer: "Dirección Creativa IDOL JOSE",
    image: "https://images.unsplash.com/photo-1509631179647-0177331693ae?auto=format&fit=crop&w=1200&q=85",
    description: "Capa estructural en crepé de seda y organza negra con hombreras anatómicas presentadas en la Semana de la Moda de Nueva York."
  },
  {
    id: "ed-2",
    title: "Draping Escultórico Oro Líquido",
    category: "editorial",
    categoryLabel: "Campaña Editorial",
    season: "Colección Sovereign · Miami Design District",
    photographer: "Editorial Studio NY",
    image: "https://images.unsplash.com/photo-1539109136881-3be0616acf4b?auto=format&fit=crop&w=1200&q=85",
    description: "Construcción sin costuras visibles que abraza la figura mediante pliegues asimétricos inspirados en la anatomía clásica."
  },
  {
    id: "ed-3",
    title: "Backstage & Fitting de Alta Costura",
    category: "backstage",
    categoryLabel: "Backstage & Atelier",
    season: "FDLA Showcase · New York",
    photographer: "Archivo Oficial IDOL JOSE",
    image: "https://images.unsplash.com/photo-1469334031218-e382a71b716b?auto=format&fit=crop&w=1200&q=85",
    description: "Últimos ajustes de precisión segundos antes de la salida a pasarela en Manhattan por los Dres. Idolfredo Hernández y Juan Francisco Cabello."
  },
  {
    id: "ed-4",
    title: "Sastrería Avant-Garde Sin Género",
    category: "runway",
    categoryLabel: "NYFW Runway",
    season: "Art Hearts Fashion · LAFW & NYFW",
    photographer: "Runway Press Official",
    image: "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=1200&q=85",
    description: "Solapas geométricas de corte quirúrgico combinadas con texturas ricas y caída fluida."
  },
  {
    id: "ed-5",
    title: "Crónicas de Alfombra Roja & Prensa",
    category: "press",
    categoryLabel: "Press & Red Carpet",
    season: "SavFaire & FDLA Gala",
    photographer: "International Press",
    image: "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?auto=format&fit=crop&w=1200&q=85",
    description: "Presencia escénica y cobertura mediática internacional de las piezas insignia de la firma."
  },
  {
    id: "ed-6",
    title: "Monolito en Marfil & Plisado Artesanal",
    category: "editorial",
    categoryLabel: "Campaña Editorial",
    season: "Atelier Privado · Colección 2026",
    photographer: "Dirección Creativa IDOL JOSE",
    image: "https://images.unsplash.com/photo-1502716119720-b23a93e5fe1b?auto=format&fit=crop&w=1200&q=85",
    description: "Estudio de luz y volumen sobre tejidos nobles con caída arquitectónica de talla universal."
  }
];

/* --------------------------------------------------------------------------
   3. INITIAL UPCOMING EVENTS & RUNWAY CALENDAR (MODULE 3)
   -------------------------------------------------------------------------- */
const DEFAULT_EVENTS = [
  {
    id: "ev-1",
    day: "14",
    monthYear: "FEB · 2027",
    title: "New York Fashion Week — Sovereign Couture Showcase",
    type: "Pasarela Oficial NYFW",
    location: "Manhattan, New York · FDLA / Art Hearts Venue",
    time: "19:30 EST · Front Row & Press Check-in",
    ticketPrice: "RSVP / VIP Pass $250",
    ticketUrl: "#rsvp",
    description: "Presentación mundial de la nueva colección Otoño/Invierno de IDOL JOSE con acceso exclusivo a prensa, compradores e invitados VIP."
  },
  {
    id: "ev-2",
    day: "28",
    monthYear: "MAR · 2027",
    title: "IDOL JOSE Runway & High-Fashion Bootcamp",
    type: "Bootcamp & Masterclass",
    location: "Miami Design District, FL",
    time: "10:00 EST · Jornada Intensiva Presencial",
    ticketPrice: "Inscripción $380",
    ticketUrl: "#rsvp",
    description: "Entrenamiento intensivo de proyección escénica, pasarela internacional, estilismo de alta costura y casting directo con la dirección creativa de IDOL JOSE."
  },
  {
    id: "ev-3",
    day: "19",
    monthYear: "MAY · 2027",
    title: "Gala Privada Trunk Show & Atelier Fitting",
    type: "Gala & Trunk Show",
    location: "Beverly Hills, Los Ángeles, CA",
    time: "20:00 PST · Cocktail & Private Acquisition",
    ticketPrice: "Acceso con Invitación",
    ticketUrl: "#rsvp",
    description: "Exhibición íntima de piezas únicas de archivo y adquisición directa con ajuste personalizado por los fundadores de la firma."
  }
];

/* --------------------------------------------------------------------------
   4. HAUTE COUTURE E-COMMERCE CATALOG (MODULE 4)
   -------------------------------------------------------------------------- */
const DEFAULT_PRODUCTS = [
  {
    id: "prod-1",
    name: "Capa Escultórica 'L'Obsidienne' Draping",
    silhouette: "Architectural Draping · Pieza de Autor",
    price: 1280,
    weightLb: 2.4, // Peso asignado para cotización USPS/UPS/FedEx en tiempo real
    universalSize: true,
    sizes: ["Talla Única / Universal (Draping Fit)", "Bespoke / A Medida"],
    defaultSize: "Talla Única / Universal (Draping Fit)",
    fabric: "Crepé pesado de seda italiana y forro de satén fluido.",
    description: "Diseñada bajo principios de proporción anatómica, esta capa envolvente prescinde de tallajes rígidos para adaptarse con caída majestuosa a cualquier silueta.",
    images: [
      "https://images.unsplash.com/photo-1509631179647-0177331693ae?auto=format&fit=crop&w=1000&q=85",
      "https://images.unsplash.com/photo-1539109136881-3be0616acf4b?auto=format&fit=crop&w=1000&q=85",
      "https://images.unsplash.com/photo-1469334031218-e382a71b716b?auto=format&fit=crop&w=1000&q=85"
    ],
    motionVideoUrl: "https://assets.mixkit.co/videos/preview/mixkit-fashion-model-posing-in-neon-light-39877-large.mp4"
  },
  {
    id: "prod-2",
    name: "Túnica Asimétrica 'Attraction' en Seda Champagne",
    silhouette: "Fluid Haute Draping · Talla Universal",
    price: 960,
    weightLb: 1.5,
    universalSize: true,
    sizes: ["Talla Única / Universal (Draping Fit)"],
    defaultSize: "Talla Única / Universal (Draping Fit)",
    fabric: "Charmeuse de seda natural con plisado diagonal hecho a mano.",
    description: "Pieza icónica de movimiento hipnótico. Su sistema de lazos internos invisibles permite modular el escote y el ajuste en cintura sin restricciones de talla.",
    images: [
      "https://images.unsplash.com/photo-1539109136881-3be0616acf4b?auto=format&fit=crop&w=1000&q=85",
      "https://images.unsplash.com/photo-1502716119720-b23a93e5fe1b?auto=format&fit=crop&w=1000&q=85"
    ],
    motionVideoUrl: "https://assets.mixkit.co/videos/preview/mixkit-woman-modeling-a-long-black-dress-41731-large.mp4"
  },
  {
    id: "prod-3",
    name: "Kaftán Estructural 'Sovereign' Negro & Oro",
    silhouette: "Statement Silhouette · Talla Universal",
    price: 1450,
    weightLb: 2.8,
    universalSize: true,
    sizes: ["Talla Única / Universal (Draping Fit)", "Bespoke / A Medida"],
    defaultSize: "Talla Única / Universal (Draping Fit)",
    fabric: "Brocado metálico tejido en telar y organza de seda.",
    description: "Volumen monumental y ligereza extrema. Una creación concebida para galas, alfombras rojas y coleccionistas de indumentaria de autor.",
    images: [
      "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=1000&q=85",
      "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?auto=format&fit=crop&w=1000&q=85"
    ],
    motionVideoUrl: "https://assets.mixkit.co/videos/preview/mixkit-fashion-model-posing-in-neon-light-39877-large.mp4"
  },
  {
    id: "prod-4",
    name: "Blazer Arquitectónico 'Bisturí' de Hombro Extendido",
    silhouette: "Sastrería Estructurada · Edición Limitada",
    price: 1620,
    weightLb: 3.1,
    universalSize: false,
    sizes: ["Talla Única / Universal (Oversized Couture)", "S / M (Tailored)", "L / XL (Tailored)", "Bespoke / A Medida"],
    defaultSize: "Talla Única / Universal (Oversized Couture)",
    fabric: "Lana virgen fría 120s con entretela de sastrería artesanal y solapa en raso.",
    description: "El sello de 'The Fashion Doctors': precisión quirúrgica en cada costura, hombreras esculturales y caída impecable.",
    images: [
      "https://images.unsplash.com/photo-1502716119720-b23a93e5fe1b?auto=format&fit=crop&w=1000&q=85",
      "https://images.unsplash.com/photo-1509631179647-0177331693ae?auto=format&fit=crop&w=1000&q=85"
    ],
    motionVideoUrl: "https://assets.mixkit.co/videos/preview/mixkit-woman-modeling-a-long-black-dress-41731-large.mp4"
  }
];

/* --------------------------------------------------------------------------
   STATE MANAGEMENT & LOCAL STORAGE PERSISTENCE
   -------------------------------------------------------------------------- */
const state = {
  selectedYear: "2026",
  galleryFilter: "all",
  gallery: JSON.parse(localStorage.getItem("idoljose_gallery_v3")) || DEFAULT_GALLERY_ITEMS,
  events: JSON.parse(localStorage.getItem("idoljose_events")) || DEFAULT_EVENTS,
  products: JSON.parse(localStorage.getItem("idoljose_products")) || DEFAULT_PRODUCTS,
  cart: JSON.parse(localStorage.getItem("idoljose_cart")) || [],
  selectedSizes: {},
  shipping: {
    country: "US",
    zipCode: "10001",
    carrier: "usps_priority",
    rates: []
  }
};

function saveState() {
  localStorage.setItem("idoljose_gallery_v3", JSON.stringify(state.gallery));
  localStorage.setItem("idoljose_events", JSON.stringify(state.events));
  localStorage.setItem("idoljose_products", JSON.stringify(state.products));
  localStorage.setItem("idoljose_cart", JSON.stringify(state.cart));
}

window.submitOfficialLead = function (event) {
  event.preventDefault();
  const form = event.target;
  const lead = {
    source: "idoljoseofficial.com",
    fullName: form.fullName.value.trim(),
    phone: form.phone.value.trim(),
    email: form.email.value.trim(),
    reason: form.reason.value,
    notes: form.notes.value.trim(),
    createdAt: new Date().toISOString()
  };
  const leads = JSON.parse(localStorage.getItem("idoljose_crm_leads") || "[]");
  leads.unshift(lead);
  localStorage.setItem("idoljose_crm_leads", JSON.stringify(leads));
  form.reset();
  showToast("✓ Registro guardado. Conectando con el Atelier por WhatsApp...");
  const waText = encodeURIComponent(
    `Hola IDOL JOSE, acabo de registrarme en idoljoseofficial.com:\n\n• Nombre/Marca: ${lead.fullName}\n• Teléfono: ${lead.phone}\n• Email: ${lead.email}\n• Motivo: ${lead.reason}\n• Detalles: ${lead.notes || "Solicitud de información"}`
  );
  window.open(`https://wa.me/${IDOL_JOSE_CONFIG.whatsappConcierge}?text=${waText}`, "_blank");
};

/* --------------------------------------------------------------------------
   FALLBACK FOR <dialog closedby="any"> IN SAFARI (Modern Web Guidance)
   -------------------------------------------------------------------------- */
function setupDialogLightDismissFallbacks() {
  const dialogs = document.querySelectorAll("dialog.luxury-dialog");
  dialogs.forEach((dialog) => {
    if (!("closedBy" in HTMLDialogElement.prototype)) {
      dialog.addEventListener("click", (event) => {
        if (event.target !== dialog) return;
        const rect = dialog.getBoundingClientRect();
        const isDialogContent =
          rect.top <= event.clientY &&
          event.clientY <= rect.top + rect.height &&
          rect.left <= event.clientX &&
          event.clientX <= rect.left + rect.width;
        if (isDialogContent) return;
        dialog.close();
      });
    }
  });
}

function showToast(message) {
  const toast = document.getElementById("luxuryToast");
  if (!toast) return;
  toast.textContent = message;
  toast.classList.add("visible");
  clearTimeout(window.__toastTimer);
  window.__toastTimer = setTimeout(() => {
    toast.classList.remove("visible");
  }, 3800);
}

/* --------------------------------------------------------------------------
   MODULE 1: RENDER INTERACTIVE TIMELINE (2017 - PRESENT)
   -------------------------------------------------------------------------- */
function renderTimeline() {
  const track = document.getElementById("yearSelectorTrack");
  const stage = document.getElementById("timelineActiveStage");
  const drawer = document.getElementById("fullChronologyDrawer");
  if (!track || !stage) return;

  track.innerHTML = TIMELINE_DATA.map(
    (item) => `
      <button type="button"
              class="year-pill-btn ${item.year === state.selectedYear ? "active" : ""}"
              onclick="selectTimelineYear('${item.year}')">
        ${item.year}
      </button>
    `
  ).join("");

  const current = TIMELINE_DATA.find((item) => item.year === state.selectedYear) || TIMELINE_DATA[TIMELINE_DATA.length - 1];

  stage.innerHTML = `
    <div class="timeline-stage-content">
      <div class="timeline-year-badge">${current.year}</div>
      <div class="timeline-tags">
        <span class="tag-chip">${current.location}</span>
        ${current.tags.map((t) => `<span class="tag-chip">${t}</span>`).join("")}
      </div>
      <h3 class="timeline-collection-title">${current.collection}</h3>
      <p style="color: var(--text-secondary); margin-bottom: 1rem;">${current.summary}</p>
      <ul class="timeline-highlights-list">
        ${current.highlights.map((h) => `<li>${h}</li>`).join("")}
      </ul>
      <p style="font-family: var(--font-serif); font-style: italic; font-size: 1.15rem; color: var(--accent-gold); margin-bottom: 1.5rem;">
        ${current.pressQuote}
      </p>
      <div style="display: flex; flex-wrap: wrap; gap: 0.85rem;">
        <a href="${current.youtubeUrl}" target="_blank" rel="noopener noreferrer" class="btn-luxury-primary">
          ▶ Ver Clips & Desfile en YouTube (${current.year})
        </a>
        <button type="button" class="btn-luxury-outline" onclick="toggleFullChronology()">
          Ver Índice Completo 2017–2026
        </button>
      </div>
    </div>
    <div class="timeline-media-card" onclick="window.open('${current.youtubeUrl}', '_blank')">
      <img src="${current.image}" alt="IDOL JOSE ${current.year} - ${current.collection}" loading="lazy" width="720" height="450" />
      <div class="video-play-overlay">
        <div class="play-circle-icon">▶</div>
        <span style="font-size: 0.72rem; letter-spacing: 0.2em; text-transform: uppercase;">
          Archivo Audiovisual · Pasarela & Backstage ${current.year}
        </span>
      </div>
    </div>
  `;

  if (drawer) {
    drawer.innerHTML = TIMELINE_DATA.map(
      (item) => `
        <div class="mini-year-card" onclick="selectTimelineYear('${item.year}')">
          <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:0.4rem;">
            <strong style="font-family:var(--font-serif); font-size:1.6rem; color:var(--accent-gold);">${item.year}</strong>
            <span style="font-size:0.68rem; text-transform:uppercase; letter-spacing:0.12em; color:var(--text-muted);">${item.location}</span>
          </div>
          <h4 style="font-family:var(--font-serif); font-size:1.15rem; margin-bottom:0.35rem;">${item.collection}</h4>
          <p style="font-size:0.8rem; color:var(--text-secondary);">${item.highlights[0]}</p>
        </div>
      `
    ).join("");
  }
}

window.selectTimelineYear = function (year) {
  state.selectedYear = year;
  renderTimeline();
};

window.toggleFullChronology = function () {
  const drawer = document.getElementById("fullChronologyDrawer");
  if (!drawer) return;
  drawer.classList.toggle("open");
};

/* --------------------------------------------------------------------------
   MODULE 2: RENDER EDITORIAL GALLERY & FULLSCREEN LIGHTBOX
   -------------------------------------------------------------------------- */
function renderGallery() {
  const grid = document.getElementById("editorialGalleryGrid");
  if (!grid) return;

  const filtered =
    state.galleryFilter === "all"
      ? state.gallery
      : state.gallery.filter((item) => item.category === state.galleryFilter);

  grid.innerHTML = filtered
    .map(
      (item) => `
      <article class="editorial-card" onclick="openLightbox('${item.id}')">
        <img src="${item.image}" alt="${item.title}" loading="lazy" width="600" height="750" />
        <div class="editorial-card-overlay">
          <span class="cat-tag">${item.categoryLabel}</span>
          <h3>${item.title}</h3>
          <p>${item.season}</p>
        </div>
      </article>
    `
    )
    .join("");
}

window.filterGallery = function (category, btnEl) {
  state.galleryFilter = category;
  document.querySelectorAll("#galleryFilterBar .filter-btn").forEach((b) => b.classList.remove("active"));
  if (btnEl) btnEl.classList.add("active");
  renderGallery();
};

window.openLightbox = function (itemId) {
  const item = state.gallery.find((g) => g.id === itemId);
  const dialog = document.getElementById("lightboxDialog");
  const content = document.getElementById("lightboxDialogContent");
  if (!item || !dialog || !content) return;

  const extraLinks = `
    ${item.pdfUrl ? `<a href="${item.pdfUrl}" target="_blank" rel="noopener" class="btn-luxury-primary" style="margin-bottom:0.65rem;">📄 Leer Artículo Completo (PDF 4 Páginas)</a>` : ""}
    ${item.videoUrl ? `<a href="${item.videoUrl}" target="_blank" rel="noopener" class="btn-luxury-outline" style="margin-bottom:0.65rem;">🎬 Ver Video Revista Impresa DFWM</a>` : ""}
  `;

  content.innerHTML = `
    <div class="modal-split-grid">
      <div style="background:#000; border:1px solid var(--border-subtle); max-height:72dvh; overflow:hidden; display:grid; place-items:center;">
        <img src="${item.image}" alt="${item.title}" style="max-height:72dvh; width:auto; object-fit:contain;" />
      </div>
      <div>
        <span class="section-eyebrow">${item.categoryLabel}</span>
        <h3 style="font-family:var(--font-serif); font-size:2.2rem; margin-bottom:0.75rem;">${item.title}</h3>
        <p style="color:var(--accent-gold); font-size:0.84rem; letter-spacing:0.12em; text-transform:uppercase; margin-bottom:1.25rem;">
          ${item.season} · ${item.photographer}
        </p>
        <p style="color:var(--text-secondary); margin-bottom:1.5rem; line-height:1.75;">
          ${item.description}
        </p>
        <div style="display:flex; flex-direction:column; gap:0.5rem;">
          ${extraLinks}
          <button type="button" class="btn-luxury-outline" onclick="document.getElementById('lightboxDialog').close()">
            Cerrar Vista Pantalla Completa
          </button>
        </div>
      </div>
    </div>
  `;
  dialog.showModal();
};

/* --------------------------------------------------------------------------
   MODULE 3: RENDER UPCOMING EVENTS & INSTAGRAM WEBHOOK AUTOMATION
   -------------------------------------------------------------------------- */
function renderEvents() {
  const list = document.getElementById("runwayEventsList");
  if (!list) return;

  list.innerHTML = state.events
    .map(
      (ev) => `
      <article class="runway-event-card">
        <div class="event-date-box">
          <span class="day">${ev.day}</span>
          <span class="month-year">${ev.monthYear}</span>
        </div>
        <div class="event-info">
          <span class="tag-chip" style="display:inline-block; margin-bottom:0.5rem;">${ev.type}</span>
          <h3>${ev.title}</h3>
          <div class="event-meta-row">
            <span>📍 ${ev.location}</span>
            <span>🕒 ${ev.time}</span>
            <span style="color:var(--accent-gold);">🎟 ${ev.ticketPrice}</span>
          </div>
          <p style="font-size:0.9rem; color:var(--text-secondary);">${ev.description}</p>
        </div>
        <div class="event-actions-col">
          <button type="button" class="btn-luxury-primary" style="justify-content:center;" onclick="openEventRsvp('${ev.id}')">
            Boletos / RSVP VIP
          </button>
          <a href="https://www.instagram.com/doralfashionweekoficial/" target="_blank" rel="noopener" class="btn-luxury-outline" style="justify-content:center; font-size:0.7rem; padding:0.65rem 1rem;">
            Ver en Instagram Oficial ↗
          </a>
        </div>
      </article>
    `
    )
    .join("");
}

window.openEventRsvp = function (eventId) {
  const ev = state.events.find((e) => e.id === eventId);
  if (!ev) return;
  const msg = encodeURIComponent(
    `Hola equipo IDOL JOSE, deseo solicitar acceso VIP / Boletos para el evento: "${ev.title}" (${ev.day} ${ev.monthYear} en ${ev.location}).`
  );
  window.open(`https://wa.me/${IDOL_JOSE_CONFIG.whatsappConcierge}?text=${msg}`, "_blank");
};

window.generateInstagramAnnouncement = async function (eventId) {
  const ev = state.events.find((e) => e.id === eventId);
  if (!ev) return;

  const caption = `✨ OFFICIAL RUNWAY ANNOUNCEMENT ✨\n\n${ev.title.toUpperCase()}\n📅 ${ev.day} ${ev.monthYear}\n📍 ${ev.location}\n🕒 ${ev.time}\n🎟 ${ev.ticketPrice}\n\n${ev.description}\n\nReserva tu acreditación y boletos en el link de nuestra biografía: https://idoljoseofficial.com/#eventos\n\n#IdolJose #IdolJoseOfficial #NYFW #HauteCouture #TheFashionDoctors #FDLA #LuxuryFashion`;

  const webhookUrl = localStorage.getItem("idoljose_ig_webhook") || IDOL_JOSE_CONFIG.instagramAutomationWebhook;
  let webhookStatus = "Modo directo (Copia automática de Press Kit para Instagram). Configura tu URL de Webhook Make/Zapier/n8n en el panel CMS para publicación 100% desatendida.";

  if (webhookUrl) {
    try {
      await fetch(webhookUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          source: "idoljoseofficial.com",
          action: "instagram_event_publish",
          event: ev,
          instagram_caption: caption,
          timestamp: new Date().toISOString()
        })
      });
      webhookStatus = "✅ Webhook disparado exitosamente hacia Make / Zapier / n8n para publicación automática en Instagram.";
    } catch (err) {
      webhookStatus = "⚠️ Se generó el anuncio oficial (verifica la URL del webhook en el panel CMS si deseas envío en segundo plano).";
    }
  }

  if (navigator.clipboard) {
    navigator.clipboard.writeText(caption).catch(() => {});
  }

  const dialog = document.getElementById("igAnnouncementDialog");
  const body = document.getElementById("igAnnouncementDialogBody");
  if (dialog && body) {
    body.innerHTML = `
      <div class="modal-split-grid">
        <div style="background:#070708; border:1px solid var(--accent-gold); padding:2.25rem; aspect-ratio:4/5; display:flex; flex-direction:column; justify-content:space-between; text-align:center;">
          <span style="font-size:0.68rem; letter-spacing:0.25em; color:var(--accent-gold); text-transform:uppercase;">
            IDOL JOSE GROUP · OFFICIAL NOTICE
          </span>
          <div>
            <div style="font-family:var(--font-serif); font-size:3.2rem; color:var(--accent-gold); line-height:1;">
              ${ev.day} ${ev.monthYear}
            </div>
            <h3 style="font-family:var(--font-serif); font-size:1.75rem; margin:1rem 0; color:#f6f4f0;">
              ${ev.title}
            </h3>
            <p style="font-size:0.8rem; color:#b5b2aa; letter-spacing:0.12em; text-transform:uppercase;">
              ${ev.location}
            </p>
          </div>
          <div style="border-top:1px solid rgba(255,255,255,0.15); padding-top:1rem; font-size:0.72rem; letter-spacing:0.2em; color:#f6f4f0;">
            IDOLJOSEOFFICIAL.COM
          </div>
        </div>
        <div>
          <p style="font-size:0.85rem; color:var(--accent-gold); margin-bottom:1rem;">${webhookStatus}</p>
          <label style="display:block; font-size:0.72rem; letter-spacing:0.15em; text-transform:uppercase; margin-bottom:0.5rem;">
            Copy Oficial Generado (Copiado al Portapapeles):
          </label>
          <textarea class="luxury-textarea" rows="11" readonly>${caption}</textarea>
          <div style="display:flex; gap:0.75rem; margin-top:1rem; flex-wrap:wrap;">
            <button type="button" class="btn-luxury-primary" onclick="navigator.clipboard.writeText(this.parentElement.previousElementSibling.value); showToast('Copy copiado al portapapeles');">
              Copiar Texto para Instagram
            </button>
            <button type="button" class="btn-luxury-outline" onclick="document.getElementById('igAnnouncementDialog').close(); openCmsModal('events');">
              Configurar Webhook Make / Zapier / n8n
            </button>
          </div>
        </div>
      </div>
    `;
    dialog.showModal();
  }
};

/* --------------------------------------------------------------------------
   MODULE 4: RENDER HAUTE COUTURE E-COMMERCE & REAL-TIME CARRIER SHIPPING
   -------------------------------------------------------------------------- */
function renderCatalog() {
  const grid = document.getElementById("coutureCatalogGrid");
  if (!grid) return;

  grid.innerHTML = state.products
    .map((prod) => {
      const currentSize = state.selectedSizes[prod.id] || prod.defaultSize;
      return `
        <article class="product-luxury-card">
          <div class="product-media-wrap" onclick="openProductDetailModal('${prod.id}')">
            <img src="${prod.images[0]}" alt="${prod.name}" loading="lazy" width="600" height="800" />
            <div class="product-pill-badges">
              <span class="badge-couture">${prod.universalSize ? "Talla Única / Universal" : "Sastrería de Autor"}</span>
              <span class="badge-couture">🎬 Micro-Video + Fotos</span>
            </div>
          </div>
          <div class="product-body">
            <span class="product-silhouette-type">${prod.silhouette}</span>
            <div class="product-title-row">
              <h3>${prod.name}</h3>
              <span class="product-price">$${prod.price.toLocaleString("en-US")}</span>
            </div>
            <p class="product-desc">${prod.description}</p>

            <div class="size-selector-box">
              <div class="size-selector-label">
                <span>Configuración de Ajuste</span>
                <span>Peso Logístico: ${prod.weightLb} lb</span>
              </div>
              <div class="size-options-row">
                ${prod.sizes
                  .map(
                    (sz) => `
                  <button type="button"
                          class="size-chip ${sz === currentSize ? "active" : ""}"
                          onclick="selectProductSize('${prod.id}', '${sz}')">
                    ${sz}
                  </button>
                `
                  )
                  .join("")}
              </div>
            </div>

            <div class="product-actions-row">
              <button type="button" class="btn-luxury-primary" style="justify-content:center;" onclick="addToCart('${prod.id}')">
                Añadir a la Bolsa
              </button>
              <button type="button" class="btn-luxury-outline" style="padding:0.85rem 1rem;" onclick="openProductDetailModal('${prod.id}')" title="Ver Ficha Multimedia y Caída de Tela">
                Ver Caída / Detalle
              </button>
            </div>
          </div>
        </article>
      `;
    })
    .join("");
}

window.selectProductSize = function (productId, size) {
  state.selectedSizes[productId] = size;
  renderCatalog();
};

window.openProductDetailModal = function (productId) {
  const prod = state.products.find((p) => p.id === productId);
  const dialog = document.getElementById("productDetailDialog");
  const body = document.getElementById("productDetailDialogBody");
  if (!prod || !dialog || !body) return;

  const selectedSize = state.selectedSizes[prod.id] || prod.defaultSize;

  body.innerHTML = `
    <div class="modal-split-grid">
      <div>
        <div id="prodMainMediaStage" style="aspect-ratio:3/4; background:#000; border:1px solid var(--border-subtle); overflow:hidden; margin-bottom:0.85rem;">
          <img src="${prod.images[0]}" alt="${prod.name}" style="width:100%; height:100%; object-fit:cover;" />
        </div>
        <div style="display:flex; gap:0.65rem; overflow-x:auto;">
          ${prod.images
            .map(
              (imgUrl, idx) => `
            <button type="button"
                    style="width:76px; height:96px; border:1px solid var(--border-strong); overflow:hidden; flex-shrink:0;"
                    onclick="switchProductMediaStage('image', '${imgUrl}')">
              <img src="${imgUrl}" alt="Vista ${idx + 1}" style="width:100%; height:100%; object-fit:cover;" />
            </button>
          `
            )
            .join("")}
          <button type="button"
                  style="padding:0.75rem 1rem; border:1px solid var(--accent-gold); background:rgba(201,179,140,0.12); color:var(--accent-gold); font-size:0.72rem; letter-spacing:0.14em; text-transform:uppercase;"
                  onclick="switchProductMediaStage('video', '${prod.motionVideoUrl}')">
            ▶ Micro-Video Caída de Tela
          </button>
        </div>
      </div>
      <div>
        <span class="section-eyebrow">${prod.silhouette}</span>
        <h3 style="font-family:var(--font-serif); font-size:2.3rem; margin-bottom:0.5rem;">${prod.name}</h3>
        <div style="font-family:var(--font-display); font-size:1.5rem; color:var(--accent-gold); margin-bottom:1.25rem;">
          $${prod.price.toLocaleString("en-US")} USD
        </div>
        <p style="color:var(--text-secondary); margin-bottom:1.25rem; line-height:1.75;">${prod.description}</p>
        <div style="padding:1rem; border:1px solid var(--border-subtle); background:var(--bg-primary); margin-bottom:1.25rem; font-size:0.85rem;">
          <p><strong>Textil & Construcción:</strong> ${prod.fabric}</p>
          <p style="margin-top:0.4rem;"><strong>Ajuste Seleccionado:</strong> <span style="color:var(--accent-gold);">${selectedSize}</span></p>
          <p style="margin-top:0.4rem;"><strong>Peso Estimado Empaque Couture:</strong> ${prod.weightLb} lb (Cotización automática USPS / UPS / FedEx)</p>
        </div>
        <button type="button" class="btn-luxury-primary" style="width:100%; justify-content:center;" onclick="addToCart('${prod.id}'); document.getElementById('productDetailDialog').close();">
          Añadir a la Bolsa y Cotizar Envío (${selectedSize})
        </button>
      </div>
    </div>
  `;
  dialog.showModal();
};

window.switchProductMediaStage = function (type, url) {
  const stage = document.getElementById("prodMainMediaStage");
  if (!stage) return;
  if (type === "video") {
    stage.innerHTML = `
      <video src="${url}" autoplay loop muted playsinline controls style="width:100%; height:100%; object-fit:cover;"></video>
    `;
  } else {
    stage.innerHTML = `
      <img src="${url}" alt="Detalle de prenda" style="width:100%; height:100%; object-fit:cover;" />
    `;
  }
};

/* --------------------------------------------------------------------------
   CART & REAL-TIME CARRIER SHIPPING ALGORITHM (USPS / UPS / FEDEX)
   -------------------------------------------------------------------------- */
window.addToCart = function (productId) {
  const prod = state.products.find((p) => p.id === productId);
  if (!prod) return;
  const size = state.selectedSizes[prod.id] || prod.defaultSize;
  const existing = state.cart.find((item) => item.productId === productId && item.size === size);
  if (existing) {
    existing.qty += 1;
  } else {
    state.cart.push({
      productId: prod.id,
      name: prod.name,
      price: prod.price,
      weightLb: prod.weightLb,
      size,
      image: prod.images[0],
      qty: 1
    });
  }
  saveState();
  updateCartBadge();
  showToast(`Añadido a la bolsa: ${prod.name}`);
  openCartDialog();
};

window.removeFromCart = function (index) {
  state.cart.splice(index, 1);
  saveState();
  updateCartBadge();
  renderCartDialog();
};

function updateCartBadge() {
  const badge = document.getElementById("cartCountBadge");
  if (!badge) return;
  const totalQty = state.cart.reduce((acc, item) => acc + item.qty, 0);
  badge.textContent = totalQty;
}

/**
 * Real-time shipping rate algorithm based on total parcel weight (lbs)
 * and destination zone (US ZIP Code prefix from origin NY/Miami or International).
 */
function calculateRealTimeCarrierRates(totalWeightLb, country, zipCode) {
  if (totalWeightLb <= 0) return [];
  const cleanZip = (zipCode || "10001").trim();
  const firstDigit = parseInt(cleanZip.charAt(0), 10);

  // Zone factor (1.0 East Coast NY/FL -> 1.45 West Coast CA/WA -> 2.35 International)
  let zoneMultiplier = 1.15;
  let zoneLabel = "Zona Nacional EE. UU.";
  if (country !== "US") {
    zoneMultiplier = 2.4;
    zoneLabel = "Envío Internacional Express Asegurado";
  } else if (!isNaN(firstDigit)) {
    if ([0, 1, 2, 3].includes(firstDigit)) {
      zoneMultiplier = 1.0;
      zoneLabel = "Zona Costa Este EE. UU. (NY / FL Origin)";
    } else if ([4, 5, 6, 7].includes(firstDigit)) {
      zoneMultiplier = 1.22;
      zoneLabel = "Zona Central EE. UU.";
    } else {
      zoneMultiplier = 1.42;
      zoneLabel = "Zona Costa Oeste EE. UU. (CA / NV / WA)";
    }
  }

  const billableWeight = Math.max(1, totalWeightLb);

  const uspsRate = Math.round((14.5 + billableWeight * 4.2) * zoneMultiplier * 100) / 100;
  const upsRate = Math.round((22.0 + billableWeight * 5.6) * zoneMultiplier * 100) / 100;
  const fedexRate = Math.round((38.0 + billableWeight * 7.8) * zoneMultiplier * 100) / 100;

  return [
    {
      id: "usps_priority",
      carrier: "USPS Priority Mail® Insured",
      eta: country === "US" ? "2–4 días hábiles" : "6–9 días hábiles",
      zoneLabel,
      price: uspsRate
    },
    {
      id: "ups_2day",
      carrier: "UPS® 2nd Day Air / Couture Box",
      eta: country === "US" ? "2 días hábiles" : "4–5 días hábiles",
      zoneLabel,
      price: upsRate
    },
    {
      id: "fedex_overnight",
      carrier: "FedEx Priority Overnight® White-Glove",
      eta: country === "US" ? "Entrega al día siguiente" : "2–3 días hábiles VIP",
      zoneLabel,
      price: fedexRate
    }
  ];
}

window.openCartDialog = function () {
  const dialog = document.getElementById("cartCheckoutDialog");
  if (!dialog) return;
  renderCartDialog();
  dialog.showModal();
};

window.updateShippingInputs = function () {
  const countryEl = document.getElementById("shipCountrySelect");
  const zipEl = document.getElementById("shipZipInput");
  if (countryEl) state.shipping.country = countryEl.value;
  if (zipEl) state.shipping.zipCode = zipEl.value;
  renderCartDialog();
};

window.selectCarrierOption = function (carrierId) {
  state.shipping.carrier = carrierId;
  renderCartDialog();
};

function renderCartDialog() {
  const container = document.getElementById("cartDialogBody");
  if (!container) return;

  if (state.cart.length === 0) {
    container.innerHTML = `
      <div style="text-align:center; padding:3rem 1rem;">
        <h3 style="font-family:var(--font-serif); font-size:2rem; margin-bottom:0.75rem;">Tu Bolsa de Alta Costura está vacía</h3>
        <p style="color:var(--text-secondary); margin-bottom:1.5rem;">Explora las piezas de autor en Talla Universal o Sastrería Arquitectónica.</p>
        <button type="button" class="btn-luxury-primary" onclick="document.getElementById('cartCheckoutDialog').close()">
          Explorar Colección
        </button>
      </div>
    `;
    return;
  }

  const subtotal = state.cart.reduce((sum, item) => sum + item.price * item.qty, 0);
  const totalWeightLb = Number(
    state.cart.reduce((sum, item) => sum + item.weightLb * item.qty, 0).toFixed(2)
  );

  const rates = calculateRealTimeCarrierRates(
    totalWeightLb,
    state.shipping.country,
    state.shipping.zipCode
  );
  state.shipping.rates = rates;

  const activeRate = rates.find((r) => r.id === state.shipping.carrier) || rates[0];
  const shippingCost = activeRate ? activeRate.price : 0;
  const grandTotal = subtotal + shippingCost;

  container.innerHTML = `
    <div class="cart-layout-grid">
      <div>
        <h3 style="font-family:var(--font-serif); font-size:1.5rem; margin-bottom:1rem;">
          Piezas Seleccionadas (${state.cart.reduce((a, b) => a + b.qty, 0)})
        </h3>
        <div>
          ${state.cart
            .map(
              (item, idx) => `
            <div class="cart-item-row">
              <img src="${item.image}" alt="${item.name}" />
              <div>
                <h4 style="font-family:var(--font-serif); font-size:1.2rem;">${item.name}</h4>
                <p style="font-size:0.78rem; color:var(--accent-gold);">${item.size}</p>
                <p style="font-size:0.76rem; color:var(--text-muted);">
                  Cantidad: ${item.qty} · Peso: ${(item.weightLb * item.qty).toFixed(1)} lb
                </p>
              </div>
              <div style="text-align:right;">
                <div style="font-weight:700; margin-bottom:0.4rem;">$${(item.price * item.qty).toLocaleString("en-US")}</div>
                <button type="button" style="font-size:0.72rem; color:var(--danger); text-transform:uppercase; letter-spacing:0.1em;" onclick="removeFromCart(${idx})">
                  Eliminar
                </button>
              </div>
            </div>
          `
            )
            .join("")}
        </div>
      </div>

      <div class="shipping-calculator-box">
        <span class="section-eyebrow" style="margin-bottom:0.35rem;">Logística Automatizada en Tiempo Real</span>
        <h3 style="font-family:var(--font-serif); font-size:1.5rem; margin-bottom:1rem;">
          Cotizador USPS · UPS · FedEx
        </h3>

        <div class="form-grid-2">
          <div>
            <label style="font-size:0.7rem; text-transform:uppercase; letter-spacing:0.12em; color:var(--text-muted); display:block; margin-bottom:0.3rem;">
              País de Entrega
            </label>
            <select id="shipCountrySelect" class="luxury-select" onchange="updateShippingInputs()">
              <option value="US" ${state.shipping.country === "US" ? "selected" : ""}>Estados Unidos (US)</option>
              <option value="INTL" ${state.shipping.country === "INTL" ? "selected" : ""}>Internacional (Europa / Latam / Caribe)</option>
            </select>
          </div>
          <div>
            <label style="font-size:0.7rem; text-transform:uppercase; letter-spacing:0.12em; color:var(--text-muted); display:block; margin-bottom:0.3rem;">
              ZIP / Código Postal
            </label>
            <input id="shipZipInput" type="text" class="luxury-input" value="${state.shipping.zipCode}" placeholder="Ej. 10001 o 33137" oninput="updateShippingInputs()" />
          </div>
        </div>

        <p style="font-size:0.76rem; color:var(--text-secondary); margin-bottom:0.65rem;">
          Peso total calculado en carrito: <strong style="color:var(--accent-gold);">${totalWeightLb} lb</strong> · ${activeRate ? activeRate.zoneLabel : ""}
        </p>

        <div class="carrier-rates-list">
          ${rates
            .map(
              (r) => `
            <div class="carrier-option ${r.id === activeRate.id ? "selected" : ""}" onclick="selectCarrierOption('${r.id}')">
              <div>
                <strong style="font-size:0.86rem; display:block;">${r.carrier}</strong>
                <span style="font-size:0.74rem; color:var(--text-secondary);">Tiempo estimado: ${r.eta}</span>
              </div>
              <span style="font-family:var(--font-display); font-weight:700; color:var(--accent-gold);">
                $${r.price.toFixed(2)}
              </span>
            </div>
          `
            )
            .join("")}
        </div>

        <div style="border-top:1px solid var(--border-subtle); padding-top:1rem; margin-top:1rem; display:grid; gap:0.45rem; font-size:0.9rem;">
          <div style="display:flex; justify-content:space-between;">
            <span>Subtotal Prendas:</span>
            <span>$${subtotal.toLocaleString("en-US")}.00</span>
          </div>
          <div style="display:flex; justify-content:space-between;">
            <span>Flete (${activeRate ? activeRate.carrier : "Envío"}):</span>
            <span>$${shippingCost.toFixed(2)}</span>
          </div>
          <div style="display:flex; justify-content:space-between; font-size:1.15rem; font-weight:700; color:var(--accent-gold); padding-top:0.45rem; border-top:1px solid var(--border-subtle);">
            <span>Total a Pagar:</span>
            <span>$${grandTotal.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })} USD</span>
          </div>
        </div>

        <div style="display:grid; gap:0.65rem; margin-top:1.25rem;">
          <button type="button" class="btn-luxury-primary" style="width:100%; justify-content:center;" onclick="proceedToLuxuryCheckout('stripe')">
            💳 Pagar con Stripe / Apple Pay / Tarjeta
          </button>
          <button type="button" class="btn-luxury-outline" style="width:100%; justify-content:center; font-size:0.72rem;" onclick="proceedToLuxuryCheckout('concierge')">
            Solicitar Asistencia de Compra en Atelier VIP
          </button>
        </div>
      </div>
    </div>
  `;
}

window.proceedToLuxuryCheckout = function (method) {
  const subtotal = state.cart.reduce((sum, item) => sum + item.price * item.qty, 0);
  const totalWeightLb = Number(
    state.cart.reduce((sum, item) => sum + item.weightLb * item.qty, 0).toFixed(2)
  );
  const activeRate =
    state.shipping.rates.find((r) => r.id === state.shipping.carrier) || state.shipping.rates[0];
  const shippingCost = activeRate ? activeRate.price : 0;
  const grandTotal = subtotal + shippingCost;

  const customStripeUrl = localStorage.getItem("idoljose_stripe_url") || IDOL_JOSE_CONFIG.stripeCheckoutWebhook;
  if (method === "stripe" && customStripeUrl && customStripeUrl.startsWith("http")) {
    window.open(customStripeUrl, "_blank");
    return;
  }

  const summaryLines = state.cart
    .map((i) => `• ${i.qty}x ${i.name} (${i.size}) - $${i.price * i.qty}`)
    .join("\n");

  const message = encodeURIComponent(
    `✨ *ORDEN DE COMPRA OFICIAL — IDOL JOSE* ✨\n\n` +
      `*Prendas seleccionadas:*\n${summaryLines}\n\n` +
      `*Peso Logístico Total:* ${totalWeightLb} lb\n` +
      `*Destino:* ${state.shipping.country} (ZIP: ${state.shipping.zipCode})\n` +
      `*Paquetería Seleccionada:* ${activeRate ? activeRate.carrier : "USPS"} ($${shippingCost.toFixed(2)} USD)\n` +
      `*TOTAL ORDEN:* $${grandTotal.toFixed(2)} USD\n\n` +
      `Deseo completar el enlace directo de pago con Tarjeta / Apple Pay / Stripe.`
  );

  showToast("Generando orden segura con cálculo de flete incluido...");
  window.open(`https://wa.me/${IDOL_JOSE_CONFIG.whatsappConcierge}?text=${message}`, "_blank");
};

/* --------------------------------------------------------------------------
   CMS ATELIER STUDIO MODAL (ADD GALLERY, EVENTS, PRODUCTS & WEBHOOKS)
   -------------------------------------------------------------------------- */
window.openCmsModal = function () {
  const dialog = document.getElementById("cmsStudioDialog");
  if (!dialog) return;
  const savedIgWebhook = localStorage.getItem("idoljose_ig_webhook") || "";
  const savedStripeUrl = localStorage.getItem("idoljose_stripe_url") || "";
  const igInput = document.getElementById("cmsIgWebhookInput");
  const stripeInput = document.getElementById("cmsStripeUrlInput");
  if (igInput) igInput.value = savedIgWebhook;
  if (stripeInput) stripeInput.value = savedStripeUrl;
  dialog.showModal();
};

window.handleAddEditorialForm = function (event) {
  event.preventDefault();
  const form = event.target;
  const newItem = {
    id: "ed-" + Date.now(),
    title: form.title.value.trim(),
    category: form.category.value,
    categoryLabel: form.category.options[form.category.selectedIndex].text,
    season: form.season.value.trim(),
    photographer: form.photographer.value.trim() || "Dirección Creativa IDOL JOSE",
    image: form.image.value.trim(),
    description: form.description.value.trim()
  };
  state.gallery.unshift(newItem);
  saveState();
  renderGallery();
  form.reset();
  showToast("Nueva sesión editorial publicada en la galería.");
};

window.handleAddEventForm = async function (event) {
  event.preventDefault();
  const form = event.target;
  const newEv = {
    id: "ev-" + Date.now(),
    day: form.day.value.trim(),
    monthYear: form.monthYear.value.trim().toUpperCase(),
    title: form.title.value.trim(),
    type: form.type.value.trim(),
    location: form.location.value.trim(),
    time: form.time.value.trim(),
    ticketPrice: form.ticketPrice.value.trim(),
    ticketUrl: "#rsvp",
    description: form.description.value.trim()
  };
  state.events.unshift(newEv);
  saveState();
  renderEvents();
  form.reset();
  document.getElementById("cmsStudioDialog").close();
  showToast("Evento publicado en Calendario Runway. Generando difusión para Instagram...");
  setTimeout(() => {
    window.generateInstagramAnnouncement(newEv.id);
  }, 350);
};

window.handleSaveIntegrations = function (event) {
  event.preventDefault();
  const igWebhook = document.getElementById("cmsIgWebhookInput").value.trim();
  const stripeUrl = document.getElementById("cmsStripeUrlInput").value.trim();
  localStorage.setItem("idoljose_ig_webhook", igWebhook);
  localStorage.setItem("idoljose_stripe_url", stripeUrl);
  showToast("Integraciones de Webhook Instagram y Stripe actualizadas.");
};

/* --------------------------------------------------------------------------
   THEME TOGGLE (NOIR ATELIER / IVORY EDITORIAL)
   -------------------------------------------------------------------------- */
window.toggleAtelierTheme = function () {
  const htmlEl = document.documentElement;
  const current = htmlEl.getAttribute("data-theme") || "noir";
  const next = current === "ivory" ? "noir" : "ivory";
  htmlEl.setAttribute("data-theme", next);

  const logoImg = document.getElementById("headerBrandLogo");
  if (logoImg) {
    logoImg.src = next === "ivory" ? "assets/logo-light.png" : "assets/logo-dark.png";
  }
};

/* --------------------------------------------------------------------------
   INITIALIZATION
   -------------------------------------------------------------------------- */
document.addEventListener("DOMContentLoaded", () => {
  renderTimeline();
  renderGallery();
  renderEvents();
  renderCatalog();
  updateCartBadge();
  setupDialogLightDismissFallbacks();

  // Atajo privado exclusivo para Edward (Shift + Alt + A) para abrir el CMS Studio oculto
  document.addEventListener("keydown", (e) => {
    if (e.shiftKey && e.altKey && (e.key === "A" || e.key === "a")) {
      window.openCmsModal();
    }
  });
});


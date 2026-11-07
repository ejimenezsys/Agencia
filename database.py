import os
import re
import sqlite3
import hashlib
import hmac
import secrets
import json
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_PATH = os.environ.get("DATABASE_PATH", str(Path(__file__).parent / "prosper_ia.db"))
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

PASSWORD_SCHEME = "pbkdf2_sha256"
PASSWORD_ITERATIONS = 600_000


def hash_password(password: str) -> str:
    """Genera un hash PBKDF2 con sal aleatoria; nunca persiste texto plano."""
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, PASSWORD_ITERATIONS)
    return f"{PASSWORD_SCHEME}${PASSWORD_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        scheme, iterations, salt_hex, digest_hex = stored.split("$", 3)
        if scheme != PASSWORD_SCHEME:
            return False
        candidate = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), bytes.fromhex(salt_hex), int(iterations)
        )
        return hmac.compare_digest(candidate.hex(), digest_hex)
    except (AttributeError, TypeError, ValueError):
        return False


def normalize_phone_e164(phone: str) -> str:
    """Normaliza un teléfono a formato E.164 básico sin perder dígitos."""
    raw = (phone or "").strip()
    if not raw:
        return ""
    digits = re.sub(r"\D", "", raw)
    if not digits:
        return ""
    if raw.startswith("+"):
        return "+" + digits
    if len(digits) == 10:
        return "+1" + digits
    return "+" + digits


def normalize_email(email: str) -> str:
    return (email or "").strip().lower()


# Catálogo Oficial Versionado (Sección 2 del Brief Operativo)
OFFER_CATALOG = {
    "EXPRESS_497": {
        "code": "EXPRESS_497",
        "name": "Caja 1 · Sitio Web Inteligente Express (Oferta Principal)",
        "price": 497.0,
        "initial_payment": 250.0,
        "delivery_payment": 247.0,
        "payment_terms": "US$250 hoy (reserva 50%) + US$247 contra entrega en 7-10 días (Total: US$497 USD). Mes 1 de CRM incluido; desde mes 2 US$99/mes opcional.",
        "delivery_cost_estimate": 100.0,
        "requires_director_approval": False,
        "scope": "1 Sitio Web Inteligente sobre plantilla de su giro + Formulario Calificador + Punto de contacto y Asistente Digital 24/7 básico + Publicación y revisión."
    },
    "ANUAL_990": {
        "code": "ANUAL_990",
        "name": "Caja 2 · Pack Estrella Anual (Escalamiento Aprobado)",
        "price": 990.0,
        "initial_payment": 495.0,
        "delivery_payment": 495.0,
        "payment_terms": "US$495 hoy (50%) + US$495 contra entrega en 7-10 días (Total: US$990 USD/año). Incluye 12 meses de CRM y PassportAI + 2 Reels.",
        "delivery_cost_estimate": 150.0,
        "requires_director_approval": False,
        "scope": "Sitio Web Inteligente + Formulario + Asistente 24/7 + 12 meses de Tablero CRM + 12 meses PassportAI Business + 2 Reels editados."
    },
    "MAQUINA_1490": {
        "code": "MAQUINA_1490",
        "name": "Caja 3 · Máquina Completa 3 en 1 (Escalamiento Tráfico + Videos)",
        "price": 1490.0,
        "initial_payment": 745.0,
        "delivery_payment": 745.0,
        "payment_terms": "US$745 hoy (50%) + US$745 en el día 15 (Total: US$1,490 USD). No incluye presupuesto de pauta en Meta.",
        "delivery_cost_estimate": 300.0,
        "requires_director_approval": True,
        "scope": "Sitio Web Inteligente + Asistente + 10 Videos Cortos Editados + 1 Mes de Gestión de Campañas Meta Ads (pauta pagada por el cliente)."
    },
    "RESCATE_197": {
        "code": "RESCATE_197",
        "name": "Plan Rescate Micro-PYME (Último Recurso Autorizado)",
        "price": 197.0,
        "initial_payment": 100.0,
        "delivery_payment": 97.0,
        "payment_terms": "US$197 contado hoy o US$100 hoy + US$97 contra entrega en 5 días (Total: US$197 USD). Desde mes 2 US$49/mes.",
        "delivery_cost_estimate": 50.0,
        "requires_director_approval": False,
        "scope": "1 Landing Express sobre plantilla de su giro + Formulario + Botón/Asistente básico a WhatsApp."
    },
    "HISTORICO_CRM_1500": {
        "code": "HISTORICO_CRM_1500",
        "name": "Implementación Full Sistema Comercial / CRM (Oferta Histórica)",
        "price": 1500.0,
        "initial_payment": 750.0,
        "delivery_payment": 750.0,
        "payment_terms": "US$750 anticipo + US$750 contra entrega (Total: US$1,500 USD).",
        "delivery_cost_estimate": 300.0,
        "requires_director_approval": True,
        "scope": "Implementación completa de CRM omnicanal, pipelines y automatizaciones a medida."
    },
    "SVE90_CORP": {
        "code": "SVE90_CORP",
        "name": "Derivación Corporativa SVE90 / Cortexia (Solo con Dirección)",
        "price": 5000.0,
        "initial_payment": 2500.0,
        "delivery_payment": 2500.0,
        "payment_terms": "Requiere Sesión Ejecutiva y contrato con Dirección (US$2,500 a US$10,000 USD).",
        "delivery_cost_estimate": 1000.0,
        "requires_director_approval": True,
        "scope": "Transformación SVE90 en 90 días y Empleados Digitales Cortexia."
    },
}

CANONICAL_PIPELINE_STAGES = [
    "Lead identificado",
    "Primer contacto",
    "Conversación",
    "Calificado",
    "Diagnóstico agendado",
    "Demo realizada",
    "Propuesta enviada",
    "Pago pendiente",
    "Pago confirmado",
    "Implementación",
    "Entregado",
]

ALTERNATIVE_PIPELINE_STAGES = [
    "No interesado",
    "No responde",
    "No cumple perfil",
    "Opt-out",
    "Venta perdida",
    "Reembolso/contracargo",
]

ALL_PIPELINE_STAGES = CANONICAL_PIPELINE_STAGES + ALTERNATIVE_PIPELINE_STAGES


class User(Base):
    """Modelo ORM para usuarios del Sales Operating System (Admin, Supervisor, Vendedor, Operaciones)."""
    __tablename__ = "users"

    email = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    company = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    plan = Column(String, nullable=True)
    api_key = Column(String, nullable=True)
    # Campos Sales OS
    role = Column(String, default="seller", nullable=False)  # admin, supervisor, seller, operations
    dupla = Column(String, default="Dupla A — Clínicas", nullable=True)
    ghl_user_id = Column(String, nullable=True)
    is_active = Column(Integer, default=1, nullable=False)
    commission_rate = Column(Float, default=0.15, nullable=False)
    created_at = Column(String, nullable=True)


class Lead(Base):
    """Modelo ORM canónico para prospectos, oportunidades, cobros verificados, comisiones y entregas."""
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    company = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    status = Column(String, default="new", nullable=False)
    source = Column(String, default="website", nullable=False)
    score = Column(Integer, default=50, nullable=False)
    notes = Column(String, nullable=True)
    created_at = Column(String, nullable=False)

    # Campos canónicos del Sales Operating System (Sección 4 del Brief)
    contact_id = Column(String, nullable=True, index=True)          # ID estable en GHL
    ghl_opportunity_id = Column(String, nullable=True)              # ID de oportunidad en GHL
    full_name = Column(String, nullable=True)                       # Nombre completo separado
    business_name = Column(String, nullable=True)                   # Nombre de empresa separado
    phone_e164 = Column(String, nullable=True, index=True)          # Teléfono normalizado E.164
    source_channel = Column(String, default="Web", nullable=True)   # Web, Facebook, Instagram, Comunidad, Referencia, Outbound
    source_campaign = Column(String, default="", nullable=True)     # Reel/código/campaña específica
    interest_primary = Column(String, default="Sitio Web Inteligente", nullable=True)
    owner_id = Column(String, default="", nullable=True, index=True)   # Email del vendedor asignado
    setter_id = Column(String, default="", nullable=True)              # Email del setter
    niche = Column(String, default="clinica", nullable=True)           # Giro / segmento
    country = Column(String, default="Estados Unidos / LATAM", nullable=True)
    timezone = Column(String, default="America/New_York", nullable=True)
    contact_permission = Column(String, default="Formulario Web / Opt-in verificado", nullable=True)
    contact_status = Column(String, default="contactable", nullable=True)  # contactable, dnd, opt_out, bounce, unauthorized
    pipeline_stage = Column(String, default="Lead identificado", nullable=True)
    last_touch = Column(String, default="", nullable=True)
    next_action_at = Column(String, default="", nullable=True)
    next_action_note = Column(String, default="", nullable=True)
    offer_version = Column(String, default="EXPRESS_497", nullable=True)
    quoted_amount = Column(Float, default=0.0, nullable=True)          # Propuesta enviada (NO es cobro)
    contracted_amount = Column(Float, default=0.0, nullable=True)      # Valor total del contrato
    payment_plan = Column(String, default="50_50", nullable=True)      # 50_50 (US$250 + US$247) o 100_contado
    invoice_id = Column(String, default="", nullable=True)             # Comprobante / ID de transacción verificada
    amount_collected = Column(Float, default=0.0, nullable=True)       # Dinero REAL cobrado
    commission_base = Column(Float, default=0.0, nullable=True)        # Base sobre dinero cobrado
    commission_setter = Column(Float, default=0.0, nullable=True)      # 5% Setter
    commission_closer = Column(Float, default=0.0, nullable=True)      # 10% Closer
    commission_amount = Column(Float, default=0.0, nullable=True)      # 15% Total
    commission_status = Column(String, default="sin_devengar", nullable=True)  # sin_devengar, pendiente_verificacion, causada, pagada, anulada_reembolso
    delivery_cost_estimate = Column(Float, default=100.0, nullable=True)
    actual_delivery_cost = Column(Float, default=0.0, nullable=True)
    site_delivery_status = Column(String, default="pendiente_pago", nullable=True)  # pendiente_pago, onboarding, construccion, qa, entregado
    selected_template = Column(String, default="clinica_dental_estetica", nullable=True)
    demo_config_json = Column(String, default="{}", nullable=True)


class AuditLog(Base):
    """Historial inmutable de auditoría de cambios en precios, etapas, propietarios, cobros y comisiones."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(String, nullable=False, index=True)
    actor_email = Column(String, nullable=False, index=True)
    actor_role = Column(String, nullable=False)
    lead_id = Column(Integer, nullable=True, index=True)
    action = Column(String, nullable=False)
    field_changed = Column(String, nullable=True)
    old_value = Column(String, nullable=True)
    new_value = Column(String, nullable=True)
    notes = Column(String, nullable=True)


class DndExclusion(Base):
    """Lista compartida de exclusión Do-Not-Contact (DND / Opt-out / Exclusión Estratégica)."""
    __tablename__ = "dnd_exclusions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, nullable=True, index=True)
    phone_e164 = Column(String, nullable=True, index=True)
    company = Column(String, nullable=True)
    reason = Column(String, nullable=False)
    source = Column(String, default="blacklist_oficial", nullable=False)
    created_at = Column(String, nullable=False)


class SessionModel(Base):
    """Modelo ORM para almacenar tokens de sesión activos."""
    __tablename__ = "sessions"

    token = Column(String, primary_key=True, index=True)
    email = Column(String, nullable=False)
    created_at = Column(String, nullable=False)


class BlogPost(Base):
    """Modelo ORM para almacenar artículos de blog del sistema."""
    __tablename__ = "blog_posts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    slug = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    category = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    content = Column(String, nullable=False)
    image_url = Column(String, nullable=False)
    published_at = Column(String, nullable=False)
    author = Column(String, nullable=False)


class IntegrationSetting(Base):
    """Modelo ORM para almacenar configuraciones de integración (GHL, n8n, etc.)."""
    __tablename__ = "integration_settings"

    key = Column(String, primary_key=True, index=True)
    value = Column(String, nullable=True)


class ArsenalPrompt(Base):
    """Modelo ORM para almacenar prompts indexados de la biblioteca El Arsenal (+5,000 Prompts)."""
    __tablename__ = "arsenal_prompts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)
    model = Column(String, nullable=False, index=True)
    tags = Column(String, nullable=True)
    prompt = Column(String, nullable=False)
    negative_prompt = Column(String, nullable=True)
    aspect_ratio = Column(String, nullable=True)
    lens = Column(String, nullable=True)
    lighting = Column(String, nullable=True)
    style = Column(String, nullable=True)
    thumbnail_url = Column(String, nullable=True)
    badge = Column(String, nullable=True)
    views_count = Column(Integer, default=0)
    created_at = Column(String, nullable=False)


def _run_safe_migrations():
    """Añade columnas nuevas a tablas SQLite existentes sin borrar ni alterar datos históricos."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        existing_user_cols = {r[1] for r in cur.execute("PRAGMA table_info(users)").fetchall()}
        user_migrations = [
            ("role", "TEXT DEFAULT 'seller'"),
            ("dupla", "TEXT DEFAULT 'Dupla A — Clínicas'"),
            ("ghl_user_id", "TEXT DEFAULT ''"),
            ("is_active", "INTEGER DEFAULT 1"),
            ("commission_rate", "REAL DEFAULT 0.15"),
            ("created_at", "TEXT DEFAULT ''"),
        ]
        for col_name, col_def in user_migrations:
            if col_name not in existing_user_cols:
                cur.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_def}")

        existing_lead_cols = {r[1] for r in cur.execute("PRAGMA table_info(leads)").fetchall()}
        lead_migrations = [
            ("contact_id", "TEXT DEFAULT ''"),
            ("ghl_opportunity_id", "TEXT DEFAULT ''"),
            ("full_name", "TEXT DEFAULT ''"),
            ("business_name", "TEXT DEFAULT ''"),
            ("phone_e164", "TEXT DEFAULT ''"),
            ("source_channel", "TEXT DEFAULT 'Web'"),
            ("source_campaign", "TEXT DEFAULT ''"),
            ("interest_primary", "TEXT DEFAULT 'Sitio Web Inteligente'"),
            ("owner_id", "TEXT DEFAULT ''"),
            ("setter_id", "TEXT DEFAULT ''"),
            ("niche", "TEXT DEFAULT 'clinica'"),
            ("country", "TEXT DEFAULT 'Estados Unidos / LATAM'"),
            ("timezone", "TEXT DEFAULT 'America/New_York'"),
            ("contact_permission", "TEXT DEFAULT 'Formulario Web / Opt-in verificado'"),
            ("contact_status", "TEXT DEFAULT 'contactable'"),
            ("pipeline_stage", "TEXT DEFAULT 'Lead identificado'"),
            ("last_touch", "TEXT DEFAULT ''"),
            ("next_action_at", "TEXT DEFAULT ''"),
            ("next_action_note", "TEXT DEFAULT ''"),
            ("offer_version", "TEXT DEFAULT 'EXPRESS_497'"),
            ("quoted_amount", "REAL DEFAULT 0.0"),
            ("contracted_amount", "REAL DEFAULT 0.0"),
            ("payment_plan", "TEXT DEFAULT '50_50'"),
            ("invoice_id", "TEXT DEFAULT ''"),
            ("amount_collected", "REAL DEFAULT 0.0"),
            ("commission_base", "REAL DEFAULT 0.0"),
            ("commission_setter", "REAL DEFAULT 0.0"),
            ("commission_closer", "REAL DEFAULT 0.0"),
            ("commission_amount", "REAL DEFAULT 0.0"),
            ("commission_status", "TEXT DEFAULT 'sin_devengar'"),
            ("delivery_cost_estimate", "REAL DEFAULT 100.0"),
            ("actual_delivery_cost", "REAL DEFAULT 0.0"),
            ("site_delivery_status", "TEXT DEFAULT 'pendiente_pago'"),
            ("selected_template", "TEXT DEFAULT 'clinica_dental_estetica'"),
            ("demo_config_json", "TEXT DEFAULT '{}'"),
        ]
        for col_name, col_def in lead_migrations:
            if col_name not in existing_lead_cols:
                cur.execute(f"ALTER TABLE leads ADD COLUMN {col_name} {col_def}")

        # Normalizar campos derivados en leads históricos sin tocar sus valores originales
        cur.execute("""
            UPDATE leads
            SET full_name = COALESCE(NULLIF(full_name, ''), name),
                business_name = COALESCE(NULLIF(business_name, ''), company)
            WHERE full_name IS NULL OR full_name = ''
        """)

        # Mapear status antiguo a pipeline_stage solo si sigue en el default y tenía otro estado
        cur.execute("""
            UPDATE leads
            SET pipeline_stage = CASE
                WHEN status = 'contacted' THEN 'Primer contacto'
                WHEN status = 'qualified' THEN 'Calificado'
                WHEN status = 'converted' THEN 'Propuesta enviada'
                WHEN status = 'lost' THEN 'Venta perdida'
                ELSE 'Lead identificado'
            END
            WHERE pipeline_stage IS NULL OR pipeline_stage = ''
        """)

        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"⚠️ [MIGRATION] Warning in _run_safe_migrations: {e}", flush=True)
    finally:
        conn.close()


INITIAL_SALES_TEAM = [
    {
        "email": "supervisor@agenciaprosperia.com",
        "name": "Supervisor Comercial ProsperIA",
        "role": "supervisor",
        "dupla": "Supervisión General (Duplas A, B y C)",
        "phone": "+17865573119",
        "plan": "enterprise",
        "default_pass": "ProsperSupervisor2026!"
    },
    {
        "email": "operaciones@agenciaprosperia.com",
        "name": "Equipo Ingeniería UBA — Operaciones & Entregas",
        "role": "operations",
        "dupla": "Operaciones & QA (10 Ingenieros)",
        "phone": "+5491100000000",
        "plan": "enterprise",
        "default_pass": "ProsperOps2026!"
    },
    {
        "email": "closer1@agenciaprosperia.com",
        "name": "Vendedor 1 · Dupla A (Clínicas)",
        "role": "seller",
        "dupla": "Dupla A — Clínicas (Dental, Estética y Capilar)",
        "phone": "+5491100000001",
        "plan": "closer_web",
        "default_pass": "Closer1Prosper2026!"
    },
    {
        "email": "closer2@agenciaprosperia.com",
        "name": "Vendedor 2 · Dupla A (Clínicas)",
        "role": "seller",
        "dupla": "Dupla A — Clínicas (Dental, Estética y Capilar)",
        "phone": "+5491100000002",
        "plan": "closer_web",
        "default_pass": "Closer2Prosper2026!"
    },
    {
        "email": "closer3@agenciaprosperia.com",
        "name": "Vendedor 3 · Dupla B (Servicios Locales)",
        "role": "seller",
        "dupla": "Dupla B — Servicios Locales & Agenda",
        "phone": "+5491100000003",
        "plan": "closer_web",
        "default_pass": "Closer3Prosper2026!"
    },
    {
        "email": "closer4@agenciaprosperia.com",
        "name": "Vendedor 4 · Dupla B (Servicios Locales)",
        "role": "seller",
        "dupla": "Dupla B — Servicios Locales & Agenda",
        "phone": "+5491100000004",
        "plan": "closer_web",
        "default_pass": "Closer4Prosper2026!"
    },
    {
        "email": "closer5@agenciaprosperia.com",
        "name": "Vendedor 5 · Dupla C (Profesionales & Academias)",
        "role": "seller",
        "dupla": "Dupla C — Profesionales, Consultores & Academias",
        "phone": "+5491100000005",
        "plan": "closer_web",
        "default_pass": "Closer5Prosper2026!"
    },
    {
        "email": "closer6@agenciaprosperia.com",
        "name": "Vendedor 6 · Dupla C (Profesionales & Academias)",
        "role": "seller",
        "dupla": "Dupla C — Profesionales, Consultores & Academias",
        "phone": "+5491100000006",
        "plan": "closer_web",
        "default_pass": "Closer6Prosper2026!"
    },
]


def init_db():
    """Inicializa la base de datos, aplica migraciones no destructivas y siembra la fuerza comercial."""
    Base.metadata.create_all(bind=engine)
    _run_safe_migrations()

    db = SessionLocal()
    try:
        now_iso = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        # Asegurar que el usuario Admin existente tenga rol 'admin'
        admin_email = os.environ.get("ADMIN_EMAIL", "edward@agenciaprosperia.com")
        admin_password = os.environ.get("ADMIN_PASSWORD", "ProsperAdmin2026!")
        existing_users = db.query(User).all()
        if not existing_users:
            admin = User(
                email=admin_email,
                name=os.environ.get("ADMIN_NAME", "Edward Jiménez (CEO & Admin)"),
                password=hash_password(admin_password),
                company=os.environ.get("ADMIN_COMPANY", "Agencia Prosper IA LLC"),
                phone=os.environ.get("ADMIN_PHONE", "+17865573119"),
                plan="premium",
                api_key=os.environ.get("ADMIN_API_KEY", ""),
                role="admin",
                dupla="Dirección Ejecutiva",
                is_active=1,
                commission_rate=0.15,
                created_at=now_iso,
            )
            db.add(admin)
        else:
            for u in existing_users:
                if u.email == admin_email or u.plan == "premium" or "admin" in (u.email or "").lower() or "edward" in (u.email or "").lower():
                    u.role = "admin"
                    u.dupla = u.dupla or "Dirección Ejecutiva"
                    u.is_active = 1

        # Sembrar los 6 Vendedores iniciales + Supervisor + Operaciones si no existen
        for member in INITIAL_SALES_TEAM:
            exists_u = db.query(User).filter(User.email == member["email"]).first()
            if not exists_u:
                db.add(User(
                    email=member["email"],
                    name=member["name"],
                    password=hash_password(member["default_pass"]),
                    company="Agencia Prosper IA LLC",
                    phone=member["phone"],
                    plan=member["plan"],
                    api_key="",
                    role=member["role"],
                    dupla=member["dupla"],
                    is_active=1,
                    commission_rate=0.15,
                    created_at=now_iso,
                ))

        # Sembrar lista de exclusión DND desde BLACKLIST_DO_NOT_CONTACT.json
        blacklist_path = Path(__file__).parent / "BLACKLIST_DO_NOT_CONTACT.json"
        if blacklist_path.exists():
            try:
                bl_items = json.loads(blacklist_path.read_text(encoding="utf-8"))
                for item in bl_items:
                    em = normalize_email(item.get("email", ""))
                    if em:
                        exists_dnd = db.query(DndExclusion).filter(DndExclusion.email == em).first()
                        if not exists_dnd:
                            db.add(DndExclusion(
                                email=em,
                                phone_e164="",
                                company=item.get("empresa", ""),
                                reason=item.get("motivo", "Exclusión DND"),
                                source="BLACKLIST_DO_NOT_CONTACT.json",
                                created_at=item.get("fecha_exclusion", now_iso),
                            ))
                        # Si ese lead existe en la tabla leads, marcarlo como dnd
                        for ld in db.query(Lead).filter(Lead.email == em).all():
                            ld.contact_status = "dnd"
            except Exception as bl_err:
                print(f"⚠️ [DND SEED] Error leyendo BLACKLIST_DO_NOT_CONTACT.json: {bl_err}")

        # Normalizar phone_e164 en leads que no lo tengan
        for ld in db.query(Lead).filter((Lead.phone_e164 == None) | (Lead.phone_e164 == "")).all():
            if ld.phone:
                ld.phone_e164 = normalize_phone_e164(ld.phone)

        # Seed Integration Settings
        default_settings = {
            "ghl_webhook_url": os.environ.get("GHL_WEBHOOK_URL", ""),
            "ghl_location_id": os.environ.get("GHL_LOCATION_ID", "CNvJBINRWBUL2EdqRh3G"),
            "ghl_pipeline_id": os.environ.get("GHL_PIPELINE_ID", "SJ4xiMasQ0GZcUNYFgpa"),
            "n8n_webhook_url": "",
            "whatsapp_status": "pending",
            "whatsapp_token": "",
            "whatsapp_phone_id": "",
            "fixed_monthly_expenses": "6000",
        }
        for key, val in default_settings.items():
            exists = db.query(IntegrationSetting).filter(IntegrationSetting.key == key).first()
            if not exists:
                setting = IntegrationSetting(key=key, value=val)
                db.add(setting)

        # Seed Leads si estuviera vacía
        if db.query(Lead).count() == 0:
            from main import INITIAL_LEADS
            for lead_data in INITIAL_LEADS:
                lead = Lead(
                    id=lead_data["id"],
                    name=lead_data["name"],
                    full_name=lead_data["name"],
                    email=lead_data["email"],
                    company=lead_data.get("company"),
                    business_name=lead_data.get("company"),
                    phone=lead_data.get("phone"),
                    phone_e164=normalize_phone_e164(lead_data.get("phone", "")),
                    status=lead_data.get("status", "new"),
                    source=lead_data.get("source", "website"),
                    score=lead_data.get("score", 50),
                    notes=lead_data.get("notes"),
                    created_at=lead_data["created_at"]
                )
                db.add(lead)

        # Seed Blog Posts
        from main import INITIAL_BLOG_POSTS
        seeded_slugs = set()
        for post_data in INITIAL_BLOG_POSTS:
            if post_data["slug"] in seeded_slugs:
                continue
            seeded_slugs.add(post_data["slug"])
            exists = db.query(BlogPost).filter(BlogPost.slug == post_data["slug"]).first()
            if not exists:
                post = BlogPost(
                    slug=post_data["slug"],
                    title=post_data["title"],
                    category=post_data["category"],
                    summary=post_data["summary"],
                    content=post_data["content"],
                    image_url=post_data["image_url"],
                    published_at=post_data["published_at"],
                    author=post_data["author"]
                )
                db.add(post)

        published_dir = Path(__file__).parent / "content" / "editorial_published"
        if published_dir.exists():
            for article_path in published_dir.glob("*.json"):
                article = json.loads(article_path.read_text(encoding="utf-8"))
                if article.get("status") != "published":
                    continue
                values = {
                    "title": article["title"],
                    "category": article["lane"],
                    "summary": article["summary"],
                    "content": article["content"],
                    "image_url": article.get("image_url", "/static/logo_prosper_ia_cropped.jpg"),
                    "published_at": article["published_at"],
                    "author": article["author"],
                }
                existing_article = db.query(BlogPost).filter(BlogPost.slug == article["slug"]).first()
                if existing_article is None:
                    db.add(BlogPost(slug=article["slug"], **values))
                else:
                    for key, value in values.items():
                        setattr(existing_article, key, value)

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()


def get_db_session():
    """Generador de sesiones de base de datos para dependencias FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def sync_blog_posts(db):
    """Sincroniza los posts de INITIAL_BLOG_POSTS y content/editorial_published con la BD."""
    from main import INITIAL_BLOG_POSTS
    synced_slugs = set()
    for post_data in INITIAL_BLOG_POSTS:
        if post_data["slug"] in synced_slugs:
            continue
        synced_slugs.add(post_data["slug"])
        exists = db.query(BlogPost).filter(BlogPost.slug == post_data["slug"]).first()
        if not exists:
            post = BlogPost(
                slug=post_data["slug"],
                title=post_data["title"],
                category=post_data["category"],
                summary=post_data["summary"],
                content=post_data["content"],
                image_url=post_data["image_url"],
                published_at=post_data["published_at"],
                author=post_data["author"]
            )
            db.add(post)
        elif exists.image_url != post_data["image_url"]:
            exists.image_url = post_data["image_url"]

    published_dir = Path(__file__).parent / "content" / "editorial_published"
    if published_dir.exists():
        for article_path in published_dir.glob("*.json"):
            try:
                article = json.loads(article_path.read_text(encoding="utf-8"))
                if article.get("status") != "published":
                    continue
                synced_slugs.add(article["slug"])
                values = {
                    "title": article["title"],
                    "category": article.get("lane", "laboratorio-prosperia"),
                    "summary": article["summary"],
                    "content": article["content"],
                    "image_url": article.get("image_url", "/static/logo_prosper_ia_cropped.jpg"),
                    "published_at": article.get("published_at", datetime.utcnow().isoformat()),
                    "author": article.get("author", "Equipo editorial ProsperIA"),
                }
                existing_article = db.query(BlogPost).filter(BlogPost.slug == article["slug"]).first()
                if existing_article is None:
                    db.add(BlogPost(slug=article["slug"], **values))
                else:
                    for key, value in values.items():
                        setattr(existing_article, key, value)
            except Exception as e:
                print(f"Error syncing {article_path}: {e}")

    for row in db.query(BlogPost).all():
        if row.slug not in synced_slugs:
            db.delete(row)

    db.commit()

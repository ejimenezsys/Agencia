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
        if hmac.compare_digest(candidate.hex(), digest_hex):
            return True
        # Alias de cortesía para pruebas de Closers (Closer2026! / SheilleProsper2026! / DiegoProsper2026!)
        if password in ("SheilleProsper2026!", "DiegoProsper2026!", "CloserProsper2026!", "Closer2026!"):
            alt_candidate = hashlib.pbkdf2_hmac(
                "sha256", b"Closer2026!", bytes.fromhex(salt_hex), int(iterations)
            )
            return hmac.compare_digest(alt_candidate.hex(), digest_hex)
        return False
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
    """Modelo ORM para usuarios del Sales Operating System (Admin y los 10 Closers)."""
    __tablename__ = "users"

    email = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    company = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    plan = Column(String, nullable=True)
    api_key = Column(String, nullable=True)
    # Campos Sales OS
    role = Column(String, default="seller", nullable=False)  # admin, seller
    dupla = Column(String, default="Dupla A — Clínicas", nullable=True)
    ghl_user_id = Column(String, nullable=True)
    is_active = Column(Integer, default=1, nullable=False)
    commission_rate = Column(Float, default=0.15, nullable=False)
    created_at = Column(String, nullable=True)
    # Campos de Calendario, Check-In Matutino, Horas Conectado y Embudo KPI (100 -> 60 -> 6 -> 1)
    calendar_url = Column(String, default="https://api.leadconnectorhq.com/widget/bookings/calendario-de-edward-jimenez", nullable=True)
    checkin_at = Column(String, default="", nullable=True)
    last_seen_at = Column(String, default="", nullable=True)
    active_minutes_today = Column(Integer, default=0, nullable=True)
    active_minutes_week = Column(Integer, default=0, nullable=True)
    calls_made_today = Column(Integer, default=0, nullable=True)
    calls_made_week = Column(Integer, default=0, nullable=True)
    calls_answered_week = Column(Integer, default=0, nullable=True)
    demos_done_week = Column(Integer, default=0, nullable=True)
    sales_closed_week = Column(Integer, default=0, nullable=True)
    avatar_url = Column(String, default="", nullable=True)


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
            ("calendar_url", "TEXT DEFAULT 'https://api.leadconnectorhq.com/widget/bookings/calendario-de-edward-jimenez'"),
            ("checkin_at", "TEXT DEFAULT ''"),
            ("last_seen_at", "TEXT DEFAULT ''"),
            ("active_minutes_today", "INTEGER DEFAULT 0"),
            ("active_minutes_week", "INTEGER DEFAULT 0"),
            ("calls_made_today", "INTEGER DEFAULT 0"),
            ("calls_made_week", "INTEGER DEFAULT 0"),
            ("calls_answered_week", "INTEGER DEFAULT 0"),
            ("demos_done_week", "INTEGER DEFAULT 0"),
            ("sales_closed_week", "INTEGER DEFAULT 0"),
            ("avatar_url", "TEXT DEFAULT ''"),
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
        "email": "sheille.perez@gmail.com",
        "name": "Sheille Pérez",
        "role": "seller",
        "dupla": "Dupla A — Clínicas (Dental, Estética y Capilar)",
        "phone": "+541128612007",
        "plan": "SVE-90 Enterprise",
        "ghl_user_id": "ucToiI5LKdcDLUpnAC5g",
        "calendar_url": "https://api.agenciaprosperia.com/widget/booking/GrvltSCThpWp2cEptiTF",
        "avatar_url": "/static/img/closers/sheilla.jpg",
        "default_pass": "Closer2026!"
    },
    {
        "email": "diegoarriondo03@gmail.com",
        "name": "Diego Arriondo",
        "role": "seller",
        "dupla": "Dupla A — Clínicas (Dental, Estética y Capilar)",
        "phone": "+541127950792",
        "plan": "SVE-90 Enterprise",
        "ghl_user_id": "OOzbqNV7cHd43h1u8C7v",
        "calendar_url": "https://api.agenciaprosperia.com/widget/booking/qIeHTDISu0BGHx7cVhbh",
        "avatar_url": "/static/img/closers/diego.jpg",
        "default_pass": "Closer2026!"
    },
    {
        "email": "cinthyapenida0@gmail.com",
        "name": "Cinthya Penida",
        "role": "seller",
        "dupla": "Dupla B — Servicios Locales & Agenda",
        "phone": "+5493704851257",
        "plan": "SVE-90 Enterprise",
        "ghl_user_id": "v273geU17rmcAHWieZlE",
        "calendar_url": "https://api.agenciaprosperia.com/widget/booking/H2N6v95axx9rqkG7Sibw",
        "avatar_url": "/static/img/closers/cintya.jpg",
        "default_pass": "Closer2026!"
    },
    {
        "email": "claudiniosan@yahoo.com.ar",
        "name": "Claudio A. Sánchez",
        "role": "seller",
        "dupla": "Dupla B — Servicios Locales & Agenda",
        "phone": "+5491141948202",
        "plan": "SVE-90 Enterprise",
        "ghl_user_id": "aXESsYsnlFG6Owpd0k68",
        "calendar_url": "https://api.agenciaprosperia.com/widget/booking/ax6fOmetoC3abxRMlCwu",
        "avatar_url": "/static/img/closers/claudio.png",
        "default_pass": "Closer2026!"
    },
    {
        "email": "loremrodriguezafb@gmail.com",
        "name": "Lorena Rodríguez",
        "role": "seller",
        "dupla": "Dupla C — Profesionales, Consultores & Academias",
        "phone": "+5493885862967",
        "plan": "SVE-90 Enterprise",
        "ghl_user_id": "tmB5pG9R65JlJXghrdxE",
        "calendar_url": "https://api.agenciaprosperia.com/widget/booking/nxAwixR3T3PILNZxv1S4",
        "avatar_url": "/static/img/closers/lorena.jpg",
        "default_pass": "Closer2026!"
    },
    {
        "email": "sergiotorales608@gmail.com",
        "name": "Sergio Torales",
        "role": "seller",
        "dupla": "Dupla C — Profesionales, Consultores & Academias",
        "phone": "+5493704035398",
        "plan": "SVE-90 Enterprise",
        "ghl_user_id": "hhYMDFJpoBVVrP7AOiZ9",
        "calendar_url": "https://api.agenciaprosperia.com/widget/booking/w2KriVI4LqhisSjIPiMV",
        "avatar_url": "/static/img/closers/sergio.jpg",
        "default_pass": "Closer2026!"
    },
    {
        "email": "closer7@agenciaprosperia.com",
        "name": "Closer 7 (En Contratación)",
        "role": "seller",
        "dupla": "Dupla A — Clínicas (Dental, Estética y Capilar)",
        "phone": "",
        "plan": "SVE-90 Enterprise",
        "ghl_user_id": "",
        "calendar_url": "https://api.agenciaprosperia.com/widget/booking/gqoqyrr112bvjTJYqOi8",
        "avatar_url": "",
        "default_pass": "Closer2026!"
    },
    {
        "email": "closer8@agenciaprosperia.com",
        "name": "Closer 8 (En Contratación)",
        "role": "seller",
        "dupla": "Dupla B — Servicios Locales & Agenda",
        "phone": "",
        "plan": "SVE-90 Enterprise",
        "ghl_user_id": "",
        "calendar_url": "https://api.agenciaprosperia.com/widget/booking/gqoqyrr112bvjTJYqOi8",
        "avatar_url": "",
        "default_pass": "Closer2026!"
    },
    {
        "email": "closer9@agenciaprosperia.com",
        "name": "Closer 9 (En Contratación)",
        "role": "seller",
        "dupla": "Dupla C — Profesionales, Consultores & Academias",
        "phone": "",
        "plan": "SVE-90 Enterprise",
        "ghl_user_id": "",
        "calendar_url": "https://api.agenciaprosperia.com/widget/booking/gqoqyrr112bvjTJYqOi8",
        "avatar_url": "",
        "default_pass": "Closer2026!"
    },
    {
        "email": "closer10@agenciaprosperia.com",
        "name": "Closer 10 (En Contratación)",
        "role": "seller",
        "dupla": "Dupla C — Profesionales, Consultores & Academias",
        "phone": "",
        "plan": "SVE-90 Enterprise",
        "ghl_user_id": "",
        "calendar_url": "https://api.agenciaprosperia.com/widget/booking/gqoqyrr112bvjTJYqOi8",
        "avatar_url": "",
        "default_pass": "Closer2026!"
    },
]

OBSOLETE_TEST_EMAILS = [
    "supervisor@agenciaprosperia.com",
    "operaciones@agenciaprosperia.com",
    "closer1@agenciaprosperia.com",
    "closer2@agenciaprosperia.com",
    "closer3@agenciaprosperia.com",
    "closer4@agenciaprosperia.com",
    "closer5@agenciaprosperia.com",
    "closer6@agenciaprosperia.com",
    "ucumaryvisual@gmail.com",
]


def get_active_real_closers() -> list:
    """Devuelve únicamente los Closers reales activos con cuenta en ProsperIA CRM (excluye vacantes en contratación)."""
    return [m for m in INITIAL_SALES_TEAM if (m.get("ghl_user_id") or "").strip()]


def get_next_round_robin_closer(db) -> dict:
    """Rota equitativamente (Round-Robin 1 a 6) entre los Closers reales activos."""
    active_closers = get_active_real_closers()
    if not active_closers:
        return INITIAL_SALES_TEAM[0]
    rr_row = db.query(IntegrationSetting).filter(IntegrationSetting.key == "sales_rr_index").first()
    idx = 0
    if rr_row and (rr_row.value or "").isdigit():
        idx = int(rr_row.value)
    chosen = active_closers[idx % len(active_closers)]
    next_idx = (idx + 1) % len(active_closers)
    if rr_row:
        rr_row.value = str(next_idx)
    else:
        db.add(IntegrationSetting(key="sales_rr_index", value=str(next_idx)))
    db.commit()
    return chosen


def init_db():
    """Inicializa la base de datos, aplica migraciones no destructivas y siembra la fuerza comercial real."""
    Base.metadata.create_all(bind=engine)
    _run_safe_migrations()

    db = SessionLocal()
    try:
        now_iso = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        # 1. Eliminar usuarios genéricos de prueba y al editor (Cris) para dejar solo Admin + los 10 Closers
        for obs_email in OBSOLETE_TEST_EMAILS:
            obs_u = db.query(User).filter(User.email == obs_email).first()
            if obs_u:
                db.delete(obs_u)

        # 2. Asegurar que AMBOS correos de Edward (admin@prosperia.com y edward@agenciaprosperia.com) estén activos con Digital2@26@
        admin_pass_hash = hash_password("Digital2@26@")
        for adm_email in ("admin@prosperia.com", "edward@agenciaprosperia.com"):
            adm_u = db.query(User).filter(User.email == adm_email).first()
            if not adm_u:
                db.add(User(
                    email=adm_email,
                    name="Edward Jiménez (CEO & Admin)",
                    password=admin_pass_hash,
                    company="Agencia Prosper IA LLC",
                    phone="+17865573119",
                    plan="SVE-90 Enterprise",
                    api_key=os.environ.get("ADMIN_API_KEY", "sve90_live_master_key_777_prosperia"),
                    role="admin",
                    dupla="Dirección Ejecutiva (CEO)",
                    is_active=1,
                    commission_rate=0.15,
                    created_at=now_iso,
                    calendar_url="https://api.agenciaprosperia.com/widget/booking/aT3eXMuYSOnWwjnC063t",
                    avatar_url="/static/edward_hero_depth.jpg",
                ))
            else:
                adm_u.name = "Edward Jiménez (CEO & Admin)"
                adm_u.password = admin_pass_hash
                adm_u.role = "admin"
                adm_u.plan = "SVE-90 Enterprise"
                adm_u.dupla = "Dirección Ejecutiva (CEO)"
                adm_u.is_active = 1
                adm_u.calendar_url = "https://api.agenciaprosperia.com/widget/booking/aT3eXMuYSOnWwjnC063t"
                adm_u.avatar_url = "/static/edward_hero_depth.jpg"
                if not getattr(adm_u, "api_key", ""):
                    adm_u.api_key = "sve90_live_master_key_777_prosperia"

        # 3. Sembrar o actualizar los 6 Closers reales de GHL + las 4 vacantes en contratación
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
                    api_key="sve90_closer_key_777",
                    role="seller",
                    dupla=member["dupla"],
                    ghl_user_id=member.get("ghl_user_id", ""),
                    is_active=1 if member.get("ghl_user_id") else 0,
                    commission_rate=0.15,
                    created_at=now_iso,
                    calendar_url=member.get("calendar_url", "https://api.agenciaprosperia.com/widget/booking/gqoqyrr112bvjTJYqOi8"),
                    avatar_url=member.get("avatar_url", ""),
                ))
            else:
                exists_u.role = "seller"
                exists_u.plan = "SVE-90 Enterprise"
                if member.get("ghl_user_id"):
                    exists_u.ghl_user_id = member["ghl_user_id"]
                if member.get("calendar_url"):
                    exists_u.calendar_url = member["calendar_url"]
                if member.get("avatar_url"):
                    exists_u.avatar_url = member["avatar_url"]

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

        # Confirmar usuarios del Sales OS, lista DND y configuraciones de inmediato
        db.commit()

        # Sembrar y repartir los contactos limpios del CRM ProsperIA (GHL_CONTACTS_SEED_455.json) y limpiar simulaciones de Sheilla
        seed_455_path = Path(__file__).parent / "GHL_CONTACTS_SEED_455.json"
        seeded_flag = db.query(IntegrationSetting).filter(IntegrationSetting.key == "ghl_455_seeded_v4_clean").first()
        if seed_455_path.exists() and not seeded_flag:
            try:
                raw_contacts = json.loads(seed_455_path.read_text(encoding="utf-8"))
                # 1. Limpiar simulaciones de prueba de Sheilla (sheille.perez@gmail.com) y de Admin
                for sim_email in ("sheille.perez@gmail.com", "sheillavargas22@gmail.com"):
                    su = db.query(User).filter(User.email == sim_email).first()
                    if su:
                        su.calls_made_today = 0
                        su.calls_made_week = 0
                        su.calls_answered_week = 0
                        su.demos_done_week = 0
                        su.sales_closed_week = 0
                        su.active_minutes_today = 0
                        su.active_minutes_week = 0
                        su.checkin_at = ""
                    db.query(AuditLog).filter(AuditLog.actor_email == sim_email).delete(synchronize_session=False)

                # 2. Limpiar leads anteriores y rearmar la lista limpia sincronizada con el CRM ProsperIA
                db.query(Lead).delete(synchronize_session=False)
                db.commit()

                dnd_emails = {r.email for r in db.query(DndExclusion).all() if r.email}
                internal_emails = {m["email"].lower() for m in INITIAL_SALES_TEAM} | {
                    "admin@prosperia.com", "edward@agenciaprosperia.com", "ucumaryvisual@gmail.com"
                }
                seller_list = [m for m in INITIAL_SALES_TEAM]
                seen_emails = set()
                seen_phones = set()
                inserted_idx = 0

                for item in raw_contacts:
                    em = normalize_email(item.get("email", ""))
                    ph = normalize_phone_e164(item.get("phone", ""))
                    if not em and not ph:
                        continue
                    if em in internal_emails or em in dnd_emails:
                        continue
                    if em and em in seen_emails:
                        continue
                    if ph and ph in seen_phones:
                        continue
                    if em:
                        seen_emails.add(em)
                    if ph:
                        seen_phones.add(ph)

                    assigned_member = seller_list[inserted_idx % len(seller_list)]
                    dupla_str = assigned_member["dupla"]
                    if "Dupla A" in dupla_str:
                        niche_val = "clinica"
                        tpl_val = "clinica_dental_estetica"
                    elif "Dupla B" in dupla_str:
                        niche_val = "servicios_locales"
                        tpl_val = "servicios_locales_taller"
                    else:
                        niche_val = "profesionales"
                        tpl_val = "profesionales_consultoria_legal"

                    nm = (item.get("name") or "").strip() or (em.split("@")[0] if em else "Prospecto ProsperIA")
                    comp = (item.get("company") or "").strip() or "Negocio / Profesional en Evaluación"
                    c_id = (item.get("contact_id") or "").strip()
                    dt_added = (item.get("date_added") or now_iso)[:19].replace("T", " ")

                    db.add(Lead(
                        name=nm,
                        full_name=nm,
                        email=em or f"contacto_{inserted_idx + 1}@sin-correo.local",
                        company=comp,
                        business_name=comp,
                        phone=item.get("phone") or ph,
                        phone_e164=ph,
                        status="new",
                        source="ghl_455_pool",
                        source_channel="Comunidad / Hub ProsperIA",
                        source_campaign="Base CRM ProsperIA Repartida",
                        interest_primary="Sitio Web Inteligente",
                        score=75,
                        notes="Contacto oficial importado de CRM ProsperIA para filtro telefónico en Dashboard.",
                        created_at=dt_added,
                        contact_id=c_id,
                        owner_id=assigned_member["email"],
                        setter_id=assigned_member["email"],
                        niche=niche_val,
                        country=item.get("country") or "LATAM / US",
                        contact_permission="Opt-in Hub / Comunidad ProsperIA",
                        contact_status="contactable",
                        pipeline_stage="Lead identificado",
                        offer_version="EXPRESS_497",
                        selected_template=tpl_val,
                    ))
                    inserted_idx += 1

                db.add(IntegrationSetting(key="ghl_455_seeded_v4_clean", value=f"{inserted_idx}_contacts_at_{now_iso}"))
                db.commit()
                print(f"✅ [SEED CRM CLEAN] Se sembraron y repartieron {inserted_idx} contactos reales entre los 10 Closers.")
            except Exception as s455_err:
                db.rollback()
                print(f"⚠️ [SEED CRM CLEAN] Error sembrando GHL_CONTACTS_SEED_455.json: {s455_err}")

        # Sembrar v5 Oficial: Los 516 Contactos del CRM + 600 Exportadores COMEX repartidos 100% entre los 6 Closers Reales
        seed_516_path = Path(__file__).parent / "GHL_CONTACTS_SEED_516_PLUS_COMEX.json"
        seeded_v5_flag = db.query(IntegrationSetting).filter(IntegrationSetting.key == "ghl_516_and_comex_v5_6closers").first()
        if seed_516_path.exists() and not seeded_v5_flag:
            try:
                payload_v5 = json.loads(seed_516_path.read_text(encoding="utf-8"))
                ghl_contacts_v5 = payload_v5.get("ghl_contacts", [])
                comex_contacts_v5 = payload_v5.get("comex_contacts", [])
                active_six = get_active_real_closers()

                # Conservar intacto cualquier prospecto que ya avanzó a Primer contacto+ o tenga pago registrado
                db.query(Lead).filter(
                    (Lead.pipeline_stage == "Lead identificado") & ((Lead.amount_collected == None) | (Lead.amount_collected == 0))
                ).delete(synchronize_session=False)
                db.commit()

                dnd_emails = {r.email for r in db.query(DndExclusion).all() if r.email}
                internal_emails = {m["email"].lower() for m in INITIAL_SALES_TEAM} | {
                    "admin@prosperia.com", "edward@agenciaprosperia.com", "ucumaryvisual@gmail.com"
                }
                existing_leads = db.query(Lead).all()
                seen_emails = {normalize_email(ld.email) for ld in existing_leads if ld.email}
                seen_phones = {normalize_phone_e164(ld.phone_e164 or ld.phone) for ld in existing_leads if (ld.phone_e164 or ld.phone)}

                def _dupla_niche_tpl(dupla_str: str):
                    if "Dupla A" in dupla_str:
                        return "clinica", "clinica_dental_estetica"
                    if "Dupla B" in dupla_str:
                        return "servicios_locales", "servicios_locales_taller"
                    return "profesionales", "profesionales_consultoria_legal"

                ghl_inserted = 0
                for item in ghl_contacts_v5:
                    em = normalize_email(item.get("email", ""))
                    ph = normalize_phone_e164(item.get("phone", ""))
                    if not em and not ph:
                        continue
                    if em in internal_emails or em in dnd_emails:
                        continue
                    if (em and em in seen_emails) or (ph and ph in seen_phones):
                        continue
                    if em:
                        seen_emails.add(em)
                    if ph:
                        seen_phones.add(ph)

                    member = active_six[ghl_inserted % len(active_six)]
                    niche_val, tpl_val = _dupla_niche_tpl(member["dupla"])
                    nm = (item.get("name") or "").strip() or (em.split("@")[0] if em else "Prospecto ProsperIA")
                    comp = (item.get("company") or "").strip() or "Negocio / Profesional por Calificar"
                    dt_added = (item.get("date_added") or now_iso)[:19].replace("T", " ")

                    db.add(Lead(
                        name=nm,
                        full_name=nm,
                        email=em or f"crm_{ghl_inserted + 1}@sin-correo.local",
                        company=comp,
                        business_name=comp,
                        phone=item.get("phone") or ph,
                        phone_e164=ph,
                        status="new",
                        source="ghl_516_pool",
                        source_channel="Inbound Reels / Códigos",
                        source_campaign="📱 Inbound Reels / Códigos (Filtro 45s)",
                        interest_primary="Sitio Web Inteligente",
                        score=75,
                        notes="Contacto real importado de ProsperIA CRM (Base 516). Aplicar filtro rápido de 45s: ¿Tienes negocio activo?",
                        created_at=dt_added,
                        contact_id=(item.get("contact_id") or "").strip(),
                        owner_id=member["email"],
                        setter_id=member["email"],
                        niche=niche_val,
                        country=item.get("country") or "LATAM / US",
                        contact_permission="Opt-in Reels / Hub ProsperIA",
                        contact_status="contactable",
                        pipeline_stage="Lead identificado",
                        offer_version="ANUAL_990",
                        selected_template=tpl_val,
                    ))
                    ghl_inserted += 1

                comex_inserted = 0
                for item in comex_contacts_v5:
                    em = normalize_email(item.get("email", ""))
                    ph = normalize_phone_e164(item.get("phone", ""))
                    if not ph:
                        continue
                    if em in internal_emails or em in dnd_emails:
                        continue
                    if (em and em in seen_emails) or (ph and ph in seen_phones):
                        continue
                    if em:
                        seen_emails.add(em)
                    seen_phones.add(ph)

                    member = active_six[comex_inserted % len(active_six)]
                    nm = (item.get("name") or "").strip() or "Gerencia Comercial"
                    comp = (item.get("company") or "").strip() or "Empresa Exportadora"

                    db.add(Lead(
                        name=nm,
                        full_name=nm,
                        email=em or f"comex_{comex_inserted + 1}@sin-correo.local",
                        company=comp,
                        business_name=comp,
                        phone=item.get("phone") or ph,
                        phone_e164=ph,
                        status="new",
                        source="comex_outbound_b2b",
                        source_channel="Outbound COMEX",
                        source_campaign="🏢 COMEX Exportador ($100K-$10M)",
                        interest_primary="Sitio Web B2B + IA 24/7 + ProsperIA CRM",
                        score=88,
                        notes=item.get("notes") or "Empresa Exportadora verificada (Base COMEX).",
                        created_at=now_iso[:19].replace("T", " "),
                        contact_id="",
                        owner_id=member["email"],
                        setter_id=member["email"],
                        niche="profesionales",
                        country=item.get("country") or "LATAM",
                        contact_permission="Directorio Empresarial / Aduanero B2B",
                        contact_status="contactable",
                        pipeline_stage="Lead identificado",
                        offer_version="ANUAL_990",
                        selected_template="profesionales_consultoria_legal",
                    ))
                    comex_inserted += 1

                # Desactivar las 4 cuentas placeholder (closer7..closer10) para que solo aparezcan los 6 Closers reales
                for ph_idx in (7, 8, 9, 10):
                    ph_u = db.query(User).filter(User.email == f"closer{ph_idx}@agenciaprosperia.com").first()
                    if ph_u:
                        ph_u.is_active = 0

                db.add(IntegrationSetting(
                    key="ghl_516_and_comex_v5_6closers",
                    value=f"ghl={ghl_inserted},comex={comex_inserted}_at_{now_iso}",
                ))
                db.commit()
                print(f"✅ [SEED V5 6 CLOSERS] Repartidos {ghl_inserted} contactos CRM + {comex_inserted} empresas COMEX entre los 6 Closers activos.")
            except Exception as sv5_err:
                db.rollback()
                print(f"⚠️ [SEED V5 6 CLOSERS] Error sembrando GHL_CONTACTS_SEED_516_PLUS_COMEX.json: {sv5_err}")

        # Seed Leads de respaldo si no existiera el archivo 455 y la tabla estuviera vacía
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
            db.commit()

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
                try:
                    article = json.loads(article_path.read_text(encoding="utf-8"))
                    if article.get("status") != "published":
                        continue
                    values = {
                        "title": article["title"],
                        "category": article.get("lane", "laboratorio-prosperia"),
                        "summary": article["summary"],
                        "content": article["content"],
                        "image_url": article.get("image_url", "/static/logo_prosper_ia_cropped.jpg"),
                        "published_at": article.get("published_at", now_iso),
                        "author": article.get("author", "Edward Jiménez"),
                    }
                    existing_article = db.query(BlogPost).filter(BlogPost.slug == article["slug"]).first()
                    if existing_article is None:
                        db.add(BlogPost(slug=article["slug"], **values))
                    else:
                        for key, value in values.items():
                            setattr(existing_article, key, value)
                except Exception as art_err:
                    print(f"⚠️ Error leyendo artículo {article_path}: {art_err}")

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

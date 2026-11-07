"""Router del Sales Operating System (Sales OS) — Sitios Web Inteligentes.

Implementa:
  - Gestión de roles y permisos (admin, supervisor, seller, operations).
  - Alta y administración de los 6-20 vendedores por Duplas (A, B, C).
  - Asignación de prospectos sin duplicación y exclusión automática DND/Opt-out.
  - Flujo comercial canónico de 11 etapas + 6 rutas alternativas.
  - Separación estricta entre monto cotizado (quoted_amount), contratado (contracted_amount)
    y dinero realmente cobrado (amount_collected).
  - Cálculo de comisión 15% (5% Setter + 10% Closer) exclusivamente sobre cobros verificados.
  - Registro de auditoría inmutable (AuditLog) y sincronización con GoHighLevel.
  - Demostrador interactivo en vivo de Sitios Web Inteligentes (/demo-sitio-web).
"""
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import (
    SessionLocal,
    User,
    Lead as DbLead,
    AuditLog,
    DndExclusion,
    SessionModel,
    OFFER_CATALOG,
    CANONICAL_PIPELINE_STAGES,
    ALTERNATIVE_PIPELINE_STAGES,
    ALL_PIPELINE_STAGES,
    hash_password,
    normalize_phone_e164,
    normalize_email,
)
from ghl_client import sync_sales_os_event_to_ghl_async, sync_lead_to_ghl_async

router = APIRouter()

# Catálogo de Plantillas por Giro para el Demostrador en Vivo ("Mostrar cómo se hacen las páginas")
WEBSITE_TEMPLATES_SHOWCASE = {
    "clinica_dental_estetica": {
        "id": "clinica_dental_estetica",
        "name": "🦷 Clínica Odontológica / Estética / Capilar (Dupla A)",
        "dupla": "Dupla A — Clínicas",
        "niche": "clinica",
        "accent": "#00e5ff",
        "secondary": "#0ea5e9",
        "badge": "SALUD & ESTÉTICA PREMIUM",
        "default_business": "Clínica Dental & Estética Avanzada",
        "default_city": "Miami / Buenos Aires / Bogotá",
        "default_offer": "Valoración Diagnóstica + Diseño de Sonrisa / Armonización con 20% OFF esta semana",
        "hero_title": "Agenda tu Valoración Especializada en Menos de 60 Segundos sin Esperar en Línea",
        "hero_subtitle": "Nuestro sistema inteligente califica tu caso y te asigna turno prioritario con nuestros especialistas por WhatsApp las 24 horas.",
        "services": [
            {"icon": "fa-tooth", "title": "Implantes & Diseño de Sonrisa", "desc": "Resultados naturales planificados digitalmente en 1 a 2 sesiones."},
            {"icon": "fa-wand-magic-sparkles", "title": "Medicina Estética & Rejuvenecimiento", "desc": "Tratamientos mínimamente invasivos con aprobación médica internacional."},
            {"icon": "fa-calendar-check", "title": "Confirmación Automática 24/7", "desc": "Recibe recordatorios en tu WhatsApp para que nunca pierdas tu turno."},
        ],
        "form_questions": [
            "¿Qué tratamiento te interesa evaluar primero?",
            "¿Para cuándo te gustaría agendar tu valoración (Esta semana / Próxima semana)?",
        ],
    },
    "servicios_locales_taller": {
        "id": "servicios_locales_taller",
        "name": "🔧 Servicios Locales / Taller / Hogar / Climatización (Dupla B)",
        "dupla": "Dupla B — Servicios Locales",
        "niche": "servicios_locales",
        "accent": "#f59e0b",
        "secondary": "#ea580c",
        "badge": "SERVICIO TÉCNICO & PRESUPUESTO RÁPIDO",
        "default_business": "Centro Técnico Especializado & Servicios Express",
        "default_city": "Tu Ciudad",
        "default_offer": "Diagnóstico Técnico Prioritario + Presupuesto Exacto por WhatsApp en 15 Minutos",
        "hero_title": "Deja los Datos de tu Solicitud y Recibe Presupuesto y Turno Hoy Mismo",
        "hero_subtitle": "Aunque nuestro equipo esté con las manos ocupadas en el taller o en terreno, nuestro Asistente 24/7 recibe tu pedido y te reserva lugar al instante.",
        "services": [
            {"icon": "fa-screwdriver-wrench", "title": "Diagnóstico Rápido con Garantía", "desc": "Revisamos tu requerimiento y te enviamos cotización clara antes de empezar."},
            {"icon": "fa-bolt", "title": "Reserva de Turno sin Llamar", "desc": "Elige día y franja horaria desde tu celular en 30 segundos."},
            {"icon": "fa-shield-halved", "title": "Seguimiento por WhatsApp", "desc": "Te avisamos automáticamente apenas tu trabajo esté listo para entrega."},
        ],
        "form_questions": [
            "¿Qué servicio, arreglo o instalación necesitas cotizar?",
            "¿Es una urgencia para hoy/mañana o mantenimiento programado?",
        ],
    },
    "inmobiliaria_bienes_raices": {
        "id": "inmobiliaria_bienes_raices",
        "name": "🏢 Inmobiliaria / Desarrollos / Bienes Raíces (Dupla B)",
        "dupla": "Dupla B — Servicios Locales",
        "niche": "inmobiliaria",
        "accent": "#10b981",
        "secondary": "#059669",
        "badge": "INVERSIONES & PROPIEDADES EXCLUSIVAS",
        "default_business": "Grupo Inmobiliario & Inversiones Patrimoniales",
        "default_city": "Miami / CDMX / Madrid / CABA",
        "default_offer": "Catálogo Privado de Propiedades de Alta Rentabilidad + Asesoría 1 a 1",
        "hero_title": "Encuentra o Vende tu Propiedad con Pre-Calificación Inteligente 24/7",
        "hero_subtitle": "Filtramos presupuesto, zona y forma de pago en 1 minuto para agendar solo visitas reales con compradores calificados.",
        "services": [
            {"icon": "fa-building", "title": "Compra & Inversión Rentable", "desc": "Acceso a unidades seleccionadas con retorno proyectado y financiación."},
            {"icon": "fa-key", "title": "Venta Rápida de tu Propiedad", "desc": "Captación con videos virales y filtro automático de curiosos."},
            {"icon": "fa-handshake", "title": "Visita Presencial o Virtual", "desc": "Agenda en el calendario del asesor asignado sin idas y vueltas."},
        ],
        "form_questions": [
            "¿Buscas comprar para vivir, invertir o vender una propiedad?",
            "¿En qué rango de inversión te encuentras y qué zona prefieres?",
        ],
    },
    "profesionales_consultoria_legal": {
        "id": "profesionales_consultoria_legal",
        "name": "⚖️ Profesionales / Estudio Contable, Legal o Consultoría (Dupla C)",
        "dupla": "Dupla C — Profesionales & Academias",
        "niche": "profesionales",
        "accent": "#6366f1",
        "secondary": "#4f46e5",
        "badge": "FIRMA PROFESIONAL & CONSULTORÍA EJECUTIVA",
        "default_business": "Estudio & Consultoría Estratégica Asociados",
        "default_city": "Atención Nacional e Internacional",
        "default_offer": "Sesión de Diagnóstico Fiscal, Legal o Empresarial de 20 Minutos",
        "hero_title": "Protege tu Empresa y Ordena tu Operación con Especialistas Certificados",
        "hero_subtitle": "Completa tu pre-diagnóstico en 45 segundos y nuestro sistema agendará tu sesión ejecutiva con el socio especialista en tu caso.",
        "services": [
            {"icon": "fa-scale-balanced", "title": "Asesoría Corporativa & Blindaje", "desc": "Estructuración legal, contable y financiera para dueños de negocio."},
            {"icon": "fa-chart-line", "title": "Optimización y Crecimiento", "desc": "Planes accionables con seguimiento mensual y reportes claros."},
            {"icon": "fa-video", "title": "Sesión por Zoom o Presencial", "desc": "Reserva tu horario confirmado automáticamente con recordatorio."},
        ],
        "form_questions": [
            "¿Cuál es el principal tema legal, contable o de negocio que necesitas resolver?",
            "¿Eres dueño de negocio/PYME o profesional independiente?",
        ],
    },
    "academia_educacion_cursos": {
        "id": "academia_educacion_cursos",
        "name": "🎓 Academia / Instituto / Infoproductor / Coaching (Dupla C)",
        "dupla": "Dupla C — Profesionales & Academias",
        "niche": "profesionales",
        "accent": "#ec4899",
        "secondary": "#db2777",
        "badge": "ACADEMIA & FORMACIÓN DE ALTO IMPACTO",
        "default_business": "Academia & Instituto de Formación Profesional",
        "default_city": "Online & Presencial",
        "default_offer": "Clase Magistral Gratuita + Entrevista de Admisión con Beca Parcial",
        "hero_title": "Inscríbete Hoy y Recibe el Programa Completo Directo en tu WhatsApp",
        "hero_subtitle": "Nuestro asistente de admisiones responde tus dudas de horarios y certificaciones al instante, de día o de noche.",
        "services": [
            {"icon": "fa-graduation-cap", "title": "Programas Certificados", "desc": "Metodología práctica paso a paso diseñada para resultados rápidos."},
            {"icon": "fa-users", "title": "Mentoría y Comunidad Activa", "desc": "Acompañamiento directo de docentes y tutores especializados."},
            {"icon": "fa-brands fa-whatsapp", "title": "Admisión Rápida por WhatsApp", "desc": "Reserva tu cupo hoy mismo con facilidades de pago."},
        ],
        "form_questions": [
            "¿Qué programa o certificación te interesa cursar este mes?",
            "¿Prefieres modalidad 100% online o híbrida?",
        ],
    },
}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_sales_user(request: Request, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Obtiene el usuario autenticado junto con su rol ('admin', 'supervisor', 'seller', 'operations') y dupla."""
    auth_header = request.headers.get("Authorization")
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    if not token:
        token = request.cookies.get("auth_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión no iniciada. Ingresa en /login."
        )

    session_row = db.query(SessionModel).filter(SessionModel.token == token).first()
    if not session_row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión expirada. Ingresa nuevamente en /login."
        )

    user_row = db.query(User).filter(User.email == session_row.email).first()
    if not user_row or not getattr(user_row, "is_active", 1):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cuenta de usuario inactiva o no encontrada."
        )

    return {
        "email": user_row.email,
        "name": user_row.name,
        "company": user_row.company,
        "phone": user_row.phone,
        "plan": user_row.plan,
        "role": getattr(user_row, "role", "seller") or "seller",
        "dupla": getattr(user_row, "dupla", "Dupla A — Clínicas") or "Dupla A — Clínicas",
        "ghl_user_id": getattr(user_row, "ghl_user_id", "") or "",
        "commission_rate": float(getattr(user_row, "commission_rate", 0.15) or 0.15),
    }


def record_audit(
    db: Session,
    actor_email: str,
    actor_role: str,
    lead_id: Optional[int],
    action: str,
    field_changed: str = "",
    old_value: Any = "",
    new_value: Any = "",
    notes: str = "",
):
    """Guarda un registro inmutable en la tabla audit_logs."""
    now_iso = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    log_entry = AuditLog(
        created_at=now_iso,
        actor_email=actor_email,
        actor_role=actor_role,
        lead_id=lead_id,
        action=action,
        field_changed=field_changed,
        old_value=str(old_value) if old_value is not None else "",
        new_value=str(new_value) if new_value is not None else "",
        notes=notes,
    )
    db.add(log_entry)


def is_contact_excluded(db: Session, email: str, phone: str) -> Optional[str]:
    """Verifica si un correo o teléfono está en la lista DND / Opt-out compartida."""
    em = normalize_email(email)
    ph = normalize_phone_e164(phone)
    if em:
        hit = db.query(DndExclusion).filter(DndExclusion.email == em).first()
        if hit:
            return f"Excluido por DND/Blacklist ({hit.reason})"
    if ph:
        hit_p = db.query(DndExclusion).filter(DndExclusion.phone_e164 == ph).first()
        if hit_p:
            return f"Teléfono excluido por DND ({hit_p.reason})"
    return None


def serialize_lead(r: DbLead) -> Dict[str, Any]:
    """Serializa un objeto Lead con todos los campos canónicos del Sales OS."""
    offer_code = getattr(r, "offer_version", "EXPRESS_497") or "EXPRESS_497"
    offer_info = OFFER_CATALOG.get(offer_code, OFFER_CATALOG["EXPRESS_497"])
    return {
        "id": r.id,
        "name": r.name,
        "full_name": getattr(r, "full_name", None) or r.name,
        "email": r.email,
        "company": r.company or "",
        "business_name": getattr(r, "business_name", None) or (r.company or ""),
        "phone": r.phone or "",
        "phone_e164": getattr(r, "phone_e164", None) or normalize_phone_e164(r.phone or ""),
        "status": r.status,
        "source": r.source,
        "source_channel": getattr(r, "source_channel", "Web") or "Web",
        "source_campaign": getattr(r, "source_campaign", "") or "",
        "interest_primary": getattr(r, "interest_primary", "Sitio Web Inteligente") or "Sitio Web Inteligente",
        "score": r.score,
        "notes": r.notes or "",
        "created_at": r.created_at,
        "contact_id": getattr(r, "contact_id", "") or "",
        "ghl_opportunity_id": getattr(r, "ghl_opportunity_id", "") or "",
        "owner_id": getattr(r, "owner_id", "") or "",
        "setter_id": getattr(r, "setter_id", "") or "",
        "niche": getattr(r, "niche", "clinica") or "clinica",
        "country": getattr(r, "country", "Estados Unidos / LATAM") or "Estados Unidos / LATAM",
        "timezone": getattr(r, "timezone", "America/New_York") or "America/New_York",
        "contact_permission": getattr(r, "contact_permission", "Opt-in verificado") or "Opt-in verificado",
        "contact_status": getattr(r, "contact_status", "contactable") or "contactable",
        "pipeline_stage": getattr(r, "pipeline_stage", "Lead identificado") or "Lead identificado",
        "last_touch": getattr(r, "last_touch", "") or "",
        "next_action_at": getattr(r, "next_action_at", "") or "",
        "next_action_note": getattr(r, "next_action_note", "") or "",
        "offer_version": offer_code,
        "offer_name": offer_info["name"],
        "quoted_amount": float(getattr(r, "quoted_amount", 0.0) or 0.0),
        "contracted_amount": float(getattr(r, "contracted_amount", 0.0) or 0.0),
        "payment_plan": getattr(r, "payment_plan", "50_50") or "50_50",
        "invoice_id": getattr(r, "invoice_id", "") or "",
        "amount_collected": float(getattr(r, "amount_collected", 0.0) or 0.0),
        "commission_base": float(getattr(r, "commission_base", 0.0) or 0.0),
        "commission_setter": float(getattr(r, "commission_setter", 0.0) or 0.0),
        "commission_closer": float(getattr(r, "commission_closer", 0.0) or 0.0),
        "commission_amount": float(getattr(r, "commission_amount", 0.0) or 0.0),
        "commission_status": getattr(r, "commission_status", "sin_devengar") or "sin_devengar",
        "delivery_cost_estimate": float(getattr(r, "delivery_cost_estimate", 100.0) or 100.0),
        "actual_delivery_cost": float(getattr(r, "actual_delivery_cost", 0.0) or 0.0),
        "site_delivery_status": getattr(r, "site_delivery_status", "pendiente_pago") or "pendiente_pago",
        "selected_template": getattr(r, "selected_template", "clinica_dental_estetica") or "clinica_dental_estetica",
        "demo_config_json": getattr(r, "demo_config_json", "{}") or "{}",
    }


# ─── SCHEMAS ────────────────────────────────────────────────────────────────

class SellerCreateOrUpdateRequest(BaseModel):
    email: EmailStr
    name: str
    password: Optional[str] = None
    phone: Optional[str] = ""
    role: Optional[str] = "seller"  # admin, supervisor, seller, operations
    dupla: Optional[str] = "Dupla A — Clínicas (Dental, Estética y Capilar)"
    ghl_user_id: Optional[str] = ""
    is_active: Optional[int] = 1
    commission_rate: Optional[float] = 0.15


class BatchAssignRequest(BaseModel):
    seller_emails: Optional[List[str]] = None
    dupla_filter: Optional[str] = None
    max_per_seller: Optional[int] = 20
    niche_override: Optional[str] = None
    lead_ids: Optional[List[int]] = None


class StageAndProposalUpdateRequest(BaseModel):
    pipeline_stage: str
    offer_version: Optional[str] = "EXPRESS_497"
    quoted_amount: Optional[float] = None
    payment_plan: Optional[str] = "50_50"
    next_action_at: Optional[str] = ""
    next_action_note: Optional[str] = ""
    niche: Optional[str] = None
    selected_template: Optional[str] = None
    demo_config_json: Optional[str] = None
    contact_status: Optional[str] = None
    owner_id: Optional[str] = None
    notes: Optional[str] = None


class PaymentVerificationRequest(BaseModel):
    invoice_id: str
    amount_collected: float
    offer_version: Optional[str] = "EXPRESS_497"
    contracted_amount: Optional[float] = None
    payment_plan: Optional[str] = "50_50_reserva_250_entrega_247"
    setter_id: Optional[str] = None
    selected_template: Optional[str] = "clinica_dental_estetica"
    notes: Optional[str] = ""


class DeliveryStatusUpdateRequest(BaseModel):
    site_delivery_status: str  # pendiente_pago, onboarding, construccion, qa, entregado
    actual_delivery_cost: Optional[float] = None
    commission_status: Optional[str] = None  # causada, pagada, anulada_reembolso
    notes: Optional[str] = ""


# ─── ENDPOINTS DEL SALES OPERATING SYSTEM ───────────────────────────────────

@router.get("/api/sales-os/catalog")
async def api_get_sales_catalog(current_user: dict = Depends(get_current_sales_user)):
    """Devuelve el catálogo oficial versionado, las 11 etapas canónicas y las plantillas de demostración."""
    return {
        "success": True,
        "data": {
            "current_user": current_user,
            "offers": OFFER_CATALOG,
            "canonical_stages": CANONICAL_PIPELINE_STAGES,
            "alternative_stages": ALTERNATIVE_PIPELINE_STAGES,
            "all_stages": ALL_PIPELINE_STAGES,
            "website_templates": WEBSITE_TEMPLATES_SHOWCASE,
            "ghl_config": {
                "location_id": "CNvJBINRWBUL2EdqRh3G",
                "pipeline_id": "SJ4xiMasQ0GZcUNYFgpa",
                "calendar_url": "https://api.leadconnectorhq.com/widget/bookings/calendario-de-edward-jimenez",
            },
        },
    }


@router.get("/api/sales-os/users")
async def api_list_sales_users(
    current_user: dict = Depends(get_current_sales_user),
    db: Session = Depends(get_db),
):
    """Lista los vendedores, supervisores y equipo de operaciones junto con sus métricas reales."""
    users = db.query(User).order_by(User.role.asc(), User.email.asc()).all()
    all_leads = db.query(DbLead).all()

    result = []
    for u in users:
        u_role = getattr(u, "role", "seller") or "seller"
        # Si el usuario que consulta es 'seller', solo ve su propio perfil y nombres básicos para referencia
        my_leads = [l for l in all_leads if (getattr(l, "owner_id", "") or "") == u.email]
        proposals = [
            l for l in my_leads
            if (getattr(l, "pipeline_stage", "") or "") in ("Propuesta enviada", "Pago pendiente", "Pago confirmado", "Implementación", "Entregado")
        ]
        paid_leads = [
            l for l in my_leads
            if float(getattr(l, "amount_collected", 0.0) or 0.0) > 0 and (getattr(l, "invoice_id", "") or "").strip() != ""
        ]
        collected_sum = sum(float(getattr(l, "amount_collected", 0.0) or 0.0) for l in paid_leads)
        comm_accrued = sum(
            float(getattr(l, "commission_amount", 0.0) or 0.0)
            for l in paid_leads
            if (getattr(l, "commission_status", "") or "") in ("causada", "pagada")
        )
        demos_done = sum(
            1 for l in my_leads
            if (getattr(l, "pipeline_stage", "") or "") in ("Demo realizada", "Propuesta enviada", "Pago pendiente", "Pago confirmado", "Implementación", "Entregado")
        )
        diag_booked = sum(
            1 for l in my_leads
            if (getattr(l, "pipeline_stage", "") or "") in ("Diagnóstico agendado", "Demo realizada", "Propuesta enviada", "Pago pendiente", "Pago confirmado", "Implementación", "Entregado")
        )

        result.append({
            "email": u.email,
            "name": u.name,
            "phone": u.phone or "",
            "role": u_role,
            "dupla": getattr(u, "dupla", "Dupla A — Clínicas") or "Dupla A — Clínicas",
            "ghl_user_id": getattr(u, "ghl_user_id", "") or "",
            "is_active": int(getattr(u, "is_active", 1) or 1),
            "commission_rate": float(getattr(u, "commission_rate", 0.15) or 0.15),
            "metrics": {
                "assigned_leads": len(my_leads),
                "diagnostics_booked": diag_booked,
                "demos_completed": demos_done,
                "proposals_sent": len(proposals),
                "paid_deals": len(paid_leads),
                "amount_collected": round(collected_sum, 2),
                "commission_accrued": round(comm_accrued, 2),
                "close_rate_pct": round((len(paid_leads) / len(my_leads) * 100.0), 1) if my_leads else 0.0,
            },
        })

    return {"success": True, "data": {"users": result}}


@router.post("/api/sales-os/users")
async def api_create_or_update_seller(
    req: SellerCreateOrUpdateRequest,
    current_user: dict = Depends(get_current_sales_user),
    db: Session = Depends(get_db),
):
    """Da de alta a un nuevo vendedor/supervisor/operaciones o actualiza sus datos (Solo Admin o Supervisor)."""
    if current_user["role"] not in ("admin", "supervisor"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo Dirección (Admin) o el Supervisor pueden dar de alta o modificar vendedores."
        )

    target_email = normalize_email(req.email)
    now_iso = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    existing = db.query(User).filter(User.email == target_email).first()

    if existing:
        old_role = getattr(existing, "role", "seller")
        existing.name = req.name.strip()
        existing.phone = (req.phone or "").strip()
        existing.dupla = (req.dupla or "Dupla A — Clínicas").strip()
        existing.ghl_user_id = (req.ghl_user_id or "").strip()
        existing.is_active = 1 if req.is_active else 0
        if current_user["role"] == "admin" and req.role:
            existing.role = req.role
        if req.commission_rate is not None:
            existing.commission_rate = float(req.commission_rate)
        if req.password and req.password.strip():
            existing.password = hash_password(req.password.strip())

        record_audit(
            db,
            actor_email=current_user["email"],
            actor_role=current_user["role"],
            lead_id=None,
            action="seller_updated",
            field_changed="users",
            old_value=f"{target_email} ({old_role})",
            new_value=f"{target_email} ({existing.role} | {existing.dupla})",
            notes=f"Vendedor actualizado por {current_user['email']}",
        )
        db.commit()
        return {"success": True, "message": f"Usuario {target_email} actualizado correctamente."}

    raw_password = (req.password or "CloserProsper2026!").strip()
    new_user = User(
        email=target_email,
        name=req.name.strip(),
        password=hash_password(raw_password),
        company="Agencia Prosper IA LLC",
        phone=(req.phone or "").strip(),
        plan="closer_web",
        api_key="",
        role=req.role if current_user["role"] == "admin" else "seller",
        dupla=(req.dupla or "Dupla A — Clínicas").strip(),
        ghl_user_id=(req.ghl_user_id or "").strip(),
        is_active=1 if req.is_active else 0,
        commission_rate=float(req.commission_rate or 0.15),
        created_at=now_iso,
    )
    db.add(new_user)
    record_audit(
        db,
        actor_email=current_user["email"],
        actor_role=current_user["role"],
        lead_id=None,
        action="seller_created",
        field_changed="users",
        old_value="",
        new_value=f"{target_email} ({new_user.role} | {new_user.dupla})",
        notes=f"Alta de vendedor en Sales OS por {current_user['email']}",
    )
    db.commit()
    return {
        "success": True,
        "message": f"Vendedor {req.name} ({target_email}) dado de alta exitosamente en {new_user.dupla}.",
    }


@router.post("/api/sales-os/assign-batch")
async def api_assign_leads_batch(
    req: BatchAssignRequest,
    current_user: dict = Depends(get_current_sales_user),
    db: Session = Depends(get_db),
):
    """Reparte prospectos sin propietario entre los vendedores activos sin duplicar ni incluir DND/Opt-out."""
    if current_user["role"] not in ("admin", "supervisor"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo Dirección o Supervisión pueden distribuir lotes de prospectos."
        )

    # 1. Determinar vendedores destino
    sellers_q = db.query(User).filter(User.role == "seller", User.is_active == 1)
    if req.seller_emails:
        clean_emails = [normalize_email(e) for e in req.seller_emails if e]
        sellers_q = sellers_q.filter(User.email.in_(clean_emails))
    elif req.dupla_filter and req.dupla_filter != "all":
        sellers_q = sellers_q.filter(User.dupla.like(f"%{req.dupla_filter}%"))

    sellers = sellers_q.order_by(User.email.asc()).all()
    if not sellers:
        raise HTTPException(status_code=400, detail="No hay vendedores activos que coincidan con el filtro seleccionado.")

    # 2. Seleccionar leads contactables sin propietario (o los IDs indicados explícitamente)
    leads_q = db.query(DbLead)
    if req.lead_ids:
        leads_q = leads_q.filter(DbLead.id.in_(req.lead_ids))
    else:
        leads_q = leads_q.filter((DbLead.owner_id == None) | (DbLead.owner_id == ""))

    candidate_leads = leads_q.order_by(DbLead.score.desc(), DbLead.id.desc()).all()

    assigned_count = 0
    skipped_dnd = 0
    max_total = (req.max_per_seller or 20) * len(sellers)
    now_iso = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    for ld in candidate_leads:
        if assigned_count >= max_total:
            break
        # Verificar exclusión DND / Opt-out
        dnd_reason = is_contact_excluded(db, ld.email, ld.phone or "")
        c_status = getattr(ld, "contact_status", "contactable") or "contactable"
        stage_now = getattr(ld, "pipeline_stage", "") or ""
        if dnd_reason or c_status in ("dnd", "opt_out", "bounce", "unauthorized") or stage_now == "Opt-out":
            ld.contact_status = "dnd"
            skipped_dnd += 1
            continue

        target_seller = sellers[assigned_count % len(sellers)]
        old_owner = getattr(ld, "owner_id", "") or ""
        ld.owner_id = target_seller.email
        if not getattr(ld, "setter_id", ""):
            ld.setter_id = target_seller.email
        if not getattr(ld, "pipeline_stage", ""):
            ld.pipeline_stage = "Lead identificado"
        if req.niche_override:
            ld.niche = req.niche_override
        elif "Dupla A" in (target_seller.dupla or ""):
            ld.niche = ld.niche or "clinica"
            ld.selected_template = "clinica_dental_estetica"
        elif "Dupla B" in (target_seller.dupla or ""):
            ld.niche = ld.niche or "servicios_locales"
            ld.selected_template = "servicios_locales_taller"
        elif "Dupla C" in (target_seller.dupla or ""):
            ld.niche = ld.niche or "profesionales"
            ld.selected_template = "profesionales_consultoria_legal"

        if not getattr(ld, "offer_version", ""):
            ld.offer_version = "EXPRESS_497"
        ld.last_touch = now_iso

        record_audit(
            db,
            actor_email=current_user["email"],
            actor_role=current_user["role"],
            lead_id=ld.id,
            action="lead_assigned",
            field_changed="owner_id",
            old_value=old_owner or "unassigned",
            new_value=target_seller.email,
            notes=f"Asignación de lote a {target_seller.name} ({target_seller.dupla})",
        )
        assigned_count += 1

    db.commit()
    return {
        "success": True,
        "message": f"Se asignaron {assigned_count} prospectos contactables entre {len(sellers)} vendedor(es). ({skipped_dnd} excluidos por DND/Blacklist).",
        "data": {
            "assigned_count": assigned_count,
            "skipped_dnd": skipped_dnd,
            "sellers_count": len(sellers),
        },
    }


@router.put("/api/sales-os/leads/{lead_id}/stage")
async def api_update_lead_stage_and_proposal(
    lead_id: int,
    req: StageAndProposalUpdateRequest,
    current_user: dict = Depends(get_current_sales_user),
    db: Session = Depends(get_db),
):
    """Actualiza la etapa del pipeline, la propuesta versionada, el siguiente paso y la plantilla del cliente."""
    lead = db.query(DbLead).filter(DbLead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Prospecto no encontrado.")

    # Regla P0 de aislamiento: un vendedor solo puede modificar sus propios prospectos
    if current_user["role"] == "seller" and (getattr(lead, "owner_id", "") or "") != current_user["email"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: este prospecto pertenece a otro vendedor."
        )

    # Regla P0 de cobro verificado: No se puede pasar a 'Pago confirmado', 'Implementación' ni 'Entregado'
    # desde este endpoint si el lead aún no tiene cobro verificado (amount_collected > 0 e invoice_id).
    current_collected = float(getattr(lead, "amount_collected", 0.0) or 0.0)
    current_invoice = (getattr(lead, "invoice_id", "") or "").strip()
    if req.pipeline_stage in ("Pago confirmado", "Implementación", "Entregado") and (current_collected <= 0 or not current_invoice):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Regla P0: No puedes marcar 'Pago confirmado' o 'Implementación' sin registrar primero el Comprobante/Factura (invoice_id) y el Monto Cobrado Verificado (> US$0)."
        )

    now_iso = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    old_stage = getattr(lead, "pipeline_stage", "Lead identificado") or "Lead identificado"
    old_offer = getattr(lead, "offer_version", "EXPRESS_497") or "EXPRESS_497"
    old_quoted = float(getattr(lead, "quoted_amount", 0.0) or 0.0)

    lead.pipeline_stage = req.pipeline_stage
    lead.last_touch = now_iso

    # Sincronizar el campo legacy 'status' para retrocompatibilidad
    if req.pipeline_stage in ("Lead identificado",):
        lead.status = "new"
    elif req.pipeline_stage in ("Primer contacto", "Conversación"):
        lead.status = "contacted"
    elif req.pipeline_stage in ("Calificado", "Diagnóstico agendado", "Demo realizada", "Propuesta enviada", "Pago pendiente"):
        lead.status = "qualified"
    elif req.pipeline_stage in ("Pago confirmado", "Implementación", "Entregado"):
        lead.status = "converted"
    else:
        lead.status = "lost"

    if req.pipeline_stage == "Opt-out" or req.contact_status in ("dnd", "opt_out"):
        lead.contact_status = "opt_out"
        em = normalize_email(lead.email)
        if em and not db.query(DndExclusion).filter(DndExclusion.email == em).first():
            db.add(DndExclusion(
                email=em,
                phone_e164=normalize_phone_e164(lead.phone or ""),
                company=lead.company or "",
                reason=f"Opt-out marcado por {current_user['email']}",
                source="sales_os_opt_out",
                created_at=now_iso,
            ))

    if req.offer_version and req.offer_version in OFFER_CATALOG:
        lead.offer_version = req.offer_version
        catalog_item = OFFER_CATALOG[req.offer_version]
        lead.delivery_cost_estimate = catalog_item["delivery_cost_estimate"]
        if req.quoted_amount is None and req.pipeline_stage in ("Propuesta enviada", "Pago pendiente"):
            lead.quoted_amount = catalog_item["price"]

    if req.quoted_amount is not None:
        lead.quoted_amount = float(req.quoted_amount)

    if req.payment_plan:
        lead.payment_plan = req.payment_plan
    if req.next_action_at is not None:
        lead.next_action_at = req.next_action_at
    if req.next_action_note is not None:
        lead.next_action_note = req.next_action_note
    if req.niche:
        lead.niche = req.niche
    if req.selected_template:
        lead.selected_template = req.selected_template
    if req.demo_config_json:
        lead.demo_config_json = req.demo_config_json
    if req.notes is not None:
        lead.notes = req.notes

    # Solo Admin o Supervisor pueden reasignar el propietario
    if req.owner_id is not None and current_user["role"] in ("admin", "supervisor"):
        old_owner = getattr(lead, "owner_id", "") or ""
        if old_owner != req.owner_id:
            lead.owner_id = req.owner_id
            record_audit(
                db,
                actor_email=current_user["email"],
                actor_role=current_user["role"],
                lead_id=lead.id,
                action="owner_reassigned",
                field_changed="owner_id",
                old_value=old_owner,
                new_value=req.owner_id,
                notes=req.next_action_note or "Reasignación por supervisión",
            )

    record_audit(
        db,
        actor_email=current_user["email"],
        actor_role=current_user["role"],
        lead_id=lead.id,
        action="stage_or_proposal_updated",
        field_changed="pipeline_stage|offer_version|quoted_amount",
        old_value=f"{old_stage} | {old_offer} | US${old_quoted:.2f}",
        new_value=f"{lead.pipeline_stage} | {lead.offer_version} | US${float(lead.quoted_amount or 0):.2f}",
        notes=req.next_action_note or "",
    )

    db.commit()
    db.refresh(lead)

    # Sincronización no bloqueante con GoHighLevel
    sync_sales_os_event_to_ghl_async(
        contact_id=getattr(lead, "contact_id", "") or "",
        opportunity_id=getattr(lead, "ghl_opportunity_id", "") or "",
        email=lead.email,
        phone=lead.phone or "",
        full_name=getattr(lead, "full_name", None) or lead.name,
        business_name=getattr(lead, "business_name", None) or (lead.company or ""),
        pipeline_stage=lead.pipeline_stage,
        owner_email=getattr(lead, "owner_id", "") or current_user["email"],
        offer_version=lead.offer_version,
        quoted_amount=float(lead.quoted_amount or 0.0),
        amount_collected=float(lead.amount_collected or 0.0),
        invoice_id=getattr(lead, "invoice_id", "") or "",
        selected_template=getattr(lead, "selected_template", "") or "",
        audit_summary=req.next_action_note or f"Actualizado por {current_user['name']}",
    )

    return {"success": True, "data": serialize_lead(lead)}


@router.post("/api/sales-os/leads/{lead_id}/verify-payment")
async def api_verify_payment_and_accrue_commission(
    lead_id: int,
    req: PaymentVerificationRequest,
    current_user: dict = Depends(get_current_sales_user),
    db: Session = Depends(get_db),
):
    """Registra un cobro real verificado, activa la comisión del 15% (5% Setter + 10% Closer) y pasa a Onboarding."""
    lead = db.query(DbLead).filter(DbLead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Prospecto no encontrado.")

    if current_user["role"] == "seller" and (getattr(lead, "owner_id", "") or "") != current_user["email"]:
        raise HTTPException(status_code=403, detail="No puedes registrar pagos sobre el prospecto de otro vendedor.")

    clean_invoice = (req.invoice_id or "").strip()
    if not clean_invoice or len(clean_invoice) < 3:
        raise HTTPException(
            status_code=400,
            detail="Debes ingresar un ID de Factura / Comprobante verificable (Hotmart, Stripe, Zelle o Transferencia)."
        )
    if req.amount_collected <= 0:
        raise HTTPException(
            status_code=400,
            detail="El monto efectivamente cobrado (amount_collected) debe ser mayor a US$0.00."
        )

    now_iso = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    offer_code = req.offer_version if req.offer_version in OFFER_CATALOG else (getattr(lead, "offer_version", "EXPRESS_497") or "EXPRESS_497")
    offer_spec = OFFER_CATALOG[offer_code]

    old_collected = float(getattr(lead, "amount_collected", 0.0) or 0.0)
    old_stage = getattr(lead, "pipeline_stage", "") or ""

    lead.offer_version = offer_code
    lead.invoice_id = clean_invoice
    lead.amount_collected = float(req.amount_collected)
    lead.contracted_amount = float(req.contracted_amount) if req.contracted_amount else float(offer_spec["price"])
    if float(getattr(lead, "quoted_amount", 0.0) or 0.0) <= 0:
        lead.quoted_amount = lead.contracted_amount
    lead.payment_plan = req.payment_plan or "50_50_reserva_250_entrega_247"

    if not getattr(lead, "owner_id", ""):
        lead.owner_id = current_user["email"]
    if req.setter_id:
        lead.setter_id = req.setter_id
    elif not getattr(lead, "setter_id", ""):
        lead.setter_id = lead.owner_id

    # Cálculo estricto de comisión 15% sobre dinero REAL cobrado (5% Setter + 10% Closer)
    lead.commission_base = float(req.amount_collected)
    lead.commission_setter = round(lead.commission_base * 0.05, 2)
    lead.commission_closer = round(lead.commission_base * 0.10, 2)
    lead.commission_amount = round(lead.commission_setter + lead.commission_closer, 2)
    lead.commission_status = "causada"

    # Actualizar etapa a Pago confirmado y abrir Onboarding en Operaciones
    lead.pipeline_stage = "Pago confirmado"
    lead.status = "converted"
    lead.site_delivery_status = "onboarding"
    lead.delivery_cost_estimate = float(offer_spec["delivery_cost_estimate"])
    if req.selected_template:
        lead.selected_template = req.selected_template
    lead.last_touch = now_iso
    if req.notes:
        lead.notes = ((lead.notes or "") + f"\n[PAGO VERIFICADO {now_iso}]: Factura {clean_invoice} por US${req.amount_collected:.2f}. {req.notes}").strip()

    record_audit(
        db,
        actor_email=current_user["email"],
        actor_role=current_user["role"],
        lead_id=lead.id,
        action="payment_verified_and_commission_accrued",
        field_changed="amount_collected|invoice_id|commission_amount|site_delivery_status",
        old_value=f"US${old_collected:.2f} | {old_stage}",
        new_value=f"US${lead.amount_collected:.2f} (Ref: {clean_invoice}) | Comisión 15%: US${lead.commission_amount:.2f} | Onboarding",
        notes=req.notes or "Alta de cliente con pago verificado",
    )

    db.commit()
    db.refresh(lead)

    sync_sales_os_event_to_ghl_async(
        contact_id=getattr(lead, "contact_id", "") or "",
        opportunity_id=getattr(lead, "ghl_opportunity_id", "") or "",
        email=lead.email,
        phone=lead.phone or "",
        full_name=getattr(lead, "full_name", None) or lead.name,
        business_name=getattr(lead, "business_name", None) or (lead.company or ""),
        pipeline_stage="Pago confirmado",
        owner_email=lead.owner_id,
        offer_version=lead.offer_version,
        quoted_amount=float(lead.quoted_amount or 0.0),
        amount_collected=float(lead.amount_collected or 0.0),
        invoice_id=lead.invoice_id,
        selected_template=lead.selected_template,
        audit_summary=f"PAGO VERIFICADO ({clean_invoice}): US${lead.amount_collected:.2f}. Comisión 15% causada: US${lead.commission_amount:.2f}. Enviado a Operaciones (Onboarding).",
    )

    return {
        "success": True,
        "message": f"Pago verificado (Ref: {clean_invoice}). Comisión 15% causada: US${lead.commission_amount:.2f} (US${lead.commission_setter:.2f} Setter + US${lead.commission_closer:.2f} Closer). Cliente enviado a Onboarding de Ingeniería.",
        "data": serialize_lead(lead),
    }


@router.put("/api/sales-os/leads/{lead_id}/delivery")
async def api_update_delivery_and_commission_settlement(
    lead_id: int,
    req: DeliveryStatusUpdateRequest,
    current_user: dict = Depends(get_current_sales_user),
    db: Session = Depends(get_db),
):
    """Permite a Operaciones o Dirección actualizar el estado de entrega del Sitio Web y liquidar comisiones."""
    if current_user["role"] not in ("admin", "supervisor", "operations"):
        raise HTTPException(
            status_code=403,
            detail="Solo Operaciones, Supervisión o Dirección pueden modificar el estado de entrega o liquidación."
        )

    lead = db.query(DbLead).filter(DbLead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Cliente/Prospecto no encontrado.")

    old_delivery = getattr(lead, "site_delivery_status", "pendiente_pago")
    old_comm_status = getattr(lead, "commission_status", "sin_devengar")

    lead.site_delivery_status = req.site_delivery_status
    if req.site_delivery_status in ("onboarding", "construccion", "qa"):
        lead.pipeline_stage = "Implementación"
    elif req.site_delivery_status == "entregado":
        lead.pipeline_stage = "Entregado"

    if req.actual_delivery_cost is not None:
        lead.actual_delivery_cost = float(req.actual_delivery_cost)

    if req.commission_status and current_user["role"] == "admin":
        lead.commission_status = req.commission_status
        if req.commission_status == "anulada_reembolso":
            lead.pipeline_stage = "Reembolso/contracargo"
            lead.status = "lost"
            lead.commission_amount = 0.0
            lead.commission_setter = 0.0
            lead.commission_closer = 0.0

    record_audit(
        db,
        actor_email=current_user["email"],
        actor_role=current_user["role"],
        lead_id=lead.id,
        action="delivery_or_settlement_updated",
        field_changed="site_delivery_status|commission_status",
        old_value=f"{old_delivery} | {old_comm_status}",
        new_value=f"{lead.site_delivery_status} | {lead.commission_status}",
        notes=req.notes or "",
    )
    db.commit()
    db.refresh(lead)
    return {"success": True, "data": serialize_lead(lead)}


@router.get("/api/sales-os/metrics")
async def api_get_sales_os_metrics(
    current_user: dict = Depends(get_current_sales_user),
    db: Session = Depends(get_db),
):
    """Calcula el Tablero de Dirección y el Tablero del Vendedor separando estrictamente propuestas de cobros reales."""
    all_leads = db.query(DbLead).all()

    # Filtrar según el rol para las métricas personales del vendedor
    if current_user["role"] == "seller":
        scoped_leads = [l for l in all_leads if (getattr(l, "owner_id", "") or "") == current_user["email"]]
    else:
        scoped_leads = all_leads

    # Clasificación financiera real (sin confundir propuestas con facturación/cobro)
    quoted_total = 0.0
    contracted_total = 0.0
    collected_total = 0.0
    commissions_accrued = 0.0
    commissions_paid = 0.0
    variable_delivery_costs = 0.0

    stage_counts = {st: 0 for st in ALL_PIPELINE_STAGES}
    by_offer = {k: {"count": 0, "quoted": 0.0, "collected": 0.0} for k in OFFER_CATALOG.keys()}
    without_next_step = 0
    dnd_excluded_count = 0
    paid_deals_count = 0

    for l in scoped_leads:
        c_status = getattr(l, "contact_status", "contactable") or "contactable"
        if c_status in ("dnd", "opt_out", "bounce", "unauthorized"):
            dnd_excluded_count += 1

        st = getattr(l, "pipeline_stage", "Lead identificado") or "Lead identificado"
        stage_counts[st] = stage_counts.get(st, 0) + 1

        # Si está en una etapa activa de seguimiento y no tiene next_action_at
        if st in CANONICAL_PIPELINE_STAGES[:-1] and not (getattr(l, "next_action_at", "") or "").strip():
            without_next_step += 1

        q_amt = float(getattr(l, "quoted_amount", 0.0) or 0.0)
        c_amt = float(getattr(l, "contracted_amount", 0.0) or 0.0)
        col_amt = float(getattr(l, "amount_collected", 0.0) or 0.0)
        inv = (getattr(l, "invoice_id", "") or "").strip()
        offer_k = getattr(l, "offer_version", "EXPRESS_497") or "EXPRESS_497"

        if q_amt > 0:
            quoted_total += q_amt
        if c_amt > 0 and inv:
            contracted_total += c_amt
        if col_amt > 0 and inv and st != "Reembolso/contracargo":
            collected_total += col_amt
            paid_deals_count += 1
            comm_amt = float(getattr(l, "commission_amount", 0.0) or 0.0)
            comm_st = getattr(l, "commission_status", "causada") or "causada"
            if comm_st == "pagada":
                commissions_paid += comm_amt
            elif comm_st == "causada":
                commissions_accrued += comm_amt

            act_cost = float(getattr(l, "actual_delivery_cost", 0.0) or 0.0)
            est_cost = float(getattr(l, "delivery_cost_estimate", 100.0) or 100.0)
            variable_delivery_costs += (act_cost if act_cost > 0 else est_cost)

        if offer_k in by_offer:
            if q_amt > 0 or col_amt > 0:
                by_offer[offer_k]["count"] += 1
                by_offer[offer_k]["quoted"] = round(by_offer[offer_k]["quoted"] + q_amt, 2)
                by_offer[offer_k]["collected"] = round(by_offer[offer_k]["collected"] + col_amt, 2)

    total_commissions = commissions_accrued + commissions_paid
    net_contribution = collected_total - total_commissions - variable_delivery_costs
    fixed_expenses = 6000.0
    gap_to_break_even = max(0.0, fixed_expenses - max(0.0, net_contribution))
    # Contribución unitaria neta de 1 Express ($497 - $74.55 com - $100 costo = $322.45)
    express_unit_margin = 322.45
    express_sales_needed = int((gap_to_break_even / express_unit_margin) + 0.999) if gap_to_break_even > 0 else 0

    contactable_count = max(1, len(scoped_leads) - dnd_excluded_count)
    close_rate = round((paid_deals_count / contactable_count) * 100.0, 2) if scoped_leads else 0.0

    return {
        "success": True,
        "data": {
            "role_scope": current_user["role"],
            "user_email": current_user["email"],
            "total_leads_in_scope": len(scoped_leads),
            "contactable_leads": len(scoped_leads) - dnd_excluded_count,
            "dnd_excluded_leads": dnd_excluded_count,
            "leads_without_next_step": without_next_step,
            "paid_deals_count": paid_deals_count,
            "close_rate_pct": close_rate,
            "financials": {
                "quoted_open_amount": round(quoted_total, 2),
                "contracted_amount": round(contracted_total, 2),
                "amount_collected_verified": round(collected_total, 2),
                "commissions_accrued_pending": round(commissions_accrued, 2),
                "commissions_paid": round(commissions_paid, 2),
                "variable_delivery_costs": round(variable_delivery_costs, 2),
                "net_contribution": round(net_contribution, 2),
                "fixed_monthly_expenses": fixed_expenses,
                "gap_to_break_even": round(gap_to_break_even, 2),
                "express_497_sales_needed_for_breakeven": express_sales_needed,
            },
            "stage_breakdown": stage_counts,
            "by_offer": by_offer,
        },
    }


@router.get("/api/sales-os/audit-logs")
async def api_get_audit_logs(
    limit: int = 80,
    lead_id: Optional[int] = None,
    current_user: dict = Depends(get_current_sales_user),
    db: Session = Depends(get_db),
):
    """Devuelve el historial de auditoría de cambios en etapas, precios, asignaciones y pagos."""
    q = db.query(AuditLog)
    if lead_id is not None:
        q = q.filter(AuditLog.lead_id == lead_id)
    elif current_user["role"] == "seller":
        q = q.filter(AuditLog.actor_email == current_user["email"])

    rows = q.order_by(AuditLog.id.desc()).limit(limit).all()
    logs = [
        {
            "id": r.id,
            "created_at": r.created_at,
            "actor_email": r.actor_email,
            "actor_role": r.actor_role,
            "lead_id": r.lead_id,
            "action": r.action,
            "field_changed": r.field_changed,
            "old_value": r.old_value,
            "new_value": r.new_value,
            "notes": r.notes,
        }
        for r in rows
    ]
    return {"success": True, "data": {"logs": logs}}


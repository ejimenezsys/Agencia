import os
import re
import sqlite3
import hashlib
import hmac
import secrets
import json
import gzip
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, func
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
        # Alias de cortesía para pruebas de Closers y Socios (Closer2026! / BeautyGrowth2026! / DavidProsper2026!)
        if password in ("BeautyGrowth2026!", "DavidProsper2026!"):
            alt_candidate = hashlib.pbkdf2_hmac(
                "sha256", b"Digital2@26@", bytes.fromhex(salt_hex), int(iterations)
            )
            if hmac.compare_digest(alt_candidate.hex(), digest_hex):
                return True
        if password in (
            "SheilleProsper2026!",
            "DiegoProsper2026!",
            "CloserProsper2026!",
            "Closer2026!",
            "BeautyGrowth2026!",
            "DavidProsper2026!",
        ):
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


def _is_callable_zero_cost_from_argentina(country: str, phone: str, phone_e164: str) -> bool:
    """Valida si el negocio tiene línea móvil con WhatsApp (MX/CO/PE/CL/ES) o línea nacional Argentina (+54) a costo $0."""
    digits = re.sub(r"\D", "", str(phone_e164 or phone or ""))
    c = (country or "").strip().lower()
    if not digits or len(digits) < 9:
        return False
    # Excluir EE. UU. / Canadá / Puerto Rico (+1) — teléfonos fijos de oficina en inglés o SMS pagado
    if digits.startswith("1") and len(digits) == 11:
        return False
    if "argent" in c or digits.startswith("54"):
        return len(digits) >= 10
    if "colomb" in c or digits.startswith("57"):
        rest = digits[2:] if digits.startswith("57") else digits
        return len(rest) == 10 and rest.startswith("3")
    if "per" in c or digits.startswith("51"):
        rest = digits[2:] if digits.startswith("51") else digits
        return len(rest) == 9 and rest.startswith("9")
    if "chile" in c or digits.startswith("56"):
        rest = digits[2:] if digits.startswith("56") else digits
        return len(rest) == 9 and rest.startswith("9")
    if "espa" in c or digits.startswith("34"):
        rest = digits[2:] if digits.startswith("34") else digits
        return len(rest) == 9 and rest[0] in ("6", "7")
    if "méx" in c or "mex" in c or digits.startswith("52"):
        rest = digits[3:] if digits.startswith("521") else (digits[2:] if digits.startswith("52") else digits)
        return len(rest) == 10 and not rest.startswith("800")
    return False


_FREEBIE_BAD_SOURCES = {
    "hub_codigos_comunidad",
    "ghl_516_pool",
    "ghl_455_pool",
    "emprendeprosperia_funnel",
    "exmaboletos_20off",
}
_FREEBIE_TEXT_TOKENS = (
    "profesional / alumno ia",
    "profesional alumno ia",
    "alumno ia",
    "passportai trial",
    "negocio / profesional por calificar",
    "empresa / negocio calificado",
    "prueba pixel",
    "cliente-demo",
    "recurso gratis",
)
_PLACEHOLDER_BIZ_NAMES = {
    "closer",
    "agencia",
    "agencia prosperia",
    "prosperia",
    "por definir",
    "n/a",
    "sin empresa",
}
_CLOSER_TEST_EMAILS = {
    "claudiniosan@yahoo.com.ar",
    "diegoarriondo03@gmail.com",
    "digitalblups@gmail.com",
    "wendyleiva59@gmail.com",
    "tanyah.unity@gmail.com",
    "cinthyapenida0@gmail.com",
    "bruno.hernan.espinosa1694@gmail.com",
    "bruno.hernan.espinosa9416@gmail.com",
    "loremrodriguezafb@gmail.com",
    "laverdaderafuerza02@gmail.com",
    "sheille.perez@gmail.com",
    "edward@agenciaprosperia.com",
    "admin@prosperia.com",
    "ejimenezsys@icloud.com",
    "maria@cliente-demo.com",
    "espitia.network@gmail.com",
}
_CLOSER_TEST_NAMES = {
    "bruno espinosa",
    "bruno hernan espinosa",
    "lorena meriel",
    "lorena rodriguez",
    "edward jimenez",
    "agencia prosperia",
    "prueba pixel",
}
_CLOSER_TEST_PHONE_TAILS = ("1135992614", "3885862967", "7865573119", "7869828707", "1155554444")
_WA_AUTO_NOTE_TOKENS = (
    "WhatsApp Agencia +1 786",
    "🤖 Setter IA Demo Enviada",
    "🔥 RESPONDIÓ A SETTER IA",
    "Plantilla reactivacion_",
)


def _is_freebie_or_closer_test_lead(ld) -> bool:
    """Identifica leads gratuitos (/codigos, Alumno IA, PassportAI Trial) y registros de prueba de Closers."""
    src = (getattr(ld, "source", "") or "").strip().lower()
    if src in _FREEBIE_BAD_SOURCES:
        return True

    biz = (getattr(ld, "business_name", "") or "").strip().lower()
    comp = (getattr(ld, "company", "") or "").strip().lower()
    nm = (getattr(ld, "name", "") or "").strip().lower()
    fnm = (getattr(ld, "full_name", "") or "").strip().lower()
    if biz in _PLACEHOLDER_BIZ_NAMES or comp in _PLACEHOLDER_BIZ_NAMES:
        return True
    if nm in _CLOSER_TEST_NAMES or fnm in _CLOSER_TEST_NAMES:
        return True

    em = normalize_email(getattr(ld, "email", "") or "")
    if em in _CLOSER_TEST_EMAILS or em.endswith("@cliente-demo.com"):
        return True

    text_fields = (
        biz,
        comp,
        nm,
        fnm,
        (getattr(ld, "interest_primary", "") or "").strip().lower(),
        (getattr(ld, "source_campaign", "") or "").strip().lower(),
    )
    if any(tok in val for val in text_fields for tok in _FREEBIE_TEXT_TOKENS):
        return True

    digits = re.sub(r"\D", "", str(getattr(ld, "phone_e164", None) or getattr(ld, "phone", None) or ""))
    if digits and any(digits.endswith(tail) for tail in _CLOSER_TEST_PHONE_TAILS):
        return True

    return False


def _real_email_pool(em_val: str) -> str:
    """Devuelve email real deduplicable para Bolsa 500 o cadena vacía si es sintético/local."""
    em_c = normalize_email(em_val or "")
    if (
        em_c
        and "@" in em_c
        and not em_c.endswith(".local")
        and "sin-correo" not in em_c
        and "noemail" not in em_c
        and not (
            (em_c.startswith("prospecto.") or em_c.startswith("prospecto_") or em_c.startswith("lote."))
            and em_c.endswith("@agenciaprosperia.com")
        )
    ):
        return em_c
    return ""


def _trim_lead_old_wa_notes(ld) -> bool:
    """Compacta historiales automáticos de WhatsApp en bitácora dejando solo el último renglón útil."""
    raw_notes = getattr(ld, "notes", "") or ""
    if not raw_notes.strip():
        return False
    static_lines = []
    bitacora_lines = []
    for ln in raw_notes.splitlines():
        if ln.strip().startswith("[20"):
            bitacora_lines.append(ln)
        else:
            static_lines.append(ln)
    if len(bitacora_lines) <= 1:
        return False

    is_owned = bool((getattr(ld, "owner_id", "") or "").strip())
    if not is_owned:
        last_line = re.sub(r"\bShey:\s*", "Nota previa: ", bitacora_lines[-1], flags=re.IGNORECASE)
        kept_bitacora = [last_line]
    else:
        human_lines = [b for b in bitacora_lines if not any(tok in b for tok in _WA_AUTO_NOTE_TOKENS)]
        auto_lines = [b for b in bitacora_lines if any(tok in b for tok in _WA_AUTO_NOTE_TOKENS)]
        kept_bitacora = list(human_lines)
        if auto_lines and not human_lines:
            kept_bitacora = [auto_lines[-1]]
        elif auto_lines and human_lines:
            last_auto_idx = max(i for i, b in enumerate(bitacora_lines) if any(tok in b for tok in _WA_AUTO_NOTE_TOKENS))
            last_human_idx = max(i for i, b in enumerate(bitacora_lines) if not any(tok in b for tok in _WA_AUTO_NOTE_TOKENS))
            if last_auto_idx > last_human_idx:
                kept_bitacora.append(bitacora_lines[last_auto_idx])

    if kept_bitacora != bitacora_lines:
        ld.notes = "\n".join(static_lines + kept_bitacora).strip()
        return True
    return False


def _strip_unreplied_bot_email_lines(ld) -> bool:
    """Elimina líneas muertas de '🤖 Setter IA Correo' en leads sin respuesta ('RESPONDIÓ')."""
    raw_notes = getattr(ld, "notes", "") or ""
    if not raw_notes or "🤖 Setter IA Correo" not in raw_notes or "RESPONDIÓ" in raw_notes:
        return False
    kept_lines = [ln for ln in raw_notes.splitlines() if "🤖 Setter IA Correo" not in ln]
    cleaned = "\n".join(kept_lines).strip()
    if cleaned != raw_notes.strip():
        ld.notes = cleaned
        return True
    return False


def _topup_free_pool_to_target(db, target: int = 500) -> tuple:
    """Recuenta activos/duplicados y rellena la Bolsa Libre hasta `target` desde archivo_reserva."""
    remaining_all = db.query(Lead).all()
    seen_phones = set()
    seen_emails = set()
    seen_biz = set()
    current_free_cnt = 0

    for ld in remaining_all:
        c_st = (getattr(ld, "contact_status", "contactable") or "contactable").lower()
        if c_st in ("archivo_reserva", "dnd", "opt_out", "bounce", "unauthorized"):
            continue
        if not (getattr(ld, "owner_id", "") or "").strip() and c_st == "contactable":
            current_free_cnt += 1
        digits = re.sub(r"\D", "", str(getattr(ld, "phone_e164", None) or getattr(ld, "phone", None) or ""))
        if len(digits) >= 9:
            seen_phones.add(digits[-10:])
        em_ok = _real_email_pool(getattr(ld, "email", "") or "")
        if em_ok:
            seen_emails.add(em_ok)
        biz_ok = (getattr(ld, "business_name", None) or getattr(ld, "company", None) or "").strip().lower()
        if biz_ok and biz_ok not in _PLACEHOLDER_BIZ_NAMES:
            seen_biz.add(biz_ok)

    promoted_cnt = 0
    if current_free_cnt < target:
        needed = target - current_free_cnt
        archived_pool = [
            ld for ld in remaining_all
            if (getattr(ld, "contact_status", "") or "").lower() == "archivo_reserva"
        ]
        promotions = _select_pool_candidates(
            archived_pool,
            seen_phones=seen_phones,
            seen_emails=seen_emails,
            seen_biz=seen_biz,
            limit=needed,
            require_real_biz=True,
        )
        for ld in promotions:
            ld.owner_id = ""
            ld.setter_id = ""
            ld.pipeline_stage = "Lead identificado"
            ld.status = "new"
            ld.contact_status = "contactable"
            _strip_unreplied_bot_email_lines(ld)
            _trim_lead_old_wa_notes(ld)
            promoted_cnt += 1

    return promoted_cnt, current_free_cnt + promoted_cnt


def _select_pool_candidates(
    leads_iterable,
    seen_phones: set,
    seen_emails: set,
    seen_biz: set,
    limit: int,
    skip_ids: set = None,
    require_real_biz: bool = False,
) -> list:
    """Selecciona y puntúa los mejores negocios B2B $0 desde Argentina sin duplicados ni freebies."""
    closed_out_stages = {"No interesado", "No cumple perfil", "Opt-out", "Venta perdida"}
    candidates = []
    skip_set = skip_ids or set()
    for ld in leads_iterable:
        if ld.id in skip_set or _is_freebie_or_closer_test_lead(ld):
            continue
        if (getattr(ld, "source", "") or "").strip().lower() == "comex_outbound_b2b":
            continue
        c_st = (getattr(ld, "contact_status", "contactable") or "contactable").lower()
        if c_st in ("dnd", "opt_out", "bounce", "unauthorized"):
            continue
        stg = (getattr(ld, "pipeline_stage", "Lead identificado") or "Lead identificado").strip()
        if stg in closed_out_stages:
            continue
        ph = getattr(ld, "phone", "") or ""
        ph164 = getattr(ld, "phone_e164", "") or ""
        country = getattr(ld, "country", "") or ""
        if not _is_callable_zero_cost_from_argentina(country, ph, ph164):
            continue
        digits = re.sub(r"\D", "", str(ph164 or ph))
        key_ph = digits[-10:]
        if not key_ph or key_ph in seen_phones:
            continue
        em_ok = _real_email_pool(getattr(ld, "email", "") or "")
        if em_ok and em_ok in seen_emails:
            continue
        biz_ok = (getattr(ld, "business_name", None) or getattr(ld, "company", None) or "").strip().lower()
        if require_real_biz and (not biz_ok or biz_ok in _PLACEHOLDER_BIZ_NAMES):
            continue
        if biz_ok and biz_ok not in _PLACEHOLDER_BIZ_NAMES and biz_ok in seen_biz:
            continue

        txt = f"{getattr(ld, 'source_campaign', '') or ''} {getattr(ld, 'notes', '') or ''}"
        src = (getattr(ld, "source", "") or "").lower()
        is_hot = (src != "apify_sprint_nov18") or ("🔥" in txt) or ("Caliente" in txt) or ("RESPONDIÓ" in txt)
        no_web = "SIN SITIO WEB" in txt
        web_no_ai = ("WEB SIN IA" in txt) or ("LÍDER" in txt)
        niche_val = (getattr(ld, "niche", "") or "").lower()
        score_val = int(getattr(ld, "score", 0) or 0)
        prio = (
            (200 if is_hot else 0)
            + (80 if no_web else (55 if web_no_ai else 0))
            + (60 if em_ok else 0)
            + (15 if niche_val in ("clinica", "inmobiliaria") else 0)
            + (score_val // 10)
        )
        candidates.append((prio, ld, key_ph, em_ok, biz_ok))

    candidates.sort(key=lambda item: item[0], reverse=True)
    selected = []
    for _prio, ld, key_ph, em_ok, biz_ok in candidates:
        if len(selected) >= limit:
            break
        if key_ph in seen_phones:
            continue
        if em_ok and em_ok in seen_emails:
            continue
        if biz_ok and biz_ok not in _PLACEHOLDER_BIZ_NAMES and biz_ok in seen_biz:
            continue
        seen_phones.add(key_ph)
        if em_ok:
            seen_emails.add(em_ok)
        if biz_ok and biz_ok not in _PLACEHOLDER_BIZ_NAMES:
            seen_biz.add(biz_ok)
        selected.append(ld)
    return selected


# Catálogo Oficial Versionado (Sección 2 del Brief Operativo)
OFFER_CATALOG = {
    "EXPRESS_497": {
        "code": "EXPRESS_497",
        "name": "1. Plan Arranque Rápido (US$497 Anual o US$49/mes)",
        "price": 497.0,
        "monthly_price": 49.0,
        "initial_payment": 250.0,
        "delivery_payment": 247.0,
        "payment_terms": "Pago Único Anual US$497 (o US$250 hoy + US$247 entrega) · O Renta Mensual US$49/mes. Incluye dominio .com alojado en Agencia Prosper IA + Bandeja Unificada + 15 Guiones + 5 Reels.",
        "delivery_cost_estimate": 100.0,
        "requires_director_approval": False,
        "link_reserva_50": "https://api.agenciaprosperia.com/payment-link/6af2287303c375ed645fe629",
        "link_liquidacion_50": "https://api.agenciaprosperia.com/payment-link/6af2289003c375ed645fe62a",
        "link_unico_100": "https://api.agenciaprosperia.com/payment-link/6af228ba03c375ed645fe62d",
        "whop_reserva_50": "https://whop.com/checkout/ch_xQflGEnePudxbjw/",
        "whop_liquidacion_50": "https://whop.com/checkout/ch_92aSdDc7D7MlELy/",
        "whop_unico_100": "https://whop.com/checkout/ch_JNFzIX0aWE7jNZN/",
        "scope": "Sitio Web Inteligente + Tu propio dominio .com conectado y alojado en servidores de Agencia Prosper IA + Bandeja Unificada Multicanal (ProsperIA CRM) + Calendario y Reseñas Google + 15 Guiones Ganadores + 5 Ediciones de Videos de Reels."
    },
    "MENSUAL_49": {
        "code": "MENSUAL_49",
        "name": "1. Plan Arranque Rápido — Renta Mensual (US$49/mes)",
        "price": 49.0,
        "monthly_price": 49.0,
        "initial_payment": 49.0,
        "delivery_payment": 0.0,
        "payment_terms": "Renta Mensual US$49 USD/mes (o Pago Anual con ahorro US$497).",
        "delivery_cost_estimate": 15.0,
        "requires_director_approval": False,
        "scope": "Sitio Web Inteligente + Dominio .com alojado en servidores de Agencia Prosper IA + Bandeja Unificada Multicanal + 15 Guiones Ganadores + 5 Ediciones de Reels al mes."
    },
    "ANUAL_990": {
        "code": "ANUAL_990",
        "name": "2. Pack Estrella Anual (US$990 Anual o US$99/mes · El Más Elegido)",
        "price": 990.0,
        "monthly_price": 99.0,
        "initial_payment": 495.0,
        "delivery_payment": 495.0,
        "payment_terms": "Pago Único Anual US$990 (o US$495 hoy + US$495 entrega) · O Renta Mensual US$99/mes (igual que PassportAI.app). Ahorras 2 meses al pagar el año.",
        "delivery_cost_estimate": 150.0,
        "requires_director_approval": False,
        "link_reserva_50": "https://api.agenciaprosperia.com/payment-link/6af227a4d4cfb789aef22986",
        "link_liquidacion_50": "https://api.agenciaprosperia.com/payment-link/6af227c7d4cfb789aef22989",
        "link_unico_100": "https://api.agenciaprosperia.com/payment-link/6af227ecd4cfb789aef2298d",
        "whop_reserva_50": "https://whop.com/checkout/ch_q4TXGYQSzBGkQSY/",
        "whop_liquidacion_50": "https://whop.com/checkout/ch_rkUci9bt0JLBW1S/",
        "whop_unico_100": "https://whop.com/checkout/ch_4vhuNtpWoJFUYkH/",
        "scope": "Todo lo de Arranque Rápido (Dominio .com alojado en Agencia Prosper IA + Bandeja Unificada CRM) + Recepcionista y Vendedor IA 24/7 en Texto (WhatsApp/IG/FB/Web) + 30 Guiones Ganadores + 15 Ediciones de Videos de Reels para todo el mes + PassportAI Business."
    },
    "MENSUAL_99": {
        "code": "MENSUAL_99",
        "name": "2. Pack Estrella — Renta Mensual (US$99/mes)",
        "price": 99.0,
        "monthly_price": 99.0,
        "initial_payment": 99.0,
        "delivery_payment": 0.0,
        "payment_terms": "Renta Mensual US$99 USD/mes (empatado con PassportAI.app; o Pago Anual US$990 con 2 meses gratis).",
        "delivery_cost_estimate": 25.0,
        "requires_director_approval": False,
        "scope": "Dominio .com alojado en Agencia Prosper IA + Bandeja Unificada + Recepcionista IA 24/7 en Texto + 30 Guiones Ganadores + 15 Ediciones de Videos de Reels al mes + PassportAI."
    },
    "MAQUINA_1490": {
        "code": "MAQUINA_1490",
        "name": "3. Máquina Completa Empresarial (US$1,497 Anual o US$149/mes)",
        "price": 1497.0,
        "monthly_price": 149.0,
        "initial_payment": 749.0,
        "delivery_payment": 748.0,
        "payment_terms": "Pago Único Anual US$1,497 (o 50/50 en 2 cuotas) · O Renta Mensual US$149/mes. Incluye Voz IA 24/7 Bilingüe + Multi-Vendedor + 30 Guiones y 30 Videos Reels/Carruseles.",
        "delivery_cost_estimate": 300.0,
        "requires_director_approval": True,
        "link_reserva_50": "https://api.agenciaprosperia.com/payment-link/6af22915d4cfb789aef2299b",
        "link_liquidacion_50": "https://api.agenciaprosperia.com/payment-link/6af22943d4cfb789aef2299d",
        "link_unico_100": "https://api.agenciaprosperia.com/payment-link/6af2297ad4cfb789aef229a0",
        "whop_reserva_50": "https://whop.com/checkout/ch_U26FriHORRYQczG/",
        "whop_liquidacion_50": "https://whop.com/checkout/ch_aiwdfkuGAcREozG/",
        "whop_unico_100": "https://whop.com/checkout/ch_fBPqhdK2KhpHPkb/",
        "scope": "Todo lo del Pack Estrella (Dominio .com alojado en Agencia Prosper IA + Bandeja Unificada + Chat IA 24/7) + Recepcionista Telefónica de Voz con IA 24/7 (Español e Inglés) + Reparto Automático entre Múltiples Vendedores o Sedes + 30 Guiones Ganadores + 30 Videos Editados para Reels y Carruseles + PassportAI (+58 modelos IA)."
    },
    "MENSUAL_149": {
        "code": "MENSUAL_149",
        "name": "3. Máquina Completa Empresarial — Renta Mensual (US$149/mes)",
        "price": 149.0,
        "monthly_price": 149.0,
        "initial_payment": 149.0,
        "delivery_payment": 0.0,
        "payment_terms": "Renta Mensual US$149 USD/mes (o Pago Único Anual US$1,497).",
        "delivery_cost_estimate": 45.0,
        "requires_director_approval": False,
        "scope": "Dominio .com alojado en Agencia Prosper IA + Bandeja Unificada + Recepcionista Telefónica de Voz con IA 24/7 (ES/EN) + Reparto Automático Multi-Vendedor/Multi-Sede + 30 Guiones + 30 Videos Editados para Reels y Carruseles + PassportAI (+58 modelos)."
    },
    "AGENCIA_VIRAL_1": {
        "code": "AGENCIA_VIRAL_1",
        "name": "Agencia Viral 1 · Viral Remoto + Trafficker (US$797 LATAM / US$997 USA al mes)",
        "price": 797.0,
        "monthly_price": 797.0,
        "usa_monthly_price": 997.0,
        "initial_payment": 797.0,
        "delivery_payment": 0.0,
        "payment_terms": "Renta Mensual US$797/mes (LATAM) · US$997/mes (USA) | Programa 2 Meses: US$1,497 (LATAM) / US$1,890 (USA). Pauta de Meta Ads aparte.",
        "delivery_cost_estimate": 240.0,
        "requires_director_approval": False,
        "scope": "Exclusivo para clientes que YA tienen Web, Chatbot y CRM: 20 Guiones Virales (Hook 3s + 7 Beats) + 1 Sesión Mensual de Dirección por Zoom + 16 Reels Editados Pro (4/semana) + 8 Carruseles + Publicación IG/FB/TikTok + Trafficker Meta Ads todo el mes."
    },
    "AGENCIA_VIRAL_2": {
        "code": "AGENCIA_VIRAL_2",
        "name": "Agencia Viral 2 · Agencia Viral 360° (US$1,497/mes · 30 Piezas + Trafficker Pro)",
        "price": 1497.0,
        "monthly_price": 1497.0,
        "initial_payment": 1497.0,
        "delivery_payment": 0.0,
        "payment_terms": "Renta Mensual US$1,497/mes (Miami & LATAM) | Programa 2 Meses: US$2,690 (Ahorra US$304). Pauta publicitaria aparte.",
        "delivery_cost_estimate": 420.0,
        "requires_director_approval": False,
        "scope": "Exclusivo para clientes que YA tienen Web, Chatbot y CRM: 30 Guiones Virales Ganadores (1 diario) + 30 Piezas Editadas Profesionales/mes (20 Reels dinámicos + 10 Carruseles/Creativos Ads) + Gestión y Publicación Diaria Completa (IG, FB, TikTok, Shorts) + Trafficker Pro Meta & IG Ads (pruebas A/B 4 ganchos/sem + escalamiento + ROAS quincenal)."
    },
    "AGENCIA_VIRAL_3": {
        "code": "AGENCIA_VIRAL_3",
        "name": "Agencia Viral 3 · VIP Filmmaker Presencial + Trafficker (US$2,497 Miami / US$1,897 LATAM al mes)",
        "price": 2497.0,
        "monthly_price": 2497.0,
        "latam_monthly_price": 1897.0,
        "initial_payment": 2497.0,
        "delivery_payment": 0.0,
        "payment_terms": "Renta Mensual US$2,497/mes (Miami) · US$1,897/mes (LATAM) | Programa 2 Meses: US$4,490 (Miami) / US$3,490 (LATAM). Pauta aparte.",
        "delivery_cost_estimate": 750.0,
        "requires_director_approval": True,
        "scope": "Exclusivo para clientes que YA tienen Web, Chatbot y CRM: Filmmaker Profesional Presencial en Oficina o Clínica (1 Shoot Day 4h/mes con cámara 4K, iluminación y audio) + Director Escénico en Sitio (graba 20–30 videos en 1 sola mañana) + Edición de 30 Piezas (Reels + Carruseles) por el equipo de +744K vistas + Publicación Total + Trafficker Avanzado (Meta + TikTok Spark Ads)."
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
    "BEAUTY_BOOST_1499": {
        "code": "BEAUTY_BOOST_1499",
        "name": "Beauty Boost · Captación Comercial Activa y Seguimiento (US$1,499/mes)",
        "price": 1499.0,
        "initial_payment": 1499.0,
        "delivery_payment": 0.0,
        "payment_terms": "US$1,499 USD/mes (Contrato inicial recomendado de 3 meses bajo pago mensual anticipado). Pauta publicitaria pagada directo por el cliente ($800-$1,500/mes FL · $500-$1,000/mes PR).",
        "delivery_cost_estimate": 300.0,
        "requires_director_approval": False,
        "scope": "Gestión y lanzamiento de campañas en Meta Ads + estrategia de captación + landing page + CRM GoHighLevel con seguimiento automatizado + atención inicial IA + Setter/Lead Manager + reporte mensual."
    },
    "BEAUTY_ELEVATE_2499": {
        "code": "BEAUTY_ELEVATE_2499",
        "name": "Beauty Elevate · Autoridad, 12 Reels, Recuperación de Bases y Recompra (US$2,499/mes)",
        "price": 2499.0,
        "initial_payment": 2499.0,
        "delivery_payment": 0.0,
        "payment_terms": "US$2,499 USD/mes (Contrato inicial recomendado de 3 meses bajo pago mensual anticipado). El cliente graba en bruto y Beauty Growth ejecuta guiones y edición.",
        "delivery_cost_estimate": 500.0,
        "requires_director_approval": False,
        "scope": "Todo Beauty Boost + gestión estratégica de redes + calendario editorial, guiones, edición de videos/Reels y diseño para 12 piezas/mes + automatizaciones WhatsApp + recuperación telefónica de bases de datos + estrategia de membresías y recompra."
    },
    "BEAUTY_EMPIRE_3499": {
        "code": "BEAUTY_EMPIRE_3499",
        "name": "Beauty Empire · Academias, Cursos, 24 Piezas y Closer por Zoom (US$3,499/mes)",
        "price": 3499.0,
        "initial_payment": 3499.0,
        "delivery_payment": 0.0,
        "payment_terms": "US$3,499 USD/mes + comisión variable del Closer por cada venta cerrada según porcentaje pactado.",
        "delivery_cost_estimate": 750.0,
        "requires_director_approval": False,
        "scope": "Todo Beauty Elevate ampliado a 24 piezas/mes + campañas y embudo especializado para cursos/formaciones o servicios high-ticket + Setter para calificar y agendar + Closer humano para cierres por Zoom."
    },
    "BEAUTY_HIGHTICKET_5000": {
        "code": "BEAUTY_HIGHTICKET_5000",
        "name": "Beauty High-Ticket · Sistema Integral + Producción Audiovisual Presencial FL (US$5,000/mes)",
        "price": 5000.0,
        "initial_payment": 5000.0,
        "delivery_payment": 0.0,
        "payment_terms": "US$5,000 USD/mes (Expansión Florida con producción audiovisual presencial hasta 10 videos en 2 visitas/mes).",
        "delivery_cost_estimate": 1300.0,
        "requires_director_approval": True,
        "scope": "Sistema integral Beauty Growth + grabación audiovisual presencial en Florida."
    },
}

CANONICAL_PIPELINE_STAGES = [
    "Lead identificado",
    "Primer contacto",
    "Contacto",
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

BEAUTY_GROWTH_PIPELINE_STAGES = [
    "1. Prospecto identificado",
    "2. Primer contacto",
    "3. Segundo contacto",
    "4. Tercer contacto",
    "5. Respondió / Interesado",
    "6. Seguimiento",
    "7. Lead calificado",
    "8. Reunión agendada",
    "9. Reunión confirmada",
    "10. Reunión realizada",
    "11. Propuesta enviada",
    "12. Negociación activa",
    "13. Ganado / Cierre",
    "14. Perdido / No calificado",
]

ALTERNATIVE_PIPELINE_STAGES = [
    "No interesado",
    "No responde",
    "No cumple perfil",
    "Opt-out",
    "Venta perdida",
    "Reembolso/contracargo",
]

ALL_PIPELINE_STAGES = list(dict.fromkeys(CANONICAL_PIPELINE_STAGES + ALTERNATIVE_PIPELINE_STAGES + BEAUTY_GROWTH_PIPELINE_STAGES))


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

        # Limpieza única pre-sprint 18 Nov: vaciar pruebas de Closer Pipeline sin tocar a Claudio (claudiniosan@yahoo.com.ar)
        has_clean_flag = False
        try:
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='integration_settings'")
            if cur.fetchone():
                cur.execute("SELECT value FROM integration_settings WHERE key='closer_pipeline_clean_nov18_v1'")
                has_clean_flag = cur.fetchone() is not None
        except Exception:
            has_clean_flag = False

        if not has_clean_flag:
            cur.execute("""
                UPDATE leads
                SET pipeline_stage = 'Lead identificado',
                    status = 'new',
                    quoted_amount = 0.0,
                    contracted_amount = 0.0,
                    contact_id = '',
                    ghl_opportunity_id = '',
                    site_delivery_status = 'pendiente_pago',
                    next_action_at = '',
                    next_action_note = ''
                WHERE LOWER(COALESCE(owner_id, '')) != 'claudiniosan@yahoo.com.ar'
                  AND COALESCE(amount_collected, 0.0) <= 0.0
                  AND (
                      COALESCE(quoted_amount, 0.0) > 0.0
                      OR COALESCE(contact_id, '') != ''
                      OR COALESCE(ghl_opportunity_id, '') != ''
                      OR pipeline_stage IN ('Calificado', 'Diagnóstico agendado', 'Demo realizada', 'Propuesta enviada', 'Pago pendiente')
                  )
            """)
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='integration_settings'")
            if cur.fetchone():
                cur.execute(
                    "INSERT OR REPLACE INTO integration_settings (key, value) VALUES ('closer_pipeline_clean_nov18_v1', ?)",
                    (datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),),
                )

        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"⚠️ [MIGRATION] Warning in _run_safe_migrations: {e}", flush=True)
    finally:
        conn.close()


INITIAL_SALES_TEAM = [
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
        "email": "laverdaderafuerza02@gmail.com",
        "name": "Agustín García",
        "role": "seller",
        "dupla": "Dupla A — Clínicas (Dental, Estética y Capilar)",
        "phone": "+5491164930987",
        "plan": "SVE-90 Enterprise",
        "ghl_user_id": "VvSOqlOsPzFQr93E1kZ6",
        "calendar_url": "https://api.agenciaprosperia.com/widget/booking/bagwspAtTp3yUCFG5Tew",
        "avatar_url": "/static/img/closers/agustin.jpg",
        "default_pass": "Closer2026!"
    },
    {
        "email": "digitalblups@gmail.com",
        "name": "Jhonatan Rivero",
        "role": "seller",
        "dupla": "Dupla C — Profesionales, Consultores & Academias",
        "phone": "",
        "plan": "SVE-90 Enterprise",
        "ghl_user_id": "KEo98brNaYD9ReQb6yWv",
        "is_active": 1,
        "calendar_url": "https://api.agenciaprosperia.com/widget/booking/I4X8M0MTxCFBRZ1y5cfZ",
        "avatar_url": "/static/img/closers/jhonatan.jpg",
        "default_pass": "Closer2026!"
    },
    {
        "email": "bruno.hernan.espinosa1694@gmail.com",
        "name": "Bruno Espinoza",
        "role": "seller",
        "dupla": "Dupla C — Profesionales, Consultores & Academias",
        "phone": "",
        "plan": "SVE-90 Enterprise",
        "ghl_user_id": "ZjuoAK127hMnciLryiF4",
        "is_active": 1,
        "calendar_url": "https://api.agenciaprosperia.com/widget/booking/6Sfg6oz7rX29XazBifWc",
        "avatar_url": "/static/img/closers/bruno.jpg",
        "default_pass": "Closer2026!"
    },
    {
        "email": "tanyah.unity@gmail.com",
        "name": "Tanya Headley Mullings",
        "role": "seller",
        "dupla": "Dupla A — Clínicas (Dental, Estética y Capilar)",
        "phone": "",
        "plan": "SVE-90 Enterprise",
        "ghl_user_id": "IdhjqKwA1bOZYYMJLVqR",
        "is_active": 1,
        "calendar_url": "https://api.agenciaprosperia.com/widget/booking/oB0o3wbRwlsoItbE4adZ",
        "avatar_url": "/static/img/closers/tanya.jpg?v=2",
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
    "closer7@agenciaprosperia.com",
    "closer8@agenciaprosperia.com",
    "closer9@agenciaprosperia.com",
    "closer10@agenciaprosperia.com",
    "ucumaryvisual@gmail.com",
    "dbecerra@agenciaprosperia.com",
    "sergiotorales608@gmail.com",
    "sheille.perez@gmail.com",
    "wendyleiva59@gmail.com",
]


CLOSER_PAIRS_CONFIG = [
    {
        "num": 1,
        "label": "Pareja 1 — Diego & Jhonatan",
        "dupla": "Pareja 1 — Diego & Jhonatan (Líder Técnico)",
        "role_note": "Líder Técnico + Ventas: Diego Arriondo (Dudas técnicas Web/IA/CRM)",
        "emails": ["diegoarriondo03@gmail.com", "digitalblups@gmail.com"],
        "excluded_from_auto": False,
    },
    {
        "num": 2,
        "label": "Pareja 2 — Bruno & Claudio",
        "dupla": "Pareja 2 — Bruno & Claudio",
        "role_note": "Célula Comercial de Ataque Directo y Demos Web",
        "emails": ["bruno.hernan.espinosa1694@gmail.com", "claudiniosan@yahoo.com.ar"],
        "excluded_from_auto": False,
    },
    {
        "num": 3,
        "label": "Pareja 3 — Lorena & Agustín",
        "dupla": "Pareja 3 — Lorena & Agustín (Líder Seteo)",
        "role_note": "Líder de Seteo (Setter): Lorena Rodríguez (Apertura, calificación y bitácora)",
        "emails": ["loremrodriguezafb@gmail.com", "laverdaderafuerza02@gmail.com"],
        "excluded_from_auto": False,
    },
    {
        "num": 4,
        "label": "Pareja 4 — Tanya & Cinthya",
        "dupla": "Pareja 4 — Tanya & Cinthya",
        "role_note": "Célula Comercial EE. UU. / LATAM (Turnos Cruzados Mañana / Tarde)",
        "emails": ["tanyah.unity@gmail.com", "cinthyapenida0@gmail.com"],
        "excluded_from_auto": False,
    },
]


def get_pair_info(email: str):
    """Devuelve la configuración de la Pareja oficial a la que pertenece el closer."""
    em = (email or "").strip().lower()
    if not em:
        return None
    for p in CLOSER_PAIRS_CONFIG:
        if em in p["emails"]:
            return p
    return None


def get_partner_emails(email: str) -> list:
    """Devuelve todos los correos electrónicos de la Pareja del closer para compartir bandeja y alertas."""
    em = (email or "").strip().lower()
    if not em:
        return []
    p = get_pair_info(em)
    return list(p["emails"]) if p else [em]


def get_active_real_closers() -> list:
    """Devuelve únicamente los Closers reales activos con cuenta en ProsperIA CRM (excluye vacantes en contratación)."""
    return [m for m in INITIAL_SALES_TEAM if (m.get("ghl_user_id") or "").strip() or m.get("is_active")]


def get_next_round_robin_closer(db) -> dict:
    """Rota equitativamente entre los Closers activos (excluyendo Pareja 6 en pausa temporal)."""
    paused = {em for p in CLOSER_PAIRS_CONFIG if p.get("excluded_from_auto") for em in p["emails"]}
    active_closers = [m for m in get_active_real_closers() if (m.get("email") or "").lower() not in paused]
    if not active_closers:
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

        # 1. Eliminar usuarios genéricos de prueba, al editor (Cris) y cuentas fuera del equipo de Closers
        for obs_email in OBSOLETE_TEST_EMAILS:
            db.query(SessionModel).filter(SessionModel.email == obs_email).delete(synchronize_session=False)
            obs_u = db.query(User).filter(User.email == obs_email).first()
            if obs_u:
                db.delete(obs_u)

        # Limpiar cualquier lead de Beauty Growth de la tabla interna de los Closers (opera directo en CRM V8tM5xk6xl15wKhbQS0p)
        db.query(Lead).filter(
            (Lead.niche == "beauty_growth") | (Lead.owner_id == "dbecerra@agenciaprosperia.com")
        ).delete(synchronize_session=False)

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
                    phone="+17869828707",
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

        # 2b. Subcuenta VIP para IDOL JOSE (Doral FW Magazine — 15ª Edición y campañas futuras)
        idol_email = "idoljose@agenciaprosperia.com"
        idol_pass_raw = os.environ.get("IDOL_CRM_PASSWORD", "IdolDFW2026!").strip() or "IdolDFW2026!"
        idol_pass_hash = hash_password(idol_pass_raw)
        idol_u = db.query(User).filter(User.email == idol_email).first()
        if not idol_u:
            db.add(User(
                email=idol_email,
                name="IDOL JOSE (Director · Doral FW Magazine)",
                password=idol_pass_hash,
                company="IDOL JOSE Group Corp · Doral FW Magazine",
                phone="+17866475982",
                plan="Subcuenta VIP · Agencia Prosper IA",
                api_key=f"sve90_sub_idol_{secrets.token_hex(8)}",
                role="subaccount",
                dupla="Subcuenta VIP — IDOL JOSE & DFW Magazine",
                is_active=1,
                commission_rate=0.0,
                created_at=now_iso,
                calendar_url="https://wa.me/17866475982",
                avatar_url="https://www.doralfwmagazine.com/logo/doralfashionweekmagazinelogo.png",
            ))
        else:
            idol_u.name = "IDOL JOSE (Director · Doral FW Magazine)"
            idol_u.company = "IDOL JOSE Group Corp · Doral FW Magazine"
            idol_u.phone = "+17866475982"
            idol_u.plan = "Subcuenta VIP · Agencia Prosper IA"
            idol_u.role = "subaccount"
            idol_u.dupla = "Subcuenta VIP — IDOL JOSE & DFW Magazine"
            idol_u.is_active = 1
            if not getattr(idol_u, "password", ""):
                idol_u.password = idol_pass_hash
            if not getattr(idol_u, "avatar_url", "") or "static/img/doralfashionweek" in str(idol_u.avatar_url):
                idol_u.avatar_url = "https://www.doralfwmagazine.com/logo/doralfashionweekmagazinelogo.png"

        # 3. Sembrar o actualizar los Closers reales de GHL con su etiqueta oficial de Pareja
        for member in INITIAL_SALES_TEAM:
            pair_dupla = (get_pair_info(member["email"]) or {}).get("dupla") or member["dupla"]
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
                    dupla=pair_dupla,
                    ghl_user_id=member.get("ghl_user_id", ""),
                    is_active=1 if (member.get("ghl_user_id") or member.get("is_active")) else 0,
                    commission_rate=0.15,
                    created_at=now_iso,
                    calendar_url=member.get("calendar_url", "https://api.agenciaprosperia.com/widget/booking/gqoqyrr112bvjTJYqOi8"),
                    avatar_url=member.get("avatar_url", ""),
                ))
            else:
                exists_u.name = member["name"]
                exists_u.dupla = pair_dupla
                exists_u.role = "seller"
                exists_u.plan = "SVE-90 Enterprise"
                if member.get("phone"):
                    exists_u.phone = member["phone"]
                if member.get("ghl_user_id") or member.get("is_active"):
                    exists_u.is_active = 1
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
            "ghl_pipeline_id": os.environ.get("GHL_PIPELINE_ID", "G9nVz4GhrxAROVkPtPis"),
            "ghl_beauty_location_id": os.environ.get("GHL_BEAUTY_LOCATION_ID", "V8tM5xk6xl15wKhbQS0p"),
            "ghl_beauty_location_active": "V8tM5xk6xl15wKhbQS0p",
            "ghl_beauty_pipeline_id": os.environ.get("GHL_BEAUTY_PIPELINE_ID", "BBQlDFhNVE0NRmKNTMS2"),
            "ghl_beauty_stage_id": os.environ.get("GHL_BEAUTY_STAGE_ID", "cc2b04de-8d38-4c73-89d9-e01983a369c8"),
            "ghl_beauty_pipeline_name": "Beauty Growth & Business System",
            "ghl_beauty_admin_email": "dbecerra@agenciaprosperia.com",
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
            elif key in ("ghl_beauty_pipeline_id", "ghl_beauty_location_active", "ghl_beauty_stage_id") and not (exists.value or "").strip() and val:
                exists.value = val

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

        # Redistribución v6 Oficial: Incorporar a Agustín García (7 Closers Reales Activos) y repartir equitativamente los prospectos sin tocar los ya gestionados
        seeded_v6_flag = db.query(IntegrationSetting).filter(IntegrationSetting.key == "ghl_516_and_comex_v6_7closers").first()
        if not seeded_v6_flag:
            try:
                active_seven = get_active_real_closers()
                if active_seven:
                    def _dupla_niche_tpl_v6(dupla_str: str):
                        if "Dupla A" in dupla_str:
                            return "clinica", "clinica_dental_estetica"
                        if "Dupla B" in dupla_str:
                            return "servicios_locales", "servicios_locales_taller"
                        return "profesionales", "profesionales_consultoria_legal"

                    # 1. Reasignar equitativamente los leads de CRM (Inbound Reels / Códigos) que aún están en "Lead identificado"
                    crm_pool_leads = db.query(Lead).filter(
                        (Lead.source != "comex_outbound_b2b")
                        & (Lead.pipeline_stage == "Lead identificado")
                        & ((Lead.amount_collected == None) | (Lead.amount_collected == 0))
                    ).order_by(Lead.id.asc()).all()

                    for idx_c, ld in enumerate(crm_pool_leads):
                        m = active_seven[idx_c % len(active_seven)]
                        niche_val, tpl_val = _dupla_niche_tpl_v6(m["dupla"])
                        ld.owner_id = m["email"]
                        ld.setter_id = m["email"]
                        ld.niche = niche_val
                        ld.selected_template = tpl_val

                    # 2. Reasignar equitativamente las empresas COMEX que aún están en "Lead identificado"
                    comex_pool_leads = db.query(Lead).filter(
                        (Lead.source == "comex_outbound_b2b")
                        & (Lead.pipeline_stage == "Lead identificado")
                        & ((Lead.amount_collected == None) | (Lead.amount_collected == 0))
                    ).order_by(Lead.id.asc()).all()

                    for idx_x, ld in enumerate(comex_pool_leads):
                        m = active_seven[idx_x % len(active_seven)]
                        ld.owner_id = m["email"]
                        ld.setter_id = m["email"]

                    # Asegurar 0 vacantes placeholder activas (closer1..closer10 fueron migrados/eliminados)
                    for ph_idx in (9, 10):
                        ph_u = db.query(User).filter(User.email == f"closer{ph_idx}@agenciaprosperia.com").first()
                        if ph_u:
                            db.delete(ph_u)

                    db.add(IntegrationSetting(
                        key="ghl_516_and_comex_v6_7closers",
                        value=f"closers={len(active_seven)},crm={len(crm_pool_leads)},comex={len(comex_pool_leads)}_at_{now_iso}",
                    ))
                    db.commit()
                    print(f"✅ [SEED V6 7 CLOSERS] Agustín García activo. Repartidos {len(crm_pool_leads)} CRM + {len(comex_pool_leads)} COMEX entre {len(active_seven)} Closers reales.")
            except Exception as sv6_err:
                db.rollback()
                print(f"⚠️ [SEED V6 7 CLOSERS] Error redistribuyendo entre 7 Closers: {sv6_err}")

        # Seed v7 Sprint 18–25 Nov: Conservar intacta la cartera actual de Claudio (top-up a 1,000)
        # y reemplazar la cartera de los otros 10 Closers con 1,000 leads calificados, etiquetados y con Speech.
        seed_11k_path = Path(__file__).parent / "seeds" / "closers_11k_master_seed.json.gz"
        seeded_v7_flag = db.query(IntegrationSetting).filter(IntegrationSetting.key == "closers_11k_sprint_nov18_v1").first()
        if seed_11k_path.exists() and not seeded_v7_flag:
            try:
                keep_owner = "claudiniosan@yahoo.com.ar"
                other_sellers = [m["email"] for m in INITIAL_SALES_TEAM if m["email"].lower() != keep_owner]

                # 1. Borrar leads previos de los 10 Closers (nunca borrar Claudio, /exmaboletos ni cobros verificados)
                db.query(Lead).filter(
                    (Lead.owner_id.in_(other_sellers))
                    & (Lead.source != "exmaboletos_20off")
                    & ((Lead.amount_collected == None) | (Lead.amount_collected == 0))
                ).delete(synchronize_session=False)

                # Limpiar también pools viejos que no pertenezcan a Claudio ni a cobros reales
                db.query(Lead).filter(
                    (Lead.source.in_(["ghl_455_pool", "ghl_516_pool", "comex_outbound_b2b"]))
                    & (Lead.owner_id != keep_owner)
                    & ((Lead.amount_collected == None) | (Lead.amount_collected == 0))
                ).delete(synchronize_session=False)

                # Resetear contadores del Sprint semanal (18-25 Nov) para los 10 Closers renovados
                for em in other_sellers:
                    u_row = db.query(User).filter(User.email == em).first()
                    if u_row:
                        u_row.calls_made_today = 0
                        u_row.calls_made_week = 0
                        u_row.calls_answered_week = 0
                        u_row.demos_done_week = 0
                        u_row.sales_closed_week = 0
                db.commit()

                dnd_emails = {r.email for r in db.query(DndExclusion).all() if r.email}
                internal_emails = {m["email"].lower() for m in INITIAL_SALES_TEAM} | {
                    "admin@prosperia.com", "edward@agenciaprosperia.com", "ucumaryvisual@gmail.com"
                }
                existing_rows = db.query(Lead).all()
                seen_phones = {normalize_phone_e164(r.phone_e164 or r.phone or "") for r in existing_rows if (r.phone_e164 or r.phone)}
                seen_phones.discard("")
                seen_emails = {normalize_email(r.email or "") for r in existing_rows if r.email and "@sin-correo.local" not in r.email}

                per_closer_counts = {}
                for r in existing_rows:
                    ow = (getattr(r, "owner_id", "") or "").lower()
                    if ow:
                        per_closer_counts[ow] = per_closer_counts.get(ow, 0) + 1

                with gzip.open(seed_11k_path, "rt", encoding="utf-8") as gz_f:
                    payload_11k = json.load(gz_f)

                junk_email_markers = ("sentry", "wixpress", "tu@email", "usuario@dominio", "email@dominio", "ejemplo@", "example.com", "noreply@")
                created_str = now_iso[:19].replace("T", " ")
                bulk_objs = []
                total_11k_inserted = 0
                overflow_items = []

                def build_lead_obj(item_dict: dict, target_owner: str, seq_idx: int):
                    ph_e164 = normalize_phone_e164(item_dict.get("phone_e164") or item_dict.get("phone") or "")
                    if not ph_e164 or ph_e164 in seen_phones:
                        return None
                    em_raw = normalize_email(item_dict.get("email") or "")
                    if em_raw in internal_emails or em_raw in dnd_emails:
                        return None
                    # Si el correo es genérico de plantilla o lo comparten varias sucursales, generamos alias único sin perder el teléfono
                    if not em_raw or "@sin-correo.local" in em_raw or em_raw in seen_emails or any(jk in em_raw for jk in junk_email_markers):
                        em_clean = f"prospecto_{seq_idx + 1}_{re.sub(r'[^0-9]', '', ph_e164)[-6:]}@sin-correo.local"
                    else:
                        em_clean = em_raw
                        seen_emails.add(em_clean)
                    seen_phones.add(ph_e164)
                    return Lead(
                        name=item_dict.get("name") or "Negocio Calificado",
                        full_name=item_dict.get("full_name") or item_dict.get("name") or "Negocio Calificado",
                        email=em_clean,
                        company=item_dict.get("business_name") or item_dict.get("name") or "",
                        business_name=item_dict.get("business_name") or item_dict.get("name") or "",
                        phone=item_dict.get("phone") or ph_e164,
                        phone_e164=ph_e164,
                        status="new",
                        source=item_dict.get("source") or "apify_sprint_nov18",
                        source_channel=item_dict.get("source_channel") or "Prospección Calificada Google Maps",
                        source_campaign=item_dict.get("source_campaign") or "",
                        interest_primary=item_dict.get("interest_primary") or "Sitio Web Inteligente",
                        score=int(item_dict.get("score") or 90),
                        notes=item_dict.get("notes") or "",
                        created_at=created_str,
                        contact_id="",
                        owner_id=target_owner,
                        setter_id=target_owner,
                        niche=item_dict.get("niche") or "clinica",
                        country=item_dict.get("country") or "LATAM / US",
                        timezone=item_dict.get("timezone") or "America/New_York",
                        contact_permission="Directorio Público Comercial (Google Maps Verificado)",
                        contact_status="contactable",
                        pipeline_stage="Lead identificado",
                        offer_version="EXPRESS_497",
                        selected_template=item_dict.get("selected_template") or "clinica_dental_estetica",
                    )

                for item in payload_11k.get("leads", []):
                    owner_em = (item.get("owner_id") or "").lower().strip()
                    if not owner_em:
                        continue
                    cur_cnt = per_closer_counts.get(owner_em, 0)
                    if cur_cnt >= 1000:
                        overflow_items.append(item)
                        continue
                    lead_obj = build_lead_obj(item, owner_em, total_11k_inserted)
                    if not lead_obj:
                        continue
                    per_closer_counts[owner_em] = cur_cnt + 1
                    bulk_objs.append(lead_obj)
                    total_11k_inserted += 1

                # Si algún Closer quedó debajo de 1,000 por colisión con teléfonos previos conservados, rellenar con overflow (p.ej. sobrantes de Claudio)
                if overflow_items:
                    for m in INITIAL_SALES_TEAM:
                        em = m["email"].lower()
                        while per_closer_counts.get(em, 0) < 1000 and overflow_items:
                            extra_item = overflow_items.pop(0)
                            lead_obj = build_lead_obj(extra_item, em, total_11k_inserted)
                            if lead_obj:
                                per_closer_counts[em] = per_closer_counts.get(em, 0) + 1
                                bulk_objs.append(lead_obj)
                                total_11k_inserted += 1

                for chunk_start in range(0, len(bulk_objs), 1000):
                    db.bulk_save_objects(bulk_objs[chunk_start:chunk_start + 1000])
                    db.commit()

                db.add(IntegrationSetting(
                    key="closers_11k_sprint_nov18_v1",
                    value=f"inserted={total_11k_inserted},claudio_kept={per_closer_counts.get(keep_owner, 0)}_at_{now_iso}",
                ))
                db.commit()
                print(f"✅ [SEED 11K SPRINT] Cargados {total_11k_inserted} leads calificados (Claudio conservado intacto y top-up a 1,000).", flush=True)
            except Exception as sv7_err:
                db.rollback()
                print(f"⚠️ [SEED 11K SPRINT] Error sembrando closers_11k_master_seed.json.gz: {sv7_err}", flush=True)

        # Limpieza única post-presentación de Sheille (sheille.perez@gmail.com) sin tocar a Claudio ni a otros Closers
        sheille_reset_flag = db.query(IntegrationSetting).filter(IntegrationSetting.key == "reset_sheille_post_presentation_v1").first()
        if not sheille_reset_flag:
            try:
                sh_email = "sheille.perez@gmail.com"
                sh_user = db.query(User).filter(func.lower(User.email) == sh_email).first()
                if sh_user:
                    sh_user.calls_made_today = 0
                    sh_user.calls_made_week = 0
                    sh_user.calls_answered_week = 0
                    sh_user.demos_done_week = 0
                    sh_user.sales_closed_week = 0
                    sh_user.active_minutes_today = 0
                    sh_user.active_minutes_week = 0
                    sh_user.checkin_at = ""
                sh_leads = db.query(Lead).filter(func.lower(Lead.owner_id) == sh_email).all()
                sh_ids = []
                for ld in sh_leads:
                    notes_raw = getattr(ld, "notes", "") or ""
                    cleaned_notes = re.sub(r"\n\[20\d{2}-\d{2}-\d{2}[T ][^\n]*", "", notes_raw).split("[Cola:")[0].strip()
                    if (
                        (getattr(ld, "pipeline_stage", "Lead identificado") or "Lead identificado") != "Lead identificado"
                        or (getattr(ld, "status", "new") or "new") != "new"
                        or bool(getattr(ld, "last_touch", "") or "")
                        or float(getattr(ld, "amount_collected", 0) or 0) > 0
                        or cleaned_notes != notes_raw.strip()
                    ):
                        ld.pipeline_stage = "Lead identificado"
                        ld.status = "new"
                        ld.last_touch = ""
                        ld.quoted_amount = 0.0
                        ld.contracted_amount = 0.0
                        ld.amount_collected = 0.0
                        ld.commission_amount = 0.0
                        ld.commission_status = "sin_devengar"
                        ld.invoice_id = ""
                        ld.next_action_at = ""
                        ld.next_action_note = ""
                        ld.notes = cleaned_notes
                        sh_ids.append(ld.id)
                db.query(AuditLog).filter(func.lower(AuditLog.actor_email) == sh_email).delete(synchronize_session=False)
                if sh_ids:
                    db.query(AuditLog).filter(AuditLog.lead_id.in_(sh_ids)).delete(synchronize_session=False)
                db.add(IntegrationSetting(
                    key="reset_sheille_post_presentation_v1",
                    value=f"reset_{len(sh_ids)}_leads_at_{now_iso}",
                ))
                db.commit()
                print(f"✅ [RESET SHEILLE] Restaurados {len(sh_ids)} leads y contadores de {sh_email} desde cero.", flush=True)
            except Exception as sh_err:
                db.rollback()
                print(f"⚠️ [RESET SHEILLE] Error: {sh_err}", flush=True)

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

        # 6. Migración idempotente: Reparto aleatorio en 5 Parejas activas (excluye Pareja 6 Cinthya/Sergio) + visibilidad Setter IA
        pairs_mig_key = "pairs_hot_redistribution_nov20_v1"
        if not db.query(IntegrationSetting).filter(IntegrationSetting.key == pairs_mig_key).first():
            for p_cfg in CLOSER_PAIRS_CONFIG:
                for p_em in p_cfg["emails"]:
                    u_row = db.query(User).filter(func.lower(User.email) == p_em).first()
                    if u_row:
                        u_row.dupla = p_cfg["dupla"]

            assign_path = Path(__file__).parent / "seeds" / "pairs_5_hot_warm_assignments.json"
            reassigned_cnt = 0
            if assign_path.exists():
                try:
                    assign_map = json.loads(assign_path.read_text(encoding="utf-8"))
                    if isinstance(assign_map, dict) and assign_map:
                        target_ids = [int(k) for k in assign_map.keys() if str(k).isdigit()]
                        for i in range(0, len(target_ids), 500):
                            chunk_ids = target_ids[i:i + 500]
                            for ld in db.query(Lead).filter(Lead.id.in_(chunk_ids)).all():
                                new_ow = (assign_map.get(str(ld.id)) or "").strip().lower()
                                if new_ow:
                                    ld.owner_id = new_ow
                                    ld.setter_id = new_ow
                                    reassigned_cnt += 1
                except Exception as assign_exc:
                    print(f"⚠️ [PAIRS MIG] Error leyendo assignments JSON: {assign_exc}", flush=True)

            setter_touched_rows = (
                db.query(Lead)
                .filter((Lead.last_touch == "") | (Lead.last_touch.is_(None)))
                .filter(Lead.notes.contains("🤖 Setter IA"))
                .all()
            )
            touched_fixed = 0
            for ld in setter_touched_rows:
                m_dt = re.search(r"\[(2026-\d{2}-\d{2})\s+(\d{2}:\d{2})\s+·\s+🤖 Setter IA", ld.notes or "")
                ld.last_touch = f"{m_dt.group(1)}T{m_dt.group(2)}:00Z" if m_dt else "2026-11-19T18:00:00Z"
                touched_fixed += 1

            db.add(IntegrationSetting(
                key=pairs_mig_key,
                value=f"reassigned={reassigned_cnt},last_touch_fixed={touched_fixed}",
            ))

        # 7. Migración idempotente: Baja definitiva de Sergio Torales y activación de Pareja 5 — Tanya & Cinthya
        pairs_v2_key = "pairs_5_tanya_cinthya_sergio_exit_nov20_v2"
        if not db.query(IntegrationSetting).filter(IntegrationSetting.key == pairs_v2_key).first():
            active_emails = []
            for p_cfg in CLOSER_PAIRS_CONFIG:
                for p_em in p_cfg["emails"]:
                    active_emails.append(p_em)
                    u_row = db.query(User).filter(func.lower(User.email) == p_em).first()
                    if u_row:
                        u_row.dupla = p_cfg["dupla"]

            assign_path = Path(__file__).parent / "seeds" / "pairs_5_hot_warm_assignments.json"
            reassigned_v2 = 0
            if assign_path.exists():
                try:
                    assign_map = json.loads(assign_path.read_text(encoding="utf-8"))
                    if isinstance(assign_map, dict) and assign_map:
                        target_ids = [int(k) for k in assign_map.keys() if str(k).isdigit()]
                        for i in range(0, len(target_ids), 500):
                            chunk_ids = target_ids[i:i + 500]
                            for ld in db.query(Lead).filter(Lead.id.in_(chunk_ids)).all():
                                new_ow = (assign_map.get(str(ld.id)) or "").strip().lower()
                                if new_ow:
                                    ld.owner_id = new_ow
                                    ld.setter_id = new_ow
                                    reassigned_v2 += 1
                except Exception as assign_exc:
                    print(f"⚠️ [PAIRS V2 MIG] Error leyendo assignments JSON: {assign_exc}", flush=True)

            sergio_rows = db.query(Lead).filter(func.lower(Lead.owner_id) == "sergiotorales608@gmail.com").all()
            sergio_moved = 0
            if sergio_rows and active_emails:
                for idx, ld in enumerate(sergio_rows):
                    dst_em = active_emails[idx % len(active_emails)]
                    ld.owner_id = dst_em
                    ld.setter_id = dst_em
                    sergio_moved += 1

            db.add(IntegrationSetting(
                key=pairs_v2_key,
                value=f"reassigned_hot_warm={reassigned_v2},sergio_reassigned={sergio_moved}",
            ))

        # 8. Migración idempotente: Bolsa Abierta de 500 Super-Calificados (100% Móviles/WA + Argentina $0) + Conservar Tocados Útiles
        pool_mig_key = "pool_500_super_qualified_nov25_v1"
        if not db.query(IntegrationSetting).filter(IntegrationSetting.key == pool_mig_key).first():
            active_team_emails = {m["email"].lower() for m in INITIAL_SALES_TEAM}
            auto_markers = (
                "🤖 Setter IA",
                "📥 Origen Correo Entrante",
                "🔥 RESPONDIÓ A SETTER IA",
                "💬 Chatbot Web",
                "Auto-respuesta detectada",
                "Auto semana18nov",
            )
            dead_notes = (
                "sin wp",
                "no tiene wp",
                "no tiene whatssap",
                "no tiene whatsapp",
                "no tiene movil",
                "no es movil",
                "landline",
                "no tiene celular",
                "no tiene sms",
                "corto la llamada",
                "no está interesado",
                "no se intereso",
                "se niega a comprar",
            )
            active_touched_stages = {
                "Contacto",
                "Conversación",
                "Calificado",
                "Diagnóstico agendado",
                "Demo realizada",
                "Propuesta enviada",
                "Pago pendiente",
                "Pago confirmado",
                "Implementación",
                "Entregado",
            }
            closed_out_stages = {"No interesado", "No cumple perfil", "Opt-out", "Venta perdida"}

            all_leads = db.query(Lead).all()
            preserved_ids = set()
            seen_phones = set()
            seen_emails = set()
            seen_biz = set()

            # Paso A: Conservar los registros útiles trabajados por los 9 integrantes activos (excluyendo freebies/pruebas)
            for ld in all_leads:
                if _is_freebie_or_closer_test_lead(ld):
                    continue
                c_st = (getattr(ld, "contact_status", "contactable") or "contactable").lower()
                if c_st in ("dnd", "opt_out", "bounce", "unauthorized"):
                    continue
                own = (getattr(ld, "owner_id", "") or "").strip().lower()
                if own not in active_team_emails:
                    continue
                stg = (getattr(ld, "pipeline_stage", "Lead identificado") or "Lead identificado").strip()
                if stg in closed_out_stages:
                    continue
                notes_raw = getattr(ld, "notes", "") or ""
                entries = [
                    e for e in re.findall(r"\[20\d{2}-[^\]]+\][^\n]*", notes_raw)
                    if not any(m in e for m in auto_markers)
                ]
                has_real_paid = float(getattr(ld, "amount_collected", 0.0) or 0.0) > 0
                has_human_work = bool(entries) or (stg in active_touched_stages) or has_real_paid
                if not has_human_work:
                    continue
                last_e_low = entries[-1].lower() if entries else ""
                if not has_real_paid and last_e_low and any(d in last_e_low for d in dead_notes):
                    continue

                preserved_ids.add(ld.id)
                ld.contact_status = "contactable"
                digits = re.sub(r"\D", "", str(getattr(ld, "phone_e164", None) or getattr(ld, "phone", None) or ""))
                if len(digits) >= 9:
                    seen_phones.add(digits[-10:])
                em_ok = _real_email_pool(getattr(ld, "email", "") or "")
                if em_ok:
                    seen_emails.add(em_ok)
                biz_ok = (getattr(ld, "business_name", None) or getattr(ld, "company", None) or "").strip().lower()
                if biz_ok and biz_ok not in _PLACEHOLDER_BIZ_NAMES:
                    seen_biz.add(biz_ok)

            # Paso B: Seleccionar exactamente 500 Negocios B2B 100% Móviles/WA + Argentina ($0) para Bolsa Libre
            selected_pool = _select_pool_candidates(
                all_leads,
                seen_phones=seen_phones,
                seen_emails=seen_emails,
                seen_biz=seen_biz,
                limit=500,
                skip_ids=preserved_ids,
                require_real_biz=True,
            )
            pool_500_ids = set()
            for ld in selected_pool:
                pool_500_ids.add(ld.id)
                ld.owner_id = ""
                ld.setter_id = ""
                ld.pipeline_stage = "Lead identificado"
                ld.status = "new"
                ld.contact_status = "contactable"

            # Paso C: Archivar el resto en archivo_reserva sin eliminarlos de BD
            archived_cnt = 0
            for ld in all_leads:
                if ld.id in preserved_ids or ld.id in pool_500_ids:
                    continue
                c_st = (getattr(ld, "contact_status", "contactable") or "contactable").lower()
                if c_st in ("dnd", "opt_out", "bounce", "unauthorized"):
                    ld.owner_id = ""
                    continue
                ld.contact_status = "archivo_reserva"
                ld.owner_id = ""
                ld.setter_id = ""
                archived_cnt += 1

            # Paso D: Pausar por defecto el motor de correos en frío Setter IA
            for st_key in ("setter_ia_campaign_state_json", "setter_ia_warmup_state_json"):
                st_row = db.query(IntegrationSetting).filter(IntegrationSetting.key == st_key).first()
                if st_row and st_row.value:
                    try:
                        st_json = json.loads(st_row.value)
                        if isinstance(st_json, dict):
                            st_json["running"] = False
                            logs_lst = st_json.get("last_log")
                            if isinstance(logs_lst, list):
                                logs_lst.insert(0, f"[{now_iso[:16]}] ⏸️ Correos en frío pausados (Bolsa 500 100% WhatsApp/Llamada $0).")
                                st_json["last_log"] = logs_lst[:40]
                            st_row.value = json.dumps(st_json, ensure_ascii=False)
                    except Exception:
                        pass

            db.add(IntegrationSetting(
                key=pool_mig_key,
                value=f"preserved={len(preserved_ids)},pool_500={len(pool_500_ids)},archived={archived_cnt}",
            ))
            print(
                f"✅ [POOL 500 SUPER-QUALIFIED] Conservados={len(preserved_ids)} | Bolsa Libre={len(pool_500_ids)} | Archivo Reserva={archived_cnt}",
                flush=True,
            )

        # 9. Migración idempotente: compactar historial viejo de WhatsApp (solo último renglón útil)
        trim_wa_key = "pool_500_trim_old_wa_notes_nov25_v2"
        if not db.query(IntegrationSetting).filter(IntegrationSetting.key == trim_wa_key).first():
            trimmed_count = 0
            active_rows = db.query(Lead).filter(
                (Lead.contact_status == None) | (Lead.contact_status != "archivo_reserva")
            ).all()
            for ld in active_rows:
                if _trim_lead_old_wa_notes(ld):
                    trimmed_count += 1

            db.add(IntegrationSetting(
                key=trim_wa_key,
                value=f"trimmed={trimmed_count}",
            ))
            print(f"✅ [TRIM OLD WA BITACORA] Compactados={trimmed_count} leads (solo último renglón útil).", flush=True)

        # 10. Migración idempotente: purgar freebies (/codigos, Alumno IA, PassportAI Trial) y pruebas de Closers + rellenar Bolsa a 500 B2B reales
        purge_key = "purge_freebies_trials_and_closer_tests_nov25_v3"
        if not db.query(IntegrationSetting).filter(IntegrationSetting.key == purge_key).first():
            deleted_cnt = 0
            for ld in db.query(Lead).all():
                if _is_freebie_or_closer_test_lead(ld):
                    db.delete(ld)
                    deleted_cnt += 1
            db.flush()

            promoted_cnt, final_free_cnt = _topup_free_pool_to_target(db, target=500)
            db.add(IntegrationSetting(
                key=purge_key,
                value=f"deleted={deleted_cnt},topped_up={promoted_cnt},free_pool={final_free_cnt}",
            ))
            print(
                f"✅ [PURGE FREEBIES & TESTS] Eliminados={deleted_cnt} | Promovidos Bolsa={promoted_cnt} | Bolsa Libre={final_free_cnt}",
                flush=True,
            )

        # 11. Migración idempotente Opción 1 COMEX: archivar COMEX fríos/no-responde (conservar solo avance real) + limpiar bot correos sin respuesta + reponer Bolsa a 500 Apify ($0 AR)
        comex_key = "archive_comex_and_topup_apify_500_nov25_v4"
        if not db.query(IntegrationSetting).filter(IntegrationSetting.key == comex_key).first():
            comex_keep_stages = {
                "Contacto",
                "Conversación",
                "Calificado",
                "Diagnóstico agendado",
                "Demo realizada",
                "Propuesta enviada",
                "Pago pendiente",
                "Pago confirmado",
                "Implementación",
                "Entregado",
            }
            comex_archived = 0
            comex_kept = 0
            bot_email_stripped = 0

            for ld in db.query(Lead).all():
                src = (getattr(ld, "source", "") or "").strip().lower()
                c_st = (getattr(ld, "contact_status", "contactable") or "contactable").lower()
                own = (getattr(ld, "owner_id", "") or "").strip()
                stg = (getattr(ld, "pipeline_stage", "Lead identificado") or "Lead identificado").strip()

                if src == "comex_outbound_b2b":
                    has_real_paid = float(getattr(ld, "amount_collected", 0.0) or 0.0) > 0
                    is_real_progress = (
                        bool(own)
                        and c_st not in ("dnd", "opt_out", "bounce", "unauthorized")
                        and (stg in comex_keep_stages or has_real_paid)
                    )
                    if is_real_progress:
                        ld.contact_status = "contactable"
                        comex_kept += 1
                    else:
                        if c_st not in ("dnd", "opt_out", "bounce", "unauthorized") and (
                            c_st != "archivo_reserva" or own or (getattr(ld, "setter_id", "") or "").strip()
                        ):
                            ld.contact_status = "archivo_reserva"
                            ld.owner_id = ""
                            ld.setter_id = ""
                            comex_archived += 1
                    continue

                if not own and c_st == "contactable":
                    if _strip_unreplied_bot_email_lines(ld):
                        bot_email_stripped += 1

            db.flush()
            promoted_cnt, final_free_cnt = _topup_free_pool_to_target(db, target=500)
            db.add(IntegrationSetting(
                key=comex_key,
                value=(
                    f"comex_archived={comex_archived},comex_kept={comex_kept},"
                    f"bot_email_stripped={bot_email_stripped},topped_up={promoted_cnt},free_pool={final_free_cnt}"
                ),
            ))
            print(
                f"✅ [COMEX OP1 + BOLSA 500 APIFY] Archivados={comex_archived} | Conservados={comex_kept} | BotEmailsLimp={bot_email_stripped} | Promovidos={promoted_cnt} | BolsaLibre={final_free_cnt}",
                flush=True,
            )

        # 12. Migración idempotente: Baja definitiva de Wendy Leiva, Sheille Pérez y Sergio Torales (y confirmar Cris Bolívar fuera de closers)
        exit_team_key = "exit_sheille_wendy_sergio_nov26_v1"
        if not db.query(IntegrationSetting).filter(IntegrationSetting.key == exit_team_key).first():
            departed_emails = (
                "sheille.perez@gmail.com",
                "wendyleiva59@gmail.com",
                "sergiotorales608@gmail.com",
                "ucumaryvisual@gmail.com",
            )
            active_pool = [em for p in CLOSER_PAIRS_CONFIG for em in p.get("emails", [])]
            reassigned_exit = 0
            for dep_em in departed_emails:
                db.query(SessionModel).filter(func.lower(SessionModel.email) == dep_em).delete(synchronize_session=False)
                dep_u = db.query(User).filter(func.lower(User.email) == dep_em).first()
                if dep_u:
                    db.delete(dep_u)
                dep_leads = db.query(Lead).filter(func.lower(Lead.owner_id) == dep_em).all()
                for idx, ld in enumerate(dep_leads):
                    if active_pool:
                        dst_em = active_pool[(idx + reassigned_exit) % len(active_pool)]
                        ld.owner_id = dst_em
                        ld.setter_id = dst_em
                        reassigned_exit += 1
            for p_cfg in CLOSER_PAIRS_CONFIG:
                for p_em in p_cfg.get("emails", []):
                    u_row = db.query(User).filter(func.lower(User.email) == p_em).first()
                    if u_row:
                        u_row.dupla = p_cfg["dupla"]
            db.add(IntegrationSetting(
                key=exit_team_key,
                value=f"reassigned={reassigned_exit}",
            ))
            print(f"✅ [BAJA CLOSERS] Wendy/Sheille/Sergio/Cris removidos del panel y {reassigned_exit} leads reasignados.", flush=True)

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

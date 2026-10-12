"""Cliente mínimo de GoHighLevel (API v2) para sincronizar leads de los formularios web.

Flujo por cada envío de formulario:
  1. Upsert del contacto (sin duplicar por email/teléfono) con campos estándar y personalizados.
  2. Etiquetas aditivas (lead_web + origen del formulario).
  3. Nota con el detalle completo del formulario.
  4. Oportunidad en el pipeline "Ventas Agencia ProsperIA" → etapa "Nuevo Contacto",
     solo si el contacto no tiene ya una oportunidad abierta en ese pipeline.

Configuración por variables de entorno (el token nunca va en el código):
  GHL_PRIVATE_TOKEN   Private Integration Token de la subcuenta (obligatorio).
  GHL_LOCATION_ID     ID de la subcuenta.
  GHL_PIPELINE_ID     ID del pipeline destino.
  GHL_STAGE_ID        ID de la etapa inicial.
Si falta el token, la sincronización se omite sin afectar el resto del flujo.
"""
import json
import os
import re
import threading
import urllib.error
import urllib.request
from typing import Optional

GHL_BASE_URL = "https://services.leadconnectorhq.com"
GHL_API_VERSION = "2021-07-28"

DEFAULT_LOCATION_ID = "CNvJBINRWBUL2EdqRh3G"
DEFAULT_PIPELINE_ID = "SJ4xiMasQ0GZcUNYFgpa"        # Ventas Agencia ProsperIA
DEFAULT_STAGE_ID = "ffd8ae02-c4c0-431c-a827-0e909a80c752"  # Nuevo Contacto

# IDs de los campos personalizados de contacto creados en la subcuenta.
CF_INDUSTRIA = "K9N5HFBIpkonykvmoqB4"
CF_TAMANO_EQUIPO = "um5xkZ48Mmgx1GzqfpRK"
CF_CUELLO_BOTELLA = "z79pnM95XgAAfR0Vy6a8"

# Valores del <select> del formulario → opciones exactas del campo en GHL.
INDUSTRY_LABELS = {
    "clinica": "Clínica (Dental / Estética / Capilar)",
    "inmobiliaria": "Inmobiliaria / Bienes Raíces",
    "servicios_profesionales": "Servicios Profesionales / Consultoría",
    "belleza_bienestar": "Belleza, Estética o Spa",
    "fitness": "Fitness o Wellness",
    "servicios_hogar": "Servicios para el Hogar",
    "enterprise": "Proyecto Empresarial / SVE90",
    "otra": "Otra industria",
}
TEAM_LABELS = {
    "1-4": "1 a 4 personas",
    "5-15": "5 a 15 personas",
    "15+": "Más de 15 personas",
}


def _cfg(name: str, default: str = "") -> str:
    return (os.environ.get(name) or default).strip()


def _request(method: str, path: str, token: str, body: Optional[dict] = None):
    req = urllib.request.Request(
        GHL_BASE_URL + path,
        method=method,
        data=json.dumps(body).encode("utf-8") if body is not None else None,
        headers={
            "Authorization": f"Bearer {token}",
            "Version": GHL_API_VERSION,
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "prosperia-web/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode("utf-8") or "{}"
            return resp.status, json.loads(raw)
    except urllib.error.HTTPError as e:
        return e.code, {"error": e.read().decode("utf-8", "replace")[:500]}
    except Exception as e:  # red, timeout, etc.
        return 0, {"error": str(e)}


def _clean_phone(phone: str) -> str:
    phone = (phone or "").strip()
    if not phone:
        return ""
    digits = re.sub(r"\D", "", phone)
    if not digits:
        return ""
    return "+" + digits if phone.startswith("+") or len(digits) > 10 else "+1" + digits


def _source_tag(source: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", (source or "web").lower()).strip("_")
    return f"origen_{slug or 'web'}"


def sync_lead_to_ghl(
    first_name: str,
    last_name: str,
    email: str,
    phone: str,
    company: str,
    source: str,
    industry: str = "",
    team_size: str = "",
    message: str = "",
    notes: str = "",
) -> dict:
    """Sincroniza un lead con GHL. Devuelve un resumen; nunca lanza excepciones."""
    token = _cfg("GHL_PRIVATE_TOKEN")
    if not token:
        print("ℹ️ [GHL] GHL_PRIVATE_TOKEN no configurado; sincronización omitida.", flush=True)
        return {"ok": False, "skipped": True}

    location_id = _cfg("GHL_LOCATION_ID", DEFAULT_LOCATION_ID)
    pipeline_id = _cfg("GHL_PIPELINE_ID", DEFAULT_PIPELINE_ID)
    stage_id = _cfg("GHL_STAGE_ID", DEFAULT_STAGE_ID)

    full_name = f"{first_name} {last_name}".strip()
    custom_fields = []
    industry_label = INDUSTRY_LABELS.get((industry or "").strip().lower())
    if industry_label:
        custom_fields.append({"id": CF_INDUSTRIA, "field_value": industry_label})
    team_label = TEAM_LABELS.get((team_size or "").strip())
    if team_label:
        custom_fields.append({"id": CF_TAMANO_EQUIPO, "field_value": team_label})
    if message:
        custom_fields.append({"id": CF_CUELLO_BOTELLA, "field_value": message})

    contact_body = {
        "locationId": location_id,
        "firstName": first_name,
        "lastName": last_name,
        "name": full_name,
        "email": email,
        "companyName": company,
        "source": f"Web ProsperIA – {source}",
        "customFields": custom_fields,
    }
    clean_phone = _clean_phone(phone)
    if clean_phone:
        contact_body["phone"] = clean_phone

    # 1. Upsert del contacto (si el teléfono es inválido, reintenta sin él).
    status, res = _request("POST", "/contacts/upsert", token, contact_body)
    if status not in (200, 201) and "phone" in contact_body:
        print(f"⚠️ [GHL] Upsert con teléfono falló ({status}); reintentando sin teléfono.", flush=True)
        contact_body.pop("phone")
        status, res = _request("POST", "/contacts/upsert", token, contact_body)
    if status not in (200, 201):
        print(f"❌ [GHL] No se pudo crear/actualizar el contacto {email}: {status} {res}", flush=True)
        return {"ok": False, "step": "contact", "status": status}

    contact = res.get("contact", {})
    contact_id = contact.get("id")
    is_new = res.get("new")

    # 2. Etiquetas (aditivas: no borran las existentes).
    _request("POST", f"/contacts/{contact_id}/tags", token,
             {"tags": ["lead_web", _source_tag(source)]})

    # 3. Nota con el detalle completo del envío.
    note_lines = [f"📥 Formulario web ({source})"]
    if company:
        note_lines.append(f"Empresa: {company}")
    if industry_label or industry:
        note_lines.append(f"Industria: {industry_label or industry}")
    if team_label or team_size:
        note_lines.append(f"Equipo: {team_label or team_size}")
    if notes or message:
        note_lines.append("")
        note_lines.append(notes or message)
    _request("POST", f"/contacts/{contact_id}/notes", token, {"body": "\n".join(note_lines)})

    # 4. Oportunidad en "Nuevo Contacto" solo si no existe una abierta en el pipeline.
    q = (f"/opportunities/search?location_id={location_id}&contact_id={contact_id}"
         f"&pipeline_id={pipeline_id}&status=open&limit=1")
    s_status, s_res = _request("GET", q, token)
    if s_status == 200 and s_res.get("opportunities"):
        opp_id = s_res["opportunities"][0].get("id")
        print(f"ℹ️ [GHL] {email} ya tiene oportunidad abierta ({opp_id}); no se duplica.", flush=True)
        return {"ok": True, "contact_id": contact_id, "contact_new": is_new,
                "opportunity_id": opp_id, "opportunity_new": False}

    opp_name = f"{company} – {full_name}" if company else (full_name or email)
    o_status, o_res = _request("POST", "/opportunities/", token, {
        "locationId": location_id,
        "pipelineId": pipeline_id,
        "pipelineStageId": stage_id,
        "contactId": contact_id,
        "name": opp_name,
        "status": "open",
        "source": f"Web ProsperIA – {source}",
    })
    if o_status not in (200, 201):
        err_text = str(o_res.get("error", ""))
        if o_status == 400 and "OPPORTUNITY_NO_DUPLICATE" in err_text:
            m = re.search(r'"existingId"\s*:\s*"([^"]+)"', err_text)
            existing_id = m.group(1) if m else None
            print(f"ℹ️ [GHL] {email} ya tiene oportunidad ({existing_id}); no se duplica.", flush=True)
            return {"ok": True, "contact_id": contact_id, "contact_new": is_new,
                    "opportunity_id": existing_id, "opportunity_new": False}
        print(f"❌ [GHL] Contacto {contact_id} creado, pero falló la oportunidad: {o_status} {o_res}", flush=True)
        return {"ok": False, "step": "opportunity", "contact_id": contact_id, "status": o_status}

    opp_id = o_res.get("opportunity", {}).get("id")
    print(f"✅ [GHL] Lead {email} → contacto {contact_id} (nuevo={is_new}), oportunidad {opp_id} en Nuevo Contacto", flush=True)
    return {"ok": True, "contact_id": contact_id, "contact_new": is_new,
            "opportunity_id": opp_id, "opportunity_new": True}


def sync_lead_to_ghl_async(**kwargs) -> None:
    """Ejecuta la sincronización en segundo plano para no retrasar la respuesta del formulario."""
    def _run():
        try:
            sync_lead_to_ghl(**kwargs)
        except Exception as e:
            print(f"❌ [GHL] Error inesperado sincronizando lead: {e}", flush=True)
    threading.Thread(target=_run, daemon=True).start()

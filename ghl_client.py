"""Cliente de GoHighLevel (API v2) para sincronizar leads, etapas del Sales OS y pagos verificados.

Flujo por cada envío de formulario o actualización del CRM de Vendedores:
  1. Upsert del contacto (sin duplicar por email/teléfono) con campos estándar y personalizados.
  2. Etiquetas aditivas (lead_web + origen + etapa + vendedor + oferta).
  3. Nota de auditoría con el detalle completo del formulario, propuesta o pago verificado.
  4. Oportunidad en el pipeline "Ventas Agencia ProsperIA" → etapa inicial "Nuevo Contacto"
     y actualización de valor monetario/estatus cuando avanza en el Sales Operating System.

Configuración por variables de entorno (el token nunca va en el código):
  GHL_PRIVATE_TOKEN   Private Integration Token de la subcuenta (obligatorio).
  GHL_LOCATION_ID     ID de la subcuenta (Default: CNvJBINRWBUL2EdqRh3G).
  GHL_PIPELINE_ID     ID del pipeline destino (Default: SJ4xiMasQ0GZcUNYFgpa).
  GHL_STAGE_ID        ID de la etapa inicial.
Si falta el token, la sincronización se omite de forma segura sin afectar el CRM local.
"""
import json
import os
import re
import time
import threading
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Optional

GHL_BASE_URL = "https://services.leadconnectorhq.com"
GHL_API_VERSION = "2021-07-28"

DEFAULT_LOCATION_ID = "CNvJBINRWBUL2EdqRh3G"
DEFAULT_PIPELINE_ID = "SJ4xiMasQ0GZcUNYFgpa"        # Ventas Agencia ProsperIA
DEFAULT_STAGE_ID = "ffd8ae02-c4c0-431c-a827-0e909a80c752"  # Nuevo Contacto

# IDs de los campos personalizados de contacto creados en la subcuenta (CNvJBINRWBUL2EdqRh3G).
CF_INDUSTRIA = "K9N5HFBIpkonykvmoqB4"
CF_TAMANO_EQUIPO = "um5xkZ48Mmgx1GzqfpRK"
CF_CUELLO_BOTELLA = "z79pnM95XgAAfR0Vy6a8"

# IDs de los campos personalizados del Sales OS creados vía API v2 en GoHighLevel:
CF_OFERTA_VERSIONADA = "Ql6BkNqxZ7s3pWLDmM5B"       # contact.oferta_versionada_sales_os
CF_MONTO_COTIZADO = "ObjUbHcGuWSIK3K3Bgen"          # contact.monto_cotizado_usd
CF_MONTO_COBRADO = "Qrhj8GKXzVed6dGtcNTq"           # contact.monto_cobrado_verificado_usd
CF_ID_FACTURA = "Z1iPiC6jJooSLxBguOhE"              # contact.id_factura__comprobante
CF_COMISION_15 = "F5fzIuWGTGUyqK4kj6o9"             # contact.comision_causada_15_usd
CF_PLANTILLA_WEB = "saKXYwR9f9KiM8uFvKE5"           # contact.plantilla_web_seleccionada
CF_ESTADO_ENTREGA = "WSy2ykDYJpLcHUthLenI"          # contact.estado_entrega_sitio_web
CF_DUPLA_COMERCIAL = "HWashNLd4BfxzgTbhG0C"         # contact.dupla_comercial_asignada

# Mapeo 1 a 1 de las Etapas del Sales OS -> Stage IDs reales del Pipeline "Ventas Agencia ProsperIA" (SJ4xiMasQ0GZcUNYFgpa) en GoHighLevel
GHL_STAGE_MAP = {
    "Lead identificado": "ffd8ae02-c4c0-431c-a827-0e909a80c752",     # Nuevo Contacto
    "Primer contacto": "da2cda3e-8c0b-4c11-b6aa-03f9549b4824",       # Contactado
    "Conversación": "da2cda3e-8c0b-4c11-b6aa-03f9549b4824",          # Contactado
    "Calificado": "da2cda3e-8c0b-4c11-b6aa-03f9549b4824",            # Contactado
    "Diagnóstico agendado": "32169283-eb6a-446a-9092-67a39af8efdf",  # Llamada agendada
    "Demo realizada": "46602de4-7daf-4624-aa44-8aabca028497",        # Demo Realizada
    "Propuesta enviada": "21cded24-ce3b-4031-bbb1-0324723ce1f6",     # Propuesta enviada
    "Pago pendiente": "443683ab-9200-4d93-891a-8960a668e86b",        # Pago Pendiente
    "Pago confirmado": "f84fbfc3-06fd-48d0-a4dc-541792558815",       # Pago confirmado
    "Implementación": "4a358f0e-0c45-40fb-8b64-2b4c75746e3d",        # En implementacion
    "Entregado": "c05d2654-58de-48ee-bdf7-bb61cf1cefbd",             # Entregado
}

# Valores del <select> del formulario → opciones exactas del campo en GHL.
INDUSTRY_LABELS = {
    "clinica": "Clínica (Dental / Estética / Capilar)",
    "inmobiliaria": "Inmobiliaria / Bienes Raíces",
    "servicios_profesionales": "Servicios Profesionales / Consultoría",
    "profesionales": "Servicios Profesionales / Consultoría",
    "servicios_locales": "Servicios para el Hogar",
    "belleza_bienestar": "Belleza, Estética o Spa",
    "fitness": "Fitness o Wellness",
    "servicios_hogar": "Servicios para el Hogar",
    "taller_comercio": "Servicios para el Hogar",
    "enterprise": "Proyecto Empresarial / SVE90",
    "corporativo_sve90": "Proyecto Empresarial / SVE90",
    "otra": "Otra industria",
}
TEAM_LABELS = {
    "1-4": "1 a 4 personas",
    "5-15": "5 a 15 personas",
    "15+": "Más de 15 personas",
}


def _cfg(name: str, default: str = "") -> str:
    return (os.environ.get(name) or default).strip()


def _request(method: str, path: str, token: str, body: Optional[dict] = None, retries: int = 2):
    """Realiza petición a GHL con reintento automático ante rate-limit (HTTP 429)."""
    for attempt in range(retries + 1):
        req = urllib.request.Request(
            GHL_BASE_URL + path,
            method=method,
            data=json.dumps(body).encode("utf-8") if body is not None else None,
            headers={
                "Authorization": f"Bearer {token}",
                "Version": GHL_API_VERSION,
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "prosperia-sales-os/2.0",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw = resp.read().decode("utf-8") or "{}"
                return resp.status, json.loads(raw)
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries:
                time.sleep(1.5 * (attempt + 1))
                continue
            return e.code, {"error": e.read().decode("utf-8", "replace")[:500]}
        except Exception as e:
            if attempt < retries:
                time.sleep(1.0)
                continue
            return 0, {"error": str(e)}
    return 0, {"error": "Max retries exceeded"}


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


def _slug_tag(prefix: str, value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", (value or "").lower()).strip("_")
    return f"{prefix}_{slug}" if slug else prefix


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
    sms_consent: bool = False,
) -> dict:
    """Sincroniza un lead con GHL. Devuelve un resumen; nunca lanza excepciones."""
    token = _cfg("GHL_PRIVATE_TOKEN") or _cfg("GHL_ACCESS_TOKEN")
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
    consent_tag = "sms_opt_in" if sms_consent else "sms_sin_consentimiento"
    _request("POST", f"/contacts/{contact_id}/tags", token,
             {"tags": ["lead_web", _source_tag(source), consent_tag]})

    # 3. Nota con el detalle completo del envío.
    note_lines = [f"📥 Formulario web ({source})"]
    if sms_consent:
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        note_lines.append(f"✅ Consentimiento SMS otorgado: {stamp} – casilla del formulario web ({source}).")
    else:
        note_lines.append("⛔ Sin consentimiento SMS (no enviar SMS de marketing).")
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


def sync_sales_os_event_to_ghl_async(
    contact_id: str,
    opportunity_id: str,
    email: str,
    phone: str,
    full_name: str,
    business_name: str,
    pipeline_stage: str,
    owner_email: str,
    offer_version: str,
    quoted_amount: float,
    amount_collected: float,
    invoice_id: str,
    selected_template: str,
    audit_summary: str,
) -> None:
    """Sincroniza en segundo plano cualquier avance comercial del vendedor hacia GoHighLevel."""
    def _run():
        try:
            token = _cfg("GHL_PRIVATE_TOKEN") or _cfg("GHL_ACCESS_TOKEN")
            if not token:
                return
            cid = (contact_id or "").strip()
            opp_id = (opportunity_id or "").strip()
            if not cid and (email or phone):
                parts = (full_name or "").split()
                fn = parts[0] if parts else full_name
                ln = " ".join(parts[1:]) if len(parts) > 1 else ""
                up_res = sync_lead_to_ghl(
                    first_name=fn,
                    last_name=ln,
                    email=email,
                    phone=phone,
                    company=business_name,
                    source="sales_os_closer",
                )
                cid = up_res.get("contact_id") or ""
                opp_id = opp_id or (up_res.get("opportunity_id") or "")

            if not cid:
                return

            # Actualizar los 8 Campos Personalizados del Sales OS directamente en la ficha del contacto en GoHighLevel
            commission_15 = round(float(amount_collected or 0.0) * 0.15, 2) if (amount_collected and amount_collected > 0 and invoice_id) else 0.0
            delivery_status = "onboarding" if (amount_collected and amount_collected > 0 and invoice_id) else "pendiente_pago"
            custom_fields_payload = [
                {"id": CF_OFERTA_VERSIONADA, "field_value": str(offer_version or "EXPRESS_497")},
                {"id": CF_MONTO_COTIZADO, "field_value": float(quoted_amount or 0.0)},
                {"id": CF_MONTO_COBRADO, "field_value": float(amount_collected or 0.0)},
                {"id": CF_ID_FACTURA, "field_value": str(invoice_id or "")},
                {"id": CF_COMISION_15, "field_value": float(commission_15)},
                {"id": CF_PLANTILLA_WEB, "field_value": str(selected_template or "")},
                {"id": CF_ESTADO_ENTREGA, "field_value": delivery_status},
                {"id": CF_DUPLA_COMERCIAL, "field_value": str(owner_email or "")},
            ]
            _request("PUT", f"/contacts/{cid}", token, {"customFields": custom_fields_payload})

            tags = [
                _slug_tag("etapa", pipeline_stage),
                _slug_tag("oferta", offer_version),
            ]
            if owner_email:
                tags.append(_slug_tag("closer", owner_email.split("@")[0]))
            if selected_template:
                tags.append(_slug_tag("plantilla", selected_template))
            if amount_collected and amount_collected > 0 and invoice_id:
                tags.append("pago_verificado_crm")
            _request("POST", f"/contacts/{cid}/tags", token, {"tags": tags})

            stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            note_body = (
                f"📊 [SALES OS PROSPER IA — {stamp}]\n"
                f"• Etapa Comercial: {pipeline_stage}\n"
                f"• Vendedor Responsable: {owner_email or 'Sin asignar'}\n"
                f"• Oferta Versionada: {offer_version} | Propuesta: US${quoted_amount:,.2f}\n"
                f"• Cobro Verificado: US${amount_collected:,.2f} (Factura/Ref: {invoice_id or 'Pendiente'})\n"
                f"• Comisión 15% Causada: US${commission_15:,.2f}\n"
                f"• Plantilla Sitio Web: {selected_template or 'Por definir'}\n"
                f"• Detalle: {audit_summary}"
            )
            _request("POST", f"/contacts/{cid}/notes", token, {"body": note_body})

            if opp_id:
                opp_status = "open"
                if pipeline_stage in ("Pago confirmado", "Implementación", "Entregado"):
                    opp_status = "won"
                elif pipeline_stage in ("No interesado", "No cumple perfil", "Opt-out", "Venta perdida", "Reembolso/contracargo"):
                    opp_status = "lost"
                elif pipeline_stage == "No responde":
                    opp_status = "abandoned"
                monetary_val = amount_collected if amount_collected > 0 else quoted_amount
                opp_update_body = {
                    "status": opp_status,
                    "monetaryValue": float(monetary_val or 0.0),
                }
                mapped_stage_id = GHL_STAGE_MAP.get(pipeline_stage)
                if mapped_stage_id:
                    opp_update_body["pipelineStageId"] = mapped_stage_id
                _request("PUT", f"/opportunities/{opp_id}", token, opp_update_body)
        except Exception as exc:
            print(f"⚠️ [GHL SALES OS SYNC] Error no bloqueante: {exc}", flush=True)

    threading.Thread(target=_run, daemon=True).start()

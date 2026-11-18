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
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Optional

GHL_BASE_URL = "https://services.leadconnectorhq.com"
GHL_API_VERSION = "2021-07-28"

DEFAULT_LOCATION_ID = "CNvJBINRWBUL2EdqRh3G"
DEFAULT_PIPELINE_ID = "G9nVz4GhrxAROVkPtPis"        # Ventas Sitios Web & Closers ProsperIA (Exclusivo B2B / Closers)
DEFAULT_STAGE_ID = "38a46419-b420-49a6-8df6-021cb0467dd0"  # 1. Nuevo Prospecto (/sitioweb)

# Subcuenta y Pipeline dedicados EXCLUSIVAMENTE a la vertical Beauty Growth & Business System
BEAUTY_LOCATION_ID = "V8tM5xk6xl15wKhbQS0p"
BEAUTY_PIPELINE_ID = "BBQlDFhNVE0NRmKNTMS2"   # Creado vía API v2 en subcuenta Beauty Growth (V8tM5xk6xl15wKhbQS0p)
BEAUTY_PIPELINE_NAME = "Beauty Growth & Business System"
BEAUTY_PIPELINE_STAGES = [
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
# Mapeo 1 a 1 de las 14 etapas de la Sección 7.3 -> Stage IDs reales en Beauty Growth (V8tM5xk6xl15wKhbQS0p)
BEAUTY_STAGE_MAP = {
    "1. Prospecto identificado": "76e19c7f-76bd-47dd-9c8e-01ad42834759",
    "2. Primer contacto": "f84baaa2-9440-4391-ac91-d1e70dddfbb5",
    "3. Segundo contacto": "8af5f803-ce16-4acf-a2cc-b6b569e8e5be",
    "4. Tercer contacto": "3f1f56d9-6cf5-4d38-904b-918ade84da47",
    "5. Respondió / Interesado": "cc2b04de-8d38-4c73-89d9-e01983a369c8",
    "6. Seguimiento": "1e08061a-e60a-4783-ba25-9a40589e44cd",
    "7. Lead calificado": "1725e066-8608-4b2c-9b72-3635d70529ae",
    "8. Reunión agendada": "c0133849-1267-4404-84b3-ecb41439845c",
    "9. Reunión confirmada": "0bdcf4ae-993b-4479-95ce-9b99b60b55be",
    "10. Reunión realizada": "3b6377b4-3636-4cda-bf5f-8658d5bf8e26",
    "11. Propuesta enviada": "eb27f27a-d321-4c58-bb08-4b1903761109",
    "12. Negociación activa": "acb9428c-6987-4aa4-b0d1-6b3865d84cfc",
    "13. Ganado / Cierre": "b45372f5-eb73-4189-b673-a746b9da85ec",
    "14. Perdido / No calificado": "b3e57e5e-8822-4774-99eb-0bb07f3798e4",
}
_BEAUTY_PIPELINE_CACHE = {}

# Usuario Admin y Calendario oficial de la subcuenta Beauty Growth (V8tM5xk6xl15wKhbQS0p)
BEAUTY_DEFAULT_USER_ID = "584u95aJ9e8PLDYOASXm"  # David Becerra (dbecerra@agenciaprosperia.com)
BEAUTY_CALENDAR_URL = "https://api.agenciaprosperia.com/widget/booking/cjMUGPVYG0Z1ABRiUf6j"
BEAUTY_OFFER_PRICES = {
    "BEAUTY_BOOST_1499": 1499.0,
    "BEAUTY_ELEVATE_2499": 2499.0,
    "BEAUTY_EMPIRE_3499": 3499.0,
    "BEAUTY_HIGHTICKET_5000": 5000.0,
}

# IDs reales de los 11 campos personalizados creados en la subcuenta Beauty Growth (V8tM5xk6xl15wKhbQS0p)
CF_BG_PAQUETE = "W0e01iiGbg1PHe2ENXT6"        # contact.paquete_beauty_growth
CF_BG_FACTURACION = "Zr2yg2YzfrMxT378fnal"    # contact.facturacion_mensual_belleza
CF_BG_CIUDAD = "mxnMlljhF4gibbxvWM8E"         # contact.ciudad_o_mercado_beauty
CF_BG_INSTAGRAM = "tNX54s024yqpM7SnEBHK"      # contact.instagram_negocio_belleza
CF_BG_PRESUPUESTO = "KEm6yOpDaHPZkcsjd4nX"    # contact.presupuesto_meta_ads_usd
CF_BG_NOTAS = "B85Jk2JfCpdPD5TebLoB"          # contact.notas_diagnostico_closer
CF_BG_BIOGRAFIA = "Cfdeptn05kCEd1Eox7jX"      # contact.biografia_instagram_beauty
CF_BG_SEGUIDORES = "uEuOsWPRiNgb6K8M7S8S"     # contact.seguidores_instagram
CF_BG_SEGUIDOS = "Sljm6KsI6j8ZTPLBTtF1"       # contact.seguidos_instagram
CF_BG_WEB_AGENDA = "6I4LCDTQj1RHuSVMOxKm"     # contact.sitio_web_o_agenda_beauty
CF_BG_SETTER = "TzYpA5qTTBJfYjVcb9Ds"         # contact.setter_asignado_beauty

# Pipeline separado para solicitudes web generales / códigos gratuitos / comunidad ("Ventas Agencia ProsperIA")
CODIGOS_PIPELINE_ID = "SJ4xiMasQ0GZcUNYFgpa"
CODIGOS_STAGE_ID = "ffd8ae02-c4c0-431c-a827-0e909a80c752"

# Etiqueta oficial del Sprint Comercial de Closers (11,000 leads -> resultados CRM con WhatsApp/SMS/Correo)
CLOSER_SPRINT_TAG = "semana18nov"
CLOSER_AUTOMATION_TAGS = (
    CLOSER_SPRINT_TAG,
    "sprint_18nov_closers",
    "closer_calificado_crm",
    "sms_opt_in",
)

# Plantillas de WhatsApp aprobadas por Meta en la subcuenta CNvJBINRWBUL2EdqRh3G (+1 786-833-6964)
GHL_WA_TEMPLATES = {
    "reactivacion_prosper_ia": {
        "tag": "wa_plantilla_prosper_ia",
        "label": "Saludo & Crecimiento Digital (reactivacion_prosper_ia)",
    },
    "reactivacion_oferta_directa": {
        "tag": "wa_plantilla_oferta_directa",
        "label": "Oferta Directa Prosper IA (reactivacion_oferta_directa)",
    },
    "reactivacion_valor_inicial": {
        "tag": "wa_plantilla_valor_inicial",
        "label": "Valor Inicial & Diagnóstico (reactivacion_valor_inicial)",
    },
}

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

# Mapeo 1 a 1 de las Etapas del Sales OS -> Stage IDs reales del Pipeline "Ventas Sitios Web & Closers ProsperIA" (G9nVz4GhrxAROVkPtPis) en GoHighLevel
GHL_STAGE_MAP = {
    "Lead identificado": "38a46419-b420-49a6-8df6-021cb0467dd0",     # 1. Nuevo Prospecto (/sitioweb)
    "Primer contacto": "9ece5b23-ff55-4cad-8ac7-eb94cd792af4",       # 2. Contactado por Closer
    "Conversación": "9ece5b23-ff55-4cad-8ac7-eb94cd792af4",          # 2. Contactado por Closer
    "Calificado": "9ece5b23-ff55-4cad-8ac7-eb94cd792af4",            # 2. Contactado por Closer
    "Diagnóstico agendado": "fd4c0d7c-49b3-4e45-9739-69318812b07d",  # 3. Cita / Diagnóstico Agendado
    "Demo realizada": "528d97ca-730f-4d5b-9afc-264f6f32dcca",        # 4. Demo en Vivo Realizada
    "Propuesta enviada": "20a0b562-9e0a-4e36-a6f0-c898c65aeeec",     # 5. Propuesta Enviada ($497 / $990 / $1,490)
    "Pago pendiente": "5c6e1081-a6a9-4499-b940-2973dd935759",        # 6. Link de Pago Enviado (50% Anticipo)
    "Pago confirmado": "58da7d90-4736-4b46-b2cb-6827d2bb1fad",       # 7. Anticipo / Pago Confirmado
    "Implementación": "f4974bf4-7e53-4897-a147-ccc9218829bf",        # 8. En Construcción (72 hrs)
    "Entregado": "3792e71a-6458-49f8-bd35-70cf29547078",             # 9. Sitio Entregado & Activo
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
    val = (os.environ.get(name) or "").strip()
    if val:
        return val
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_file):
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(f"{name}="):
                        parsed = line.split("=", 1)[1].strip().strip("'\"")
                        if parsed:
                            return parsed
        except Exception:
            pass
    return default.strip()


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


def _infer_country_routing_tags(phone: str, country: str = "") -> list:
    """Devuelve etiquetas de enrutamiento comercial por país para workflows GHL y candado anti-tarifas."""
    raw = (phone or "").strip()
    c_low = (country or "").strip().lower()
    cleaned = _clean_phone(raw)
    latam_hint = any(k in c_low for k in ("argent", "mex", "méx", "colomb", "chile", "per", "espa", "latam", "ecuad", "urug"))

    if cleaned.startswith("+54") or "argent" in c_low:
        return ["pais_argentina_54", "pais_latam_wa"]
    if (cleaned.startswith("+1") and len(cleaned) == 12 and not latam_hint) or (
        not raw and any(k in c_low for k in ("estados unidos", "usa", "puerto rico", "us")) and c_low != "latam / us"
    ):
        return ["pais_usa_1", "ruta_sip_miami"]
    return ["pais_latam_wa"]


def _is_beauty_growth(
    source: str = "",
    industry: str = "",
    owner_email: str = "",
    offer_version: str = "",
) -> bool:
    src = (source or "").lower()
    ind = (industry or "").lower()
    own = (owner_email or "").strip().lower()
    off = (offer_version or "").strip().upper()
    return (
        "beauty" in src
        or "beauty" in ind
        or own == "dbecerra@agenciaprosperia.com"
        or off.startswith("BEAUTY_")
    )


def _build_beauty_stage_lookup(raw_pairs: dict) -> dict:
    """Normaliza un diccionario {nombre_etapa: stage_id} para aceptar con/sin prefijo numérico."""
    stages_map = {}
    for raw_name, st_id in raw_pairs.items():
        st_name = (raw_name or "").strip()
        clean_id = (st_id or "").strip()
        if not st_name or not clean_id:
            continue
        stages_map[st_name] = clean_id
        stages_map[st_name.lower()] = clean_id
        stripped = re.sub(r"^\d+\.\s*", "", st_name).strip().lower()
        if stripped:
            stages_map[stripped] = clean_id
    return stages_map


def _cfg_db(key: str, default: str = "") -> str:
    """Lee configuración desde env/.env o tabla integration_settings de SQLite sin requerir reiniciar contenedor."""
    val = _cfg(key)
    if val:
        return val
    try:
        from database import IntegrationSetting, SessionLocal

        db = SessionLocal()
        try:
            row = (
                db.query(IntegrationSetting)
                .filter(IntegrationSetting.key.in_([key, key.lower(), key.upper()]))
                .first()
            )
            if row and (row.value or "").strip():
                return row.value.strip()
        finally:
            db.close()
    except Exception:
        pass
    return default.strip()


def _save_beauty_db_settings(location_id: str, pipeline_id: str, stages_list: list) -> None:
    """Persiste en SQLite los IDs descubiertos/creados para la subcuenta Beauty Growth."""
    try:
        from database import IntegrationSetting, SessionLocal

        db = SessionLocal()
        try:
            pairs = {
                "ghl_beauty_location_active": location_id,
                "ghl_beauty_pipeline_id": pipeline_id,
                "ghl_beauty_stages_json": json.dumps(stages_list or [], ensure_ascii=False),
            }
            for k, v in pairs.items():
                if not v:
                    continue
                row = db.query(IntegrationSetting).filter(IntegrationSetting.key == k).first()
                if row:
                    row.value = v
                else:
                    db.add(IntegrationSetting(key=k, value=v))
            db.commit()
        finally:
            db.close()
    except Exception as exc:
        print(f"⚠️ [GHL BEAUTY DB] No se pudieron guardar IDs locales: {exc}", flush=True)


def _cached_beauty_pipeline_from_db() -> dict:
    """Recupera mapa de etapas guardado para V8tM5xk6xl15wKhbQS0p (nunca de otra subcuenta)."""
    loc_active = _cfg_db("ghl_beauty_location_active", BEAUTY_LOCATION_ID)
    if loc_active != BEAUTY_LOCATION_ID:
        return {"pipeline_id": "", "pipeline_name": BEAUTY_PIPELINE_NAME, "stages": {}, "default_stage_id": "", "location_id": BEAUTY_LOCATION_ID}

    pip_id = _cfg_db("ghl_beauty_pipeline_id") or BEAUTY_PIPELINE_ID
    raw_json = _cfg_db("ghl_beauty_stages_json")
    raw_pairs = dict(BEAUTY_STAGE_MAP)
    first_id = BEAUTY_STAGE_MAP.get("1. Prospecto identificado", "")
    if raw_json:
        try:
            for item in json.loads(raw_json):
                nm = (item.get("name") or "").strip()
                sid = (item.get("id") or "").strip()
                if sid and not first_id:
                    first_id = sid
                if nm and sid:
                    raw_pairs[nm] = sid
        except Exception:
            pass
    stages_map = _build_beauty_stage_lookup(raw_pairs)
    return {
        "pipeline_id": pip_id,
        "pipeline_name": BEAUTY_PIPELINE_NAME,
        "stages": stages_map,
        "default_stage_id": stages_map.get("5. Respondió / Interesado") or _cfg_db("GHL_BEAUTY_STAGE_ID") or first_id,
        "location_id": BEAUTY_LOCATION_ID,
    }


def _resolve_beauty_stage_id(stages_map: dict, stage_name: str, default_id: str = "") -> str:
    """Resuelve una etapa Beauty Growth (con o sin número) o mapea equivalencias canónicas."""
    if not stage_name:
        return default_id
    s = stage_name.strip()
    if s in stages_map:
        return stages_map[s]
    s_low = s.lower()
    if s_low in stages_map:
        return stages_map[s_low]
    stripped = re.sub(r"^\d+\.\s*", "", s).strip().lower()
    if stripped in stages_map:
        return stages_map[stripped]
    canonical_to_beauty = {
        "lead identificado": "1. Prospecto identificado",
        "primer contacto": "2. Primer contacto",
        "conversación": "5. Respondió / Interesado",
        "calificado": "7. Lead calificado",
        "diagnóstico agendado": "8. Reunión agendada",
        "demo realizada": "10. Reunión realizada",
        "propuesta enviada": "11. Propuesta enviada",
        "pago pendiente": "12. Negociación activa",
        "pago confirmado": "13. Ganado / Cierre",
        "implementación": "13. Ganado / Cierre",
        "entregado": "13. Ganado / Cierre",
        "no interesado": "14. Perdido / No calificado",
        "no cumple perfil": "14. Perdido / No calificado",
        "venta perdida": "14. Perdido / No calificado",
    }
    target = canonical_to_beauty.get(s_low)
    if target and target in stages_map:
        return stages_map[target]
    return default_id


def discover_beauty_pipeline_and_stages(token: str, location_id: str = "") -> dict:
    """Consulta o crea automáticamente el Pipeline de 14 etapas EXCLUSIVAMENTE en la subcuenta Beauty Growth (V8tM5xk6xl15wKhbQS0p)."""
    loc = location_id or _cfg_db("GHL_BEAUTY_LOCATION_ID", BEAUTY_LOCATION_ID) or BEAUTY_LOCATION_ID
    if not token:
        return {"pipeline_id": "", "pipeline_name": BEAUTY_PIPELINE_NAME, "stages": {}, "default_stage_id": "", "location_id": loc, "needs_token": True}
    if loc in _BEAUTY_PIPELINE_CACHE and _BEAUTY_PIPELINE_CACHE[loc].get("stages"):
        return _BEAUTY_PIPELINE_CACHE[loc]

    status, res = _request("GET", f"/opportunities/pipelines?locationId={loc}", token)
    if status != 200:
        print(f"⚠️ [GHL BEAUTY] Token sin acceso a subcuenta Beauty Growth ({loc}): HTTP {status} {res}", flush=True)
        return {"pipeline_id": "", "pipeline_name": BEAUTY_PIPELINE_NAME, "stages": {}, "default_stage_id": "", "location_id": loc, "error": res}

    pipelines = res.get("pipelines") or []
    env_pip_id = _cfg_db("GHL_BEAUTY_PIPELINE_ID")
    chosen = None
    if env_pip_id:
        for p in pipelines:
            if p.get("id") == env_pip_id:
                chosen = p
                break
    if not chosen:
        for p in pipelines:
            if "beauty growth" in (p.get("name") or "").lower():
                chosen = p
                break

    # Si no existe aún el pipeline de 14 etapas en V8tM5xk6xl15wKhbQS0p, lo creamos automáticamente aquí
    if not chosen:
        create_payload = {
            "locationId": loc,
            "name": BEAUTY_PIPELINE_NAME,
            "showInFunnel": True,
            "showInPieChart": True,
            "stages": [
                {"name": name, "position": idx, "showInFunnel": True, "showInPieChart": True}
                for idx, name in enumerate(BEAUTY_PIPELINE_STAGES)
            ],
        }
        st_cp, cp_res = _request("POST", "/opportunities/pipelines", token, create_payload)
        if st_cp in (200, 201):
            chosen = cp_res.get("pipeline") or cp_res
            print(f"✅ [GHL BEAUTY] Pipeline '{BEAUTY_PIPELINE_NAME}' creado automáticamente en subcuenta {loc} ({chosen.get('id')}).", flush=True)
        else:
            print(f"❌ [GHL BEAUTY] No se pudo crear el pipeline en {loc}: HTTP {st_cp} {cp_res}", flush=True)
            if pipelines:
                chosen = pipelines[0]

    if not chosen:
        return {"pipeline_id": "", "pipeline_name": BEAUTY_PIPELINE_NAME, "stages": {}, "default_stage_id": "", "location_id": loc}

    stages_list = chosen.get("stages") or []
    raw_pairs = {}
    first_stage_id = ""
    for st in stages_list:
        st_name = (st.get("name") or "").strip()
        st_id = (st.get("id") or "").strip()
        if not st_id:
            continue
        if not first_stage_id:
            first_stage_id = st_id
        if st_name:
            raw_pairs[st_name] = st_id

    stages_map = _build_beauty_stage_lookup(raw_pairs)
    pip_id = chosen.get("id") or ""
    _save_beauty_db_settings(loc, pip_id, stages_list)
    data = {
        "pipeline_id": pip_id,
        "pipeline_name": chosen.get("name") or BEAUTY_PIPELINE_NAME,
        "stages": stages_map,
        "stages_raw": stages_list,
        "default_stage_id": stages_map.get("5. Respondió / Interesado") or _cfg_db("GHL_BEAUTY_STAGE_ID") or first_stage_id,
        "location_id": loc,
    }
    _BEAUTY_PIPELINE_CACHE[loc] = data
    return data


def _resolve_beauty_connection() -> tuple:
    """Resuelve (token, location_id, pipeline_discovery) EXCLUSIVAMENTE para V8tM5xk6xl15wKhbQS0p (sin fallback a CNvJBINRWBUL2EdqRh3G)."""
    beauty_tok = _cfg_db("GHL_BEAUTY_PRIVATE_TOKEN")
    beauty_loc = _cfg_db("GHL_BEAUTY_LOCATION_ID", BEAUTY_LOCATION_ID) or BEAUTY_LOCATION_ID
    if not beauty_tok:
        return "", beauty_loc, _cached_beauty_pipeline_from_db()
    disc = discover_beauty_pipeline_and_stages(beauty_tok, beauty_loc)
    return beauty_tok, beauty_loc, disc


def _extract_beauty_custom_fields(raw_text: str, offer_version: str = "", industry: str = "") -> list:
    """Extrae Ciudad, Facturación, Paquete e Instagram del mensaje de /beautygrowth hacia los 6 campos de V8tM5xk6xl15wKhbQS0p."""
    text = (raw_text or "").strip()

    def _grab(label_pat: str) -> str:
        m = re.search(rf"{label_pat}\s*:\s*([^|\n]+)", text, re.IGNORECASE)
        return m.group(1).strip() if m else ""

    paquete = _grab(r"Paquete") or (offer_version or "BEAUTY_ELEVATE_2499")
    ciudad = _grab(r"Ciudad/Mercado") or _grab(r"Ciudad")
    facturacion = _grab(r"Facturaci[oó]n(?:\s+actual)?")
    notas_ig = _grab(r"Notas/IG") or _grab(r"Instagram")
    ig_match = re.search(r"(@[A-Za-z0-9._]+|https?://(?:www\.)?instagram\.com/[^\s|,]+)", text, re.IGNORECASE)
    instagram = ig_match.group(1) if ig_match else notas_ig

    fields = []
    if paquete:
        fields.append({"id": CF_BG_PAQUETE, "field_value": paquete})
    if facturacion:
        fields.append({"id": CF_BG_FACTURACION, "field_value": facturacion})
    if ciudad:
        fields.append({"id": CF_BG_CIUDAD, "field_value": ciudad})
    if instagram:
        fields.append({"id": CF_BG_INSTAGRAM, "field_value": instagram})
    if "miami" in ciudad.lower() or "houston" in ciudad.lower() or "florida" in ciudad.lower() or "tx" in ciudad.lower():
        fields.append({"id": CF_BG_PRESUPUESTO, "field_value": "$800 - $1,500 USD/mes"})
    elif ciudad:
        fields.append({"id": CF_BG_PRESUPUESTO, "field_value": "$500 - $1,000 USD/mes"})
    note_val = text or industry
    if note_val:
        fields.append({"id": CF_BG_NOTAS, "field_value": note_val[:900]})
    return fields


def _persist_lead_ghl_ids(lead_db_id: Optional[int], contact_id: str, opp_id: Optional[str]) -> None:
    """Guarda contact_id y ghl_opportunity_id en SQLite cuando el lead se sincroniza con GHL."""
    if not lead_db_id or (not contact_id and not opp_id):
        return
    try:
        from database import Lead as DbLead, SessionLocal

        db = SessionLocal()
        try:
            row = db.query(DbLead).filter(DbLead.id == lead_db_id).first()
            if row:
                if contact_id:
                    row.contact_id = contact_id
                if opp_id:
                    row.ghl_opportunity_id = opp_id
                db.commit()
        finally:
            db.close()
    except Exception as exc:
        print(f"⚠️ [GHL DB SYNC] No se pudieron actualizar IDs en Lead {lead_db_id}: {exc}", flush=True)


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
    assigned_to: str = "",
    extra_tags: Optional[list] = None,
    owner_email: str = "",
    offer_version: str = "",
    initial_stage: str = "",
    lead_db_id: Optional[int] = None,
) -> dict:
    """Sincroniza un lead con GHL. Devuelve un resumen; nunca lanza excepciones."""
    is_beauty = _is_beauty_growth(
        source=source,
        industry=industry,
        owner_email=owner_email,
        offer_version=offer_version,
    )
    if is_beauty:
        token, location_id, disc = _resolve_beauty_connection()
        if not token:
            print(
                f"ℹ️ [GHL BEAUTY GROWTH] Token GHL_BEAUTY_PRIVATE_TOKEN no configurado aún para la subcuenta {location_id}; "
                "lead guardado en SQLite pendiente de sincronizar cuando se conecte la subcuenta.",
                flush=True,
            )
            return {"ok": False, "skipped": True, "location_id": location_id}
        if not assigned_to:
            assigned_to = BEAUTY_DEFAULT_USER_ID
        pipeline_id = disc.get("pipeline_id") or _cfg_db("GHL_BEAUTY_PIPELINE_ID") or BEAUTY_PIPELINE_ID
        stages_map = disc.get("stages") or _build_beauty_stage_lookup(BEAUTY_STAGE_MAP)
        inferred_stage = initial_stage
        if not inferred_stage:
            msg_low = (message or notes or "").lower()
            has_slot = (
                any(tok in msg_low for tok in ("fecha:", "horario:", "cita agendada", "reunión agendada"))
                or bool(re.search(r"\b\d{1,2}:\d{2}\s*(am|pm)\b", msg_low))
            )
            inferred_stage = "8. Reunión agendada" if has_slot else "5. Respondió / Interesado"
        default_st = (
            stages_map.get("5. Respondió / Interesado")
            or _cfg_db("GHL_BEAUTY_STAGE_ID")
            or disc.get("default_stage_id", "")
        )
        stage_id = _resolve_beauty_stage_id(stages_map, inferred_stage, default_st)
    else:
        token = _cfg_db("GHL_PRIVATE_TOKEN") or _cfg_db("GHL_ACCESS_TOKEN")
        if not token:
            print("ℹ️ [GHL] GHL_PRIVATE_TOKEN no configurado; sincronización omitida.", flush=True)
            return {"ok": False, "skipped": True}
        location_id = _cfg_db("GHL_LOCATION_ID", DEFAULT_LOCATION_ID)
        src_lower = (source or "").lower()
        is_closer_origin = (
            any(k in src_lower for k in ("sales_os_closer", "closer_prospeccion_propia", "closer_lote_excel"))
            or bool((owner_email or "").strip())
        )
        if is_closer_origin:
            # Excluye formularios web generales; este pipeline recibe SOLO resultados provocados por Closers
            pipeline_id = DEFAULT_PIPELINE_ID
            stage_id = GHL_STAGE_MAP.get(initial_stage) or DEFAULT_STAGE_ID
        else:
            # Formularios generales de la web y comunidad van a "Ventas Agencia ProsperIA"
            pipeline_id = CODIGOS_PIPELINE_ID
            stage_id = CODIGOS_STAGE_ID

    full_name = f"{first_name} {last_name}".strip()
    custom_fields = []
    industry_label = INDUSTRY_LABELS.get((industry or "").strip().lower())
    if is_beauty and location_id == BEAUTY_LOCATION_ID:
        team_label = TEAM_LABELS.get((team_size or "").strip())
        custom_fields = _extract_beauty_custom_fields(message or notes, offer_version=offer_version, industry=industry)
    elif location_id == DEFAULT_LOCATION_ID:
        if industry_label:
            custom_fields.append({"id": CF_INDUSTRIA, "field_value": industry_label})
        team_label = TEAM_LABELS.get((team_size or "").strip())
        if team_label:
            custom_fields.append({"id": CF_TAMANO_EQUIPO, "field_value": team_label})
        if message:
            custom_fields.append({"id": CF_CUELLO_BOTELLA, "field_value": message})
    else:
        team_label = TEAM_LABELS.get((team_size or "").strip())

    contact_body = {
        "locationId": location_id,
        "firstName": first_name,
        "lastName": last_name,
        "name": full_name,
        "email": email,
        "companyName": company,
        "source": f"Beauty Growth – {source}" if is_beauty else f"Web ProsperIA – {source}",
    }
    if custom_fields:
        contact_body["customFields"] = custom_fields
    clean_phone = _clean_phone(phone)
    if clean_phone:
        contact_body["phone"] = clean_phone
    if assigned_to:
        contact_body["assignedTo"] = assigned_to

    # 1. Upsert del contacto (si el teléfono es inválido, reintenta sin él).
    status, res = _request("POST", "/contacts/upsert", token, contact_body)
    if status not in (200, 201) and "phone" in contact_body:
        print(f"⚠️ [GHL] Upsert con teléfono falló ({status}); reintentando sin teléfono.", flush=True)
        contact_body.pop("phone")
        status, res = _request("POST", "/contacts/upsert", token, contact_body)
    if status not in (200, 201):
        print(f"❌ [GHL] No se pudo crear/actualizar el contacto {email} (loc={location_id}): {status} {res}", flush=True)
        return {"ok": False, "step": "contact", "status": status, "location_id": location_id}

    contact = res.get("contact", {})
    contact_id = contact.get("id")
    is_new = res.get("new")

    # 2. Etiquetas (aditivas: no borran las existentes).
    is_closer_origin = (not is_beauty) and (
        any(k in (source or "").lower() for k in ("sales_os_closer", "closer_prospeccion_propia", "closer_lote_excel"))
        or bool((owner_email or "").strip())
    )
    consent_tag = "sms_opt_in" if (sms_consent or is_closer_origin) else "sms_sin_consentimiento"
    tag_list = ["lead_web" if not is_closer_origin else "closer_sprint_11k", _source_tag(source), consent_tag]
    if is_closer_origin:
        for ct in CLOSER_AUTOMATION_TAGS:
            if ct not in tag_list:
                tag_list.append(ct)
        if owner_email:
            ct_closer = _slug_tag("closer", owner_email.split("@")[0])
            if ct_closer not in tag_list:
                tag_list.append(ct_closer)
    if is_beauty:
        for bt in ("beauty_growth", "vertical_belleza", "socio_jhonkelwins_becerra"):
            if bt not in tag_list:
                tag_list.append(bt)
    else:
        for rt in _infer_country_routing_tags(phone):
            if rt not in tag_list:
                tag_list.append(rt)
    if extra_tags:
        for t in extra_tags:
            if t and t not in tag_list:
                tag_list.append(t)
    _request("POST", f"/contacts/{contact_id}/tags", token, {"tags": tag_list})

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

    if not pipeline_id or not stage_id:
        print(f"ℹ️ [GHL] Contacto {contact_id} creado en {location_id}, pendiente pipeline_id/stage_id de Beauty Growth.", flush=True)
        return {"ok": True, "contact_id": contact_id, "contact_new": is_new, "opportunity_id": None, "opportunity_new": False}

    # 4. Oportunidad solo si no existe una abierta en el pipeline.
    q = (f"/opportunities/search?location_id={location_id}&contact_id={contact_id}"
         f"&pipeline_id={pipeline_id}&status=open&limit=1")
    s_status, s_res = _request("GET", q, token)
    if s_status == 200 and s_res.get("opportunities"):
        opp_id = s_res["opportunities"][0].get("id")
        _persist_lead_ghl_ids(lead_db_id, contact_id, opp_id)
        print(f"ℹ️ [GHL] {email} ya tiene oportunidad abierta ({opp_id}); no se duplica.", flush=True)
        return {"ok": True, "contact_id": contact_id, "contact_new": is_new,
                "opportunity_id": opp_id, "opportunity_new": False,
                "location_id": location_id, "pipeline_id": pipeline_id, "stage_id": stage_id}

    opp_name = f"{company} – {full_name}" if company else (full_name or email)
    opp_payload = {
        "locationId": location_id,
        "pipelineId": pipeline_id,
        "pipelineStageId": stage_id,
        "contactId": contact_id,
        "name": opp_name,
        "status": "open",
        "source": f"Beauty Growth – {source}" if is_beauty else f"Web ProsperIA – {source}",
    }
    if is_beauty:
        opp_val = BEAUTY_OFFER_PRICES.get((offer_version or "").strip().upper(), 2499.0)
        opp_payload["monetaryValue"] = float(opp_val)
    if assigned_to:
        opp_payload["assignedTo"] = assigned_to
    o_status, o_res = _request("POST", "/opportunities/", token, opp_payload)
    if o_status not in (200, 201):
        err_text = str(o_res.get("error", ""))
        if o_status == 400 and "OPPORTUNITY_NO_DUPLICATE" in err_text:
            m = re.search(r'"existingId"\s*:\s*"([^"]+)"', err_text)
            existing_id = m.group(1) if m else None
            _persist_lead_ghl_ids(lead_db_id, contact_id, existing_id)
            print(f"ℹ️ [GHL] {email} ya tiene oportunidad ({existing_id}); no se duplica.", flush=True)
            return {"ok": True, "contact_id": contact_id, "contact_new": is_new,
                    "opportunity_id": existing_id, "opportunity_new": False,
                    "location_id": location_id, "pipeline_id": pipeline_id, "stage_id": stage_id}
        print(f"❌ [GHL] Contacto {contact_id} creado, pero falló la oportunidad: {o_status} {o_res}", flush=True)
        return {"ok": False, "step": "opportunity", "contact_id": contact_id, "status": o_status}

    opp_id = o_res.get("opportunity", {}).get("id")
    _persist_lead_ghl_ids(lead_db_id, contact_id, opp_id)
    print(f"✅ [GHL] Lead {email} → contacto {contact_id} (nuevo={is_new}), oportunidad {opp_id} en loc={location_id} (pipeline={pipeline_id})", flush=True)
    return {"ok": True, "contact_id": contact_id, "contact_new": is_new,
            "opportunity_id": opp_id, "opportunity_new": True,
            "location_id": location_id, "pipeline_id": pipeline_id, "stage_id": stage_id}


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
    lead_db_id: Optional[int] = None,
) -> None:
    """Sincroniza en segundo plano cualquier avance comercial del vendedor hacia GoHighLevel."""
    def _run():
        try:
            is_beauty = (
                _is_beauty_growth(owner_email=owner_email, offer_version=offer_version)
                or pipeline_stage in BEAUTY_PIPELINE_STAGES
                or "beauty" in (selected_template or "").lower()
            )
            if is_beauty:
                token, loc_id, beauty_disc = _resolve_beauty_connection()
                pip_id = beauty_disc.get("pipeline_id") or _cfg_db("GHL_BEAUTY_PIPELINE_ID")
            else:
                token = _cfg_db("GHL_PRIVATE_TOKEN") or _cfg_db("GHL_ACCESS_TOKEN")
                loc_id = _cfg_db("GHL_LOCATION_ID", DEFAULT_LOCATION_ID)
                beauty_disc = {}
                pip_id = DEFAULT_PIPELINE_ID
            if not token:
                return

            cid = (contact_id or "").strip()
            opp_id = (opportunity_id or "").strip()
            if (not cid or not opp_id) and (email or phone):
                parts = (full_name or "").split()
                fn = parts[0] if parts else full_name
                ln = " ".join(parts[1:]) if len(parts) > 1 else ""
                up_res = sync_lead_to_ghl(
                    first_name=fn,
                    last_name=ln,
                    email=email,
                    phone=phone,
                    company=business_name,
                    source="beautygrowth_sales_os" if is_beauty else "sales_os_closer",
                    owner_email=owner_email,
                    offer_version=offer_version,
                    initial_stage=pipeline_stage,
                    sms_consent=True,
                    lead_db_id=lead_db_id,
                )
                cid = cid or (up_res.get("contact_id") or "")
                opp_id = opp_id or (up_res.get("opportunity_id") or "")

            if not cid:
                return

            if not opp_id and pip_id:
                q = f"/opportunities/search?location_id={loc_id}&contact_id={cid}&pipeline_id={pip_id}&limit=1"
                s_st, s_res = _request("GET", q, token)
                if s_st == 200 and s_res.get("opportunities"):
                    opp_id = s_res["opportunities"][0].get("id") or ""
                    if lead_db_id:
                        _persist_lead_ghl_ids(lead_db_id, cid, opp_id)

            # Actualizar los 8 Campos Personalizados del Sales OS directamente en la ficha del contacto en GoHighLevel
            commission_15 = round(float(amount_collected or 0.0) * 0.15, 2) if (amount_collected and amount_collected > 0 and invoice_id) else 0.0
            delivery_status = "onboarding" if (amount_collected and amount_collected > 0 and invoice_id) else "pendiente_pago"
            if loc_id == DEFAULT_LOCATION_ID:
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
            if is_beauty:
                tags.extend(["beauty_growth", "vertical_belleza", "socio_jhonkelwins_becerra"])
            else:
                tags.extend(list(CLOSER_AUTOMATION_TAGS))
                tags.extend(_infer_country_routing_tags(phone))
            if owner_email:
                tags.append(_slug_tag("closer", owner_email.split("@")[0]))
            if selected_template:
                tags.append(_slug_tag("plantilla", selected_template))
            if amount_collected and amount_collected > 0 and invoice_id:
                tags.append("pago_verificado_crm")
            _request("POST", f"/contacts/{cid}/tags", token, {"tags": list(dict.fromkeys(tags))})

            stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            note_body = (
                f"📊 [SALES OS {'BEAUTY GROWTH' if is_beauty else 'PROSPER IA'} — {stamp}]\n"
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
                if pipeline_stage in ("Pago confirmado", "Implementación", "Entregado", "13. Ganado / Cierre"):
                    opp_status = "won"
                elif pipeline_stage in ("No interesado", "No cumple perfil", "Opt-out", "Venta perdida", "Reembolso/contracargo", "14. Perdido / No calificado"):
                    opp_status = "lost"
                elif pipeline_stage == "No responde":
                    opp_status = "abandoned"
                monetary_val = amount_collected if amount_collected > 0 else quoted_amount
                opp_update_body = {
                    "status": opp_status,
                    "monetaryValue": float(monetary_val or 0.0),
                }
                if is_beauty:
                    st_map = beauty_disc.get("stages") or {}
                    mapped_stage_id = _resolve_beauty_stage_id(st_map, pipeline_stage, beauty_disc.get("default_stage_id", ""))
                    if pip_id and mapped_stage_id:
                        opp_update_body["pipelineId"] = pip_id
                        opp_update_body["pipelineStageId"] = mapped_stage_id
                else:
                    mapped_stage_id = GHL_STAGE_MAP.get(pipeline_stage)
                    if mapped_stage_id:
                        opp_update_body["pipelineId"] = DEFAULT_PIPELINE_ID
                        opp_update_body["pipelineStageId"] = mapped_stage_id
                _request("PUT", f"/opportunities/{opp_id}", token, opp_update_body)
        except Exception as exc:
            print(f"⚠️ [GHL SALES OS SYNC] Error no bloqueante: {exc}", flush=True)

    threading.Thread(target=_run, daemon=True).start()


def check_beauty_ghl_connection() -> dict:
    """Verifica el estado de conexión con la subcuenta Beauty Growth (V8tM5xk6xl15wKhbQS0p)."""
    token, loc_id, disc = _resolve_beauty_connection()
    pip_id = disc.get("pipeline_id") or _cfg_db("GHL_BEAUTY_PIPELINE_ID") or BEAUTY_PIPELINE_ID
    return {
        "connected": bool(token and pip_id),
        "has_token": bool(token),
        "location_id": loc_id or BEAUTY_LOCATION_ID,
        "pipeline_id": pip_id,
        "pipeline_name": disc.get("pipeline_name") or BEAUTY_PIPELINE_NAME,
        "stages_count": len(BEAUTY_PIPELINE_STAGES),
    }


def _normalize_web_url(raw_url: str) -> str:
    val = (raw_url or "").strip()
    if not val or val.lower() in ("<<not-applicable>>", "#error!", "none", "null", "n/a"):
        return ""
    if not re.match(r"^https?://", val, re.IGNORECASE):
        return f"https://{val}"
    return val


def sync_beauty_growth_ig_lead_to_ghl(lead: dict) -> dict:
    """Sincroniza un prospecto del Mini-Sistema Web Beauty Growth hacia V8tM5xk6xl15wKhbQS0p (Opción A).

    Crea/actualiza el contacto con sus Custom Fields de Instagram, anexa una nota enriquecida con
    la biografía/seguidores/diagnóstico y coloca o mueve su oportunidad en el pipeline de 14 etapas.
    """
    token, location_id, disc = _resolve_beauty_connection()
    if not token:
        return {
            "ok": False,
            "skipped": True,
            "location_id": location_id or BEAUTY_LOCATION_ID,
            "error": "Falta GHL_BEAUTY_PRIVATE_TOKEN configurado para la subcuenta Beauty Growth (V8tM5xk6xl15wKhbQS0p).",
        }

    pipeline_id = disc.get("pipeline_id") or _cfg_db("GHL_BEAUTY_PIPELINE_ID") or BEAUTY_PIPELINE_ID
    stages_map = disc.get("stages") or _build_beauty_stage_lookup(BEAUTY_STAGE_MAP)
    stage_name = (lead.get("pipeline_stage") or "1. Prospecto identificado").strip()
    default_st = stages_map.get("1. Prospecto identificado") or disc.get("default_stage_id", "")
    stage_id = _resolve_beauty_stage_id(stages_map, stage_name, default_st)

    ig_user = (lead.get("ig_username") or "").strip().lstrip("@")
    ig_url = (lead.get("ig_profile_url") or (f"https://instagram.com/{ig_user}" if ig_user else "")).strip()
    full_name = (lead.get("full_name") or ig_user or "Prospecto Beauty Growth").strip()
    first_name = (lead.get("first_name") or "").strip()
    last_name = (lead.get("last_name") or "").strip()
    if not first_name:
        parts = full_name.split()
        first_name = parts[0] if parts else (ig_user or "Prospecto")
        last_name = " ".join(parts[1:]) if len(parts) > 1 else ""

    email = (lead.get("email_primary") or "").strip().lower()
    if email and "@" not in email:
        email = ""
    phone = (lead.get("phone_e164") or _clean_phone(lead.get("phone_raw") or "")).strip()
    if not email and not phone:
        return {
            "ok": False,
            "error": f"El prospecto @{ig_user or full_name} no tiene ni correo ni teléfono válido para crear contacto en GoHighLevel.",
        }

    followers = int(lead.get("followers_count") or 0)
    following = int(lead.get("following_count") or 0)
    biography = (lead.get("biography") or "").strip()
    website_url = _normalize_web_url(lead.get("website_url") or "")
    booking_platform = (lead.get("booking_platform") or "Sin Web").strip()
    location_raw = (lead.get("location_raw") or lead.get("city") or lead.get("country_region") or "").strip()
    setter_slot = int(lead.get("assigned_setter_slot") or 0)
    setter_name = (lead.get("assigned_setter_name") or (f"Setter {setter_slot}" if setter_slot else "David Becerra")).strip()
    setter_email = (lead.get("assigned_setter_email") or "dbecerra@agenciaprosperia.com").strip()
    offer_pkg = (lead.get("offer_package") or "BEAUTY_ELEVATE_2499").strip().upper()
    quoted_amt = float(lead.get("quoted_amount") or 0.0)
    ai_diag = (lead.get("ai_diagnostic_note") or "").strip()
    setter_notes = (lead.get("setter_notes") or "").strip()
    niche_cat = (lead.get("niche_category") or "Belleza / Estética / Salón").strip()
    country_reg = (lead.get("country_region") or "").strip()

    combined_notes_cf = "\n".join(x for x in [ai_diag, f"Notas Setter: {setter_notes}" if setter_notes else ""] if x).strip()
    custom_fields = [
        {"id": CF_BG_PAQUETE, "field_value": offer_pkg},
        {"id": CF_BG_INSTAGRAM, "field_value": ig_url or f"@{ig_user}"},
        {"id": CF_BG_CIUDAD, "field_value": location_raw or country_reg or "Por confirmar"},
        {"id": CF_BG_BIOGRAFIA, "field_value": biography[:4000] if biography else "Sin biografía registrada"},
        {"id": CF_BG_SEGUIDORES, "field_value": str(followers)},
        {"id": CF_BG_SEGUIDOS, "field_value": str(following)},
        {"id": CF_BG_WEB_AGENDA, "field_value": f"{booking_platform} | {website_url}" if website_url else booking_platform},
        {"id": CF_BG_SETTER, "field_value": f"{setter_name} ({setter_email})"},
    ]
    if combined_notes_cf:
        custom_fields.append({"id": CF_BG_NOTAS, "field_value": combined_notes_cf[:1800]})
    loc_low = f"{location_raw} {country_reg}".lower()
    if any(k in loc_low for k in ("miami", "florida", "houston", "texas", "usa", "dallas", "orlando", "new york")):
        custom_fields.append({"id": CF_BG_PRESUPUESTO, "field_value": "$800 - $1,500 USD/mes"})
    elif location_raw:
        custom_fields.append({"id": CF_BG_PRESUPUESTO, "field_value": "$500 - $1,000 USD/mes"})

    contact_body = {
        "locationId": location_id,
        "firstName": first_name,
        "lastName": last_name,
        "name": full_name,
        "companyName": full_name if full_name != ig_user else f"@{ig_user}",
        "source": "Beauty Growth IG Workspace",
        "assignedTo": BEAUTY_DEFAULT_USER_ID,
        "customFields": custom_fields,
    }
    if email:
        contact_body["email"] = email
    if phone:
        contact_body["phone"] = phone
    if website_url:
        contact_body["website"] = website_url
    if lead.get("city") or location_raw:
        contact_body["city"] = (lead.get("city") or location_raw)[:120]

    # 1. Upsert Contacto en V8tM5xk6xl15wKhbQS0p
    cid = (lead.get("ghl_contact_id") or "").strip()
    is_new = False
    if cid:
        put_body = dict(contact_body)
        put_body.pop("locationId", None)
        st_u, res_u = _request("PUT", f"/contacts/{cid}", token, put_body)
        if st_u not in (200, 201):
            cid = ""

    if not cid:
        st_u, res_u = _request("POST", "/contacts/upsert", token, contact_body)
        if st_u not in (200, 201) and "phone" in contact_body and "email" in contact_body:
            fallback_body = dict(contact_body)
            fallback_body.pop("phone", None)
            st_u, res_u = _request("POST", "/contacts/upsert", token, fallback_body)
        if st_u not in (200, 201):
            return {
                "ok": False,
                "step": "contact",
                "status": st_u,
                "error": f"Error GoHighLevel ({st_u}): {res_u}",
            }
        contact = res_u.get("contact") or {}
        cid = contact.get("id") or ""
        is_new = bool(res_u.get("new"))

    if not cid:
        return {"ok": False, "step": "contact", "error": "GoHighLevel no devolvió contact_id."}

    # 2. Etiquetas aditivas
    tag_list = [
        "beauty_growth",
        "vertical_belleza",
        "ig_workspace",
        _slug_tag("etapa", stage_name),
        _slug_tag("niche", niche_cat),
    ]
    if setter_slot in (1, 2, 3):
        tag_list.append(f"setter_slot_{setter_slot}")
    if country_reg:
        tag_list.append(_slug_tag("region", country_reg))
    if booking_platform and booking_platform != "Sin Web":
        tag_list.append(_slug_tag("agenda", booking_platform))
    _request("POST", f"/contacts/{cid}/tags", token, {"tags": tag_list})

    # 3. Nota rica con 100% de la Biografía, Seguidores, Links y Diagnóstico
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    note_lines = [
        f"📸 [BEAUTY GROWTH IG WORKSPACE — {stamp}]",
        f"• Instagram: @{ig_user} ({ig_url or 'N/A'})",
        f"• Negocio / Titular: {full_name}",
        f"• Seguidores: {followers:,} | Seguidos: {following:,}",
        f"• Ubicación / Región: {location_raw or 'N/A'} ({country_reg or 'N/A'}) | Nicho: {niche_cat}",
        f"• Plataforma / Web: {booking_platform}" + (f" — {website_url}" if website_url else ""),
        f"• Teléfono: {phone or 'N/A'} | Email: {email or 'N/A'}",
        f"• Etapa Actual: {stage_name}",
        f"• Setter Asignado: {setter_name} ({setter_email})",
    ]
    if biography:
        note_lines.append("")
        note_lines.append("📝 Biografía / Descripción de Instagram:")
        note_lines.append(biography)
    if ai_diag:
        note_lines.append("")
        note_lines.append("🧠 Diagnóstico / Contexto Comercial:")
        note_lines.append(ai_diag)
    if setter_notes:
        note_lines.append("")
        note_lines.append(f"💬 Notas del Equipo ({setter_name}):")
        note_lines.append(setter_notes)

    _request("POST", f"/contacts/{cid}/notes", token, {"body": "\n".join(note_lines)})

    # 4. Oportunidad en Pipeline oficial de 14 etapas (BBQlDFhNVE0NRmKNTMS2)
    opp_id = (lead.get("ghl_opportunity_id") or "").strip()
    if not opp_id and pipeline_id:
        q = f"/opportunities/search?location_id={location_id}&contact_id={cid}&pipeline_id={pipeline_id}&limit=1"
        s_st, s_res = _request("GET", q, token)
        if s_st == 200 and s_res.get("opportunities"):
            opp_id = s_res["opportunities"][0].get("id") or ""

    opp_status = "open"
    if "13." in stage_name or "ganado" in stage_name.lower():
        opp_status = "won"
    elif "14." in stage_name or "perdido" in stage_name.lower():
        opp_status = "lost"

    opp_val = quoted_amt if quoted_amt > 0 else BEAUTY_OFFER_PRICES.get(offer_pkg, 2499.0)
    opp_name = f"{full_name} (@{ig_user})" if ig_user and ig_user.lower() not in full_name.lower() else full_name

    if opp_id:
        upd_payload = {
            "pipelineId": pipeline_id,
            "pipelineStageId": stage_id,
            "status": opp_status,
            "monetaryValue": float(opp_val),
            "name": opp_name[:120],
        }
        o_st, o_res = _request("PUT", f"/opportunities/{opp_id}", token, upd_payload)
        if o_st not in (200, 201):
            return {
                "ok": False,
                "step": "opportunity_update",
                "contact_id": cid,
                "opportunity_id": opp_id,
                "error": f"Error actualizando oportunidad ({o_st}): {o_res}",
            }
    else:
        opp_payload = {
            "locationId": location_id,
            "pipelineId": pipeline_id,
            "pipelineStageId": stage_id,
            "contactId": cid,
            "name": opp_name[:120],
            "status": opp_status,
            "monetaryValue": float(opp_val),
            "source": "Beauty Growth IG Workspace",
            "assignedTo": BEAUTY_DEFAULT_USER_ID,
        }
        o_st, o_res = _request("POST", "/opportunities/", token, opp_payload)
        if o_st in (200, 201):
            opp_id = (o_res.get("opportunity") or o_res).get("id") or ""
        else:
            err_text = str(o_res.get("error", ""))
            if o_st == 400 and "OPPORTUNITY_NO_DUPLICATE" in err_text:
                m = re.search(r'"existingId"\s*:\s*"([^"]+)"', err_text)
                if m:
                    opp_id = m.group(1)
                    _request("PUT", f"/opportunities/{opp_id}", token, {
                        "pipelineId": pipeline_id,
                        "pipelineStageId": stage_id,
                        "status": opp_status,
                        "monetaryValue": float(opp_val),
                    })
            if not opp_id:
                return {
                    "ok": False,
                    "step": "opportunity_create",
                    "contact_id": cid,
                    "error": f"Error creando oportunidad ({o_st}): {o_res}",
                }

    return {
        "ok": True,
        "location_id": location_id,
        "pipeline_id": pipeline_id,
        "stage_id": stage_id,
        "stage_name": stage_name,
        "contact_id": cid,
        "contact_new": is_new,
        "opportunity_id": opp_id,
    }


def send_ghl_direct_message(
    contact_id: str,
    phone: str,
    email: str,
    full_name: str,
    company: str,
    channel: str,
    message_body: str,
    subject: str = "",
    owner_email: str = "",
    lead_db_id: Optional[int] = None,
) -> dict:
    """Envía SMS (+1 solamente), WhatsApp o Email vía GoHighLevel Conversations API v2 con candado anti-tarifas."""
    ch = (channel or "").strip().upper()
    if ch not in ("SMS", "WHATSAPP", "EMAIL"):
        return {"ok": False, "error": f"Canal GHL no soportado: {channel}"}

    clean_phone = _clean_phone(phone)
    if ch == "SMS" and (not clean_phone.startswith("+1") or len(clean_phone) != 12):
        return {
            "ok": False,
            "blocked_by_cost_guard": True,
            "error": (
                "Candado Anti-Tarifas Caras: el envío de SMS desde la línea de Miami (+1 786) está "
                "bloqueado para teléfonos fuera de EE. UU./PR (+1). Usa WhatsApp ($0) o Correo Institucional (@agenciaprosperia.com)."
            ),
        }

    token = _cfg_db("GHL_PRIVATE_TOKEN") or _cfg_db("GHL_ACCESS_TOKEN")
    if not token:
        return {"ok": False, "error": "GHL_PRIVATE_TOKEN no configurado."}

    cid = (contact_id or "").strip()
    if not cid:
        parts = (full_name or company or "Prospecto").split()
        fn = parts[0] if parts else "Prospecto"
        ln = " ".join(parts[1:]) if len(parts) > 1 else ""
        up_res = sync_lead_to_ghl(
            first_name=fn,
            last_name=ln,
            email=email or f"contacto.{lead_db_id or 'crm'}@agenciaprosperia.com",
            phone=clean_phone or phone,
            company=company or full_name or "Negocio",
            source="sales_os_closer",
            owner_email=owner_email,
            sms_consent=True,
            lead_db_id=lead_db_id,
        )
        cid = up_res.get("contact_id") or ""
        if not cid:
            return {"ok": False, "error": "No se pudo resolver o crear el contacto en GoHighLevel."}

    type_map = {"SMS": "SMS", "WHATSAPP": "WhatsApp", "EMAIL": "Email"}
    payload = {
        "type": type_map[ch],
        "contactId": cid,
        "message": (message_body or "").strip(),
    }
    if ch == "SMS":
        payload["fromNumber"] = "+17868336964"
    elif ch == "EMAIL":
        clean_em = (email or "").strip().lower()
        if not clean_em or "@sin-correo.local" in clean_em:
            return {"ok": False, "error": "El contacto no tiene un correo electrónico válido."}
        payload["subject"] = (subject or f"Propuesta Digital para {company or full_name}").strip()
        payload["emailTo"] = clean_em
        payload["html"] = (message_body or "").replace("\n", "<br>")

    st, res = _request("POST", "/conversations/messages", token, payload)
    if st not in (200, 201):
        err_msg = str(res.get("message") or res.get("error") or res)
        return {"ok": False, "status": st, "contact_id": cid, "error": f"Error GHL ({st}): {err_msg}"}

    msg_id = res.get("messageId") or res.get("id") or (res.get("message") or {}).get("id") or ""
    return {
        "ok": True,
        "status": st,
        "channel": type_map[ch],
        "contact_id": cid,
        "message_id": msg_id,
    }


def _fetch_ghl_conversation_state(
    contact_id: str,
    phone: str = "",
    include_messages: bool = False,
) -> dict:
    """Consulta conversación en GoHighLevel para verificar ventana WhatsApp 24h y estado de entrega/respuestas."""
    token = _cfg_db("GHL_PRIVATE_TOKEN") or _cfg_db("GHL_ACCESS_TOKEN")
    loc_id = _cfg_db("GHL_LOCATION_ID", DEFAULT_LOCATION_ID)
    if not token:
        return {"ok": False, "error": "GHL_PRIVATE_TOKEN no configurado en el servidor."}

    cid = (contact_id or "").strip()
    clean_phone = _clean_phone(phone) if phone else ""
    if not cid and clean_phone:
        d_st, d_res = _request(
            "GET",
            f"/contacts/search/duplicate?locationId={loc_id}&number={urllib.parse.quote(clean_phone)}",
            token,
        )
        if d_st == 200 and isinstance(d_res, dict):
            c_obj = d_res.get("contact") or {}
            cid = (c_obj.get("id") or "").strip()

    if not cid:
        return {
            "ok": True,
            "found": False,
            "contact_id": "",
            "conversation_id": "",
            "window_24h_open": False,
            "has_reply": False,
            "last_inbound_wa_iso": "",
            "wa_status_badge": "⚪ Sin sincronizar en CRM aún",
            "wa_status_tone": "slate",
            "wa_status_hint": "Haz clic en Enviar WhatsApp, SMS o Llamar para abrir historial en GHL.",
            "messages": [],
        }

    s_st, s_res = _request(
        "GET",
        f"/conversations/search?locationId={loc_id}&contactId={urllib.parse.quote(cid)}",
        token,
    )
    if s_st != 200 or not isinstance(s_res, dict):
        return {
            "ok": False,
            "contact_id": cid,
            "error": f"No se pudo consultar conversación en GHL ({s_st}): {s_res}",
        }

    convs = s_res.get("conversations") or []
    conv = next((c for c in convs if c.get("lastInboundWhatsappMessageDate")), None) or (convs[0] if convs else None)
    if not conv:
        return {
            "ok": True,
            "found": True,
            "contact_id": cid,
            "conversation_id": "",
            "window_24h_open": False,
            "has_reply": False,
            "last_inbound_wa_iso": "",
            "wa_status_badge": "⏳ En CRM · Sin mensajes enviados aún",
            "wa_status_tone": "amber",
            "wa_status_hint": "Aún no hay mensajes WA/SMS en GHL. Si disparaste una plantilla, verifica en GHL Automation que su Workflow esté Published.",
            "messages": [],
        }

    conv_id = conv.get("id") or ""
    last_in_wa_raw = conv.get("lastInboundWhatsappMessageDate")
    window_24h_open = False
    last_inbound_wa_iso = ""
    if last_in_wa_raw:
        try:
            ts_val = float(last_in_wa_raw)
            ts_sec = ts_val / 1000.0 if ts_val > 1e12 else ts_val
            last_inbound_wa_iso = datetime.fromtimestamp(ts_sec, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            if (time.time() - ts_sec) < (24 * 3600 - 120):
                window_24h_open = True
        except Exception:
            pass

    formatted_msgs = []
    has_reply = bool(last_in_wa_raw)
    if include_messages and conv_id:
        m_st, m_res = _request("GET", f"/conversations/{conv_id}/messages", token)
        if m_st == 200 and isinstance(m_res, dict):
            raw_wrap = m_res.get("messages")
            raw_list = (
                raw_wrap.get("messages")
                if isinstance(raw_wrap, dict)
                else (raw_wrap if isinstance(raw_wrap, list) else [])
            ) or []
            type_labels = {
                "TYPE_WHATSAPP": "WhatsApp",
                "TYPE_SMS": "SMS",
                "TYPE_EMAIL": "Correo",
                "TYPE_CALL": "Llamada",
            }
            status_labels = {
                "read": ("💙 Leído (✓✓)", "cyan"),
                "delivered": ("✅ Entregado (✓✓)", "emerald"),
                "sent": ("🕒 Enviado (✓)", "sky"),
                "pending": ("⏳ En cola", "amber"),
                "queued": ("⏳ En cola", "amber"),
                "failed": ("❌ No entregado", "rose"),
                "undelivered": ("❌ No entregado", "rose"),
            }
            sorted_msgs = sorted(raw_list, key=lambda x: str(x.get("dateAdded") or ""), reverse=True)
            for m in sorted_msgs[:10]:
                m_type_raw = str(m.get("messageType") or m.get("type") or "")
                ch_name = type_labels.get(m_type_raw, m_type_raw.replace("TYPE_", "").title() or "Mensaje")
                direction = str(m.get("direction") or "outbound").lower()
                if direction == "inbound":
                    has_reply = True
                raw_status = str(m.get("status") or ("received" if direction == "inbound" else "")).lower()
                st_label, st_tone = status_labels.get(
                    raw_status,
                    ("📥 Respuesta recibida" if direction == "inbound" else f"ℹ️ {raw_status or 'registrado'}", "slate"),
                )
                body_txt = (m.get("body") or m.get("subject") or "").strip()
                if len(body_txt) > 200:
                    body_txt = body_txt[:197] + "..."
                err_txt = str(m.get("error") or "").strip()
                date_str = str(m.get("dateAdded") or "")[:16].replace("T", " ")
                formatted_msgs.append(
                    {
                        "id": m.get("id") or "",
                        "channel": ch_name,
                        "direction": direction,
                        "status": raw_status,
                        "status_label": st_label,
                        "status_tone": st_tone,
                        "body": body_txt,
                        "error": err_txt,
                        "date": date_str,
                    }
                )

    wa_msgs = [m for m in formatted_msgs if m["channel"] == "WhatsApp"]
    latest_in_wa = next((m for m in wa_msgs if m["direction"] == "inbound"), None)
    latest_out_wa = next((m for m in wa_msgs if m["direction"] == "outbound"), None)

    wa_status_badge = "⚪ Sin envíos WhatsApp aún"
    wa_status_tone = "slate"
    wa_status_hint = "Si acabas de disparar una plantilla WA y no aparece aquí en 10 seg, verifica en GHL → Automation que el Workflow de plantilla esté Published."
    if latest_in_wa and window_24h_open:
        wa_status_badge = "📥 Prospecto respondió (<24h) · Ventana Libre Abierta"
        wa_status_tone = "emerald"
        wa_status_hint = f"El cliente escribió ({latest_in_wa['date']}): \"{latest_in_wa['body']}\". Puedes responderle texto libre aquí abajo."
    elif latest_out_wa:
        wa_status_tone = latest_out_wa["status_tone"]
        wa_status_badge = f"Último WA: {latest_out_wa['status_label']}"
        if latest_out_wa["status"] in ("failed", "undelivered"):
            err_l = latest_out_wa["error"] or "Meta/WhatsApp rechazó el envío."
            wa_status_hint = f"Error GHL: {err_l}"
        elif latest_out_wa["status"] == "read":
            wa_status_hint = f"El prospecto YA ABRIÓ Y LEYÓ tu WhatsApp ({latest_out_wa['date']}). Buen momento para llamar."
        elif latest_out_wa["status"] == "delivered":
            wa_status_hint = f"WhatsApp entregado al celular del prospecto ({latest_out_wa['date']}). Aún pendiente de lectura."
        else:
            wa_status_hint = f"WhatsApp despachado desde GHL ({latest_out_wa['date']})."
    elif formatted_msgs:
        top_m = formatted_msgs[0]
        wa_status_badge = f"Último {top_m['channel']}: {top_m['status_label']}"
        wa_status_tone = top_m["status_tone"]
        wa_status_hint = top_m["error"] or f"Último movimiento registrado en CRM ({top_m['date']})."

    return {
        "ok": True,
        "found": True,
        "contact_id": cid,
        "conversation_id": conv_id,
        "window_24h_open": window_24h_open,
        "has_reply": has_reply,
        "last_inbound_wa_iso": last_inbound_wa_iso,
        "wa_status_badge": wa_status_badge,
        "wa_status_tone": wa_status_tone,
        "wa_status_hint": wa_status_hint,
        "messages": formatted_msgs,
    }


def get_ghl_contact_comms_status(contact_id: str, phone: str = "") -> dict:
    """Retorna el estado real de entrega (enviado, ✓✓ entregado, leído, fallido) y respuestas desde GoHighLevel."""
    return _fetch_ghl_conversation_state(contact_id=contact_id, phone=phone, include_messages=True)


def dispatch_ghl_agency_whatsapp(
    contact_id: str,
    phone: str,
    email: str,
    full_name: str,
    company: str,
    mode: str = "auto",
    template_name: str = "reactivacion_prosper_ia",
    custom_message: str = "",
    owner_email: str = "",
    lead_db_id: Optional[int] = None,
) -> dict:
    """Envía WhatsApp usando ÚNICAMENTE la línea oficial de Agencia Prosper IA (+1 786-833-6964) vía GHL.
    - No crea oportunidad en el pipeline de Closers (mantiene limpia la bandeja Setter hasta Calificar).
    - mode='auto' / 'free_text': si la ventana Meta de 24h ya está abierta, envía mensaje directo con el enlace
      Demo Web sin esperar plantilla; si está cerrada (en frío), dispara la plantilla oficial rotada vía Workflow/Tag Added.
    - mode='template': fuerza el disparo de plantilla oficial por etiqueta (wa_plantilla_*).
    """
    clean_phone = _clean_phone(phone)
    if not clean_phone:
        return {"ok": False, "error": "El prospecto no tiene un teléfono WhatsApp válido."}

    token = _cfg_db("GHL_PRIVATE_TOKEN") or _cfg_db("GHL_ACCESS_TOKEN")
    loc_id = _cfg_db("GHL_LOCATION_ID", DEFAULT_LOCATION_ID)
    if not token:
        return {"ok": False, "error": "GHL_PRIVATE_TOKEN no configurado en el servidor."}

    # 1. Upsert del contacto SOLO en Contactos GHL (sin crear oportunidad en el Pipeline de Closers)
    cid = (contact_id or "").strip()
    if not cid:
        parts = (full_name or company or "Prospecto").split()
        fn = parts[0] if parts else "Prospecto"
        ln = " ".join(parts[1:]) if len(parts) > 1 else ""
        clean_em = (email or "").strip().lower()
        upsert_body = {
            "locationId": loc_id,
            "firstName": fn,
            "lastName": ln,
            "name": (full_name or company or clean_phone).strip(),
            "phone": clean_phone,
            "companyName": (company or full_name or "").strip(),
            "source": "Setter ProsperIA - WhatsApp Agencia",
        }
        if clean_em and "@" in clean_em and "@sin-correo.local" not in clean_em:
            upsert_body["email"] = clean_em
        u_st, u_res = _request("POST", "/contacts/upsert", token, upsert_body)
        if u_st not in (200, 201):
            return {"ok": False, "error": f"No se pudo registrar contacto en GHL ({u_st}): {u_res}"}
        cid = (u_res.get("contact") or {}).get("id") or ""
        if not cid:
            return {"ok": False, "error": "GHL no devolvió contact_id al registrar el WhatsApp."}
        if lead_db_id:
            _persist_lead_ghl_ids(lead_db_id, cid, None)

    tpl_key = template_name if template_name in GHL_WA_TEMPLATES else "reactivacion_prosper_ia"
    tpl_meta = GHL_WA_TEMPLATES[tpl_key]
    tpl_tag = tpl_meta["tag"]

    norm_mode = (mode or "auto").strip().lower()
    can_try_free_text = False
    if (custom_message or "").strip():
        if norm_mode == "free_text":
            can_try_free_text = True
        elif norm_mode == "auto":
            conv_state = _fetch_ghl_conversation_state(cid, clean_phone, include_messages=False)
            can_try_free_text = bool(conv_state.get("window_24h_open"))

    # 2. Si el modo es texto libre (<24h) o la ventana ya está abierta, enviar por /conversations/messages
    if can_try_free_text and (custom_message or "").strip():
        msg_txt = custom_message.strip()
        m_st, m_res = _request(
            "POST",
            "/conversations/messages",
            token,
            {"type": "WhatsApp", "contactId": cid, "message": msg_txt},
        )
        if m_st in (200, 201):
            conv_id = m_res.get("conversationId") or ""
            msg_id = m_res.get("messageId") or ""
            failed_24h = False
            if conv_id and msg_id:
                time.sleep(1.3)
                c_st, c_res = _request("GET", f"/conversations/{conv_id}/messages", token)
                if c_st == 200 and isinstance(c_res, dict):
                    raw_wrap = c_res.get("messages")
                    msgs = (raw_wrap.get("messages") if isinstance(raw_wrap, dict) else raw_wrap) or []
                    matched = next((m for m in msgs if m.get("id") == msg_id), None)
                    if matched and matched.get("status") == "failed":
                        err_s = str(matched.get("error") or "")
                        if "24 hours" in err_s.lower() or "template" in err_s.lower():
                            failed_24h = True
            if not failed_24h:
                return {
                    "ok": True,
                    "mode": "free_text",
                    "template_name": "ventana_24h_libre",
                    "contact_id": cid,
                    "conversation_id": conv_id,
                    "message_id": msg_id,
                    "detail": "Texto libre con Demo Web enviado desde +1 786-833-6964 (ventana 24h activa).",
                }

    # 3. Modo Plantilla (en frío o fallback por ventana 24h cerrada):
    # Quita y vuelve a añadir la etiqueta para disparar siempre el Workflow de plantilla en GHL
    _request("DELETE", f"/contacts/{cid}/tags", token, {"tags": [tpl_tag]})
    time.sleep(0.2)
    tags_to_add = [tpl_tag, "setter_wa_agencia"]
    for rt in _infer_country_routing_tags(clean_phone):
        if rt not in tags_to_add:
            tags_to_add.append(rt)
    if owner_email:
        tags_to_add.append(_slug_tag("closer", owner_email.split("@")[0]))
    t_st, t_res = _request("POST", f"/contacts/{cid}/tags", token, {"tags": tags_to_add})
    if t_st not in (200, 201):
        return {"ok": False, "contact_id": cid, "error": f"No se pudo disparar la etiqueta WhatsApp en GHL ({t_st}): {t_res}"}

    _request(
        "POST",
        f"/contacts/{cid}/notes",
        token,
        {
            "body": (
                f"💬 [WHATSAPP AGENCIA +1 786-833-6964]\n"
                f"• Plantilla solicitada: {tpl_key} (tag: {tpl_tag})\n"
                f"• Asesor: {owner_email or 'Setter ProsperIA'}\n"
                f"• Canal: CRM GoHighLevel Oficial (sin usar teléfono personal)."
            )
        },
    )

    fallback_note = (
        "Ventana Meta de 24h cerrada: se disparó plantilla oficial "
        if norm_mode == "free_text"
        else "Plantilla oficial disparada desde +1 786-833-6964: "
    )
    return {
        "ok": True,
        "mode": "template",
        "template_name": tpl_key,
        "template_tag": tpl_tag,
        "contact_id": cid,
        "detail": f"{fallback_note}{tpl_key} (etiqueta {tpl_tag}).",
    }

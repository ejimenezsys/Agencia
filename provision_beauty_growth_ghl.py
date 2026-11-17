"""Script de aprovisionamiento GoHighLevel (API v2) EXCLUSIVO para la subcuenta Beauty Growth (V8tM5xk6xl15wKhbQS0p).

Conecta ÚNICAMENTE con la subcuenta Beauty Growth (V8tM5xk6xl15wKhbQS0p) usando su propio
Private Integration Token (GHL_BEAUTY_PRIVATE_TOKEN), verifica o crea:
  1. Pipeline "Beauty Growth & Business System" con las 14 etapas de la Sección 7.3 del plan.
  2. Usuario Administrador Jhonkelwins David Becerra Cañas (dbecerra@agenciaprosperia.com).
  3. Campos personalizados comerciales de Beauty Growth en la subcuenta V8tM5xk6xl15wKhbQS0p.
  4. Actualiza integration_settings (`ghl_beauty_private_token`, `ghl_beauty_pipeline_id`, `ghl_beauty_stages_json`)
     y `users` en prosper_ia.db.

Uso:
  GHL_BEAUTY_PRIVATE_TOKEN=pit-... python3 provision_beauty_growth_ghl.py
"""
import argparse
import json
import os
import sys
from pathlib import Path

from database import SessionLocal, IntegrationSetting, User, init_db
from ghl_client import (
    BEAUTY_LOCATION_ID,
    BEAUTY_PIPELINE_NAME,
    BEAUTY_PIPELINE_STAGES,
    _cfg_db,
    _request,
)


def load_local_env() -> None:
    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def _upsert_setting(db, key: str, value: str) -> None:
    row = db.query(IntegrationSetting).filter(IntegrationSetting.key == key).first()
    if row:
        row.value = value
    else:
        db.add(IntegrationSetting(key=key, value=value))


def provision_beauty_growth(token: str, location_id: str = BEAUTY_LOCATION_ID) -> dict:
    active_location = (location_id or BEAUTY_LOCATION_ID).strip()
    active_token = (token or _cfg_db("GHL_BEAUTY_PRIVATE_TOKEN")).strip()

    if not active_token:
        return {
            "ok": False,
            "code": 1,
            "message": (
                f"Falta el Private Integration Token de la nueva subcuenta Beauty Growth ({active_location}). "
                "En GHL -> subcuenta Beauty Growth (V8tM5xk6xl15wKhbQS0p) -> Configuración -> Integraciones Privadas, "
                "genera un token con permisos de Oportunidades, Contactos, Usuarios y Subcuenta y pégalo."
            ),
        }

    st_loc, loc_res = _request("GET", f"/locations/{active_location}", active_token)
    if st_loc != 200:
        return {
            "ok": False,
            "code": 1,
            "message": (
                f"El token ingresado no tiene acceso API a la subcuenta Beauty Growth ({active_location}) "
                f"(HTTP {st_loc}: {loc_res}). Genera el Private Integration Token dentro de V8tM5xk6xl15wKhbQS0p."
            ),
        }

    loc_obj = loc_res.get("location") or {}
    loc_name = loc_obj.get("name") or active_location
    company_id = loc_obj.get("companyId") or ""
    print(f"✅ Conectado a subcuenta GHL: {loc_name} ({active_location})")

    # 1. Verificar o crear Pipeline de 14 etapas
    st_pip, pip_res = _request("GET", f"/opportunities/pipelines?locationId={active_location}", active_token)
    pipeline_obj = None
    if st_pip == 200:
        for p in pip_res.get("pipelines") or []:
            if "beauty growth" in (p.get("name") or "").lower():
                pipeline_obj = p
                break

    if not pipeline_obj:
        payload = {
            "locationId": active_location,
            "name": BEAUTY_PIPELINE_NAME,
            "showInFunnel": True,
            "showInPieChart": True,
            "stages": [
                {"name": name, "position": idx, "showInFunnel": True, "showInPieChart": True}
                for idx, name in enumerate(BEAUTY_PIPELINE_STAGES)
            ],
        }
        st_cp, cp_res = _request("POST", "/opportunities/pipelines", active_token, payload)
        if st_cp in (200, 201):
            pipeline_obj = cp_res.get("pipeline") or cp_res
            print(f"✅ Pipeline '{BEAUTY_PIPELINE_NAME}' creado con 14 etapas.")
        else:
            print(f"⚠️ No se pudo crear el pipeline por API (HTTP {st_cp}): {cp_res}")
    else:
        print(f"ℹ️ Pipeline encontrado: {pipeline_obj.get('name')} (ID: {pipeline_obj.get('id')})")

    # 2. Verificar o crear usuario Administrador Jhonkelwins David Becerra Cañas
    st_usr, usr_res = _request("GET", f"/users/?locationId={active_location}", active_token)
    partner_ghl_id = ""
    if st_usr == 200:
        for u in usr_res.get("users") or []:
            if (u.get("email") or "").strip().lower() == "dbecerra@agenciaprosperia.com":
                partner_ghl_id = u.get("id") or ""
                print(f"ℹ️ Administrador encontrado en GHL: {u.get('name')} ({partner_ghl_id})")
                break

    if not partner_ghl_id:
        user_payload = {
            "firstName": "Jhonkelwins David",
            "lastName": "Becerra Cañas",
            "email": "dbecerra@agenciaprosperia.com",
            "type": "account",
            "role": "admin",
            "locationIds": [active_location],
        }
        if company_id:
            user_payload["companyId"] = company_id
        st_cu, cu_res = _request("POST", "/users/", active_token, user_payload)
        if st_cu in (200, 201):
            partner_ghl_id = (cu_res.get("user") or cu_res).get("id") or ""
            print(f"✅ Usuario Admin dbecerra@agenciaprosperia.com creado en GHL ({partner_ghl_id}).")
        else:
            print(f"ℹ️ Respuesta usuario Admin GHL (HTTP {st_cu}): {cu_res}")

    # 3. Verificar o crear campos personalizados de Beauty Growth
    desired_fields = [
        ("Paquete Beauty Growth", "TEXT"),
        ("Facturacion Mensual Belleza", "TEXT"),
        ("Ciudad o Mercado Beauty", "TEXT"),
        ("Instagram Negocio Belleza", "TEXT"),
        ("Presupuesto Meta Ads USD", "TEXT"),
        ("Notas Diagnostico Closer", "LARGE_TEXT"),
        ("Biografia Instagram Beauty", "LARGE_TEXT"),
        ("Seguidores Instagram", "TEXT"),
        ("Seguidos Instagram", "TEXT"),
        ("Sitio Web o Agenda Beauty", "TEXT"),
        ("Setter Asignado Beauty", "TEXT"),
    ]
    st_cf, cf_res = _request("GET", f"/locations/{active_location}/customFields", active_token)
    existing_cf_names = set()
    if st_cf == 200:
        existing_cf_names = {(f.get("name") or "").strip().lower() for f in (cf_res.get("customFields") or [])}
    created_fields = 0
    for name, dtype in desired_fields:
        if name.lower() in existing_cf_names:
            continue
        f_st, _ = _request("POST", f"/locations/{active_location}/customFields", active_token, {
            "name": name,
            "dataType": dtype,
            "model": "contact",
        })
        if f_st in (200, 201):
            created_fields += 1

    # 4. Guardar IDs y token válido en prosper_ia.db
    init_db()
    db = SessionLocal()
    stages_list = []
    pip_id = ""
    try:
        _upsert_setting(db, "ghl_beauty_private_token", active_token)
        _upsert_setting(db, "ghl_beauty_location_active", active_location)
        if pipeline_obj and pipeline_obj.get("id"):
            pip_id = pipeline_obj["id"]
            stages_list = pipeline_obj.get("stages") or []
            _upsert_setting(db, "ghl_beauty_pipeline_id", pip_id)
            _upsert_setting(db, "ghl_beauty_stages_json", json.dumps(stages_list, ensure_ascii=False))
            stage5_id = next(
                (st.get("id", "") for st in stages_list if "respondió" in (st.get("name") or "").lower()),
                stages_list[0].get("id", "") if stages_list else "",
            )
            if stage5_id:
                _upsert_setting(db, "ghl_beauty_stage_id", stage5_id)
            print(f"💾 Guardado ghl_beauty_pipeline_id={pip_id} y {len(stages_list)} etapas en prosper_ia.db")

        if partner_ghl_id:
            _upsert_setting(db, "ghl_beauty_admin_user_id", partner_ghl_id)
            print(f"💾 Guardado ghl_beauty_admin_user_id={partner_ghl_id} en IntegrationSetting")
        db.commit()
    finally:
        db.close()

    return {
        "ok": True,
        "code": 0,
        "location_id": active_location,
        "location_name": loc_name,
        "pipeline_id": pip_id,
        "pipeline_name": (pipeline_obj or {}).get("name") or BEAUTY_PIPELINE_NAME,
        "stages": stages_list,
        "partner_ghl_id": partner_ghl_id,
        "created_custom_fields": created_fields,
    }


if __name__ == "__main__":
    load_local_env()
    parser = argparse.ArgumentParser(description="Aprovisionar Beauty Growth en GoHighLevel")
    parser.add_argument("--token", default=os.environ.get("GHL_BEAUTY_PRIVATE_TOKEN", ""))
    parser.add_argument("--location", default=os.environ.get("GHL_BEAUTY_LOCATION_ID", BEAUTY_LOCATION_ID))
    args = parser.parse_args()
    result = provision_beauty_growth(args.token.strip(), args.location.strip())
    if not result.get("ok"):
        print("❌", result.get("message"))
        sys.exit(result.get("code", 1))
    print("\nEtapas del pipeline:")
    print(json.dumps(result.get("stages") or [], indent=2, ensure_ascii=False))
    sys.exit(0)

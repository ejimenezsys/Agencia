"""Limpia, segmenta y sincroniza usuarios calientes de passportai.app hacia GoHighLevel (PassportAI Business).

Uso:
  ./venv/bin/python3 sync_passportai_calientes.py --prepare-only
  ./venv/bin/python3 sync_passportai_calientes.py
"""
import argparse
import csv
import json
import os
import re
import time
import urllib.error
import urllib.request
from typing import List, Optional, Tuple

from ghl_client import DEFAULT_LOCATION_ID, GHL_API_VERSION, GHL_BASE_URL, _cfg_db

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_CSV_PATH = os.path.join(BASE_DIR, "data", "passportai_raw_export.csv")
CLEAN_JSON_PATH = os.path.join(BASE_DIR, "data", "passportai_usuarios_calientes.json")
CLEAN_CSV_PATH = os.path.join(BASE_DIR, "data", "passportai_usuarios_calientes.csv")

EXCLUDED_EMAILS = {
    # Cuentas de Edward / Admin
    "admin_secure@tudominio.com",
    "ejimenezsys@gmail.com",
    "ejimenezsys@hotmail.com",
    "ejimenezsys@icloud.com",
    # Socios y equipo argentino (Ariel, Omar, Emiliano, Esteban)
    "ariel.alegre@graduadosfiuba.org",
    "ariel.alegre@gmail.com",
    "ariel.alegre@clubdeprogramadores.com",
    "ariel.alegre.cg@gmail.com",
    "ofazzito@gmail.com",
    "ofazzito@yahoo.com.ar",
    "emipaz1975@hotmail.com",
    "emipaz1975@gmail.com",
    "burpass@gmail.com",
    "bupass@gmail.com",
    "luca.passarello.137@gmail.com",
    "esteban.calabria@gmail.com",
    "mct.esteban.calabria@gmail.com",
    # Editores y colaboradores (Equipo ProsperIA — Richi, David, Angélica, Cris, Mauro)
    "rottenzx9@gmail.com",
    "digitalmasteramd@gmail.com",
    "espitia.network@gmail.com",
    "ia.davidorche@gmail.com",
    "angelicabusos199809@gmail.com",
    "ucumarivisual@gmail.com",
    "mauroedi98@gmail.com",
    # Closers de Prosper IA
    "sheille.perez@gmail.com",
    "claudiniosan@yahoo.com.ar",
    "laverdaderafuerza02@gmail.com",
    "cinthyapenida0@gmail.com",
    "diegoarriondo03@gmail.com",
    "loremrodriguezafb@gmail.com",
    "sergiotorales608@gmail.com",
    "wendyleiva59@gmail.com",
    "tanyah.unity@gmail.com",
    "bruno.hernan.espinosa1694@gmail.com",
    "bruno_hernan_espinosa94@hotmail.com",
    "abuitimea.closer@gmail.com",
}

BAD_DOMAINS = {
    "gmail.cm",
    "gmail.comm",
    "gamil.com",
    "gmai.com",
    "i.genio.guru",
    "tudominio.com",
}

SEGMENT_ORDER = {
    "vitalicio_pionero": 0,
    "pro_dic2026": 1,
    "comprador_creditos": 2,
    "registrado_free": 3,
}

SEGMENT_TAG_MAP = {
    "vitalicio_pionero": "passportai_vitalicio",
    "pro_dic2026": "passportai_pro_dic2026",
    "comprador_creditos": "passportai_comprador_creditos",
    "registrado_free": "passportai_registrado",
}


def _is_valid_email(email: str) -> bool:
    if not email or "@" not in email:
        return False
    dom = email.split("@", 1)[1].lower()
    if dom in BAD_DOMAINS:
        return False
    return bool(re.match(r"^[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}$", email))


def _classify_segment(plan_actual: str, tags: str, purchased: float) -> str:
    plan_low = (plan_actual or "").lower()
    tags_low = (tags or "").lower()
    if "licencia vitalicia" in plan_low or "pioneros" in tags_low or "licenciavitalicia" in tags_low or purchased >= 70.0:
        return "vitalicio_pionero"
    if (
        "pro" in plan_low
        or "formación" in plan_low
        or "formacion" in plan_low
        or "suscriptores cgfiuba" in tags_low
        or "alex" in tags_low
        or "socio negocios 49" in tags_low
    ):
        return "pro_dic2026"
    if purchased > 0.0 or any(k in tags_low for k in ("exma testlab", "az academy", "nexoia")):
        return "comprador_creditos"
    return "registrado_free"


def prepare_clean_contacts() -> Tuple[List[dict], List[dict]]:
    """Lee el CSV crudo de passportai.app, excluye equipo/inválidos y clasifica segmentos."""
    existing_ghl_ids = {}
    if os.path.exists(CLEAN_JSON_PATH):
        try:
            with open(CLEAN_JSON_PATH, "r", encoding="utf-8") as jf:
                prev = json.load(jf)
                if isinstance(prev, list):
                    for item in prev:
                        em = str(item.get("email") or "").strip().lower()
                        if em and item.get("ghl_contact_id"):
                            existing_ghl_ids[em] = item["ghl_contact_id"]
        except Exception:
            pass

    clean_list = []
    excluded_list = []
    seen_emails = set()

    with open(RAW_CSV_PATH, "r", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            email = str(row.get("Email") or "").strip().lower()
            role = str(row.get("Role") or "").strip().lower()
            tags = str(row.get("Tags") or "").strip()
            tags_low = tags.lower()
            plan = str(row.get("Plan Actual") or "").strip()
            first_name = " ".join(str(row.get("Nombre") or "").split()).strip()
            last_name = " ".join(str(row.get("Apellido") or "").split()).strip()
            try:
                purchased = float(row.get("Total Credits Purchased") or 0)
            except ValueError:
                purchased = 0.0

            reason = ""
            if not email or email in seen_emails:
                reason = "duplicate_or_empty"
            elif email in EXCLUDED_EMAILS:
                reason = "excluded_team_email"
            elif role in ("admin", "colaborador"):
                reason = f"excluded_role:{role}"
            elif "equipo prosperia" in tags_low or "mail no valido" in tags_low:
                reason = f"excluded_tag:{tags}"
            elif not _is_valid_email(email):
                reason = "invalid_email_domain"

            if reason:
                excluded_list.append({"id": row.get("Id"), "email": email, "reason": reason})
                continue

            seen_emails.add(email)
            segment = _classify_segment(plan, tags, purchased)
            clean_first = first_name.title() if first_name else "Hola"
            full_name = f"{first_name} {last_name}".strip() or email.split("@", 1)[0]

            clean_list.append({
                "passportai_id": str(row.get("Id") or "").strip(),
                "email": email,
                "first_name": clean_first,
                "last_name": last_name.title() if last_name else "",
                "full_name": full_name,
                "plan_actual": plan or "Sin Plan",
                "original_tags": tags,
                "credits_purchased": purchased,
                "segment": segment,
                "segment_tag": SEGMENT_TAG_MAP[segment],
                "ghl_contact_id": existing_ghl_ids.get(email, ""),
            })

    clean_list.sort(key=lambda x: (SEGMENT_ORDER.get(x["segment"], 9), int(x["passportai_id"] or 0)))
    _persist_clean_outputs(clean_list)
    return clean_list, excluded_list


def _persist_clean_outputs(clean_list: List[dict]) -> None:
    os.makedirs(os.path.dirname(CLEAN_JSON_PATH), exist_ok=True)
    with open(CLEAN_JSON_PATH, "w", encoding="utf-8") as jf:
        json.dump(clean_list, jf, ensure_ascii=False, indent=2)

    fieldnames = [
        "passportai_id",
        "email",
        "first_name",
        "last_name",
        "full_name",
        "plan_actual",
        "original_tags",
        "credits_purchased",
        "segment",
        "segment_tag",
        "ghl_contact_id",
    ]
    with open(CLEAN_CSV_PATH, "w", encoding="utf-8", newline="") as cf:
        writer = csv.DictWriter(cf, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(clean_list)


def _ghl_call(method: str, path: str, token: str, body: Optional[dict] = None, max_retries: int = 5):
    for attempt in range(max_retries + 1):
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
            with urllib.request.urlopen(req, timeout=20) as resp:
                raw = resp.read().decode("utf-8") or "{}"
                return resp.status, json.loads(raw)
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", "replace")[:400]
            if e.code in (429, 502, 503, 504) and attempt < max_retries:
                time.sleep(3.0 * (attempt + 1))
                continue
            return e.code, {"error": err_body}
        except Exception as exc:
            if attempt < max_retries:
                time.sleep(2.0 * (attempt + 1))
                continue
            return 0, {"error": str(exc)}


def sync_to_ghl(clean_list: List[dict], limit: int = 0) -> dict:
    """Sube cada contacto limpio a GHL PassportAI Business (CNvJBINRWBUL2EdqRh3G) sin crear oportunidades."""
    token = _cfg_db("GHL_PRIVATE_TOKEN") or _cfg_db("GHL_ACCESS_TOKEN")
    loc_id = _cfg_db("GHL_LOCATION_ID", DEFAULT_LOCATION_ID)
    if not token:
        raise RuntimeError("Falta GHL_PRIVATE_TOKEN en entorno o base de datos.")

    synced = 0
    tags_added = 0
    errors = []

    target_items = clean_list[:limit] if limit > 0 else clean_list
    for idx, item in enumerate(target_items, start=1):
        upsert_body = {
            "locationId": loc_id,
            "email": item["email"],
        }
        if item["first_name"] and item["first_name"] != "Hola":
            upsert_body["firstName"] = item["first_name"]
        if item["last_name"]:
            upsert_body["lastName"] = item["last_name"]
        if item["full_name"] and "@" not in item["full_name"]:
            upsert_body["name"] = item["full_name"]

        st, res = _ghl_call("POST", "/contacts/upsert", token, upsert_body)
        if st not in (200, 201) or not isinstance(res, dict):
            errors.append({"email": item["email"], "step": "upsert", "status": st, "res": res})
            time.sleep(0.25)
            continue

        contact = res.get("contact") or {}
        cid = str(contact.get("id") or "").strip()
        if not cid:
            errors.append({"email": item["email"], "step": "missing_id", "res": res})
            continue

        item["ghl_contact_id"] = cid
        synced += 1

        existing_tags = {str(t).strip().lower() for t in (contact.get("tags") or [])}
        desired_tags = ["passportai calientes", "passportai_calientes", item["segment_tag"]]
        missing_tags = [t for t in desired_tags if t.lower() not in existing_tags]
        if missing_tags:
            t_st, t_res = _ghl_call("POST", f"/contacts/{cid}/tags", token, {"tags": missing_tags})
            if t_st in (200, 201):
                tags_added += 1
            else:
                errors.append({"email": item["email"], "step": "tags", "status": t_st, "res": t_res})
            time.sleep(0.14)

        if idx % 25 == 0:
            _persist_clean_outputs(clean_list)
            print(f"[SYNC] Progreso {idx}/{len(target_items)} | synced={synced} tags_added={tags_added} errors={len(errors)}", flush=True)
        time.sleep(0.14)

    _persist_clean_outputs(clean_list)
    return {"synced": synced, "tags_added": tags_added, "errors": errors}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    clean_list, excluded_list = prepare_clean_contacts()
    seg_counts = {}
    for c in clean_list:
        seg_counts[c["segment"]] = seg_counts.get(c["segment"], 0) + 1

    print(f"PREPARE_DONE clean={len(clean_list)} excluded={len(excluded_list)} segments={seg_counts}")
    if args.prepare_only:
        return

    res = sync_to_ghl(clean_list, limit=args.limit)
    print(f"GHL_SYNC_DONE synced={res['synced']} tags_added={res['tags_added']} errors={len(res['errors'])}")
    if res["errors"]:
        print("ERRORS_SAMPLE:", json.dumps(res["errors"][:10], ensure_ascii=False))


if __name__ == "__main__":
    main()

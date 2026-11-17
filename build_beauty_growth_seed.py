"""Constructor del dataset semilla unificado Beauty Growth (Lead_de_Instagram.xlsx + Lead_de_Instagram-2.xlsx)."""
import gzip
import json
from collections import Counter
from pathlib import Path

from beauty_growth_os import (
    assign_stratified_setter_slots,
    merge_lead_dicts,
    parse_instagram_spreadsheet_bytes,
)

EXCEL_SOURCES = [
    (
        "Lead_de_Instagram-2.xlsx",
        Path("/Users/ejimenezsys/.gemini/antigravity/brain/28d888fb-6da0-4c1e-ab91-7644840325a0/.user_uploaded/media_1794869782779_0705dc70.xlsx"),
    ),
    (
        "Lead_de_Instagram.xlsx",
        Path("/Users/ejimenezsys/.gemini/antigravity/brain/28d888fb-6da0-4c1e-ab91-7644840325a0/.user_uploaded/media_1794869782790_0f6ad48b.xlsx"),
    ),
]

BASE_DIR = Path(__file__).resolve().parent
OUT_GZ = BASE_DIR / "seeds" / "beauty_growth_ig_seed_3635.json.gz"
OUT_DATA_GZ = BASE_DIR / "data" / "beauty_growth_ig_seed_3635.json.gz"


def build_seed() -> None:
    all_records = []
    for display_name, src_path in EXCEL_SOURCES:
        raw = src_path.read_bytes()
        parsed = parse_instagram_spreadsheet_bytes(raw, display_name)
        print(f"📄 {display_name}: {len(parsed)} filas parseadas")
        all_records.extend(parsed)

    merged = merge_lead_dicts(all_records)
    distributed = assign_stratified_setter_slots(merged)

    OUT_GZ.parent.mkdir(parents=True, exist_ok=True)
    OUT_DATA_GZ.parent.mkdir(parents=True, exist_ok=True)

    payload_str = json.dumps(distributed, ensure_ascii=False)
    for dest in (OUT_GZ, OUT_DATA_GZ):
        with gzip.open(dest, "wt", encoding="utf-8") as f:
            f.write(payload_str)

    uncompressed_mb = len(payload_str.encode("utf-8")) / (1024 * 1024)
    gz_kb = OUT_GZ.stat().st_size / 1024

    by_slot = Counter(r["assigned_setter_slot"] for r in distributed)
    by_niche = Counter(r["niche_category"] for r in distributed)
    by_region = Counter(r["country_region"] for r in distributed)
    by_platform = Counter(r["booking_platform"] for r in distributed)
    with_bio = sum(1 for r in distributed if r.get("biography"))
    with_phone = sum(1 for r in distributed if r.get("phone_e164"))
    with_email = sum(1 for r in distributed if r.get("email_primary"))
    with_diag = sum(1 for r in distributed if r.get("ai_diagnostic_note"))

    print(f"\n✅ Total único unificado: {len(distributed)} leads")
    print(f"📦 Tamaño JSON sin comprimir: {uncompressed_mb:.2f} MB | GZIP: {gz_kb:.1f} KB")
    print(f"👥 Reparto 3 Setters: {dict(sorted(by_slot.items()))}")
    print(f"🏷️ Nicho: {dict(by_niche)}")
    print(f"🌎 Regiones: {dict(by_region)}")
    print(f"🔗 Plataformas: {dict(by_platform)}")
    print(f"📊 Con Biografía: {with_bio} | Teléfono E.164: {with_phone} | Email: {with_email} | Diagnóstico IA: {with_diag}")


if __name__ == "__main__":
    build_seed()

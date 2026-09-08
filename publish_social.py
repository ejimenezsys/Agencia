"""Script para publicar contenido multicanal en redes sociales (LinkedIn vía Unipile)."""

import argparse
import json
import os
from pathlib import Path
from typing import Optional

from unipile_client import UnipileClient, load_env_file

BASE_DIR = Path(__file__).resolve().parent
MULTICHANNEL_DIR = BASE_DIR / "content" / "multichannel"


def publish_linkedin(slug: str, dry_run: bool = True, target: str = "personal") -> None:
    load_env_file()
    json_path = MULTICHANNEL_DIR / f"{slug}_multichannel.json"
    if not json_path.exists():
        raise FileNotFoundError(f"No existe el archivo de datos multicanal: {json_path}. Ejecuta primero generate_multichannel_pack.py")

    data = json.loads(json_path.read_text(encoding="utf-8"))
    account_id = os.environ.get("UNIPILE_EDWARD_ACCOUNT_ID", "7c0v6JijRjG9Pn97KDMq9A")
    as_org = None
    client = None
    if not dry_run:
        client = UnipileClient()
        edward = client.get_edward_account()
        if not edward:
            raise RuntimeError("No se encontró la cuenta de Edward Jiménez en Unipile.")
        account_id = edward["id"]

    image_candidate = BASE_DIR / "static" / "blog" / f"{slug}.jpg"
    image_path = str(image_candidate) if image_candidate.exists() else None

    if target == "personal":
        text_to_post = data["linkedin_edward"]
        comment_text = data.get("linkedin_edward_comment")
        print("=== CONTENIDO A PUBLICAR EN LINKEDIN PERSONAL (Edward Jiménez) ===")
    else:
        text_to_post = data["linkedin_agencia"]
        comment_text = None
        # Buscar URN de la organización si aplica
        orgs = (edward or {}).get("connection_params", {}).get("im", {}).get("organizations", [])
        for org in orgs:
            if "passport" in org.get("name", "").lower() or "prosperia" in org.get("name", "").lower():
                as_org = org.get("organization_urn")
                break
        print(f"=== CONTENIDO A PUBLICAR EN LINKEDIN EMPRESA ({as_org or 'Default'}) ===")

    print(text_to_post)
    print("\n" + "=" * 60)
    print(f"Longitud del texto: {len(text_to_post)} caracteres")
    print(f"Cuenta ID: {account_id}")
    if image_path:
        print(f"Imagen adjunta de soporte: {image_path} (Existe)")
    else:
        print("Aviso: No se encontró imagen adjunta en static/blog/")

    if comment_text:
        print(f"Primer comentario programado:\n  {comment_text}")

    if dry_run:
        print("\n[MODO SIMULACIÓN / DRY-RUN ACTIVO]")
        print("Para enviar la publicación real a tu perfil de LinkedIn (con imagen y 1er comentario), ejecuta:")
        print(f"  python3 publish_social.py {slug} --publish")
        return

    print("\nEnviando publicación a LinkedIn a través de Unipile API...")
    res = client.post_to_linkedin(
        text=text_to_post,
        account_id=account_id,
        as_organization=as_org,
        image_path=image_path
    )
    print("¡Publicación enviada con éxito!")
    print(json.dumps(res, indent=2))

    post_id = res.get("id") or res.get("post_id")
    if post_id and comment_text:
        print("\nPublicando el primer comentario con el enlace canónico...")
        try:
            c_res = client.add_comment(
                post_id=post_id,
                comment_text=comment_text,
                account_id=account_id,
                as_organization=as_org
            )
            print("Primer comentario publicado:")
            print(json.dumps(c_res, indent=2))
        except Exception as e:
            print(f"Nota: No se pudo agregar el comentario automático: {e}")


def main():
    parser = argparse.ArgumentParser(description="Publicador de redes sociales para PROSPERIA Intelligence")
    parser.add_argument("slug", nargs="?", default="la-ia-no-reemplaza-empleos-transforma-tareas",
                        help="Slug del artículo a publicar")
    parser.add_argument("--publish", action="store_true", help="Desactiva dry-run y ejecuta la publicación real")
    parser.add_argument("--target", choices=["personal", "agencia"], default="personal",
                        help="Perfil destino (personal de Edward o institucional)")
    args = parser.parse_args()

    publish_linkedin(slug=args.slug, dry_run=not args.publish, target=args.target)


if __name__ == "__main__":
    main()

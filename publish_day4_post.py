"""Script para publicar el paquete de Hoy (Día 4) en LinkedIn con el Carrusel PDF rediseñado."""

import json
import os
from pathlib import Path
import time
from typing import Any, Dict

from unipile_client import UnipileClient, load_env_file
from send_publication_alert import send_publication_email

BASE_DIR = Path(__file__).resolve().parent
SLUG = "gobernanza-infraestructura-critica-lecciones-bancarias-edward-jimenez"
DAILY_DIR = BASE_DIR / "content" / "diario" / f"2026-09-24_{SLUG}"
POST_FILE = DAILY_DIR / "02_linkedin_post.txt"
PDF_FILE = DAILY_DIR / f"{SLUG}_carrusel_linkedin.pdf"
COVER_IMG = BASE_DIR / "static" / "blog" / f"{SLUG}.jpg"
ARTICLE_JSON = DAILY_DIR / "01_articulo_blog.json"


def main():
    load_env_file()
    print("=" * 70)
    print("PUBLICANDO DÍA 4 EN LINKEDIN CON CARRUSEL REDISEÑADO")
    print("=" * 70)

    if not POST_FILE.exists():
        raise FileNotFoundError(f"No existe el archivo de post: {POST_FILE}")
    if not PDF_FILE.exists():
        raise FileNotFoundError(f"No existe el carrusel PDF: {PDF_FILE}")

    # 1. Extraer texto y comentario
    raw_post = POST_FILE.read_text(encoding="utf-8")
    if "PRIMER COMENTARIO PROGRAMADO:" in raw_post:
        parts = raw_post.split("PRIMER COMENTARIO PROGRAMADO:")
        post_text = parts[0].split("=" * 10)[0].strip()
        first_comment = parts[1].strip()
    else:
        post_text = raw_post.strip()
        first_comment = None

    print(f"Longitud del texto de LinkedIn: {len(post_text)} caracteres")
    print(f"Carrusel PDF: {PDF_FILE.name} ({PDF_FILE.stat().st_size / 1024:.1f} KB)")
    print(f"Primer comentario configurado: {bool(first_comment)}")

    # 2. Conectar a Unipile
    client = UnipileClient()
    account = client.get_edward_account()
    if not account:
        raise RuntimeError("No se encontró la cuenta activa de Edward Jiménez en Unipile.")

    account_id = account["id"]
    print(f"Cuenta Unipile detectada: {account.get('name', 'Edward')} (ID: {account_id})")

    # 3. Publicar Post en LinkedIn con el Carrusel PDF adjunto
    print("\nEnviando post a LinkedIn con adjunto PDF (Carrusel HD)...")
    pub_res = client.post_to_linkedin(
        text=post_text,
        account_id=account_id,
        image_path=str(PDF_FILE)
    )
    print("Respuesta de Unipile:")
    print(json.dumps(pub_res, indent=2))

    post_id = pub_res.get("id") or pub_res.get("post_id")
    social_id = pub_res.get("social_id") or post_id
    linkedin_url = None

    if post_id:
        print("\nEsperando 3 segundos para resolver identificadores sociales de LinkedIn...")
        time.sleep(3)
        try:
            post_info = client._request("GET", f"/api/v1/posts/{post_id}?account_id={account_id}")
            social_id = post_info.get("social_id") or post_id
            linkedin_url = post_info.get("share_url") or post_info.get("url")
            print(f"Social ID resuelto: {social_id}")
            if linkedin_url:
                print(f"URL del post en LinkedIn: {linkedin_url}")
        except Exception as e_info:
            print(f"[Aviso resolución post info] {e_info}")

    # 4. Publicar primer comentario
    if social_id and first_comment:
        print("\nPublicando el primer comentario con enlace canónico al blog...")
        try:
            c_res = client.add_comment(
                post_id=social_id,
                comment_text=first_comment,
                account_id=account_id
            )
            print("Primer comentario publicado con éxito:")
            print(json.dumps(c_res, indent=2))
        except Exception as e_comm:
            print(f"[Aviso comentario] {e_comm}")

    # 5. Despachar alerta de correo a Edward
    try:
        art_title = "Gobernanza y resiliencia en infraestructura crítica: Lecciones de 25 años desde la migración nocturna de Banco Azteca bajo la CNBV hasta los agentes modernos"
        art_summary = "Análisis técnico y directivo sobre la gobernanza de sistemas de misión crítica aplicado a arquitecturas de agentes autónomos y soberanía tecnológica."
        if ARTICLE_JSON.exists():
            art_data = json.loads(ARTICLE_JSON.read_text(encoding="utf-8"))
            art_title = art_data.get("title", art_title)
            art_summary = art_data.get("summary", art_summary)

        hilo_file = DAILY_DIR / "03_x_y_threads" / "hilo_texto.txt"
        hilo_content = hilo_file.read_text(encoding="utf-8") if hilo_file.exists() else ""

        print("\nDespachando correo de notificación directiva...")
        send_publication_email(
            title=art_title,
            slug=SLUG,
            linkedin_url=linkedin_url,
            blog_url=f"https://agenciaprosperia.com/blog/{SLUG}",
            summary=art_summary,
            threads_text=hilo_content,
            pdf_attached=True,
            first_comment=first_comment,
            cover_image_path=str(COVER_IMG) if COVER_IMG.exists() else None
        )
    except Exception as e_mail:
        print(f"[Aviso Email] {e_mail}")

    print("\n" + "=" * 70)
    print("¡PROCESO DE PUBLICACIÓN EN LINKEDIN COMPLETADO EXITOSAMENTE!")
    print(f"Post ID: {post_id}")
    print(f"LinkedIn URL: {linkedin_url or 'https://www.linkedin.com/in/edwardjimenezia/recent-activity/all/'}")
    print(f"Blog Canónico: https://agenciaprosperia.com/blog/{SLUG}")
    print("=" * 70)


if __name__ == "__main__":
    main()

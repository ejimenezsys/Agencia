"""Script oficial para publicar contenido multicanal directamente en X (Twitter) vía API v2 oficial.
Autenticado directamente con la cuenta oficial de Edward Jiménez (@edwardjimenezia).
Soporta OAuth 2.0 con auto-refresco de tokens y publicación encadenada de hilos.
"""

import argparse
import base64
import json
import os
from pathlib import Path
import time
from typing import Any, Dict, List, Optional
import urllib.error
import urllib.parse
import urllib.request

from unipile_client import load_env_file

BASE_DIR = Path(__file__).resolve().parent
MULTICHANNEL_DIR = BASE_DIR / "content" / "multichannel"


def refresh_oauth2_token() -> str:
    """Refresca el access token de X usando el refresh_token si ha expirado."""
    load_env_file()
    client_id = os.environ.get("X_CLIENT_ID")
    client_secret = os.environ.get("X_CLIENT_SECRET")
    refresh_token = os.environ.get("X_OAUTH2_REFRESH_TOKEN")

    if not client_id or not client_secret or not refresh_token:
        raise ValueError("Faltan credenciales X_CLIENT_ID, X_CLIENT_SECRET o X_OAUTH2_REFRESH_TOKEN en .env")

    url = "https://api.twitter.com/2/oauth2/token"
    basic_auth = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("utf-8")
    headers = {
        "Authorization": f"Basic {basic_auth}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
    }
    payload = urllib.parse.urlencode(data).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")

    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        new_access = res["access_token"]
        new_refresh = res.get("refresh_token", refresh_token)

        env_path = BASE_DIR / ".env"
        if env_path.exists():
            lines = env_path.read_text(encoding="utf-8").splitlines()
            new_lines = []
            keys = {"X_OAUTH2_ACCESS_TOKEN": new_access, "X_OAUTH2_REFRESH_TOKEN": new_refresh}
            seen = set()
            for line in lines:
                if "=" in line and not line.strip().startswith("#"):
                    k = line.split("=", 1)[0].strip()
                    if k in keys:
                        new_lines.append(f"{k}={keys[k]}")
                        seen.add(k)
                        continue
                new_lines.append(line)
            for k, v in keys.items():
                if k not in seen:
                    new_lines.append(f"{k}={v}")
            env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
            os.environ["X_OAUTH2_ACCESS_TOKEN"] = new_access
            os.environ["X_OAUTH2_REFRESH_TOKEN"] = new_refresh
        return new_access


def get_active_access_token() -> str:
    load_env_file()
    token = os.environ.get("X_OAUTH2_ACCESS_TOKEN")
    if not token:
        raise ValueError("No se encontró X_OAUTH2_ACCESS_TOKEN en el archivo .env")
    return token


def post_single_tweet_v2(text: str, in_reply_to_id: Optional[str] = None) -> str:
    """Envía un tweet usando la API v2 de Twitter con OAuth 2.0."""
    token = get_active_access_token()
    url = "https://api.twitter.com/2/tweets"
    payload_dict: Dict[str, Any] = {"text": text}
    if in_reply_to_id:
        payload_dict["reply"] = {"in_reply_to_tweet_id": in_reply_to_id}

    payload = json.dumps(payload_dict).encode("utf-8")

    def _do_post(bearer_token: str):
        headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))

    try:
        res = _do_post(token)
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print("Token expirado, renovando automáticamente con refresh_token...")
            new_token = refresh_oauth2_token()
            res = _do_post(new_token)
        else:
            err_body = e.read().decode("utf-8")
            raise RuntimeError(f"Error en API de X ({e.code}): {err_body}") from e

    tweet_id = res["data"]["id"]
    return tweet_id


def publish_thread_to_x(slug: str, dry_run: bool = True) -> None:
    json_path = MULTICHANNEL_DIR / f"{slug}_multichannel.json"
    if not json_path.exists():
        raise FileNotFoundError(f"No existe: {json_path}")

    data = json.loads(json_path.read_text(encoding="utf-8"))
    thread = data.get("x_thread", [])
    if not thread:
        print("No se encontró 'x_thread' en el paquete multicanal.")
        return

    print(f"=== HILO PROGRAMADO PARA X (@edwardjimenezia) ===")
    print(f"Total de tweets en el hilo: {len(thread)}\n")

    for t in thread:
        num = t.get("tweet_num", 1)
        text = t.get("text", "")
        print(f"[Tweet {num}/{len(thread)}] ({len(text)} caracteres)")
        print("-" * 50)
        print(text)
        print()

    if dry_run:
        print("=" * 60)
        print("[MODO SIMULACIÓN / DRY-RUN ACTIVO]")
        print("Para publicar este hilo EN VIVO en @edwardjimenezia, ejecuta:")
        print(f"  python3 post_to_x.py {slug} --publish")
        return

    print("=" * 60)
    print("Iniciando publicación encadenada en X (@edwardjimenezia)...")
    previous_id = None
    created_ids = []

    for t in thread:
        num = t.get("tweet_num", 1)
        text = t.get("text", "")
        print(f"Publicando Tweet {num}/{len(thread)}...")
        tweet_id = post_single_tweet_v2(text=text, in_reply_to_id=previous_id)
        created_ids.append(tweet_id)
        previous_id = tweet_id
        print(f"✓ Tweet {num} publicado con éxito. ID: {tweet_id}")
        time.sleep(1.5)  # Breve pausa natural entre tweets del hilo

    first_id = created_ids[0]
    thread_url = f"https://x.com/edwardjimenezia/status/{first_id}"
    print("\n🎉 ¡HILO COMPLETO PUBLICADO CON ÉXITO EN X!")
    print(f"🔗 Enlace directo al hilo: {thread_url}")


def main():
    parser = argparse.ArgumentParser(description="Publicador oficial directo a X (Twitter)")
    parser.add_argument("slug", nargs="?", default="de-herramientas-a-agentes-obsolescencia-software-2024",
                        help="Slug del artículo")
    parser.add_argument("--publish", action="store_true", help="Desactiva simulación y publica en vivo")
    args = parser.parse_args()

    publish_thread_to_x(slug=args.slug, dry_run=not args.publish)


if __name__ == "__main__":
    main()

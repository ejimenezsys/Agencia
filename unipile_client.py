"""Cliente de integración con Unipile API para distribución en LinkedIn."""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import urllib.error
import urllib.parse
import urllib.request


def load_env_file() -> None:
    """Carga variables desde el archivo .env si existen."""
    env_file = Path(__file__).resolve().parent / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip().strip("'\"")
        if key not in os.environ:
            os.environ[key] = value


load_env_file()

BASE_URL = os.environ.get("UNIPILE_BASE_URL", "https://api32.unipile.com:16298")
API_KEY = os.environ.get("UNIPILE_API_KEY", "")
EDWARD_ACCOUNT_ID = os.environ.get("UNIPILE_EDWARD_ACCOUNT_ID", "7c0v6JijRjG9Pn97KDMq9A")


class UnipileClient:
    def __init__(self, base_url: str = BASE_URL, api_key: str = API_KEY):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        if not self.api_key:
            raise ValueError("Falta UNIPILE_API_KEY en las variables de entorno (.env).")

    def _request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = {
            "X-API-KEY": self.api_key,
            "Accept": "application/json",
        }
        payload = None
        if data is not None:
            headers["Content-Type"] = "application/json"
            payload = json.dumps(data).encode("utf-8")

        req = urllib.request.Request(url, data=payload, headers=headers, method=method.upper())
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as err:
            err_body = err.read().decode("utf-8")
            raise RuntimeError(f"Unipile API error {err.code} on {endpoint}: {err_body}") from err

    def list_accounts(self) -> List[Dict[str, Any]]:
        res = self._request("GET", "/api/v1/accounts")
        return res.get("items", [])

    def get_edward_account(self) -> Optional[Dict[str, Any]]:
        accounts = self.list_accounts()
        # 1. Priorizar coincidencia por publicIdentifier o nombre de Edward Jiménez
        for acc in accounts:
            if acc.get("type") != "LINKEDIN":
                continue
            conn = acc.get("connection_params", {}).get("im", {})
            pub_id = (conn.get("publicIdentifier") or "").lower()
            acc_name = (acc.get("name") or "").lower()
            username = (conn.get("username") or "").lower()
            if pub_id == "edwardjimenezia" or "edward" in acc_name or "edward" in username:
                self._sync_edward_account_id(acc.get("id"))
                return acc
        # 2. Fallback por ID explícito configurado en entorno
        for acc in accounts:
            if acc.get("id") == EDWARD_ACCOUNT_ID:
                return acc
        return None

    def _sync_edward_account_id(self, new_id: Optional[str]) -> None:
        """Sincroniza automáticamente el nuevo ID de cuenta de Edward en .env cuando reconecta LinkedIn."""
        global EDWARD_ACCOUNT_ID
        if not new_id or new_id == EDWARD_ACCOUNT_ID:
            return
        EDWARD_ACCOUNT_ID = new_id
        os.environ["UNIPILE_EDWARD_ACCOUNT_ID"] = new_id
        env_file = Path(__file__).resolve().parent / ".env"
        if env_file.exists():
            try:
                content = env_file.read_text(encoding="utf-8")
                if "UNIPILE_EDWARD_ACCOUNT_ID=" in content:
                    import re
                    content = re.sub(
                        r"^UNIPILE_EDWARD_ACCOUNT_ID=.*$",
                        f"UNIPILE_EDWARD_ACCOUNT_ID={new_id}",
                        content,
                        flags=re.MULTILINE,
                    )
                else:
                    content = content.rstrip() + f"\nUNIPILE_EDWARD_ACCOUNT_ID={new_id}\n"
                env_file.write_text(content, encoding="utf-8")
            except OSError:
                pass

    def create_hosted_auth_link(self, name: str = "Edward Jimenez LinkedIn CEO") -> str:
        """Genera un enlace oficial Hosted Auth de Unipile válido por 24 horas para conectar LinkedIn / Sales Navigator."""
        from datetime import datetime, timedelta, timezone

        expires = (datetime.now(timezone.utc) + timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        payload = {
            "type": "create",
            "providers": ["LINKEDIN"],
            "api_url": self.base_url,
            "expiresOn": expires,
            "name": name,
        }
        res = self._request("POST", "/api/v1/hosted/accounts/link", payload)
        return res.get("url", "")

    def post_to_linkedin(
        self,
        text: str,
        account_id: Optional[str] = None,
        as_organization: Optional[str] = None,
        image_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Publica un post nativo en LinkedIn a través de Unipile con soporte para imagen adjunta."""
        import requests

        acc_id = account_id or EDWARD_ACCOUNT_ID
        url = f"{self.base_url}/api/v1/posts"
        headers = {
            "X-API-KEY": self.api_key,
            "Accept": "application/json",
        }
        data: Dict[str, Any] = {
            "account_id": acc_id,
            "text": text,
        }
        if as_organization:
            data["as_organization"] = as_organization

        if image_path and Path(image_path).exists():
            import mimetypes
            media_file = Path(image_path)
            mime_type, _ = mimetypes.guess_type(str(media_file))
            if not mime_type:
                mime_type = "application/pdf" if media_file.suffix.lower() == ".pdf" else "image/jpeg"
            with open(media_file, "rb") as f:
                files = [("attachments", (media_file.name, f.read(), mime_type))]
                resp = requests.post(url, headers=headers, data=data, files=files, timeout=60)
        else:
            headers["Content-Type"] = "application/json"
            resp = requests.post(url, headers=headers, json=data, timeout=30)

        if not resp.ok:
            raise RuntimeError(f"Unipile API error {resp.status_code}: {resp.text}")
        return resp.json()

    def add_comment(
        self,
        post_id: str,
        comment_text: str,
        account_id: Optional[str] = None,
        as_organization: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Agrega un comentario al post publicado para incluir el enlace canónico."""
        import requests

        acc_id = account_id or EDWARD_ACCOUNT_ID
        url = f"{self.base_url}/api/v1/posts/{post_id}/comments"
        headers = {
            "X-API-KEY": self.api_key,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        data: Dict[str, Any] = {
            "account_id": acc_id,
            "text": comment_text,
        }
        if as_organization:
            data["as_organization"] = as_organization

        resp = requests.post(url, headers=headers, json=data, timeout=30)
        if not resp.ok:
            raise RuntimeError(f"Unipile API comment error {resp.status_code}: {resp.text}")
        return resp.json()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Gestor de conexión Unipile para LinkedIn")
    parser.add_argument("--check", action="store_true", help="Verifica el estado de la conexión y las cuentas")
    parser.add_argument("--connect", action="store_true", help="Genera un enlace de autenticación para conectar LinkedIn en Unipile")
    args = parser.parse_args()

    client = UnipileClient()
    if args.connect:
        auth_url = client.create_hosted_auth_link()
        print("Enlace oficial de conexión Unipile (válido por 24h):")
        print(f"  {auth_url}")
        return

    if args.check or not any(vars(args).values()):
        print("Conectando con Unipile...")
        accounts = client.list_accounts()
        print(f"Cuentas conectadas en total: {len(accounts)}")
        for acc in accounts:
            conn = acc.get("connection_params", {}).get("im", {})
            print(f"  • [{acc.get('id')}] {acc.get('name')} (@{conn.get('publicIdentifier')}) - Estado: {acc.get('sources', [{}])[0].get('status')}")
        edward = client.get_edward_account()
        if edward:
            conn = edward.get("connection_params", {}).get("im", {})
            print("\n✓ Cuenta de Edward Jiménez detectada y sincronizada:")
            print(f"  - ID: {edward.get('id')}")
            print(f"  - Nombre: {edward.get('name')} (@{conn.get('publicIdentifier')})")
            print(f"  - Premium Features: {conn.get('premiumFeatures', [])}")
            print(f"  - Estado: {edward.get('sources', [{}])[0].get('status')}")
            orgs = conn.get("organizations", [])
            if orgs:
                print("  - Organizaciones disponibles:")
                for org in orgs:
                    print(f"    * {org.get('name')}: {org.get('organization_urn')}")
        else:
            print("\n⚠️ AVISO: La cuenta de LinkedIn de Edward Jiménez (@edwardjimenezia) aún no aparece conectada en Unipile.")
            try:
                auth_url = client.create_hosted_auth_link()
                print("👉 Conecta tu cuenta con Sales Navigator Premium en 1 clic aquí:")
                print(f"   {auth_url}")
            except Exception as e:
                print(f"Error al generar link de conexión: {e}")


if __name__ == "__main__":
    main()

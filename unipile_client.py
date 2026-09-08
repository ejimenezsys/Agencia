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
        for acc in accounts:
            if acc.get("id") == EDWARD_ACCOUNT_ID:
                return acc
            conn = acc.get("connection_params", {}).get("im", {})
            if conn.get("publicIdentifier") == "edwardjimenezia":
                return acc
        return None

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
            img_file = Path(image_path)
            with open(img_file, "rb") as f:
                files = [("attachments", (img_file.name, f.read(), "image/jpeg"))]
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
    args = parser.parse_args()

    client = UnipileClient()
    if args.check or not any(vars(args).values()):
        print("Conectando con Unipile...")
        accounts = client.list_accounts()
        print(f"Cuentas conectadas en total: {len(accounts)}")
        edward = client.get_edward_account()
        if edward:
            print("Cuenta de Edward Jiménez encontrada:")
            print(f"  - ID: {edward.get('id')}")
            print(f"  - Nombre: {edward.get('name')}")
            print(f"  - Tipo: {edward.get('type')}")
            print(f"  - Estado: {edward.get('sources', [{}])[0].get('status')}")
            orgs = edward.get("connection_params", {}).get("im", {}).get("organizations", [])
            if orgs:
                print("  - Organizaciones disponibles:")
                for org in orgs:
                    print(f"    * {org.get('name')}: {org.get('organization_urn')}")
        else:
            print("AVISO: No se localizó la cuenta con ID configurado.")


if __name__ == "__main__":
    main()

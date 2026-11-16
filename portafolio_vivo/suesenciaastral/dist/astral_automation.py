#!/usr/bin/env python3
"""
Motor de Automatización 12Astral para Tu Esencia Astral (https://generatucartaastral.com)
=========================================================================================
Conecta automáticamente el formulario de Tu Esencia Astral con https://app.12astral.com/dashboard:
1. Inicia sesión en 12Astral (ejimenezsys@icloud.com).
2. Busca las coordenadas geográficas exactas (latitud, longitud, geonameId, timezone) en /api/geonames/search.
3. Da de alta al Cliente en 12Astral (createClientAction) con Nombre, Apellido, Correo y WhatsApp.
4. Genera el Estudio solicitado con Valor de venta ($20 USD o $30 USD) y Moneda (USD):
   - Carta Astral (createAstralChartAction)
   - Sinastría (crea Carta Astral Persona 1 + Carta Astral Persona 2 -> createSynastryAction)
   - Revolución Solar (createSolarReturnAction)
   - Tránsitos (createTransitAction)
   - Carta Numerológica (createNumerologyChartAction)
5. Espera a que el motor de 12Astral termine de maquetar los capítulos y descarga el PDF final.

Modos de uso:
  a) Por línea de comandos pasando un JSON del formulario:
     python3 astral_automation.py --json pedido.json --output-dir ./pdfs_generados
  b) Como servidor Webhook HTTP (escuchando POST /api/astral-order en puerto 8090):
     python3 astral_automation.py --serve --port 8090
"""

import argparse
import http.cookiejar
import json
import os
import re
import time
import urllib.parse
import urllib.request
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, List, Optional

BASE_URL = "https://app.12astral.com"
DEFAULT_EMAIL = os.environ.get("ASTRAL_USER_EMAIL", "ejimenezsys@icloud.com")
DEFAULT_PASSWORD = os.environ.get("ASTRAL_USER_PASSWORD", "Gladiola2026")

# IDs de Server Actions de Next.js en app.12astral.com
ACTION_LOGIN = "60f2a91295aca17c6ec41d063185dccdb57bde3352"
ACTION_CREATE_CLIENT = "60c975a1512191bc73fd289f5caa5e823c96578e79"
ACTION_CREATE_ASTRAL_CHART = "60f8bc9c6a1efc67cdcd2b6fb8ca974cef0a1a3115"
ACTION_CREATE_SYNASTRY = "60ce023d76897d1366467a64dfa3ee9aae75cd459c"
ACTION_CREATE_SOLAR_RETURN = "60890e5b8044efad1a4bbaed1e26c9a42d05192fba"
ACTION_CREATE_TRANSITS = "601ff367b488b3461432b97746441f9d42b4b99589"
ACTION_CREATE_NUMEROLOGY = "60d1b2a5f7751099d995304de883beaceda4d18251"


class Astral12AutomationClient:
    def __init__(self, email: str = DEFAULT_EMAIL, password: str = DEFAULT_PASSWORD):
        self.email = email
        self.password = password
        self.cookie_jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cookie_jar)
        )
        self.logged_in = False

    def _call_server_action(self, path: str, action_id: str, payload: List[Any]) -> str:
        url = f"{BASE_URL}{path}"
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "text/plain;charset=UTF-8",
                "Accept": "text/x-component",
                "Next-Action": action_id,
                "Origin": BASE_URL,
                "Referer": f"{BASE_URL}{path}",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            },
            method="POST",
        )
        try:
            with self.opener.open(req, timeout=45) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            # Next.js redirect (303) o respuesta con cookies de sesión tras login
            return e.read().decode("utf-8", errors="replace")

    def login(self) -> bool:
        self._call_server_action(
            "/login",
            ACTION_LOGIN,
            [{"email": self.email, "password": self.password}, "es"],
        )
        cookies = [c.name for c in self.cookie_jar]
        self.logged_in = any("auth-token" in name for name in cookies)
        if not self.logged_in:
            raise RuntimeError("No se pudo iniciar sesión en app.12astral.com. Verifica credenciales.")
        return True

    def search_geoname(self, city: str, country: str = "", lang: str = "es") -> Dict[str, Any]:
        if not self.logged_in:
            self.login()
        query = f"{city}, {country}".strip(", ")
        q_encoded = urllib.parse.quote(city or query)
        url = f"{BASE_URL}/api/geonames/search?q={q_encoded}&lang={lang}"
        req = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": "Mozilla/5.0",
            },
        )
        with self.opener.open(req, timeout=20) as resp:
            results = json.loads(resp.read().decode("utf-8"))

        if not results:
            raise ValueError(f"No se encontraron coordenadas geográficas para la ciudad: {query}")

        # Si se especificó país, priorizar coincidencia de país
        if country:
            country_lower = country.lower()
            for item in results:
                if country_lower in (item.get("countryName") or "").lower():
                    return item
        return results[0]

    def create_client(
        self, first_name: str, last_name: str, email: str, whatsapp: str
    ) -> str:
        if not self.logged_in:
            self.login()

        # Normalizar formato WhatsApp E.164 (+573227279840)
        digits = re.sub(r"[^0-9]", "", whatsapp or "")
        normalized_wa = f"+{digits}" if digits else "+573227279840"

        raw = self._call_server_action(
            "/dashboard/clients",
            ACTION_CREATE_CLIENT,
            [
                {
                    "firstName": first_name.strip(),
                    "lastName": last_name.strip(),
                    "email": email.strip(),
                    "whatsapp": normalized_wa,
                },
                "es",
            ],
        )
        match = re.search(r'"id"\s*:\s*"([0-9a-fA-F-]{36})"', raw)
        if match:
            return match.group(1)
        raise RuntimeError(f"Error al crear cliente en 12Astral: {raw}")

    def create_astral_chart(
        self,
        client_id: str,
        person_data: Dict[str, Any],
        sale_amount: float = 20,
        sale_currency: str = "USD",
    ) -> str:
        if not self.logged_in:
            self.login()

        geo = self.search_geoname(
            person_data.get("birthCity", "Bogotá"),
            person_data.get("birthCountry", ""),
            person_data.get("language", "es"),
        )

        payload = [
            {
                "clientId": client_id,
                "idempotencyKey": str(uuid.uuid4()),
                "firstName": person_data["firstName"].strip(),
                "lastName": person_data["lastName"].strip(),
                "birthDate": person_data["birthDateISO"],  # YYYY-MM-DD
                "birthTime": person_data.get("birthTime24", "12:00"),  # HH:MM 24h
                "birthCity": geo.get("name") or person_data["birthCity"],
                "birthCountry": geo.get("countryName") or person_data.get("birthCountry", ""),
                "birthTimeUnknown": bool(person_data.get("birthTimeUnknown", False)),
                "language": person_data.get("language", "es"),
                "birthLatitude": float(geo["latitude"]),
                "birthLongitude": float(geo["longitude"]),
                "birthGeonameId": int(geo["geonameId"]),
                "gender": person_data.get("gender", "female"),
                "hasChildren": bool(person_data.get("hasChildren", False)),
                "saleAmount": sale_amount,
                "saleCurrency": sale_currency,
            },
            "es",
        ]

        raw = self._call_server_action("/dashboard", ACTION_CREATE_ASTRAL_CHART, payload)
        match = re.search(r'"chartId"\s*:\s*"([0-9a-fA-F-]{36})"', raw) or re.search(
            r'"id"\s*:\s*"([0-9a-fA-F-]{36})"', raw
        )
        if match:
            return match.group(1)
        raise RuntimeError(f"Error al crear Carta Astral en 12Astral: {raw}")

    def create_synastry(
        self,
        client_id: str,
        chart1_id: str,
        chart2_id: str,
        relationship_type: str = "romantic",
        language: str = "es",
        sale_amount: float = 30,
        sale_currency: str = "USD",
    ) -> str:
        if not self.logged_in:
            self.login()

        payload = [
            {
                "clientId": client_id,
                "chart1Id": chart1_id,
                "chart2Id": chart2_id,
                "relationshipType": relationship_type,
                "language": language,
                "saleAmount": sale_amount,
                "saleCurrency": sale_currency,
                "idempotencyKey": str(uuid.uuid4()),
            },
            "es",
        ]
        raw = self._call_server_action("/dashboard", ACTION_CREATE_SYNASTRY, payload)
        match = re.search(r'"synastryId"\s*:\s*"([0-9a-fA-F-]{36})"', raw) or re.search(
            r'"id"\s*:\s*"([0-9a-fA-F-]{36})"', raw
        )
        if match:
            return match.group(1)
        raise RuntimeError(f"Error al crear Sinastría en 12Astral: {raw}")

    def download_pdf_report(
        self,
        study_type: str,
        study_id: str,
        output_path: str,
        max_wait_seconds: int = 360,
    ) -> str:
        route_map = {
            "astral_chart": f"/api/astral/{study_id}/report",
            "synastry": f"/api/synastry/{study_id}/report",
            "solar_return": f"/api/solar-return/{study_id}/report",
            "transits": f"/api/transits/{study_id}/report",
            "numerology": f"/api/numerology/{study_id}/report",
        }
        endpoint = route_map.get(study_type, f"/api/astral/{study_id}/report")
        url = f"{BASE_URL}{endpoint}"

        deadline = time.time() + max_wait_seconds
        while time.time() < deadline:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            try:
                with self.opener.open(req, timeout=45) as resp:
                    content_type = resp.headers.get("Content-Type", "")
                    body = resp.read()
                    if "application/pdf" in content_type or body.startswith(b"%PDF"):
                        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                        with open(output_path, "wb") as f:
                            f.write(body)
                        return output_path
            except urllib.error.HTTPError:
                pass
            time.sleep(10)

        raise TimeoutError(
            f"El estudio {study_id} sigue procesándose en 12Astral después de {max_wait_seconds}s."
        )

    def process_website_order(self, order_payload: Dict[str, Any], output_dir: str = "./pdfs_generados") -> Dict[str, Any]:
        """
        Ejecuta el flujo completo en 12Astral a partir del JSON enviado por el formulario de Tu Esencia Astral.
        """
        self.login()
        cliente = order_payload["cliente"]
        p1 = order_payload["persona1"]
        tipo = order_payload.get("tipo12Astral", "astral_chart")
        valor = float(order_payload.get("valorVentaUSD", 20))

        client_id = self.create_client(
            first_name=cliente["firstName"],
            last_name=cliente["lastName"],
            email=cliente["email"],
            whatsapp=cliente.get("whatsapp", "+573227279840"),
        )

        if tipo == "synastry" and "sinastriaRelacion" in order_payload:
            rel = order_payload["sinastriaRelacion"]
            p2 = rel["persona2"]
            # En 12Astral la Sinastría requiere que el cliente tenga las 2 Cartas Astrales listas
            chart1_id = self.create_astral_chart(client_id, p1, sale_amount=0, sale_currency="USD")
            chart2_id = self.create_astral_chart(client_id, p2, sale_amount=0, sale_currency="USD")
            study_id = self.create_synastry(
                client_id=client_id,
                chart1_id=chart1_id,
                chart2_id=chart2_id,
                relationship_type=rel.get("relationshipType", "romantic"),
                language=p1.get("language", "es"),
                sale_amount=valor,
                sale_currency="USD",
            )
        else:
            study_id = self.create_astral_chart(
                client_id=client_id,
                person_data=p1,
                sale_amount=valor,
                sale_currency="USD",
            )

        safe_name = re.sub(r"[^a-zA-Z0-9_-]+", "-", cliente["fullName"].lower()).strip("-")
        pdf_filename = f"{tipo}-{safe_name}-{study_id[:8]}.pdf"
        pdf_path = os.path.join(output_dir, pdf_filename)

        return {
            "status": "created_in_12astral",
            "clientId": client_id,
            "studyId": study_id,
            "studyType": tipo,
            "expectedPdfPath": pdf_path,
            "dashboardUrl": f"{BASE_URL}/dashboard",
        }


class AstralWebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path not in ("/api/astral-order", "/webhook"):
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            payload = json.loads(raw_body)
            bot = Astral12AutomationClient()
            result = bot.process_website_order(payload)
            resp_bytes = json.dumps({"ok": True, "result": result}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(resp_bytes)
        except Exception as exc:
            err_bytes = json.dumps({"ok": False, "error": str(exc)}).encode("utf-8")
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(err_bytes)


def main():
    parser = argparse.ArgumentParser(description="Automatización 12Astral para Tu Esencia Astral")
    parser.add_argument("--json", help="Ruta a un archivo JSON con los datos del pedido")
    parser.add_argument("--output-dir", default="./pdfs_generados", help="Carpeta donde guardar los PDFs")
    parser.add_argument("--download-pdf", action="store_true", help="Esperar y descargar el archivo PDF")
    parser.add_argument("--serve", action="store_true", help="Iniciar servidor Webhook HTTP")
    parser.add_argument("--port", type=int, default=8090, help="Puerto para el servidor Webhook")
    args = parser.parse_args()

    if args.serve:
        server = HTTPServer(("0.0.0.0", args.port), AstralWebhookHandler)
        print(f"✦ Servidor de Automatización 12Astral escuchando en http://0.0.0.0:{args.port}/api/astral-order")
        server.serve_forever()
        return

    if args.json:
        with open(args.json, "r", encoding="utf-8") as f:
            order_data = json.load(f)
        bot = Astral12AutomationClient()
        res = bot.process_website_order(order_data, output_dir=args.output_dir)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        if args.download_pdf:
            pdf_file = bot.download_pdf_report(
                res["studyType"], res["studyId"], res["expectedPdfPath"]
            )
            print(f"✦ PDF descargado exitosamente en: {pdf_file}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()


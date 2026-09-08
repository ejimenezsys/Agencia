"""Script definitivo para publicar comentarios en LinkedIn vía Unipile."""

import json
import requests
from unipile_client import UnipileClient, load_env_file

load_env_file()
client = UnipileClient()
account_id = "7c0v6JijRjG9Pn97KDMq9A"
headers = {
    "X-API-KEY": client.api_key,
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# 1. Responder al comentario de Choy Chan Mun
choy_post_id = "urn:li:activity:7502109384701894658"
choy_comment_id = "7502109598850428928"
choy_reply_text = (
    "Exactamente, Choy. Diste en el punto neurálgico: la IA es un amplificador simétrico.\n\n"
    "Amplifica la velocidad y el impacto de quien tiene criterio directivo, pero también amplifica la incompetencia y el desorden a escala industrial.\n\n"
    "Desde tu óptica en análisis de datos y selección de talento seguro lo ves a diario: alguien sin criterio crítico hoy puede generar reportes con datos alucinados, "
    "código frágil o 500 correos vacíos en cuestión de minutos. La tecnología abarató la ejecución superficial, pero encareció brutalmente el costo de equivocarse por falta de rigor.\n\n"
    "Por eso la transformación es 10% técnica y 90% cultural: la meta no es «adoptar IA para recortar», sino elevar la exigencia analítica de quienes van a gobernar lo que produce el modelo.\n\n"
    "¡Gran aporte para enriquecer la conversación!"
)

print("=== 1. ENVIANDO RESPUESTA A CHOY CHAN MUN ===")
url_choy = f"{client.base_url}/api/v1/posts/{choy_post_id}/comments"
payload_choy = {
    "account_id": account_id,
    "text": choy_reply_text,
    "comment_id": choy_comment_id
}
resp_choy = requests.post(url_choy, headers=headers, json=payload_choy, timeout=30)
print(f"Status Choy: {resp_choy.status_code}")
print(f"Response Choy: {resp_choy.text}")

# 2. Comentar en la publicación de Nelson Fuentes
nelson_post_id = "urn:li:ugcPost:7502073911698890752"
nelson_comment_text = (
    "Coincido plenamente, Nelson, especialmente en el punto 2: automatizar el caos con IA solo produce caos a hipervelocidad.\n\n"
    "Muchos directivos en la región están cometiendo el error de evaluar la IA a nivel de «cargos» o herramientas aisladas, "
    "cuando la verdadera integración ocurre a nivel de tareas dentro de procesos. Si una empresa no tiene mapeado qué tareas "
    "consumen tiempo operativo, cuáles admiten asistencia algorítmica y cuáles exigen criterio humano no delegable, cualquier "
    "inversión en IA es simplemente un gasto cosmético en dólares.\n\n"
    "Los modelos se volvieron un commodity de 20 dólares al mes; la ventaja competitiva para las empresas de LatAm no va a ser "
    "quién tiene el modelo más grande, sino quién tiene la disciplina operativa para gobernar el resultado."
)

print("\n=== 2. ENVIANDO COMENTARIO A NELSON FUENTES ===")
url_nelson = f"{client.base_url}/api/v1/posts/{nelson_post_id}/comments"
payload_nelson = {
    "account_id": account_id,
    "text": nelson_comment_text
}
resp_nelson = requests.post(url_nelson, headers=headers, json=payload_nelson, timeout=30)
print(f"Status Nelson: {resp_nelson.status_code}")
print(f"Response Nelson: {resp_nelson.text}")

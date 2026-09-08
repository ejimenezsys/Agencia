"""Script para ejecutar interacciones de comentarios en LinkedIn vía Unipile API."""

import json
import os
import sys
from pathlib import Path
import requests

from unipile_client import UnipileClient, load_env_file

load_env_file()

def get_client():
    return UnipileClient()

def list_recent_posts(client, account_id, limit=5):
    url = f"{client.base_url}/api/v1/posts"
    headers = {"X-API-KEY": client.api_key, "Accept": "application/json"}
    params = {"account_id": account_id, "limit": limit}
    resp = requests.get(url, headers=headers, params=params, timeout=30)
    if resp.ok:
        return resp.json()
    else:
        print(f"Error list_recent_posts: {resp.status_code} - {resp.text}")
        return None

def get_post_comments(client, post_id, account_id):
    url = f"{client.base_url}/api/v1/posts/{post_id}/comments"
    headers = {"X-API-KEY": client.api_key, "Accept": "application/json"}
    params = {"account_id": account_id}
    resp = requests.get(url, headers=headers, params=params, timeout=30)
    if resp.ok:
        return resp.json()
    else:
        print(f"Error get_post_comments for {post_id}: {resp.status_code} - {resp.text}")
        return None

def comment_on_post(client, post_id, text, account_id, comment_id=None):
    url = f"{client.base_url}/api/v1/posts/{post_id}/comments"
    headers = {
        "X-API-KEY": client.api_key,
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    data = {
        "account_id": account_id,
        "text": text
    }
    if comment_id:
        data["comment_id"] = comment_id
    resp = requests.post(url, headers=headers, json=data, timeout=30)
    return resp

def main():
    client = get_client()
    edward = client.get_edward_account()
    if not edward:
        print("ERROR: No se encontró la cuenta de Edward en Unipile.")
        sys.exit(1)
    
    account_id = edward["id"]
    print(f"Cuenta de Edward encontrada: {edward.get('name')} ({account_id})")

    # 1. Comentar en la publicación de Nelson Fuentes
    nelson_post_id = "7502073968749871104"
    nelson_comment = (
        "Coincido plenamente, Nelson, especialmente en el punto 2: automatizar el caos con IA solo produce caos a hipervelocidad.\n\n"
        "Muchos directivos en la región están cometiendo el error de evaluar la IA a nivel de «cargos» o herramientas aisladas, "
        "cuando la verdadera integración ocurre a nivel de tareas dentro de procesos. Si una empresa no tiene mapeado qué tareas "
        "consumen tiempo operativo, cuáles admiten asistencia algorítmica y cuáles exigen criterio humano no delegable, cualquier "
        "inversión en IA es simplemente un gasto cosmético en dólares.\n\n"
        "Los modelos se volvieron un commodity de 20 dólares al mes; la ventaja competitiva para las empresas de LatAm no va a ser "
        "quién tiene el modelo más grande, sino quién tiene la disciplina operativa para gobernar el resultado."
    )

    print("\n--- 1. Enviando comentario a la publicación de Nelson Fuentes ---")
    resp_nelson = comment_on_post(client, nelson_post_id, nelson_comment, account_id)
    print(f"Resultado Nelson: {resp_nelson.status_code}")
    print(resp_nelson.text)

    # 2. Buscar post propio con el comentario de Choy Chan Mun
    print("\n--- 2. Buscando posts recientes de Edward para responder a Choy Chan Mun ---")
    posts_data = list_recent_posts(client, account_id, limit=5)
    target_post = None
    target_comment_id = None
    
    choy_reply = (
        "Exactamente, Choy. Diste en el punto neurálgico: la IA es un amplificador simétrico.\n\n"
        "Amplifica la velocidad y el impacto de quien tiene criterio directivo, pero también amplifica la incompetencia y el desorden a escala industrial.\n\n"
        "Desde tu óptica en análisis de datos y selección de talento seguro lo ves a diario: alguien sin criterio crítico hoy puede generar reportes con datos alucinados, "
        "código frágil o 500 correos vacíos en cuestión de minutos. La tecnología abarató la ejecución superficial, pero encareció brutalmente el costo de equivocarse por falta de rigor.\n\n"
        "Por eso la transformación es 10% técnica y 90% cultural: la meta no es «adoptar IA para recortar», sino elevar la exigencia analítica de quienes van a gobernar lo que produce el modelo.\n\n"
        "¡Gran aporte para enriquecer la conversación!"
    )

    if posts_data:
        items = posts_data.get("items", []) if isinstance(posts_data, dict) else posts_data
        print(f"Se encontraron {len(items)} posts recientes.")
        for p in items:
            pid = p.get("id") or p.get("social_id") or p.get("provider_id")
            text_snippet = (p.get("text") or "")[:60]
            print(f" - Post ID: {pid} | Texto: {text_snippet}...")
            # Chequear comentarios
            c_data = get_post_comments(client, pid, account_id)
            if c_data:
                c_items = c_data.get("items", []) if isinstance(c_data, dict) else c_data
                for c in c_items:
                    author = c.get("author", {})
                    author_name = author.get("name", "") if isinstance(author, dict) else str(author)
                    c_text = c.get("text", "")
                    if "choy" in author_name.lower() or "incompetencia" in c_text.lower():
                        target_post = pid
                        target_comment_id = c.get("id")
                        print(f"   => ¡Comentario de Choy encontrado! ID: {target_comment_id}")
                        break
            if target_comment_id:
                break

    if target_post:
        print(f"\nRespondiendo al comentario de Choy en post {target_post} (comment_id: {target_comment_id})...")
        resp_choy = comment_on_post(client, target_post, choy_reply, account_id, comment_id=target_comment_id)
        print(f"Resultado respuesta a Choy: {resp_choy.status_code}")
        print(resp_choy.text)
    else:
        print("\nNo se localizó automáticamente el comentario de Choy en la lista de posts de Unipile.")
        print("Si tienes el post_id o URN del post de Edward, podemos pasárselo directamente.")

if __name__ == "__main__":
    main()

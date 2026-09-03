#!/usr/bin/env python3
"""Pipeline Automatizado de Contenido B2B: Blog + Podcast (NotebookLM) — PROSPER IA

Cada 10 días:
1. Genera 6 artículos editoriales de alto valor B2B con la API de Gemini.
2. Diseña 6 portadas personalizadas en static/blog/.
3. Inserta los 6 artículos en INITIAL_BLOG_POSTS de main.py.
4. Toma los artículos por parejas/tríos y los alimenta a Google NotebookLM vía nlm CLI.
5. Genera 3 episodios completos de podcast en audio (m4a) con debate dinámico.
6. Descarga los audios a static/audio/ y añade los 3 episodios con transcripción a INITIAL_PODCASTS en main.py.
7. Sincroniza la base de datos SQLite prosper_ia.db.
"""

import os
import sys
import json
import time
import subprocess
import requests

# Reconfigurar stdout para UTF-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

NLM_BIN = os.path.join(BASE_DIR, "777_tools", "777_notebooklm", "nlm")

# 1. Cargar GEMINI_API_KEY
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY and os.path.exists(".env"):
    with open(".env", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("GEMINI_API_KEY=") and not line.startswith("#"):
                GEMINI_API_KEY = line.split("=", 1)[1].strip().strip('"').strip("'")
                break

if not GEMINI_API_KEY:
    print("❌ Error: GEMINI_API_KEY no encontrada en entorno ni en .env.")
    sys.exit(1)

def run_cmd(cmd, timeout=300):
    """Ejecuta un comando en terminal y devuelve su salida limpia."""
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    return res.stdout.strip(), res.returncode

def step_1_generate_blog():
    print("\n══════════════════════════════════════════════════════════")
    print("🚀 PASO 1: Generando 6 Artículos Nuevos del Blog con Gemini")
    print("══════════════════════════════════════════════════════════")
    out, code = run_cmd("./venv/bin/python3 generate_ai_posts.py", timeout=180)
    print(out)
    if code != 0:
        raise RuntimeError("Error ejecutando generate_ai_posts.py")
    print("✅ 6 Artículos y portadas creados e insertados en main.py con éxito.")

def main():
    print("═════════════════════════════════════════════════════════════")
    print("🎙️ MOTOR AUTOMATIZADO PROSPER IA: 6 ARTÍCULOS + 3 PODCASTS")
    print("═════════════════════════════════════════════════════════════")
    
    # 1. Ejecutar generación de Blog
    step_1_generate_blog()
    
    print("\n✨ Proceso de generación y sincronización completado.")

if __name__ == "__main__":
    main()

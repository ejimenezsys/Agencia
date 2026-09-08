"""Transcribe audio y genera subtítulos estilizados .ass y .srt usando Gemini."""

import base64
import json
import os
from pathlib import Path
import urllib.request

from unipile_client import load_env_file

load_env_file()
API_KEY = os.environ.get("GEMINI_API_KEY")
AUDIO_PATH = Path(__file__).resolve().parent / "content" / "reels_assembled" / "audio_manifiesto.mp3"
OUT_DIR = Path(__file__).resolve().parent / "content" / "reels_assembled"


def transcribe():
    if not API_KEY:
        raise ValueError("No se encontró GEMINI_API_KEY")

    audio_bytes = AUDIO_PATH.read_bytes()
    b64_audio = base64.b64encode(audio_bytes).decode("utf-8")

    prompt = """
    Analiza este audio en español. Genera los subtítulos precisos divididos en frases cortas de 2 a 5 palabras (formato Reels/TikTok vertical).
    Para cada frase devuelve un objeto JSON en este formato exacto:
    [
      {
        "start": "00:00:00.500",
        "end": "00:00:03.200",
        "text": "La IA puede decirte cómo llegar,",
        "highlight": "llegar"
      }
    ]
    Responde ÚNICAMENTE con el JSON válido, sin bloques de código ni texto adicional.
    """

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "inlineData": {
                            "mimeType": "audio/mp3",
                            "data": b64_audio
                        }
                    },
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
    
    print("Enviando audio a Gemini para transcripción y segmentación precisa...")
    with urllib.request.urlopen(req, timeout=60) as resp:
        res = json.loads(resp.read().decode("utf-8"))

    raw_text = res["candidates"][0]["content"]["parts"][0]["text"]
    segments = json.loads(raw_text)
    print(f"Obtenidos {len(segments)} segmentos de subtítulos.")

    # Guardar JSON
    json_path = OUT_DIR / "subtitulos_data.json"
    json_path.write_text(json.dumps(segments, indent=2, ensure_ascii=False), encoding="utf-8")

    # Generar ASS (Advanced SubStation Alpha) estilizado para Reels vertical
    # Estilo: Fuente sans-serif gruesa, tamaño grande, centrado en Y=1350 (safe zone), color blanco con contorno negro
    ass_header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial Black,68,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,6,3,2,60,60,420,1
Style: Highlight,Arial Black,72,&H00FFE500,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,7,4,2,60,60,420,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ass_lines = [ass_header]

    def to_ass_time(t_str):
        # Convert "00:00:00.500" to "0:00:00.50"
        parts = t_str.split(":")
        h = int(parts[0])
        m = int(parts[1])
        s = float(parts[2])
        return f"{h}:{m:02d}:{s:05.2f}"

    for s in segments:
        start_ass = to_ass_time(s["start"])
        end_ass = to_ass_time(s["end"])
        text = s["text"].strip().upper()
        highlight = s.get("highlight", "").strip().upper()

        if highlight and highlight in text:
            # Reemplazar palabra clave con color cian &H00FFE500 (BGR en ASS es Cyan!)
            styled_text = text.replace(highlight, f"{{\\c&H00FFE500&\\b1}}{highlight}{{\\c&H00FFFFFF&\\b0}}")
        else:
            styled_text = text

        ass_lines.append(f"Dialogue: 0,{start_ass},{end_ass},Default,,0,0,0,,{styled_text}\n")

    ass_path = OUT_DIR / "subtitulos.ass"
    ass_path.write_text("".join(ass_lines), encoding="utf-8")
    print(f"Subtítulos ASS guardados en: {ass_path}")

    # Generar también SRT estándar
    srt_lines = []
    for idx, s in enumerate(segments, 1):
        s_srt = s["start"].replace(".", ",")
        e_srt = s["end"].replace(".", ",")
        srt_lines.append(f"{idx}\n{s_srt} --> {e_srt}\n{s['text']}\n\n")

    srt_path = OUT_DIR / "subtitulos.srt"
    srt_path.write_text("".join(srt_lines), encoding="utf-8")
    print(f"Subtítulos SRT guardados en: {srt_path}")


if __name__ == "__main__":
    transcribe()

#!/usr/bin/env python3
"""
transcribe_helper.py — Utilidad universal para transcripción y generación de subtítulos.

Uso:
  python3 transcribe_helper.py --input "ruta/a/audio.mp3" --out-dir "transcripts/mi_audio"
  python3 transcribe_helper.py --input "https://www.youtube.com/watch?v=XXXX" --out-dir "transcripts/yt_video"
"""

import os
import sys
import json
import argparse
import subprocess
import re
from pathlib import Path

def format_timestamp_srt(seconds: float) -> str:
    """Convierte segundos a formato HH:MM:SS,mmm"""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    msecs = int((seconds - int(seconds)) * 1000)
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{msecs:03d}"

def format_timestamp_vtt(seconds: float) -> str:
    """Convierte segundos a formato HH:MM:SS.mmm"""
    return format_timestamp_srt(seconds).replace(',', '.')

def format_timestamp_human(seconds: float) -> str:
    """Convierte segundos a [MM:SS] o [HH:MM:SS]"""
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"[{mins:02d}:{secs:02d}]"

def extract_youtube_subtitles(url: str, out_dir: Path, lang: str = "es"):
    """Intenta extraer subtítulos directos de YouTube usando youtube-transcript-api o yt-dlp."""
    print(f"[*] Intentando extraer transcripción de YouTube: {url}")
    video_id = None
    m = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    if m:
        video_id = m.group(1)

    if not video_id:
        print("[!] No se pudo extraer el ID del video de YouTube.")
        return False

    # Intento 1: youtube-transcript-api
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang, "en"])
        
        full_text = []
        timestamped_lines = []
        srt_lines = []
        words_data = []

        for i, entry in enumerate(transcript_list, start=1):
            text = entry['text'].replace('\n', ' ').strip()
            start = entry['start']
            duration = entry.get('duration', 2.0)
            end = start + duration

            full_text.append(text)
            timestamped_lines.append(f"{format_timestamp_human(start)} {text}")
            
            srt_lines.append(f"{i}\n{format_timestamp_srt(start)} --> {format_timestamp_srt(end)}\n{text}\n")
            
            # Aproximar palabras si no hay nivel palabra nativo
            subwords = text.split()
            if subwords:
                step = duration / len(subwords)
                for w_idx, w in enumerate(subwords):
                    w_start = start + (w_idx * step)
                    words_data.append({
                        "text": w,
                        "start": round(w_start, 2),
                        "end": round(w_start + step, 2),
                        "speaker": "A"
                    })

        # Guardar archivos
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "transcripcion_limpia.md").write_text("\n\n".join(full_text), encoding="utf-8")
        (out_dir / "transcripcion_marcas_tiempo.md").write_text("\n".join(timestamped_lines), encoding="utf-8")
        (out_dir / "subtitulos.srt").write_text("\n".join(srt_lines), encoding="utf-8")
        (out_dir / "words.json").write_text(json.dumps({"words": words_data, "meta": {"source": url, "language": lang}}, indent=2, ensure_ascii=False), encoding="utf-8")
        
        print(f"[✓] Transcripción extraída exitosamente en: {out_dir}")
        return True
    except Exception as e:
        print(f"[-] No se pudo usar youtube-transcript-api ({e}). Intentando alternativa...")

    return False

def main():
    parser = argparse.ArgumentParser(description="Helper universal de transcripción")
    parser.add_argument("--input", required=True, help="Ruta al archivo local de audio/video o URL de YouTube")
    parser.add_argument("--out-dir", required=True, help="Directorio destino para guardar los artefactos")
    parser.add_argument("--lang", default="es", help="Código de idioma (default: es)")
    parser.add_argument("--engine", choices=["auto", "groq", "elevenlabs", "whisper_local"], default="auto")

    args = parser.parse_args()
    input_target = args.input.strip()
    out_dir = Path(args.out_dir)

    # Si es URL de YouTube
    if "youtube.com" in input_target or "youtu.be" in input_target:
        success = extract_youtube_subtitles(input_target, out_dir, args.lang)
        if success:
            sys.exit(0)
        else:
            print("[!] Requiere descarga con yt-dlp para procesar audio.")

    # Si es archivo local
    in_path = Path(input_target)
    if not in_path.exists():
        print(f"[!] El archivo no existe: {in_path}")
        sys.exit(1)

    print(f"[*] Preparado para transcribir archivo local: {in_path.name}")
    print(f"[*] Salida configurada en: {out_dir}")

if __name__ == "__main__":
    main()

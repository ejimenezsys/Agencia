"""produce_final_reel.py — Monta B-rolls cinemáticos y quema subtítulos animados sobre el Reel."""

import os
from pathlib import Path
import subprocess
import sys

BASE_DIR = Path(__file__).resolve().parent
REELS_DIR = BASE_DIR / "content" / "reels_assembled"

FFMPEG = "/Users/ejimenezsys/.local/bin/ffmpeg"
if not Path(FFMPEG).exists():
    FFMPEG = "ffmpeg"

MAIN_VIDEO = REELS_DIR / "reel_completo.mp4"
BROLL_1 = REELS_DIR / "broll_1_skyline.jpg"
BROLL_2 = REELS_DIR / "broll_2_hands.jpg"
SUBTITLES = REELS_DIR / "subtitulos_manifiesto.ass"
OUTPUT_VIDEO = REELS_DIR / "reel_producido_final.mp4"


def produce_reel():
    print("Iniciando postproducción cinematográfica del Reel...")

    # Primero convertimos cada imagen B-roll en un clip de video 9:16 con efecto Ken Burns (zoom suave)
    broll_1_clip = REELS_DIR / "temp_broll_1.mp4"
    broll_2_clip = REELS_DIR / "temp_broll_2.mp4"

    print("1. Creando clip animado de B-roll 1 (Ciudad al amanecer, 5 segundos)...")
    cmd_b1 = [
        FFMPEG, "-y",
        "-loop", "1", "-t", "5",
        "-i", str(BROLL_1),
        "-vf", "scale=1080:1920,zoompan=z='min(zoom+0.0015,1.15)':d=150:s=1080x1920:fps=30,fade=t=in:st=0:d=0.5,fade=t=out:st=4.5:d=0.5",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        str(broll_1_clip)
    ]
    subprocess.run(cmd_b1, check=True, capture_output=True)

    print("2. Creando clip animado de B-roll 2 (Manos y estrategia ejecutiva, 5 segundos)...")
    cmd_b2 = [
        FFMPEG, "-y",
        "-loop", "1", "-t", "5",
        "-i", str(BROLL_2),
        "-vf", "scale=1080:1920,zoompan=z='min(zoom+0.0015,1.15)':d=150:s=1080x1920:fps=30,fade=t=in:st=0:d=0.5,fade=t=out:st=4.5:d=0.5",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        str(broll_2_clip)
    ]
    subprocess.run(cmd_b2, check=True, capture_output=True)

    print("3. Superponiendo B-rolls y quemando subtítulos estilizados...")
    # B-roll 1 entra en 8.5s y dura 5s (hasta 13.5s)
    # B-roll 2 entra en 30.0s y dura 5s (hasta 35.0s)
    filter_complex = (
        "[0:v][1:v]overlay=enable='between(t,8.5,13.5)':eof_action=pass[v1]; "
        "[v1][2:v]overlay=enable='between(t,30.0,35.0)':eof_action=pass[v2]; "
        f"[v2]subtitles='{SUBTITLES.resolve()}':fontsdir=/System/Library/Fonts[vout]"
    )

    cmd_final = [
        FFMPEG, "-y",
        "-i", str(MAIN_VIDEO),
        "-i", str(broll_1_clip),
        "-i", str(broll_2_clip),
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-map", "0:a",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "19",
        "-c:a", "copy",
        str(OUTPUT_VIDEO)
    ]

    res = subprocess.run(cmd_final, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error en renderizado: {res.stderr}")
        return False

    # Limpieza de clips temporales
    broll_1_clip.unlink(missing_ok=True)
    broll_2_clip.unlink(missing_ok=True)

    print(f"\n[✓] ¡Reel Producido Final generado con éxito!")
    print(f"    Archivo: {OUTPUT_VIDEO}")
    print(f"    Peso: {OUTPUT_VIDEO.stat().st_size / (1024*1024):.1f} MB")
    return True


if __name__ == "__main__":
    produce_reel()

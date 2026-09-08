"""stitch_reel.py — Une, limpia márgenes de silencio y ensambla clips de video (Hook, Contenido, CTA) en un Reel vertical 9:16 fluido."""

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys

BASE_DIR = Path(__file__).resolve().parent
REELS_RAW_DIR = BASE_DIR / "content" / "reels_raw"
REELS_OUT_DIR = BASE_DIR / "content" / "reels_assembled"
REELS_OUT_DIR.mkdir(parents=True, exist_ok=True)

FFMPEG = os.environ.get("FFMPEG_PATH", "/Users/ejimenezsys/.local/bin/ffmpeg")
if not Path(FFMPEG).exists():
    FFMPEG = "ffmpeg"


def get_video_files(raw_dir: Path):
    valid_exts = {".mp4", ".mov", ".m4v", ".webm", ".mkv"}
    files = [f for f in raw_dir.iterdir() if f.is_file() and f.suffix.lower() in valid_exts and not f.name.startswith(".")]
    return sorted(files, key=lambda x: x.name)


def get_speech_bounds(video_path: Path):
    """Detecta automáticamente el inicio y fin real de la voz para recortar los segundos muertos."""
    cmd = [
        FFMPEG, "-i", str(video_path),
        "-af", "silencedetect=noise=-30dB:d=0.35",
        "-f", "null", "-"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    out = res.stderr

    start_cut = 0.0
    # Silencio al inicio
    start_silence_match = re.search(r"silence_start: 0(?:\.0+)?.*?silence_end: ([0-9.]+)", out, re.DOTALL)
    if start_silence_match:
        end_s = float(start_silence_match.group(1))
        start_cut = max(0.0, end_s - 0.12)  # Dejar 120ms de respiro antes de la primera consonante

    # Silencio al final (cuando estiras la mano para apagar la cámara)
    end_silences = re.findall(r"silence_start: ([0-9.]+)", out)
    end_cut = None
    if end_silences:
        last_start = float(end_silences[-1])
        dur_match = re.search(r"Duration: ([0-9:]+\.[0-9]+)", out)
        if dur_match:
            parts = dur_match.group(1).split(":")
            dur = float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
            if dur - last_start < 4.0:  # Es silencio final
                end_cut = min(dur, last_start + 0.25)  # Dejar 250ms de respiro

    return start_cut, end_cut


def normalize_and_trim_clip(input_path: Path, output_path: Path, start_s: float, end_s: float = None):
    """Recorta silencios y normaliza a 1080x1920 (9:16), 30fps, audio AAC estéreo y H.264."""
    cmd = [FFMPEG, "-y"]

    if start_s > 0.05:
        cmd.extend(["-ss", f"{start_s:.3f}"])

    if end_s is not None:
        cmd.extend(["-to", f"{end_s:.3f}"])

    cmd.extend([
        "-i", str(input_path),
        "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,setsar=1",
        "-r", "30",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "19",
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "44100",
        "-ac", "2",
        str(output_path)
    ])

    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Error normalizando {input_path.name}: {res.stderr}")


def stitch_clips(clips, output_path: Path):
    """Concatena los clips normalizados en un solo archivo final de forma fluida."""
    concat_txt = REELS_OUT_DIR / "concat_list.txt"
    lines = [f"file '{c.resolve()}'" for c in clips]
    concat_txt.write_text("\n".join(lines), encoding="utf-8")

    cmd = [
        FFMPEG, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_txt),
        "-c", "copy",
        str(output_path)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    concat_txt.unlink(missing_ok=True)
    if res.returncode != 0:
        raise RuntimeError(f"Error concatenando clips: {res.stderr}")


def get_duration(video_path: Path) -> float:
    cmd = [
        FFMPEG, "-i", str(video_path),
        "-f", "null", "-"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    m = re.search(r"Duration: ([0-9:]+\.[0-9]+)", res.stderr)
    if m:
        parts = m.group(1).split(":")
        return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
    return 0.0


def main():
    parser = argparse.ArgumentParser(description="Ensamblador automático de Reels 9:16 con corte de silencios")
    parser.add_argument("--raw-dir", default=str(REELS_RAW_DIR), help="Carpeta con los clips crudos")
    parser.add_argument("--output-name", default="reel_completo.mp4", help="Nombre del archivo ensamblado")
    args = parser.parse_args()

    raw_dir = Path(args.raw_dir)
    videos = get_video_files(raw_dir)
    if not videos:
        print(f"[!] No se encontraron videos en: {raw_dir}")
        return

    print(f"[*] Se encontraron {len(videos)} tomas para ensamblar en {raw_dir.name}:")
    for idx, v in enumerate(videos, 1):
        print(f"    {idx}. {v.name} ({v.stat().st_size / (1024*1024):.1f} MB)")

    temp_normalized = []
    print("\n[1/2] Limpiando pausas muertas y normalizando formato 9:16 (1080x1920)...")
    for idx, v in enumerate(videos, 1):
        norm_file = REELS_OUT_DIR / f"temp_norm_{idx}.mp4"
        start_s, end_s = get_speech_bounds(v)
        trim_info = f"corte inicio: {start_s:.2f}s"
        if end_s:
            trim_info += f", corte fin: {end_s:.2f}s"
        print(f"      Procesando {v.name} ({trim_info})...")
        normalize_and_trim_clip(v, norm_file, start_s, end_s)
        temp_normalized.append(norm_file)

    final_output = REELS_OUT_DIR / args.output_name
    print(f"\n[2/2] Fusionando tomas en {final_output.name}...")
    stitch_clips(temp_normalized, final_output)

    # Limpieza de archivos temporales
    for t in temp_normalized:
        t.unlink(missing_ok=True)

    dur_final = get_duration(final_output)
    print(f"\n[✓] ¡Reel ensamblado con éxito!")
    print(f"    Archivo final: {final_output}")
    print(f"    Duración total: {dur_final:.1f} segundos")
    print(f"    Peso: {final_output.stat().st_size / (1024*1024):.1f} MB")


if __name__ == "__main__":
    main()

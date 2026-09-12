"""ORQUESTADOR MATUTINO DE PROSPERIA INTELLIGENCE (SISTEMA 5×4×1 — 9:00 AM)

Automatiza la rutina matutina de las 9:00 AM:
1. Lee CANALES_DIGITALES_Y_AUDIENCIA.json para sincronizar los canales de Edward Jiménez.
2. Ingesta la noticia del día o rota el banco verificado de Cortexia.
3. Genera el paquete omnicanal en content/diario/YYYY-MM-DD_<slug>/ incorporando la Regla del Elefante de Víctor Heras.
4. Publica/sincroniza en SQLite (prosper_ia.db) y en content/editorial_published/{slug}.json.
5. Publica en LinkedIn a través de Unipile API (post nativo + primer comentario con link al blog).
6. Si es Viernes (Día 5), dispara automáticamente la compilación semanal del Guion Maestro de YouTube (20 min en 5 actos).
"""

import argparse
from datetime import datetime, time, timedelta, timezone
import json
import os
from pathlib import Path
import sys
import time as time_lib
from typing import Any, Dict, Optional

BASE_DIR = Path(__file__).resolve().parent
CANALES_FILE = BASE_DIR / "CANALES_DIGITALES_Y_AUDIENCIA.json"
ENV_FILE = BASE_DIR / ".env"

# Importar el motor central de Cortexia
from cortexia_engine import run_daily_pipeline, run_weekly_compiler
from unipile_client import UnipileClient, load_env_file


def load_channels_registry() -> Dict[str, Any]:
    """Carga el registro maestro de canales y configuración creativa."""
    if not CANALES_FILE.exists():
        raise FileNotFoundError(f"No se encontró el registro de canales en {CANALES_FILE}")
    return json.loads(CANALES_FILE.read_text(encoding="utf-8"))


def get_current_week_number() -> int:
    """Calcula el número de semana ISO del año."""
    return datetime.now().isocalendar()[1]


def print_orchestrator_banner(channels_data: Dict[str, Any], day_index: int, is_friday: bool) -> None:
    """Imprime el banner directivo del orquestador con el estado de canales."""
    owner = channels_data.get("owner", "Edward Jiménez")
    ch = channels_data.get("channels", {})
    rules = channels_data.get("creative_framework", {})

    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    dia_nombre = dias[(day_index - 1) % 7]

    print("=" * 70)
    print(f" CORTEXIA 5×4×1 — ORQUESTADOR MATUTINO (9:00 AM)")
    print(f" Director: {owner} | Día {day_index} ({dia_nombre}) | Semana ISO #{get_current_week_number()}")
    print("=" * 70)
    print("CANALES ACTIVOS SINCRONIZADOS:")
    print(f" • YouTube:      {ch.get('youtube', {}).get('name')} ({ch.get('youtube', {}).get('url')})")
    print(f" • IG Principal: {ch.get('instagram', {}).get('principal_ia', {}).get('handle')} (+1.300 seguidores recientes)")
    print(f" • IG Secundarias: {ch.get('instagram', {}).get('marketing', {}).get('handle')} | {ch.get('instagram', {}).get('ceo', {}).get('handle')}")
    print(f" • LinkedIn:     {ch.get('linkedin', {}).get('name')} (Unipile API: {ch.get('linkedin', {}).get('posting_time')})")
    print(f" • Threads & X:  {ch.get('threads', {}).get('handle')} | {ch.get('x_twitter', {}).get('handle')}")
    print(f" • TikTok:       {ch.get('tiktok', {}).get('handle')}")
    print("-" * 70)
    print(f"PRINCIPIO VISUAL: {rules.get('golden_rule_visual', 'Regla del Elefante activa')}")
    print(f"RUTINA: 1 Blog + 1 LinkedIn (Unipile 9:00 AM) + 1 Carrusel (01-08.png) + 1 Reel 50s (Víctor Heras)")
    if is_friday:
        print("⚡ HOY ES VIERNES: Se activará además el Compilador Maestro de YouTube (20 min / 5 Actos)")
    print("=" * 70 + "\n")


def execute_morning_routine(
    day_override: Optional[int] = None,
    topic_override: Optional[str] = None,
    lane_override: str = "radar-disrupcion",
    dry_run: bool = True,
    force_weekly: bool = False
) -> Dict[str, Any]:
    """Ejecuta la rutina matutina completa de las 9:00 AM."""
    channels_data = load_channels_registry()
    load_env_file()

    # Determinar día (1=Lunes a 5=Viernes)
    now = datetime.now()
    weekday = now.weekday() + 1  # 1 = Lunes, 5 = Viernes
    day_idx = day_override if day_override is not None else weekday
    if day_idx > 5:
        day_idx = 1  # Por defecto al ciclo L-V

    is_friday = (day_idx == 5) or force_weekly

    print_orchestrator_banner(channels_data, day_idx, is_friday)

    # 1. Ejecución del pipeline diario (Blog, Post LinkedIn, Carrusel PNG/PDF, Reel 50s, Meta)
    publish_to_unipile = not dry_run
    daily_result = run_daily_pipeline(
        topic=topic_override,
        lane=lane_override,
        day_index=day_idx,
        date_str=now.strftime("%Y-%m-%d"),
        publish_linkedin=publish_to_unipile
    )

    slug = daily_result["slug"]
    daily_dir = Path(daily_result["target_dir"])

    # 2. Resumen de archivos generados en la carpeta diaria
    print("\n" + "-" * 70)
    print("PAQUETE DIARIO GENERADO BAJO LA REGLA DEL ELEFANTE:")
    print(f" • Carpeta Diaria:  {daily_dir}")
    print(f" • Artículo Blog:   {daily_dir / '01_articulo_blog.json'} (Publicado en SQLite)")
    print(f" • LinkedIn Unipile: {daily_dir / '02_linkedin_post.txt'}")
    print(f" • Hilo X/Threads:  {daily_dir / '03_x_y_threads' / 'hilo_texto.txt'}")
    print(f" • Carrusel PNG:    {daily_dir / '03_x_y_threads' / 'carrusel_png'} (01.png a 08.png)")
    print(f" • Guion Reel 50s:  {daily_dir / '04_para_grabar' / 'guion_ig_reel_50s.md'} (Teleprompter)")
    print(f" • Meta Noticia:    {daily_dir / '_meta_noticia.json'}")
    print("-" * 70)

    # 3. Publicación en LinkedIn si está en dry-run
    if dry_run:
        print("\n[MODO SIMULACIÓN / DRY-RUN ACTIVO]")
        print("La publicación en LinkedIn NO se disparó automáticamente.")
        print("Para enviar la publicación real a tu perfil de LinkedIn (con imagen y 1er comentario), ejecuta:")
        print(f"  venv/bin/python cortexia_daily_orchestrator.py --publish --day {day_idx}")
    else:
        print("\n✓ Publicación disparada a LinkedIn vía Unipile API a las 9:00 AM con su primer comentario.")

    # 4. Si es Viernes, ejecutar la compilación semanal de 20 min
    if is_friday:
        week_num = get_current_week_number()
        print(f"\n=======================================================")
        print(f" DISPARANDO COMPILACIÓN SEMANAL DE LOS VIERNES (Semana {week_num:02d})")
        print(f"=======================================================")
        youtube_file = run_weekly_compiler(week_number=week_num)
        print(f"✓ Guion Maestro de YouTube listo para grabación directiva: {youtube_file}")

    return {
        "status": "success",
        "day": day_idx,
        "is_friday": is_friday,
        "daily_result": daily_result
    }


def wait_until_9am_daemon() -> None:
    """Modo daemon que espera activamente hasta las 9:00 AM de cada día hábil."""
    print("Modo DAEMON activado: esperando a las 9:00 AM para disparar la rutina matutina...")
    while True:
        now = datetime.now()
        target_time = time(9, 0, 0)
        # Si ya pasaron las 9:00 AM de hoy, esperar hasta mañana a las 9:00 AM
        if now.time() >= target_time:
            next_run = datetime.combine(now.date() + timedelta(days=1), target_time)
        else:
            next_run = datetime.combine(now.date(), target_time)

        wait_seconds = (next_run - now).total_seconds()
        print(f"Próxima ejecución programada: {next_run.strftime('%Y-%m-%d %H:%M:%S')} (esperando {wait_seconds/3600:.1f} horas)")
        time_lib.sleep(min(wait_seconds, 3600))

        # Al despertar cerca del tiempo objetivo
        if abs((datetime.now() - next_run).total_seconds()) < 120:
            weekday = datetime.now().weekday() + 1
            if weekday <= 5:  # Solo de Lunes a Viernes
                execute_morning_routine(day_override=weekday, dry_run=False)
            time_lib.sleep(300)


def main() -> None:
    parser = argparse.ArgumentParser(description="Orquestador Matutino de ProsperIA Intelligence (Sistema 5×4×1)")
    parser.add_argument("--run-now", action="store_true", default=True, help="Ejecuta la rutina matutina de inmediato (default)")
    parser.add_argument("--publish", action="store_true", help="Desactiva dry-run y publica inmediatamente en LinkedIn vía Unipile")
    parser.add_argument("--dry-run", action="store_true", help="Fuerza el modo simulación (no envía a Unipile)")
    parser.add_argument("--day", type=int, default=None, help="Forzar día específico de la semana (1 a 5)")
    parser.add_argument("--topic", type=str, default=None, help="Tema o noticia específica para el día")
    parser.add_argument("--lane", type=str, default="radar-disrupcion", help="Ruta editorial de ProsperIA")
    parser.add_argument("--force-weekly", action="store_true", help="Fuerza la compilación del guion de YouTube de 20 min de los Viernes")
    parser.add_argument("--daemon", action="store_true", help="Ejecuta en segundo plano esperando cada mañana a las 9:00 AM")

    args = parser.parse_args()

    if args.daemon:
        wait_until_9am_daemon()
    else:
        is_dry = not args.publish
        execute_morning_routine(
            day_override=args.day,
            topic_override=args.topic,
            lane_override=args.lane,
            dry_run=is_dry,
            force_weekly=args.force_weekly
        )


if __name__ == "__main__":
    main()

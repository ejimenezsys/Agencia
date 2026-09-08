"""Genera subtítulos estilizados .ass calibrados al guion y los tiempos de Edward."""

from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent / "content" / "reels_assembled"

ass_content = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial Black,58,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,5,2,2,70,70,420,1
Style: Title,Arial Black,68,&H00FFE500,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,6,3,2,60,60,420,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.50,0:00:04.20,Default,,0,0,0,,LA IA PUEDE DECIRTE {\\c&H00FFE500&\\b1}CÓMO LLEGAR{\\c&H00FFFFFF&\\b0}
Dialogue: 0,0:00:04.30,0:00:08.50,Title,,0,0,0,,NUNCA DEBERÍA ELEGIR TU {\\c&H00FFE500&\\b1}DESTINO{\\c&H00FFFFFF&\\b0}
Dialogue: 0,0:00:08.60,0:00:14.20,Default,,0,0,0,,LA DIRECCIÓN SIGUE SIENDO {\\c&H00FFE500&\\b1}HUMANA{\\c&H00FFFFFF&\\b0}
Dialogue: 0,0:00:14.30,0:00:20.50,Default,,0,0,0,,CAPACIDADES {\\c&H00FFE500&\\b1}EXTRAORDINARIAS{\\c&H00FFFFFF&\\b0}
Dialogue: 0,0:00:20.80,0:00:25.50,Default,,0,0,0,,UNA PERSONA PODRÁ CREAR COMO ANTES {\\c&H00FFE500&\\b1}GRANDES EQUIPOS{\\c&H00FFFFFF&\\b0}
Dialogue: 0,0:00:25.60,0:00:30.20,Default,,0,0,0,,UNA EMPRESA PEQUEÑA PODRÁ {\\c&H00FFE500&\\b1}COMPETIR{\\c&H00FFFFFF&\\b0} CON ORGANIZACIONES ENORMES
Dialogue: 0,0:00:30.30,0:00:34.80,Default,,0,0,0,,LO IMPOSIBLE SE VOLVERÁ {\\c&H00FFE500&\\b1}NORMAL{\\c&H00FFFFFF&\\b0}
Dialogue: 0,0:00:34.90,0:00:39.50,Default,,0,0,0,,PERO HAY ALGO QUE LA IA {\\c&H000000FF&\\b1}NO DEBE DECIDIR{\\c&H00FFFFFF&\\b0}
Dialogue: 0,0:00:39.60,0:00:44.20,Default,,0,0,0,,QUÉ CONSTRUIR Y PARA QUÉ {\\c&H00FFE500&\\b1}PROSPERAR{\\c&H00FFFFFF&\\b0}
Dialogue: 0,0:00:44.30,0:00:49.20,Default,,0,0,0,,LA TECNOLOGÍA PUEDE DARTE {\\c&H00FFE500&\\b1}VELOCIDAD{\\c&H00FFFFFF&\\b0}
Dialogue: 0,0:00:49.50,0:00:54.00,Default,,0,0,0,,LA INTELIGENCIA FINANCIERA TE DA {\\c&H00FFE500&\\b1}VALOR{\\c&H00FFFFFF&\\b0}
Dialogue: 0,0:00:54.10,0:00:58.80,Default,,0,0,0,,LA EMOCIONAL TE PERMITE {\\c&H00FFE500&\\b1}LIDERAR{\\c&H00FFFFFF&\\b0} EN INCERTIDUMBRE
Dialogue: 0,0:00:58.90,0:01:03.50,Title,,0,0,0,,LA DIRECCIÓN {\\c&H00FFE500&\\b1}SIGUE SIENDO HUMANA{\\c&H00FFFFFF&\\b0}
Dialogue: 0,0:01:03.60,0:01:07.80,Default,,0,0,0,,TECNOLOGÍA, {\\c&H00FFE500&\\b1}CRITERIO{\\c&H00FFFFFF&\\b0} Y {\\c&H00FFE500&\\b1}PROPÓSITO{\\c&H00FFFFFF&\\b0}
Dialogue: 0,0:01:07.90,0:01:11.80,Title,,0,0,0,,ÉSTA ES TU CONVERSACIÓN. {\\c&H00FFE500&\\b1}SÍGUEME.{\\c&H00FFFFFF&\\b0}
"""

(OUT_DIR / "subtitulos_manifiesto.ass").write_text(ass_content, encoding="utf-8")
print(f"Subtítulos ASS creados en: {OUT_DIR / 'subtitulos_manifiesto.ass'}")

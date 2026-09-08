# Skill: `transcribe-master` (Portable para Antigravity)

Este skill autónomo y portable permite transcribir cualquier archivo de audio, video o enlace de YouTube a texto estructurado de alta precisión.

Genera de forma automática:
1. **Texto limpio continuo (`.md`):** Lectura humana sin muletillas.
2. **Registro con marcas de tiempo (`.md`):** Con diarización de hablantes (`[01:23] Hablante 1: ...`).
3. **Subtítulos sincronizados (`.srt` y `.vtt`):** Listos para editores de video (CapCut, Premiere, DaVinci).
4. **Esquema palabra por palabra (`words.json`):** Para animaciones de tipografía cinética y Remotion.
5. **Resumen ejecutivo:** Con puntos clave y tareas acordadas.

---

## 🚀 Cómo instalar este skill en tu configuración global

Ejecuta este comando en la terminal de tu Mac para tenerlo disponible en **todos tus proyectos de Antigravity**:

```bash
mkdir -p ~/.gemini/config/skills/transcribe-master
cp -r /Users/ejimenezsys/Desktop/Cortexia/777_cortexia_v15.2_Ejimenezsys/DOCS/SKILLS_EXPORT/transcribe-master/* ~/.gemini/config/skills/transcribe-master/
```

O si prefieres instalarlo únicamente en un proyecto específico:

```bash
mkdir -p /ruta/a/tu/nuevo-proyecto/.agents/skills/transcribe-master
cp -r /Users/ejimenezsys/Desktop/Cortexia/777_cortexia_v15.2_Ejimenezsys/DOCS/SKILLS_EXPORT/transcribe-master/* /ruta/a/tu/nuevo-proyecto/.agents/skills/transcribe-master/
```

---

## 📁 Estructura del Skill

```
transcribe-master/
├── SKILL.md                               # Instrucciones maestras del skill
├── README.md                              # Guía de instalación y ejemplos de uso
├── scripts/
│   └── transcribe_helper.py               # Script ejecutor local y extractor de YouTube
└── references/
    ├── formats-and-schemas.md             # Especificación técnica de SRT, VTT, Markdown y words.json
    └── engines-and-setup.md               # Guía de configuración para Groq, Whisper local, Scribe y yt-dlp
```

---

## 💡 Cómo usarlo en cualquier proyecto

Una vez instalado en tu carpeta global o local, puedes invocarlo con prompts naturales como:

- *"Usa el skill **transcribe-master** para transcribir este audio: `fuentes/audio/entrevista.mp3`. Quiero el texto limpio y los subtítulos SRT."*
- *"Extrae la transcripción completa de este video de YouTube: `https://www.youtube.com/watch?v=...` y genera un resumen ejecutivo."*
- *"Necesito un archivo `words.json` con marcas de tiempo por palabra de esta locución para sincronizar subtítulos cinéticos."*
- *"Transcribe esta reunión y separa las intervenciones por cada persona que habla."*

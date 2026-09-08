# Motores de Transcripción y Configuración Técnica

El skill `transcribe-master` puede operar tanto de forma 100% local (sin costo ni dependencias externas) como a través de APIs de alta velocidad y precisión.

---

## 1. Extracción Directa de YouTube (Sin descargar audio)

Si el video de YouTube ya cuenta con subtítulos generados por el autor o por la plataforma, se pueden extraer al instante en texto puro:

```bash
# Opción A: Mediante la librería ligera youtube-transcript-api (Python)
pip install youtube-transcript-api

python3 -c "
from youtube_transcript_api import YouTubeTranscriptApi
transcript = YouTubeTranscriptApi.get_transcript('VIDEO_ID', languages=['es', 'en'])
text = ' '.join([x['text'] for x in transcript])
print(text[:500])
"

# Opción B: Mediante yt-dlp (descarga directa de pistas VTT/SRT)
yt-dlp --write-auto-sub --sub-lang es --skip-download -o "subtitulos" "https://www.youtube.com/watch?v=VIDEO_ID"
```

---

## 2. Motor Groq Whisper (Ultra-Rápido en la Nube)

Groq ejecuta el modelo `whisper-large-v3` sobre chips LPU a velocidades de hasta 200x tiempo real (transcribe 1 hora en menos de 10 segundos).

- **Variable de entorno:** `export GROQ_API_KEY="gsk_..."`
- **Costo:** Capa gratuita muy generosa (~$0.00004 / segundo en producción).
- **Ejemplo con curl o cliente OpenAI:**

```bash
curl -X POST "https://api.groq.com/openai/v1/audio/transcriptions" \
     -H "Authorization: Bearer $GROQ_API_KEY" \
     -H "Content-Type: multipart/form-data" \
     -F file="@mi_audio.mp3" \
     -F model="whisper-large-v3" \
     -F response_format="verbose_json" \
     -F timestamp_granularities[]="word"
```

---

## 3. Motor ElevenLabs Scribe (Máxima Precisión Fonética y Diarización)

Ideal cuando se requiere `words.json` con sincronización palabra por palabra para videos con tipografía cinética (Remotion/HyperFrames) o detección precisa de hablantes (Speaker A vs Speaker B).

- **Variable de entorno:** `export ELEVENLABS_API_KEY="..."`
- **Endpoint:** `https://api.elevenlabs.io/v1/speech-to-text`
- **Capacidades:** Detección de idiomas mixtos, marcado de respiraciones, números exactos y diarización automática.

---

## 4. Whisper Local (100% Gratuito y Privado)

Si estás trabajando con audios confidenciales, contratos legales o datos médicos y no deseas subir información a la nube:

```bash
# Instalación recomendada (4x más rápido que Whisper original):
pip install faster-whisper

# Script de ejecución rápida en Python:
python3 -c "
from faster_whisper import WhisperModel
model = WhisperModel('medium', device='cpu', compute_type='int8')
segments, info = model.transcribe('mi_audio.mp3', language='es')
for segment in segments:
    print(f'[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}')
"
```

---

## 5. Pre-procesamiento de Audio con FFmpeg (Buena Práctica)

Para acelerar las subidas y reducir costos en cualquier API, convierte siempre audios pesados (WAV o MP4 grandes) a un formato ligero optimizado para voz:

```bash
# Convierte a mono, 16 kHz y bitrate de 64 kbps (perfecto para reconocimiento de voz)
ffmpeg -i video_o_audio_original.mp4 -vn -ar 16000 -ac 1 -b:a 64k audio_optimizado.mp3
```

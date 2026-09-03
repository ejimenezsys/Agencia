# 777 NotebookLM Podcast

Wrapper del tool portable `777_tools/777_notebooklm/`. Genera un podcast de audio (audio overview) a partir de un notebook NotebookLM, con opciones de formato, duración, idioma y foco temático.

## Cuándo lo activa el usuario

- "Podcast" / "Audio overview" / "Podcast Cortexia"
- "NotebookLM podcast" / `/777-notebooklm-podcast`
- Cuando entrega un archivo fuente y pide un podcast.

## Qué tiene que hacer el usuario

1. Tener un notebook con fuentes ya cargadas (usar `777-notebooklm-add` si no existe).
2. Invocar el skill — pregunta destino, formato, duración e idioma vía picker.
3. Esperar el render (puede tomar minutos en NotebookLM).

## Qué produce

Un archivo de audio (mp3/m4a) en `DOCS/CONTENIDO/PROYECTOS/<Project>/notebooklm/audio/` por por defecto — o ruta custom si el usuario lo pide.

## Lo que NO hace

- No genera infográfico ni video — para eso usar los skills hermanos.
- No agrega fuentes al notebook — eso lo hace `777-notebooklm-add`.

## Qué te va a preguntar

1. Destino del salida (proyecto activo del espacio de trabajo por por defecto / ruta custom).
2. Notebook nuevo o existente.
3. Fuentes a agregar (si nuevo) — ciclo hasta que digas listo.
4. Formato del podcast (análisis profundo conversacional / brief informativo / debate / estilo entrevista).
5. Duración (short / standard / long — varía por NotebookLM).
6. Idioma de salida.
7. Foco temático (texto libre — qué quieres que el podcast enfatice).
8. Confirmación final antes de gastar tiempo de generación (puede tomar varios minutos).

## Ejemplo de uso

Tú dices *"podcast del notebook Cortexia Radar, formato análisis profundo, ~15 min, español neutro"* → el skill route salida al proyecto activo, confirma el notebook, eliges formato + duración + idioma + el foco temático. Confirma el resumen y dispara la generación. Mientras NotebookLM renderiza, el skill espera en segundo plano y al terminar descarga el mp3 a `DOCS/CONTENIDO/PROYECTOS/cortexia/notebooklm/audio/<nombre>.mp3`. Listo para subir o encadenar con flujos posteriores.

## Detalle interno

Ver `SKILL.md` y `FLOWS/777-notebooklm-podcast.md`.

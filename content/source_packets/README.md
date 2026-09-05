# Paquetes de fuentes

Cada borrador comienza con un archivo JSON revisado por una persona. El generador no
investiga por su cuenta ni completa referencias faltantes.

```json
{
  "editorial_question": "¿Qué cambió y qué decisión empresarial podría afectar?",
  "audience": "Dueños de clínicas dentales, estéticas o capilares",
  "facts": [
    {"claim": "Hecho comprobable", "source_id": "source-1"}
  ],
  "sources": [
    {
      "id": "source-1",
      "title": "Título exacto de la fuente",
      "url": "https://fuente-primaria.example/reporte",
      "publisher": "Entidad responsable",
      "published_at": "AAAA-MM-DD",
      "accessed_at": "AAAA-MM-DD"
    }
  ],
  "unknowns": ["Aquello que la evidencia todavía no permite afirmar"],
  "edward_interpretation": null
}
```

`edward_interpretation` permanece vacío hasta que Edward aporte o apruebe su lectura.
Los archivos de esta carpeta son insumos; nunca equivalen a autorización de publicación.

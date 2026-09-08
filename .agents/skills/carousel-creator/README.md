# Skill: `carousel-creator` (Portable para Antigravity)

Este skill autónomo y portable permite conceptualizar, redactar, dirigir el diseño y renderizar carruseles de alta retención para **LinkedIn** (PDFs multi-página), **Instagram** (carruseles 4:5 de 1080x1350px) y **X/Threads**.

---

## 🚀 Cómo instalar este skill en otro proyecto de Antigravity

Tienes dos formas muy sencillas de llevarlo a cualquier otro workspace de Antigravity:

### Opción A: Copiar la carpeta directamente (Recomendado)
Copia la carpeta `carousel-creator/` dentro del directorio de skills de tu nuevo proyecto:

```bash
# Desde la terminal de tu nuevo proyecto:
cp -r /Users/ejimenezsys/Desktop/Cortexia/777_cortexia_v15.2_Ejimenezsys/DOCS/SKILLS_EXPORT/carousel-creator/ .agents/skills/carousel-creator/
```

O si prefieres mantenerlo como skill de uso manual o esporádico:
```bash
cp -r /Users/ejimenezsys/Desktop/Cortexia/777_cortexia_v15.2_Ejimenezsys/DOCS/SKILLS_EXPORT/carousel-creator/ .agents/skills-manual/carousel-creator/
```

### Opción B: Copia global para todos tus proyectos
Si quieres que esté disponible en cualquier proyecto que abras en tu máquina sin tener que copiarlo cada vez, colócalo en tu configuración global de Antigravity:

```bash
mkdir -p ~/.gemini/config/skills/carousel-creator
cp -r /Users/ejimenezsys/Desktop/Cortexia/777_cortexia_v15.2_Ejimenezsys/DOCS/SKILLS_EXPORT/carousel-creator/* ~/.gemini/config/skills/carousel-creator/
```

---

## 📁 Estructura del Skill

```
carousel-creator/
├── SKILL.md                          # Instrucciones operativas y flujo en 5 pasos
├── README.md                         # Esta guía de instalación y uso rápido
└── references/
    ├── carousel-archetypes.md        # Los 5 arquetipos psicológicos y fórmulas de Slide 1
    ├── design-system-specs.md        # Medidas (1080x1350), safe zones, tipografías y paletas
    └── html-template.html            # Plantilla visual responsive para previsualizar y exportar a PDF/PNG
```

---

## 💡 Cómo usarlo en tu nuevo proyecto

Una vez instalado, simplemente habla de forma natural con el agente en tu nuevo proyecto:

- *"Crea un carrusel de 7 diapositivas para LinkedIn explicando [tu tema]"*
- *"Convierte este artículo en un carrusel con el arquetipo Paso a Paso"*
- *"Diseña un carrusel contrarian sobre los errores comunes en [tu nicho]"*
- *"Usa el skill carousel-creator para preparar un post deslizable"*

El agente seguirá la metodología para:
1. Proponerte 3 ganchos magnéticos para la Lámina 1.
2. Escribir el guion lámina por lámina respetando la regla de 1 idea por slide.
3. Generar la lámina de síntesis (el disparador de guardados).
4. Configurar la llamada a la acción (CTA) y adaptar el archivo `html-template.html` con tu contenido para que puedas previsualizarlo o imprimirlo como PDF listo para LinkedIn.

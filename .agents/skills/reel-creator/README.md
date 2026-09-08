# Skill: `reel-creator` (Portable para Antigravity)

Este skill autónomo y portable permite conceptualizar, redactar y dirigir videos cortos verticales (9:16) de alto impacto para **Instagram Reels**, **TikTok** y **YouTube Shorts**.

Aplica los 7 beats narrativos de retención, las fórmulas probadas de ganchos de 3 segundos, las zonas seguras (safe zones) para móviles y genera tablas de guion con indicaciones visuales, prompts de B-roll y captions.

---

## 🚀 Cómo instalar este skill en tu configuración global

Ejecuta este comando en la terminal de tu Mac para tenerlo disponible en **todos tus proyectos de Antigravity**:

```bash
mkdir -p ~/.gemini/config/skills/reel-creator
cp -r /Users/ejimenezsys/Desktop/Cortexia/777_cortexia_v15.2_Ejimenezsys/DOCS/SKILLS_EXPORT/reel-creator/* ~/.gemini/config/skills/reel-creator/
```

O si solo quieres usarlo en un proyecto específico:
```bash
mkdir -p /ruta/a/tu/nuevo-proyecto/.agents/skills/reel-creator
cp -r /Users/ejimenezsys/Desktop/Cortexia/777_cortexia_v15.2_Ejimenezsys/DOCS/SKILLS_EXPORT/reel-creator/* /ruta/a/tu/nuevo-proyecto/.agents/skills/reel-creator/
```

---

## 📁 Estructura del Skill

```
reel-creator/
├── SKILL.md                               # Flujo maestro en 5 pasos y reglas de oro
├── README.md                              # Guía de instalación y ejemplos de uso
└── references/
    ├── hook-formulas-916.md               # 6 familias de ganchos para los primeros 3 segundos
    ├── reel-templates-7beats.md           # Plantillas y presupuestos de palabras (30s, 45s, 60s)
    └── safe-zones-and-visual-specs.md     # Zonas seguras 1080x1920, tipografía cinética y pacing
```

---

## 💡 Cómo pedirle un Reel al agente en cualquier proyecto

Una vez instalado en tu carpeta global o local, puedes invocarlo con prompts naturales como:

- *"Usa el skill reel-creator para escribir un guion de 45 segundos sobre [tu tema] para Instagram Reels. Quiero formato talking-head con B-roll y gancho contrarian."*
- *"Escribe un guion viral de 30 segundos para TikTok explicando [concepto clave] en 3 pasos rápidos."*
- *"Convierte este artículo / publicación en un guion de Reel de 60 segundos con los 7 beats de retención y la tabla de dirección visual."*
- *"Dame 3 ganchos magnéticos para empezar un video sobre [problema común en tu nicho]."*

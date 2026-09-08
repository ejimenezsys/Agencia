# Especificaciones del Sistema de Diseño para Carruseles

El diseño de un carrusel determina si el usuario continúa deslizando o abandona tras la primera lámina. Esta guía estandariza las proporciones, márgenes seguros, tipografía y paletas cromáticas para garantizar una legibilidad impecable en dispositivos móviles.

---

## 1. Dimensiones Canónicas y Ratios

| Formato | Resolución | Ratio | Uso Recomendado |
|---|---|---|---|
| **Vertical Retrato (Gold Standard)** | `1080 x 1350 px` | **4:5** | Instagram Carousel & LinkedIn Document PDF. Ocupa el máximo espacio en pantalla móvil. |
| **Cuadrado Clásico** | `1080 x 1080 px` | **1:1** | Instagram Feed tradicional, Facebook, compatibilidad universal. |

> **Regla de oro:** Usa siempre **4:5 (1080 x 1350 px)** a menos que exista una restricción técnica específica. Ofrece un 25% más de área visible en el scroll respecto a 1:1, lo que incrementa el stopping power.

---

## 2. Safe Zones (Zonas Seguras) en Pantalla Móvil

Para evitar que los textos queden tapados por elementos de la interfaz de usuario (iconos de guardado, likes, barra de paginación de LinkedIn, etc.):

```
+------------------------------------------+  ^
|            MARGIN TOP: 120px             |  | Safe Zone Superior
|  [Logo / Handle]              [01 / 07]  |  v
+------------------------------------------+
| <--- MARGIN LEFT: 80px                   |
|                                          |
|            ÁREA DE CONTENIDO             |
|            (920 x 1070 px)               |
|                                          |
|                    MARGIN RIGHT: 80px -> |
+------------------------------------------+
|  [Desliza →]              [Paginación]   |  ^ Safe Zone Inferior
|           MARGIN BOTTOM: 160px           |  | (Crucial en IG/LinkedIn)
+------------------------------------------+  v
```

- **Margen Superior:** Mínimo `120 px`. Reservado para handle/avatar del autor y contador de lámina.
- **Margen Inferior:** Mínimo `160 px`. Especialmente sensible en LinkedIn (los botones de paginación tapan el fondo) e Instagram (texto de descripción y botones de interacción).
- **Márgenes Laterales:** Mínimo `80 px`. Evita que el texto toque los bordes físicos del teléfono.

---

## 3. Jerarquía Tipográfica y Escalas

El texto debe leerse sin esfuerzo en una pantalla de 6 pulgadas con el brillo al 50%.

### Escala de Tamaños (Base 1080x1350 px):
- **Hero Title (Slide 1):** `56 px – 72 px` | Peso: `Bold` o `ExtraBold` (800) | Line-height: `1.15`
- **Slide Title (Slides 2 al final):** `44 px – 52 px` | Peso: `Bold` (700) | Line-height: `1.2`
- **Cuerpo de texto / Explicación:** `26 px – 32 px` | Peso: `Medium` o `Regular` (400–500) | Line-height: `1.4`
- **Etiquetas superiores (Category Badges):** `16 px – 18 px` | Peso: `SemiBold` (600) | Tracking: `+1.5px` (Uppercase)
- **Notas al pie / Contadores / Handle:** `16 px – 18 px` | Peso: `Medium` (500)

### Tipografías Recomendadas (Google Fonts gratuitas y modernas):
1. **Opción A (Moderna / Tech / SaaS):** `Plus Jakarta Sans` o `Inter`
2. **Opción B (Energética / Disruptiva):** `Outfit` o `Clash Display`
3. **Opción C (Editorial / Consultoría / Finanzas):** Titular en `Fraunces` o `Merriweather` + Cuerpo en `Plus Jakarta Sans`

---

## 4. Paletas Cromáticas Validadas

Elige una paleta y mantenla en las N diapositivas para crear identidad de marca consistente.

### Paleta 1: Dark Tech Luxury (Alto impacto y modernidad)
- **Fondo:** `#0A0D14` (Negro carbón azulado profundo)
- **Superficie de tarjetas:** `#161B26` (Gris oscuro con elevación)
- **Texto Principal:** `#F8FAFC` (Blanco puro suave)
- **Texto Secundario:** `#94A3B8` (Gris frío legible)
- **Acento Primario:** `#38BDF8` (Azul cian eléctrico) o `#818CF8` (Índigo moderno)
- **Acento de Éxito / Warning:** `#4ADE80` (Verde menta) / `#FB7185` (Rosa coral)

### Paleta 2: Editorial Warm (Consultores, agencias, marcas personales)
- **Fondo:** `#FBFBF9` (Blanco crema cálido estilo papel de arte)
- **Superficie de tarjetas:** `#FFFFFF` (Blanco puro con sombra sutil)
- **Bordes:** `#E7E5E4` (Gris arena tenue)
- **Texto Principal:** `#1C1917` (Negro asfalto cálido)
- **Texto Secundario:** `#57534E` (Gris grafito cálido)
- **Acento Primario:** `#D97706` (Ámbar terracota) o `#2563EB` (Azul real)

### Paleta 3: High-Energy Neon (Growth, Marketing, Emprendimiento)
- **Fondo:** `#111827` (Gris azulado oscuro)
- **Texto Principal:** `#FFFFFF`
- **Acento Primario:** `#CCFF00` (Cyber Lime / Amarillo voltio) — Máxima retención visual en feeds saturados.

---

## 5. Elementos Clave de Retención y Micro-Diseño

1. **Badge de Categoría Superior:**
   - Una píldora o etiqueta en la parte superior del slide: `PASO 03`, `ERROR TÍPICO`, `MÉTODO 777`. Ayuda al cerebro a ordenar la información.
2. **Visual Bleed (Corte de Continuidad):**
   - Un elemento gráfico circular, flecha o diagrama que se corta en el borde derecho del Slide N y continúa en el borde izquierdo del Slide N+1. Crea una tensión visual en el cerebro que incita inconscientemente a deslizar.
3. **Cajas de Resalte (Callouts):**
   - Tarjetas redondeadas (`border-radius: 20px`) con fondo ligeramente contrastado y un borde sutil (`1px solid rgba(255,255,255,0.08)`) para encapsular ejemplos o notas clave.
4. **Slide de Síntesis (Slide N-1):**
   - Antes del CTA final, coloca una lámina de "Resumen en 1 Vistazo". Agrupa los 3-5 puntos clave en bullets ordenados con iconos. Esta es la lámina que la audiencia guardará en favoritos.
5. **Slide Final con Credencial:**
   - Foto circular del creador (100x100px), nombre completo en negrita, subtítulo de una línea ("Ayudo a X a lograr Y"), y el CTA principal bien destacado.

# Especificaciones Visuales y Safe Zones 9:16 (1080 x 1920 px)

En videos verticales (Instagram Reels, TikTok y YouTube Shorts), las aplicaciones superponen botones, textos y controles que tapan hasta el 35% de la pantalla. Si tus subtítulos o tu rostro quedan en esas áreas, el contenido pierde profesionalismo y retención.

---

## 1. Diagrama de Zonas Seguras (Safe Zones)

```
0px +------------------------------------------+
    |         ZONA DE PELIGRO SUPERIOR         |  ^ 220 px
    |       (Tabs de Reels / TikTok Search)    |  v
220 +------------------------------------------+
    |                                          |
    |                                          |
    |             ÁREA SEGURA TOTAL            |
    |          (Rostro del creador,            |
    |           subtítulos principales,        |
    |           gráficos y diagramas)          |  1080 px ancho
    |                                          |
    |             (960 x 1280 px)       |ICONOS|  <-- 120 px margen derecho
    |                                   |LIKES |      (Botones de like,
    |                                   |SHARE |       comentarios y audio)
    |                                   |GUARD |
1500+-----------------------------------+------+
    |         ZONA DE PELIGRO INFERIOR         |  ^ 420 px
    |   (Nombre de usuario, descripción,       |  | (Crucial: TikTok e IG
    |    nombre de audio y barra de progreso)  |  v  tapan todo aquí)
1920+------------------------------------------+
```

### Reglas de Ubicación:
- **Margen Superior:** Mantén un espacio libre de **220 px**.
- **Margen Inferior:** Mantén un espacio libre de **420 px**. NUNCA coloques subtítulos o información clave en el tercio inferior de la pantalla.
- **Margen Derecho:** Deja **120 px** libres a la derecha en la mitad inferior para no chocar con la columna de interacción (Corazón, Comentarios, Guardar, Compartir).
- **Posición Óptima para Subtítulos:** Entre los **900 px y 1350 px** verticales (justo debajo del pecho del creador o en el centro exacto de la pantalla).

---

## 2. Tipografía y Subtítulos Dinámicos (Kinetic Typography)

El 75% de los usuarios en redes sociales consumen videos con el volumen silenciado o bajo. Los subtítulos dinámicos son obligatorios.

### Buenas Prácticas para Subtítulos:
1. **Pocas palabras por pantalla:** Muestra entre **1 y 4 palabras simultáneas**. Evita párrafos largos que parezcan un libro.
2. **Jerarquía Cromática:**
   - Color base: Blanco puro (`#FFFFFF`) o blanco cálido (`#F8FAFC`).
   - Color de acento de marca: Aplícalo únicamente a la palabra clave que se está pronunciando (ej. Ámbar, Azul Eléctrico o Verde Lima).
3. **Legibilidad garantizada sobre cualquier fondo:**
   - Aplica una sombra suave de contraste: `drop-shadow: 0 4px 16px rgba(0,0,0,0.85)` o un fondo semitransparente estilo marcador detrás de la palabra.
   - Tipografía sans-serif gruesa y limpia: *Plus Jakarta Sans*, *Inter Black*, *Montserrat ExtraBold* o *The Bold Font*.
4. **Micro-Animación (El Pop del Keyword):**
   - La palabra clave debe experimentar un leve crecimiento de escala (un "pop" del 10-15%) justo en la milésima de segundo en que se pronuncia.

---

## 3. Pacing y Composición Visual

- **Regla de los 3 Segundos:** La composición visual debe renovarse cada 2.5 a 4 segundos. Si una misma toma estática dura más de 5 segundos, el usuario experimenta fatiga visual y abandona.
- **Técnicas de Variación Visual:**
  - **Zoom In Digital:** Pasa de un plano medio (pecho arriba) a un primer plano (hombros arriba) para enfatizar una frase crítica.
  - **Inserción de B-Roll:** Intercala clips de apoyo cinematográficos de 1.5 a 2.5 segundos.
  - **Overlays Gráficos:** Inserta capturas de pantalla, cuadros de diálogo, gráficos o iconos que ilustren el concepto hablado.
  - **Efectos de Sonido Sutiles (SFX):** Un sonido "whoosh" en las transiciones o un "pop" en la aparición de gráficos mantiene despierta la atención auditiva.

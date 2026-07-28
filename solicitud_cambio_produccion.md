# Solicitud de Configuración Única en Producción — PROSPER IA

Hola Omar,

Hemos optimizado la arquitectura del proyecto para que **NUNCA MÁS requieras reconstruir el contenedor Docker (`docker build`) ni intervenir manualmente** cuando el bot de IA publique nuevos artículos de blog cada 10 días.

---

## 🤖 ¿Cómo funciona la automatización de 0 intervención?

1. **Montaje Directo de Archivos Estáticos**:
   Se ha actualizado [docker-compose.prod.yml](file:///e:/Proyectos/Eduardo/Agencia/docker-compose.prod.yml) para incluir un montaje de volumen directo: `- ./static:/app/static`. De este modo, cualquier archivo `.jpg` nuevo que llegue al servidor vía `git pull` estará disponible en el contenedor al instante **sin reconstruir la imagen**.

2. **Sincronización Dinámica de Base de Datos**:
   [database.py](file:///e:/Proyectos/Eduardo/Agencia/database.py) y [main.py](file:///e:/Proyectos/Eduardo/Agencia/main.py) ahora sincronizan automáticamente los nuevos artículos con SQLite en tiempo de ejecución al recibir peticiones en `/blog`.

3. **Despliegue Automático por SSH (Opcional)**:
   Se ha añadido un paso en [.github/workflows/generate_blog.yml](file:///e:/Proyectos/Eduardo/Agencia/.github/workflows/generate_blog.yml) para que GitHub Actions se conecte por SSH al VPS y ejecute `git pull origin main` de forma autónoma.

---

## 🚀 Pasos para la Configuración Única (Solo se realiza 1 vez):

1. **Conectarse al servidor VPS** y navegar a la carpeta de la aplicación:
   ```bash
   cd /ruta/de/la/app/agencia
   ```
2. **Descargar los últimos cambios**:
   ```bash
   git pull origin main
   ```
3. **Reconstruir el contenedor por última vez** (para aplicar el nuevo montaje de volumen `./static:/app/static`):
   ```bash
   docker compose -f docker-compose.prod.yml up -d --build
   ```

### 🔐 (Opcional) Activar el Despliegue 100% Autónomo en GitHub Secrets
Para que ni siquiera tengas que hacer `git pull` manualmente en el VPS cada 10 días, agrega los siguientes secretos en el repositorio de GitHub (**Settings > Secrets and variables > Actions**):

- `VPS_HOST`: Dirección IP o dominio de tu VPS.
- `VPS_USERNAME`: Usuario SSH (ej. `root` u `ubuntu`).
- `VPS_SSH_KEY`: Clave privada SSH con acceso al VPS.
- `VPS_APP_DIR`: Ruta absoluta del repositorio en el servidor (ej. `/var/www/agencia`).

¡Una vez aplicado esto, la publicación de noticias con IA y sus imágenes correrá al 100% de forma desatendida! 🚀

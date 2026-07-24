# Solicitud de Despliegue en Producción — PROSPER IA

Hola Omar,

Edward ha implementado un script de automatización (`generate_ai_posts.py`) que genera 6 artículos de blog con sus respectivas portadas visuales creadas con IA de forma totalmente automatizada. 

## 🤖 ¿Cómo funciona la automatización?
1. Se ha configurado un **GitHub Action** (`.github/workflows/generate_blog.yml`) que se ejecuta de forma totalmente autónoma **cada 10 días**.
2. El script consulta la API de Gemini, redacta 6 artículos profesionales orientados a CEOs, genera programáticamente 6 imágenes de portada abstractas en `static/` y actualiza la lista `INITIAL_BLOG_POSTS` en `main.py`.
3. El GitHub Action realiza automáticamente el `git commit` y `git push` de estos cambios de vuelta al repositorio en la rama `main`.

---

## 🚀 Instrucciones de Despliegue en Producción
Para desplegar los cambios actuales (que ya contienen las noticias y las nuevas imágenes en el repositorio):

1. **Conectarse al servidor VPS** (donde corre la web `https://agenciaprosperia.com/`).
2. **Navegar al directorio de la aplicación**:
   ```bash
   cd /ruta/de/la/app/agencia
   ```
3. **Descargar los últimos cambios desde GitHub** (para obtener el nuevo `main.py` y las portadas `.jpg` en `static/`):
   ```bash
   git pull origin main
   ```
4. **Reconstruir y levantar el contenedor Docker de producción**:
   Dado que el Dockerfile copia los archivos estáticos en la fase de construcción (`COPY . .`), es necesario forzar la reconstrucción de la imagen para que empaquete las nuevas imágenes en la carpeta `/app/static/` del contenedor:
   ```bash
   docker compose -f docker-compose.prod.yml up -d --build
   ```

---

## 💡 Recomendación de Automatización para el Futuro
Para evitar tener que hacer este despliegue manual cada 10 días cuando el GitHub Action publique nuevos artículos, te sugerimos una de las siguientes opciones:

* **Opción A (Webhooks)**: Configurar un webhook en el repositorio de GitHub que apunte a un script en el servidor que ejecute el `git pull` y `docker compose up -d --build` de forma automática.
* **Opción B (Watchtower)**: Si utilizas un registro de Docker, configurar Watchtower para que actualice el contenedor automáticamente al detectar una nueva imagen.
* **Opción C (GitHub Actions Deploy)**: Añadir un paso final al workflow de GitHub Actions que realice la conexión SSH al servidor para ejecutar los comandos de despliegue.

¡Muchas gracias por el apoyo con la administración del servidor!

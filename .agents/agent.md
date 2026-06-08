# 🤖 Prosper IA (Agencia) - Master Agent Instructions (agent.md)

Este archivo sirve como la **memoria principal y guía maestra** para cualquier asistente de IA trabajando en el proyecto **Prosper IA (Agencia)**. Sintetiza la arquitectura de la aplicación, las decisiones tecnológicas clave y las reglas de programación y colaboración obligatorias.

---

## 1. 🌐 Contexto Global del Proyecto
- **Propósito**: CRM y plataforma de administración de leads para **Prosper IA (Agencia)**, que incluye notificaciones por correo electrónico automáticas al recibir solicitudes de contacto.
- **Stack Tecnológico**:
  - **Frontend**: Plantillas HTML renderizadas del lado del servidor (FastAPI Jinja2/HTML templates en `/templates`) acompañadas de recursos estáticos en `/static`.
  - **Backend (CRM y API)**: [FastAPI (Python 3.11)](https://fastapi.tiangolo.com/) - Servidor API asíncrono, ruteador de templates y gestor de tareas de email.
  - **Base de Datos**: [SQLite](https://www.sqlite.org/) - Almacenamiento rápido y autocontenido de leads y sesiones.
  - **Infraestructura**: Docker, Docker Compose (entornos locales `dev` y productivos `prod`), despliegues gestionados por **Coolify**.

---

## 2. 🧠 Lecciones Aprendidas y Decisiones Arquitectónicas

### 2.1. Jinja2/HTML Templates y Estáticos
- Las páginas no se pre-renderizan de forma estática en la construcción, sino que son generadas de forma dinámica en cada petición por el backend usando las plantillas ubicadas en la carpeta `/templates`.
- **Regla**: Los archivos estáticos (JS, CSS e imágenes del cliente) residen bajo el directorio `/static`. El servidor de producción expone este directorio de forma transparente.

### 2.2. Notificaciones SMTP
- El backend envía correos electrónicos al administrador ante nuevos leads utilizando un servidor SMTP.
- **Configuración**: El contenedor productivo requiere de variables de entorno SMTP configuradas (`SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_SENDER`).
- **Regla**: Nunca hardcodear credenciales en el código. Las variables deben ser recuperadas siempre mediante `os.environ` y tener fallbacks seguros para desarrollo local sin SMTP.

### 2.3. Configuración de Puertos y Base de Datos
- **Puerto Asignado**: La aplicación se publica en el puerto **`8000`** en producción (o mediante la variable de entorno `APP_PORT` de Coolify).
- **Persistencia**: La base de datos se almacena en `/app/data/prosper_ia.db`, mapeada al volumen Docker nombrado `prosper_ia_prod_data`.

---

## 3. 📜 Reglas de Codificación y Estilo (Obligatorias)

### 3.1. Idioma
- **Idioma**: SIEMPRE responder, documentar, comentar el código y realizar el análisis en **ESPAÑOL**.

### 3.2. Estándar de Código (PEP8 y Google Style)
- **Docstrings**: Todos los módulos, clases y funciones no triviales de Python deben documentarse siguiendo el formato de **Estilo Google** (con secciones estructuradas de `Args`, `Returns` y `Raises`).
- **Comentarios Funcionales**: Incluir explicaciones claras al inicio de bloques lógicos complejos para facilitar el mantenimiento por otros desarrolladores.
- **Alineación Vertical**: **NO** utilizar alineación vertical por el signo de asignación `=` o `:` en diccionarios y variables. Mantener el formato estándar de PEP8 para evitar diffs innecesarios en Git.
- **Nombrado**: Convención Python estándar (`snake_case` para funciones/variables, `PascalCase` para clases).

---

## 4. 🔄 Flujo de Trabajo en Git y Colaboración

Para mantener la estabilidad de la rama principal (`main`) y garantizar la continuidad en producción:

1. **Ramas de Características**: Todo desarrollo de nuevas funcionalidades o correcciones de bugs debe iniciarse en una rama separada (ej: `feature/nombre-de-la-mejora` o `bugfix/nombre-del-error`).
2. **Pull Requests (PR)**:
   * **Cambios Mayores**: Cualquier cambio que altere el esquema de la base de datos SQLite, modifique la lógica de autenticación del CRM, afecte el pipeline de Docker o reestructure rutas críticas del backend/frontend **DEBE** subirse mediante un Pull Request (PR) al repositorio de GitHub para revisión conjunta antes de fusionarse.
   * **Cambios Menores**: Ajustes de estilo simples, corrección de textos menores o typos en documentación pueden subirse de forma directa a `main` si la rama de producción está estable.
3. **Validación Local**: Siempre levantar el contenedor local en desarrollo (`docker compose -f docker-compose.dev.yml up --build`) y realizar pruebas de flujo de login, registro de leads y navegación antes de confirmar un commit.

---
*Última actualización: Junio 2026 — Agencia Prosper IA*

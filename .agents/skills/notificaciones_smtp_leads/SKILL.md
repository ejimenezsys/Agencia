---
name: Notificaciones SMTP de Leads
description: Guía táctica para la integración y envío seguro de correos electrónicos desde FastAPI ante nuevos prospectos.
---

# 🏢 Habilidad: Notificaciones SMTP de Leads

Esta habilidad contiene las instrucciones y flujos específicos para el mantenimiento, edición y despliegue del sistema de notificaciones automáticas por correo electrónico en **Agencia (Prosper IA)**.

## ⚙️ Estructura del Servido de Plantillas
A diferencia de los sitios estáticos puros, **Agencia** utiliza plantillas HTML dinámicas renderizadas del lado del servidor usando el motor Jinja2:
1. **Templates Dinámicos**: Ubicados en la carpeta `/templates` (ej: vistas del login, dashboard y notificaciones por correo).
2. **Archivos Estáticos**: Ubicados en la carpeta `/static` (CSS corporativo, JS del cliente y logotipos).

---

## 📧 Envío de Correos Electrónicos con SMTP
El backend de FastAPI intercepta las solicitudes de nuevos prospectos en el endpoint de contacto y despacha correos automáticos usando variables de entorno que se inyectan en el [docker-compose.prod.yml](file:///e:/Proyectos/Eduardo/Agencia/docker-compose.prod.yml):
- `SMTP_HOST`: Dirección del servidor SMTP.
- `SMTP_PORT`: Puerto del servidor SMTP (comúnmente 587 para TLS).
- `SMTP_USER`: Cuenta de correo emisora.
- `SMTP_PASSWORD`: Contraseña o clave de aplicación de la cuenta.
- `SMTP_SENDER`: Remitente de las notificaciones.
- `NOTIFICATION_EMAIL`: Correo electrónico del administrador que recibirá las alertas.

---

## ⚠️ Reglas de Oro
1. **Seguridad de Credenciales**: Nunca dejes contraseñas o datos del SMTP hardcodeados en `main.py` u otros archivos. Todas deben ser leídas mediante `os.environ` y configuradas a través del panel de **Coolify** o archivos `.env` locales.
2. **Tareas Asíncronas**: El envío de correos por red puede demorar. Utiliza las tareas en segundo plano (`BackgroundTasks` de FastAPI) para despachar los emails de forma asíncrona sin bloquear la respuesta HTTP al cliente que completa el formulario.
3. **Manejo de Errores (SMTP)**: Envuelve el flujo de conexión al servidor SMTP en bloques `try/except` robustos. Si el servicio SMTP falla o se encuentra desconfigurado en local, el sistema debe registrar el error en logs y guardar el Lead en la base de datos SQLite sin retornar una excepción HTTP 500 al cliente.

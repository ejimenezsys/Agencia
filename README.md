# PROSPER IA — Stack Completo en Python (FastAPI + HTML + CSS)

Este repositorio contiene la migración y consolidación de la landing page y el panel de administración de clientes de **PROSPER IA** a un stack moderno, responsivo y completamente funcional desarrollado en **Python (FastAPI)** con plantillas dinámicas **Jinja2 (HTML/CSS)** y almacenamiento en base de datos portable (in-memory).

---

## 🚀 Características Principales

1. **Backend FastAPI**: Servidor de alto rendimiento que expone APIs REST robustas para autenticación, gestión de leads CRM, estadísticas en tiempo real y perfil de usuario.
2. **Consolidación de Activos**: Todos los archivos de diseño premium (Tailwind CSS, FontAwesome, fuentes Space Grotesk/Inter y librerías Chart.js) se sirven de forma local y óptima desde la ruta `/static`.
3. **CRM de Leads**: Visualización interactiva con filtros dinámicos por estado y origen del lead, adición de nuevos prospectos en caliente con cálculo automático de score e historial de notas, y eliminación segura.
4. **Gráficos Dinámicos**: Los indicadores de rendimiento y los gráficos de barra y donut se actualizan automáticamente en tiempo real basándose en los datos consumidos de la API.
5. **Panel de Ajustes**: Permite modificar la información del perfil y actualizar la contraseña del usuario con almacenamiento persistente en memoria por sesión.

---

## 🛠️ Requisitos e Instalación

### Opción A: Ejecución Local Tradicional

#### 1. Crear y activar un entorno virtual de Python
Se recomienda el uso de `venv` para mantener las dependencias aisladas:

En Windows:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

En macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 2. Instalar dependencias
Instala FastAPI y los módulos requeridos usando `pip`:
```bash
pip install -r requirements.txt
```

#### 3. Ejecutar el Servidor
Inicia el servidor de desarrollo local usando **Uvicorn** con recarga automática:
```bash
uvicorn main:app --reload
```

---

### Opción B: Ejecución con Docker (Recomendado para Dev/Prod)

Hemos configurado entornos independientes utilizando Docker Compose:

#### 1. Modo Desarrollo (Hot Reload + Volumen Local)
Levanta la aplicación montando tu código local en tiempo real dentro del contenedor. Cualquier cambio que hagas en el código activará la recarga automática.

```bash
docker compose -f docker-compose.dev.yml up --build
```
* La base de datos local de desarrollo se guardará de forma persistente en `./data/prosper_ia_dev.db`.

#### 2. Modo Producción
Levanta la aplicación optimizada sin recarga automática y con almacenamiento persistente administrado por Docker.

```bash
# Recuerda configurar o inyectar tus variables SMTP en el entorno
docker compose -f docker-compose.prod.yml up -d --build
```
* La base de datos de producción persistirá de forma segura en el volumen de Docker con nombre `prosper_ia_prod_data`.

---

## ⚙️ Acceso a la Aplicación

Una vez que el servidor esté activo (por cualquiera de los métodos), navega en tu navegador a:
- 🔗 **Landing Page / Inicio**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- 🔑 **Portal de Acceso / Login**: [http://127.0.0.1:8000/login](http://127.0.0.1:8000/login)
- 📊 **Panel de Clientes / Dashboard**: [http://127.0.0.1:8000/dashboard](http://127.0.0.1:8000/dashboard)

---

## 👤 Credenciales de Acceso Predeterminadas

Usa la siguiente cuenta administradora configurada en el sistema para iniciar sesión de inmediato:
- **Correo Electrónico**: `admin@prosperia.com`
- **Contraseña**: `admin1234`

---

## 📂 Estructura del Proyecto

```text
sitiosweb/
├── static/                   # Recursos estáticos globales localizados
│   ├── tw.css                # Compilación Tailwind CSS optimizada
│   ├── fa.min.css            # Iconografía completa FontAwesome
│   ├── fonts.css             # Tipografía Space Grotesk e Inter
│   ├── chart.min.js          # Librería de gráficos interactivos Chart.js
│   └── webfonts/             # Archivos WOFF/WOFF2 para iconos locales
├── templates/                # Plantillas HTML dinámicas procesadas por Jinja2
│   ├── index.html            # Landing page principal
│   ├── login.html            # Portal de acceso seguro
│   └── dashboard.html        # Panel interactivo de gestión CRM y métricas
├── main.py                   # Núcleo del servidor FastAPI, API endpoints y Mock DB
├── requirements.txt          # Dependencias oficiales del entorno Python
└── README.md                 # Guía y manual de usuario actual
```

---

## 📊 Endpoints de la API REST

| Método | Ruta | Descripción |
| :--- | :--- | :--- |
| **POST** | `/api/auth/login` | Inicia sesión del usuario y crea cookie de sesión activa. |
| **POST** | `/api/auth/logout` | Cierra sesión activa y remueve cookies. |
| **GET** | `/api/users/me` | Obtiene los detalles de perfil del usuario autenticado. |
| **PUT** | `/api/users/me` | Actualiza la información de contacto y empresa del perfil. |
| **PUT** | `/api/users/me/password` | Cambia de forma segura la contraseña del usuario. |
| **GET** | `/api/leads` | Lista los leads registrados. Soporta filtros `status`, `source` y `limit`. |
| **POST** | `/api/leads` | Registra un nuevo lead con asignación automática de ID y timestamp. |
| **DELETE** | `/api/leads/{id}` | Elimina un lead específico del sistema CRM en memoria. |
| **GET** | `/api/dashboard/stats` | Retorna métricas agregadas (leads totales, ingresos estimados, tasa conversión). |

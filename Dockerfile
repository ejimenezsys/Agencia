# Usar una imagen oficial de Python ligera
FROM python:3.11-slim

# Evitar que Python escriba archivos .pyc en el disco
ENV PYTHONDONTWRITEBYTECODE=1
# Evitar que Python almacene en búfer stdout y stderr
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo en el contenedor
WORKDIR /app

# Crear el directorio para los datos persistentes de la base de datos
RUN mkdir -p /app/data

# Instalar dependencias del sistema necesarias para construir ciertas librerías (si aplica)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar el archivo de requerimientos e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código de la aplicación
COPY . .

# Definir variables de entorno por defecto
# Indicamos que la base de datos SQLite se guarde en el volumen persistente
ENV DATABASE_PATH=/app/data/prosper_ia.db
ENV PORT=8000

# Exponer el puerto en el contenedor
EXPOSE 8000

# Comando para ejecutar la aplicación con Uvicorn en producción
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]

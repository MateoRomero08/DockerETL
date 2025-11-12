# Imagen base ligera con Python
FROM python:3.10-slim

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Crear carpeta de trabajo
WORKDIR /app

# Copiar archivos de dependencias primero
COPY requirements.txt .

# Instalar dependencias
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copiar el resto del proyecto
COPY . .

# Comando por defecto al ejecutar el contenedor
CMD ["python", "main.py"]
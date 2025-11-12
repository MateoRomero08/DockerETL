# DockerETL
# 🚀 Proyecto Docker-Python

Este repositorio contiene un contenedor Docker básico para ejecutar código Python.

## Cómo usarlo

### 1️⃣ Construir la imagen
```bash
docker build -t mi_app_python .
# docker-file-para-python
```

Proyecto: docker-python-app

Descripción
Este proyecto contiene una aplicación Python dockerizada que realiza un proceso ETL simple:
- Lee el primer dataset disponible desde la carpeta `data/` (formatos: csv, tsv, parquet, xlsx).
- Ejecuta limpieza y normalización de columnas.
- Guarda el dataset limpio en `data/cleaned_dataset.csv` y muestra un resumen en la salida estándar.

Estructura relevante
- /app (directorio de trabajo dentro del contenedor)
- data/  <- Carpeta donde debes subir tu CSV (ruta en el workspace: /workspaces/docker-file-para-python/docker-python-app/data)
- main.py (ejecuta el ETL)
- Dockerfile
- requirements.txt

Cómo usar (local / con Docker)
1) Crear la carpeta de datos y copiar el CSV:
   mkdir -p data
   cp /ruta/tu_dataset.csv data/

2) Ejecutar con Docker (montando la carpeta data para usar archivos locales):
   cd /workspaces/docker-file-para-python/docker-python-app
   docker build -t docker-python-app .
   docker run --rm -v "$(pwd)/data:/app/data" docker-python-app

3) Ejecutar localmente sin Docker:
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   python main.py

Guardar cambios en control de versiones
   git add .
   git commit -m "Agregar ETL, README y dependencias"
   git push origin main   # ajustar rama/remoto según corresponda

Preparar imagen para subir a un servidor

Opción A — Subir a un registro (Docker Hub / registry):
   docker login
   docker build -t docker-python-app .
   docker tag docker-python-app <REGISTRO>/<USUARIO>/<REPO>:<TAG>
   docker push <REGISTRO>/<USUARIO>/<REPO>:<TAG>

Reemplazar <REGISTRO> por `docker.io` o el registro que uses, y <USUARIO>/<REPO>:<TAG> por tu destino.

Opción B — Enviar imagen al servidor por SCP (si no usas registry):
   # Guardar imagen en un tar
   docker build -t docker-python-app .
   docker save -o docker-python-app.tar docker-python-app

   # Copiar al servidor (reemplazar user@server:/ruta/destino)
   scp docker-python-app.tar user@server:/ruta/destino

   # En el servidor:
   ssh user@server
   docker load -i /ruta/destino/docker-python-app.tar
   docker run --rm -v /ruta/datos:/app/data docker-python-app

Notas
- Asegúrate de que `data/` esté montada o incluida en la imagen si quieres que el CSV esté disponible dentro del contenedor.
- Ajusta nombres de imagen, usuario y servidor según tu flujo de despliegue.
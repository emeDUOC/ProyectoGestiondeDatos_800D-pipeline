FROM python:3.12-slim

# Instalar uv en el sistema para la gestión rápida de paquetes
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copiar el archivo de configuración de dependencias
COPY pyproject.toml /app/

# Instalar las librerías necesarias directamente en el sistema del contenedor
RUN uv pip install --system -r pyproject.toml

# Copiar todo el código de nuestro proyecto dentro del contenedor
COPY . /app

# Comando por defecto que se ejecuta al encender el contenedor
CMD ["python", "main.py"]
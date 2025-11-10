FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias del sistema necesarias para Pillow y otras libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero para aprovechar la cache de Docker
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copiar la app
COPY . /app/

ENV DJANGO_SETTINGS_MODULE=gaon.settings

# Crear carpeta media (opcional)
RUN mkdir -p /app/media

# Copiar entrypoint
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]

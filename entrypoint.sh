#!/bin/sh
set -e

# Esperar si hace falta (opcional: útil si la DB tarda en provisionarse)
# sleep 2

echo "[entrypoint] Ejecutando migraciones..."
python manage.py migrate --noinput

echo "[entrypoint] Collect static..."
python manage.py collectstatic --noinput || true

echo "[entrypoint] Lanzando Gunicorn..."
exec gunicorn gaon.wsgi:application --bind 0.0.0.0:8000 --workers 3

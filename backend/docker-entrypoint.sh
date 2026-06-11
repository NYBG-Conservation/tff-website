#!/bin/sh
set -e

export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-config.settings.prod}"

echo "Running migrations..."
python backend/manage.py migrate --noinput

echo "Collecting static files..."
python backend/manage.py collectstatic --noinput

echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application \
  --chdir backend \
  --bind "0.0.0.0:${PORT:-8000}" \
  --workers "${GUNICORN_WORKERS:-2}" \
  --timeout 120

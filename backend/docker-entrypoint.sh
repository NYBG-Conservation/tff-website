#!/bin/sh
set -e

export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-config.settings.prod}"

echo "Running migrations..."
python backend/manage.py migrate --noinput

echo "Collecting static files..."
python backend/manage.py collectstatic --noinput

echo "Starting Gunicorn..."
# 2 sync-ish processes × 2 threads covers overlapping RDS/SMTP I/O without extra RAM.
# Recycle workers periodically so a slow leak cannot pin the t3 instance.
exec gunicorn config.wsgi:application \
  --chdir backend \
  --bind "0.0.0.0:${PORT:-8000}" \
  --workers "${GUNICORN_WORKERS:-2}" \
  --threads "${GUNICORN_THREADS:-2}" \
  --timeout "${GUNICORN_TIMEOUT:-120}" \
  --keep-alive "${GUNICORN_KEEPALIVE:-5}" \
  --max-requests "${GUNICORN_MAX_REQUESTS:-500}" \
  --max-requests-jitter "${GUNICORN_MAX_REQUESTS_JITTER:-50}"

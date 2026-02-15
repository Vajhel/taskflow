#!/bin/bash
set -e

echo "Применение миграций frontend..."
python manage.py migrate --noinput

echo "Запуск frontend..."
exec gunicorn frontend.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 120

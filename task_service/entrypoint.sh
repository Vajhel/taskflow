#!/bin/bash
set -e

echo "Ожидание готовности PostgreSQL..."
while ! python -c "import psycopg2; psycopg2.connect(dbname='$DB_NAME', user='$DB_USER', password='$DB_PASSWORD', host='$DB_HOST', port='$DB_PORT')" 2>/dev/null; do
    echo "PostgreSQL недоступен, повторная попытка через 2 секунды..."
    sleep 2
done
echo "PostgreSQL готов!"

echo "Генерация миграций..."
python manage.py makemigrations tasks --noinput

echo "Применение миграций..."
python manage.py migrate --noinput

echo "Запуск task_service..."
exec gunicorn task_service.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 120

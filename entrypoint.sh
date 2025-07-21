#!/bin/bash
set -e

echo "⌛ Ждём базу данных..."
/wait-for-it.sh db:5432 --timeout=30 --strict -- echo "✅ DB готова"

echo "🔄 Миграции..."
python manage.py migrate

echo "📦 Collect static..."
python manage.py collectstatic --noinput

echo "🔥 Запуск сервера Django (dev)..."
exec python manage.py runserver 0.0.0.0:8000

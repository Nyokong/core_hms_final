#!/bin/ash

echo "Make database migrations"
python manage.py makemigrations

echo "Apply database migrations"
python manage.py migrate

echo "collect static"
python manage.py collectstatic

exec "$@"

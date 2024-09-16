#!/bin/ash

echo "Make database migrations"
python manage.py makemigrations api

echo "Apply database migrations"
python manage.py migrate

exec "$@"

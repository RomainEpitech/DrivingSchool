#!/bin/sh
echo "Waiting for database..."
sleep 5

mkdir -p /app/data/logs

echo "Checking project structure..."
ls -la /app/

python manage.py migrate

python manage.py loaddata initial_data

echo "Starting server..."
exec "$@"
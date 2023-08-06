#!/bin/bash

# Запуск миграций
python manage.py migrate

# Сборка статики
python manage.py collectstatic --noinput

# Запуск сервера
exec "$@"
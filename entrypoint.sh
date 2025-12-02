#!/bin/bash

# Применяем миграции базы данных
echo "Applying database migrations..."
alembic upgrade head

# Запуск бота
echo "Starting bot..."
python -m src.main
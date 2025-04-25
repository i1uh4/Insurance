#!/bin/bash

# Инициализация Alembic (если еще не инициализирован)
python init_alembic.py

# Создание начальной миграции (если нет миграций)
if [ ! -d "migrations/versions" ] || [ -z "$(ls -A migrations/versions)" ]; then
    python create_initial_migration.py
fi

# Применение миграций
python apply_migrations.py

# Запуск отслеживания изменений в фоновом режиме
python watch_changes.py &
WATCH_PID=$!

# Запуск основного приложения
uvicorn main:app --host 0.0.0.0 --port 8001 --reload --reload-dir /app

# Завершение фонового процесса при выходе
kill $WATCH_PID
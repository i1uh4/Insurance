#!/bin/bash

echo "Running service migrations..."
cd /app
alembic revision --autogenerate -m "$1"
alembic upgrade head
echo "Migrations completed successfully!"
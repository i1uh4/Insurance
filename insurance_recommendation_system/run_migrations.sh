#!/bin/bash

echo "Running database migrations..."
cd /app
alembic revision --autogenerate -m "$1"
alembic upgrade head
echo "Migrations completed successfully!"
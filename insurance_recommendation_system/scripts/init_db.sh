#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
until PGPASSWORD=postgres psql -h db -U postgres -d postgres -c '\q'; do
  >&2 echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

# Run migrations
echo "Running database migrations..."
alembic upgrade head

echo "Database initialization completed!"
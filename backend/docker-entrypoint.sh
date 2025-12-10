#!/bin/bash
set -e

echo "Starting Backend entrypoint script..."

# Wait for PostgreSQL
echo "Waiting for PostgreSQL..."
until pg_isready -h postgres -U telegram_monitor -d telegram_monitor > /dev/null 2>&1; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done
echo "PostgreSQL is up!"

# Wait for Redis
echo "Waiting for Redis..."
until redis-cli -h redis ping > /dev/null 2>&1; do
  echo "Redis is unavailable - sleeping"
  sleep 2
done
echo "Redis is up!"

# Run database migrations
echo "Running database migrations..."
alembic upgrade head
echo "Migrations completed!"

# Execute the main command
echo "Starting application: $@"
exec "$@"

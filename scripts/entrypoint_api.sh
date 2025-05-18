#!/usr/bin/env bash
set -euo pipefail

# Run database migrations
echo "Running Alembic migrations..."
poetry run alembic upgrade head

# Execute the CMD
echo "Starting application..."
exec "$@" 
#!/bin/bash
# Database migration script for use with distroless containers
# This can be run as an init container or before starting the main application

set -e

echo "Starting database migration process..."

# Wait for database if configured
if [ -n "$REVIEWPOINT_DB_URL" ]; then
    echo "Waiting for database to be ready..."
    until pg_isready -h $(echo $REVIEWPOINT_DB_URL | sed "s/.*@\([^:]*\):.*/\1/") -p $(echo $REVIEWPOINT_DB_URL | sed "s/.*:\([0-9]*\)\/.*/\1/") -U postgres; do
        echo "Database is unavailable - sleeping"
        sleep 2
    done
    echo "Database is ready!"
fi

# Run database migrations if alembic.ini exists
if [ -f alembic.ini ]; then
    echo "Running database migrations..."
    alembic upgrade head
    echo "Database migrations completed successfully!"
else
    echo "No alembic.ini found, skipping migrations"
fi

echo "Migration process completed!"

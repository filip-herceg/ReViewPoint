#!/bin/bash
# backend/docker/docker-entrypoint.sh
set -e

# Wait for database to be ready
if [ -n "$REVIEWPOINT_DB_URL" ]; then
    echo "Waiting for database to be ready..."
    until pg_isready -h $(echo $REVIEWPOINT_DB_URL | sed 's/.*@\([^:]*\):.*/\1/') -p $(echo $REVIEWPOINT_DB_URL | sed 's/.*:\([0-9]*\)\/.*/\1/') -U postgres; do
        echo "Database is unavailable - sleeping"
        sleep 2
    done
    echo "Database is ready!"
fi

# Run database migrations
if [ -f alembic.ini ]; then
    echo "Running database migrations..."
    alembic upgrade head
fi

# Execute the main command
exec "$@"

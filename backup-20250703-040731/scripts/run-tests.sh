#!/bin/bash
# scripts/run-tests.sh
set -e

# Clean up and recreate the test database before running tests
/app/scripts/cleanup-test-db.sh reviewpoint_test postgres postgres_test 5432 postgres

echo "Waiting for PostgreSQL to be ready..."
/app/scripts/wait-for-postgres.sh postgres_test 5432

echo "Running database migrations..."
cd /app
export PYTHONPATH=/app/src
poetry run alembic upgrade head

echo "Running tests..."
poetry run pytest -v --cov=src --cov-report=html --cov-report=term-missing

echo "Tests completed successfully!"

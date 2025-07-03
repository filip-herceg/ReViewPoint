# scripts/cleanup-test-db.sh
# This script drops and recreates the test database for a clean test run.

set -e

DB_NAME=${1:-reviewpoint_test}
DB_USER=${2:-postgres}
DB_HOST=${3:-localhost}
DB_PORT=${4:-5432}

export PGPASSWORD=${5:-postgres}

# Drop the test database if it exists
psql -h "$DB_HOST" -U "$DB_USER" -p "$DB_PORT" -c "DROP DATABASE IF EXISTS $DB_NAME WITH (FORCE);"
# Recreate the test database
psql -h "$DB_HOST" -U "$DB_USER" -p "$DB_PORT" -c "CREATE DATABASE $DB_NAME;"

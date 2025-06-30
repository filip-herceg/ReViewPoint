#!/bin/bash
# scripts/wait-for-postgres.sh
set -e
host="$1"
port="$2"
shift 2
cmd="$@"

until pg_isready -h "$host" -p "$port" -U postgres; do
  >&2 echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

>&2 echo "PostgreSQL is up - executing command"
exec $cmd

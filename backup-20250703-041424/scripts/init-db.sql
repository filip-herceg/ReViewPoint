-- scripts/init-db.sql
-- This script ensures the test database exists and grants privileges

DO
$do$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'reviewpoint_test') THEN
      PERFORM dblink_exec('dbname=' || current_database(), 'CREATE DATABASE reviewpoint_test');
   END IF;
END
$do$;

GRANT ALL PRIVILEGES ON DATABASE reviewpoint TO postgres;
GRANT ALL PRIVILEGES ON DATABASE reviewpoint_test TO postgres;

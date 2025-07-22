# Alembic Migrations

This directory contains the Alembic database migration configuration and scripts for the ReViewPoint backend application.

## Overview

Alembic is the database migration tool used by SQLAlchemy. It provides a way to manage database schema changes over time in a version-controlled manner. This configuration is set up for a single-database environment.

## Directory Structure

```
alembic_migrations/
├── README              # Generic single-database configuration note
├── env.py             # Alembic environment configuration
├── script.py.mako     # Template for new migration scripts
├── versions/          # Directory containing migration files
│   ├── f140e6f46727_initial_migration.py
│   ├── 31eb30e5f037_add_file_size_field.py
│   └── 20250605_add_used_password_reset_tokens.py
└── __init__.py
```

## Configuration

The Alembic configuration is defined in `alembic.ini` at the backend root, which points to this directory as the script location:

```ini
script_location = src/alembic_migrations
```

## Key Files

### env.py
Contains the Alembic environment configuration that:
- Connects to the database using SQLAlchemy
- Configures the migration context
- Handles both online and offline migration modes

### script.py.mako
A Mako template used to generate new migration files. It provides the standard structure for migration scripts including:
- Revision metadata
- Import statements
- Upgrade and downgrade functions

### versions/
Contains all migration files in chronological order. Each migration file includes:
- Unique revision ID
- Reference to previous migration
- Upgrade operations (schema changes)
- Downgrade operations (rollback changes)

## Usage

### Creating New Migrations

From the backend directory:

```bash
# Auto-generate migration from model changes
python -m alembic revision --autogenerate -m "description of changes"

# Create empty migration file
python -m alembic revision -m "description of changes"
```

### Running Migrations

```bash
# Apply all pending migrations
python -m alembic upgrade head

# Apply specific migration
python -m alembic upgrade [revision_id]

# Rollback to previous migration
python -m alembic downgrade -1

# Rollback to specific migration
python -m alembic downgrade [revision_id]
```

### Migration History

```bash
# Show current migration status
python -m alembic current

# Show migration history
python -m alembic history

# Show pending migrations
python -m alembic heads
```

## Migration Files

### f140e6f46727_initial_migration.py
The initial database schema migration that creates all base tables including:
- `blacklisted_tokens` - JWT token blacklist
- `users` - User accounts
- `file_metadata` - File upload metadata
- `user_sessions` - User session tracking

### 31eb30e5f037_add_file_size_field.py
Adds file size tracking to the file metadata table for better storage management.

### 20250605_add_used_password_reset_tokens.py
Adds tracking for used password reset tokens to prevent token reuse and improve security.

## Best Practices

1. **Always review auto-generated migrations** before applying them
2. **Test migrations on a copy of production data** before deployment
3. **Include both upgrade and downgrade operations** for reversibility
4. **Use descriptive names** for migration files
5. **Keep migrations atomic** - each migration should represent a single logical change
6. **Backup database** before running migrations in production

## Database Support

The migration system supports multiple database backends:
- PostgreSQL (production)
- SQLite (development/testing)

The specific database URL is configured via environment variables or the `alembic.ini` file.
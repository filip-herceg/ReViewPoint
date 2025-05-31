# `alembic_migrations/versions/9fc3acc47815_initial_migration_users_and_files_tables.py`

| Item | Value |
|------|-------|
| **Layer** | Database Migration |
| **Responsibility** | Initial database schema creation for User and File tables |
| **Status** | 🟢 Done |

## 1. Purpose  
This is the initial migration file that sets up the core database schema including the `users` and `files` tables. It establishes the foundation for user authentication and file metadata storage.

## 2. Migration Details  

**Revision ID**: `9fc3acc47815`  
**Down Revision**: None (This is the first migration)  
**Created**: 2025-05-20 03:45:35.116822

## 3. Schema Changes  

This migration:

1. Creates the `users` table with:
   - `email`: String(255), indexed with uniqueness constraint
   - `hashed_password`: String(255)
   - `is_active`: Boolean
   - `id`: Integer (primary key)
   - `created_at`: DateTime
   - `updated_at`: DateTime

2. Creates the `files` table with:
   - `filename`: String(255)
   - `content_type`: String(128)
   - `user_id`: Integer (foreign key to users.id)
   - `id`: Integer (primary key)
   - `created_at`: DateTime
   - `updated_at`: DateTime

3. Adds indexes:
   - `ix_users_email` on `users.email` (unique)
   - `ix_files_user_id` on `files.user_id` (non-unique)

4. Establishes foreign key:
   - `files.user_id` references `users.id`

## 4. Upgrade & Downgrade  

- **Upgrade**: Creates tables, indexes, and constraints
- **Downgrade**: Drops all created objects in reverse order

## 5. Dependencies  

- **Internal**: None
  
- **External**:
  - `alembic`: For migration framework
  - `sqlalchemy`: For schema definition

## 6. Notes  
This initial migration forms the foundation of the database and must be run before any application use. Future migrations will build upon this schema.

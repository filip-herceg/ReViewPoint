# `alembic_migrations/versions/9fc3acc47815_initial_migration_users_and_files_tables.py`

| Item               | Value                                                     |
| ------------------ | --------------------------------------------------------- |
| **Layer**          | Database Migration                                        |
| **Responsibility** | Initial database schema creation for User and File tables |
| **Status**         | 🟢 Done                                                   |

## 1. Purpose

This is the initial migration file that sets up the core database schema including the `users` and `files` tables. It establishes the foundation for user authentication and file metadata storage.

## 2. Migration Details

**Revision ID**: `9fc3acc47815`  
**Down Revision**: None (This is the first migration)

## 3. Schema Changes

This migration:

- Creates the `users` table with:
  - `email`: String(255), indexed, unique
  - `hashed_password`: String(255)
  - `is_active`: Boolean
  - `id`: Integer (primary key)
  - `created_at`: DateTime
  - `updated_at`: DateTime
- Creates the `files` table with:
  - `filename`: String(255)
  - `content_type`: String(128)
  - `user_id`: Integer (foreign key to users.id)
  - `id`: Integer (primary key)
  - `created_at`: DateTime
  - `updated_at`: DateTime

# `alembic_migrations/versions/f140e6f46727_initial_migration.py`

| Item               | Value                                                              |
| ------------------ | ------------------------------------------------------------------ |
| **Layer**          | Database Migration                                                 |
| **Responsibility** | Initial database schema creation for the ReViewPoint platform     |
| **Status**         | 🟢 Done                                                            |

## 1. Purpose

This is the foundational Alembic migration that creates the initial database schema for ReViewPoint, establishing the core tables and relationships required for user management and file operations.

## 2. Migration Details

| Item       | Value                            |
| ---------- | -------------------------------- |
| **Revision ID** | f140e6f46727                |
| **Revises**     | None (initial migration)        |
| **Created**     | Auto-generated migration        |
| **Operation**   | Create initial schema           |

## 3. Schema Creation

### Tables Created

#### Users Table
- `id`: Primary key (UUID)
- `email`: Unique email address
- `hashed_password`: Encrypted password storage
- `is_active`: Account status flag
- `created_at`: Timestamp of account creation
- `updated_at`: Timestamp of last modification

#### Files Table
- `id`: Primary key (UUID)
- `filename`: Original filename
- `content_type`: MIME type of the file
- `user_id`: Foreign key to users table
- `created_at`: Upload timestamp
- `updated_at`: Last modification timestamp

### Indexes Created
- Unique index on `users.email`
- Index on `files.user_id` for efficient user file queries

### Relationships
- Files table has foreign key relationship to users table
- One-to-many relationship: one user can have multiple files

## 4. SQL Schema

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Files table  
CREATE TABLE files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename VARCHAR(255) NOT NULL,
    content_type VARCHAR(100),
    user_id UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE UNIQUE INDEX ix_users_email ON users(email);
CREATE INDEX ix_files_user_id ON files(user_id);
```

## 5. Dependencies

- **Database**: PostgreSQL or SQLite
- **SQLAlchemy**: ORM models must match this schema
- **Alembic**: Migration framework for schema management

## 6. Usage

This migration is applied automatically when setting up a new ReViewPoint instance:

```bash
# Apply initial migration
alembic upgrade head
```

## 7. Post-Migration

After this migration:
- User registration and authentication become available
- File upload functionality is enabled
- Basic CRUD operations on users and files are supported

## 8. Notes

- This migration cannot be rolled back as it's the initial schema
- All subsequent migrations build upon this foundation
- The schema supports both PostgreSQL (production) and SQLite (development)

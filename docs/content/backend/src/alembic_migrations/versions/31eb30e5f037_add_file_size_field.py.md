# `alembic_migrations/versions/31eb30e5f037_add_file_size_field.py`

| Item               | Value                                                              |
| ------------------ | ------------------------------------------------------------------ |
| **Layer**          | Database Migration                                                 |
| **Responsibility** | Adds file size field to files table for storage tracking          |
| **Status**         | 🟢 Done                                                            |

## 1. Purpose

This Alembic migration adds a `file_size` field to the files table to track the size of uploaded files in bytes. This enables better storage management, quota enforcement, and usage analytics.

## 2. Migration Details

| Item       | Value                            |
| ---------- | -------------------------------- |
| **Revision ID** | 31eb30e5f037                |
| **Revises**     | Previous migration revision     |
| **Created**     | Auto-generated migration        |
| **Operation**   | Add column `file_size` (BigInteger) |

## 3. Schema Changes

### Added Fields
- `file_size`: BigInteger field to store file size in bytes
- Nullable: True (to handle existing records)
- Default: None

### SQL Operations
```sql
-- Add file_size column to files table
ALTER TABLE files ADD COLUMN file_size BIGINT;
```

## 4. Dependencies

- **Previous Migration**: Depends on initial files table migration
- **SQLAlchemy Models**: Updates File model to include file_size field
- **Storage Service**: Integrates with upload service to capture file sizes

## 5. Usage

This migration is automatically applied when running:
```bash
alembic upgrade head
```

The file_size field is populated by the upload service when new files are uploaded and can be backfilled for existing files if needed.

## 6. Rollback

To rollback this migration:
```bash
alembic downgrade -1
```

This will remove the file_size column from the files table.

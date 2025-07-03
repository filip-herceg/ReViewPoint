# `alembic_migrations/versions/20250605_add_used_password_reset_tokens.py`

| Item               | Value                                                        |
| ------------------ | ------------------------------------------------------------ |
| **Layer**          | Database Migration                                           |
| **Responsibility** | Adds a table for one-time-use password reset tokens         |
| **Status**         | 🟢 Done                                                      |

## 1. Purpose

This migration adds the `used_password_reset_tokens` table to track tokens that have been used for password resets, ensuring each token is only used once.

## 2. Migration Details

**Revision ID**: `20250605_add_used_password_reset_tokens`

## 3. Schema Changes

- Creates the `used_password_reset_tokens` table with:
  - `id`: Integer, primary key
  - `email`: String(255), indexed
  - `nonce`: String(64), indexed
  - `used_at`: DateTime, defaults to now
- Adds indexes on `email` and `nonce`

## 4. Downgrade

- Drops the indexes and the table if the migration is reversed.

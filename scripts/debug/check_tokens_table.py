#!/usr/bin/env python3
"""Check for indexes related to used_password_reset_tokens."""

import psycopg2


def main() -> None:
    conn: psycopg2.extensions.connection = psycopg2.connect(
        "postgresql://postgres:postgres@localhost:5432/reviewpoint"
    )
    cursor: psycopg2.extensions.cursor = conn.cursor()

    # Check for indexes containing 'used_password_reset_tokens'
    cursor.execute(
        """
        SELECT schemaname, tablename, indexname
        FROM pg_indexes
        WHERE indexname LIKE '%used_password_reset_tokens%';
    """
    )

    print("Indexes containing 'used_password_reset_tokens':")
    index_rows = cursor.fetchall()
    for row in index_rows:
        schemaname: str = row[0]
        tablename: str = row[1]
        indexname: str = row[2]
        print(f"  Schema: {schemaname}, Table: {tablename}, Index: {indexname}")

    # Check for the specific table
    cursor.execute(
        """
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name = 'used_password_reset_tokens'
        );
    """
    )
    result = cursor.fetchone()
    table_exists: bool = (
        bool(result[0]) if result is not None and len(result) > 0 else False
    )
    print(f"used_password_reset_tokens table exists: {table_exists}")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()

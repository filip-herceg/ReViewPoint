#!/usr/bin/env python3
"""Check the alembic_version table structure."""

import psycopg2


def main() -> None:
    conn: psycopg2.extensions.connection = psycopg2.connect(
        "postgresql://postgres:postgres@localhost:5432/reviewpoint"
    )
    cursor: psycopg2.extensions.cursor = conn.cursor()

    # Check the table structure
    cursor.execute(
        """
        SELECT column_name, data_type, character_maximum_length
        FROM information_schema.columns
        WHERE table_name = 'alembic_version' AND table_schema = 'public';
    """
    )

    print("alembic_version table structure:")
    columns = cursor.fetchall()
    for row in columns:
        column_name: str = row[0]
        data_type: str = row[1]
        max_length: int | None = row[2]
        print(f"  Column: {column_name}, Type: {data_type}, Max Length: {max_length}")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()

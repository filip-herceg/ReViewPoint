#!/usr/bin/env python3
"""Check the current state of the PostgreSQL database and Alembic version tracking."""

import psycopg2

from src.core.config import get_settings


def main() -> None:
    # Get the sync DB URL for direct connection
    settings = get_settings()
    db_url = settings.db_url
    print(f"Database URL: {db_url}")

    if not db_url:
        print("Error: No database URL configured")
        return

    # Convert async URL to sync for psycopg2
    sync_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
    print(f"Sync URL: {sync_url}")

    # Connect and check tables
    try:
        conn = psycopg2.connect(sync_url)
        cursor = conn.cursor()

        # Check if alembic_version table exists
        cursor.execute(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'alembic_version'
            );
        """
        )
        result = cursor.fetchone()
        alembic_exists = result[0] if result else False
        print(f"Alembic version table exists: {alembic_exists}")

        if alembic_exists:
            cursor.execute("SELECT version_num FROM alembic_version;")
            version_result = cursor.fetchone()
            print(
                f'Current alembic version: {version_result[0] if version_result else "None"}'
            )

        # List all tables
        cursor.execute(
            """
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """
        )
        tables = cursor.fetchall()
        print(f"All tables: {[t[0] for t in tables]}")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()

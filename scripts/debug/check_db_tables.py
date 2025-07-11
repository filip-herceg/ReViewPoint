#!/usr/bin/env python3
"""Check database tables and structure"""

import sys

sys.path.append("../../backend")
sys.path.append("../../")

import asyncio

from sqlalchemy import text


async def check_database():
    try:
        from backend.src.core.database import get_async_session

        async with get_async_session() as session:
            print("=== Database Connection Test ===")

            # Test basic connection
            result = await session.execute(text("SELECT 1"))
            print("Database connection: OK")

            # Check if users table exists (PostgreSQL)
            result = await session.execute(
                text(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema = 'public' AND table_name = 'users'",
                ),
            )
            table_exists = result.scalar() is not None
            print(f"Users table exists: {table_exists}")

            if table_exists:
                # Check table structure
                result = await session.execute(
                    text(
                        "SELECT column_name, data_type, is_nullable "
                        "FROM information_schema.columns "
                        "WHERE table_schema = 'public' AND table_name = 'users' "
                        "ORDER BY ordinal_position",
                    ),
                )
                columns = result.fetchall()
                print("\nUsers table columns:")
                for col in columns:
                    print(f"  {col[0]} {col[1]} (nullable: {col[2] == 'YES'})")
            else:
                print("\n❌ Users table does not exist!")
                print("This is likely the cause of the 500 error.")
                print("Run migrations to create the table.")

            # List all tables in public schema
            result = await session.execute(
                text(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema = 'public' ORDER BY table_name",
                ),
            )
            tables = result.fetchall()
            print(f"\nExisting tables in 'public' schema ({len(tables)}):")
            for table in tables:
                print(f"  - {table[0]}")

            # Check if alembic migration table exists
            result = await session.execute(
                text(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema = 'public' AND table_name = 'alembic_version'",
                ),
            )
            alembic_exists = result.scalar() is not None
            print(f"\nAlembic version table exists: {alembic_exists}")

            if alembic_exists:
                result = await session.execute(
                    text("SELECT version_num FROM alembic_version"),
                )
                version = result.scalar()
                print(f"Current migration version: {version if version else 'None'}")
            else:
                print("❌ No alembic version table found - migrations not initialized!")

    except Exception as e:
        print(f"❌ Database check failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = asyncio.run(check_database())
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""Debug user creation errors by testing the user service directly."""

import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Import backend modules
from src.core.database import get_async_session
from src.schemas.user import UserCreate
from src.services.user import UserService


async def test_user_creation():
    """Test user creation directly to see the error."""
    print("=== Debug User Creation ===")

    # Test data
    user_data = UserCreate(
        email="debug.test@example.com",
        password="TestPassword123!",
        name="Debug Test User",
    )

    try:
        # Get database session
        print("Getting database session...")
        async for db in get_async_session():
            print("Creating user service...")
            user_service = UserService(db)

            print(f"Attempting to create user: {user_data.email}")
            try:
                result = await user_service.create_user_with_validation(user_data)
                print(f"✅ User created successfully: {result}")
                return result
            except Exception as e:
                print(f"❌ User creation failed: {type(e).__name__}: {e}")
                import traceback

                traceback.print_exc()
                return None
            finally:
                await db.close()

    except Exception as e:
        print(f"❌ Database connection failed: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = asyncio.run(test_user_creation())
    if result:
        print(f"Final result: {result}")

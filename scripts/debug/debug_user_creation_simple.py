#!/usr/bin/env python3
"""Test user creation with better error handling."""

import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))


async def test_user_creation():
    """Test user creation directly."""
    print("=== Test User Creation ===")

    try:
        from src.core.database import get_async_session
        from src.repositories.user import create_user_with_validation

        # Get a database session
        async for session in get_async_session():
            try:
                print("Testing user creation...")
                result = await create_user_with_validation(
                    session,
                    "debug.test@example.com",
                    "TestPassword123!",
                    "Debug Test User",
                )
                print(f"✅ User created: {result}")

            except Exception as e:
                print(f"❌ User creation error: {type(e).__name__}: {e}")
                import traceback

                traceback.print_exc()
            break  # Only use one session

    except Exception as e:
        print(f"❌ Setup error: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_user_creation())

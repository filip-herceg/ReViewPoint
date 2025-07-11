#!/usr/bin/env python3

"""
Create Test User Script

Creates a test user for WebSocket testing when registration is disabled.
"""

import asyncio
import sys
import os

# Add the backend directory to Python path
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

from src.core.database import get_async_session
from src.repositories.user import create_user_with_validation


async def create_test_user():
    """Create a test user for WebSocket testing."""
    print("🔧 Creating test user for WebSocket testing...")
    
    try:
        # Get database session
        async with get_async_session() as session:
            try:
                # Create test user
                user = await create_user_with_validation(
                    session=session,
                    email="test@example.com",
                    password="testpassword123",
                    name="Test User"
                )
                
                print(f"✅ Test user created successfully!")
                print(f"📧 Email: {user.email}")
                print(f"👤 Name: {user.name}")
                print(f"🆔 ID: {user.id}")
                print(f"🔑 You can now log in with:")
                print(f"   Email: test@example.com")
                print(f"   Password: testpassword123")
                
                return user
                
            except Exception as e:
                if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                    print("ℹ️  Test user already exists!")
                    print("🔑 You can log in with:")
                    print("   Email: test@example.com")
                    print("   Password: testpassword123")
                else:
                    print(f"❌ Error creating test user: {e}")
                    raise
            
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return None


if __name__ == "__main__":
    asyncio.run(create_test_user())

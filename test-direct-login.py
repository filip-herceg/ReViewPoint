#!/usr/bin/env python3
"""Direct test of the backend authentication without relying on environment loading."""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, 'backend/src')

# Manually set environment variables for this test
os.environ['REVIEWPOINT_DB_URL'] = 'postgresql+asyncpg://postgres:postgres@localhost:5432/reviewpoint'
os.environ['REVIEWPOINT_JWT_SECRET_KEY'] = 'testsecret'
os.environ['REVIEWPOINT_FEATURE_AUTH'] = 'true'
os.environ['REVIEWPOINT_FEATURE_AUTH_LOGIN'] = 'true'
os.environ['REVIEWPOINT_FEATURE_HEALTH'] = 'true'
os.environ['REVIEWPOINT_ENVIRONMENT'] = 'dev'

# Test feature flags first
from src.core.feature_flags import FeatureFlags

print("Testing feature flags:")
print(f"  auth:login: {FeatureFlags.is_enabled('auth:login')}")
print(f"  health: {FeatureFlags.is_enabled('health')}")

# Test user authentication directly
from src.core.database import get_async_session
from src.services.user import UserService

async def test_login():
    try:
        print("\nTesting direct login...")
        
        # Get a database session
        session_generator = get_async_session()
        session = await session_generator.__anext__()
        
        try:
            user_service = UserService()
            
            # Test the login
            try:
                result = await user_service.authenticate_user(session, "test@example.com", "testpassword")
                if result:
                    print(f"✓ Login successful! User: {result.email}")
                    
                    # Generate a token
                    from src.core.security import create_access_token
                    token = create_access_token({"sub": str(result.id)})
                    print(f"✓ Token generated: {token[:50]}...")
                    
                    return token
                else:
                    print("✗ Login failed - invalid credentials")
            except Exception as e:
                print(f"✗ Login error: {e}")
                import traceback
                traceback.print_exc()
        
        finally:
            await session.close()
            
    except Exception as e:
        print(f"✗ Database connection error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_login())

#!/usr/bin/env python3

"""
Debug script to understand why API key validation fails in fast test environment.
"""

import os
import sys
sys.path.insert(0, "src")

from unittest import mock

# Set up the fast test environment similar to conftest_fast.py
os.environ.update({
    "REVIEWPOINT_ENVIRONMENT": "test",
    "REVIEWPOINT_JWT_SECRET": "fasttestsecret123",
    "REVIEWPOINT_JWT_SECRET_KEY": "fasttestsecret123",
    "REVIEWPOINT_API_KEY_ENABLED": "false",  # This is the default in fast tests
    "REVIEWPOINT_API_KEY": "testkey",
    "REVIEWPOINT_AUTH_ENABLED": "true",
    "REVIEWPOINT_LOG_LEVEL": "WARNING",
    "REVIEWPOINT_DB_URL": "sqlite+aiosqlite:///:memory:",
    # Feature flags - enable all
    "REVIEWPOINT_FEATURE_HEALTH": "true",
    "REVIEWPOINT_FEATURE_HEALTH_READ": "true",
    "REVIEWPOINT_FEATURE_UPLOADS": "true",
    "REVIEWPOINT_FEATURE_UPLOADS_LIST": "true"
})

# Now simulate what the test does - override environment vars
test_env_overrides = {
    "REVIEWPOINT_API_KEY_ENABLED": "true",  # Enable API key auth
    "REVIEWPOINT_API_KEY": "nottherightkey",
    "REVIEWPOINT_FEATURE_HEALTH": "true",
    "REVIEWPOINT_FEATURE_HEALTH_READ": "true"
}

print("=== BEFORE OVERRIDE ===")
print(f"API_KEY_ENABLED: {os.environ.get('REVIEWPOINT_API_KEY_ENABLED')}")
print(f"API_KEY: {os.environ.get('REVIEWPOINT_API_KEY')}")

# Apply overrides
with mock.patch.dict(os.environ, test_env_overrides):
    print("\n=== AFTER OVERRIDE ===")
    print(f"API_KEY_ENABLED: {os.environ.get('REVIEWPOINT_API_KEY_ENABLED')}")
    print(f"API_KEY: {os.environ.get('REVIEWPOINT_API_KEY')}")
    
    # Clear any cached settings
    from src.core.config import clear_settings_cache
    clear_settings_cache()
    
    # Now import and test the settings
    from src.core.config import get_settings
    settings = get_settings()
    
    print(f"\n=== SETTINGS OBJECT ===")
    print(f"api_key_enabled: {settings.api_key_enabled}")
    print(f"api_key (first 10 chars): {str(settings.api_key)[:10]}...")
    
    # Test the validate_api_key function directly
    from src.api.deps import validate_api_key
    from fastapi import HTTPException
    import asyncio
    
    print(f"\n=== TESTING API KEY VALIDATION ===")
    
    async def test_api_key_validation():
        try:
            # Test with wrong key
            result = await validate_api_key("wrongkey")
            print(f"validate_api_key('wrongkey') result: {result}")
            if not result:
                print("✅ API key validation correctly rejected the wrong key!")
            else:
                print("❌ API key validation did NOT reject the wrong key!")
        except Exception as e:
            print(f"Error in validate_api_key: {e}")
            
        try:
            # Test with correct key
            result = await validate_api_key("nottherightkey")  # This is what we set as the valid key
            print(f"validate_api_key('nottherightkey') result: {result}")
            if result:
                print("✅ API key validation correctly accepted the right key!")
            else:
                print("❌ API key validation rejected the right key!")
        except Exception as e:
            print(f"Error in validate_api_key with right key: {e}")
    
    asyncio.run(test_api_key_validation())

print("\n=== AFTER OVERRIDE CONTEXT ===")
print(f"API_KEY_ENABLED: {os.environ.get('REVIEWPOINT_API_KEY_ENABLED')}")
print(f"API_KEY: {os.environ.get('REVIEWPOINT_API_KEY')}")

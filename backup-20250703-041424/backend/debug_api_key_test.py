#!/usr/bin/env python3
"""
Debug script to test API key validation logic.
"""

import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Set initial environment
os.environ["REVIEWPOINT_API_KEY_ENABLED"] = "true"
os.environ["REVIEWPOINT_API_KEY"] = "testkey"
os.environ["REVIEWPOINT_DB_URL"] = "postgresql+asyncpg://test:test@localhost/test"
os.environ["REVIEWPOINT_JWT_SECRET"] = "testsecret"
os.environ["REVIEWPOINT_JWT_SECRET_KEY"] = "testsecret"

def test_api_key_validation():
    from src.core.config import get_settings, clear_settings_cache
    from src.api.deps import validate_api_key
    import asyncio
    
    print("=== Initial state ===")
    settings = get_settings()
    print(f"API key enabled: {settings.api_key_enabled}")
    print(f"Configured API key: {settings.api_key}")
    
    # Test with correct key
    print("\n=== Test with correct key ===")
    async def test_correct():
        result = await validate_api_key("testkey")
        print(f"validate_api_key('testkey') = {result}")
    
    asyncio.run(test_correct())
    
    # Test with wrong key
    print("\n=== Test with wrong key ===")
    async def test_wrong():
        result = await validate_api_key("wrongkey")
        print(f"validate_api_key('wrongkey') = {result}")
    
    asyncio.run(test_wrong())
    
    # Change environment and test
    print("\n=== Change environment ===")
    os.environ["REVIEWPOINT_API_KEY"] = "nottherightkey"
    clear_settings_cache()
    
    settings = get_settings()
    print(f"API key enabled: {settings.api_key_enabled}")
    print(f"New configured API key: {settings.api_key}")
    
    print("\n=== Test with wrong key after env change ===")
    async def test_wrong_after_change():
        result = await validate_api_key("wrongkey")
        print(f"validate_api_key('wrongkey') = {result}")
    
    asyncio.run(test_wrong_after_change())

if __name__ == "__main__":
    test_api_key_validation()

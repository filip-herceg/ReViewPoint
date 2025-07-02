#!/usr/bin/env python3

import os
import sys
sys.path.insert(0, "src")

# Set minimal required environment variables for test mode
os.environ["REVIEWPOINT_ENVIRONMENT"] = "test"
os.environ["REVIEWPOINT_DB_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["REVIEWPOINT_JWT_SECRET_KEY"] = "testsecret"

# Test what settings we get
print("Current environment variables:")
for key, value in os.environ.items():
    if key.startswith("REVIEWPOINT_"):
        print(f"  {key}={value}")

print("\nInitial settings:")
from src.core.config import get_settings
settings = get_settings()
print(f"  api_key_enabled: {settings.api_key_enabled}")
print(f"  api_key: {settings.api_key}")

# Test API key validation
print("\nTesting API key validation with fresh environment variables:")
os.environ["REVIEWPOINT_API_KEY"] = "nottherightkey"
os.environ["REVIEWPOINT_API_KEY_ENABLED"] = "true"

# Clear the settings cache to pick up new env vars
from src.core.config import clear_settings_cache
clear_settings_cache()

settings = get_settings()
print(f"  api_key_enabled after setting env vars: {settings.api_key_enabled}")
print(f"  api_key after setting env vars: {settings.api_key}")

from src.api.deps import validate_api_key
import asyncio

async def test_validation():
    print("\nTesting validate_api_key function:")
    
    # Test with wrong key
    result = await validate_api_key("wrongkey")
    print(f"  validate_api_key('wrongkey') result: {result}")
    
    # Test with correct key
    result = await validate_api_key("nottherightkey")
    print(f"  validate_api_key('nottherightkey') result: {result}")
    
    # Test API key disabled
    os.environ["REVIEWPOINT_API_KEY_ENABLED"] = "false"
    clear_settings_cache()
    
    result = await validate_api_key("anythingworks")
    print(f"  validate_api_key('anythingworks') with api_key_enabled=false result: {result}")

asyncio.run(test_validation())

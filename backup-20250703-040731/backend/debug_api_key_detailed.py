#!/usr/bin/env python3
"""
Debug script to test API key validation in test context.
"""

import os
import sys
import asyncio
from fastapi import Security
from fastapi.testclient import TestClient

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Set initial environment
os.environ["REVIEWPOINT_API_KEY_ENABLED"] = "true"
os.environ["REVIEWPOINT_API_KEY"] = "testkey"
os.environ["REVIEWPOINT_DB_URL"] = "postgresql+asyncpg://test:test@localhost/test"
os.environ["REVIEWPOINT_JWT_SECRET"] = "testsecret"
os.environ["REVIEWPOINT_JWT_SECRET_KEY"] = "testsecret"
os.environ["REVIEWPOINT_ENVIRONMENT"] = "test"
os.environ["REVIEWPOINT_FEATURE_HEALTH"] = "true"
os.environ["REVIEWPOINT_FEATURE_HEALTH_READ"] = "true"

def test_api_key_validation_detailed():
    from src.core.config import get_settings, clear_settings_cache
    from src.api.deps import validate_api_key, require_api_key, api_key_header
    from src.core.feature_flags import FeatureFlags
    from src.main import app
    
    print("=== Test environment ===")
    settings = get_settings()
    print(f"Environment: {settings.environment}")
    print(f"API key enabled: {settings.api_key_enabled}")
    print(f"Configured API key: {settings.api_key}")
    
    # Check feature flags
    print(f"\n=== Feature flags ===")
    flags = FeatureFlags()
    print(f"health:read enabled: {flags.is_enabled('health:read')}")
    print(f"REVIEWPOINT_FEATURE_HEALTH: {os.environ.get('REVIEWPOINT_FEATURE_HEALTH')}")
    print(f"REVIEWPOINT_FEATURE_HEALTH_READ: {os.environ.get('REVIEWPOINT_FEATURE_HEALTH_READ')}")
    
    # Test with TestClient
    print("\n=== Create TestClient ===")
    client = TestClient(app)
    
    # Test 1: Correct API key
    print("\n=== Test 1: Correct API key ===")
    response = client.get("/api/v1/health", headers={"X-API-Key": "testkey"})
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Response: {response.text}")
    
    # Test 2: Wrong API key with original setting
    print("\n=== Test 2: Wrong API key (original setting) ===")
    response = client.get("/api/v1/health", headers={"X-API-Key": "wrongkey"})
    print(f"Status: {response.status_code}")
    if response.status_code != 401:
        print(f"Response: {response.text}")
    
    # Test 3: Change environment and test
    print("\n=== Test 3: Change env and test wrong key ===")
    os.environ["REVIEWPOINT_API_KEY"] = "nottherightkey"
    clear_settings_cache()
    
    # Create a new client to ensure settings are refreshed
    client = TestClient(app)
    
    new_settings = get_settings()
    print(f"New API key: {new_settings.api_key}")
    
    # Check feature flags again
    flags = FeatureFlags()
    print(f"health:read still enabled: {flags.is_enabled('health:read')}")
    
    response = client.get("/api/v1/health", headers={"X-API-Key": "wrongkey"})
    print(f"Status: {response.status_code}")
    if response.status_code != 401:
        print(f"Response: {response.text}")
        
    # Test validate_api_key directly
    print("\n=== Test 4: Direct validate_api_key call ===")
    async def test_direct():
        result = await validate_api_key("wrongkey")
        print(f"validate_api_key('wrongkey') = {result}")
        
        # Test require_api_key directly
        try:
            await require_api_key("wrongkey")
            print("require_api_key('wrongkey') did NOT raise an exception!")
        except Exception as e:
            print(f"require_api_key('wrongkey') raised: {type(e).__name__}: {e}")
    
    asyncio.run(test_direct())

if __name__ == "__main__":
    test_api_key_validation_detailed()

#!/usr/bin/env python3
"""
Debug script to test exact test conditions.
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Set initial environment exactly like in tests
os.environ["REVIEWPOINT_JWT_SECRET"] = "testsecret"
os.environ["REVIEWPOINT_JWT_SECRET_KEY"] = "testsecret"
os.environ["REVIEWPOINT_API_KEY_ENABLED"] = "true"
os.environ["REVIEWPOINT_API_KEY"] = "testkey"
os.environ["REVIEWPOINT_ENVIRONMENT"] = "test"
os.environ["REVIEWPOINT_FEATURE_HEALTH"] = "true"
os.environ["REVIEWPOINT_FEATURE_HEALTH_READ"] = "true"

def test_like_real_test():
    from src.core.config import get_settings, clear_settings_cache
    from src.main import create_app
    
    # Create app like in tests
    app = create_app()
    client = TestClient(app)
    
    print("=== Test 1: Valid API key ===")
    response = client.get("/api/v1/health", headers={"X-API-Key": "testkey"})
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Response: {response.text}")
    
    print("\n=== Test 2: Invalid API key ===")
    response = client.get("/api/v1/health", headers={"X-API-Key": "wrongkey"})
    print(f"Status: {response.status_code}")
    if response.status_code != 401:
        print(f"Response: {response.text}")
    
    print("\n=== Test 3: Change API key setting ===")
    # Override environment like the test does
    os.environ["REVIEWPOINT_API_KEY"] = "nottherightkey"
    clear_settings_cache()
    
    # Create new client to pick up changes
    app = create_app()
    client = TestClient(app)
    
    new_settings = get_settings()
    print(f"New configured API key: {new_settings.api_key}")
    
    response = client.get("/api/v1/health", headers={"X-API-Key": "wrongkey"})
    print(f"Status: {response.status_code}")
    if response.status_code != 401:
        print(f"Response: {response.text}")
    
    print("\n=== Test 4: No API key header ===")
    response = client.get("/api/v1/health")
    print(f"Status: {response.status_code}")
    if response.status_code != 401:
        print(f"Response: {response.text}")

if __name__ == "__main__":
    test_like_real_test()

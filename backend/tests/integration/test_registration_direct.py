#!/usr/bin/env python3
"""Test registration endpoint directly to see the actual error"""

import asyncio
import json
import sys

from httpx import AsyncClient


async def test_registration():
    """Test the registration endpoint directly"""
    print("=== Testing Registration Endpoint ===")

    # Test data
    test_data = {
        "email": "debug.test@example.com",
        "password": "TestPassword123!",
        "name": "Debug Test User",
    }

    try:
        # Test against the backend directly
        async with AsyncClient(
            base_url="http://localhost:8000",
            headers={"X-API-Key": "testkey"},
            timeout=30.0,
        ) as client:
            print("Making request to /api/v1/auth/register...")
            response = await client.post("/api/v1/auth/register", json=test_data)

            print(f"Status: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")

            try:
                response_data = response.json()
                print(f"Response JSON: {json.dumps(response_data, indent=2)}")
            except Exception as e:
                print(f"Response text: {response.text}")
                print(f"Failed to parse JSON: {e}")

            if response.status_code != 201:
                print("❌ Registration failed!")
                return False
            print("✅ Registration successful!")
            return True

    except Exception as e:
        print(f"❌ Request failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_registration())
    sys.exit(0 if success else 1)

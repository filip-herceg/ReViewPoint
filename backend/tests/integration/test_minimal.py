#!/usr/bin/env python3
"""Test minimal endpoints without database dependencies."""

import asyncio

import httpx


async def test_minimal_endpoints():
    """Test endpoints that don't require database connections."""
    print("=== Testing Minimal Backend Endpoints ===")

    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            # Test debug endpoint (should have no dependencies)
            print("1. Testing debug endpoint...")
            response = await client.get("http://localhost:8000/debug/test")
            print(f"   GET /debug/test: {response.status_code}")
            if response.status_code == 200:
                print(f"   Response: {response.json()}")
            else:
                print(f"   Error response: {response.text}")

            # Test debug POST endpoint
            print("2. Testing debug POST endpoint...")
            response = await client.post("http://localhost:8000/debug/test-post")
            print(f"   POST /debug/test-post: {response.status_code}")
            if response.status_code == 200:
                print(f"   Response: {response.json()}")
            else:
                print(f"   Error response: {response.text}")

        except httpx.ReadTimeout:
            print("❌ Request timed out - endpoints are hanging")
        except httpx.ConnectError:
            print("❌ Cannot connect to backend")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(test_minimal_endpoints())

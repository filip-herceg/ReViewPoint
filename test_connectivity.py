#!/usr/bin/env python3
"""Quick test to diagnose registration endpoint connectivity issues."""

import asyncio

import httpx


async def test_endpoint_connectivity():
    """Test if we can connect to the registration endpoint at all."""
    print("=== Testing Backend Connectivity ===")

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            # First test if backend is responding at all
            print("1. Testing backend health...")
            response = await client.get("http://localhost:8000/health")
            print(f"   Health check: {response.status_code}")

            # Test if auth router is mounted
            print("2. Testing auth routes existence...")
            response = await client.get("http://localhost:8000/api/v1/auth/")
            print(f"   Auth router: {response.status_code}")

            # Test registration endpoint with minimal data
            print("3. Testing registration endpoint reachability...")
            test_data = {
                "email": "test@example.com",
                "password": "testpassword123",
                "name": "Test User",
            }

            print("   Sending request to /api/v1/auth/register...")
            response = await client.post(
                "http://localhost:8000/api/v1/auth/register",
                json=test_data,
                timeout=5.0,  # Shorter timeout to catch hangs
            )
            print(f"   Registration response: {response.status_code}")
            if response.status_code != 200:
                print(f"   Response body: {response.text}")

        except httpx.ReadTimeout:
            print("❌ Request timed out - endpoint may be hanging")
        except httpx.ConnectError:
            print("❌ Cannot connect to backend - is it running?")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(test_endpoint_connectivity())

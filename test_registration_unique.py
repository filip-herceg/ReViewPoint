#!/usr/bin/env python3
"""Test registration with a unique email to verify complete flow."""

import asyncio
import time

import httpx


async def test_registration_flow():
    """Test registration with unique email."""
    print("=== Testing Registration Flow ===")

    # Use timestamp to ensure unique email
    timestamp = int(time.time() * 1000)
    test_data = {
        "email": f"test-{timestamp}@example.com",
        "password": "testpassword123",
        "name": "Test User",
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            print(f"Testing registration with email: {test_data['email']}")
            response = await client.post(
                "http://localhost:8000/api/v1/auth/register",
                json=test_data,
            )
            print(f"Registration response: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                print("✅ Registration successful!")
                print(f"   User ID: {result.get('user', {}).get('id', 'N/A')}")
                print(
                    f"   Access token: {'✓ Present' if result.get('access_token') else '✗ Missing'}"
                )
                print(
                    f"   Refresh token: {'✓ Present' if result.get('refresh_token') else '✗ Missing'}"
                )
            else:
                print(f"❌ Registration failed: {response.text}")

        except Exception as e:
            print(f"❌ Error during registration: {e}")


if __name__ == "__main__":
    asyncio.run(test_registration_flow())

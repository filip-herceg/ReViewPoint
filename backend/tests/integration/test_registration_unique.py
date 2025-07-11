#!/usr/bin/env python3
"""Test registration with a unique email to verify complete flow."""

from __future__ import annotations

import asyncio
import time
from typing import Any, Final

import httpx

# HTTP status constants
HTTP_STATUS_OK: Final[int] = 200

# API endpoint constants
API_BASE_URL: Final[str] = "http://localhost:8000/api/v1"
REGISTRATION_ENDPOINT: Final[str] = f"{API_BASE_URL}/auth/register"
REQUEST_TIMEOUT: Final[float] = 10.0

# Test constants
PASSWORD_TEST_VALUE: Final[str] = "testpassword123"  # Test-only password
TEST_USER_NAME: Final[str] = "Test User"
EMAIL_DOMAIN: Final[str] = "@example.com"

# Display constants
TOKEN_PRESENT: Final[str] = "✓ Present"
TOKEN_MISSING: Final[str] = "✗ Missing"
USER_ID_FALLBACK: Final[str] = "N/A"


async def test_registration_flow() -> None:
    """Test registration with unique email.

    Tests the complete registration flow using a unique timestamp-based email
    to ensure no conflicts with existing users.

    Raises:
        httpx.RequestError: If the HTTP request fails.
        httpx.TimeoutException: If the request times out.
        ValueError: If response parsing fails.

    """
    print("=== Testing Registration Flow ===")

    # Use timestamp to ensure unique email
    timestamp: int = int(time.time() * 1000)
    test_data: dict[str, str] = {
        "email": f"test-{timestamp}{EMAIL_DOMAIN}",
        "password": PASSWORD_TEST_VALUE,
        "name": TEST_USER_NAME,
    }

    timeout_config: httpx.Timeout = httpx.Timeout(REQUEST_TIMEOUT)
    async with httpx.AsyncClient(timeout=timeout_config) as client:
        try:
            print(f"Testing registration with email: {test_data['email']}")
            response: httpx.Response = await client.post(
                REGISTRATION_ENDPOINT,
                json=test_data,
            )
            print(f"Registration response: {response.status_code}")

            if response.status_code == HTTP_STATUS_OK:
                result: dict[str, Any] = response.json()
                print("✅ Registration successful!")

                user_data: dict[str, Any] | None = result.get("user")
                user_id: str = (
                    user_data.get("id", USER_ID_FALLBACK)
                    if user_data
                    else USER_ID_FALLBACK
                )
                print(f"   User ID: {user_id}")

                access_token: str | None = result.get("access_token")
                access_token_status: str = (
                    TOKEN_PRESENT if access_token else TOKEN_MISSING
                )
                print(f"   Access token: {access_token_status}")

                refresh_token: str | None = result.get("refresh_token")
                refresh_token_status: str = (
                    TOKEN_PRESENT if refresh_token else TOKEN_MISSING
                )
                print(f"   Refresh token: {refresh_token_status}")
            else:
                error_text: str = response.text
                print(f"❌ Registration failed: {error_text}")

        except (httpx.RequestError, httpx.TimeoutException) as e:
            print(f"❌ HTTP error during registration: {e}")
        except ValueError as e:
            print(f"❌ JSON parsing error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error during registration: {e}")


if __name__ == "__main__":
    asyncio.run(test_registration_flow())

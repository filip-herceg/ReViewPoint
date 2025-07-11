#!/usr/bin/env python3
"""Quick test to diagnose registration endpoint connectivity issues."""

from __future__ import annotations

import asyncio
from typing import Final

import httpx

# HTTP status constants
HTTP_STATUS_OK: Final[int] = 200

# URL constants
BASE_URL: Final[str] = "http://localhost:8000"
HEALTH_ENDPOINT: Final[str] = f"{BASE_URL}/health"
AUTH_ROUTER_ENDPOINT: Final[str] = f"{BASE_URL}/api/v1/auth/"
REGISTRATION_ENDPOINT: Final[str] = f"{BASE_URL}/api/v1/auth/register"

# Timeout constants
CLIENT_TIMEOUT: Final[float] = 10.0
REQUEST_TIMEOUT: Final[float] = 5.0

# Test data constants
TEST_EMAIL: Final[str] = "test@example.com"
TEST_PASSWORD: Final[str] = "testpassword123"  # Test-only password
TEST_NAME: Final[str] = "Test User"

# Test step messages
TEST_STEP_1: Final[str] = "1. Testing backend health..."
TEST_STEP_2: Final[str] = "2. Testing auth routes existence..."
TEST_STEP_3: Final[str] = "3. Testing registration endpoint reachability..."

# Display messages
CONNECTIVITY_HEADER: Final[str] = "=== Testing Backend Connectivity ==="
HEALTH_CHECK_MSG: Final[str] = "   Health check:"
AUTH_ROUTER_MSG: Final[str] = "   Auth router:"
REGISTRATION_MSG: Final[str] = "   Registration response:"
SENDING_REQUEST_MSG: Final[str] = "   Sending request to /api/v1/auth/register..."
RESPONSE_BODY_MSG: Final[str] = "   Response body:"

# Error messages
TIMEOUT_ERROR_MSG: Final[str] = "❌ Request timed out - endpoint may be hanging"
CONNECTION_ERROR_MSG: Final[str] = "❌ Cannot connect to backend - is it running?"
UNEXPECTED_ERROR_MSG: Final[str] = "❌ Unexpected error:"


async def test_endpoint_connectivity() -> None:
    """Test if we can connect to the registration endpoint at all.

    Tests basic connectivity to backend endpoints including health check,
    auth router, and registration endpoint to diagnose connectivity issues.

    Raises:
        httpx.ReadTimeout: If requests timeout.
        httpx.ConnectError: If connection to backend fails.
        Exception: Any other unexpected errors during testing.

    """
    timeout_config: httpx.Timeout = httpx.Timeout(CLIENT_TIMEOUT)
    async with httpx.AsyncClient(timeout=timeout_config) as client:
        try:
            # First test if backend is responding at all
            health_response: httpx.Response = await client.get(HEALTH_ENDPOINT)
            if health_response.status_code != HTTP_STATUS_OK:
                msg = f"Health endpoint failed: {health_response.status_code}"
                raise AssertionError(msg)

            # Test if auth router is mounted
            auth_response: httpx.Response = await client.get(
                AUTH_ROUTER_ENDPOINT,
            )
            if auth_response.status_code != HTTP_STATUS_OK:
                msg = f"Auth router failed: {auth_response.status_code}"
                raise AssertionError(msg)

            # Test registration endpoint with minimal data
            test_data: dict[str, str] = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
                "name": TEST_NAME,
            }

            registration_response: httpx.Response = await client.post(
                REGISTRATION_ENDPOINT,
                json=test_data,
                timeout=REQUEST_TIMEOUT,  # Shorter timeout to catch hangs
            )
            # Registration may fail due to existing user, but should respond
            valid_codes = {200, 201, 400, 409}
            if registration_response.status_code not in valid_codes:
                msg = f"Unexpected status: {registration_response.status_code}"
                raise AssertionError(msg)

        except httpx.ReadTimeout as e:
            timeout_msg = "Request timed out"
            raise TimeoutError(timeout_msg) from e
        except httpx.ConnectError as e:
            connect_msg = "Cannot connect to backend"
            raise ConnectionError(connect_msg) from e
        except (ValueError, httpx.RequestError) as e:
            error_msg = f"Unexpected error: {e}"
            raise RuntimeError(error_msg) from e


if __name__ == "__main__":
    asyncio.run(test_endpoint_connectivity())

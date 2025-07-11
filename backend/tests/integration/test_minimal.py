#!/usr/bin/env python3
"""Test minimal endpoints without database dependencies."""

from __future__ import annotations

import asyncio
from typing import Any, Final

import httpx

# HTTP status constants
HTTP_STATUS_OK: Final[int] = 200

# URL constants
BASE_URL: Final[str] = "http://localhost:8000"
DEBUG_TEST_ENDPOINT: Final[str] = f"{BASE_URL}/debug/test"
DEBUG_POST_ENDPOINT: Final[str] = f"{BASE_URL}/debug/test-post"

# Timeout constants
REQUEST_TIMEOUT: Final[float] = 5.0

# Test step messages
TEST_STEP_1: Final[str] = "1. Testing debug endpoint..."
TEST_STEP_2: Final[str] = "2. Testing debug POST endpoint..."

# Error messages
TIMEOUT_ERROR_MSG: Final[str] = "❌ Request timed out - endpoints are hanging"
CONNECTION_ERROR_MSG: Final[str] = "❌ Cannot connect to backend"
UNEXPECTED_ERROR_MSG: Final[str] = "❌ Unexpected error:"


async def test_minimal_endpoints() -> None:
    """Test endpoints that don't require database connections.

    Tests basic debug endpoints to verify the backend is responding
    without requiring database connectivity.

    Raises:
        httpx.ReadTimeout: If requests timeout.
        httpx.ConnectError: If connection to backend fails.
        Exception: Any other unexpected errors during testing.

    """
    print("=== Testing Minimal Backend Endpoints ===")

    timeout_config: httpx.Timeout = httpx.Timeout(REQUEST_TIMEOUT)
    async with httpx.AsyncClient(timeout=timeout_config) as client:
        try:
            # Test debug endpoint (should have no dependencies)
            print(TEST_STEP_1)
            response: httpx.Response = await client.get(DEBUG_TEST_ENDPOINT)
            print(f"   GET /debug/test: {response.status_code}")
            if response.status_code == HTTP_STATUS_OK:
                response_data: dict[str, Any] = response.json()
                print(f"   Response: {response_data}")
            else:
                error_text: str = response.text
                print(f"   Error response: {error_text}")

            # Test debug POST endpoint
            print(TEST_STEP_2)
            post_response: httpx.Response = await client.post(
                DEBUG_POST_ENDPOINT,
            )
            print(f"   POST /debug/test-post: {post_response.status_code}")
            if post_response.status_code == HTTP_STATUS_OK:
                post_response_data: dict[str, Any] = post_response.json()
                print(f"   Response: {post_response_data}")
            else:
                post_error_text: str = post_response.text
                print(f"   Error response: {post_error_text}")

        except httpx.ReadTimeout:
            print(TIMEOUT_ERROR_MSG)
        except httpx.ConnectError:
            print(CONNECTION_ERROR_MSG)
        except (ValueError, httpx.RequestError) as e:
            print(f"{UNEXPECTED_ERROR_MSG} {e}")


if __name__ == "__main__":
    asyncio.run(test_minimal_endpoints())

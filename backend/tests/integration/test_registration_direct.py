#!/usr/bin/env python3
"""Test registration endpoint directly to see the actual error."""

from __future__ import annotations

import asyncio
import json
import sys
import traceback
from typing import TYPE_CHECKING, Any, Final

if TYPE_CHECKING:
    from collections.abc import Mapping

from httpx import AsyncClient, Response, Timeout

# HTTP status constants
HTTP_STATUS_CREATED: Final[int] = 201
HTTP_STATUS_SUCCESS_EXIT: Final[int] = 0
HTTP_STATUS_FAILURE_EXIT: Final[int] = 1

# API configuration constants
BASE_URL: Final[str] = "http://localhost:8000"
API_ENDPOINT: Final[str] = "/api/v1/auth/register"
API_KEY_HEADER: Final[str] = "X-API-Key"
TEST_API_KEY: Final[str] = "testkey"
REQUEST_TIMEOUT: Final[float] = 30.0

# Test data constants
TEST_EMAIL: Final[str] = "debug.test@example.com"
TEST_PASSWORD: Final[str] = "TestPassword123!"
TEST_NAME: Final[str] = "Debug Test User"

# Display constants
SUCCESS_MESSAGE: Final[str] = "✅ Registration successful!"
FAILURE_MESSAGE: Final[str] = "❌ Registration failed!"
REQUEST_FAILED_MESSAGE: Final[str] = "❌ Request failed:"


async def test_registration() -> bool:
    """Test the registration endpoint directly.

    Makes a direct HTTP request to the registration endpoint to test
    the complete registration flow and error handling.

    Returns:
        bool: True if registration succeeds, False otherwise.

    Raises:
        Exception: Any network, JSON parsing, or unexpected errors
            during testing.

    """
    print("=== Testing Registration Endpoint ===")

    # Test data
    test_data: dict[str, str] = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "name": TEST_NAME,
    }

    try:
        # Test against the backend directly
        timeout_config: Timeout = Timeout(REQUEST_TIMEOUT)
        headers: dict[str, str] = {API_KEY_HEADER: TEST_API_KEY}

        async with AsyncClient(
            base_url=BASE_URL,
            headers=headers,
            timeout=timeout_config,
        ) as client:
            print("Making request to /api/v1/auth/register...")
            response: Response = await client.post(
                API_ENDPOINT,
                json=test_data,
            )

            print(f"Status: {response.status_code}")
            response_headers: Mapping[str, str] = dict(response.headers)
            print(f"Headers: {response_headers}")

            try:
                response_data: dict[str, Any] = response.json()
                formatted_response: str = json.dumps(response_data, indent=2)
                print(f"Response JSON: {formatted_response}")
            except (ValueError, json.JSONDecodeError) as e:
                response_text: str = response.text
                print(f"Response text: {response_text}")
                print(f"Failed to parse JSON: {e}")

            if response.status_code != HTTP_STATUS_CREATED:
                print(FAILURE_MESSAGE)
                return False
            print(SUCCESS_MESSAGE)
            return True

    except (
        OSError,
        ConnectionError,
        TimeoutError,
        ValueError,
        json.JSONDecodeError,
    ) as e:
        print(f"{REQUEST_FAILED_MESSAGE} {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success: bool = asyncio.run(test_registration())
    exit_code: int = HTTP_STATUS_SUCCESS_EXIT if success else HTTP_STATUS_FAILURE_EXIT
    sys.exit(exit_code)

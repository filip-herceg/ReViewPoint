#!/usr/bin/env python3
"""Test pydantic-settings .env loading directly."""

from __future__ import annotations

import os
import sys
import traceback
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from backend.src.core.config import Settings

# Path configuration constants
BACKEND_PATH: Final[str] = "./backend"
ENV_FILE_PATH: Final[str] = "backend/config/.env"

# Environment variable constants
REVIEWPOINT_FEATURE_AUTH_REGISTER: Final[str] = "REVIEWPOINT_FEATURE_AUTH_REGISTER"
NOT_SET_VALUE: Final[str] = "NOT_SET"

# Display constants
DB_URL_DISPLAY_LENGTH: Final[int] = 50
MASKED_SECRET: Final[str] = "***"  # Display mask for secrets
NONE_DISPLAY: Final[str] = "None"

# Test section headers
PYDANTIC_TEST_HEADER: Final[str] = "=== Pydantic .env Loading Test ==="
DIRECT_PYDANTIC_HEADER: Final[str] = "Direct pydantic loading results:"
BACKEND_CONFIG_HEADER: Final[str] = "Backend config results:"

# Path manipulation
sys.path.append(BACKEND_PATH)


def test_pydantic_env_loading() -> None:
    """Test pydantic-settings .env loading functionality.

    Tests both direct pydantic-settings loading and backend config loading
    to verify environment variable handling.

    Raises:
        ImportError: If required modules cannot be imported.
        OSError: If file operations fail.
        Exception: Any other unexpected errors during testing.

    """
    print(PYDANTIC_TEST_HEADER)

    # First, ensure we're in the right directory context
    current_dir: str = os.getcwd()
    print(f"Current working directory: {current_dir}")

    # Test direct pydantic-settings loading
    try:
        from pydantic_settings import BaseSettings

        class TestSettings(BaseSettings):
            """Test settings class for direct pydantic testing."""

            # Test a few key variables
            reviewpoint_db_url: str | None = None
            reviewpoint_feature_auth_register: str | None = None
            reviewpoint_jwt_secret_key: str | None = None

            class Config:
                """Pydantic configuration."""

                env_file: str = ENV_FILE_PATH
                case_sensitive: bool = False

        settings: TestSettings = TestSettings()

        print(DIRECT_PYDANTIC_HEADER)

        # Format DB URL display
        db_url_display: str = (
            f"{settings.reviewpoint_db_url[:DB_URL_DISPLAY_LENGTH]}..."
            if settings.reviewpoint_db_url
            else f"{NONE_DISPLAY}..."
        )
        print(f"  DB URL: {db_url_display}")

        # Always mask auth register value for security
        auth_register_display: str = (
            MASKED_SECRET
            if settings.reviewpoint_feature_auth_register
            else NONE_DISPLAY
        )
        print(f"  Auth Register: {auth_register_display}")

        # Always mask JWT secret for security - never log actual secret values
        jwt_secret_display: str = (
            MASKED_SECRET if settings.reviewpoint_jwt_secret_key else NONE_DISPLAY
        )
        print(f"  JWT Secret: {jwt_secret_display}")

    except (ImportError, OSError, ValueError) as e:
        print(f"Direct pydantic test failed: {e}")
        traceback.print_exc()

    print()

    # Now test the actual backend config
    try:
        # Clear any cached settings first
        from backend.src.core.config import get_settings

        get_settings.cache_clear()

        backend_settings: Settings = get_settings()
        print(BACKEND_CONFIG_HEADER)
        print(f"  Environment: {backend_settings.environment}")

        # Format backend DB URL display
        backend_db_url_display: str = (
            f"{backend_settings.db_url[:DB_URL_DISPLAY_LENGTH]}..."
            if backend_settings.db_url
            else f"{NONE_DISPLAY}..."
        )
        print(f"  DB URL: {backend_db_url_display}")

        # Test if individual feature flag variables are accessible
        # Note: These might not be directly on settings object
        # Always mask the auth register value for security
        auth_register_raw: str = os.getenv(
            REVIEWPOINT_FEATURE_AUTH_REGISTER,
            NOT_SET_VALUE,
        )
        auth_register_masked: str = (
            MASKED_SECRET if auth_register_raw != NOT_SET_VALUE else NOT_SET_VALUE
        )
        print(f"  Auth Register (os.getenv): {auth_register_masked}")

    except (ImportError, AttributeError, OSError) as e:
        print(f"Backend config test failed: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    test_pydantic_env_loading()

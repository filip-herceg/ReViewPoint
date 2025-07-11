#!/usr/bin/env python3
"""Test pydantic-settings .env loading directly"""

import os
import sys

sys.path.append("./backend")


def test_pydantic_env_loading():
    print("=== Pydantic .env Loading Test ===")

    # First, ensure we're in the right directory context
    print(f"Current working directory: {os.getcwd()}")

    # Test direct pydantic-settings loading
    try:
        from typing import Optional

        from pydantic_settings import BaseSettings

        class TestSettings(BaseSettings):
            # Test a few key variables
            reviewpoint_db_url: Optional[str] = None
            reviewpoint_feature_auth_register: Optional[str] = None
            reviewpoint_jwt_secret_key: Optional[str] = None

            class Config:
                env_file = "backend/config/.env"
                case_sensitive = False

        settings = TestSettings()

        print("Direct pydantic loading results:")
        print(
            f"  DB URL: {settings.reviewpoint_db_url[:50] if settings.reviewpoint_db_url else 'None'}..."
        )
        print(f"  Auth Register: {settings.reviewpoint_feature_auth_register}")
        print(
            f"  JWT Secret: {'***' if settings.reviewpoint_jwt_secret_key else 'None'}"
        )

    except Exception as e:
        print(f"Direct pydantic test failed: {e}")
        import traceback

        traceback.print_exc()

    print()

    # Now test the actual backend config
    try:
        # Clear any cached settings first
        from backend.src.core.config import get_settings

        get_settings.cache_clear()

        settings = get_settings()
        print("Backend config results:")
        print(f"  Environment: {settings.environment}")
        print(f"  DB URL: {settings.db_url[:50] if settings.db_url else 'None'}...")

        # Test if individual feature flag variables are accessible
        # Note: These might not be directly on settings object
        auth_register = os.getenv("REVIEWPOINT_FEATURE_AUTH_REGISTER", "NOT_SET")
        print(f"  Auth Register (os.getenv): {auth_register}")

    except Exception as e:
        print(f"Backend config test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_pydantic_env_loading()

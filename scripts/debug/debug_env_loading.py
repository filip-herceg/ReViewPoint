#!/usr/bin/env python3
"""Debug .env file loading"""

import os
import sys
from pathlib import Path

sys.path.append("./backend")


def debug_env_loading():
    print("=== Environment File Loading Debug ===")

    # Check if .env file exists
    env_path = Path("backend/config/.env")
    print(f".env file exists: {env_path.exists()}")

    if env_path.exists():
        print(f".env file path: {env_path.absolute()}")
        print(f".env file size: {env_path.stat().st_size} bytes")

        # Read the .env file directly
        content = env_path.read_text()
        lines = content.strip().split("\n")
        print(f"\n.env file has {len(lines)} lines")

        # Check for feature flag lines
        feature_lines = [
            line
            for line in lines
            if "FEATURE" in line and not line.strip().startswith("#")
        ]
        print(f"Feature flag lines in .env: {len(feature_lines)}")

        for line in feature_lines[:5]:  # Show first 5
            print(f"  {line.strip()}")

        if len(feature_lines) > 5:
            print(f"  ... and {len(feature_lines) - 5} more")

    print()

    # Now try loading config
    try:
        from backend.src.core.config import get_settings

        settings = get_settings()

        print(f"Config loaded successfully - Environment: {settings.environment}")

        # Check if _env_file was detected
        from backend.src.core.config import _env_file

        print(f"Detected .env file path: {_env_file}")

    except Exception as e:
        print(f"Config loading failed: {e}")
        import traceback

        traceback.print_exc()

    print()

    # Manual environment variable check
    print("Manual environment variable check:")
    test_vars = [
        "REVIEWPOINT_DB_URL",
        "REVIEWPOINT_FEATURES",
        "REVIEWPOINT_FEATURE_AUTH_REGISTER",
        "REVIEWPOINT_JWT_SECRET_KEY",
    ]

    for var in test_vars:
        value = os.getenv(var, "NOT_SET")
        status = "✅" if value != "NOT_SET" else "❌"
        print(f"  {status} {var} = {value[:50]}{'...' if len(str(value)) > 50 else ''}")


if __name__ == "__main__":
    debug_env_loading()

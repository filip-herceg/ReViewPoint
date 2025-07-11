#!/usr/bin/env python3

"""Test Feature Flags Script.

Tests if feature flags are working correctly.

This module tests the feature flags configuration to ensure they work
correctly. The test may raise OSError if environment access fails.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Mapping

# Add the backend directory to Python path
backend_dir: str = str(Path(__file__).parent / "backend")
sys.path.insert(0, backend_dir)
from src.core.feature_flags import FeatureFlags  # noqa: E402

# Test features constants - these never change
FEATURES_TO_TEST: Final[list[str]] = [
    "auth:login",
    "auth:register",
    "auth:logout",
    "health",
]

# Status display constants
ENABLED_STATUS: Final[str] = "✅ ENABLED"
DISABLED_STATUS: Final[str] = "❌ DISABLED"


def test_feature_flags() -> None:
    """Test the feature flags configuration.

    This function tests the feature flags system by checking enabled/disabled
    status for auth and health features.

    Raises:
        OSError: If environment variables cannot be accessed.
        AttributeError: If FeatureFlags instance cannot be created.

    """
    print("🔧 Testing feature flags...")

    flags: FeatureFlags = FeatureFlags()

    print("Environment variables:")
    environ_mapping: Mapping[str, str] = os.environ
    for key, value in environ_mapping.items():
        if "REVIEWPOINT" in key:
            print(f"  {key}={value}")

    print("\nFeature flags status:")
    for feature in FEATURES_TO_TEST:
        is_enabled: bool = flags.is_enabled(feature)
        status: str = ENABLED_STATUS if is_enabled else DISABLED_STATUS
        print(f"  {feature}: {status}")


if __name__ == "__main__":
    test_feature_flags()

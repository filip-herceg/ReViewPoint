#!/usr/bin/env python3
"""Debug feature flags with proper backend config loading"""

import os
import sys

sys.path.append("./backend")


def debug_feature_flags_with_config():
    print("=== Feature Flag Debug with Backend Config ===")

    # Load the backend config which should load .env file
    try:
        from backend.src.core.config import get_settings

        settings = get_settings()

        print(f"Environment: {settings.environment}")
        print(f"Database URL: {settings.db_url[:50]}...")
        print()

        # Now check feature flags after config is loaded
        from backend.src.core.feature_flags import FeatureFlags

        flags = FeatureFlags()

        # Check specific environment variables
        relevant_vars = [
            "REVIEWPOINT_FEATURES",
            "REVIEWPOINT_FEATURE_AUTH",
            "REVIEWPOINT_FEATURE_AUTH_REGISTER",
        ]

        print("Environment Variables (after config loading):")
        for var in relevant_vars:
            value = os.getenv(var, "NOT_SET")
            print(f"  {var} = {value}")

        print()

        # Test feature flag logic
        features_to_test = ["auth:register", "auth:login", "auth"]

        for feature in features_to_test:
            enabled = flags.is_enabled(feature)
            print(f"FeatureFlags.is_enabled('{feature}') = {enabled}")

        # Check the raw REVIEWPOINT_FEATURES value
        features_str = os.getenv("REVIEWPOINT_FEATURES", "")
        enabled_features = {f.strip() for f in features_str.split(",") if f.strip()}
        print("\nEnabled features from REVIEWPOINT_FEATURES:")
        for feature in sorted(enabled_features):
            print(f"  - {feature}")

        print(
            f"\nIs 'auth:register' in enabled features? {'auth:register' in enabled_features}"
        )

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    debug_feature_flags_with_config()

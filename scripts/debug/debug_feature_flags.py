#!/usr/bin/env python3
"""Debug feature flags"""

import os
import sys

# Set up the environment
sys.path.append("./backend")


def debug_feature_flags():
    print("=== Feature Flag Debug ===")

    # Print relevant env vars
    relevant_vars = [
        "REVIEWPOINT_FEATURES",
        "REVIEWPOINT_FEATURE_AUTH",
        "REVIEWPOINT_FEATURE_AUTH_REGISTER",
    ]

    print("Environment Variables:")
    for var in relevant_vars:
        value = os.getenv(var, "NOT_SET")
        print(f"  {var} = {value}")

    print()

    # Test the feature flag logic
    try:
        from backend.src.core.feature_flags import FeatureFlags

        flags = FeatureFlags()
        auth_register_enabled = flags.is_enabled("auth:register")

        print(f"FeatureFlags.is_enabled('auth:register') = {auth_register_enabled}")

        # Test other auth flags
        auth_login_enabled = flags.is_enabled("auth:login")
        print(f"FeatureFlags.is_enabled('auth:login') = {auth_login_enabled}")

        # Test general auth flag
        auth_enabled = flags.is_enabled("auth")
        print(f"FeatureFlags.is_enabled('auth') = {auth_enabled}")

    except Exception as e:
        print(f"Feature flag test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    debug_feature_flags()

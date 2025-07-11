#!/usr/bin/env python3
"""Test script to check feature flag configuration."""

import os
import sys

sys.path.insert(0, "backend/src")

# Load environment from .env file manually
from dotenv import load_dotenv

from src.core.feature_flags import FeatureFlags

load_dotenv("backend/config/.env")

# Test specific feature flags
features_to_test = ["auth", "auth:login", "auth:register", "health"]

print("Environment variables:")
for key, value in os.environ.items():
    if "REVIEWPOINT_FEATURE" in key:
        print(f"  {key} = {value}")

print("\nFeature flag results:")
for feature in features_to_test:
    result = FeatureFlags.is_enabled(feature)
    print(f"  {feature}: {'ENABLED' if result else 'DISABLED'}")

# Also check the raw environment variables
print("\nDirect environment check:")
print(
    f"  REVIEWPOINT_FEATURE_AUTH = {os.getenv('REVIEWPOINT_FEATURE_AUTH', 'NOT SET')}"
)
print(
    f"  REVIEWPOINT_FEATURE_AUTH_LOGIN = {os.getenv('REVIEWPOINT_FEATURE_AUTH_LOGIN', 'NOT SET')}"
)
print(
    f"  REVIEWPOINT_FEATURE_HEALTH = {os.getenv('REVIEWPOINT_FEATURE_HEALTH', 'NOT SET')}"
)

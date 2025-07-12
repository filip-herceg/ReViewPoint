#!/usr/bin/env python3
"""Test backend feature flag loading directly."""

import os
import sys

# Add backend source to path
sys.path.insert(0, "../../src")
from dotenv import load_dotenv

from src.api.deps import get_feature_flags

load_dotenv("../../config/.env")

print("Loaded environment variables:")
for key, value in os.environ.items():
    if "REVIEWPOINT_FEATURE" in key:
        print(f"  {key} = {value}")

feature_flags = get_feature_flags()

# Test the specific features that the auth endpoints need
test_features = [
    "auth:login",
    "auth:register",
    "health",
]

print("\nTesting feature flags through backend dependency system:")
for feature in test_features:
    enabled = feature_flags.is_enabled(feature)
    print(f"  {feature}: {'ENABLED' if enabled else 'DISABLED'}")

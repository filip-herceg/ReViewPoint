#!/usr/bin/env python3
"""Test backend feature flag loading directly."""

import os
import sys

# Add backend source to path
sys.path.insert(0, 'backend/src')

# Load the environment file first
from dotenv import load_dotenv
load_dotenv('backend/config/.env')

print("Loaded environment variables:")
for key, value in os.environ.items():
    if "REVIEWPOINT_FEATURE" in key:
        print(f"  {key} = {value}")

# Now test the backend dependency system
from src.api.deps import get_feature_flags

feature_flags = get_feature_flags()

# Test the specific features that the auth endpoints need
test_features = [
    "auth:login",
    "auth:register", 
    "health"
]

print(f"\nTesting feature flags through backend dependency system:")
for feature in test_features:
    enabled = feature_flags.is_enabled(feature)
    print(f"  {feature}: {'ENABLED' if enabled else 'DISABLED'}")

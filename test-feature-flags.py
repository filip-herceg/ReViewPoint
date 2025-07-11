#!/usr/bin/env python3

"""
Test Feature Flags Script

Tests if feature flags are working correctly.
"""

import sys
import os

# Add the backend directory to Python path
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

from src.core.feature_flags import FeatureFlags

def test_feature_flags():
    """Test the feature flags configuration."""
    print("🔧 Testing feature flags...")
    
    flags = FeatureFlags()
    
    # Test auth features
    features_to_test = [
        "auth:login",
        "auth:register", 
        "auth:logout",
        "health",
    ]
    
    print("Environment variables:")
    for key, value in os.environ.items():
        if "REVIEWPOINT" in key:
            print(f"  {key}={value}")
    
    print("\nFeature flags status:")
    for feature in features_to_test:
        is_enabled = flags.is_enabled(feature)
        status = "✅ ENABLED" if is_enabled else "❌ DISABLED"
        print(f"  {feature}: {status}")

if __name__ == "__main__":
    test_feature_flags()

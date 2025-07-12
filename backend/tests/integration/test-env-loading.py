import os
import sys

sys.path.append("./backend/src")

from core.feature_flags import FeatureFlags

print("=== Environment Variables Check ===")
print(f"REVIEWPOINT_FEATURES: {os.getenv('REVIEWPOINT_FEATURES', 'NOT_SET')}")
print(
    f"REVIEWPOINT_FEATURE_HEALTH: {os.getenv('REVIEWPOINT_FEATURE_HEALTH', 'NOT_SET')}"
)
print(
    f"REVIEWPOINT_FEATURE_HEALTH_READ: {os.getenv('REVIEWPOINT_FEATURE_HEALTH_READ', 'NOT_SET')}"
)
print(f"REVIEWPOINT_FEATURE_AUTH: {os.getenv('REVIEWPOINT_FEATURE_AUTH', 'NOT_SET')}")

print("\n=== Feature Flag Tests ===")
print(f"health:read enabled: {FeatureFlags.is_enabled('health:read')}")
print(f"auth:register enabled: {FeatureFlags.is_enabled('auth:register')}")
print(f"auth:login enabled: {FeatureFlags.is_enabled('auth:login')}")

print("\n=== Direct Environment Test ===")
# Test if .env is being loaded at all
print(f"DB_URL: {os.getenv('REVIEWPOINT_DB_URL', 'NOT_SET')}")
print(f"JWT_SECRET: {os.getenv('REVIEWPOINT_JWT_SECRET_KEY', 'NOT_SET')}")

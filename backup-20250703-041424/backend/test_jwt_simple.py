#!/usr/bin/env python3
"""
Simple test to debug JWT secret key issue during tests.
"""
import pytest
import os
from src.core.config import get_settings


def test_jwt_secret_key_available():
    """Test that JWT secret key is available."""
    print(f"JWT_SECRET_KEY env var: {'REVIEWPOINT_JWT_SECRET_KEY' in os.environ}")
    print(f"JWT_SECRET env var: {'REVIEWPOINT_JWT_SECRET' in os.environ}")
    
    if 'REVIEWPOINT_JWT_SECRET_KEY' in os.environ:
        print("JWT_SECRET_KEY value: [REDACTED]")
    if 'REVIEWPOINT_JWT_SECRET' in os.environ:
        print("JWT_SECRET value: [REDACTED]")
    
    settings = get_settings()
    print("Settings JWT secret key: [REDACTED]")
    print("Settings JWT secret (legacy): [REDACTED]")
    
    assert settings.jwt_secret_key is not None, "JWT secret key should be available"


if __name__ == "__main__":
    test_jwt_secret_key_available()

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
        print(f"JWT_SECRET_KEY value: {os.environ['REVIEWPOINT_JWT_SECRET_KEY']}")
    if 'REVIEWPOINT_JWT_SECRET' in os.environ:
        print(f"JWT_SECRET value: {os.environ['REVIEWPOINT_JWT_SECRET']}")
    
    settings = get_settings()
    print(f"Settings JWT secret key: {settings.jwt_secret_key}")
    print(f"Settings JWT secret (legacy): {settings.jwt_secret}")
    
    assert settings.jwt_secret_key is not None, "JWT secret key should be available"


if __name__ == "__main__":
    test_jwt_secret_key_available()

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
        print("JWT_SECRET_KEY is set (value masked)")
    if 'REVIEWPOINT_JWT_SECRET' in os.environ:
        print("JWT_SECRET is set (value masked)")
    
    settings = get_settings()
    print(f"Settings JWT secret key is {'set' if settings.jwt_secret_key else 'not set'} (value masked)")
    print(f"Settings JWT secret (legacy) is {'set' if settings.jwt_secret else 'not set'} (value masked)")
    
    assert settings.jwt_secret_key is not None, "JWT secret key should be available"


if __name__ == "__main__":
    test_jwt_secret_key_available()

#!/usr/bin/env python3
"""
Debug JWT token issues in auth logout.
"""
import os
import sys
from jose import jwt, JWTError, ExpiredSignatureError
from datetime import datetime, timedelta, UTC
import uuid

# Add src to path 
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.config import get_settings

def debug_jwt():
    print("DEBUG: JWT Token Creation and Decoding Test")
    print("=" * 50)
    
    # Set environment variables
    os.environ["REVIEWPOINT_JWT_SECRET_KEY"] = "test-secret-key-12345"
    os.environ["REVIEWPOINT_JWT_ALGORITHM"] = "HS256"
    os.environ["REVIEWPOINT_JWT_EXPIRE_MINUTES"] = "60"
    
    settings = get_settings()
    print(f"JWT_SECRET_KEY set: {bool(settings.jwt_secret_key)}")
    print(f"JWT_ALGORITHM: {settings.jwt_algorithm}")
    print(f"JWT_EXPIRE_MINUTES: {settings.jwt_expire_minutes}")
    
    # Create a test token
    data = {"sub": "1", "role": "user"}
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=settings.jwt_expire_minutes)
    to_encode["exp"] = int(expire.timestamp())
    to_encode["iat"] = int(datetime.now(UTC).timestamp())
    to_encode["jti"] = str(uuid.uuid4())
    
    print(f"Token payload: {to_encode}")
    
    # Encode the token
    try:
        token = jwt.encode(
            to_encode,
            str(settings.jwt_secret_key),
            algorithm=settings.jwt_algorithm,
        )
        print(f"Token created successfully: {token[:50]}...")
        print(f"Token length: {len(token)}")
    except Exception as e:
        print(f"ERROR creating token: {e}")
        return
    
    # Try to decode the token
    try:
        payload = jwt.decode(
            token, str(settings.jwt_secret_key), algorithms=[settings.jwt_algorithm]
        )
        print(f"Token decoded successfully: {payload}")
        jti = payload.get("jti") or token
        exp = payload.get("exp")
        print(f"JTI: {jti}")
        print(f"EXP: {exp}")
        if exp:
            expires_at = datetime.fromtimestamp(exp, tz=UTC)
            print(f"Expires at: {expires_at}")
    except ExpiredSignatureError as e:
        print(f"ERROR: Token expired: {e}")
    except JWTError as e:
        print(f"ERROR: JWT error: {e}")
    except Exception as e:
        print(f"ERROR decoding token: {e} ({type(e).__name__})")

if __name__ == "__main__":
    debug_jwt()

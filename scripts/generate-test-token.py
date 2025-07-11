#!/usr/bin/env python3
"""Generate a valid JWT token for testing WebSocket connection."""

import sys
import os
import json
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, 'backend/src')

# Load environment from .env file
from dotenv import load_dotenv
load_dotenv('backend/config/.env')

# Set additional environment variables
os.environ['REVIEWPOINT_JWT_SECRET_KEY'] = 'testsecret'
os.environ['REVIEWPOINT_JWT_ALGORITHM'] = 'HS256'
os.environ['REVIEWPOINT_JWT_EXPIRE_MINUTES'] = '30'

try:
    from src.core.security import create_access_token
    
    # Create a token for a test user
    token_data = {
        "sub": "1",  # user ID
        "email": "test@example.com",
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    
    token = create_access_token(token_data)
    print(f"Generated token: {token}")
    
    # Test the WebSocket URL
    print(f"\nTest WebSocket connection with:")
    print(f"  curl -s -i -N -H \"Connection: Upgrade\" -H \"Upgrade: websocket\" -H \"Sec-WebSocket-Version: 13\" -H \"Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\" http://localhost:8000/api/v1/ws/{token}")
    
except Exception as e:
    print(f"Error generating token: {e}")
    import traceback
    traceback.print_exc()

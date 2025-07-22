# core/security.py - JWT Authentication and Token Management

## Purpose

The `core/security.py` module provides comprehensive JWT (JSON Web Token) authentication and token management for the ReViewPoint platform. It implements secure token creation, validation, and verification with support for both access and refresh tokens, authentication bypassing for development, and robust error handling with comprehensive logging.

## File Location

```
backend/src/core/security.py
```

## Architecture Overview

### Component Responsibilities

1. **Token Creation**: Secure JWT access and refresh token generation with unique identifiers
2. **Token Validation**: Comprehensive token verification with format and signature validation
3. **Development Support**: Authentication bypass for development environments
4. **Security Features**: Token blacklisting support, expiration handling, and claim validation
5. **Error Management**: Detailed error handling with security-conscious logging

### Key Design Patterns

- **Factory Pattern**: Token creation with standardized payload structure
- **Validation Pattern**: Multi-layer token validation with format, signature, and claim verification
- **Configuration Pattern**: Settings-driven security parameters and algorithms
- **Error Handling Pattern**: Comprehensive exception handling with security logging

## Source Code Analysis

### Module Imports and Dependencies

```python
"""JWT creation and validation utilities for authentication."""

import uuid
from collections.abc import Mapping, MutableMapping, Sequence
from datetime import UTC, datetime, timedelta
from typing import (
    TypedDict,
    cast,
)

from jose import JWTError, jwt
from loguru import logger

from src.core.config import get_settings
```

**Technical Implementation:**

- **UUID Generation**: Unique token identifiers for blacklisting support
- **Modern Collections**: Collections.abc for future-compatible type hints
- **UTC Timezone**: Proper timezone-aware datetime handling for security
- **Type Safety**: Comprehensive typing with TypedDict for structured payloads
- **JWT Library**: Python-jose for secure JWT operations
- **Configuration Integration**: Settings-driven security parameters

### JWT Payload Type Definition

```python
class JWTPayload(TypedDict, total=False):
    sub: str
    role: str
    is_authenticated: bool
    exp: int
    iat: int
    jti: str
    # Add other claims as needed
```

**Technical Implementation:**

- **Structured Payload**: TypedDict for type-safe JWT payload definition
- **Standard Claims**: JWT standard claims (sub, exp, iat, jti) for interoperability
- **Custom Claims**: Application-specific claims (role, is_authenticated)
- **Flexible Schema**: total=False allows optional claims for different token types
- **Extension Ready**: Comments indicate future claim additions

### Module Exports

```python
__all__: Sequence[str] = (
    "create_access_token",
    "create_refresh_token",
    "decode_access_token",
    "verify_access_token",
)
```

**Technical Implementation:**

- **Explicit Exports**: Clear public API definition with **all** tuple
- **API Documentation**: Self-documenting public interface
- **Import Control**: Prevents accidental import of internal functions
- **Type Safety**: Sequence[str] type annotation for exports

### Access Token Creation

```python
def create_access_token(data: Mapping[str, str | int | bool]) -> str:
    """Create a JWT access token with the given data payload.
    Uses config-driven secret, expiry, and algorithm.
    Never log or expose the token.
    Adds a unique jti for blacklisting support.

    Raises:
        ValueError: If the JWT secret key is not configured.
        JWTError: If JWT encoding fails.
        RuntimeError: If token creation fails for unknown reasons.
    """
    to_encode: MutableMapping[str, str | int | bool | datetime] = dict(data)
    settings = get_settings()
    
    # Set expiration time
    expire: datetime = datetime.now(UTC) + timedelta(
        minutes=settings.jwt_expire_minutes,
    )
    to_encode["exp"] = expire
    to_encode["iat"] = int(datetime.now(UTC).timestamp())
    to_encode["jti"] = str(uuid.uuid4())
    
    # Validate secret key configuration
    if not settings.jwt_secret_key:
        logger.error("JWT secret key is not configured. Cannot create access token.")
        raise ValueError("JWT secret key is not configured.")

    try:
        token: str = jwt.encode(
            to_encode,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )
        logger.debug(
            "JWT access token created (claims: {})",
            {k: v for k, v in to_encode.items() if k != "exp"},
        )
        return str(token)
    except ValueError as e:
        logger.error("ValueError during JWT access token creation: {}", str(e))
        raise
    except JWTError as e:
        logger.error("JWTError during JWT access token creation: {}", str(e))
        raise
    raise RuntimeError("Failed to create access token")
```

**Technical Implementation:**

- **Configuration-Driven**: Uses settings for secret key, algorithm, and expiration time
- **Standard Claims**: Automatic addition of exp (expiration), iat (issued at), jti (JWT ID)
- **UUID Token ID**: Unique jti claim for token blacklisting and tracking
- **Security Validation**: Early validation of secret key configuration
- **Comprehensive Error Handling**: Specific exception types for different failure scenarios
- **Security Logging**: Debug logging excludes sensitive expiration information
- **Type Safety**: Explicit type annotations for all variables and return values

### Access Token Verification

```python
def verify_access_token(token: str) -> JWTPayload:
    """Validate a JWT access token and return the decoded payload.
    If authentication is disabled, return a default admin payload.

    Raises:
        JWTError: If the token is invalid or cannot be decoded.
        ValueError: If the JWT secret key is not configured.
        TypeError: If the decoded payload is not a dictionary.
        RuntimeError: If verification fails for unknown reasons.
    """
    settings = get_settings()
    
    # Development authentication bypass
    if not settings.auth_enabled:
        logger.warning(
            "Authentication is DISABLED! Bypassing token verification and returning default admin payload.",
        )
        now: datetime = datetime.now(UTC)
        return JWTPayload(
            sub="dev-user",
            role="admin",
            is_authenticated=True,
            exp=int((now + timedelta(hours=24)).timestamp()),
        )

    # Early token format validation
    if not token or not isinstance(token, str) or token.count(".") != 2:
        logger.warning("JWT access token validation failed: Malformed token format")
        raise JWTError("Invalid token format")

    # Secret key validation
    if not settings.jwt_secret_key:
        logger.error("JWT secret key is not configured. Cannot verify access token.")
        raise ValueError("JWT secret key is not configured.")
    
    try:
        payload: dict[str, object] = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        
        if not isinstance(payload, dict):
            raise TypeError("Decoded JWT payload is not a dictionary")
        
        logger.debug(
            "JWT access token successfully verified (claims: {})",
            {k: v for k, v in payload.items() if k != "exp"},
        )
        
        # Cast to JWTPayload for type safety
        return cast("JWTPayload", payload)
        
    except JWTError as e:
        logger.warning("JWT access token validation failed: {}", str(e))
        raise
    except Exception as e:
        logger.error("Unexpected error during JWT validation: {}", str(e))
        raise
    raise RuntimeError("Failed to verify access token")
```

**Technical Implementation:**

- **Development Bypass**: Authentication disabled mode returns admin payload for development
- **Multi-Layer Validation**: Format validation, secret key validation, signature validation
- **JWT Format Check**: Early validation of JWT structure (3 parts separated by dots)
- **Type Safety**: Runtime type checking of decoded payload structure
- **Security Logging**: Appropriate log levels for different validation failures
- **Error Classification**: Specific exception types for different validation failures
- **Defensive Programming**: Guard clauses and early validation prevent deeper errors

### Token Decode Compatibility

```python
def decode_access_token(token: str) -> JWTPayload:
    """Alias for verify_access_token for backward compatibility.
    Decode and validate a JWT access token and return the payload.

    Args:
        token: The JWT token to decode and validate

    Returns:
        JWTPayload: The decoded and validated token payload

    Raises:
        JWTError: If the token is invalid or cannot be decoded.
        ValueError: If the JWT secret key is not configured.
        TypeError: If the decoded payload is not a dictionary.
        RuntimeError: If verification fails for unknown reasons.
    """
    return verify_access_token(token)
```

**Technical Implementation:**

- **Backward Compatibility**: Alias function maintains API compatibility
- **Single Responsibility**: Delegates to main verification function
- **Complete Documentation**: Full docstring with args, returns, and raises
- **Type Safety**: Maintains type annotations from delegated function

### Refresh Token Creation

```python
def create_refresh_token(data: Mapping[str, str | int | bool]) -> str:
    """Create a JWT refresh token with the given data payload.
    Uses config-driven secret, expiry, and algorithm.
    Refresh tokens typically have a longer expiry than access tokens.
    Adds a unique jti for blacklisting support.

    Raises:
        ValueError: If the JWT secret key is not configured.
        JWTError: If JWT encoding fails.
        RuntimeError: If token creation fails for unknown reasons.
    """
    settings = get_settings()
    to_encode: MutableMapping[str, str | int | bool | datetime] = dict(data)
    
    # Longer expiration for refresh tokens (7 days)
    expire: datetime = datetime.now(UTC) + timedelta(days=7)
    to_encode["exp"] = expire
    to_encode["iat"] = int(datetime.now(UTC).timestamp())
    to_encode["jti"] = str(uuid.uuid4())
    
    if not settings.jwt_secret_key:
        logger.error("JWT secret key is not configured. Cannot create refresh token.")
        raise ValueError("JWT secret key is not configured.")
        
    try:
        token: str = jwt.encode(
            to_encode,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )
        logger.debug(
            "JWT refresh token created (claims: {})",
            {k: v for k, v in to_encode.items() if k != "exp"},
        )
        return str(token)
    except ValueError as e:
        logger.error("ValueError during JWT refresh token creation: {}", str(e))
        raise
    except JWTError as e:
        logger.error("JWTError during JWT refresh token creation: {}", str(e))
        raise
    raise RuntimeError("Failed to create refresh token")
```

**Technical Implementation:**

- **Extended Expiration**: 7-day expiration for refresh tokens vs minutes for access tokens
- **Consistent Structure**: Same claims structure as access tokens for uniformity
- **UUID Token ID**: Unique jti for refresh token tracking and blacklisting
- **Configuration Reuse**: Same secret key and algorithm as access tokens
- **Error Handling**: Same comprehensive error handling pattern as access tokens
- **Security Logging**: Debug logging excludes sensitive token information

### Refresh Token Verification

```python
def verify_refresh_token(token: str) -> JWTPayload:
    """Validate a JWT refresh token and return the decoded payload.
    Uses the same secret and algorithm as create_refresh_token.

    Raises:
        JWTError: If the token is invalid or cannot be decoded.
        ValueError: If the JWT secret key is not configured or required claims are missing/expired.
        TypeError: If the decoded payload is not a dictionary.
    """
    settings = get_settings()
    
    if not settings.jwt_secret_key:
        logger.error("JWT secret key is not configured. Cannot verify refresh token.")
        raise ValueError("JWT secret key is not configured.")
        
    try:
        payload: dict[str, object] = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        
        if not isinstance(payload, dict):
            raise TypeError("Decoded JWT payload is not a dictionary")
        
        # Ensure required claims are present
        if not ("sub" in payload and "jti" in payload and "exp" in payload):
            raise ValueError("Refresh token missing required claims (sub, jti, exp)")
        
        # Check expiration manually
        exp_val: int = (
            int(payload["exp"])
            if isinstance(payload["exp"], int)
            else int(str(payload["exp"]))
        )
        if exp_val < int(datetime.now(UTC).timestamp()):
            raise ValueError("Refresh token is expired")
        
        return cast("JWTPayload", payload)
        
    except JWTError as e:
        logger.error("JWT refresh token verification failed: %s", str(e))
        raise ValueError("Invalid or expired refresh token") from e
    except Exception as e:
        logger.error("JWT refresh token verification failed: %s", str(e))
        raise ValueError("Invalid or expired refresh token") from e
```

**Technical Implementation:**

- **Required Claims Validation**: Explicit validation of sub, jti, and exp claims
- **Manual Expiration Check**: Additional expiration validation beyond JWT library
- **Type Coercion**: Safe handling of exp claim type conversion
- **Error Wrapping**: JWTError wrapped in ValueError for consistent API
- **Exception Chaining**: Preserves original exception context with from clause
- **Security Logging**: Error-level logging for refresh token verification failures

## Integration Patterns

### FastAPI Authentication Dependency

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from core.security import verify_access_token, JWTPayload

security = HTTPBearer()

async def get_current_user(token: str = Depends(security)) -> JWTPayload:
    """FastAPI dependency for authenticated user extraction."""
    try:
        payload = verify_access_token(token.credentials)
        return payload
    except (JWTError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

# Usage in route
@app.get("/protected")
async def protected_route(user: JWTPayload = Depends(get_current_user)):
    return {"user_id": user["sub"], "role": user.get("role")}
```

### User Authentication Service

```python
from core.security import create_access_token, create_refresh_token

class AuthenticationService:
    """Service for user authentication and token management."""
    
    async def authenticate_user(
        self, 
        email: str, 
        password: str
    ) -> tuple[str, str]:
        """Authenticate user and return access and refresh tokens."""
        # Validate user credentials (implementation omitted)
        user = await self.validate_credentials(email, password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Create token payload
        token_data = {
            "sub": str(user.id),
            "role": user.role,
            "is_authenticated": True
        }
        
        # Generate tokens
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        return access_token, refresh_token
```

### Token Refresh Implementation

```python
from core.security import verify_refresh_token, create_access_token

async def refresh_access_token(refresh_token: str) -> str:
    """Refresh access token using valid refresh token."""
    try:
        # Verify refresh token
        payload = verify_refresh_token(refresh_token)
        
        # Create new access token with same payload
        new_token_data = {
            "sub": payload["sub"],
            "role": payload.get("role"),
            "is_authenticated": payload.get("is_authenticated", True)
        }
        
        return create_access_token(new_token_data)
        
    except (JWTError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        ) from e
```

### Role-Based Access Control

```python
from functools import wraps
from fastapi import HTTPException, status

def require_role(required_role: str):
    """Decorator for role-based access control."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, user: JWTPayload = Depends(get_current_user), **kwargs):
            user_role = user.get("role")
            
            if user_role != required_role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Required role: {required_role}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Usage
@app.get("/admin")
@require_role("admin")
async def admin_endpoint():
    return {"message": "Admin access granted"}
```

## Security Features

### Token Blacklisting Support

```python
# Token blacklisting with Redis
import redis
from core.security import verify_access_token

redis_client = redis.Redis(host='localhost', port=6379, db=0)

async def is_token_blacklisted(token: str) -> bool:
    """Check if token is blacklisted."""
    try:
        payload = verify_access_token(token)
        jti = payload.get("jti")
        
        if jti:
            return redis_client.exists(f"blacklist:{jti}") == 1
        return False
    except (JWTError, ValueError):
        return True  # Invalid tokens are considered blacklisted

async def blacklist_token(token: str):
    """Add token to blacklist."""
    try:
        payload = verify_access_token(token)
        jti = payload.get("jti")
        exp = payload.get("exp")
        
        if jti and exp:
            # Set TTL based on token expiration
            ttl = exp - int(datetime.now(UTC).timestamp())
            if ttl > 0:
                redis_client.setex(f"blacklist:{jti}", ttl, "1")
    except (JWTError, ValueError):
        pass  # Invalid tokens don't need blacklisting
```

### Development Authentication Bypass

```python
# Environment-based authentication bypass
from core.config import get_settings

def setup_development_auth():
    """Configure development authentication settings."""
    settings = get_settings()
    
    if settings.environment == "development":
        # Authentication bypass is handled in verify_access_token
        logger.info("Development mode: Authentication bypass enabled")
    else:
        logger.info("Production mode: Full authentication required")
```

### Token Validation Middleware

```python
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

class TokenValidationMiddleware(BaseHTTPMiddleware):
    """Middleware for automatic token validation and blacklist checking."""
    
    async def dispatch(self, request: Request, call_next):
        # Skip validation for public endpoints
        if request.url.path in ["/docs", "/health", "/login"]:
            return await call_next(request)
        
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
            
            try:
                # Verify token
                payload = verify_access_token(token)
                
                # Check blacklist
                if await is_token_blacklisted(token):
                    return Response(
                        content="Token has been revoked",
                        status_code=401
                    )
                
                # Add user info to request state
                request.state.user = payload
                
            except (JWTError, ValueError):
                return Response(
                    content="Invalid token",
                    status_code=401
                )
        
        return await call_next(request)
```

## Error Handling

### Comprehensive Exception Handling

```python
def handle_token_errors(func):
    """Decorator for consistent token error handling."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Authentication service configuration error"
            )
        except JWTError as e:
            logger.warning(f"Token validation error: {e}")
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token"
            )
        except TypeError as e:
            logger.error(f"Token format error: {e}")
            raise HTTPException(
                status_code=401,
                detail="Malformed token"
            )
        except Exception as e:
            logger.error(f"Unexpected authentication error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Authentication service error"
            )
    return wrapper
```

### Token Validation with Retry

```python
import asyncio
from typing import Optional

async def validate_token_with_retry(
    token: str, 
    max_retries: int = 3
) -> Optional[JWTPayload]:
    """Validate token with retry logic for transient failures."""
    for attempt in range(max_retries):
        try:
            return verify_access_token(token)
        except JWTError as e:
            # Don't retry for invalid tokens
            logger.warning(f"Token validation failed: {e}")
            return None
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"Token validation failed after {max_retries} attempts: {e}")
                return None
            
            logger.warning(f"Token validation attempt {attempt + 1} failed, retrying: {e}")
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    return None
```

## Security Considerations

### Token Security Best Practices

1. **Secret Key Management**: Strong secret keys from environment variables
2. **Algorithm Whitelist**: Specific algorithm configuration prevents algorithm confusion
3. **Token Expiration**: Short-lived access tokens with longer refresh tokens
4. **Unique Token IDs**: JTI claims enable token tracking and blacklisting
5. **Secure Logging**: Tokens never logged, only metadata and claims

### Authentication Flow Security

1. **Multi-Layer Validation**: Format, signature, and claim validation
2. **Early Validation**: Format checks prevent unnecessary processing
3. **Error Classification**: Specific error types for different failure modes
4. **Development Safety**: Authentication bypass only in development mode
5. **Type Safety**: Runtime type checking prevents payload corruption

### Production Security

1. **Configuration Validation**: Early validation of security configuration
2. **Error Isolation**: Security errors don't expose internal details
3. **Audit Logging**: Comprehensive logging for security monitoring
4. **Token Blacklisting**: Support for token revocation and tracking
5. **Refresh Token Security**: Longer expiration with separate validation

This comprehensive security module provides the foundation for authentication and authorization across the ReViewPoint platform, ensuring secure token management with flexibility for development workflows and robust production security.

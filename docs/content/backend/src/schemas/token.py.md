# Token Schema Module

## Overview

The `token.py` schema module provides comprehensive Pydantic model definitions for JWT token operations in the ReViewPoint application. This module implements token authentication, refresh token handling, and token data validation with proper type safety and security considerations for all authentication token-related operations throughout the API.

**Key Features:**

- Complete JWT token response schemas
- Refresh token request validation
- Token payload data structures
- Type-safe authentication flows
- Security-focused token handling
- Comprehensive field documentation for API generation

## Module Structure

```python
"""Token-related schemas for authentication and authorization."""

from datetime import datetime
from pydantic import BaseModel, Field
```

### Core Dependencies

#### External Dependencies

- `datetime` - Standard library datetime support for token expiration
- `pydantic` - Core validation and serialization framework
- `pydantic.BaseModel` - Base class for schema definitions
- `pydantic.Field` - Field validation and metadata

## Authentication Token Schemas

### 1. Token Response Schema

#### TokenResponse Class

```python
class TokenResponse(BaseModel):
    """Response schema for authentication endpoints that return tokens."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int | None = Field(None, description="Token expiration time in seconds")
```

**Purpose:** Standard response schema for authentication endpoints that issue JWT tokens.

**Key Features:**

- **Complete Token Response:** Both access and refresh tokens included
- **Token Type Specification:** OAuth2-compliant bearer token type
- **Expiration Information:** Optional expiration time in seconds
- **API Documentation:** Comprehensive field descriptions for OpenAPI
- **Type Safety:** Strict typing with optional expiration field

**Field Definitions:**

- **`access_token: str`** - JWT access token for API authentication
- **`refresh_token: str`** - JWT refresh token for token renewal
- **`token_type: str`** - Token type, defaults to "bearer" (OAuth2 standard)
- **`expires_in: int | None`** - Token expiration time in seconds (optional)

**Usage Contexts:**

- Login endpoint responses
- Registration endpoint responses
- Token refresh endpoint responses
- OAuth2-compliant authentication flows

**Authentication Flow Integration:**

```python
# Login endpoint returning tokens
@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest) -> TokenResponse:
    tokens = await auth_service.authenticate(credentials)
    return TokenResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        expires_in=3600  # 1 hour
    )
```

### 2. Refresh Token Request Schema

#### RefreshTokenRequest Class

```python
class RefreshTokenRequest(BaseModel):
    """Request schema for refresh token endpoint."""

    refresh_token: str = Field(
        ..., description="Refresh token to exchange for new access token"
    )
```

**Purpose:** Validates refresh token requests for token renewal operations.

**Key Features:**

- **Single Field Schema:** Only requires refresh token for renewal
- **Required Validation:** Refresh token must be provided
- **Security Focus:** Simple validation for token refresh flow
- **Clear Documentation:** Field description for API understanding

**Security Considerations:**

- Refresh token validation happens in service layer
- Schema ensures token is provided as string
- Additional validation (expiration, blacklist) in business logic
- Used for secure token renewal without re-authentication

**Token Refresh Flow:**

```python
# Token refresh endpoint
@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest) -> TokenResponse:
    new_tokens = await auth_service.refresh_tokens(request.refresh_token)
    return TokenResponse(
        access_token=new_tokens.access_token,
        refresh_token=new_tokens.refresh_token,
        expires_in=3600
    )
```

## Token Payload Schema

### TokenData Class

```python
class TokenData(BaseModel):
    """Token payload data schema."""

    user_id: str = Field(..., description="User ID from token")
    email: str | None = Field(None, description="User email from token")
    exp: datetime | None = Field(None, description="Token expiration timestamp")
    jti: str | None = Field(None, description="JWT ID for token tracking")
```

**Purpose:** Represents the decoded JWT token payload data for internal use.

**Key Features:**

- **User Identification:** User ID as primary identifier
- **Optional Email:** Email for additional user context
- **Expiration Tracking:** Token expiration timestamp
- **Token Tracking:** JWT ID for token management and blacklisting
- **Type Safety:** Union types for optional fields

**Field Definitions:**

- **`user_id: str`** - User identifier from token claims (required)
- **`email: str | None`** - User email from token claims (optional)
- **`exp: datetime | None`** - Token expiration timestamp (optional)
- **`jti: str | None`** - JWT ID for token tracking and revocation (optional)

**JWT Integration:**

```python
# Decoding JWT token to TokenData
def decode_access_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return TokenData(
            user_id=payload["sub"],
            email=payload.get("email"),
            exp=datetime.fromtimestamp(payload["exp"]) if "exp" in payload else None,
            jti=payload.get("jti")
        )
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

## Token Type Safety

### String-Based User ID

```python
user_id: str = Field(..., description="User ID from token")
```

**Design Decision:**

- JWT standard uses string claims
- Consistent with JWT "sub" (subject) claim
- Allows for UUID or integer ID formats
- Maintains compatibility with JWT libraries

### Optional Token Fields

```python
email: str | None = Field(None, description="User email from token")
exp: datetime | None = Field(None, description="Token expiration timestamp")
jti: str | None = Field(None, description="JWT ID for token tracking")
```

**Benefits:**

- Flexible token payload structure
- Not all tokens need all fields
- Backwards compatibility with minimal tokens
- Clear indication of optional vs required data

## Authentication Security Patterns

### Token Expiration Handling

```python
async def validate_token_expiration(token_data: TokenData) -> bool:
    if token_data.exp is None:
        return True  # No expiration set

    if token_data.exp < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Token expired")

    return True
```

### Token Blacklisting Integration

```python
async def check_token_blacklist(token_data: TokenData) -> bool:
    if token_data.jti is None:
        return True  # No JTI, cannot be blacklisted

    is_blacklisted = await blacklist_service.is_token_blacklisted(token_data.jti)
    if is_blacklisted:
        raise HTTPException(status_code=401, detail="Token revoked")

    return True
```

### User Context Resolution

```python
async def get_current_user(token_data: TokenData) -> User:
    # Convert string user_id to appropriate type
    try:
        user_id = int(token_data.user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid user ID in token")

    user = await user_repository.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user
```

## API Integration Examples

### Authentication Endpoints

```python
@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest) -> TokenResponse:
    # Validate credentials
    user = await auth_service.authenticate_user(
        credentials.email,
        credentials.password
    )

    # Generate tokens
    access_token = await jwt_service.create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )
    refresh_token = await jwt_service.create_refresh_token(
        data={"sub": str(user.id)}
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest) -> TokenResponse:
    # Validate refresh token
    token_data = await jwt_service.verify_refresh_token(request.refresh_token)

    # Generate new tokens
    new_access_token = await jwt_service.create_access_token(
        data={"sub": token_data.user_id}
    )
    new_refresh_token = await jwt_service.create_refresh_token(
        data={"sub": token_data.user_id}
    )

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
```

### Token Validation Middleware

```python
async def get_current_user_from_token(
    token: str = Depends(oauth2_scheme)
) -> User:
    # Decode token to schema
    token_data = jwt_service.decode_access_token(token)

    # Validate expiration
    await validate_token_expiration(token_data)

    # Check blacklist
    await check_token_blacklist(token_data)

    # Get user
    return await get_current_user(token_data)
```

## Error Handling

### Token Validation Errors

```python
try:
    token_response = TokenResponse(**response_data)
except ValidationError as e:
    for error in e.errors():
        field = error['loc'][0]

        if field == 'access_token':
            raise HTTPException(
                status_code=500,
                detail="Failed to generate access token"
            )
        elif field == 'refresh_token':
            raise HTTPException(
                status_code=500,
                detail="Failed to generate refresh token"
            )
```

### Token Data Validation

```python
def validate_token_payload(payload: dict) -> TokenData:
    try:
        return TokenData(**payload)
    except ValidationError as e:
        # Log validation errors for debugging
        logger.error(f"Invalid token payload: {e}")
        raise HTTPException(
            status_code=401,
            detail="Invalid token format"
        )
```

## Testing Strategies

### Schema Validation Testing

```python
def test_token_response_valid():
    data = {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "token_type": "bearer",
        "expires_in": 3600
    }
    token_response = TokenResponse(**data)
    assert token_response.access_token.startswith("eyJ")
    assert token_response.token_type == "bearer"
    assert token_response.expires_in == 3600

def test_token_response_default_type():
    data = {
        "access_token": "access_token_value",
        "refresh_token": "refresh_token_value"
        # token_type should default to "bearer"
    }
    token_response = TokenResponse(**data)
    assert token_response.token_type == "bearer"

def test_refresh_token_request_valid():
    data = {"refresh_token": "valid_refresh_token"}
    request = RefreshTokenRequest(**data)
    assert request.refresh_token == "valid_refresh_token"

def test_token_data_minimal():
    data = {"user_id": "123"}
    token_data = TokenData(**data)
    assert token_data.user_id == "123"
    assert token_data.email is None
    assert token_data.exp is None
    assert token_data.jti is None

def test_token_data_complete():
    data = {
        "user_id": "123",
        "email": "user@example.com",
        "exp": datetime(2023, 12, 31, 23, 59, 59),
        "jti": "unique-jwt-id"
    }
    token_data = TokenData(**data)
    assert token_data.user_id == "123"
    assert token_data.email == "user@example.com"
    assert token_data.jti == "unique-jwt-id"
```

### Mock Data Factories

```python
def create_token_response_data():
    return {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjMifQ.hash",
        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjMifQ.hash",
        "token_type": "bearer",
        "expires_in": 3600
    }

def create_token_data():
    return {
        "user_id": "123",
        "email": "user@example.com",
        "exp": datetime.utcnow() + timedelta(hours=1),
        "jti": "unique-jwt-id-123"
    }
```

## Performance Considerations

### Lightweight Schemas

- **Minimal Fields:** Only essential token information included
- **String Types:** Efficient string handling for tokens
- **Optional Fields:** Memory-efficient optional field handling
- **Fast Validation:** Simple validation rules for quick processing

### Token Processing

- **Direct Field Access:** No complex validation or transformation
- **UTC Timestamps:** Consistent timezone handling
- **String-Based IDs:** Compatible with JWT string claims
- **Efficient Serialization:** Direct JSON mapping

## Security Best Practices

### Token Schema Security

- **No Sensitive Data:** Tokens are opaque to schema validation
- **Required Fields:** Critical fields marked as required
- **Type Safety:** Strict typing prevents injection
- **Expiration Handling:** Proper datetime handling for security

### JWT Security Integration

- **JTI Support:** Token tracking for revocation
- **Expiration Validation:** Timestamp-based expiration
- **Blacklist Compatibility:** JTI field for blacklisting
- **User Context:** Secure user ID handling

## Related Modules

### **Core Dependencies**

- **`src.core.security`** - JWT token generation and validation
- **`src.api.v1.auth`** - Authentication endpoints using token schemas

### **Integration Points**

- **`src.services.auth`** - Authentication service using token schemas
- **`src.repositories.blacklisted_token`** - Token blacklist operations
- **`src.utils.security`** - Security utilities for token handling

### **External Dependencies**

- **`datetime`** - Standard library datetime support
- **`pydantic`** - Core validation and serialization framework
- **`python-jose`** - JWT library for token operations

## Configuration Dependencies

- JWT secret key configuration
- Token expiration time settings
- Token algorithm configuration (HS256, RS256, etc.)
- Blacklist storage configuration

## Summary

The `token.py` schema module provides comprehensive, security-focused schemas for JWT token operations in the ReViewPoint application. Through well-structured Pydantic models with proper validation, type safety, and security considerations, it ensures token data integrity and provides excellent developer experience for authentication flows.

Key strengths include comprehensive token response schemas with OAuth2 compliance, secure token payload handling with optional fields, type-safe authentication flows, proper expiration and blacklist support, and clear API contract definitions for authentication endpoints. The module serves as the foundation for secure authentication token handling across the entire application.

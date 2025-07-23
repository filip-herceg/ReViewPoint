# Token Schema Documentation

## Purpose

The `token.py` schema module defines Pydantic data validation models for JWT token management in the ReViewPoint application. This schema provides structured validation, serialization, and type safety for authentication tokens, refresh tokens, and token-based security operations, ensuring consistent token handling across the API authentication layer.

## Architecture

The schema follows a comprehensive token validation pattern:

- **Token Response Layer**: JWT access and refresh token delivery
- **Token Request Layer**: Refresh token validation and processing
- **Token Data Layer**: Internal JWT payload structure and claims
- **Type Safety Layer**: Strong typing with Field validation and documentation
- **Security Layer**: Token expiration and scope management
- **API Serialization Layer**: Optimized JSON responses for authentication flows

## Core Schema Classes

### `TokenResponse`

Comprehensive authentication token response with access and refresh tokens.

```python
# Example usage - Login response
login_response = TokenResponse(
    access_token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    refresh_token="dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4gZXhhbXBsZQ...",
    token_type="bearer",
    expires_in=3600
)

# API response usage
return login_response.model_dump()
```

**Field Specifications:**

- `access_token: str` - JWT access token for API authentication
- `refresh_token: str` - Long-lived token for access token renewal
- `token_type: str` - Token type specification (typically "bearer")
- `expires_in: int` - Access token expiration time in seconds

### `RefreshTokenRequest`

Token refresh request validation for secure token renewal.

```python
# Example usage - Token refresh
refresh_request = RefreshTokenRequest(
    refresh_token="dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4gZXhhbXBsZQ..."
)

# Validation in endpoint
async def refresh_token(request: RefreshTokenRequest):
    new_tokens = await auth_service.refresh_tokens(request.refresh_token)
    return TokenResponse(**new_tokens)
```

**Field Specifications:**

- `refresh_token: str` - Valid refresh token for token renewal

### `TokenData`

Internal JWT token payload structure for claims validation.

```python
# Example usage - Token decoding
token_data = TokenData(
    username="user@example.com",
    scopes=["read", "write"],
    sub="12345",
    exp=1640995200
)

# Token validation usage
def validate_token_payload(payload: dict) -> TokenData:
    return TokenData(**payload)
```

**Field Specifications:**

- `username: Optional[str]` - Username from token claims (nullable)
- `scopes: list[str]` - Permission scopes granted to token
- `sub: Optional[str]` - Subject identifier (user ID) from token
- `exp: Optional[int]` - Token expiration timestamp

## Validation Features

### Token Response Validation

**Access Token Validation:**

```python
access_token: str = Field(..., description="JWT access token")
```

- **Required Field**: Cannot be null or empty
- **String Type**: Base64-encoded JWT format
- **Security**: Contains encrypted user claims and permissions
- **Short-lived**: Typically 15 minutes to 1 hour expiration

**Refresh Token Validation:**

```python
refresh_token: str = Field(..., description="Refresh token")
```

- **Required Field**: Cannot be null or empty
- **Long-lived**: Typically 7-30 days expiration
- **Single Use**: Often invalidated after use for security
- **Secure Storage**: Should be stored securely on client

**Token Type Specification:**

```python
token_type: str = Field(default="bearer", description="Type of the token")
```

- **Default Value**: "bearer" (OAuth 2.0 standard)
- **Standard Compliance**: Follows RFC 6750 Bearer Token standard
- **Case Insensitive**: Should be treated case-insensitively
- **Authorization Header**: Used in "Authorization: Bearer {token}" format

**Expiration Time:**

```python
expires_in: int = Field(..., description="Token expiration time in seconds")
```

- **Integer Type**: Seconds until token expiration
- **Required Field**: Client needs to know when to refresh
- **Countdown Timer**: Starts from response time
- **Security**: Enables proper token lifecycle management

### Refresh Request Validation

**Refresh Token Input:**

```python
refresh_token: str = Field(..., description="Refresh token")
```

- **Required Field**: Must provide valid refresh token
- **Validation**: Server validates against stored tokens
- **Security**: Should match user session and not be blacklisted
- **Single Use**: Often invalidated after successful refresh

### Token Data Validation

**Username Claims:**

```python
username: Optional[str] = Field(None, description="Username from token")
```

- **Optional Field**: May not be present in all token types
- **Nullable**: Can be None for certain token scopes
- **Identity**: Primary user identifier in token claims
- **Validation**: Should match registered user accounts

**Scope Management:**

```python
scopes: list[str] = Field(default_factory=list, description="List of token scopes")
```

- **List Type**: Multiple permission scopes supported
- **Default Empty**: New tokens start with no scopes
- **Permission Model**: Enables fine-grained access control
- **Standard Compliance**: Follows OAuth 2.0 scope specification

**Subject Identifier:**

```python
sub: Optional[str] = Field(None, description="Subject (user ID)")
```

- **Optional Field**: May not be present in all contexts
- **User Reference**: Links token to specific user account
- **JWT Standard**: Standard "sub" claim from JWT specification
- **String Type**: Flexible identifier format

**Expiration Timestamp:**

```python
exp: Optional[int] = Field(None, description="Expiration timestamp")
```

- **Optional Field**: May not be present in all token types
- **Unix Timestamp**: Standard Unix epoch time format
- **JWT Standard**: Standard "exp" claim from JWT specification
- **Validation**: Should be validated against current time

## Usage Patterns

### Authentication Flow

```python
async def login_endpoint(credentials: UserLoginRequest):
    # Validate user credentials
    user = await auth_service.authenticate_user(
        email=credentials.email,
        password=credentials.password
    )
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generate tokens
    access_token = await token_service.create_access_token(
        data={"sub": str(user.id), "username": user.email},
        expires_delta=timedelta(hours=1)
    )
    
    refresh_token = await token_service.create_refresh_token(user.id)
    
    # Return token response
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=3600  # 1 hour
    )
```

### Token Refresh Flow

```python
async def refresh_token_endpoint(request: RefreshTokenRequest):
    try:
        # Validate refresh token
        user_id = await token_service.validate_refresh_token(
            request.refresh_token
        )
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        # Get user details
        user = await user_service.get_user(user_id)
        
        # Generate new tokens
        new_access_token = await token_service.create_access_token(
            data={"sub": str(user.id), "username": user.email},
            expires_delta=timedelta(hours=1)
        )
        
        new_refresh_token = await token_service.create_refresh_token(user.id)
        
        # Invalidate old refresh token
        await token_service.blacklist_token(request.refresh_token)
        
        # Return new tokens
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=3600
        )
        
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(status_code=401, detail="Token refresh failed")
```

### Token Validation

```python
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode token payload
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Validate token data
        token_data = TokenData(
            username=payload.get("username"),
            sub=payload.get("sub"),
            exp=payload.get("exp"),
            scopes=payload.get("scopes", [])
        )
        
        if token_data.username is None:
            raise credentials_exception
            
        # Check token expiration
        if token_data.exp and token_data.exp < time.time():
            raise HTTPException(status_code=401, detail="Token expired")
            
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    user = await user_service.get_user_by_email(token_data.username)
    if user is None:
        raise credentials_exception
    
    return user
```

### Logout Implementation

```python
async def logout_endpoint(
    request: RefreshTokenRequest, 
    current_user: User = Depends(get_current_user)
):
    try:
        # Blacklist the refresh token
        await token_service.blacklist_token(request.refresh_token)
        
        # Optionally blacklist access token (requires token storage)
        # await token_service.blacklist_access_token(access_token)
        
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        raise HTTPException(status_code=500, detail="Logout failed")
```

## Security Considerations

### Token Security

**JWT Security:**

- Access tokens contain minimal sensitive information
- Tokens are signed with secure secret keys
- Expiration times limit exposure window
- Refresh tokens enable secure token renewal

**Scope Management:**

- Token scopes limit access to specific resources
- Fine-grained permission control
- Principle of least privilege enforcement
- Scope validation on each request

### Refresh Token Security

**Single Use Pattern:**

```python
async def secure_token_refresh(refresh_token: str):
    # Validate and use refresh token
    user_id = await validate_refresh_token(refresh_token)
    
    # Immediately blacklist used token
    await blacklist_token(refresh_token)
    
    # Generate new refresh token
    new_refresh_token = await create_refresh_token(user_id)
    
    return new_refresh_token
```

**Token Rotation:**

- Refresh tokens are rotated on each use
- Old refresh tokens are immediately invalidated
- Prevents token replay attacks
- Limits exposure window for compromised tokens

### Validation Security

**Input Validation:**

- All token fields are validated for type and format
- Refresh tokens are validated against stored values
- Token expiration is checked on every use
- Invalid tokens result in clear error responses

**Error Handling:**

- Security-aware error messages (no information leakage)
- Consistent error responses for invalid tokens
- Proper HTTP status codes for different failure modes
- Audit logging for security events

## Performance Considerations

### Token Generation

**Efficient Creation:**

```python
# Optimized token generation
async def create_tokens_bulk(user_id: int, scopes: list[str]):
    # Generate both tokens in parallel
    access_task = asyncio.create_task(
        create_access_token({"sub": str(user_id)}, scopes)
    )
    refresh_task = asyncio.create_task(
        create_refresh_token(user_id)
    )
    
    access_token, refresh_token = await asyncio.gather(
        access_task, refresh_task
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=3600
    )
```

### Token Validation

**Caching Strategy:**

- Cache decoded token data for repeated requests
- Use Redis for distributed token validation
- Implement token blacklist caching
- Optimize database lookups for user validation

### Memory Management

**Schema Efficiency:**

- Minimal memory footprint for token schemas
- Efficient string handling for token data
- Optional fields reduce memory usage
- List comprehensions for scope processing

## Error Handling

### Token Validation Errors

```python
# Comprehensive token validation error handling
async def validate_token_response(token_data: dict) -> TokenResponse:
    try:
        return TokenResponse(**token_data)
    except ValidationError as e:
        # Handle specific validation failures
        for error in e.errors():
            field = error["loc"][-1]
            error_type = error["type"]
            
            if field == "access_token" and "missing" in error_type:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to generate access token"
                )
            elif field == "expires_in" and "int_parsing" in error_type:
                raise HTTPException(
                    status_code=500,
                    detail="Invalid token expiration configuration"
                )
        
        # Generic validation error
        raise HTTPException(
            status_code=500,
            detail="Token generation failed"
        )
```

### Refresh Token Errors

```python
# Refresh token validation error handling
async def validate_refresh_request(request_data: dict) -> RefreshTokenRequest:
    try:
        return RefreshTokenRequest(**request_data)
    except ValidationError as e:
        # Handle refresh token validation errors
        for error in e.errors():
            if error["loc"][-1] == "refresh_token":
                if "missing" in error["type"]:
                    raise HTTPException(
                        status_code=400,
                        detail="Refresh token is required"
                    )
                elif "str_type" in error["type"]:
                    raise HTTPException(
                        status_code=400,
                        detail="Refresh token must be a string"
                    )
        
        raise HTTPException(
            status_code=400,
            detail="Invalid refresh token request"
        )
```

## Best Practices

### Schema Design

- **Security First**: All schemas designed with security considerations
- **Type Safety**: Strong typing throughout token handling
- **Validation**: Comprehensive input validation for all token operations
- **Documentation**: Clear field documentation for API consumers
- **Standards Compliance**: Follows OAuth 2.0 and JWT standards

### Token Management

- **Short-lived Access Tokens**: Minimize exposure window
- **Secure Refresh Tokens**: Long-lived but securely managed
- **Token Rotation**: Regular refresh token rotation
- **Scope Management**: Fine-grained permission control
- **Proper Expiration**: Clear expiration handling

### API Integration

- **Consistent Response Format**: Standardized token response structure
- **Error Handling**: Clear and secure error messages
- **Performance**: Efficient token validation and generation
- **Security**: Proper authentication flow implementation
- **Standards**: OAuth 2.0 and JWT best practices

## Testing Strategies

### Unit Testing

```python
def test_token_response_creation():
    # Test valid token response creation
    token_data = {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.test",
        "refresh_token": "refresh_token_example",
        "token_type": "bearer",
        "expires_in": 3600
    }
    
    token_response = TokenResponse(**token_data)
    assert token_response.access_token == token_data["access_token"]
    assert token_response.refresh_token == token_data["refresh_token"]
    assert token_response.token_type == "bearer"
    assert token_response.expires_in == 3600

def test_refresh_token_request():
    # Test refresh token request validation
    request_data = {
        "refresh_token": "valid_refresh_token"
    }
    
    refresh_request = RefreshTokenRequest(**request_data)
    assert refresh_request.refresh_token == "valid_refresh_token"

def test_token_data_with_scopes():
    # Test token data with scopes
    token_data = {
        "username": "test@example.com",
        "scopes": ["read", "write", "admin"],
        "sub": "12345",
        "exp": 1640995200
    }
    
    token = TokenData(**token_data)
    assert token.username == "test@example.com"
    assert token.scopes == ["read", "write", "admin"]
    assert token.sub == "12345"
    assert token.exp == 1640995200
```

### Integration Testing

```python
async def test_complete_auth_flow():
    # Test complete authentication flow
    client = TestClient(app)
    
    # Login and get tokens
    login_response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "testpass"
    })
    
    assert login_response.status_code == 200
    tokens = TokenResponse(**login_response.json())
    
    # Validate token structure
    assert tokens.access_token is not None
    assert tokens.refresh_token is not None
    assert tokens.token_type == "bearer"
    assert tokens.expires_in == 3600
    
    # Test token refresh
    refresh_response = client.post("/auth/refresh", json={
        "refresh_token": tokens.refresh_token
    })
    
    assert refresh_response.status_code == 200
    new_tokens = TokenResponse(**refresh_response.json())
    assert new_tokens.access_token != tokens.access_token
```

### Security Testing

```python
async def test_token_security():
    # Test token expiration
    expired_token_data = {
        "username": "test@example.com",
        "sub": "12345",
        "exp": int(time.time()) - 3600  # Expired 1 hour ago
    }
    
    with pytest.raises(HTTPException) as exc:
        await validate_token_claims(expired_token_data)
    assert exc.value.status_code == 401
    
    # Test invalid refresh token
    with pytest.raises(HTTPException) as exc:
        await refresh_token_endpoint(RefreshTokenRequest(
            refresh_token="invalid_token"
        ))
    assert exc.value.status_code == 401
```

## Related Files

### Dependencies

- `typing` - Type annotations and Optional types
- `pydantic` - Schema validation framework with Field
- `datetime` - Token expiration handling

### Service Integration

- `src.services.auth` - Authentication business logic
- `src.services.token` - Token generation and validation
- `src.repositories.blacklisted_token` - Token blacklist management

### API Integration

- `src.api.v1.auth` - Authentication endpoints
- `src.api.deps` - Authentication dependencies
- `src.core.security` - JWT token utilities

## Configuration

### Token Settings

```python
# Token configuration
TOKEN_CONFIG = {
    "access_token_expire_minutes": 60,
    "refresh_token_expire_days": 30,
    "algorithm": "HS256",
    "token_type": "bearer"
}
```

### Security Settings

```python
# JWT security configuration
JWT_CONFIG = {
    "secret_key": "your-secret-key",
    "algorithm": "HS256",
    "access_token_expire_minutes": 60,
    "refresh_token_expire_days": 30
}
```

### Scope Configuration

```python
# Available token scopes
TOKEN_SCOPES = {
    "read": "Read access to user data",
    "write": "Write access to user data", 
    "admin": "Administrative access",
    "upload": "File upload permissions"
}
```

This token schema module provides a comprehensive, secure foundation for JWT token management in the ReViewPoint application, ensuring proper authentication flows, token security, and standards compliance through well-designed Pydantic validation patterns.

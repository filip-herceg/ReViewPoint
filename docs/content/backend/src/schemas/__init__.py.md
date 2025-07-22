# Schema Package Overview

## Purpose

The `schemas` package provides comprehensive Pydantic model definitions for data validation, serialization, and API contracts throughout the ReViewPoint application. This package implements the data transfer object (DTO) pattern, defining strict schemas for request/response validation, authentication flows, user management, file operations, and token handling with proper type safety and validation rules.

## Package Architecture

The schema layer serves as the contract definition layer between the API endpoints and the underlying business logic, ensuring consistent data validation and type safety across all application interfaces.

### Schema Categories

#### **Authentication & Security Schemas**
- **`auth.py`** - Authentication requests and responses (login, registration, password reset)
- **`token.py`** - JWT token structures and refresh token handling
- **`blacklisted_token.py`** - Token blacklisting for logout and security

#### **Entity Schemas**
- **`user.py`** - User profile, preferences, and management schemas
- **`file.py`** - File metadata and upload response schemas

### Common Patterns

#### **Request/Response Separation**
```python
# Request schemas for input validation
class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

# Response schemas for output serialization
class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"]
```

#### **Validation Integration**
```python
@field_validator("email")
@classmethod
def validate_email_field(cls, v: str) -> str:
    if not validate_email(v):
        raise ValueError("Invalid email format.")
    return v
```

#### **Configuration Management**
```python
model_config = ConfigDict(
    from_attributes=True,  # For ORM model conversion
    extra="forbid"         # Strict field validation
)
```

## Schema Validation Philosophy

### **Strict Validation**
- All schemas use `extra="forbid"` to prevent unexpected fields
- Field constraints with proper min/max lengths
- Type-safe field definitions with Union types where appropriate

### **Security-First Design**
- Password validation integration with utility functions
- Email validation with proper format checking
- Token expiration and security field handling

### **API Contract Enforcement**
- Clear separation between request and response schemas
- Comprehensive field documentation with descriptions
- Example values in schema configurations for API documentation

## Integration Patterns

### **With API Layer**
```python
# API endpoint using schema validation
@router.post("/register", response_model=AuthResponse)
async def register(request: UserRegisterRequest):
    # Schema automatically validates input
    user = await user_service.create_user(request)
    return AuthResponse(...)
```

### **With ORM Models**
```python
# Conversion from ORM to schema
user_profile = UserProfile.model_validate(user_orm)

# Configuration enables ORM attribute mapping
model_config = ConfigDict(from_attributes=True)
```

### **With Service Layer**
```python
# Service layer receives validated schema objects
async def create_user(user_data: UserRegisterRequest) -> User:
    # user_data is already validated by Pydantic
    return await user_repository.create(user_data)
```

## Error Handling Strategy

### **Validation Errors**
```python
try:
    user_request = UserRegisterRequest(**request_data)
except ValidationError as e:
    # Pydantic provides detailed validation error information
    raise HTTPException(status_code=422, detail=e.errors())
```

### **Custom Validators**
```python
@field_validator("password")
@classmethod
def validate_password_field(cls, v: str) -> str:
    err = get_password_validation_error(v)
    if err:
        raise ValueError(err)  # Becomes ValidationError
    return v
```

## Type Safety Implementation

### **Literal Types for Constants**
```python
TOKEN_TYPE_BEARER: Final[Literal["bearer"]] = "bearer"

class AuthResponse(BaseModel):
    token_type: Literal["bearer"] = TOKEN_TYPE_BEARER
```

### **TypedDict for Compatibility**
```python
class AuthResponseDict(TypedDict):
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"]
```

### **Optional and Union Types**
```python
name: str | None = Field(None, max_length=128)
created_at: str | None = None  # ISO datetime string
```

## Performance Considerations

### **Model Configuration**
- `from_attributes=True` for efficient ORM conversion
- Field constraints reduce validation overhead
- Proper use of Optional types for better memory usage

### **Validation Caching**
- Field validators are cached by Pydantic
- Schema compilation happens once at startup
- Efficient serialization/deserialization

## Testing Integration

### **Schema Testing Patterns**
```python
def test_user_register_request_validation():
    # Valid data should pass
    valid_data = {
        "email": "test@example.com",
        "password": "SecurePass123!",
        "name": "Test User"
    }
    schema = UserRegisterRequest(**valid_data)
    assert schema.email == "test@example.com"

    # Invalid data should raise ValidationError
    with pytest.raises(ValidationError):
        UserRegisterRequest(email="invalid", password="weak")
```

### **Mock Data Generation**
```python
# Schema examples for testing
user_register_example = {
    "email": "user@example.com",
    "password": "strongpassword123",
    "name": "Jane Doe"
}
```

## Documentation Integration

### **OpenAPI Schema Generation**
- Pydantic models automatically generate OpenAPI schemas
- Field descriptions become API documentation
- Examples in `json_schema_extra` appear in Swagger UI

### **Type Hints for IDE Support**
- Full type safety with modern Python typing
- IDE autocompletion and error detection
- Integration with static type checkers (mypy)

## Migration and Versioning

### **Schema Evolution Strategy**
```python
# Backwards-compatible additions
class UserProfileV2(UserProfile):
    new_field: str | None = None  # Optional for compatibility

# Version-specific schemas
class UserProfileV1(BaseModel):
    # Legacy fields only
    pass
```

### **Deprecation Handling**
```python
class UserProfileUpdate(BaseModel):
    name: str | None = Field(
        None, 
        deprecated=True,  # Mark deprecated fields
        max_length=128
    )
```

## Related Modules

### **Core Dependencies**
- **`src.utils.validation`** - Email and password validation functions
- **`src.utils.errors`** - Custom exception classes for validation
- **`pydantic`** - Core validation and serialization framework

### **Integration Points**
- **`src.api.v1.*`** - API endpoints using schemas for validation
- **`src.services.*`** - Service layer receiving validated schema objects
- **`src.models.*`** - ORM models converted to/from schemas

### **External Dependencies**
- **`pydantic[email]`** - EmailStr validation support
- **`typing_extensions`** - Enhanced typing support for older Python versions

## Configuration Dependencies

- Pydantic configuration for validation behavior
- Email validation configuration in utils
- Password complexity requirements in validation utilities
- JSON schema generation settings for API documentation

## Summary

The `schemas` package provides a comprehensive, type-safe foundation for data validation and API contracts in the ReViewPoint application. Through strict Pydantic models with custom validators, clear request/response separation, and integration with the broader application architecture, it ensures data integrity and type safety throughout the system.

Key strengths include comprehensive validation with custom rules, clear API contract definitions, security-first design with proper authentication schemas, type safety with modern Python typing, and efficient ORM integration. The package serves as the authoritative source for data structure definitions and validation rules across the entire application.

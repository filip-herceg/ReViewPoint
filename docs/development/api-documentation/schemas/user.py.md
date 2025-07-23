# User Schema Documentation

## Purpose

The `user.py` schema module defines comprehensive Pydantic data validation models for user profile management, preferences, and user-related operations in the ReViewPoint application. This module provides structured data validation, serialization, and type safety for user profiles, preferences management, avatar handling, and administrative user operations.

## Architecture

The schema module follows a modular validation design with specialized schemas for different user operations:

- **Profile Management Layer**: Complete user profile data structures
- **Preferences Layer**: User customization and settings management  
- **Avatar Management Layer**: Profile image handling
- **Administrative Layer**: Bulk user operations and management
- **Type Safety Layer**: Strict typing with ConfigDict and Field validation

## Core Schema Classes

### User Profile Schemas

#### `UserProfile`

Complete user profile representation with comprehensive metadata.

```python
# Example usage
user_profile = UserProfile(
    id=123,
    email="user@example.com",
    name="John Doe",
    bio="Software developer passionate about AI",
    avatar_url="https://example.com/avatars/user123.jpg",
    created_at="2024-01-15T10:30:00Z",
    updated_at="2024-07-20T14:45:00Z"
)
```

**Field Specifications:**

- `id: int` - Unique user identifier (primary key)
- `email: str` - User email address
- `name: str | None` - Optional display name
- `bio: str | None` - Optional user biography/description
- `avatar_url: str | None` - Optional profile image URL
- `created_at: str | None` - ISO datetime string for account creation
- `updated_at: str | None` - ISO datetime string for last profile update

**Configuration Features:**

```python
model_config = ConfigDict(extra="forbid")
```

- **Strict Validation**: Forbids extra fields to prevent data contamination
- **Type Safety**: All fields strongly typed with None handling
- **JSON Serializable**: Optimized for API responses

#### `UserRead`

Alias for `UserProfile` providing semantic clarity for read operations.

```python
# Example usage
user_data: UserRead = UserProfile(**profile_data)
UserResponse = UserProfile  # Type alias for API responses
```

**Design Purpose:**
- Semantic distinction between data models
- Future extensibility for read-specific fields
- Type alias consistency across API layers

### Profile Update Schemas

#### `UserProfileUpdate`

Focused schema for profile modification operations with validation constraints.

```python
# Example usage
profile_update = UserProfileUpdate(
    name="Jane Smith",
    bio="Updated bio: Full-stack developer with 5 years experience"
)

# Partial updates supported
partial_update = UserProfileUpdate(name="Jane Smith")  # Only name updated
```

**Field Specifications:**

- `name: str | None` - Optional display name (max 128 characters)
- `bio: str | None` - Optional biography (max 512 characters)

**Validation Features:**

```python
name: str | None = Field(None, max_length=128)
bio: str | None = Field(None, max_length=512)
```

- **Length Constraints**: Prevents excessive data storage
- **Optional Fields**: Supports partial profile updates
- **Null Handling**: Distinguishes between null and unchanged values

**Security Features:**
- Field length limits prevent DoS attacks
- No email updates (requires separate verification flow)
- Strict field validation with `extra="forbid"`

### User Preferences Management

#### `UserPreferences`

Comprehensive user customization and application settings schema.

```python
# Example usage
user_preferences = UserPreferences(
    theme="dark",
    locale="en-US"
)

# With all fields
full_preferences = UserPreferences(
    theme="light", 
    locale="fr-FR"
)
```

**Field Specifications:**

- `theme: Literal["dark", "light"] | None` - UI theme preference
- `locale: str | None` - User locale setting (e.g., 'en', 'fr', 'de')

**Type Safety Features:**

```python
theme: Literal["dark", "light"] | None = Field(
    None, description="UI theme, e.g. 'dark' or 'light'"
)
locale: str | None = Field(None, description="User locale, e.g. 'en', 'fr'")
```

- **Literal Types**: Constrains theme to valid values only
- **Extensible Design**: Easy addition of new preference fields
- **Documentation**: Field descriptions for API documentation

#### `UserPreferencesUpdate`

Flexible preference update schema supporting arbitrary preference keys.

```python
# Example usage
preferences_update = UserPreferencesUpdate(
    preferences={
        "theme": "dark",
        "locale": "en-US", 
        "notifications": True,
        "autoSave": False,
        "fontSize": 14
    }
)
```

**Field Specifications:**

- `preferences: Mapping[str, object]` - Arbitrary key-value preference mapping

**Design Features:**
- **Flexible Structure**: Supports any preference key-value pairs
- **Type Safety**: Uses `object` instead of `Any` for better type checking
- **Future Proof**: Easily accommodates new preference types
- **Validation**: Maintains type safety while allowing flexibility

### Avatar Management Schemas

#### `UserAvatarResponse`

Standardized response format for avatar upload operations.

```python
# Example usage
avatar_response = UserAvatarResponse(
    avatar_url="https://cdn.example.com/avatars/user123_updated.jpg"
)
```

**Field Specifications:**

- `avatar_url: str` - Complete URL to user's uploaded avatar image

**Use Cases:**
- Avatar upload confirmation responses
- Profile image update notifications
- Avatar deletion confirmations (with placeholder URL)

### User Creation Schemas

#### `UserCreateRequest`

Administrative user creation schema with comprehensive validation and examples.

```python
# Example usage (admin operations)
new_user_request = UserCreateRequest(
    email="newuser@example.com",
    password="SecureAdminPassword123!",
    name="New Team Member"
)
```

**Field Specifications:**

- `email: str` - Valid email address for new user
- `password: str` - Initial password for account
- `name: str` - Required display name

**Configuration Features:**

```python
model_config = ConfigDict(
    json_schema_extra={
        "examples": [
            {
                "email": "user@example.com",
                "password": "strongpassword123",
                "name": "Jane Doe",
            }
        ]
    }
)
```

- **API Documentation**: Provides examples for OpenAPI schema
- **Required Fields**: All fields mandatory for admin creation
- **Validation**: Inherits email and password validation from base validators

### User List Management

#### `UserListResponse`

Paginated user listing response with metadata for administrative interfaces.

```python
# Example usage
user_list = UserListResponse(
    users=[user1, user2, user3],  # List of UserProfile objects
    total=150  # Total users in system (for pagination)
)
```

**Field Specifications:**

- `users: Sequence[UserProfile]` - Array of user profile objects
- `total: int` - Total count of users (for pagination calculations)

**Pagination Support:**
- **User Array**: Current page of user profiles
- **Total Count**: Enables pagination UI calculations
- **Type Safety**: Strongly typed user sequence
- **Performance**: Supports efficient pagination queries

## Data Validation Patterns

### Field Validation Rules

**Length Constraints:**
```python
# Profile update constraints
name: str | None = Field(None, max_length=128)    # Reasonable name length
bio: str | None = Field(None, max_length=512)     # Extended bio support
```

**Type Constraints:**
```python
# Theme validation with literals
theme: Literal["dark", "light"] | None = Field(None)
```

**Configuration Patterns:**
```python
# Strict validation configuration
model_config = ConfigDict(extra="forbid")
```

### Schema Relationships

**Profile Inheritance:**
```python
# UserRead extends UserProfile
class UserRead(UserProfile):
    pass

# Type aliases for semantic clarity
UserResponse = UserProfile
```

**Update Patterns:**
```python
# Separate schemas for different operations
UserProfile       # Complete profile data
UserProfileUpdate # Partial profile modifications
UserPreferences   # Settings management
```

## Security Considerations

### Data Protection

**Field Access Control:**
- Profile fields are read-only in base schema
- Updates require separate validated schema
- No sensitive data exposure in profile responses
- Email updates require separate verification workflow

**Input Validation:**
- Length limits prevent buffer overflow attacks
- `extra="forbid"` prevents field injection
- Type constraints prevent data type confusion
- Optional fields properly handle null values

**Privacy Features:**
- Avatar URLs support CDN integration
- Bio field supports markdown-safe content
- Preference data isolated from profile data
- No password exposure in any schema

### Validation Security

**Preference Validation:**
```python
# Safe preference handling
preferences: Mapping[str, object]  # Not Any - better type safety
```

**Field Constraints:**
```python
# Prevent oversized data
name: str | None = Field(None, max_length=128)
bio: str | None = Field(None, max_length=512)
```

## Usage Patterns

### Profile Management Workflow

```python
async def update_user_profile(user_id: int, update_data: UserProfileUpdate):
    # Schema validation happens automatically
    current_profile = await get_user_profile(user_id)
    
    # Apply updates
    updated_fields = {}
    if update_data.name is not None:
        updated_fields["name"] = update_data.name
    if update_data.bio is not None:
        updated_fields["bio"] = update_data.bio
    
    # Update and return
    updated_profile = await update_profile(user_id, updated_fields)
    return UserProfile(**updated_profile.__dict__)
```

### Preferences Management Workflow

```python
async def update_user_preferences(user_id: int, prefs: UserPreferencesUpdate):
    # Validate preference structure
    preferences_data = prefs.preferences
    
    # Apply preferences with validation
    valid_preferences = {}
    for key, value in preferences_data.items():
        if key == "theme" and value in ["dark", "light"]:
            valid_preferences[key] = value
        elif key == "locale" and isinstance(value, str):
            valid_preferences[key] = value
        # Add more preference validation as needed
    
    await save_user_preferences(user_id, valid_preferences)
    return UserPreferences(**valid_preferences)
```

### User Creation Workflow

```python
async def create_new_user(request: UserCreateRequest):
    # Schema validation ensures data integrity
    hashed_password = hash_password(request.password)
    
    new_user = await create_user(
        email=request.email,
        password_hash=hashed_password,
        name=request.name
    )
    
    # Return profile representation
    return UserProfile(
        id=new_user.id,
        email=new_user.email,
        name=new_user.name,
        created_at=new_user.created_at.isoformat()
    )
```

### User Listing Workflow

```python
async def list_users_paginated(page: int, per_page: int):
    offset = (page - 1) * per_page
    users, total = await get_users_paginated(offset, per_page)
    
    # Convert to profile schemas
    user_profiles = [
        UserProfile(
            id=user.id,
            email=user.email,
            name=user.name,
            bio=user.bio,
            avatar_url=user.avatar_url,
            created_at=user.created_at.isoformat() if user.created_at else None,
            updated_at=user.updated_at.isoformat() if user.updated_at else None
        )
        for user in users
    ]
    
    return UserListResponse(users=user_profiles, total=total)
```

## Error Handling

### Validation Error Patterns

```python
# Profile update validation errors
try:
    profile_update = UserProfileUpdate(**update_data)
except ValidationError as e:
    # Handle field validation failures
    for error in e.errors():
        field = error["loc"][-1]
        if field == "name" and error["type"] == "value_error.any_str.max_length":
            raise HTTPException(status_code=400, detail="Name too long (max 128 characters)")
        elif field == "bio" and error["type"] == "value_error.any_str.max_length":
            raise HTTPException(status_code=400, detail="Bio too long (max 512 characters)")
```

### Preference Validation Errors

```python
# Preference update error handling
try:
    preferences_update = UserPreferencesUpdate(**preference_data)
    
    # Validate individual preferences
    for key, value in preferences_update.preferences.items():
        if key == "theme" and value not in ["dark", "light"]:
            raise HTTPException(status_code=400, detail=f"Invalid theme: {value}")
        elif key == "locale" and not isinstance(value, str):
            raise HTTPException(status_code=400, detail="Locale must be a string")
            
except ValidationError as e:
    raise HTTPException(status_code=422, detail="Invalid preference data structure")
```

## Best Practices

### Schema Design

- **Separation of Concerns**: Different schemas for different operations
- **Type Safety**: Use Literal types for constrained values
- **Validation**: Field-level validation with appropriate constraints
- **Documentation**: Include field descriptions for API documentation
- **Extensibility**: Design for easy addition of new fields

### Performance Optimization

- **Selective Updates**: Support partial updates with optional fields
- **Efficient Serialization**: Use `from_attributes=True` for ORM integration
- **Memory Management**: Appropriate field length limits
- **Validation Caching**: Reuse compiled validation patterns

### Security Practices

- **Input Sanitization**: Validate all input fields appropriately
- **Length Limits**: Prevent resource exhaustion attacks
- **Type Safety**: Use strong typing to prevent injection
- **Access Control**: Separate schemas for different privilege levels
- **Data Isolation**: Keep sensitive data out of profile schemas

## Testing Strategies

### Unit Testing

```python
def test_user_profile_creation():
    # Test complete profile creation
    profile_data = {
        "id": 1,
        "email": "test@example.com",
        "name": "Test User",
        "bio": "Test biography",
        "avatar_url": "https://example.com/avatar.jpg",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
    profile = UserProfile(**profile_data)
    assert profile.email == "test@example.com"
    assert profile.name == "Test User"

def test_user_profile_update_validation():
    # Test profile update constraints
    valid_update = UserProfileUpdate(name="Valid Name", bio="Valid bio")
    assert valid_update.name == "Valid Name"
    
    # Test length constraints
    with pytest.raises(ValidationError):
        UserProfileUpdate(name="x" * 129)  # Too long
    
    with pytest.raises(ValidationError):
        UserProfileUpdate(bio="x" * 513)  # Too long
```

### Preferences Testing

```python
def test_user_preferences_theme_validation():
    # Test valid themes
    valid_prefs = UserPreferences(theme="dark", locale="en")
    assert valid_prefs.theme == "dark"
    
    # Test invalid theme (should be caught by Literal type)
    with pytest.raises(ValidationError):
        UserPreferences(theme="blue")  # Invalid theme

def test_preferences_update_flexibility():
    # Test flexible preference structure
    prefs_update = UserPreferencesUpdate(
        preferences={
            "theme": "light",
            "customSetting": True,
            "numberSetting": 42
        }
    )
    assert len(prefs_update.preferences) == 3
```

### Integration Testing

```python
async def test_profile_management_flow():
    # Test complete profile management workflow
    
    # Create user
    create_request = UserCreateRequest(
        email="flow@example.com",
        password="TestPassword123!",
        name="Flow Test User"
    )
    
    # Update profile
    update_request = UserProfileUpdate(
        name="Updated Name",
        bio="Updated biography"
    )
    
    # Update preferences
    prefs_request = UserPreferencesUpdate(
        preferences={"theme": "dark", "locale": "en-US"}
    )
    
    # Verify all schemas validate correctly
    assert create_request.email == "flow@example.com"
    assert update_request.name == "Updated Name"
    assert prefs_request.preferences["theme"] == "dark"
```

## Related Files

### Dependencies

- `pydantic` - Schema validation framework
- `typing` - Type annotations and Literal types
- `collections.abc` - Mapping and Sequence types

### Model Integration

- `src.models.user` - User SQLAlchemy model
- `src.repositories.user` - User data access layer
- `src.services.user` - User business logic

### API Integration

- `src.api.v1.users.core` - User profile endpoints
- `src.api.v1.users.exports` - User data export endpoints
- `src.api.v1.auth` - Authentication endpoints

## Configuration

### Schema Configuration

```python
# Global schema settings
class UserSchemaConfig:
    extra = "forbid"           # Strict field validation
    validate_assignment = True  # Validate on field assignment
    str_strip_whitespace = True # Clean string inputs
```

### Field Constraints

```python
# Standard field limits
MAX_NAME_LENGTH = 128
MAX_BIO_LENGTH = 512
VALID_THEMES = ["dark", "light"]
DEFAULT_LOCALE = "en-US"
```

This user schema module provides comprehensive, type-safe data validation for all user-related operations in the ReViewPoint application, ensuring data integrity, security, and proper API documentation through well-designed Pydantic validation patterns.

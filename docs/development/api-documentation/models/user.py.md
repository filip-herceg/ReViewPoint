# User Model Documentation

## Purpose

The `user.py` module defines the SQLAlchemy ORM model for user entities in the ReViewPoint application. This model provides comprehensive user management functionality including authentication, profile management, preferences, role-based access control, and relationship mappings for user-owned resources, serving as the central identity management component of the system.

## Architecture

The model follows a comprehensive user management pattern:

- **Identity Layer**: Email-based authentication with secure password storage
- **Profile Layer**: User metadata including name, bio, avatar, and preferences
- **Security Layer**: Role-based access control and account status management
- **Relationship Layer**: Connections to user-owned files and resources
- **Audit Layer**: Activity tracking with login timestamps and modification history
- **Preferences Layer**: JSON-based user settings and customization storage

## Core Model Class

### `User`

Comprehensive user model with authentication, profile, and relationship management.

```python
# Example usage - User creation
user = User(
    email="user@example.com",
    hashed_password="$2b$12$hashed_password_string",
    name="John Doe",
    bio="Research scientist specializing in AI",
    is_active=True,
    preferences={"theme": "dark", "language": "en"}
)

# Save to database
session.add(user)
await session.commit()
```

**Table Configuration:**
- `__tablename__ = "users"` - Database table name
- Inherits from `BaseModel` (id, created_at, updated_at)

## Field Specifications

### Authentication Fields

**Email Identity:**
```python
email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
```

- **Unique Constraint**: Ensures one account per email address
- **Indexed**: Optimized for login queries and lookups
- **Required**: Cannot be null or empty
- **Length Limit**: 255 characters for comprehensive email support

**Password Security:**
```python
hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
```

- **Hashed Storage**: Never stores plain text passwords
- **Required Field**: All users must have password authentication
- **Length Support**: 255 characters supports all modern hashing algorithms
- **Security**: Compatible with bcrypt, Argon2, and other secure hashing methods

### Account Status Fields

**Active Status:**
```python
is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
```

- **Default Active**: New accounts are active by default
- **Account Control**: Enables account suspension without deletion
- **Required**: Cannot be null (explicit boolean state)
- **Login Control**: Inactive users cannot authenticate

**Soft Delete:**
```python
is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
```

- **Soft Deletion**: Marks users as deleted without removing data
- **Data Retention**: Preserves user data for audit and recovery
- **Default False**: Users are not deleted by default
- **Compliance**: Supports GDPR and data retention requirements

**Activity Tracking:**
```python
last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
```

- **Optional Field**: Nullable for users who have never logged in
- **Timezone Aware**: Uses DateTime for proper timezone handling
- **Security Audit**: Tracks user authentication patterns
- **Session Management**: Supports security monitoring and session validation

### Profile Fields

**Display Name:**
```python
name: Mapped[str | None] = mapped_column(String(128), nullable=True)
```

- **Optional Field**: Users can choose to provide display name
- **Length Limit**: 128 characters for comprehensive name support
- **Privacy**: Users control their identity visibility
- **Display**: Used for user interface and identification

**Biography:**
```python
bio: Mapped[str | None] = mapped_column(String(512), nullable=True)
```

- **Optional Field**: Users can provide biography information
- **Extended Length**: 512 characters for detailed descriptions
- **Profile Enhancement**: Supports rich user profiles
- **Professional Use**: Suitable for academic and professional contexts

**Avatar Image:**
```python
avatar_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
```

- **Optional Field**: Users can upload profile pictures
- **URL Storage**: Stores URL reference to image location
- **External Support**: Compatible with cloud storage services
- **Performance**: Avoids storing binary data in database

### Preferences and Settings

**User Preferences:**
```python
preferences: Mapped[Mapping[str, Any] | None] = mapped_column(JSON, nullable=True)
```

- **JSON Storage**: Flexible schema for user settings
- **Optional Field**: Users start with default preferences
- **Extensible**: Can store arbitrary preference structures
- **Type Safety**: Proper typing with Mapping[str, Any]

**Example Preferences Structure:**
```python
{
    "theme": "dark",
    "language": "en",
    "notifications": {
        "email": True,
        "browser": False
    },
    "ui": {
        "sidebar_collapsed": False,
        "items_per_page": 20
    }
}
```

### Role Management

**Administrative Access:**
```python
is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
```

- **Default User**: New accounts are not administrators by default
- **Role-Based Access**: Controls access to administrative functions
- **Required Field**: Explicit boolean state for security
- **Permission Model**: Foundation for authorization system

## Dynamic Properties and Methods

### Role Property

**Dynamic Role Access:**
```python
@property
def role(self: User) -> Literal["admin", "user"]:
    """Returns the role of the user."""
    return "admin" if self.is_admin else "user"

@role.setter
def role(self: User, value: str) -> None:
    """Allows setting the role dynamically for test/deps purposes only."""
    self.is_admin = value == "admin"
```

**Usage Examples:**
```python
# Check user role
if user.role == "admin":
    # Grant administrative access
    pass

# Set role (for testing/dependencies)
user.role = "admin"  # Sets is_admin = True
user.role = "user"   # Sets is_admin = False
```

### String Representation

**Debug-Friendly Representation:**
```python
def __repr__(self: User) -> str:
    """Return a string representation of the User instance."""
    return f"<User id={self.id} email={self.email}>"
```

- **Debugging**: Clear identification in logs and debug output
- **Privacy**: Only shows non-sensitive fields (id and email)
- **Consistency**: Standard format across all models
- **Development**: Helpful for development and testing

## Relationship Management

### File Ownership

**User-File Relationship:**
```python
files: WriteOnlyMapped[File] = relationship(
    "File", back_populates="user", passive_deletes=True
)
```

- **WriteOnlyMapped**: Optimized for large collections of files
- **Bidirectional**: Files reference users, users reference files
- **Cascade Deletes**: Files are deleted when user is deleted
- **Performance**: Lazy loading for efficient memory usage

**Usage Patterns:**
```python
# Access user files (requires explicit query)
user_files = await session.execute(
    select(File).where(File.user_id == user.id)
)

# Count user files
file_count = await session.scalar(
    select(func.count(File.id)).where(File.user_id == user.id)
)
```

## Usage Patterns

### User Registration

```python
async def register_user(email: str, password: str, name: str = None) -> User:
    """Register a new user with secure password hashing."""
    
    # Check if user already exists
    existing_user = await session.execute(
        select(User).where(User.email == email)
    )
    if existing_user.scalar_one_or_none():
        raise ValueError("User already exists")
    
    # Hash password securely
    hashed_password = hash_password(password)
    
    # Create user
    user = User(
        email=email,
        hashed_password=hashed_password,
        name=name,
        is_active=True,
        preferences={"theme": "light", "language": "en"}
    )
    
    session.add(user)
    await session.commit()
    return user
```

### User Authentication

```python
async def authenticate_user(email: str, password: str) -> User | None:
    """Authenticate user with email and password."""
    
    # Find user by email
    result = await session.execute(
        select(User).where(
            User.email == email,
            User.is_active == True,
            User.is_deleted == False
        )
    )
    user = result.scalar_one_or_none()
    
    if not user:
        return None
    
    # Verify password
    if not verify_password(password, user.hashed_password):
        return None
    
    # Update last login
    user.last_login_at = datetime.utcnow()
    await session.commit()
    
    return user
```

### Profile Management

```python
async def update_user_profile(
    user_id: int, 
    name: str = None,
    bio: str = None,
    avatar_url: str = None,
    preferences: dict = None
) -> User:
    """Update user profile information."""
    
    user = await session.get(User, user_id)
    if not user:
        raise ValueError("User not found")
    
    # Update provided fields
    if name is not None:
        user.name = name
    if bio is not None:
        user.bio = bio
    if avatar_url is not None:
        user.avatar_url = avatar_url
    if preferences is not None:
        # Merge with existing preferences
        current_prefs = user.preferences or {}
        current_prefs.update(preferences)
        user.preferences = current_prefs
    
    await session.commit()
    return user
```

### Role Management

```python
async def manage_user_roles(user_id: int, is_admin: bool) -> User:
    """Manage user administrative privileges."""
    
    user = await session.get(User, user_id)
    if not user:
        raise ValueError("User not found")
    
    # Update role
    user.is_admin = is_admin
    
    # Log role change
    logger.info(
        f"User {user.email} role changed to {'admin' if is_admin else 'user'}"
    )
    
    await session.commit()
    return user
```

### Account Status Management

```python
async def manage_account_status(
    user_id: int, 
    is_active: bool = None,
    is_deleted: bool = None
) -> User:
    """Manage user account status."""
    
    user = await session.get(User, user_id)
    if not user:
        raise ValueError("User not found")
    
    # Update status fields
    if is_active is not None:
        user.is_active = is_active
        logger.info(f"User {user.email} active status: {is_active}")
    
    if is_deleted is not None:
        user.is_deleted = is_deleted
        if is_deleted:
            user.is_active = False  # Deleted users should be inactive
        logger.info(f"User {user.email} deleted status: {is_deleted}")
    
    await session.commit()
    return user
```

## Security Considerations

### Password Security

**Secure Storage:**
- Never store plain text passwords
- Use bcrypt, Argon2, or equivalent secure hashing
- Salt passwords to prevent rainbow table attacks
- Implement proper password complexity requirements

**Authentication Security:**
```python
# Secure password verification
def verify_user_password(user: User, password: str) -> bool:
    """Verify password with timing attack protection."""
    if not user.is_active or user.is_deleted:
        # Still hash to prevent timing attacks
        hash_password("dummy_password")
        return False
    
    return verify_password(password, user.hashed_password)
```

### Account Security

**Account Lockout:**
- Implement failed login attempt tracking
- Temporary account lockout after failed attempts
- Email notifications for suspicious activity
- IP-based rate limiting for login attempts

**Session Security:**
- Update last_login_at for audit trails
- Implement session timeout mechanisms
- Track concurrent sessions per user
- Provide session management in user profiles

### Data Privacy

**Personal Information:**
- Optional profile fields protect user privacy
- Configurable privacy settings in preferences
- Data anonymization for deleted accounts
- GDPR compliance with data export/deletion

## Performance Considerations

### Database Optimization

**Indexing Strategy:**
```python
# Current indexes
email: Mapped[str] = mapped_column(String(255), unique=True, index=True)

# Additional recommended indexes for large datasets
__table_args__ = (
    Index("ix_users_active_not_deleted", "is_active", "is_deleted"),
    Index("ix_users_last_login", "last_login_at"),
    Index("ix_users_created_at", "created_at"),
)
```

**Query Optimization:**
```python
# Efficient user lookups
active_users = await session.execute(
    select(User).where(
        User.is_active == True,
        User.is_deleted == False
    ).options(selectinload(User.files))  # Eager load if needed
)
```

### Memory Management

**Relationship Optimization:**
- Use `WriteOnlyMapped` for large collections
- Implement pagination for user file listings
- Use `selectinload` for controlled eager loading
- Avoid N+1 queries with proper relationship loading

### Caching Strategies

**User Session Caching:**
```python
# Cache frequently accessed user data
@cache.memoize(timeout=300)  # 5 minutes
async def get_user_for_session(user_id: int) -> dict:
    """Get user data optimized for session storage."""
    user = await session.get(User, user_id)
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "preferences": user.preferences
    }
```

## Error Handling

### Validation Errors

```python
# User creation validation
async def create_user_safely(user_data: dict) -> User:
    try:
        # Validate email format
        if not is_valid_email(user_data["email"]):
            raise ValueError("Invalid email format")
        
        # Check email uniqueness
        existing = await session.execute(
            select(User).where(User.email == user_data["email"])
        )
        if existing.scalar_one_or_none():
            raise ValueError("Email already registered")
        
        # Create user
        user = User(**user_data)
        session.add(user)
        await session.commit()
        return user
        
    except IntegrityError as e:
        await session.rollback()
        if "unique constraint" in str(e).lower():
            raise ValueError("Email already registered")
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"User creation failed: {e}")
        raise
```

### Authentication Errors

```python
# Secure authentication error handling
async def authenticate_user_safely(email: str, password: str) -> User | None:
    try:
        user = await authenticate_user(email, password)
        if user:
            # Log successful authentication
            logger.info(f"Successful authentication for {email}")
        else:
            # Log failed authentication (without exposing why)
            logger.warning(f"Failed authentication attempt for {email}")
        return user
        
    except Exception as e:
        logger.error(f"Authentication error for {email}: {e}")
        return None
```

## Best Practices

### Model Design

- **Single Responsibility**: User model focuses on user identity and profile
- **Security First**: Secure password storage and authentication patterns
- **Privacy Aware**: Optional fields and configurable privacy settings
- **Extensible**: JSON preferences for future feature expansion
- **Audit Ready**: Comprehensive tracking fields for compliance

### Data Management

- **Soft Deletes**: Use is_deleted flag instead of hard deletion
- **Status Tracking**: Maintain clear account status with is_active
- **Relationship Management**: Use appropriate SQLAlchemy relationship patterns
- **Validation**: Implement comprehensive input validation
- **Error Handling**: Provide clear, secure error messages

### Security Implementation

- **Password Security**: Never store plain text, use secure hashing
- **Access Control**: Implement role-based authorization
- **Session Management**: Track login activity and session state
- **Audit Logging**: Log all security-relevant events
- **Privacy Protection**: Respect user privacy preferences

## Testing Strategies

### Unit Testing

```python
def test_user_model_creation():
    """Test basic user model creation."""
    user = User(
        email="test@example.com",
        hashed_password="hashed_password",
        name="Test User",
        is_active=True
    )
    
    assert user.email == "test@example.com"
    assert user.name == "Test User"
    assert user.is_active is True
    assert user.is_admin is False  # Default value
    assert user.role == "user"

def test_user_role_property():
    """Test dynamic role property."""
    user = User(email="test@example.com", hashed_password="hash")
    
    # Test default role
    assert user.role == "user"
    assert user.is_admin is False
    
    # Test admin role
    user.role = "admin"
    assert user.role == "admin"
    assert user.is_admin is True
    
    # Test back to user role
    user.role = "user"
    assert user.role == "user"
    assert user.is_admin is False
```

### Integration Testing

```python
async def test_user_database_operations():
    """Test user database operations."""
    
    # Create user
    user = User(
        email="integration@example.com",
        hashed_password="hashed_password",
        name="Integration Test",
        preferences={"theme": "dark"}
    )
    
    session.add(user)
    await session.commit()
    
    # Verify creation
    assert user.id is not None
    assert user.created_at is not None
    assert user.updated_at is not None
    
    # Test retrieval
    retrieved_user = await session.get(User, user.id)
    assert retrieved_user.email == "integration@example.com"
    assert retrieved_user.preferences["theme"] == "dark"
    
    # Test update
    retrieved_user.name = "Updated Name"
    await session.commit()
    
    # Verify update
    updated_user = await session.get(User, user.id)
    assert updated_user.name == "Updated Name"
    assert updated_user.updated_at > updated_user.created_at
```

### Security Testing

```python
async def test_user_authentication_security():
    """Test user authentication security features."""
    
    # Create test user
    user = User(
        email="security@example.com",
        hashed_password=hash_password("secure_password"),
        is_active=True,
        is_deleted=False
    )
    session.add(user)
    await session.commit()
    
    # Test successful authentication
    auth_user = await authenticate_user("security@example.com", "secure_password")
    assert auth_user is not None
    assert auth_user.id == user.id
    
    # Test failed authentication
    auth_user = await authenticate_user("security@example.com", "wrong_password")
    assert auth_user is None
    
    # Test inactive user
    user.is_active = False
    await session.commit()
    
    auth_user = await authenticate_user("security@example.com", "secure_password")
    assert auth_user is None
```

## Related Files

### Dependencies

- `sqlalchemy` - ORM framework with Mapped, mapped_column, relationship for model definition
- `datetime` - Timestamp handling for last_login_at and inherited timestamp fields
- `typing` - Type annotations including TYPE_CHECKING, Literal, Any for type safety
- `collections.abc` - Mapping interface for preferences field typing

### Model Integration

- `src.models.base` - BaseModel inheritance providing id, created_at, updated_at
- `src.models.file` - File model with user_id foreign key relationship
- Database relationships support user-owned resources and audit trails

### Service Integration

- `src.services.user` - User business logic and operations
- `src.repositories.user` - User data access patterns and queries
- `src.schemas.user` - User validation and serialization schemas
- `src.api.v1.users.*` - User API endpoints and authentication

### Security Integration

- `src.core.security` - Password hashing and JWT token management
- `src.api.deps` - Authentication dependencies and current user resolution
- `src.utils.hashing` - Password hashing utilities and verification

## Configuration

### User Model Settings

```python
# User field configuration
USER_CONFIG = {
    "email_max_length": 255,
    "password_max_length": 255,
    "name_max_length": 128,
    "bio_max_length": 512,
    "avatar_url_max_length": 255
}
```

### Security Settings

```python
# Security configuration
SECURITY_CONFIG = {
    "password_hash_algorithm": "bcrypt",
    "password_rounds": 12,
    "require_email_verification": True,
    "session_timeout_hours": 24
}
```

### Default Settings

```python
# Default user preferences
DEFAULT_USER_PREFERENCES = {
    "theme": "light",
    "language": "en",
    "notifications": {
        "email": True,
        "browser": True
    },
    "ui": {
        "items_per_page": 20,
        "sidebar_collapsed": False
    }
}
```

This user model provides comprehensive identity management functionality for the ReViewPoint application, supporting secure authentication, rich user profiles, role-based access control, and extensible preferences through well-designed SQLAlchemy patterns and security best practices.

# Backend Documentation

The ReViewPoint backend is a **modern, high-performance FastAPI application** built with Python 3.11+ that provides a comprehensive REST API for the ReViewPoint platform. This section contains complete documentation for all backend components, APIs, and development practices.

## Overview

### Architecture at a Glance

The backend follows a **layered architecture pattern** optimized for maintainability, testability, and performance:

```mermaid
graph TB
    subgraph "Presentation Layer"
        API[FastAPI Routes]
        Schemas[Pydantic Schemas]
        Auth[Authentication Middleware]
    end

    subgraph "Business Logic Layer"
        Services[Service Classes]
        Validators[Input Validation]
        Cache[Cache Layer]
    end

    subgraph "Data Access Layer"
        Repositories[Repository Pattern]
        Models[SQLAlchemy Models]
        Migrations[Alembic Migrations]
    end

    subgraph "Infrastructure"
        DB[(PostgreSQL)]
        Files[File Storage]
        Redis[(Redis Cache)]
    end

    API --> Services
    Schemas --> Services
    Auth --> Services
    Services --> Repositories
    Repositories --> Models
    Models --> DB
    Services --> Cache
    Cache --> Redis
    Services --> Files
```

### Key Technologies

| Technology     | Version | Purpose                           |
| -------------- | ------- | --------------------------------- |
| **FastAPI**    | 0.104+  | High-performance web framework    |
| **SQLAlchemy** | 2.0+    | Modern ORM with async support     |
| **PostgreSQL** | 15+     | Primary production database       |
| **Alembic**    | 1.12+   | Database migration management     |
| **Pydantic**   | 2.0+    | Data validation and serialization |
| **JWT**        | PyJWT   | Secure authentication tokens      |
| **Pytest**     | 7.0+    | Comprehensive testing framework   |
| **Hatch**      | 1.7+    | Python project management         |

## Quick Navigation

### 🚀 **Getting Started**

- [API Reference](#api-reference) - Complete endpoint documentation
- [Authentication System](#authentication-system) - JWT auth and RBAC
- [Database Schema](#database-schema) - Models and relationships
- [Testing Guide](#testing-guide) - Running and writing tests

### 🔧 **Development**

- [Project Structure](#project-structure) - Directory organization
- [Configuration](#configuration) - Environment and settings
- [Development Workflow](#development-workflow) - Daily development tasks
- [Performance](#performance) - Optimization strategies

### 📊 **Advanced Topics**

- [File Upload System](#file-upload-system) - Secure file handling
- [Caching Strategy](#caching-strategy) - Redis integration
- [Error Handling](#error-handling) - Robust error management
- [Security](#security) - Security implementation details

## Project Structure

```
backend/
├── src/                    # Source code
│   ├── api/               # FastAPI route handlers
│   │   ├── __init__.py    # API module initialization
│   │   ├── auth.py        # Authentication endpoints
│   │   ├── users.py       # User management endpoints
│   │   └── uploads.py     # File upload endpoints
│   ├── core/              # Core application logic
│   │   ├── __init__.py    # Core module initialization
│   │   ├── auth.py        # Authentication service
│   │   ├── cache.py       # Caching layer
│   │   ├── config.py      # Configuration management
│   │   └── security.py    # Security utilities
│   ├── models/            # SQLAlchemy database models
│   │   ├── __init__.py    # Models module initialization
│   │   ├── base.py        # Base model class
│   │   ├── user.py        # User model
│   │   ├── file.py        # File model
│   │   └── token.py       # Token model
│   ├── repositories/      # Data access layer
│   │   ├── __init__.py    # Repository module initialization
│   │   ├── base.py        # Base repository class
│   │   ├── user.py        # User repository
│   │   └── file.py        # File repository
│   ├── schemas/           # Pydantic request/response schemas
│   │   ├── __init__.py    # Schemas module initialization
│   │   ├── auth.py        # Authentication schemas
│   │   ├── user.py        # User schemas
│   │   └── file.py        # File schemas
│   ├── services/          # Business logic layer
│   │   ├── __init__.py    # Services module initialization
│   │   ├── auth.py        # Authentication service
│   │   ├── user.py        # User service
│   │   └── upload.py      # Upload service
│   ├── utils/             # Utility functions
│   │   ├── __init__.py    # Utils module initialization
│   │   └── helpers.py     # Helper functions
│   └── main.py            # FastAPI application entry point
├── tests/                 # Test suite (135+ tests)
│   ├── conftest.py        # Pytest configuration
│   ├── test_auth.py       # Authentication tests
│   ├── test_users.py      # User management tests
│   ├── test_uploads.py    # File upload tests
│   └── integration/       # Integration tests
├── config/                # Configuration files
│   ├── .env               # Environment variables
│   └── logging.conf       # Logging configuration
├── deployment/            # Deployment configurations
│   ├── Dockerfile         # Docker configuration
│   └── docker-compose.yml # Multi-service Docker setup
├── alembic/               # Database migrations
│   ├── versions/          # Migration scripts
│   └── env.py             # Alembic configuration
├── alembic.ini            # Alembic settings
├── pyproject.toml         # Python project configuration
└── README.md              # Backend-specific documentation
```

## API Reference

### Base Configuration

- **Base URL**: `http://localhost:8000/api/v1`
- **Authentication**: JWT Bearer tokens
- **Content Type**: `application/json`
- **Documentation**: Available at `/docs` (Swagger UI) and `/redoc` (ReDoc)

### Authentication Endpoints

#### POST `/auth/register`

Register a new user account.

**Request Body:**

```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

**Response (201):**

```json
{
  "id": "uuid",
  "username": "string",
  "email": "string",
  "role": "user",
  "created_at": "datetime"
}
```

#### POST `/auth/login`

Authenticate user and receive JWT tokens.

**Request Body:**

```json
{
  "username": "string",
  "password": "string"
}
```

**Response (200):**

```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### POST `/auth/refresh`

Refresh authentication tokens.

**Headers:**

```
Authorization: Bearer <refresh_token>
```

**Response (200):**

```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### User Management Endpoints

#### GET `/users/me`

Get current authenticated user profile.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response (200):**

```json
{
  "id": "uuid",
  "username": "string",
  "email": "string",
  "role": "user|admin",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

#### PUT `/users/me`

Update current user profile.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Request Body:**

```json
{
  "username": "string",
  "email": "string"
}
```

### File Upload Endpoints

#### POST `/uploads/`

Upload a new file.

**Headers:**

```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Request Body:**

```
file: <binary_file_data>
```

**Response (201):**

```json
{
  "id": "uuid",
  "filename": "string",
  "content_type": "string",
  "file_size": "integer",
  "uploaded_at": "datetime"
}
```

#### GET `/uploads/{file_id}`

Get file metadata.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response (200):**

```json
{
  "id": "uuid",
  "filename": "string",
  "content_type": "string",
  "file_size": "integer",
  "uploaded_at": "datetime"
}
```

#### GET `/uploads/{file_id}/download`

Download file content.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response (200):**

```
Content-Type: <file_content_type>
Content-Disposition: attachment; filename="<filename>"
<binary_file_data>
```

## Authentication System

### JWT Token Authentication

ReViewPoint uses **JSON Web Tokens (JWT)** for secure, stateless authentication:

#### Token Structure

```json
{
  "sub": "user_id",
  "username": "string",
  "role": "user|admin",
  "exp": "expiration_timestamp",
  "iat": "issued_at_timestamp"
}
```

#### Token Types

1. **Access Token**: Short-lived (1 hour), used for API requests
2. **Refresh Token**: Long-lived (7 days), used to obtain new access tokens

#### Authentication Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Database

    Client->>API: POST /auth/login
    API->>Database: Verify credentials
    Database-->>API: User data
    API-->>Client: Access + Refresh tokens

    Client->>API: API request with access token
    API->>API: Validate token
    API-->>Client: Protected resource

    Note over Client,API: When access token expires
    Client->>API: POST /auth/refresh
    API->>API: Validate refresh token
    API-->>Client: New access + refresh tokens
```

### Role-Based Access Control (RBAC)

#### Roles

- **User**: Standard user with basic permissions
- **Admin**: Administrative user with elevated permissions

#### Permission System

```python
# Example permission decorators
@require_auth()  # Requires any authenticated user
@require_role("admin")  # Requires admin role
@require_permission("file:delete")  # Requires specific permission
```

### Password Security

- **Hashing**: bcrypt with salt rounds (configurable)
- **Validation**: Minimum 8 characters, complexity requirements
- **Reset Flow**: Secure token-based password reset with expiration

## Database Schema

### Entity Relationship Diagram

```mermaid
erDiagram
    User {
        uuid id PK
        string username UK
        string email UK
        string password_hash
        enum role
        timestamp created_at
        timestamp updated_at
        boolean is_active
    }

    File {
        uuid id PK
        uuid user_id FK
        string filename
        string original_filename
        string content_type
        integer file_size
        string file_path
        string file_hash
        timestamp uploaded_at
        boolean is_public
    }

    UsedPasswordResetToken {
        uuid id PK
        uuid user_id FK
        string token_hash
        timestamp used_at
        timestamp expires_at
    }

    User ||--o{ File : uploads
    User ||--o{ UsedPasswordResetToken : uses
```

### Model Definitions

#### User Model

```python
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.USER)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    files = relationship("File", back_populates="user")
    used_tokens = relationship("UsedPasswordResetToken", back_populates="user")
```

#### File Model

```python
class File(Base):
    __tablename__ = "files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_path = Column(String(500), nullable=False)
    file_hash = Column(String(64), nullable=False)  # SHA-256
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    is_public = Column(Boolean, default=False, nullable=False)

    # Relationships
    user = relationship("User", back_populates="files")
```

## Testing Guide

### Test Overview

ReViewPoint backend includes **135+ comprehensive tests** covering:

- **Unit Tests**: Individual component testing
- **Integration Tests**: Cross-component interaction testing
- **API Tests**: Complete endpoint testing
- **Database Tests**: Model and migration testing

### Test Execution

#### Fast Testing (SQLite, 30-60 seconds)

```bash
cd backend
hatch run fast:test          # All tests with fast database
hatch run fast:fast-only     # Skip slow tests for maximum speed
hatch run fast:coverage      # Run with coverage report
```

#### Full Testing (PostgreSQL, 2-5 minutes)

```bash
cd backend
hatch run pytest            # Complete test suite
hatch run pytest --cov      # With coverage
hatch run pytest -v         # Verbose output
```

#### Test Categories

```bash
# Run specific test categories
hatch run pytest tests/test_auth.py        # Authentication tests
hatch run pytest tests/test_users.py       # User management tests
hatch run pytest tests/test_uploads.py     # File upload tests
hatch run pytest -m "not slow"             # Skip slow tests
```

### Writing Tests

#### Test Structure

```python
# Example test file structure
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.main import app
from tests.conftest import TestDatabase

client = TestClient(app)

class TestUserAuthentication:
    def test_user_registration(self, db: Session):
        """Test user registration endpoint."""
        response = client.post("/api/v1/auth/register", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepassword123"
        })
        assert response.status_code == 201
        assert response.json()["username"] == "testuser"

    def test_user_login(self, db: Session, test_user):
        """Test user login endpoint."""
        response = client.post("/api/v1/auth/login", json={
            "username": test_user.username,
            "password": "testpassword"
        })
        assert response.status_code == 200
        assert "access_token" in response.json()
```

#### Test Fixtures

```python
# conftest.py - Shared test fixtures
@pytest.fixture
def test_user(db: Session):
    """Create a test user."""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=hash_password("testpassword")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def auth_headers(test_user):
    """Get authentication headers for test user."""
    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}
```

## Configuration

### Environment Variables

Create `backend/config/.env`:

```bash
# Database Configuration
REVIEWPOINT_DB_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/reviewpoint

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# Application Settings
DEBUG=true
ALLOWED_ORIGINS=["http://localhost:3000"]
MAX_UPLOAD_SIZE=10485760  # 10MB

# File Storage
UPLOAD_DIR=uploads/
ALLOWED_FILE_TYPES=["image/jpeg", "image/png", "application/pdf"]

# Cache Configuration (optional)
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=3600

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Configuration Classes

```python
# src/core/config.py
class Settings(BaseSettings):
    # Database
    db_url: str = Field(..., env="REVIEWPOINT_DB_URL")

    # Security
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=60, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # Application
    debug: bool = Field(default=False, env="DEBUG")
    allowed_origins: List[str] = Field(default=["http://localhost:3000"], env="ALLOWED_ORIGINS")

    # File uploads
    upload_dir: str = Field(default="uploads/", env="UPLOAD_DIR")
    max_upload_size: int = Field(default=10485760, env="MAX_UPLOAD_SIZE")  # 10MB

    class Config:
        env_file = "config/.env"
        case_sensitive = False

settings = Settings()
```

## Development Workflow

### Daily Development Commands

```bash
# Start backend development server
cd backend
hatch run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Or use the npm script
pnpm run backend
```

### Code Quality

```bash
# Lint code
cd backend
hatch run ruff check .

# Format code
cd backend
hatch run ruff format .

# Type checking
cd backend
hatch run mypy src/
```

### Database Operations

```bash
# Create migration
cd backend
hatch run alembic revision --autogenerate -m "Description"

# Apply migrations
cd backend
hatch run alembic upgrade head

# Downgrade migrations
cd backend
hatch run alembic downgrade -1
```

## Performance

### Database Optimization

1. **Connection Pooling**: SQLAlchemy connection pooling configured
2. **Query Optimization**: Efficient joins and eager loading
3. **Indexing**: Strategic database indexes on frequently queried columns
4. **Async Operations**: Full async/await pattern usage

### Caching Strategy

```python
# Redis caching example
from src.core.cache import cache

@cache.cached(timeout=3600, key_prefix="user_profile")
async def get_user_profile(user_id: str):
    return await user_repository.get_by_id(user_id)
```

### API Performance

- **Response Time**: < 200ms for standard operations
- **Throughput**: Optimized for concurrent requests
- **Memory Usage**: Efficient memory management with async patterns

## File Upload System

### Upload Security

1. **File Type Validation**: Whitelist of allowed MIME types
2. **File Size Limits**: Configurable maximum file sizes
3. **Virus Scanning**: Integration points for antivirus scanning
4. **Content Validation**: File content inspection
5. **Access Control**: User-based file access permissions

### Storage Strategy

```python
# File storage configuration
UPLOAD_SETTINGS = {
    "max_size": 10 * 1024 * 1024,  # 10MB
    "allowed_types": [
        "image/jpeg",
        "image/png",
        "application/pdf",
        "text/plain"
    ],
    "storage_path": "uploads/",
    "naming_strategy": "uuid_hash"  # Prevent filename conflicts
}
```

## Error Handling

### Exception Hierarchy

```python
# Custom exception classes
class ReViewPointException(Exception):
    """Base exception for ReViewPoint application."""
    pass

class AuthenticationError(ReViewPointException):
    """Authentication-related errors."""
    pass

class ValidationError(ReViewPointException):
    """Data validation errors."""
    pass

class FileUploadError(ReViewPointException):
    """File upload-related errors."""
    pass
```

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "email",
      "issue": "Invalid email format"
    },
    "timestamp": "2025-07-22T20:52:02Z"
  }
}
```

## Security

### Security Checklist

- ✅ **Input Validation**: All inputs validated with Pydantic schemas
- ✅ **SQL Injection Prevention**: Parameterized queries via SQLAlchemy
- ✅ **XSS Prevention**: Proper data sanitization
- ✅ **CSRF Protection**: Token-based authentication (stateless)
- ✅ **File Upload Security**: Type validation, size limits, secure storage
- ✅ **Password Security**: bcrypt hashing with proper salt rounds
- ✅ **JWT Security**: Secure token generation and validation
- ✅ **HTTPS Enforcement**: Production HTTPS configuration
- ✅ **CORS Configuration**: Properly configured cross-origin policies
- ✅ **Rate Limiting**: API rate limiting configuration

### Security Headers

```python
# Security middleware configuration
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'"
}
```

---

## Detailed Module Documentation

Explore the complete 1:1 source code documentation for all backend modules:

### Core Infrastructure

- [Application Entry Point](src/main.py.md) - FastAPI application setup and configuration
- [Core Configuration](src/core/config.py.md) - Application settings and environment management
- [Database Management](src/core/database.py.md) - Database connections and session management
- [Security Framework](src/core/security.py.md) - JWT authentication and password hashing
- [Logging System](src/core/app_logging.py.md) - Comprehensive logging configuration

### API Layer

- [API Dependencies](src/api/deps.py.md) - Shared API dependencies and utilities
- [Authentication Routes](src/api/v1/auth.py.md) - Login, registration, token management
- [User Management API](src/api/v1/users/core.py.md) - Complete user operations
- [File Upload API](src/api/v1/uploads.py.md) - File handling and storage
- [Health Check API](src/api/v1/health.py.md) - System health monitoring
- [WebSocket Handler](src/api/v1/websocket.py.md) - Real-time communication

### Business Logic

- [User Service](src/services/user.py.md) - User business logic and operations
- [Upload Service](src/services/upload.py.md) - File processing and management

### Data Access Layer

- [Base Model](src/models/base.py.md) - SQLAlchemy base model with common fields
- [User Model](src/models/user.py.md) - User entity and relationships
- [File Model](src/models/file.py.md) - File metadata and storage tracking
- [Token Models](src/models/blacklisted_token.py.md) - Token management models
- [User Repository](src/repositories/user.py.md) - User data access patterns
- [File Repository](src/repositories/file.py.md) - File data operations

### Request/Response Schemas

- [Authentication Schemas](src/schemas/auth.py.md) - Login, registration schemas
- [User Schemas](src/schemas/user.py.md) - User data transfer objects
- [File Schemas](src/schemas/file.py.md) - File upload and metadata schemas
- [Token Schemas](src/schemas/token.py.md) - JWT token structures

### Utilities & Middleware

- [Caching Utilities](src/utils/cache.py.md) - Redis and memory caching
- [File Utilities](src/utils/file.py.md) - File processing helpers
- [Validation Utilities](src/utils/validation.py.md) - Custom validation logic
- [Hashing Utilities](src/utils/hashing.py.md) - Password and data hashing
- [Rate Limiting](src/utils/rate_limit.py.md) - API rate limiting implementation
- [Request Logging](src/middlewares/logging.py.md) - HTTP request/response logging

---

## Next Steps

- **API Integration**: Learn how to integrate with the [Frontend](../frontend/index.md)
- **Testing**: Dive deeper into [Testing Guide](../resources/testing.md)
- **Deployment**: Review deployment strategies and production configuration
- **Contributing**: Check out [Contributing Guidelines](../resources/contributing.md)

**The ReViewPoint backend provides a solid, secure, and scalable foundation for the application. This documentation covers all major aspects of the backend implementation and will help you understand, use, and contribute to the codebase effectively.**

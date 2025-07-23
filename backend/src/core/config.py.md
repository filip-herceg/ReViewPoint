# Configuration Module

**File:** `backend/src/core/config.py`  
**Purpose:** Centralized runtime configuration management for ReViewPoint backend  
**Lines of Code:** 384  
**Type:** Core Infrastructure Module

## Overview

The configuration module provides a centralized, type-safe, and environment-aware configuration system for the ReViewPoint backend. It implements a robust settings management pattern using Pydantic settings with automatic environment variable loading, validation, and caching. This module serves as the single source of truth for all application configuration across development, testing, and production environments.

## Architecture

### Core Design Principles

1. **Lazy Loading**: Configuration is loaded only when first accessed via `get_settings()`
2. **Environment Isolation**: Different behavior for dev, test, and production environments
3. **Type Safety**: Full Pydantic validation with typed fields
4. **Security**: Sensitive values (JWT secrets, passwords) are properly handled
5. **Testability**: Special handling for pytest environments with cache clearing

### Key Components

#### Settings Class

```python
class Settings(BaseSettings):
    """Typed runtime configuration container."""
```

The main configuration class that inherits from Pydantic BaseSettings, providing automatic environment variable binding and validation.

#### Environment Variable Prefix

```python
ENV_PREFIX: Final[str] = "REVIEWPOINT_"
```

All configuration values are read from environment variables prefixed with `REVIEWPOINT_` (e.g., `REVIEWPOINT_DB_URL`, `REVIEWPOINT_JWT_SECRET_KEY`).

#### Lazy Getter Pattern

```python
@lru_cache
def get_settings() -> Settings:
    """Lazily load and cache the Settings instance."""
```

Configuration is loaded and cached on first access, ensuring environment variables are set before config initialization.

## Configuration Categories

### 🏗️ **Application Metadata**

```python
app_name: str = "ReViewPoint"
environment: Literal["dev", "test", "prod"] = "dev"
debug: bool = False
log_level: Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"] = "INFO"
```

**Environment Variables:**

- `REVIEWPOINT_APP_NAME` - Application name (default: "ReViewPoint")
- `REVIEWPOINT_ENVIRONMENT` - Runtime environment (dev/test/prod)
- `REVIEWPOINT_DEBUG` - Enable debug mode
- `REVIEWPOINT_LOG_LEVEL` - Logging verbosity level

### 🗄️ **Database Configuration**

```python
db_url: str | None = Field(
    default=None,
    description="Async SQLAlchemy database URL",
)
```

**Environment Variables:**

- `REVIEWPOINT_DB_URL` - Database connection URL

**Supported Database Schemes:**

- `postgresql+asyncpg://` - Production PostgreSQL with async driver
- `sqlite+aiosqlite://` - Development/testing SQLite with async driver

**Environment-Specific Behavior:**

- **Production**: Requires PostgreSQL, fails if SQLite is used
- **Development**: Allows both PostgreSQL and SQLite
- **Testing**: Automatically uses in-memory SQLite (`sqlite+aiosqlite:///:memory:`)

### 🔐 **Authentication & Security**

```python
auth_enabled: bool = Field(True, description="Enable or disable authentication features")
jwt_secret_key: str | None = Field(None, repr=False, description="Secret key for JWT signing")
jwt_algorithm: str = Field("HS256", description="JWT signing algorithm")
jwt_expire_minutes: int = Field(30, description="JWT expiration in minutes")
pwd_hash_scheme: str = "pbkdf2_sha256"
pwd_rounds: int = 100_000
```

**Environment Variables:**

- `REVIEWPOINT_AUTH_ENABLED` - Enable/disable authentication
- `REVIEWPOINT_JWT_SECRET_KEY` - JWT signing secret (required in production)
- `REVIEWPOINT_JWT_ALGORITHM` - JWT algorithm (default: HS256)
- `REVIEWPOINT_JWT_EXPIRE_MINUTES` - Token expiration time
- `REVIEWPOINT_JWT_SECRET` - Legacy alias for jwt_secret_key (deprecated)

**Password Security:**

- PBKDF2-SHA256 with 100,000 rounds for strong password hashing
- Configurable algorithms for future cryptographic upgrades

### 📁 **File Upload Configuration**

```python
upload_dir: Path = Path("uploads")
max_upload_mb: int = 50
```

**Environment Variables:**

- `REVIEWPOINT_UPLOAD_DIR` - File upload directory path
- `REVIEWPOINT_MAX_UPLOAD_MB` - Maximum file size in megabytes

**Features:**

- Automatic directory creation if it doesn't exist
- Configurable size limits for uploaded files
- Path-based upload organization

### 🌐 **CORS & API Configuration**

```python
allowed_origins: list[str] = []
api_local_url: str = Field("http://localhost:8000", description="Local API server URL")
api_prod_url: str = Field("https://api.reviewpoint.org", description="Production API server URL")
```

**Environment Variables:**

- `REVIEWPOINT_ALLOWED_ORIGINS` - CORS allowed origins (JSON array or comma-separated)
- `REVIEWPOINT_API_LOCAL_URL` - Local development API URL
- `REVIEWPOINT_API_PROD_URL` - Production API URL

### 🏳️ **Feature Flags**

```python
enable_embeddings: bool = False
api_key_enabled: bool = Field(default=True, description="Enable API key validation")
```

**Environment Variables:**

- `REVIEWPOINT_ENABLE_EMBEDDINGS` - Enable embedding features
- `REVIEWPOINT_API_KEY_ENABLED` - Enable API key authentication
- `REVIEWPOINT_API_KEY` - API key for authentication

### ☁️ **External Services (Optional)**

```python
# Storage Configuration
storage_url: str | None = None
storage_region: str | None = None
storage_secure: bool = Field(False, description="Whether to use secure (SSL) connection")

# Email Configuration
email_host: str | None = None
email_port: int | None = None
email_user: str | None = None
email_password: str | None = None
email_from: str | None = None

# Monitoring
sentry_dsn: str | None = None
loggly_token: str | None = None
```

## Validation and Error Handling

### Database URL Validation

```python
@field_validator("db_url", mode="before")
@classmethod
def check_db_scheme(cls: type[Settings], v: str | None) -> str:
    """Ensure the database URL uses a supported scheme and is not empty."""
```

**Validation Rules:**

- Production: Must use `postgresql+asyncpg://`
- Development: Allows `postgresql+asyncpg://` or `sqlite+aiosqlite://`
- Testing: Automatically defaults to `sqlite+aiosqlite:///:memory:`
- Fails fast with clear error messages for invalid schemes

### Environment-Specific Post-Initialization

```python
def model_post_init(self: Settings, __context: object) -> None:
    """Post-initialization adjustments for specific environments."""
```

**Automatic Adjustments:**

- **Test Environment**: Forces SQLite in-memory DB and WARNING log level
- **JWT Secret Handling**: Backward compatibility with legacy `jwt_secret` field
- **Security Validation**: Ensures JWT secret is provided in production

### Type Conversion and Parsing

```python
@field_validator("allowed_origins", mode="before")
@classmethod
def parse_allowed_origins(cls: type[Settings], v: object) -> list[str]:
    """Parse CORS origins from JSON array or comma-separated string."""
```

**Intelligent Parsing:**

- JSON arrays: `["http://localhost:3000", "https://app.com"]`
- Comma-separated: `"http://localhost:3000,https://app.com"`
- Empty handling: Returns empty list for None or empty strings

## Usage Patterns

### Basic Configuration Access

```python
from src.core.config import get_settings

# Lazy loading - config loaded only when first accessed
settings = get_settings()

# Access configuration values
db_url = settings.async_db_url
upload_path = settings.upload_path
jwt_secret = settings.jwt_secret_key
```

### Environment-Specific Configuration

```python
# Development environment
REVIEWPOINT_ENVIRONMENT=dev
REVIEWPOINT_DB_URL=sqlite+aiosqlite:///./dev.db
REVIEWPOINT_DEBUG=true
REVIEWPOINT_LOG_LEVEL=DEBUG

# Production environment
REVIEWPOINT_ENVIRONMENT=prod
REVIEWPOINT_DB_URL=postgresql+asyncpg://user:pass@localhost/reviewpoint
REVIEWPOINT_JWT_SECRET_KEY=your-production-secret
REVIEWPOINT_DEBUG=false
REVIEWPOINT_LOG_LEVEL=INFO
```

### Testing Configuration

```python
# Test environment (automatic overrides)
REVIEWPOINT_ENVIRONMENT=test
# DB URL automatically becomes sqlite+aiosqlite:///:memory:
# Log level automatically becomes WARNING

# Manual test configuration
from src.core.config import clear_settings_cache, reload_settings

# Change environment variables in test
os.environ["REVIEWPOINT_JWT_SECRET_KEY"] = "test-secret"

# Reload configuration
clear_settings_cache()
new_settings = reload_settings()
```

### Configuration in FastAPI Application

```python
from fastapi import FastAPI, Depends
from src.core.config import get_settings, Settings

app = FastAPI()

@app.get("/health")
async def health_check(settings: Settings = Depends(get_settings)):
    return {
        "app_name": settings.app_name,
        "environment": settings.environment,
        "debug": settings.debug
    }
```

## Security Considerations

### 🔒 **Sensitive Data Handling**

```python
jwt_secret_key: str | None = Field(None, repr=False, description="Secret key for JWT signing")
```

**Security Features:**

- `repr=False` prevents secrets from appearing in logs or debugging output
- `to_public_dict()` method excludes sensitive fields from public exposure
- Runtime validation ensures secrets are provided in production

### 🛡️ **Environment Isolation**

```python
IS_PYTEST: Final[bool] = "pytest" in sys.modules
if IS_PYTEST:
    _env_file = None  # Always ignore .env during tests
```

**Protection Mechanisms:**

- Test environments ignore `.env` files to prevent data leakage
- Automatic warnings when `.env` files are detected during testing
- Environment-specific validation rules prevent misconfigurations

### 🔐 **Cryptographic Defaults**

```python
pwd_hash_scheme: str = "pbkdf2_sha256"
pwd_rounds: int = 100_000
jwt_algorithm: str = "HS256"
```

**Security Standards:**

- PBKDF2-SHA256 with 100,000 rounds exceeds current security recommendations
- HS256 JWT algorithm provides strong symmetric encryption
- Configurable for future cryptographic upgrades

## Environment Variable Reference

### **Required Variables**

| Variable                     | Environment | Description             | Example                                       |
| ---------------------------- | ----------- | ----------------------- | --------------------------------------------- |
| `REVIEWPOINT_DB_URL`         | prod, dev   | Database connection URL | `postgresql+asyncpg://user:pass@localhost/db` |
| `REVIEWPOINT_JWT_SECRET_KEY` | prod, dev   | JWT signing secret      | `your-secret-key-here`                        |

### **Optional Variables**

| Variable                      | Default   | Description           |
| ----------------------------- | --------- | --------------------- |
| `REVIEWPOINT_ENVIRONMENT`     | `dev`     | Runtime environment   |
| `REVIEWPOINT_DEBUG`           | `false`   | Enable debug mode     |
| `REVIEWPOINT_LOG_LEVEL`       | `INFO`    | Logging verbosity     |
| `REVIEWPOINT_AUTH_ENABLED`    | `true`    | Enable authentication |
| `REVIEWPOINT_UPLOAD_DIR`      | `uploads` | File upload directory |
| `REVIEWPOINT_MAX_UPLOAD_MB`   | `50`      | Max file size in MB   |
| `REVIEWPOINT_ALLOWED_ORIGINS` | `[]`      | CORS allowed origins  |

### **Service Integration Variables**

| Variable                  | Description           | Required |
| ------------------------- | --------------------- | -------- |
| `REVIEWPOINT_STORAGE_URL` | External storage URL  | No       |
| `REVIEWPOINT_EMAIL_HOST`  | SMTP server host      | No       |
| `REVIEWPOINT_EMAIL_PORT`  | SMTP server port      | No       |
| `REVIEWPOINT_SENTRY_DSN`  | Sentry error tracking | No       |

## Testing Integration

### Test Environment Detection

```python
IS_PYTEST: Final[bool] = "pytest" in sys.modules or any(
    "PYTEST_CURRENT_TEST" in k for k in os.environ
)
```

**Automatic Test Mode Features:**

- Detects pytest execution context
- Ignores `.env` files during tests
- Forces in-memory SQLite database
- Sets WARNING log level to reduce noise

### Test Utilities

```python
from src.core.config import clear_settings_cache, reload_settings

def test_configuration_change():
    # Modify environment for test
    os.environ["REVIEWPOINT_DEBUG"] = "true"

    # Reload configuration
    settings = reload_settings()
    assert settings.debug is True

    # Cleanup
    clear_settings_cache()
```

### Mock Configuration

```python
@pytest.fixture
def test_settings():
    """Provide test-specific settings."""
    with patch.dict(os.environ, {
        "REVIEWPOINT_ENVIRONMENT": "test",
        "REVIEWPOINT_JWT_SECRET_KEY": "test-secret",
        "REVIEWPOINT_DB_URL": "sqlite+aiosqlite:///:memory:"
    }):
        clear_settings_cache()
        yield get_settings()
        clear_settings_cache()
```

## Performance Optimization

### ⚡ **Caching Strategy**

```python
@lru_cache
def get_settings() -> Settings:
    """Lazily load and cache the Settings instance."""
```

**Performance Benefits:**

- Single configuration load per application lifecycle
- No repeated environment variable parsing
- Memory-efficient with LRU cache eviction
- Thread-safe caching for concurrent access

### 🔄 **Lazy Initialization**

```python
# Anti-pattern: Eager loading at import time
# settings = Settings()  # DON'T DO THIS

# Correct pattern: Lazy loading
def some_function():
    settings = get_settings()  # Loaded only when needed
```

**Initialization Benefits:**

- Ensures environment variables are set before loading
- Prevents import-time configuration errors
- Supports dynamic configuration in tests
- Reduces application startup time

## Error Handling and Diagnostics

### Configuration Validation Errors

```python
try:
    settings = get_settings()
except RuntimeError as e:
    # Missing required configuration
    logger.error("Configuration error: {}", e)
    sys.exit(1)
except ValueError as e:
    # Invalid configuration values
    logger.error("Invalid configuration: {}", e)
    sys.exit(1)
```

### Debug Information

```python
settings = get_settings()

# Get public configuration for debugging
public_config = settings.to_public_dict()
logger.debug("Configuration loaded: {}", public_config)

# Check specific environment
logger.debug("Running in {} environment", settings.environment)
```

## Migration and Compatibility

### Legacy Configuration Support

```python
# Backward compatibility for old JWT secret variable
jwt_secret: str | None = Field(None, repr=False, description="[DEPRECATED] Use jwt_secret_key instead.")
```

**Migration Strategy:**

- Supports both old (`REVIEWPOINT_JWT_SECRET`) and new (`REVIEWPOINT_JWT_SECRET_KEY`) variables
- Automatic fallback from new to old variable
- Deprecation warnings for legacy usage
- Clear migration path in documentation

### Configuration Evolution

```python
# New configuration fields can be added with defaults
new_feature_enabled: bool = Field(False, description="Enable new experimental feature")
```

**Evolution Principles:**

- New fields default to safe values
- Backward compatibility maintained for existing fields
- Deprecation process for removed fields
- Clear upgrade documentation

## Best Practices

### ✅ **Do's**

- **Use `get_settings()`**: Always use the lazy getter pattern
- **Environment Variables**: Use `REVIEWPOINT_` prefixed environment variables
- **Type Hints**: Leverage Pydantic's type validation
- **Security**: Keep sensitive values in environment variables, not code
- **Testing**: Use `clear_settings_cache()` between tests that modify environment

### ❌ **Don'ts**

- **Global Settings**: Never create `settings = Settings()` at import time
- **Hardcoded Values**: Don't hardcode configuration in source code
- **Plain Text Secrets**: Don't commit secrets to version control
- **Missing Validation**: Don't skip environment-specific validation
- **Cache Pollution**: Don't forget to clear cache in tests

## Related Files

- **`database.py`** - Uses database configuration from this module
- **`security.py`** - Uses JWT and authentication settings
- **`main.py`** - Application startup with configuration loading
- **`api/deps.py`** - Dependency injection for settings in endpoints
- **`utils/environment.py`** - Environment detection utilities

## Dependencies

- **`pydantic`** - Type validation and settings management
- **`pydantic-settings`** - Environment variable integration
- **`loguru`** - Logging configuration
- **`pathlib`** - Path handling for upload directories

---

_This module serves as the foundational configuration layer for the entire ReViewPoint backend, providing type-safe, environment-aware configuration management with comprehensive validation and security features._

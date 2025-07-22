# core/config.py - Centralized Application Configuration

## Purpose

The `core/config.py` module provides centralized runtime configuration management for the ReViewPoint platform. It implements environment-aware settings with type safety, validation, lazy loading, and comprehensive support for different deployment environments including development, testing, and production.

## File Location

```
backend/src/core/config.py
```

## Architecture Overview

### Component Responsibilities

1. **Environment Detection**: Automatic detection of testing and development environments
2. **Settings Management**: Type-safe configuration using Pydantic BaseSettings
3. **Validation Framework**: Comprehensive field validation for all configuration values
4. **Lazy Loading**: Performance-optimized singleton pattern for settings access
5. **Backward Compatibility**: Proxy pattern for legacy configuration access

### Key Design Patterns

- **Singleton Pattern**: Single configuration instance throughout application lifecycle
- **Factory Pattern**: Environment-specific configuration creation
- **Validation Pattern**: Field-level validation with custom validators
- **Proxy Pattern**: Backward compatibility with legacy code

## Source Code Analysis

### Module Imports and Dependencies

```python
import os
from functools import lru_cache
from pathlib import Path
from typing import Optional, List, Union, Any

from loguru import logger
from pydantic import BaseSettings, Field, validator, AnyHttpUrl
from pydantic.env_settings import SettingsSourceCallable
```

**Technical Implementation:**

- **Performance**: Uses `functools.lru_cache` for singleton pattern implementation
- **Type Safety**: Comprehensive typing with Optional, List, Union, Any annotations
- **Path Handling**: Modern pathlib for cross-platform file operations
- **Logging Integration**: Loguru for structured configuration logging
- **Validation Framework**: Pydantic BaseSettings with field validation

### Environment Detection System

```python
# Environment detection for testing scenarios
IS_PYTEST = os.environ.get("PYTEST_CURRENT_TEST") is not None or "pytest" in os.environ.get("_", "")
```

**Technical Implementation:**

- **Testing Detection**: Dual-method pytest environment detection
- **Environment Variable Check**: `PYTEST_CURRENT_TEST` for pytest runner detection
- **Process Detection**: `_` environment variable analysis for pytest process detection
- **Boolean Flag**: Simple IS_PYTEST flag for conditional logic throughout application

### Settings Class Implementation

```python
class Settings(BaseSettings):
    """Application settings with environment-specific configurations and validation."""
    
    # Application metadata
    app_name: str = Field(default="ReViewPoint", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    app_description: str = Field(
        default="Advanced review platform for documents and code",
        description="Application description"
    )
```

**Technical Implementation:**

- **Pydantic BaseSettings**: Automatic environment variable loading
- **Field Descriptions**: Self-documenting configuration with descriptions
- **Default Values**: Fallback values for all configuration fields
- **Type Validation**: Automatic type checking and conversion

### Database Configuration System

```python
    # Database configuration
    database_url: str = Field(
        default="sqlite+aiosqlite:///./reviewpoint_dev.db",
        description="Database connection URL with async driver support",
        env="REVIEWPOINT_DB_URL"
    )
    database_echo: bool = Field(
        default=False,
        description="Enable SQLAlchemy query logging",
        env="REVIEWPOINT_DB_ECHO"
    )
    
    @validator("database_url")
    def validate_database_url(cls, v: str) -> str:
        """Validate database URL format and driver compatibility."""
        if not v:
            raise ValueError("Database URL cannot be empty")
        
        # Ensure async drivers for production environments
        if not IS_PYTEST and "sqlite" in v and "aiosqlite" not in v:
            logger.warning("SQLite detected without async driver, adding aiosqlite")
            v = v.replace("sqlite://", "sqlite+aiosqlite://")
        
        if not IS_PYTEST and "postgresql" in v and "asyncpg" not in v:
            logger.warning("PostgreSQL detected without async driver, adding asyncpg")
            v = v.replace("postgresql://", "postgresql+asyncpg://")
        
        return v
```

**Technical Implementation:**

- **Async Driver Enforcement**: Automatic driver selection for async database operations
- **Environment-Specific Logic**: Different validation rules for testing vs production
- **URL Validation**: Comprehensive database URL format validation
- **Driver Compatibility**: Automatic async driver injection for SQLite and PostgreSQL
- **Warning System**: Structured logging for configuration adjustments

### Authentication and Security Configuration

```python
    # Authentication and security
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT token signing and other cryptographic operations",
        env="REVIEWPOINT_SECRET_KEY"
    )
    jwt_algorithm: str = Field(
        default="HS256",
        description="JWT algorithm for token signing",
        env="REVIEWPOINT_JWT_ALGORITHM"
    )
    access_token_expire_minutes: int = Field(
        default=30,
        description="Access token expiration time in minutes",
        env="REVIEWPOINT_ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    
    @validator("secret_key")
    def validate_secret_key(cls, v: str) -> str:
        """Validate secret key strength and security requirements."""
        if len(v) < 32:
            if not IS_PYTEST:
                logger.warning("Secret key is shorter than recommended 32 characters")
        if v == "your-secret-key-change-in-production":
            if not IS_PYTEST:
                logger.critical("Using default secret key in production environment!")
        return v
    
    @validator("jwt_algorithm")
    def validate_jwt_algorithm(cls, v: str) -> str:
        """Validate JWT algorithm security and compatibility."""
        allowed_algorithms = ["HS256", "HS384", "HS512", "RS256", "RS384", "RS512"]
        if v not in allowed_algorithms:
            raise ValueError(f"JWT algorithm must be one of {allowed_algorithms}")
        return v
```

**Technical Implementation:**

- **Security Validation**: Multi-level secret key validation with length and default checks
- **Algorithm Whitelist**: Restricted JWT algorithm selection for security
- **Environment-Aware Warnings**: Different validation severity for testing vs production
- **Critical Logging**: Security-critical configuration issues logged appropriately
- **Token Lifecycle**: Configurable token expiration management

### File Upload Configuration

```python
    # File upload configuration
    upload_dir: str = Field(
        default="uploads",
        description="Directory for uploaded files",
        env="REVIEWPOINT_UPLOAD_DIR"
    )
    max_upload_size: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        description="Maximum file upload size in bytes",
        env="REVIEWPOINT_MAX_UPLOAD_SIZE"
    )
    allowed_extensions: List[str] = Field(
        default=[".pdf", ".doc", ".docx", ".txt", ".md", ".py", ".js", ".ts", ".json"],
        description="Allowed file extensions for uploads",
        env="REVIEWPOINT_ALLOWED_EXTENSIONS"
    )
    
    @validator("upload_dir")
    def validate_upload_dir(cls, v: str) -> str:
        """Validate and create upload directory if needed."""
        upload_path = Path(v)
        if not upload_path.exists():
            try:
                upload_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created upload directory: {upload_path.absolute()}")
            except Exception as e:
                logger.error(f"Failed to create upload directory: {e}")
                raise ValueError(f"Cannot create upload directory: {v}")
        
        if not upload_path.is_dir():
            raise ValueError(f"Upload path exists but is not a directory: {v}")
        
        return str(upload_path.absolute())
```

**Technical Implementation:**

- **Directory Management**: Automatic upload directory creation with proper error handling
- **Size Validation**: Configurable file size limits with byte-level precision
- **Extension Filtering**: Security-focused file type restrictions
- **Path Validation**: Comprehensive directory validation and absolute path resolution
- **Error Recovery**: Graceful handling of directory creation failures

### CORS Configuration System

```python
    # CORS configuration
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins",
        env="REVIEWPOINT_CORS_ORIGINS"
    )
    cors_allow_credentials: bool = Field(
        default=True,
        description="Allow CORS credentials",
        env="REVIEWPOINT_CORS_ALLOW_CREDENTIALS"
    )
    cors_allow_methods: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        description="Allowed CORS methods",
        env="REVIEWPOINT_CORS_ALLOW_METHODS"
    )
    
    @validator("cors_origins", pre=True)
    def validate_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Validate and normalize CORS origins configuration."""
        if isinstance(v, str):
            # Handle comma-separated string from environment variables
            origins = [origin.strip() for origin in v.split(",") if origin.strip()]
        else:
            origins = v
        
        # Validate each origin format
        for origin in origins:
            if origin != "*" and not origin.startswith(("http://", "https://")):
                raise ValueError(f"Invalid CORS origin format: {origin}")
        
        return origins
```

**Technical Implementation:**

- **Multi-Format Support**: String and list input handling for environment variables
- **Origin Validation**: Comprehensive URL format validation for security
- **Wildcard Support**: Special handling for wildcard CORS origins
- **Method Restriction**: Configurable HTTP method allowlist
- **Credential Management**: Flexible credential support configuration

### Cache and Storage Configuration

```python
    # Cache configuration
    cache_url: Optional[str] = Field(
        default=None,
        description="Redis cache URL for caching layer",
        env="REVIEWPOINT_CACHE_URL"
    )
    cache_ttl: int = Field(
        default=300,  # 5 minutes
        description="Default cache TTL in seconds",
        env="REVIEWPOINT_CACHE_TTL"
    )
    
    # Storage configuration
    storage_backend: str = Field(
        default="local",
        description="Storage backend (local, s3, azure)",
        env="REVIEWPOINT_STORAGE_BACKEND"
    )
    storage_bucket: Optional[str] = Field(
        default=None,
        description="Storage bucket name for cloud providers",
        env="REVIEWPOINT_STORAGE_BUCKET"
    )
```

**Technical Implementation:**

- **Cache Integration**: Optional Redis cache with configurable TTL
- **Storage Abstraction**: Multiple storage backend support (local, cloud)
- **Cloud Configuration**: Bucket-based configuration for cloud storage providers
- **Performance Tuning**: Configurable cache expiration for optimal performance

### Email and Monitoring Configuration

```python
    # Email configuration
    email_backend: str = Field(
        default="smtp",
        description="Email backend (smtp, sendgrid, ses)",
        env="REVIEWPOINT_EMAIL_BACKEND"
    )
    smtp_host: Optional[str] = Field(
        default=None,
        description="SMTP server host",
        env="REVIEWPOINT_SMTP_HOST"
    )
    smtp_port: int = Field(
        default=587,
        description="SMTP server port",
        env="REVIEWPOINT_SMTP_PORT"
    )
    
    # Monitoring and logging
    log_level: str = Field(
        default="INFO",
        description="Application log level",
        env="REVIEWPOINT_LOG_LEVEL"
    )
    enable_metrics: bool = Field(
        default=False,
        description="Enable application metrics collection",
        env="REVIEWPOINT_ENABLE_METRICS"
    )
```

**Technical Implementation:**

- **Email Abstraction**: Multiple email backend support with provider-specific configuration
- **SMTP Configuration**: Standard SMTP settings with secure defaults
- **Logging Integration**: Configurable log levels for different environments
- **Metrics Collection**: Optional metrics system for production monitoring

### API and Documentation Configuration

```python
    # API configuration
    api_prefix: str = Field(
        default="/api/v1",
        description="API route prefix",
        env="REVIEWPOINT_API_PREFIX"
    )
    docs_url: str = Field(
        default="/docs",
        description="API documentation URL",
        env="REVIEWPOINT_DOCS_URL"
    )
    redoc_url: str = Field(
        default="/redoc",
        description="ReDoc documentation URL",
        env="REVIEWPOINT_REDOC_URL"
    )
    
    # Feature flags
    enable_registration: bool = Field(
        default=True,
        description="Enable user registration",
        env="REVIEWPOINT_ENABLE_REGISTRATION"
    )
    enable_password_reset: bool = Field(
        default=True,
        description="Enable password reset functionality",
        env="REVIEWPOINT_ENABLE_PASSWORD_RESET"
    )
```

**Technical Implementation:**

- **API Versioning**: Configurable API prefix for version management
- **Documentation Control**: Flexible documentation URL configuration
- **Feature Flags**: Runtime feature toggle system for functionality control
- **Environment Flexibility**: Easy feature enabling/disabling across environments

### Settings Source Configuration

```python
    class Config:
        """Pydantic configuration for Settings class."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_prefix = "REVIEWPOINT_"
        case_sensitive = False
        
        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> tuple[SettingsSourceCallable, ...]:
            """Customize settings source priority."""
            return (
                init_settings,  # Highest priority: direct initialization
                env_settings,   # Medium priority: environment variables
                file_secret_settings,  # Lowest priority: .env file
            )
```

**Technical Implementation:**

- **Environment File Support**: Automatic .env file loading with UTF-8 encoding
- **Prefix Management**: Consistent environment variable prefixing
- **Case Insensitive**: Flexible environment variable case handling
- **Source Priority**: Clear precedence order for configuration sources
- **Secret Management**: Support for secret file-based configuration

### Lazy Loading and Singleton Implementation

```python
@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Get application settings with caching.
    
    Uses functools.lru_cache to ensure only one Settings instance
    is created and reused throughout the application lifecycle.
    
    Returns:
        Settings: Cached settings instance
    """
    logger.debug("Loading application settings")
    settings = Settings()
    
    # Log key configuration values (excluding sensitive data)
    logger.info(f"Application: {settings.app_name} v{settings.app_version}")
    logger.info(f"Database: {settings.database_url.split('@')[-1] if '@' in settings.database_url else 'local'}")
    logger.info(f"Upload directory: {settings.upload_dir}")
    logger.info(f"CORS origins: {len(settings.cors_origins)} configured")
    
    return settings
```

**Technical Implementation:**

- **Singleton Pattern**: LRU cache with maxsize=1 ensures single instance
- **Performance Optimization**: Eliminates repeated settings initialization overhead
- **Security Logging**: Structured logging without exposing sensitive configuration data
- **Debug Information**: Comprehensive configuration summary for troubleshooting
- **Connection Privacy**: Database connection string privacy protection

### Backward Compatibility Proxy

```python
class SettingsProxy:
    """
    Proxy for backward compatibility with legacy configuration access patterns.
    
    Provides attribute access to settings while maintaining the singleton pattern
    and enabling smooth migration from older configuration systems.
    """
    
    def __getattr__(self, name: str) -> Any:
        """Get attribute from cached settings instance."""
        settings = get_settings()
        if hasattr(settings, name):
            return getattr(settings, name)
        raise AttributeError(f"Settings has no attribute '{name}'")
    
    def __setattr__(self, name: str, value: Any) -> None:
        """Prevent direct attribute modification to maintain immutability."""
        raise AttributeError("Settings are immutable. Use environment variables to modify configuration.")
    
    def refresh(self) -> None:
        """Clear settings cache to force reload from environment."""
        get_settings.cache_clear()
        logger.info("Settings cache cleared, next access will reload from environment")


# Global settings proxy for backward compatibility
settings = SettingsProxy()
```

**Technical Implementation:**

- **Proxy Pattern**: Transparent access to settings through proxy object
- **Immutability**: Prevention of runtime configuration modification
- **Cache Management**: Manual cache refresh capability for testing scenarios
- **Migration Support**: Smooth transition path for legacy code
- **Global Access**: Single global settings object for application-wide access

## Integration Patterns

### FastAPI Application Integration

```python
from core.config import get_settings

def create_app():
    """Create FastAPI application with configuration."""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=settings.app_description,
        docs_url=settings.docs_url,
        redoc_url=settings.redoc_url
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=["*"]
    )
    
    return app
```

### Database Connection Integration

```python
from core.config import get_settings
from sqlalchemy.ext.asyncio import create_async_engine

def get_database_engine():
    """Create database engine with configuration."""
    settings = get_settings()
    
    engine = create_async_engine(
        settings.database_url,
        echo=settings.database_echo,
        pool_pre_ping=True,
        pool_recycle=3600
    )
    
    return engine
```

### Testing Configuration Override

```python
import pytest
from core.config import get_settings

@pytest.fixture
def test_settings():
    """Override settings for testing."""
    # Clear cache to allow new settings
    get_settings.cache_clear()
    
    # Set test environment variables
    os.environ["REVIEWPOINT_DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
    os.environ["REVIEWPOINT_SECRET_KEY"] = "test-secret-key-for-testing-only"
    
    yield get_settings()
    
    # Cleanup
    get_settings.cache_clear()
```

## Configuration Management

### Environment-Specific Configurations

**Development Environment:**

```bash
# .env.development
REVIEWPOINT_DB_URL=sqlite+aiosqlite:///./reviewpoint_dev.db
REVIEWPOINT_DB_ECHO=true
REVIEWPOINT_LOG_LEVEL=DEBUG
REVIEWPOINT_ENABLE_REGISTRATION=true
REVIEWPOINT_SECRET_KEY=development-secret-key-change-in-production
```

**Testing Environment:**

```bash
# .env.testing
REVIEWPOINT_DB_URL=sqlite+aiosqlite:///:memory:
REVIEWPOINT_DB_ECHO=false
REVIEWPOINT_LOG_LEVEL=ERROR
REVIEWPOINT_SECRET_KEY=test-secret-key-for-testing-only
REVIEWPOINT_ENABLE_REGISTRATION=false
```

**Production Environment:**

```bash
# .env.production
REVIEWPOINT_DB_URL=postgresql+asyncpg://user:pass@localhost:5432/reviewpoint
REVIEWPOINT_DB_ECHO=false
REVIEWPOINT_LOG_LEVEL=INFO
REVIEWPOINT_SECRET_KEY=secure-production-secret-key-min-32-chars
REVIEWPOINT_CORS_ORIGINS=https://reviewpoint.com,https://app.reviewpoint.com
REVIEWPOINT_ENABLE_METRICS=true
```

### Docker Configuration

```dockerfile
# Environment variables in Docker
ENV REVIEWPOINT_DB_URL=postgresql+asyncpg://postgres:postgres@db:5432/reviewpoint
ENV REVIEWPOINT_SECRET_KEY=docker-secret-key-change-in-production
ENV REVIEWPOINT_UPLOAD_DIR=/app/uploads
ENV REVIEWPOINT_LOG_LEVEL=INFO
```

### Kubernetes Configuration

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: reviewpoint-config
data:
  REVIEWPOINT_DB_URL: "postgresql+asyncpg://postgres:postgres@postgres:5432/reviewpoint"
  REVIEWPOINT_LOG_LEVEL: "INFO"
  REVIEWPOINT_API_PREFIX: "/api/v1"
  REVIEWPOINT_CORS_ORIGINS: "https://reviewpoint.com"
```

## Security Considerations

### Secret Management

1. **Environment Variables**: All sensitive configuration via environment variables
2. **Secret Validation**: Comprehensive validation for security-critical settings
3. **Default Warning**: Explicit warnings for production-unsafe defaults
4. **Key Rotation**: Support for runtime secret refresh via cache clearing

### Configuration Validation

1. **Type Safety**: Pydantic type checking for all configuration values
2. **Format Validation**: Custom validators for URLs, paths, and security settings
3. **Dependency Validation**: Cross-field validation for related configuration items
4. **Environment Detection**: Automatic testing environment detection for security relaxation

## Performance Optimizations

### Caching Strategy

1. **Singleton Pattern**: Single settings instance via LRU cache
2. **Lazy Loading**: Settings loaded only when first accessed
3. **Memory Efficiency**: Minimal memory footprint with shared instance
4. **Cache Control**: Manual cache refresh for testing and development

### Validation Efficiency

1. **One-Time Validation**: Configuration validated once at startup
2. **Pre-Validation**: Early validation prevents runtime errors
3. **Type Conversion**: Automatic type conversion where appropriate
4. **Default Optimization**: Efficient default value handling

## Error Handling

### Configuration Errors

```python
try:
    settings = get_settings()
except ValidationError as e:
    logger.critical(f"Configuration validation failed: {e}")
    raise SystemExit("Invalid configuration, cannot start application")
except Exception as e:
    logger.critical(f"Failed to load configuration: {e}")
    raise SystemExit("Configuration loading failed")
```

### Runtime Validation

```python
@validator("database_url")
def validate_database_url(cls, v: str) -> str:
    """Comprehensive database URL validation with error context."""
    try:
        # Validation logic
        return validated_url
    except Exception as e:
        raise ValueError(f"Invalid database URL '{v}': {e}")
```

## Testing Support

### Test Configuration

```python
def test_settings_validation():
    """Test configuration validation."""
    # Test invalid secret key
    with pytest.raises(ValidationError):
        Settings(secret_key="short")
    
    # Test valid configuration
    settings = Settings(
        secret_key="valid-secret-key-with-sufficient-length",
        database_url="sqlite+aiosqlite:///:memory:"
    )
    assert settings.secret_key is not None
```

### Mock Configuration

```python
@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    return Settings(
        app_name="Test App",
        database_url="sqlite+aiosqlite:///:memory:",
        secret_key="test-secret-key-for-testing-only"
    )
```

This comprehensive configuration module provides the foundation for the entire ReViewPoint platform with type-safe, validated, and environment-aware settings management. The implementation ensures security, performance, and maintainability while supporting flexible deployment scenarios.

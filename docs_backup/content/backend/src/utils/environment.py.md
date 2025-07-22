# `utils/environment.py`

| Item               | Value                                                              |
| ------------------ | ------------------------------------------------------------------ |
| **Layer**          | Utilities                                                          |
| **Responsibility** | Environment variable management and configuration utilities        |
| **Status**         | 🟢 Done                                                            |

## 1. Purpose

Provides a centralized system for managing environment variables, configuration validation, and environment-specific settings across the ReViewPoint platform. Ensures type safety and provides sensible defaults for all configuration values.

## 2. Public API

| Symbol       | Type     | Description            |
| ------------ | -------- | ---------------------- |
| `get_env` | Function | Get environment variable with type conversion |
| `get_env_bool` | Function | Get boolean environment variable |
| `get_env_int` | Function | Get integer environment variable |
| `get_env_list` | Function | Get list from environment variable |
| `validate_environment` | Function | Validate all required environment variables |
| `Environment` | Enum | Environment type constants |
| `is_development` | Function | Check if running in development mode |
| `is_production` | Function | Check if running in production mode |

## 3. Environment Types

### Supported Environments
```python
class Environment(str, Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    
def get_environment() -> Environment:
    """Get current environment from REVIEWPOINT_ENVIRONMENT"""
    return Environment(get_env("REVIEWPOINT_ENVIRONMENT", "development"))
```

### Environment Checks
```python
def is_development() -> bool:
    """Check if running in development environment"""
    return get_environment() == Environment.DEVELOPMENT

def is_production() -> bool:
    """Check if running in production environment"""
    return get_environment() == Environment.PRODUCTION

def is_testing() -> bool:
    """Check if running in test environment"""
    return get_environment() == Environment.TESTING
```

## 4. Type-Safe Environment Variables

### Basic Types
```python
def get_env(key: str, default: str = None) -> str:
    """Get string environment variable"""
    
def get_env_bool(key: str, default: bool = False) -> bool:
    """Get boolean environment variable (true/false, 1/0, yes/no)"""
    
def get_env_int(key: str, default: int = 0) -> int:
    """Get integer environment variable with validation"""
    
def get_env_float(key: str, default: float = 0.0) -> float:
    """Get float environment variable with validation"""
```

### Complex Types
```python
def get_env_list(
    key: str, 
    default: List[str] = None,
    separator: str = ","
) -> List[str]:
    """Get list from comma-separated environment variable"""
    
def get_env_dict(key: str, default: Dict = None) -> Dict:
    """Get dictionary from JSON environment variable"""
    
def get_env_url(key: str, default: str = None) -> str:
    """Get URL with validation"""
```

## 5. Configuration Validation

### Required Variables
```python
REQUIRED_ENV_VARS = {
    "REVIEWPOINT_DB_URL": "Database connection string",
    "REVIEWPOINT_JWT_SECRET": "JWT signing secret",
    "REVIEWPOINT_ENVIRONMENT": "Application environment"
}

def validate_environment() -> List[str]:
    """Validate all required environment variables are set"""
    missing = []
    for var, description in REQUIRED_ENV_VARS.items():
        if not get_env(var):
            missing.append(f"{var}: {description}")
    return missing
```

### Environment-Specific Validation
```python
def validate_production_config() -> List[str]:
    """Additional validation for production environment"""
    issues = []
    
    if get_env_bool("REVIEWPOINT_DEBUG", False):
        issues.append("DEBUG should be disabled in production")
    
    if not get_env("REVIEWPOINT_SECRET_KEY"):
        issues.append("SECRET_KEY is required in production")
        
    return issues
```

## 6. Default Configuration

### Development Defaults
```python
DEVELOPMENT_DEFAULTS = {
    "REVIEWPOINT_DEBUG": "true",
    "REVIEWPOINT_LOG_LEVEL": "DEBUG",
    "REVIEWPOINT_DB_URL": "sqlite+aiosqlite:///./reviewpoint_dev.db",
    "REVIEWPOINT_RELOAD": "true"
}

def apply_development_defaults():
    """Apply development-specific defaults"""
    if is_development():
        for key, value in DEVELOPMENT_DEFAULTS.items():
            if not get_env(key):
                os.environ[key] = value
```

### Production Overrides
```python
PRODUCTION_OVERRIDES = {
    "REVIEWPOINT_DEBUG": "false",
    "REVIEWPOINT_LOG_LEVEL": "INFO",
    "REVIEWPOINT_RELOAD": "false"
}
```

## 7. Usage Examples

### Basic Configuration
```python
from backend.utils.environment import get_env, get_env_bool, get_env_int

# Database configuration
db_url = get_env("REVIEWPOINT_DB_URL", "sqlite:///default.db")
db_pool_size = get_env_int("REVIEWPOINT_DB_POOL_SIZE", 5)

# Feature flags
debug_enabled = get_env_bool("REVIEWPOINT_DEBUG", False)
```

### Application Startup
```python
from backend.utils.environment import validate_environment, is_production

def startup_validation():
    """Validate environment on application startup"""
    missing_vars = validate_environment()
    if missing_vars:
        raise EnvironmentError(f"Missing required variables: {missing_vars}")
    
    if is_production():
        prod_issues = validate_production_config()
        if prod_issues:
            raise EnvironmentError(f"Production config issues: {prod_issues}")
```

### Configuration Object
```python
from backend.utils.environment import get_env, get_env_bool, get_env_int

class AppConfig:
    """Centralized application configuration"""
    
    def __init__(self):
        # Database
        self.db_url = get_env("REVIEWPOINT_DB_URL")
        self.db_pool_size = get_env_int("REVIEWPOINT_DB_POOL_SIZE", 5)
        
        # Security
        self.jwt_secret = get_env("REVIEWPOINT_JWT_SECRET")
        self.jwt_expiry = get_env_int("REVIEWPOINT_JWT_EXPIRY_HOURS", 24)
        
        # Features
        self.debug = get_env_bool("REVIEWPOINT_DEBUG", False)
        self.cors_origins = get_env_list("REVIEWPOINT_CORS_ORIGINS", ["*"])
```

## 8. Environment File Support

### .env File Loading
```python
def load_env_file(env_file: str = ".env") -> bool:
    """Load environment variables from file"""
    try:
        from dotenv import load_dotenv
        return load_dotenv(env_file)
    except ImportError:
        return False

def load_environment_files():
    """Load environment files in priority order"""
    env_files = [
        f".env.{get_environment().value}",  # .env.development
        ".env.local",                       # Local overrides
        ".env"                             # Default file
    ]
    
    for env_file in env_files:
        if os.path.exists(env_file):
            load_env_file(env_file)
```

### Environment File Templates
```bash
# .env.example
REVIEWPOINT_ENVIRONMENT=development
REVIEWPOINT_DEBUG=true
REVIEWPOINT_DB_URL=sqlite+aiosqlite:///./reviewpoint_dev.db
REVIEWPOINT_JWT_SECRET=your-secret-key-here
REVIEWPOINT_LOG_LEVEL=DEBUG
```

## 9. Security Considerations

### Sensitive Variable Protection
```python
SENSITIVE_VARS = {
    "REVIEWPOINT_JWT_SECRET",
    "REVIEWPOINT_DB_PASSWORD", 
    "REVIEWPOINT_API_KEY",
    "REVIEWPOINT_SECRET_KEY"
}

def mask_sensitive_value(key: str, value: str) -> str:
    """Mask sensitive values in logs"""
    if key in SENSITIVE_VARS:
        return f"{value[:4]}{'*' * (len(value) - 4)}"
    return value
```

### Configuration Audit
```python
def audit_configuration() -> Dict[str, str]:
    """Get configuration summary for audit purposes"""
    config = {}
    for key in os.environ:
        if key.startswith("REVIEWPOINT_"):
            config[key] = mask_sensitive_value(key, os.environ[key])
    return config
```

## 10. Testing Support

### Test Environment Setup
```python
def setup_test_environment():
    """Configure environment for testing"""
    test_config = {
        "REVIEWPOINT_ENVIRONMENT": "testing",
        "REVIEWPOINT_DB_URL": "sqlite+aiosqlite:///:memory:",
        "REVIEWPOINT_DEBUG": "true",
        "REVIEWPOINT_LOG_LEVEL": "WARNING"
    }
    
    for key, value in test_config.items():
        os.environ[key] = value
```

### Environment Mocking
```python
@contextmanager
def mock_env(**kwargs):
    """Temporarily override environment variables"""
    old_values = {}
    for key, value in kwargs.items():
        old_values[key] = os.environ.get(key)
        os.environ[key] = str(value)
    
    try:
        yield
    finally:
        for key, old_value in old_values.items():
            if old_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = old_value
```

## 11. Error Handling

### Custom Exceptions
```python
class EnvironmentError(Exception):
    """Environment configuration error"""
    pass

class MissingEnvironmentVariable(EnvironmentError):
    """Required environment variable is missing"""
    pass

class InvalidEnvironmentValue(EnvironmentError):
    """Environment variable has invalid value"""
    pass
```

### Graceful Degradation
```python
def get_env_with_fallback(
    primary_key: str,
    fallback_keys: List[str],
    default: str = None
) -> str:
    """Get environment variable with multiple fallback options"""
    for key in [primary_key] + fallback_keys:
        value = os.environ.get(key)
        if value:
            return value
    return default
```

# Environment Utilities Documentation

## Purpose

The `environment.py` module provides reliable environment detection utilities for the ReViewPoint application. This module centralizes the logic for determining the current runtime environment, particularly focusing on test mode detection across different testing frameworks and deployment scenarios. The utility ensures consistent behavior detection whether running under pytest, manual testing, or production environments.

## Architecture

The environment detection system follows a multi-source validation approach:

- **Multiple Detection Sources**: Checks various environment variables for comprehensive test mode detection
- **Framework Agnostic**: Works with pytest, manual testing, and custom test environments
- **Constant Management**: Centralized environment variable names for maintainability
- **Type Safety**: Full type annotations for reliable environment checks
- **Boolean Simplicity**: Single function interface for easy integration
- **Immutable Constants**: Final constants prevent accidental modification

## Constants

### Environment Variable Names

**Core Environment Variables:**

```python
ENVIRONMENT_VAR: Final[str] = "ENVIRONMENT"
PYTEST_CURRENT_TEST_VAR: Final[str] = "PYTEST_CURRENT_TEST"
REVIEWPOINT_TEST_MODE_VAR: Final[str] = "REVIEWPOINT_TEST_MODE"
TEST_ENV_LITERAL: Final[str] = "test"
TEST_MODE_LITERAL: Final[str] = "1"
```

**Constant Specifications:**

- **`ENVIRONMENT_VAR`**: Standard environment variable for deployment environment
- **`PYTEST_CURRENT_TEST_VAR`**: pytest-specific variable automatically set during test execution
- **`REVIEWPOINT_TEST_MODE_VAR`**: Application-specific test mode override
- **`TEST_ENV_LITERAL`**: Expected value for ENVIRONMENT variable in test mode
- **`TEST_MODE_LITERAL`**: Expected value for boolean-style test mode flags

**Usage Benefits:**

- **Maintainability**: Single source of truth for environment variable names
- **Type Safety**: Final annotation prevents runtime modification
- **Consistency**: Standardized naming across application
- **Refactoring Safety**: IDE can track usage and changes

## Core Function

### `is_test_mode() -> bool`

Determines if the application is currently running in test mode by checking multiple environment indicators.

```python
from src.utils.environment import is_test_mode

# Basic usage
if is_test_mode():
    print("Running in test mode - using test database")
    database_url = "sqlite:///:memory:"
else:
    print("Running in production mode")
    database_url = os.environ["DATABASE_URL"]

# Integration with application configuration
def get_database_config():
    if is_test_mode():
        return {
            "url": "sqlite:///:memory:",
            "echo": True,  # SQL logging for tests
            "pool_size": 1
        }
    else:
        return {
            "url": os.environ["DATABASE_URL"],
            "echo": False,
            "pool_size": 20
        }
```

**Detection Logic:**
The function returns `True` if ANY of the following conditions are met:

1. **Standard Environment**: `ENVIRONMENT == "test"`
2. **pytest Detection**: `PYTEST_CURRENT_TEST` is set (not None or empty)
3. **Manual Override**: `REVIEWPOINT_TEST_MODE == "1"`

## Detection Methods

### Standard Environment Detection

**ENVIRONMENT Variable Check:**

```python
# Environment setup examples
# Development
export ENVIRONMENT=development

# Testing
export ENVIRONMENT=test

# Production
export ENVIRONMENT=production

# Function behavior
def environment_detection_example():
    os.environ["ENVIRONMENT"] = "test"
    assert is_test_mode() == True

    os.environ["ENVIRONMENT"] = "production"
    # Will still be True if other test indicators are present
    result = is_test_mode()
```

**Production Environment Safety:**

- Production deployments should never set `ENVIRONMENT=test`
- Multiple detection methods prevent false positives
- Clear separation between deployment and testing modes

### pytest Framework Detection

**Automatic pytest Detection:**

```python
# pytest automatically sets PYTEST_CURRENT_TEST when running tests
def test_automatic_detection():
    """This test will automatically be detected as test mode."""

    # pytest sets PYTEST_CURRENT_TEST to something like:
    # "tests/test_environment.py::test_automatic_detection (setup)"

    assert is_test_mode() == True
    assert os.environ.get("PYTEST_CURRENT_TEST") is not None

# Manual pytest simulation
def simulate_pytest_environment():
    """Simulate pytest environment for testing."""

    os.environ["PYTEST_CURRENT_TEST"] = "tests/test_example.py::test_function"
    assert is_test_mode() == True

    # Cleanup
    del os.environ["PYTEST_CURRENT_TEST"]
    # is_test_mode() may still be True due to other indicators
```

**Benefits of pytest Detection:**

- **Automatic**: No manual configuration required
- **Reliable**: Set by pytest framework itself
- **Specific**: Only present during actual test execution
- **Framework Integration**: Works with all pytest plugins and configurations

### Manual Test Mode Override

**REVIEWPOINT_TEST_MODE Flag:**

```python
# Manual test mode activation
def activate_manual_test_mode():
    """Activate test mode manually for debugging or development."""

    os.environ["REVIEWPOINT_TEST_MODE"] = "1"
    assert is_test_mode() == True

    # Use case: debugging with test database
    if is_test_mode():
        database.connect("test_database")

def deactivate_manual_test_mode():
    """Deactivate manual test mode."""

    os.environ["REVIEWPOINT_TEST_MODE"] = "0"  # or del os.environ["REVIEWPOINT_TEST_MODE"]
    # Result depends on other environment indicators
```

**Manual Override Use Cases:**

- **Development Testing**: Test with production-like setup but test database
- **Debugging**: Enable test mode for specific debugging sessions
- **CI/CD Flexibility**: Override detection in complex deployment scenarios
- **Integration Testing**: Control test mode in docker containers or scripts

## Usage Patterns

### Application Configuration

**Database Configuration:**

```python
from src.utils.environment import is_test_mode
from src.core.config import settings

def get_database_url() -> str:
    """Get database URL based on environment."""

    if is_test_mode():
        # Use in-memory SQLite for tests
        return "sqlite:///:memory:"
    else:
        # Use configured database for production
        return settings.database_url

def get_cache_configuration() -> dict:
    """Configure caching based on environment."""

    if is_test_mode():
        return {
            "backend": "memory",
            "ttl_default": 1,  # Short TTL for tests
            "max_entries": 100
        }
    else:
        return {
            "backend": "redis",
            "ttl_default": 3600,
            "max_entries": 10000,
            "redis_url": settings.redis_url
        }
```

### Logging Configuration

**Environment-Specific Logging:**

```python
import logging
from src.utils.environment import is_test_mode

def configure_logging():
    """Configure logging based on environment."""

    if is_test_mode():
        # Detailed logging for tests
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler()]
        )

        # Suppress external library noise in tests
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("requests").setLevel(logging.WARNING)

    else:
        # Production logging configuration
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("app.log"),
                logging.StreamHandler()
            ]
        )

# Usage in application startup
def initialize_application():
    configure_logging()

    if is_test_mode():
        logger.info("Application started in TEST mode")
    else:
        logger.info("Application started in PRODUCTION mode")
```

### Security and Authentication

**Test Mode Security Overrides:**

```python
from src.utils.environment import is_test_mode

def get_jwt_settings() -> dict:
    """JWT configuration with test mode considerations."""

    base_settings = {
        "algorithm": "HS256",
        "access_token_expire_minutes": 30,
    }

    if is_test_mode():
        # Simplified JWT for tests
        base_settings.update({
            "secret_key": "test-secret-key",
            "access_token_expire_minutes": 60 * 24,  # 24 hours for test stability
        })
    else:
        # Production JWT settings
        base_settings.update({
            "secret_key": os.environ["JWT_SECRET_KEY"],
            "access_token_expire_minutes": 30,
        })

    return base_settings

def bypass_rate_limiting() -> bool:
    """Determine if rate limiting should be bypassed."""

    # Bypass rate limiting in test mode
    return is_test_mode()

# Usage in middleware
async def rate_limit_middleware(request, call_next):
    if not bypass_rate_limiting():
        # Apply rate limiting logic
        await apply_rate_limiting(request)

    response = await call_next(request)
    return response
```

### Feature Flags and Testing

**Test-Specific Feature Activation:**

```python
from src.utils.environment import is_test_mode

class FeatureFlags:
    """Feature flag management with test mode support."""

    def __init__(self):
        self.flags = self._load_feature_flags()

    def _load_feature_flags(self) -> dict:
        """Load feature flags with test mode overrides."""

        base_flags = {
            "enable_email_verification": True,
            "enable_file_upload": True,
            "enable_analytics": True,
            "enable_rate_limiting": True,
        }

        if is_test_mode():
            # Override flags for testing
            base_flags.update({
                "enable_email_verification": False,  # Disable external services
                "enable_analytics": False,           # No tracking in tests
                "enable_rate_limiting": False,       # No limits in tests
                "enable_debug_endpoints": True,      # Enable test endpoints
            })

        return base_flags

    def is_enabled(self, flag_name: str) -> bool:
        """Check if a feature flag is enabled."""
        return self.flags.get(flag_name, False)

# Usage throughout application
feature_flags = FeatureFlags()

def send_email(recipient: str, subject: str, body: str):
    if feature_flags.is_enabled("enable_email_verification"):
        # Send actual email
        email_service.send(recipient, subject, body)
    else:
        # Log email in test mode
        logger.info(f"Test mode: would send email to {recipient}")
```

### Database and Migration Management

**Environment-Specific Database Operations:**

```python
from src.utils.environment import is_test_mode
from alembic import command
from alembic.config import Config

async def setup_database():
    """Set up database based on environment."""

    if is_test_mode():
        # Create fresh test database
        await create_test_database()

        # Run migrations on test database
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", "sqlite:///:memory:")
        command.upgrade(alembic_cfg, "head")

        # Seed test data
        await seed_test_data()

    else:
        # Production database setup
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")

async def cleanup_database():
    """Clean up database after operations."""

    if is_test_mode():
        # Drop test database
        await drop_test_database()
    # No cleanup needed for production
```

## Testing Strategies

### Unit Testing

**Environment Detection Testing:**

```python
import pytest
import os
from unittest.mock import patch
from src.utils.environment import is_test_mode

class TestEnvironmentDetection:
    """Test suite for environment detection."""

    def setup_method(self):
        """Clean environment before each test."""
        # Store original values
        self.original_env = {}
        vars_to_clean = ["ENVIRONMENT", "PYTEST_CURRENT_TEST", "REVIEWPOINT_TEST_MODE"]

        for var in vars_to_clean:
            self.original_env[var] = os.environ.get(var)
            if var in os.environ:
                del os.environ[var]

    def teardown_method(self):
        """Restore original environment."""
        for var, value in self.original_env.items():
            if value is not None:
                os.environ[var] = value
            elif var in os.environ:
                del os.environ[var]

    def test_environment_variable_detection(self):
        """Test ENVIRONMENT variable detection."""

        # Test mode
        os.environ["ENVIRONMENT"] = "test"
        assert is_test_mode() == True

        # Non-test mode
        os.environ["ENVIRONMENT"] = "production"
        assert is_test_mode() == False

        os.environ["ENVIRONMENT"] = "development"
        assert is_test_mode() == False

    def test_pytest_detection(self):
        """Test pytest-specific detection."""

        # Simulate pytest environment
        os.environ["PYTEST_CURRENT_TEST"] = "tests/test_example.py::test_function"
        assert is_test_mode() == True

        # Empty pytest variable should still trigger test mode
        os.environ["PYTEST_CURRENT_TEST"] = ""
        assert is_test_mode() == False  # Empty string is falsy

    def test_manual_override(self):
        """Test manual test mode override."""

        # Enable manual test mode
        os.environ["REVIEWPOINT_TEST_MODE"] = "1"
        assert is_test_mode() == True

        # Disable manual test mode
        os.environ["REVIEWPOINT_TEST_MODE"] = "0"
        assert is_test_mode() == False

    def test_multiple_indicators(self):
        """Test behavior with multiple indicators."""

        # Set both environment and pytest
        os.environ["ENVIRONMENT"] = "production"  # Not test
        os.environ["PYTEST_CURRENT_TEST"] = "test_file.py::test_func"  # Is test

        # Should still return True due to pytest indicator
        assert is_test_mode() == True

        # Set conflicting indicators
        os.environ["ENVIRONMENT"] = "test"
        os.environ["REVIEWPOINT_TEST_MODE"] = "0"  # Not test

        # Should return True due to ENVIRONMENT
        assert is_test_mode() == True

    def test_no_indicators(self):
        """Test behavior with no test indicators."""

        # No environment variables set
        assert is_test_mode() == False

        # Set non-test values
        os.environ["ENVIRONMENT"] = "production"
        os.environ["REVIEWPOINT_TEST_MODE"] = "0"

        assert is_test_mode() == False

    @patch.dict(os.environ, {}, clear=True)
    def test_clean_environment(self):
        """Test behavior in completely clean environment."""

        assert is_test_mode() == False
```

### Integration Testing

**Application Behavior Testing:**

```python
import pytest
from src.utils.environment import is_test_mode
from src.core.config import get_database_url, get_cache_configuration

class TestEnvironmentIntegration:
    """Test environment detection integration with application components."""

    @pytest.mark.parametrize("env_vars,expected_test_mode", [
        ({"ENVIRONMENT": "test"}, True),
        ({"PYTEST_CURRENT_TEST": "test.py::test_func"}, True),
        ({"REVIEWPOINT_TEST_MODE": "1"}, True),
        ({"ENVIRONMENT": "production"}, False),
        ({}, False),
    ])
    def test_configuration_changes(self, env_vars, expected_test_mode, monkeypatch):
        """Test that configuration changes based on environment detection."""

        # Clear environment
        for var in ["ENVIRONMENT", "PYTEST_CURRENT_TEST", "REVIEWPOINT_TEST_MODE"]:
            monkeypatch.delenv(var, raising=False)

        # Set test environment
        for var, value in env_vars.items():
            monkeypatch.setenv(var, value)

        # Verify detection
        assert is_test_mode() == expected_test_mode

        # Verify configuration changes
        if expected_test_mode:
            assert "sqlite" in get_database_url().lower()
            assert get_cache_configuration()["backend"] == "memory"
        else:
            # Would need proper config for production test
            pass
```

## Performance Considerations

### Optimization Strategies

**Efficient Environment Checking:**

```python
# Cache result for performance in high-frequency code
from functools import lru_cache

@lru_cache(maxsize=1)
def cached_is_test_mode() -> bool:
    """Cached version of is_test_mode for performance-critical code."""
    return is_test_mode()

# Usage in hot code paths
def high_frequency_function():
    if cached_is_test_mode():
        # Test mode logic
        pass
    else:
        # Production logic
        pass

# Clear cache if environment changes during runtime
def update_environment():
    os.environ["REVIEWPOINT_TEST_MODE"] = "1"
    cached_is_test_mode.cache_clear()  # Clear cache after change
```

**Minimize Environment Variable Access:**

```python
# Store result at module level for frequently used code
_test_mode_cache: bool | None = None

def optimized_is_test_mode() -> bool:
    """Optimized version with module-level caching."""
    global _test_mode_cache

    if _test_mode_cache is None:
        _test_mode_cache = is_test_mode()

    return _test_mode_cache

def reset_test_mode_cache():
    """Reset cache when environment changes."""
    global _test_mode_cache
    _test_mode_cache = None
```

## Best Practices

### Environment Variable Management

- **Clear Naming**: Use descriptive, consistent environment variable names
- **Documentation**: Document all environment variables and their expected values
- **Validation**: Validate environment variable values where appropriate
- **Security**: Never hardcode sensitive values, use environment variables

### Test Mode Detection

- **Multiple Sources**: Check multiple indicators for robust detection
- **Fail Safe**: Default to production mode when detection is uncertain
- **Logging**: Log environment detection results for debugging
- **Immutable**: Use Final constants to prevent accidental modification

### Application Integration

- **Early Detection**: Check test mode early in application startup
- **Configuration**: Use test mode detection to drive configuration decisions
- **Feature Flags**: Integrate with feature flag systems for test-specific behavior
- **Clean Separation**: Clearly separate test and production code paths

## Related Files

### Dependencies

- `os` - Operating system environment variable access
- `typing.Final` - Immutable constant annotations

### Integration Points

- `src.core.config` - Application configuration based on environment
- `src.core.database` - Database selection and configuration
- `src.core.logging` - Environment-specific logging configuration
- `src.middleware` - Request processing behavior based on environment

### Testing Integration

- `tests/conftest.py` - Pytest configuration and test environment setup
- `pytest.ini` - pytest configuration file
- Test fixtures that need environment-aware behavior

## Configuration

### Environment Variables

```python
# Required environment variables
REQUIRED_ENV_VARS = {
    "ENVIRONMENT": "deployment environment (development/test/production)",
    "PYTEST_CURRENT_TEST": "automatically set by pytest during test execution",
    "REVIEWPOINT_TEST_MODE": "manual test mode override (0/1)",
}

# Default values
DEFAULT_VALUES = {
    "ENVIRONMENT": "production",  # Safe default
    "REVIEWPOINT_TEST_MODE": "0",  # Disabled by default
}
```

### Deployment Configuration

```bash
# Development environment
export ENVIRONMENT=development
export REVIEWPOINT_TEST_MODE=0

# Test environment
export ENVIRONMENT=test
export REVIEWPOINT_TEST_MODE=1

# Production environment
export ENVIRONMENT=production
# REVIEWPOINT_TEST_MODE should not be set in production
```

This environment utility provides reliable, multi-source environment detection that ensures the ReViewPoint application behaves correctly across development, testing, and production environments.

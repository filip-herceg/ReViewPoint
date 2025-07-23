# feature_flags.py - Environment-Based Feature Flag Management

## Purpose

Provides a comprehensive feature flag system for enabling/disabling features through environment variables and configuration files. This module implements flexible feature toggling with support for granular feature control, environment file loading, and runtime feature state management without requiring application restarts.

## Key Components

### Core Feature Flag System

#### **FeatureFlags Class**

- **Purpose**: Static utility class for feature flag evaluation and management
- **Design**: Environment variable-based feature detection with multiple naming conventions
- **Features**: Hierarchical feature checking, explicit enable/disable control, flexible naming support
- **Integration**: Seamless integration with application configuration and environment management

#### **is_enabled() Method**

- **Purpose**: Primary feature flag evaluation with comprehensive naming support
- **Design**: Multi-level feature checking with explicit override capabilities
- **Logic**: Feature list, specific variables, base variables with precedence handling
- **Flexibility**: Supports both simple flags and hierarchical feature names

### Environment Management

#### **\_ensure_env_loaded() Function**

- **Purpose**: Lazy loading of environment variables from .env files into os.environ
- **Design**: Module-level state tracking to prevent redundant file operations
- **Features**: Multiple .env file location support, safe parsing, quote handling
- **Performance**: Single-load optimization with global state management

#### **Environment Variable Loading**

- **Purpose**: Bridge between Pydantic configuration and os.environ for feature flags
- **Design**: Manual .env file parsing with comprehensive error handling
- **Locations**: Multiple supported .env file locations for flexibility
- **Safety**: Non-destructive loading that preserves existing environment variables

## Dependencies

### External Libraries

- **os**: Environment variable access and manipulation
- **pathlib**: Modern file path handling for .env file detection
- **typing**: Type hints and constants for type safety

### Internal Dependencies

- **No internal dependencies**: Standalone module to prevent circular imports
- **Configuration integration**: Works with configuration system without direct dependencies

### Environment Integration

- **Pydantic compatibility**: Bridges gap between Pydantic .env loading and os.environ
- **Configuration system**: Integrates with core configuration without tight coupling

## Feature Flag Patterns

### Basic Feature Flags

```python
from core.feature_flags import FeatureFlags

# Simple feature check
if FeatureFlags.is_enabled("new_ui"):
    # Use new UI implementation
    render_new_ui()
else:
    # Use legacy UI
    render_legacy_ui()
```

### Hierarchical Feature Flags

```python
# Hierarchical feature naming
if FeatureFlags.is_enabled("api:v2"):
    # Use API v2 endpoints
    use_api_v2()

if FeatureFlags.is_enabled("analytics:detailed"):
    # Enable detailed analytics
    enable_detailed_analytics()
```

### Environment Variable Conventions

```bash
# Multiple ways to enable features:

# 1. Feature list (REVIEWPOINT_FEATURES)
REVIEWPOINT_FEATURES="new_ui,api:v2,analytics:detailed"

# 2. Specific feature variables
REVIEWPOINT_FEATURE_NEW_UI=true
REVIEWPOINT_FEATURE_API_V2=true
REVIEWPOINT_FEATURE_ANALYTICS_DETAILED=true

# 3. Base feature variables (for hierarchical features)
REVIEWPOINT_FEATURE_API=true       # Enables all api:* features
REVIEWPOINT_FEATURE_ANALYTICS=true # Enables all analytics:* features
```

## Configuration Integration

### Environment File Discovery

```python
def _ensure_env_loaded() -> None:
    """Environment file discovery with fallback locations"""
    env_path = os.getenv("ENV_FILE")  # Explicit path override

    # Standard locations in order of preference:
    locations = [
        "config/.env",           # Primary config location
        "backend/config/.env",   # Backend-specific config
        "backend/.env"           # Fallback backend location
    ]

    # Load first available .env file
    env_file = find_first_existing_file(locations)
    if env_file:
        load_env_variables(env_file)
```

### Environment Variable Parsing

```python
def parse_env_file(env_file: Path) -> dict[str, str]:
    """Safe .env file parsing with quote handling"""
    env_vars = {}

    with env_file.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue

            # Parse key=value assignments
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()

                # Remove surrounding quotes
                value = value.strip('"\'')

                # Only set if not already in environment
                if key not in os.environ:
                    env_vars[key] = value

    return env_vars
```

## Feature Flag Evaluation Logic

### Precedence Rules

1. **Explicit Disable**: If any specific or base variable is set to "false", feature is disabled
2. **Explicit Enable**: If any specific or base variable is set to "true", feature is enabled
3. **Feature List**: If feature name appears in REVIEWPOINT_FEATURES list, feature is enabled
4. **Default**: If no explicit configuration, feature is disabled

### Evaluation Implementation

```python
def is_enabled(feature_name: str) -> bool:
    """Feature flag evaluation with precedence rules"""
    _ensure_env_loaded()

    # Parse feature list
    features_env = os.getenv("REVIEWPOINT_FEATURES", "")
    enabled_features = {
        f.strip() for f in features_env.split(",") if f.strip()
    }

    # Extract base feature name (before colon)
    base_name = feature_name.split(":")[0].upper()

    # Build environment variable names
    specific_var = f"REVIEWPOINT_FEATURE_{feature_name.upper().replace(':', '_')}"
    base_var = f"REVIEWPOINT_FEATURE_{base_name}"

    # Get environment values
    specific_value = os.getenv(specific_var)
    base_value = os.getenv(base_var)

    # Check for explicit disable (highest precedence)
    if (specific_value and specific_value.lower() == "false") or \
       (base_value and base_value.lower() == "false"):
        return False

    # Check for explicit enable or feature list inclusion
    return (
        feature_name in enabled_features or
        (specific_value and specific_value.lower() == "true") or
        (base_value and base_value.lower() == "true")
    )
```

## Performance Considerations

### Lazy Loading Optimization

```python
# Module-level state to prevent redundant file operations
_env_loaded: bool = False

def _ensure_env_loaded() -> None:
    """Optimized environment loading with state tracking"""
    global _env_loaded

    # Early return if already loaded
    if _env_loaded:
        return

    # Perform expensive file operations only once
    load_environment_files()
    _env_loaded = True
```

### Environment Variable Caching

- **OS environment**: Environment variables are cached by the operating system
- **Single load**: .env files are loaded once per application lifecycle
- **No redundant I/O**: Module-level flag prevents repeated file operations

### Feature Flag Evaluation

```python
# Efficient feature flag checking
def is_enabled(feature_name: str) -> bool:
    """Optimized feature flag evaluation"""
    # Ensure environment is loaded (cached after first call)
    _ensure_env_loaded()

    # Use efficient string operations and set membership
    features_set = parse_feature_list()  # Parsed once per call

    # Fast dictionary lookups for environment variables
    specific_check = os.getenv(build_specific_var_name(feature_name))
    base_check = os.getenv(build_base_var_name(feature_name))

    # Short-circuit evaluation for performance
    return evaluate_with_precedence(feature_name, features_set, specific_check, base_check)
```

## Error Handling Strategy

### File Operation Safety

```python
def _ensure_env_loaded() -> None:
    """Safe environment loading with comprehensive error handling"""
    try:
        # File discovery and parsing
        env_file = discover_env_file()
        if env_file:
            parse_env_file(env_file)
    except (OSError, ValueError, IndexError):
        # Graceful degradation: continue without .env file
        # In production: log error for debugging
        pass
    finally:
        # Always mark as loaded to prevent retry loops
        _env_loaded = True
```

### Feature Flag Evaluation Safety

```python
def is_enabled(feature_name: str) -> bool:
    """Safe feature flag evaluation with error handling"""
    try:
        _ensure_env_loaded()
        return evaluate_feature_flag(feature_name)
    except (OSError, ValueError) as e:
        # Log error and return safe default
        logger.warning(f"Feature flag evaluation failed for {feature_name}: {e}")
        return False  # Safe default: feature disabled
```

### Environment Variable Safety

```python
def safe_getenv(var_name: str, default: str = "") -> str:
    """Safe environment variable access"""
    try:
        return os.getenv(var_name, default)
    except (OSError, KeyError):
        return default
```

## Security Considerations

### Environment Variable Safety

- **No sensitive data**: Feature flags contain only boolean configuration
- **Environment isolation**: Proper environment separation prevents flag leakage
- **Access control**: Feature flags respect environment access controls

### Configuration File Security

```python
def secure_env_file_loading():
    """Security considerations for .env file loading"""
    # 1. File permissions: .env files should have restricted permissions
    # 2. Path validation: Prevent directory traversal attacks
    # 3. Content validation: Validate environment variable names and values
    # 4. Sanitization: Remove potentially harmful characters
```

### Feature Flag Naming

```python
# Secure feature flag naming conventions
VALID_FEATURE_NAME_PATTERN = r'^[a-zA-Z][a-zA-Z0-9_:]*$'

def validate_feature_name(feature_name: str) -> bool:
    """Validate feature flag names for security"""
    return bool(re.match(VALID_FEATURE_NAME_PATTERN, feature_name))
```

## Usage Examples

### Basic Feature Toggling

```python
from core.feature_flags import FeatureFlags

class UserService:
    def get_user_profile(self, user_id: str):
        """User profile with feature flag support"""
        if FeatureFlags.is_enabled("enhanced_profiles"):
            return self.get_enhanced_profile(user_id)
        else:
            return self.get_basic_profile(user_id)
```

### API Versioning

```python
@app.route("/api/data")
def get_data():
    """API endpoint with version feature flags"""
    if FeatureFlags.is_enabled("api:v3"):
        return handle_api_v3_request()
    elif FeatureFlags.is_enabled("api:v2"):
        return handle_api_v2_request()
    else:
        return handle_api_v1_request()
```

### Gradual Feature Rollout

```python
class AnalyticsService:
    def track_event(self, event_data):
        """Analytics with gradual feature rollout"""
        # Base analytics (always enabled)
        self.basic_tracking(event_data)

        # Enhanced analytics (feature flagged)
        if FeatureFlags.is_enabled("analytics:enhanced"):
            self.enhanced_tracking(event_data)

        # Real-time analytics (feature flagged)
        if FeatureFlags.is_enabled("analytics:realtime"):
            self.realtime_tracking(event_data)
```

### Environment-Specific Features

```python
# Development environment (.env)
REVIEWPOINT_FEATURES="debug_mode,dev_tools,mock_services"

# Staging environment (.env)
REVIEWPOINT_FEATURES="new_ui,api:v2"

# Production environment (.env)
REVIEWPOINT_FEATURES="api:v2,analytics:basic"
```

## Configuration Examples

### Environment File Configuration

```bash
# config/.env - Feature flag configuration

# Feature list (comma-separated)
REVIEWPOINT_FEATURES="new_ui,api:v2,analytics:detailed"

# Specific feature variables
REVIEWPOINT_FEATURE_DEBUG_MODE=true
REVIEWPOINT_FEATURE_NEW_UI=true
REVIEWPOINT_FEATURE_API_V2=true

# Base feature variables (hierarchical)
REVIEWPOINT_FEATURE_ANALYTICS=true  # Enables all analytics:* features
REVIEWPOINT_FEATURE_API=false       # Disables all api:* features (override)

# Explicit disable (highest precedence)
REVIEWPOINT_FEATURE_EXPERIMENTAL=false
```

### Application Integration

```python
# In FastAPI application
from core.feature_flags import FeatureFlags

@app.middleware("http")
async def feature_flag_middleware(request: Request, call_next):
    """Middleware for feature flag context"""
    # Add feature flag helper to request context
    request.state.features = FeatureFlags
    response = await call_next(request)
    return response

@app.get("/features")
async def get_enabled_features():
    """API endpoint to list enabled features"""
    features = [
        "new_ui", "api:v2", "analytics:detailed",
        "debug_mode", "experimental"
    ]

    enabled = {
        feature: FeatureFlags.is_enabled(feature)
        for feature in features
    }

    return {"enabled_features": enabled}
```

## Testing Integration

### Feature Flag Testing

```python
import pytest
import os
from core.feature_flags import FeatureFlags

def test_feature_flag_enabled():
    """Test feature flag evaluation"""
    # Set environment variable for test
    os.environ["REVIEWPOINT_FEATURE_TEST_FEATURE"] = "true"

    assert FeatureFlags.is_enabled("test_feature") is True

    # Cleanup
    del os.environ["REVIEWPOINT_FEATURE_TEST_FEATURE"]

def test_feature_flag_disabled():
    """Test feature flag disabled by default"""
    assert FeatureFlags.is_enabled("nonexistent_feature") is False

def test_hierarchical_feature_flags():
    """Test hierarchical feature flag support"""
    os.environ["REVIEWPOINT_FEATURE_API"] = "true"

    # Base feature enables hierarchical features
    assert FeatureFlags.is_enabled("api:v1") is True
    assert FeatureFlags.is_enabled("api:v2") is True

    # Specific override
    os.environ["REVIEWPOINT_FEATURE_API_V2"] = "false"
    assert FeatureFlags.is_enabled("api:v2") is False

    # Cleanup
    del os.environ["REVIEWPOINT_FEATURE_API"]
    del os.environ["REVIEWPOINT_FEATURE_API_V2"]
```

### Mock Feature Flags

```python
@pytest.fixture
def mock_feature_flags():
    """Fixture for mocking feature flags in tests"""
    original_env = os.environ.copy()

    # Set test feature flags
    os.environ.update({
        "REVIEWPOINT_FEATURES": "test_feature1,test_feature2",
        "REVIEWPOINT_FEATURE_DEBUG": "true"
    })

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)
```

## Related Files

- **[config.py](config.py.md)**: Configuration settings and environment management
- **[app_logging.py](app_logging.py.md)**: Logging configuration for feature flag evaluation
- **[main.py](../main.py.md)**: Application startup and feature flag initialization
- **[../middlewares/logging.py](../middlewares/logging.py.md)**: HTTP middleware with potential feature flag integration

## Future Enhancements

### Planned Features

- **Dynamic feature flags**: Runtime feature flag updates without restart
- **User-specific flags**: Per-user or per-group feature flag overrides
- **Time-based flags**: Feature flags with automatic expiration
- **A/B testing**: Built-in A/B testing framework with feature flags

### Integration Extensions

```python
# Future: Dynamic feature flag updates
class DynamicFeatureFlags:
    def __init__(self):
        self.cache = {}
        self.last_update = None

    async def refresh_from_remote(self):
        """Refresh feature flags from remote configuration"""
        # Implementation for remote feature flag management
        pass

    def is_enabled(self, feature_name: str, user_id: str = None) -> bool:
        """Enhanced feature flag evaluation with user context"""
        # Implementation for user-specific feature flags
        pass
```

The feature_flags.py module provides a robust, flexible foundation for feature flag management in the ReViewPoint backend, enabling safe feature rollouts, A/B testing, and environment-specific configuration without requiring application restarts.

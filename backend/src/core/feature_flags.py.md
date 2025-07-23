# Feature Flags Module

**File:** `backend/src/core/feature_flags.py`  
**Purpose:** Environment variable-based feature flag system for ReViewPoint backend  
**Lines of Code:** 157  
**Type:** Core Infrastructure Module  

## Overview

The feature flags module provides a flexible, environment variable-based feature flagging system for the ReViewPoint backend. It enables conditional feature activation through multiple configuration methods, supports hierarchical feature naming, and integrates seamlessly with the application's configuration system. The module allows for runtime feature control without code deployment, making it ideal for gradual rollouts, A/B testing, and environment-specific feature management.

## Architecture

### Core Design Principles

1. **Environment Variable Foundation**: Uses environment variables for configuration
2. **Multiple Configuration Methods**: Supports individual flags and grouped features
3. **Hierarchical Naming**: Feature names can use colon-separated hierarchies
4. **Explicit Override**: False values always take precedence over true values
5. **Lazy Loading**: Environment files loaded only when needed
6. **No External Dependencies**: Pure Python implementation for reliability

### Key Components

#### Constants and Configuration
```python
# Environment variable constants
ENV_FILE_VAR: Final[str] = "ENV_FILE"
REVIEWPOINT_FEATURES_VAR: Final[str] = "REVIEWPOINT_FEATURES" 
FEATURE_PREFIX: Final[str] = "REVIEWPOINT_FEATURE_"

# Boolean string constants
TRUE_VALUE: Final[str] = "true"
FALSE_VALUE: Final[str] = "false"
```

**Configuration Variables:**
- `ENV_FILE_VAR`: Specifies custom .env file location
- `REVIEWPOINT_FEATURES_VAR`: Comma-separated list of enabled features
- `FEATURE_PREFIX`: Prefix for individual feature environment variables

#### File Path Discovery
```python
# File path constants for .env file discovery
CONFIG_ENV_PATH: Final[str] = "config/.env"
BACKEND_CONFIG_ENV_PATH: Final[str] = "backend/config/.env"
BACKEND_ENV_PATH: Final[str] = "backend/.env"
```

Automatic discovery of .env files in common locations for flexible deployment scenarios.

## Core Classes and Functions

### 🚩 **FeatureFlags Class**

#### `is_enabled()` Method
```python
@staticmethod
def is_enabled(feature_name: str) -> bool:
    """Check if a feature is enabled via environment variables."""
```

**Purpose:** Primary interface for checking feature flag status

**Feature Resolution Logic:**
1. **Environment Loading**: Ensures .env files are loaded into os.environ
2. **Grouped Features**: Checks `REVIEWPOINT_FEATURES` for feature name
3. **Specific Variables**: Checks `REVIEWPOINT_FEATURE_<FEATURE_NAME>`
4. **Base Variables**: Checks `REVIEWPOINT_FEATURE_<BASE_NAME>` for hierarchical features
5. **Priority Resolution**: False values override true values

**Hierarchical Feature Support:**
```python
# Feature name: "api:v2:endpoints"
# Creates environment variables:
# - REVIEWPOINT_FEATURE_API_V2_ENDPOINTS (specific)
# - REVIEWPOINT_FEATURE_API (base)

# Both are checked, allowing for base-level and specific-level control
```

**Resolution Priority (Highest to Lowest):**
1. Explicit false in specific variable (`REVIEWPOINT_FEATURE_API_V2_ENDPOINTS=false`)
2. Explicit false in base variable (`REVIEWPOINT_FEATURE_API=false`)
3. Explicit true in specific variable (`REVIEWPOINT_FEATURE_API_V2_ENDPOINTS=true`)
4. Explicit true in base variable (`REVIEWPOINT_FEATURE_API=true`)
5. Feature name in grouped features list (`REVIEWPOINT_FEATURES=api:v2:endpoints,other_feature`)

## Configuration Methods

### 📝 **Method 1: Individual Environment Variables**

```bash
# Enable specific features
REVIEWPOINT_FEATURE_NEW_API=true
REVIEWPOINT_FEATURE_ADVANCED_SEARCH=true
REVIEWPOINT_FEATURE_BETA_UI=false

# Hierarchical features
REVIEWPOINT_FEATURE_API_V2_ENDPOINTS=true
REVIEWPOINT_FEATURE_EMBEDDINGS_PROCESSING=true
```

**Usage in Code:**
```python
from src.core.feature_flags import FeatureFlags

# Check individual features
if FeatureFlags.is_enabled("new_api"):
    # Use new API implementation
    return new_api_handler(request)

if FeatureFlags.is_enabled("api:v2:endpoints"):
    # Enable v2 API endpoints
    app.include_router(v2_router)
```

### 📝 **Method 2: Grouped Features List**

```bash
# Enable multiple features in a single variable
REVIEWPOINT_FEATURES="new_api,advanced_search,api:v2:endpoints,embeddings:processing"
```

**Usage Benefits:**
- Simpler configuration for multiple features
- Easy to read and manage feature sets
- Ideal for environment-specific feature bundles

### 📝 **Method 3: Mixed Configuration**

```bash
# Combination approach for fine-grained control
REVIEWPOINT_FEATURES="new_api,advanced_search"
REVIEWPOINT_FEATURE_BETA_UI=false          # Explicitly disabled
REVIEWPOINT_FEATURE_DEBUG_MODE=true        # Explicitly enabled
```

## Environment File Integration

### 🔧 **Automatic Environment Loading**

#### `_ensure_env_loaded()` Function
```python
def _ensure_env_loaded() -> None:
    """Ensure environment variables from .env file are loaded."""
```

**Purpose:** Loads .env files into os.environ for feature flag access

**Loading Process:**
1. **Single Loading**: Uses module-level flag to prevent repeated loading
2. **File Discovery**: Searches multiple locations for .env files
3. **Parse and Load**: Reads key-value pairs and sets environment variables
4. **Precedence Respect**: Only sets variables not already in environment
5. **Error Tolerance**: Continues gracefully if loading fails

**File Discovery Order:**
```python
# 1. Custom path from ENV_FILE environment variable
env_path = os.getenv("ENV_FILE")

# 2. Standard locations (first found wins)
locations = [
    "config/.env",
    "backend/config/.env", 
    "backend/.env"
]
```

### 📁 **.env File Format**

```bash
# Comments are supported
# Feature flags configuration

# Individual feature flags
REVIEWPOINT_FEATURE_NEW_API=true
REVIEWPOINT_FEATURE_BETA_UI=false

# Grouped features
REVIEWPOINT_FEATURES="advanced_search,api:v2,embeddings"

# Quoted values are supported
REVIEWPOINT_FEATURE_DEBUG="true"
REVIEWPOINT_FEATURE_EXPERIMENTAL='false'

# Other configuration
REVIEWPOINT_DB_URL=postgresql://localhost/db
```

**Parsing Features:**
- Comment support (lines starting with #)
- Key-value assignment with = separator
- Quote removal (both single and double quotes)
- Whitespace trimming
- Environment variable precedence (existing vars not overwritten)

## Usage Patterns

### 🔀 **Conditional Feature Implementation**

```python
from src.core.feature_flags import FeatureFlags

class APIRouter:
    def __init__(self):
        # Conditionally include endpoints based on feature flags
        if FeatureFlags.is_enabled("api:v2"):
            self.include_v2_endpoints()
            
        if FeatureFlags.is_enabled("api:experimental"):
            self.include_experimental_endpoints()
    
    def get_user_data(self, user_id: int):
        # Use different implementations based on feature flags
        if FeatureFlags.is_enabled("optimized_queries"):
            return self.get_user_data_optimized(user_id)
        else:
            return self.get_user_data_standard(user_id)
```

### 🧪 **A/B Testing Implementation**

```python
from src.core.feature_flags import FeatureFlags

class RecommendationService:
    def get_recommendations(self, user_id: int):
        # A/B test different recommendation algorithms
        if FeatureFlags.is_enabled("recommendations:ml_enhanced"):
            return self.get_ml_recommendations(user_id)
        elif FeatureFlags.is_enabled("recommendations:collaborative"):
            return self.get_collaborative_recommendations(user_id)
        else:
            return self.get_basic_recommendations(user_id)
```

### 🔄 **Gradual Feature Rollout**

```python
from src.core.feature_flags import FeatureFlags

class EmailService:
    def send_notification(self, user: User, message: str):
        # Gradual rollout of new email template system
        if FeatureFlags.is_enabled("email:new_templates"):
            # New template system
            return self.send_with_new_templates(user, message)
        else:
            # Legacy template system
            return self.send_with_legacy_templates(user, message)
```

### 🏗️ **Environment-Specific Features**

```python
from src.core.feature_flags import FeatureFlags

class DebugService:
    def __init__(self):
        # Development-only features
        self.debug_mode = FeatureFlags.is_enabled("debug:detailed_logging")
        self.profiling = FeatureFlags.is_enabled("debug:profiling")
        self.mock_external_apis = FeatureFlags.is_enabled("debug:mock_apis")
    
    def log_request(self, request):
        if self.debug_mode:
            # Detailed request logging
            logger.debug("Full request: {}", request.dict())
        else:
            # Basic request logging
            logger.info("Request: {} {}", request.method, request.path)
```

### 🎛️ **Configuration-Based Routing**

```python
from fastapi import FastAPI
from src.core.feature_flags import FeatureFlags

def create_app() -> FastAPI:
    app = FastAPI()
    
    # Conditionally include routers based on feature flags
    if FeatureFlags.is_enabled("api:auth"):
        from src.api.auth import auth_router
        app.include_router(auth_router, prefix="/auth")
    
    if FeatureFlags.is_enabled("api:admin"):
        from src.api.admin import admin_router
        app.include_router(admin_router, prefix="/admin")
    
    if FeatureFlags.is_enabled("api:uploads"):
        from src.api.uploads import upload_router
        app.include_router(upload_router, prefix="/uploads")
    
    return app
```

## Environment-Specific Configuration

### 🔧 **Development Environment**

```bash
# .env for development
REVIEWPOINT_FEATURES="debug:detailed_logging,debug:profiling,api:experimental"
REVIEWPOINT_FEATURE_MOCK_EXTERNAL_APIS=true
REVIEWPOINT_FEATURE_AUTO_RELOAD=true
REVIEWPOINT_FEATURE_DEBUG_TOOLBAR=true
```

```python
# Development-specific feature usage
if FeatureFlags.is_enabled("debug:detailed_logging"):
    init_logging(level="DEBUG", logfile="logs/debug.log")

if FeatureFlags.is_enabled("mock_external_apis"):
    # Use mock implementations for external services
    email_service = MockEmailService()
    payment_service = MockPaymentService()
```

### 🏭 **Production Environment**

```bash
# .env for production
REVIEWPOINT_FEATURES="optimized_queries,caching:redis"
REVIEWPOINT_FEATURE_DEBUG_MODE=false
REVIEWPOINT_FEATURE_EXPERIMENTAL_FEATURES=false
REVIEWPOINT_FEATURE_MONITORING=true
```

```python
# Production-specific feature usage
if FeatureFlags.is_enabled("optimized_queries"):
    # Use optimized database queries
    db_config.use_read_replicas = True
    db_config.enable_query_cache = True

if FeatureFlags.is_enabled("monitoring"):
    # Enable comprehensive monitoring
    setup_sentry_monitoring()
    setup_performance_tracking()
```

### 🧪 **Testing Environment**

```bash
# .env for testing
REVIEWPOINT_FEATURES="fast_tests"
REVIEWPOINT_FEATURE_EXTERNAL_APIS=false
REVIEWPOINT_FEATURE_DATABASE_TRANSACTIONS=false
REVIEWPOINT_FEATURE_EMAIL_SENDING=false
```

```python
# Test-specific feature usage
if FeatureFlags.is_enabled("fast_tests"):
    # Skip slow integration tests
    pytest.mark.skipif(not FeatureFlags.is_enabled("slow_tests"))

if not FeatureFlags.is_enabled("external_apis"):
    # Use mocks for external services during testing
    monkeypatch.setattr("src.services.email", MockEmailService)
```

## Advanced Usage Patterns

### 🏗️ **Feature-Based Service Factory**

```python
from src.core.feature_flags import FeatureFlags

class ServiceFactory:
    @staticmethod
    def create_search_service():
        """Create search service based on enabled features."""
        if FeatureFlags.is_enabled("search:elasticsearch"):
            from src.services.search.elasticsearch import ElasticsearchService
            return ElasticsearchService()
        elif FeatureFlags.is_enabled("search:algolia"):
            from src.services.search.algolia import AlgoliaService
            return AlgoliaService()
        else:
            from src.services.search.basic import BasicSearchService
            return BasicSearchService()
    
    @staticmethod
    def create_cache_service():
        """Create cache service based on enabled features."""
        if FeatureFlags.is_enabled("cache:redis"):
            from src.services.cache.redis import RedisCache
            return RedisCache()
        elif FeatureFlags.is_enabled("cache:memcached"):
            from src.services.cache.memcached import MemcachedCache
            return MemcachedCache()
        else:
            from src.services.cache.memory import InMemoryCache
            return InMemoryCache()
```

### 🔀 **Conditional Middleware**

```python
from fastapi import FastAPI, Request
from src.core.feature_flags import FeatureFlags

def create_app() -> FastAPI:
    app = FastAPI()
    
    # Conditionally add middleware based on feature flags
    if FeatureFlags.is_enabled("middleware:cors"):
        from fastapi.middleware.cors import CORSMiddleware
        app.add_middleware(CORSMiddleware, allow_origins=["*"])
    
    if FeatureFlags.is_enabled("middleware:compression"):
        from fastapi.middleware.gzip import GZipMiddleware
        app.add_middleware(GZipMiddleware)
    
    if FeatureFlags.is_enabled("middleware:rate_limiting"):
        from src.middleware.rate_limit import RateLimitMiddleware
        app.add_middleware(RateLimitMiddleware)
    
    return app
```

### 📊 **Feature Flag Monitoring**

```python
from src.core.feature_flags import FeatureFlags
from loguru import logger

class FeatureFlagMonitor:
    """Monitor and log feature flag usage."""
    
    @staticmethod
    def log_feature_usage(feature_name: str, context: dict = None):
        """Log when a feature is checked."""
        is_enabled = FeatureFlags.is_enabled(feature_name)
        
        logger.info(
            "Feature flag checked: {} = {}",
            feature_name,
            is_enabled,
            extra={
                "feature_name": feature_name,
                "feature_enabled": is_enabled,
                "context": context or {}
            }
        )
        
        return is_enabled
    
    @staticmethod
    def audit_enabled_features() -> dict[str, bool]:
        """Audit all known features and their status."""
        known_features = [
            "api:v2",
            "api:experimental", 
            "debug:detailed_logging",
            "optimized_queries",
            "new_ui",
            "advanced_search"
        ]
        
        status = {}
        for feature in known_features:
            status[feature] = FeatureFlags.is_enabled(feature)
        
        logger.info("Feature flag audit: {}", status)
        return status
```

## Testing Strategies

### 🧪 **Unit Testing with Feature Flags**

```python
import pytest
import os
from src.core.feature_flags import FeatureFlags

class TestFeatureFlags:
    def test_individual_feature_flag(self, monkeypatch):
        """Test individual feature flag functionality."""
        monkeypatch.setenv("REVIEWPOINT_FEATURE_NEW_API", "true")
        assert FeatureFlags.is_enabled("new_api") is True
        
        monkeypatch.setenv("REVIEWPOINT_FEATURE_NEW_API", "false")
        assert FeatureFlags.is_enabled("new_api") is False
    
    def test_grouped_features(self, monkeypatch):
        """Test grouped features functionality."""
        monkeypatch.setenv("REVIEWPOINT_FEATURES", "feature1,feature2,feature3")
        
        assert FeatureFlags.is_enabled("feature1") is True
        assert FeatureFlags.is_enabled("feature2") is True
        assert FeatureFlags.is_enabled("feature4") is False
    
    def test_hierarchical_features(self, monkeypatch):
        """Test hierarchical feature naming."""
        monkeypatch.setenv("REVIEWPOINT_FEATURE_API", "true")
        
        # Base feature enables sub-features
        assert FeatureFlags.is_enabled("api:v2:endpoints") is True
        assert FeatureFlags.is_enabled("api:experimental") is True
        
        # Specific override
        monkeypatch.setenv("REVIEWPOINT_FEATURE_API_V2_ENDPOINTS", "false")
        assert FeatureFlags.is_enabled("api:v2:endpoints") is False
    
    def test_priority_resolution(self, monkeypatch):
        """Test that false values override true values."""
        monkeypatch.setenv("REVIEWPOINT_FEATURES", "feature1")
        monkeypatch.setenv("REVIEWPOINT_FEATURE_FEATURE1", "false")
        
        # Explicit false overrides grouped true
        assert FeatureFlags.is_enabled("feature1") is False

@pytest.fixture
def clean_environment():
    """Clean environment for feature flag tests."""
    old_environ = os.environ.copy()
    
    # Remove all REVIEWPOINT_FEATURE* variables
    for key in list(os.environ.keys()):
        if key.startswith("REVIEWPOINT_FEATURE"):
            del os.environ[key]
    
    if "REVIEWPOINT_FEATURES" in os.environ:
        del os.environ["REVIEWPOINT_FEATURES"]
    
    yield
    
    # Restore environment
    os.environ.clear()
    os.environ.update(old_environ)
```

### 🏗️ **Integration Testing with Features**

```python
import pytest
from fastapi.testclient import TestClient
from src.main import create_app

@pytest.fixture
def app_with_features(monkeypatch):
    """Create app with specific features enabled."""
    monkeypatch.setenv("REVIEWPOINT_FEATURES", "api:v2,advanced_search")
    app = create_app()
    return TestClient(app)

def test_api_v2_endpoints(app_with_features):
    """Test that v2 endpoints are available when feature is enabled."""
    response = app_with_features.get("/api/v2/users")
    assert response.status_code != 404  # Endpoint should exist

@pytest.fixture
def app_without_features(monkeypatch):
    """Create app with features disabled."""
    monkeypatch.setenv("REVIEWPOINT_FEATURE_API_V2", "false")
    app = create_app()
    return TestClient(app)

def test_api_v2_disabled(app_without_features):
    """Test that v2 endpoints are not available when feature is disabled."""
    response = app_without_features.get("/api/v2/users")
    assert response.status_code == 404  # Endpoint should not exist
```

## Performance Considerations

### ⚡ **Caching Flag Checks**

```python
from functools import lru_cache
from src.core.feature_flags import FeatureFlags

class CachedFeatureFlags:
    """Cached feature flag checks for performance."""
    
    @staticmethod
    @lru_cache(maxsize=128)
    def is_enabled(feature_name: str) -> bool:
        """Cached feature flag check."""
        return FeatureFlags.is_enabled(feature_name)
    
    @staticmethod
    def clear_cache():
        """Clear the feature flag cache."""
        CachedFeatureFlags.is_enabled.cache_clear()

# Usage in performance-critical code
if CachedFeatureFlags.is_enabled("optimized_queries"):
    # Use cached result for repeated checks
    pass
```

### 🔄 **Lazy Feature Evaluation**

```python
from src.core.feature_flags import FeatureFlags

class LazyFeatureService:
    """Service with lazy feature evaluation."""
    
    def __init__(self):
        # Don't check flags during initialization
        self._advanced_search = None
        self._new_ui = None
    
    @property
    def advanced_search_enabled(self) -> bool:
        """Lazy evaluation of advanced search feature."""
        if self._advanced_search is None:
            self._advanced_search = FeatureFlags.is_enabled("advanced_search")
        return self._advanced_search
    
    @property
    def new_ui_enabled(self) -> bool:
        """Lazy evaluation of new UI feature."""
        if self._new_ui is None:
            self._new_ui = FeatureFlags.is_enabled("new_ui")
        return self._new_ui
```

## Best Practices

### ✅ **Do's**

- **Use Descriptive Names**: Choose clear, hierarchical feature names
- **Document Features**: Maintain a list of all available features and their purposes
- **Test Both States**: Always test code with features enabled and disabled
- **Use Hierarchical Naming**: Leverage colon-separated naming for related features
- **Environment-Specific Flags**: Use different flag sets for dev/test/prod
- **Monitor Usage**: Log feature flag checks for analytics and debugging
- **Clean Up**: Remove unused feature flags and their code regularly

### ❌ **Don'ts**

- **Don't Hardcode**: Avoid hardcoding feature names; use constants
- **Don't Over-Flag**: Not every code path needs a feature flag
- **Don't Leave Dead Code**: Remove disabled feature code after rollout
- **Don't Ignore Performance**: Cache feature checks in performance-critical paths
- **Don't Forget Documentation**: Always document what each feature flag controls
- **Don't Mix Concerns**: Keep feature flags focused on single features
- **Don't Assume Defaults**: Always check feature flags explicitly

## Error Handling

### 🛠️ **Graceful Degradation**

```python
from src.core.feature_flags import FeatureFlags

def get_recommendations(user_id: int):
    """Get recommendations with graceful feature degradation."""
    try:
        if FeatureFlags.is_enabled("recommendations:ml"):
            return get_ml_recommendations(user_id)
    except Exception as e:
        logger.warning("ML recommendations failed: {}", e)
    
    try:
        if FeatureFlags.is_enabled("recommendations:collaborative"):
            return get_collaborative_recommendations(user_id)
    except Exception as e:
        logger.warning("Collaborative recommendations failed: {}", e)
    
    # Fallback to basic recommendations
    return get_basic_recommendations(user_id)
```

### 🔧 **Configuration Validation**

```python
from src.core.feature_flags import FeatureFlags

def validate_feature_configuration():
    """Validate feature flag configuration at startup."""
    required_features = ["api:auth", "database:migrations"]
    
    for feature in required_features:
        if not FeatureFlags.is_enabled(feature):
            logger.error("Required feature not enabled: {}", feature)
            raise ValueError(f"Required feature {feature} is not enabled")
    
    # Warn about deprecated features
    deprecated_features = ["old_api", "legacy_auth"]
    for feature in deprecated_features:
        if FeatureFlags.is_enabled(feature):
            logger.warning("Deprecated feature enabled: {}", feature)
```

## Related Files

- **`config.py`** - Integration with main configuration system
- **`main.py`** - Application startup with feature-based routing
- **`api/`** - API endpoints using feature flags for conditional inclusion
- **`services/`** - Business logic services with feature-controlled implementations
- **`middleware/`** - Middleware components enabled via feature flags

## Dependencies

- **`pathlib`** - File path handling for .env file discovery
- **`os`** - Environment variable access and manipulation
- **Standard library only** - No external dependencies for reliability

---

*This module provides flexible, environment-based feature flag management for the ReViewPoint backend, enabling controlled feature rollouts, A/B testing, and environment-specific functionality without code deployment.*

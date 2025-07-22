# `core/feature_flags.py`

| Item               | Value                                                              |
| ------------------ | ------------------------------------------------------------------ |
| **Layer**          | Core Infrastructure                                                |
| **Responsibility** | Feature flag management and configuration-driven feature toggles  |
| **Status**         | 🟢 Done                                                            |

## 1. Purpose

Provides a centralized system for managing feature flags, allowing developers to toggle features on/off without code deployments. Supports gradual rollouts, A/B testing, and safe feature deployment practices.

## 2. Public API

| Symbol       | Type     | Description            |
| ------------ | -------- | ---------------------- |
| `FeatureFlag` | Class | Individual feature flag configuration |
| `FeatureFlagManager` | Class | Centralized flag management |
| `is_enabled` | Function | Check if a feature is enabled |
| `get_flag_value` | Function | Get feature flag value with type safety |
| `@feature_flag` | Decorator | Conditional endpoint/function execution |

## 3. Feature Flag Types

### Boolean Flags
Simple on/off toggles for features:
```python
NEW_UI_ENABLED = FeatureFlag(
    name="new_ui_enabled",
    default=False,
    description="Enable the new user interface"
)
```

### Percentage Rollouts
Gradual feature rollouts to user percentages:
```python
ENHANCED_ANALYTICS = FeatureFlag(
    name="enhanced_analytics",
    default=0,  # 0-100 percentage
    description="Enhanced analytics features"
)
```

### User-Specific Flags
Flags targeting specific users or groups:
```python
BETA_FEATURES = FeatureFlag(
    name="beta_features",
    default=[],  # List of user IDs
    description="Beta features for specific users"
)
```

## 4. Usage Examples

### Basic Feature Check
```python
from backend.core.feature_flags import is_enabled

@app.get("/api/v1/new-endpoint")
async def new_endpoint():
    if not is_enabled("new_api_features"):
        raise HTTPException(404, "Endpoint not available")
    
    return {"message": "New feature enabled!"}
```

### Decorator Usage
```python
from backend.core.feature_flags import feature_flag

@feature_flag("advanced_search")
@app.get("/api/v1/search/advanced")
async def advanced_search():
    # Only accessible when feature is enabled
    return {"results": [...]}
```

### Percentage-Based Rollout
```python
from backend.core.feature_flags import get_rollout_percentage

async def get_recommendations(user_id: str):
    if get_rollout_percentage("ml_recommendations", user_id) > 50:
        return await get_ml_recommendations(user_id)
    else:
        return await get_basic_recommendations(user_id)
```

## 5. Configuration Sources

### Environment Variables
```bash
# Feature flags via environment
FEATURE_NEW_UI_ENABLED=true
FEATURE_ENHANCED_ANALYTICS=25
FEATURE_BETA_USERS=user1,user2,user3
```

### Database Storage
```python
# Dynamic flags stored in database
class FeatureFlagModel(Base):
    __tablename__ = "feature_flags"
    
    name = Column(String, primary_key=True)
    enabled = Column(Boolean, default=False)
    value = Column(JSON)
    updated_at = Column(DateTime, default=datetime.utcnow)
```

### External Services
- Integration with LaunchDarkly, Split.io, or similar services
- Real-time flag updates without deployment
- Advanced targeting and analytics

## 6. Flag Management

### Admin Interface
```python
@app.post("/admin/feature-flags/{flag_name}")
async def update_feature_flag(
    flag_name: str, 
    enabled: bool,
    current_user: User = Depends(require_admin)
):
    await flag_manager.update_flag(flag_name, enabled)
    return {"status": "updated"}
```

### Audit Logging
```python
class FeatureFlagAudit(Base):
    __tablename__ = "feature_flag_audit"
    
    id = Column(UUID, primary_key=True)
    flag_name = Column(String, nullable=False)
    old_value = Column(JSON)
    new_value = Column(JSON)
    changed_by = Column(UUID, ForeignKey("users.id"))
    changed_at = Column(DateTime, default=datetime.utcnow)
```

## 7. Best Practices

### Flag Naming
- Use descriptive, consistent naming conventions
- Include feature area prefix: `analytics_`, `ui_`, `api_`
- Use snake_case for consistency

### Lifecycle Management
- Set expiration dates for temporary flags
- Regular cleanup of unused flags
- Documentation for each flag's purpose

### Testing
```python
@pytest.mark.parametrize("flag_enabled", [True, False])
async def test_feature_with_flag(flag_enabled):
    with mock_feature_flag("new_feature", flag_enabled):
        result = await call_feature_dependent_function()
        assert result.status == ("enabled" if flag_enabled else "disabled")
```

## 8. Performance Considerations

### Caching
- In-memory caching of frequently accessed flags
- Redis caching for distributed deployments
- Cache invalidation on flag updates

### Lazy Loading
- Load flags on first access
- Background refresh for long-running processes
- Fallback to defaults on cache miss

## 9. Security

### Access Control
- Admin-only flag modification endpoints
- Audit logging for all flag changes
- Role-based access to sensitive flags

### Validation
- Type validation for flag values
- Range validation for percentage flags
- Schema validation for complex flag data

## 10. Monitoring

### Metrics
- Flag usage frequency
- Performance impact of flag checks
- Rollout progress tracking

### Alerts
- Unexpected flag state changes
- High error rates from flag-dependent features
- Performance degradation from flag overhead

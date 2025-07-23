# Health Monitoring API Router

**File:** `backend/src/api/v1/health.py`  
**Purpose:** Health check and metrics endpoints for API monitoring and observability  
**Lines of Code:** 418  
**Type:** Health Monitoring API Router  

## Overview

The Health Monitoring API Router provides comprehensive health check and metrics collection endpoints for monitoring the ReViewPoint API service. This module implements robust health monitoring capabilities including database connectivity checks, system uptime tracking, dependency version reporting, database connection pool monitoring, and Prometheus-compatible metrics exposure. It's designed for integration with monitoring systems, load balancers, and observability platforms.

## Architecture

### Core Design Principles

1. **Observability-First**: Comprehensive monitoring and metrics collection
2. **Service Health**: Multi-layer health status validation
3. **Performance Monitoring**: Response time and connection pool tracking
4. **Standards Compliance**: Prometheus-compatible metrics format
5. **High Availability**: Graceful degradation and error handling
6. **Security Protected**: API key protection for sensitive metrics

### Health Check Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Health Check  │    │   DB Connection │    │  Pool Metrics   │
│    /health      │────┤    Validation   │────┤   Collection    │
│                 │    │                 │    │                 │
│ • Status        │    │ • Connectivity  │    │ • Pool Size     │
│ • Uptime        │    │ • Error Detect  │    │ • Active Conn   │
│ • Response Time │    │ • Pool Stats    │    │ • Overflow      │
│ • Versions      │    │ • Health Status │    │ • Awaiting      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Prometheus    │
                    │    Metrics      │
                    │   /metrics      │
                    │                 │
                    │ • Text Format   │
                    │ • Time Series   │
                    │ • Pool Stats    │
                    │ • Uptime        │
                    └─────────────────┘
```

## Core Endpoints

### 🏥 **Health Check Endpoint**

#### `GET /health`
```python
@router.get("/health", status_code=200)
async def health_check(
    response: Response,
    request_id: str = Depends(get_request_id),
    feature_flag_ok: bool = Depends(require_feature("health:read")),
    _api_key: None = Depends(require_api_key),
) -> HealthResponseDict:
```

**Purpose:** Comprehensive health status check for API and dependencies

**Health Check Process:**
1. **Database Connectivity**: Test database connection with health check query
2. **Response Time Tracking**: Measure and report endpoint response time
3. **Pool Statistics**: Collect database connection pool metrics
4. **Version Information**: Report versions of key dependencies
5. **Status Determination**: Calculate overall service health status
6. **HTTP Status Mapping**: Return appropriate HTTP status codes

**Response Structure:**
```json
{
  "status": "ok",
  "db": {
    "ok": true,
    "error": null,
    "pool": {
      "size": 5,
      "checkedin": 4,
      "checkedout": 1,
      "overflow": 0,
      "awaiting": 0
    }
  },
  "uptime": 1234.56,
  "response_time": 0.0012,
  "versions": {
    "python": "3.11.8",
    "fastapi": "0.110.0",
    "sqlalchemy": "2.0.29"
  }
}
```

**Health Status Logic:**
```python
# Healthy response (200 OK)
{
  "status": "ok",
  "db": {"ok": true, "error": null}
}

# Unhealthy response (503 Service Unavailable)
{
  "status": "error",
  "db": {"ok": false, "error": "Database connection failed"},
  "detail": "Database connection failed"
}
```

**Response Headers:**
- `X-Health-Response-Time`: Endpoint execution duration
- Standard HTTP status codes for health state

### 📊 **Prometheus Metrics Endpoint**

#### `GET /metrics`
```python
@router.get("/metrics", status_code=200)
def metrics() -> Response:
```

**Purpose:** Prometheus-compatible metrics for monitoring integration

**Metrics Format:**
```
app_uptime_seconds 12345.67
db_pool_size 5
db_pool_checkedin 4
db_pool_checkedout 1
db_pool_overflow 0
db_pool_awaiting 0
```

**Exported Metrics:**

| Metric Name | Type | Description | Example Value |
|-------------|------|-------------|---------------|
| `app_uptime_seconds` | Gauge | API service uptime in seconds | `12345.67` |
| `db_pool_size` | Gauge | Total database connection pool size | `5` |
| `db_pool_checkedin` | Gauge | Idle connections in pool | `4` |
| `db_pool_checkedout` | Gauge | Active connections from pool | `1` |
| `db_pool_overflow` | Gauge | Overflow connections beyond pool | `0` |
| `db_pool_awaiting` | Gauge | Connections waiting for availability | `0` |

**Prometheus Integration:**
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'reviewpoint-api'
    static_configs:
      - targets: ['api.reviewpoint.org:443']
    metrics_path: '/api/v1/metrics'
    scheme: 'https'
```

## Utility Functions

### 📊 **Database Pool Statistics**

#### `get_pool_stats()`
```python
def get_pool_stats() -> PoolStatsDict:
    """Returns statistics about the database connection pool."""
```

**Purpose:** Collect comprehensive database connection pool metrics

**Pool Metrics Collection:**
```python
# SQLAlchemy pool attributes
pool_attributes = [
    "size",        # Total pool size
    "checkedin",   # Available connections
    "checkedout",  # Active connections  
    "overflow",    # Overflow connections
    "awaiting"     # Connections waiting
]
```

**Error Handling:**
- **Engine Initialization**: Handles uninitialized database engine
- **Attribute Access**: Graceful handling of missing pool attributes
- **Method Calls**: Safe execution of pool statistic methods
- **Exception Safety**: Returns empty stats on any failure

**Implementation Details:**
```python
for attr in ("size", "checkedin", "checkedout", "overflow", "awaiting"):
    val = getattr(pool, attr, None)
    if callable(val):
        try:
            stats[attr] = val()  # Call method if callable
        except Exception:
            stats[attr] = None   # Handle method call failures
    else:
        stats[attr] = val        # Use direct value
```

### 🕐 **Application Uptime Tracking**

#### Global Uptime Tracking
```python
APP_START_TIME: Final[float] = time.time()

# Calculate uptime
uptime: float = time.time() - APP_START_TIME
```

**Purpose:** Track API service uptime from application start

**Uptime Calculation:**
- **Start Time Recording**: Captured at module import time
- **Current Uptime**: Calculated as current time minus start time
- **Precision**: Floating-point seconds for sub-second accuracy
- **Persistence**: Survives across individual requests

## Type Definitions

### 🏗️ **TypedDict Structures**

#### Health Response Structure
```python
class HealthResponseDict(TypedDict, total=False):
    status: Literal["ok", "error"]
    db: DBStatusDict
    uptime: float
    response_time: float
    versions: VersionsDict
    detail: str | None
```

#### Database Status Structure
```python
class DBStatusDict(TypedDict, total=False):
    ok: bool
    error: str | None
    pool: PoolStatsDict
```

#### Connection Pool Statistics
```python
class PoolStatsDict(TypedDict, total=False):
    size: int | None
    checkedin: int | None
    checkedout: int | None
    overflow: int | None
    awaiting: int | None
```

#### Version Information
```python
class VersionsDict(TypedDict):
    python: str
    fastapi: str | None
    sqlalchemy: str | None
```

**Type Safety Benefits:**
- **Compile-Time Validation**: MyPy type checking support
- **IDE Support**: Enhanced autocomplete and error detection
- **Documentation**: Self-documenting response structures
- **API Contracts**: Clear interface definitions

## Security Features

### 🔐 **Protected Access**

#### API Key Protection
```python
dependencies=[
    Depends(get_request_id),
    Depends(require_feature("health:read")),
    Depends(require_api_key),
]
```

**Security Layers:**
1. **API Key Validation**: Service-level authentication
2. **Feature Flags**: Runtime endpoint control
3. **Request Tracing**: Correlation ID for audit logging

#### Information Disclosure Prevention
```python
# Safe error handling - no sensitive information exposure
except Exception as exc:
    db_ok = False
    db_error = str(exc)  # Generic error message only
```

**Security Measures:**
- **Error Sanitization**: No sensitive data in error messages
- **Controlled Exposure**: Only necessary health information exposed
- **Audit Logging**: All health check requests logged with request ID

### 🛡️ **Rate Limiting Considerations**

**Health Check Protection:**
- Protected by API key requirement
- Feature flag controlled access
- No additional rate limiting (monitoring tools need frequent access)

**Metrics Endpoint Protection:**
- Same security model as health check
- Designed for frequent scraping by monitoring systems
- Lightweight response format for high-frequency access

## Error Handling

### 🛠️ **Database Health Failures**

```python
try:
    await db_healthcheck()
except Exception as exc:
    db_ok = False
    db_error = str(exc)
    response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
```

**Error Response Pattern:**
```json
{
  "status": "error",
  "db": {
    "ok": false,
    "error": "Database connection failed",
    "pool": {}
  },
  "detail": "Database connection failed"
}
```

**HTTP Status Codes:**
- **200 OK**: All systems healthy
- **503 Service Unavailable**: Database connectivity issues
- **401 Unauthorized**: Missing/invalid API key
- **403 Forbidden**: Feature flag disabled

### 🔄 **Graceful Degradation**

```python
# Pool stats collection with error handling
try:
    stats[attr] = val() if callable(val) else val
except Exception:
    stats[attr] = None  # Graceful fallback
```

**Degradation Strategy:**
- **Partial Information**: Return available metrics even if some fail
- **Empty Fallbacks**: Safe default values for missing data
- **Error Isolation**: Individual metric failures don't break entire response

## Performance Considerations

### ⚡ **Optimized Health Checks**

#### Fast Database Health Check
```python
# Lightweight database connectivity test
await db_healthcheck()  # Simple SELECT 1 query
```

**Performance Features:**
- **Minimal Query**: Simple connectivity test, not full database scan
- **Fast Response**: Sub-millisecond response times
- **Async Operations**: Non-blocking health check execution
- **Cached Engine**: Reuses existing database engine

#### Response Time Measurement
```python
start: float = time.monotonic()
# ... health check operations ...
duration: float = time.monotonic() - start
response.headers["X-Health-Response-Time"] = f"{duration:.4f}s"
```

**Timing Benefits:**
- **Monotonic Clock**: Immune to system clock adjustments
- **High Precision**: Sub-millisecond accuracy
- **Header Exposure**: Response time available to monitoring tools

### 📊 **Efficient Metrics Collection**

```python
# Lightweight metrics generation
lines: list[str] = [
    f"app_uptime_seconds {uptime}",
    f"db_pool_size {pool_stats.get('size', 0)}",
    # ... other metrics
]
return Response("\n".join(lines), media_type="text/plain")
```

**Efficiency Features:**
- **Text Format**: Minimal overhead compared to JSON
- **Single Pass**: Collect all metrics in one operation
- **Memory Efficient**: Direct string concatenation
- **Fast Serialization**: Plain text, no complex serialization

## Usage Patterns

### 🔧 **Load Balancer Health Checks**

```bash
# Simple health check for load balancer
curl -H "X-API-Key: your-api-key" \
     https://api.reviewpoint.org/api/v1/health

# Expected responses:
# 200 OK - Service healthy, route traffic
# 503 Service Unavailable - Service unhealthy, stop routing
```

### 📊 **Prometheus Monitoring**

```yaml
# Grafana dashboard query examples
# Uptime visualization
app_uptime_seconds

# Database connection pool utilization
(db_pool_checkedout / db_pool_size) * 100

# Connection pool health
db_pool_awaiting > 0  # Alert if connections waiting
```

### 🔍 **Application Monitoring**

```python
# Application monitoring integration
import requests

async def check_service_health():
    """Monitor service health from application code."""
    try:
        response = requests.get(
            "https://api.reviewpoint.org/api/v1/health",
            headers={"X-API-Key": "monitoring-key"},
            timeout=5
        )
        
        if response.status_code == 200:
            health_data = response.json()
            if health_data["status"] == "ok":
                print("✅ Service healthy")
            else:
                print(f"❌ Service unhealthy: {health_data.get('detail')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            
    except requests.RequestException as e:
        print(f"❌ Health check error: {e}")
```

### 🐳 **Docker Health Checks**

```dockerfile
# Dockerfile health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f -H "X-API-Key: docker-health-key" \
      http://localhost:8000/api/v1/health || exit 1
```

### ☸️ **Kubernetes Health Probes**

```yaml
# Kubernetes deployment health probes
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      containers:
      - name: reviewpoint-api
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
            httpHeaders:
            - name: X-API-Key
              value: k8s-health-key
          initialDelaySeconds: 30
          periodSeconds: 10
        
        readinessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
            httpHeaders:
            - name: X-API-Key
              value: k8s-health-key
          initialDelaySeconds: 5
          periodSeconds: 5
```

## Testing Strategies

### 🧪 **Health Check Testing**

```python
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

def test_health_check_healthy():
    """Test health check when all systems are healthy."""
    client = TestClient(app)
    
    with patch('src.api.v1.health.db_healthcheck', new_callable=AsyncMock) as mock_health:
        mock_health.return_value = None  # Successful health check
        
        response = client.get(
            "/api/v1/health",
            headers={"X-API-Key": "test-key"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["db"]["ok"] is True
        assert "uptime" in data
        assert "response_time" in data
        assert "versions" in data

def test_health_check_db_failure():
    """Test health check when database is unavailable."""
    client = TestClient(app)
    
    with patch('src.api.v1.health.db_healthcheck', new_callable=AsyncMock) as mock_health:
        mock_health.side_effect = Exception("Database connection failed")
        
        response = client.get(
            "/api/v1/health",
            headers={"X-API-Key": "test-key"}
        )
        
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "error"
        assert data["db"]["ok"] is False
        assert data["db"]["error"] == "Database connection failed"
        assert data["detail"] == "Database connection failed"
```

### 📊 **Metrics Testing**

```python
def test_metrics_endpoint():
    """Test Prometheus metrics endpoint."""
    client = TestClient(app)
    
    response = client.get(
        "/api/v1/metrics",
        headers={"X-API-Key": "test-key"}
    )
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/plain; charset=utf-8"
    
    metrics_text = response.text
    assert "app_uptime_seconds" in metrics_text
    assert "db_pool_size" in metrics_text
    assert "db_pool_checkedin" in metrics_text

def test_pool_stats_collection():
    """Test database pool statistics collection."""
    with patch('src.api.v1.health.engine') as mock_engine:
        mock_pool = Mock()
        mock_pool.size = 5
        mock_pool.checkedin = lambda: 4
        mock_pool.checkedout = lambda: 1
        mock_pool.overflow = lambda: 0
        mock_pool.awaiting = lambda: 0
        
        mock_engine.pool = mock_pool
        
        stats = get_pool_stats()
        
        assert stats["size"] == 5
        assert stats["checkedin"] == 4
        assert stats["checkedout"] == 1
        assert stats["overflow"] == 0
        assert stats["awaiting"] == 0
```

### 🔒 **Security Testing**

```python
def test_health_check_requires_api_key():
    """Test that health check requires API key."""
    client = TestClient(app)
    
    response = client.get("/api/v1/health")
    assert response.status_code == 401

def test_metrics_requires_api_key():
    """Test that metrics endpoint requires API key."""
    client = TestClient(app)
    
    response = client.get("/api/v1/metrics")
    assert response.status_code == 401

def test_feature_flag_enforcement():
    """Test feature flag enforcement on health endpoints."""
    client = TestClient(app)
    
    with patch('src.api.v1.health.require_feature') as mock_feature:
        mock_feature.side_effect = HTTPException(403, "Feature disabled")
        
        response = client.get(
            "/api/v1/health",
            headers={"X-API-Key": "test-key"}
        )
        assert response.status_code == 403
```

## Monitoring Integration

### 📊 **Grafana Dashboard Queries**

```promql
# Service uptime
app_uptime_seconds

# Database connection pool utilization rate
(db_pool_checkedout / db_pool_size) * 100

# Connection pool health - connections waiting
db_pool_awaiting

# Pool overflow indicator
db_pool_overflow > 0

# Service availability (health check success rate)
up{job="reviewpoint-api"}
```

### 🚨 **Alerting Rules**

```yaml
# Prometheus alerting rules
groups:
- name: reviewpoint-api
  rules:
  - alert: ServiceDown
    expr: up{job="reviewpoint-api"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "ReViewPoint API is down"
      
  - alert: DatabaseConnectionPoolExhausted
    expr: db_pool_checkedout / db_pool_size > 0.9
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "Database connection pool nearly exhausted"
      
  - alert: ConnectionsWaiting
    expr: db_pool_awaiting > 0
    for: 30s
    labels:
      severity: warning
    annotations:
      summary: "Database connections waiting for availability"
```

## Best Practices

### ✅ **Do's**

- **Use for Load Balancer Health Checks**: Integrate with load balancer health monitoring
- **Monitor Response Times**: Track health check endpoint performance
- **Set Up Alerts**: Configure alerts on health check failures
- **Use Metrics for Capacity Planning**: Monitor connection pool usage trends
- **Implement Retries**: Add retry logic for transient health check failures
- **Cache Pool Stats**: Consider caching pool statistics for high-frequency access

### ❌ **Don'ts**

- **Don't Expose Sensitive Information**: Keep error messages generic
- **Don't Skip API Key Protection**: Always require authentication for health endpoints
- **Don't Make Health Checks Heavy**: Keep database health checks lightweight
- **Don't Ignore Pool Metrics**: Monitor connection pool for capacity planning
- **Don't Hardcode Thresholds**: Make alert thresholds configurable

## Related Files

- **`src/core/database.py`** - Database engine and health check functions
- **`src/core/events.py`** - Database health check implementation
- **`src/api/deps.py`** - Dependency injection for health check requirements
- **`src/core/config.py`** - Configuration for health check settings

## Dependencies

- **`fastapi`** - Web framework for API endpoints
- **`sqlalchemy`** - Database connection pool monitoring
- **`time`** - Timing and uptime calculations
- **`platform`** - System version information

---

*This health monitoring router provides comprehensive observability and monitoring capabilities for the ReViewPoint API, enabling effective monitoring, alerting, and capacity planning in production environments.*

# HTTP Request Logging Middleware - Request Correlation and Observability

## Purpose

The HTTP request logging middleware (`logging.py`) provides comprehensive request/response logging with unique request ID tracking for the ReViewPoint platform. This middleware implements cross-cutting observability concerns including request correlation, timing analysis, error tracking, and privacy-aware logging for all HTTP requests flowing through the FastAPI application.

## Key Components

### RequestLoggingMiddleware Class

**Core Middleware Implementation**:

The main middleware class that processes all HTTP requests and responses:

```python
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests with unique request IDs."""
    
    def __init__(
        self,
        app: ASGIApp,
        *,
        exclude_paths: Sequence[str] | None = None,
        logger_instance: "Logger | None" = None,
        header_name: str = "X-Request-ID",
    ) -> None:
```

#### Configuration Parameters
- **exclude_paths** - Paths to skip logging (default: `/health`, `/metrics`)
- **logger_instance** - Custom logger or default middleware logger
- **header_name** - HTTP header for request ID (default: `X-Request-ID`)

### Request Correlation System

**Global Request ID Management**:

```python
# Thread-local request ID storage
request_id_var: Final[ContextVar[str | None]] = ContextVar("request_id", default=None)

def get_request_id() -> str | None:
    """Get the current request ID from the context variable."""
    return request_id_var.get()
```

#### Correlation Features
- **Context Variables** - Thread-local request ID storage
- **UUID Generation** - Unique identifier creation for each request
- **Header Propagation** - Request ID transmission via HTTP headers
- **Cross-Service Tracking** - Distributed tracing support

## Request Processing Pipeline

### Middleware Execution Flow

The middleware implements a comprehensive request/response processing pipeline:

#### Processing Stages

1. **Path Filtering** - Skip excluded paths for performance
2. **Request ID Management** - Generate or extract correlation ID
3. **Context Setup** - Configure thread-local request context
4. **Pre-Request Logging** - Log incoming request details
5. **Request Processing** - Execute downstream middleware and handlers
6. **Post-Request Logging** - Log response details and timing
7. **Context Cleanup** - Reset thread-local context variables

### Request ID Handling

Sophisticated request ID management for distributed systems:

#### ID Generation Strategy
```python
# Generate or extract request ID
request_id: str = request.headers.get(self.header_name, str(uuid.uuid4()))
# Set the request ID in the context variable for this request/response cycle
token: Token[str | None] = request_id_var.set(request_id)
```

#### Benefits
- **Client Correlation** - Accept existing request IDs from clients
- **Automatic Generation** - Create new IDs when not provided
- **Context Propagation** - Make request ID available throughout request lifecycle
- **Service Integration** - Support for microservice request tracing

## Privacy and Security

### Sensitive Data Protection

Comprehensive sensitive data filtering for secure logging:

#### Sensitive Fields Configuration
```python
SENSITIVE_FIELDS: Final[frozenset[str]] = frozenset({
    "password",
    "token", 
    "access_token",
    "refresh_token",
})
```

#### Data Filtering Process
```python
# Filter sensitive fields from query params
filtered_query: list[tuple[str, str]] = [
    (k, "[FILTERED]") if k.lower() in SENSITIVE_FIELDS else (k, v)
    for k, v in request.query_params.multi_items()
]
```

### Privacy Features

Robust privacy protection in logging:

#### Protection Mechanisms
- **Query Parameter Filtering** - Remove sensitive data from URLs
- **Header Protection** - Filter authentication and sensitive headers
- **Automatic Detection** - Pattern-based sensitive data identification
- **Compliance Support** - GDPR and privacy regulation compliance

## Performance Monitoring

### Request Timing Analysis

Comprehensive request performance tracking:

#### Timing Implementation
```python
start_time: float = time.time()
# ... process request ...
process_time: float = time.time() - start_time
process_time_ms: int = round(process_time * 1000)
```

#### Performance Metrics
- **Request Duration** - End-to-end request processing time
- **Response Time Distribution** - Percentile analysis support
- **Slow Request Detection** - Performance bottleneck identification
- **Trend Analysis** - Historical performance tracking

### Monitoring Integration

Structured logging for monitoring systems:

#### Log Structure
```python
log_extra: dict[str, Any] = {
    "request_id": request_id,
    "method": request.method,
    "path": request.url.path,
    "query": filtered_query_str,
    "status_code": response.status_code,
    "process_time_ms": process_time_ms,
}
```

## Error Handling and Resilience

### Exception Logging

Comprehensive error tracking with full request context:

#### Error Processing
```python
except Exception as exc:
    # Log exceptions with request context
    error_process_time: float = time.time() - start_time
    error_process_time_ms: int = round(error_process_time * 1000)
    
    cast("Logger", self.logger.bind(**log_extra, error=str(exc))).exception(
        f"Error processing request {request.method} {request.url.path}: {exc}",
    )
    raise
```

#### Error Handling Features
- **Context Preservation** - Full request context in error logs
- **Exception Re-raising** - Proper error propagation to clients
- **Timing Tracking** - Error response time measurement
- **Stack Trace Logging** - Complete exception information

### Resilience Patterns

Robust middleware operation under various conditions:

#### Resilience Features
- **Graceful Degradation** - Continue operation despite logging failures
- **Resource Cleanup** - Proper context variable cleanup on errors
- **Memory Management** - Efficient handling of large request volumes
- **Thread Safety** - Safe operation in concurrent environments

## Structured Logging

### Log Format and Structure

Consistent, machine-readable log output:

#### Request Logging Format
```python
self.logger.info(
    f"Request {request.method} {request.url.path} | query: {filtered_query_str}"
)
```

#### Response Logging Format
```python
self.logger.info(
    f"Response {request.method} {request.url.path} completed with status {response.status_code} in {process_time_ms}ms"
)
```

### Log Enrichment

Enhanced log entries with contextual information:

#### Enrichment Features
- **Request Correlation** - Unique request ID in every log entry
- **HTTP Method** - Request method for filtering and analysis
- **URL Path** - Request path without sensitive query parameters
- **Status Codes** - Response status for success/error analysis
- **Timing Information** - Request processing duration

## Integration Patterns

### FastAPI Middleware Integration

Seamless integration with FastAPI's middleware system:

#### Middleware Registration
```python
from fastapi import FastAPI
from middlewares.logging import RequestLoggingMiddleware

app = FastAPI()
app.add_middleware(RequestLoggingMiddleware)
```

#### Configuration Options
```python
app.add_middleware(
    RequestLoggingMiddleware,
    exclude_paths=["/health", "/metrics", "/docs"],
    logger_instance=custom_logger,
    header_name="X-Correlation-ID"
)
```

### Service Integration

Integration with external services and systems:

#### Service Features
- **Load Balancer Integration** - Health check path exclusion
- **Monitoring System** - Structured log format for ingestion
- **API Gateway** - Request ID propagation support
- **Distributed Tracing** - OpenTelemetry integration ready

## Development and Testing

### Development Experience

Excellent development and debugging support:

#### Development Features
- **Local Debugging** - Detailed request information
- **Request Tracing** - Complete request lifecycle visibility
- **Performance Profiling** - Request timing analysis
- **Error Investigation** - Comprehensive error context

### Testing Support

Comprehensive testing capabilities:

#### Testing Features
- **Middleware Isolation** - Independent middleware testing
- **Mock Integration** - Easy mocking for unit tests
- **Request Simulation** - Test request/response logging
- **Performance Testing** - Middleware overhead measurement

## Configuration and Customization

### Flexible Configuration

Comprehensive configuration options for different environments:

#### Configuration Parameters
- **Path Exclusions** - Skip specific endpoints from logging
- **Custom Loggers** - Integration with different logging frameworks
- **Header Customization** - Configurable request ID headers
- **Filtering Rules** - Custom sensitive data patterns

### Environment-Specific Setup

Different configurations for various environments:

#### Environment Configurations
- **Development** - Verbose logging with full request details
- **Staging** - Production-like logging with testing features
- **Production** - Optimized logging with security filtering
- **Testing** - Minimal logging for performance testing

## Observability and Monitoring

### Comprehensive Observability

Full observability into application request patterns:

#### Observability Features
- **Request Rate Monitoring** - Track application throughput
- **Error Rate Analysis** - Monitor application health
- **Performance Metrics** - Response time percentiles
- **User Behavior** - Request pattern analysis

### Monitoring System Integration

Designed for integration with modern monitoring stacks:

#### Integration Support
- **Prometheus Metrics** - Structured logging for metric extraction
- **ELK Stack** - JSON log format for Elasticsearch ingestion
- **APM Integration** - Application Performance Monitoring support
- **Alert Generation** - Error pattern detection for alerting

## Security Considerations

### Security-Focused Design

Security-first approach to request logging:

#### Security Features
- **Data Protection** - Comprehensive sensitive data filtering
- **Audit Trail** - Complete request audit logging
- **Compliance Support** - GDPR and privacy regulation compliance
- **Attack Detection** - Request pattern analysis for threats

### Threat Detection Support

Advanced security monitoring capabilities:

#### Detection Features
- **Anomaly Detection** - Unusual request pattern identification
- **Rate Limiting Support** - Integration with abuse prevention
- **Authentication Tracking** - User session monitoring
- **Injection Detection** - SQL injection and XSS attempt logging

## Performance Optimization

### Efficient Implementation

High-performance middleware with minimal overhead:

#### Performance Features
- **Async Operations** - Non-blocking request processing
- **Memory Efficiency** - Minimal memory footprint
- **CPU Optimization** - Efficient string processing
- **Context Management** - Proper resource cleanup

### Scalability Support

Designed for high-throughput production environments:

#### Scalability Features
- **Horizontal Scaling** - Stateless design for multi-instance deployment
- **Load Distribution** - Efficient processing across instances
- **Resource Management** - Optimal CPU and memory usage
- **Concurrent Safety** - Thread-safe operation

## Related Files

- [`__init__.py`](__init__.py.md) - Middlewares package overview and integration
- [`../core/logging.py`](../core/logging.py.md) - Core logging configuration and setup
- [`../core/config.py`](../core/config.py.md) - Application configuration management
- [`../api/deps.py`](../api/deps.py.md) - Dependency injection system integration
- [`../main.py`](../main.py.md) - Application setup and middleware registration
- [`../utils/http_error.py`](../utils/http_error.py.md) - HTTP error handling utilities
- [`../core/security.py`](../core/security.py.md) - Security utilities and patterns

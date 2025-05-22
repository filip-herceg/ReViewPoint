<!-- filepath: c:\Users\00010654\Documents\Git\ReViewPoint\docs\backend\middlewares\logging.py.md -->
# `middlewares/logging.py`

| Item | Value |
|------|-------|
| **Layer** | Middleware |
| **Responsibility** | Implements FastAPI middleware for HTTP request/response logging with unique request IDs and timing. |
| **Status** | 🟢 Done |

## 1. Purpose  
Adds a unique request ID to each HTTP request, logs request and response details (including timing), and attaches the request ID to logs and response headers for traceability.

## 2. Public API  
| Symbol | Type | Description |
|--------|------|-------------|
| `RequestLoggingMiddleware` | class | FastAPI middleware for logging requests/responses |
| `get_request_id` | function | Returns the current request ID for the active request |
| `RequestIdFilter` | class | Logging filter that injects request ID into log records |

## 3. Behaviour & Edge-Cases  
- Each request gets a unique ID (or uses `X-Request-ID` header if provided).
- Request ID is stored in a context variable for access throughout the request lifecycle.
- Middleware logs incoming requests, outgoing responses, and errors with timing and request context.
- Excludes certain paths (e.g., `/health`, `/metrics`) from logging by default.
- Attaches request ID to response headers for client correlation.
- Handles context variable reset to avoid leaks between requests.

## 4. Dependencies  
- **Internal**: None
- **External**:
  - `fastapi`, `starlette` (for middleware and request/response handling)
  - `logging`, `uuid`, `contextvars`, `time` (standard library)

## 5. Tests  
| Test file | Scenario |
|-----------|----------|
| `backend/tests/middlewares/test_logging.py` | Tests request ID generation, logging, error handling, and propagation |

## 6. Open TODOs  
- [ ] Add configuration for excluded paths via environment or settings
- [ ] Add support for structured logging (e.g., JSON) in middleware logs

> **Update this page whenever the implementation changes.**

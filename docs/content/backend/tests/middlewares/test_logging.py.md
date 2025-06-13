# Test Documentation: backend/tests/middlewares/test_logging.py

## Overview

This file documents the tests for the backend logging middleware, which ensures:

- Logging of incoming requests and outgoing responses
- Proper formatting and log levels
- Handling of edge cases (e.g., large payloads, errors)
- Propagation of request IDs
- Filtering of sensitive data in logs

## Test Coverage

| Test Name                                   | Purpose                                                        | Method/Route                  | Expected Results                                                                                 |
|---------------------------------------------|----------------------------------------------------------------|-------------------------------|--------------------------------------------------------------------------------------------------|
| test_request_id_generation                  | Verifies a request ID is generated and logged for each request | GET /test                     | Response includes X-Request-ID header and request_id in body; logs contain request/response info |
| test_custom_request_id_header               | Checks custom X-Request-ID header is respected and logged      | GET /test (custom header)     | Response/JSON echo custom ID; logs reflect custom ID                                             |
| test_error_logging                          | Ensures errors are logged with request context                 | GET /error                    | Raises ValueError; logs contain error entry for request                                          |
| test_request_id_propagation_to_other_middleware | Checks request ID is available to downstream middleware        | GET /request-id               | (Skipped in TestClient)                                                                          |
| test_performance_logging                    | Verifies request performance (timing) is logged                | GET /test                     | Logs include status code and response time in ms                                                 |
| test_sensitive_query_param_filtering         | Ensures sensitive query params are filtered in logs            | GET /test?email=...&password=...&token=... | Logs filter out password/token values, show [FILTERED]; non-sensitive fields present            |

## Best Practices

- Use fixtures to capture and assert log output (e.g., loguru_list_sink)
- Test both normal and error scenarios
- Ensure logs do not leak sensitive information
- Use FastAPI's TestClient for route/middleware testing

## Example Test Structure

```python
import pytest
from fastapi.testclient import TestClient
from backend.src.main import app

def test_logging_middleware_logs_requests_and_responses():
    client = TestClient(app)
    response = client.get("/some-endpoint")
    # Check logs for expected entries (use caplog or similar)
    assert response.status_code == 200
```

## Related Docs

- [Logging Middleware Source](../../../src/middlewares/logging.py.md)
- [Backend Source Guide](../../../../backend-source-guide.md)

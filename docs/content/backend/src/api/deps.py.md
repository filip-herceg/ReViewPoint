<!-- filepath: c:\Users\00010654\Documents\Git\ReViewPoint\docs\backend\api\deps.py.md -->

# `api/deps.py`

| Item               | Value                                                                  |
| ------------------ | ---------------------------------------------------------------------- |
| **Layer**          | API                                                                    |
| **Responsibility** | (Stub) Intended for dependency-injection helpers for FastAPI endpoints |
| **Status**         | 🔴 TODO                                                                |

## 1. Purpose

This file is a placeholder for dependency-injection helpers. It will provide reusable dependency functions (e.g., get current user, get DB session) for route handlers.

## 2. Public API

_None yet. To be implemented._

## 3. Behaviour & Edge-Cases

_None yet. To be implemented._

## 4. Dependencies

- **Internal**: None
- **External**: None

## 5. Tests

| Test file  | Scenario                    |
| ---------- | --------------------------- |
| _None yet_ | _No implementation to test_ |

## 6. Open TODOs

- [ ] Implement dependency-injection helpers

> **Update this page whenever the implementation changes.**

# Dependency Injection Utilities (`deps.py`)

This module provides robust, reusable dependencies for FastAPI API endpoints in the backend. All dependencies use loguru for error and event logging, follow security best practices, and are designed for easy testing and mocking.

---

## Summary Table

| Dependency                  | Purpose                                                      | Returns / Usage Example                        |
|-----------------------------|--------------------------------------------------------------|------------------------------------------------|
| `get_db`                    | Yields DB session, manages lifecycle                        | `db = Depends(get_db)`                         |
| `get_current_user`          | Authenticates user via JWT, fetches from DB                 | `user = Depends(get_current_user)`             |
| `get_current_active_user`   | Ensures user is active (403 if not)                         | `user = Depends(get_current_active_user)`      |
| `optional_get_current_user` | Like above, but returns None if not valid                   | `user = Depends(optional_get_current_user)`     |
| `pagination_params`         | Validates pagination params, returns offset/limit           | `params = Depends(pagination_params)`           |
| `get_user_repository`       | Service locator for user repo, easy to mock                 | `repo = Depends(get_user_repository)`           |
| `get_request_id`            | Extracts/generates request ID for tracing                   | `request_id = Depends(get_request_id)`          |
| `get_current_request_id`    | Gets current request ID from contextvar                     | `trace_id = get_current_request_id()`           |

---

## Dependency Details

### `get_db`
Yields a SQLAlchemy AsyncSession for DB access. Handles session lifecycle, logs errors, and ensures proper cleanup.

**Usage:**
```python
from fastapi import Depends
from src.api.deps import get_db

def endpoint(db = Depends(get_db)):
    ...
```

**Testing:**
Override with a mock session using FastAPI's `dependency_overrides`.

---

### `get_current_user`
Extracts and validates JWT, fetches user from DB. Handles invalid/missing/expired tokens, user not found, or inactive/deleted users with HTTP 401.

**Usage:**
```python
from fastapi import Depends
from src.api.deps import get_current_user

def endpoint(user = Depends(get_current_user)):
    ...
```

**Testing:**
Override `verify_access_token` and `get_user_by_id` in tests. Use mock tokens and users. Use `pytest.raises(HTTPException)` to assert error cases.

---

### `get_current_active_user`
Ensures user is active (403 if not). Depends on `get_current_user`.

**Usage:**
```python
from fastapi import Depends
from src.api.deps import get_current_active_user

def endpoint(user = Depends(get_current_active_user)):
    ...
```

**Testing:**
Test with both active and inactive user mocks. Assert HTTP 403 for inactive users.

---

### `optional_get_current_user`
Like `get_current_user`, but returns `None` if not valid.

**Usage:**
```python
from fastapi import Depends
from src.api.deps import optional_get_current_user

def endpoint(user = Depends(optional_get_current_user)):
    if user:
        ...
```

**Testing:**
Test with valid, invalid, and missing tokens. Assert `user is None` for invalid/missing tokens.

---

### `pagination_params`
Standardizes and validates pagination query params. Returns a `PaginationParams` object with `offset` and `limit`.

**Usage:**
```python
from fastapi import Depends
from src.api.deps import pagination_params

def endpoint(params = Depends(pagination_params)):
    items = repo.list(offset=params.offset, limit=params.limit)
```

**Testing:**
Test with valid and invalid offset/limit values. Assert HTTP 400 for invalid input. Use `caplog` to check for error logs.

---

### `get_user_repository`
Service locator for user repository (testable/mocked). Allows easy override in tests.

**Usage:**
```python
from fastapi import Depends
from src.api.deps import get_user_repository

def endpoint(repo = Depends(get_user_repository)):
    ...
```

**Testing:**
Override with a mock repository in tests using `dependency_overrides`.

---

### `get_request_id` and `get_current_request_id`
Extracts or generates a request ID for tracing. Stores in a context variable for access throughout the request.

**Usage:**
```python
from fastapi import Depends
from src.api.deps import get_request_id, get_current_request_id

def endpoint(request_id = Depends(get_request_id)):
    trace_id = get_current_request_id()
    ...
```

**Testing:**
Test with and without the `X-Request-ID` header. Assert correct propagation and uniqueness. Use `caplog` to check for log messages.

---

## Security & Logging
- All error and important events are logged with loguru.
- No sensitive data (e.g., passwords, tokens) is ever logged.
- Logging follows the security guidelines in [`core/logging.py`](../../core/logging.py).

## Advanced Testing & Mocking
- Use FastAPI's `dependency_overrides` for all dependencies.
- Use `pytest` fixtures and `monkeypatch` for token and DB/session mocks.
- Use `caplog` to assert loguru logs for error cases.
- For full API coverage, see also the [autogenerated API docs](deps_autodoc.md).

---

For more details, see the docstrings in [`deps.py`](deps.py) or related modules like [`core/logging.py`](../../core/logging.py).

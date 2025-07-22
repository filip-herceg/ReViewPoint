<!-- filepath: c:\Users\00010654\Documents\Git\ReViewPoint\docs\backend\core\security.py.md -->

# `core/security.py`

| Item               | Value                                                                                                                                                                                                                    |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Layer**          | Core                                                                                                                                                                                                                     |
| **Responsibility** | Security utilities for authentication, including JWT token handling. If password hashing/verification is implemented, document the corresponding public API functions here; otherwise, remove this mention for accuracy. |
| **Status**         | 🟢 Implemented                                                                                                                                                                                                           |

## 1. Purpose

Implements JWT token creation/validation and password hashing/verification for authentication and user management.

## 2. Public API

- `create_access_token(data: dict) -> str`
  - Creates a JWT access token with the given payload.
  - Uses config-driven secret, expiry, and algorithm.
  - Never logs or exposes the token.
  - Example:

    ```python
    from backend.core.security import create_access_token
    token = create_access_token({"sub": "user_id"})
    ```

- `verify_access_token(token: str) -> dict`
  - Validates a JWT access token and returns the decoded payload.
  - Raises `JWTError` if invalid or expired. Never logs or exposes the token.
  - Example:

    ```python
    from backend.core.security import verify_access_token
    payload = verify_access_token(token)
    ```

## 3. Behaviour & Edge-Cases

- If `settings.auth_enabled` is False, all JWT validation is bypassed and a default admin payload is returned. This is for development/testing only and logs a warning.
- Expiry, secret, and algorithm are always loaded from config (`settings`).
- Tokens are never logged or exposed in error messages.
- Expired or invalid tokens raise `JWTError`.
- Backward compatibility for secret key is handled by config.

## 4. Dependencies

- **Internal**: `backend.core.config`
- **External**: `python-jose[cryptography]`

## 5. Tests

| Test file                           | Scenario                    |
| ----------------------------------- | --------------------------- |
| `backend/tests/api/v1/test_auth.py` | JWT creation and validation |

## 6. Open TODOs

- [ ] Add more edge-case tests if needed

> **Update this page whenever the implementation changes.**

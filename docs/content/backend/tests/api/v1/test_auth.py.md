# `test_auth.py`

| Item | Value |
|------|-------|
| **Layer** | API Tests |
| **Responsibility** | Test authentication API endpoints: registration, login, logout, password reset, JWT, and error/edge cases |
| **Status** | 🟢 Complete |

## 1. Purpose
This file tests all authentication-related API endpoints, ensuring correct behavior for registration, login, logout, password reset, JWT creation/validation, and error/edge cases. It covers both success and failure scenarios, including security and logging.

## 2. Key Test Scenarios
- Registration: success, duplicate, invalid email/password
- Login: success, invalid password, non-existent user, inactive/deleted user, auth toggle
- JWT: creation, validation, expiry, tampering, config errors, logging
- Password reset: request, confirm, invalid/expired/reused token, weak password, non-existent email
- Logout: session invalidation
- /me endpoint: user info retrieval, invalid token
- Logging: no sensitive data leaked
- Edge cases: error handling, auth toggle

## 3. Notes
- All main authentication flows and edge cases are covered.
- Tests are automated and run in CI.
- See the test file for implementation details and specific scenarios.

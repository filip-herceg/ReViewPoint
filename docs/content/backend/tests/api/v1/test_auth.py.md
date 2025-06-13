# Test Documentation: backend/tests/api/v1/test_auth.py

## Overview

This file documents the tests for backend authentication API endpoints, ensuring:

- Registration, login, logout, password reset, JWT creation/validation
- Security, logging, and error/edge case handling

## Test Coverage

| Test Name                                      | Purpose                                                        | Method/Route/Type                | Expected Results                                                                                 |
|------------------------------------------------|----------------------------------------------------------------|----------------------------------|--------------------------------------------------------------------------------------------------|
| test_create_and_verify_access_token             | Validates JWT creation and verification                        | Unit (core.security)             | Token is created, verified, and contains correct payload                                          |
| test_verify_access_token_invalid                | Ensures tampered tokens are rejected                           | Unit (core.security)             | Raises JWTError                                                                                   |
| test_verify_access_token_expired                | Ensures expired tokens are rejected                            | Unit (core.security)             | Raises JWTError                                                                                   |
| test_create_access_token_logs                   | Checks logging for token creation/verification                 | Unit (core.security, caplog)     | Logs contain creation/verification messages                                                       |
| test_verify_access_token_logs_failure           | Checks logging for failed token verification                   | Unit (core.security, caplog)     | Logs contain failure messages                                                                    |
| test_create_access_token_missing_secret         | Ensures error if secret is missing                             | Unit (core.security)             | Raises ValueError                                                                                |
| test_create_access_token_jwt_error              | Handles JWTError during token creation                         | Unit (core.security)             | Raises JWTError                                                                                  |
| test_verify_access_token_missing_secret         | Ensures error if secret is missing during verification         | Unit (core.security)             | Raises ValueError                                                                                |
| test_verify_access_token_type_error             | Handles non-dict payload from decode                           | Unit (core.security)             | Raises TypeError                                                                                 |
| test_verify_access_token_unexpected_error       | Handles unexpected errors in decode                            | Unit (core.security)             | Raises RuntimeError                                                                              |
| test_protected_endpoint_accessible_when_auth_disabled | Checks /me endpoint when auth is disabled                | Async API (deps, monkeypatch)    | Returns dev admin user                                                                           |
| test_get_current_user_logs_warning_when_auth_disabled | Checks warning log when auth is disabled                 | Async API (deps, loguru_list_sink)| Logs contain warning                                                                            |
| test_register_endpoint                         | Tests user registration endpoint                               | Async API                        | Registers user, handles duplicate, returns correct status and messages                            |
| test_login_endpoint                            | Tests login endpoint (valid/invalid/non-existent)              | Async API                        | Authenticates, rejects invalid, returns correct status and messages                               |
| test_me_endpoint                               | Tests /me endpoint for user profile retrieval                  | Async API                        | Returns user info for valid token, 401 for invalid                                                |
| test_logout_endpoint                           | Tests logout endpoint and session invalidation                 | Async API                        | Logs out user, invalidates session, returns correct status and message                            |
| test_password_reset_request_endpoint           | Tests password reset request endpoint                          | Async API, loguru_list_sink      | Sends reset link, logs event, handles non-existent email                                          |
| test_password_reset_confirm_endpoint           | Tests password reset confirmation endpoint                     | Async API, monkeypatch           | Resets password, handles invalid/used token, allows login with new password                      |
| test_auth_logging_and_no_sensitive_data        | Ensures auth events are logged and sensitive data is filtered  | Async API, loguru_list_sink      | Logs contain events, do not leak passwords or tokens                                              |

## Best Practices

- Use fixtures for test data setup/teardown
- Test both positive and negative scenarios
- Mock external dependencies if needed
- Assert that logs do not leak sensitive information

## Related Docs

- [User API Source](../../../src/api/v1/users.py.md)
- [Backend Source Guide](../../../../backend-source-guide.md)

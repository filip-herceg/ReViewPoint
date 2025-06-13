# Test Documentation: backend/tests/services/test_user.py

## Overview

This file documents the tests for the backend user service layer, ensuring:

- Registration, authentication, password management
- User CRUD, roles, preferences, and edge cases

## Test Coverage

| Test Name                                 | Purpose                                                        | Method                  | Expected Results                                                      |
|--------------------------------------------|----------------------------------------------------------------|-------------------------|-----------------------------------------------------------------------|
| test_register_user_success                 | Registers a new user successfully                              | Async                   | User is created, active, and password is hashed                       |
| test_register_user_duplicate_email         | Ensures duplicate email registration is rejected               | Async                   | Raises UserAlreadyExistsError                                         |
| test_register_user_invalid_email           | Ensures invalid email is rejected                              | Async                   | Raises ValidationError                                                |
| test_register_user_invalid_password        | Ensures invalid password is rejected                           | Async                   | Raises ValidationError                                                |
| test_authenticate_user_success             | Authenticates user with valid credentials                      | Async                   | Returns JWT token                                                     |
| test_authenticate_user_wrong_password      | Rejects authentication with wrong password                     | Async                   | Raises ValidationError                                                |
| test_authenticate_user_not_found           | Rejects authentication for non-existent user                   | Async                   | Raises UserNotFoundError                                              |
| test_logout_user_deactivates               | Deactivates user on logout                                     | Async                   | User is marked inactive                                               |
| test_is_authenticated                      | Checks user authentication status                              | Sync                    | Returns True/False as appropriate                                     |
| test_is_authenticated_stub_cases           | Checks edge cases for authentication status                    | Sync                    | Returns correct status for all cases                                  |
| test_logout_user_nonexistent               | Handles logout for non-existent user                           | Async                   | Does not raise exception                                              |
| test_refresh_access_token_valid            | Refreshes access token for valid user                          | Sync                    | Returns new valid token                                               |
| test_refresh_access_token_invalid_subject  | Rejects refresh if subject does not match                      | Sync                    | Raises ValidationError                                                |
| test_refresh_access_token_invalid_token    | Rejects invalid token on refresh                               | Sync                    | Raises ValidationError                                                |
| test_revoke_refresh_token_stub             | Stub for token revocation                                      | Sync                    | Does not raise                                                        |
| test_verify_email_token_valid              | Verifies valid email token                                     | Sync                    | Returns decoded payload                                               |
| test_verify_email_token_invalid            | Rejects invalid email token                                    | Sync                    | Raises ValidationError                                                |
| test_get_password_reset_token_and_reset_password | Tests password reset flow                                | Async                   | Resets password, authenticates with new password                      |
| test_reset_password_invalid_token          | Rejects invalid reset token                                    | Async                   | Raises ValidationError                                                |
| test_reset_password_weak_password          | Rejects weak new password on reset                             | Async                   | Raises ValidationError                                                |
| test_reset_password_wrong_purpose          | Rejects reset with wrong token purpose                         | Async                   | Raises ValidationError                                                |
| test_change_password_success_and_failures  | Tests password change (success, wrong old, weak new, not found)| Async                   | Changes password or raises appropriate error                          |
| test_validate_password_strength            | Validates password strength                                    | Sync                    | Accepts strong, raises on weak                                        |

## Best Practices

- Use fixtures for test data setup/teardown
- Test both positive and negative scenarios
- Assert that business logic and security are enforced

## Related Docs

- [User Service Source](../../src/services/user.py.md)
- [Backend Source Guide](../../../backend-source-guide.md)

# `test_user.py`

| Item               | Value                                                                                                                         |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------- |
| **Layer**          | Service Tests                                                                                                                 |
| **Responsibility** | Test user service logic: registration, login, password hashing, password reset, user CRUD, roles, preferences, and edge cases |
| **Status**         | 🟢 Complete                                                                                                                   |

## 1. Purpose

This file tests the user service layer, ensuring correct business logic for user registration, authentication, password management, CRUD operations, role assignment/checking, and user preferences. It covers both normal and edge cases.

## 2. Key Test Scenarios

- Registration: success, duplicate, invalid email/password
- Login: success, invalid password, non-existent user, inactive/deleted user, auth toggle
- Password hashing: hash/verify, uniqueness, never plain text
- Password reset: request, confirm, invalid/expired/reused token, weak password, non-existent email
- User CRUD: create, read, update, delete, deactivate/reactivate, anonymize, partial update, preferences
- Roles: assign/check, invalid/duplicate/empty roles
- Preferences: set/update, invalid/extra fields
- Edge cases: error handling, logging, auth toggle

## 3. Notes

- All main user management flows and edge cases are covered.
- Tests are automated and run in CI.
- See the test file for implementation details and specific scenarios.

# `tests/models/test_*.py`

| Item               | Value                                          |
| ------------------ | ---------------------------------------------- |
| **Layer**          | Tests                                          |
| **Responsibility** | Test the model classes and their functionality |
| **Status**         | 🟢 Done                                        |

## 1. Purpose

These test files verify that the SQLAlchemy models function correctly, including their CRUD operations, relationships, and helper methods. The tests ensure that the database schema works as expected and that model operations perform correctly.

## 2. Test Files Overview

| Test File      | Description                                                          |
| -------------- | -------------------------------------------------------------------- |
| `test_base.py` | Tests for the Base class functionality like to_dict() and **repr**() |
| `test_user.py` | Tests CRUD operations for User model                                 |
| `test_file.py` | Tests CRUD operations and relationships for File model               |

## 3. Test Coverage

The model tests cover:

- Creating, reading, updating, and deleting database records
- Testing unique constraints and indexes
- Testing relationships between models
- Testing helper methods and serialization
- Testing common Base class functionality

## 4. Key Test Scenarios

### Base Model Tests

- Verify that `to_dict()` correctly serializes model attributes
- Ensure that `__repr__()` provides useful debugging output

### User Model Tests

- Create users and verify persistence
- Test unique email constraint
- Update user attributes and verify changes
- Delete users and verify removal

### File Model Tests

- Create files with user relationship
- Test file attribute updates
- Verify user-file relationship navigation
- Delete files and check for proper cleanup

## 5. Dependencies

- **Internal**:
  - `backend.models`: Modules being tested
  - `backend.core.database`: For database access
- **External**:
  - `pytest`: Testing framework
  - `pytest-asyncio`: For async test support
  - `sqlalchemy`: For database operations

## 6. Notes

The tests use isolated in-memory databases with unique connection strings to ensure test independence.

## 7. Authentication & User Management Test Coverage

The following test files cover all authentication and user management flows, including registration, login, password hashing, JWT, user CRUD, and edge cases:

| Test File                         | Description                                                                                                                  |
| --------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `tests/api/v1/test_auth.py`       | API endpoint tests for registration, login, logout, password reset, JWT, and error/edge cases                                |
| `tests/services/test_user.py`     | Service logic tests for registration, login, password hashing, password reset, user CRUD, roles, preferences, and edge cases |
| `tests/repositories/test_user.py` | Repository/model tests for user CRUD, validation, constraints, and edge cases                                                |
| `tests/utils/test_hashing.py`     | Password hashing and verification utility tests                                                                              |
| `tests/models/test_user.py`       | Basic SQLAlchemy User model CRUD tests                                                                                       |

### Key Test Scenarios

- **Registration:** Success, duplicate email, invalid email, invalid/weak password
- **Login:** Success, invalid password, non-existent user, inactive/deleted user, auth toggle
- **Password Hashing:** Hashing, verification, uniqueness, never storing plain text
- **JWT:** Token creation, validation, expiry, tampering, config errors, logging
- **Password Reset:** Request, confirm, invalid/expired/reused token, weak password, non-existent email
- **User CRUD:** Create, read, update, delete, deactivate/reactivate, anonymize, partial update, preferences
- **Edge Cases:** Invalid/duplicate data, role assignment/checking, preferences with extra fields, logging (no sensitive data), error handling, auth toggle

### Notes

- All main flows and edge cases are covered by automated tests.
- Coverage is high and tests are passing in CI.
- See the above test files for implementation details and specific scenarios.

## 8. Additional API Test Files

| Test File                      | Description                                                                                     |
| ------------------------------ | ----------------------------------------------------------------------------------------------- |
| `tests/api/v1/test_deps.py`    | Tests FastAPI dependency injection and security dependencies (e.g., current user, permissions). |
| `tests/api/v1/test_uploads.py` | Tests file upload API endpoints, including upload success, validation, and error cases.         |

**Note:** These files complement the authentication and user management tests by ensuring that API dependencies and file upload flows are robust and secure.

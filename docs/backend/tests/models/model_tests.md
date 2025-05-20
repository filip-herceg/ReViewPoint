# `tests/models/test_*.py`

| Item | Value |
|------|-------|
| **Layer** | Tests |
| **Responsibility** | Test the model classes and their functionality |
| **Status** | 🟢 Done |
| **Owner** | @ReViewPointTeam |

## 1. Purpose  
These test files verify that the SQLAlchemy models function correctly, including their CRUD operations, relationships, and helper methods. The tests ensure that the database schema works as expected and that model operations perform correctly.

## 2. Test Files Overview

| Test File | Description |
|-----------|-------------|
| `test_base.py` | Tests for the Base class functionality like to_dict() and __repr__() |
| `test_user.py` | Tests CRUD operations for User model |
| `test_file.py` | Tests CRUD operations and relationships for File model |

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

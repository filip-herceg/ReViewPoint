# `models/user.py`

| Item | Value |
|------|-------|
| **Layer** | Models |
| **Responsibility** | Defines the User model for authentication and user management |
| **Status** | 🟢 Done |

## 1. Purpose  
This file defines the User model that represents application users in the database. It handles the storage of user credentials and account status, providing the foundation for authentication and user management features.

## 2. Public API  

| Symbol | Type | Description |
|--------|------|-------------|
| `User` | SQLAlchemy model class | User entity model with authentication attributes |

**User Model Fields**:
- `email`: String(255), unique, indexed, non-nullable
- `hashed_password`: String(255), non-nullable
- `is_active`: Boolean, defaults to True
- Plus inherited fields from Base: `id`, `created_at`, `updated_at`

## 3. Behaviour & Edge-Cases  

- Email uniqueness is enforced at the database level
- The email field is indexed for performance in lookups
- Passwords are stored hashed, never in plain text
- The `is_active` flag allows disabling users without deletion
- Custom `__repr__` method for better debugging output

## 4. Dependencies  

- **Internal**:
  - `backend.models.base`: For Base class inheritance
  
- **External**:
  - `sqlalchemy.orm`: For ORM mapping
  - `sqlalchemy`: For column types and constraints

## 5. Tests  

| Test file | Scenario |
|-----------|----------|
| `backend/tests/models/test_user.py` | CRUD operations for User model |

## 6. Open TODOs  
- [ ] Add additional profile fields (name, preferences, etc.)
- [ ] Consider adding role-based authorization fields
- [ ] Add methods for common operations like verify_password

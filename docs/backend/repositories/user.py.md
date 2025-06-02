<!-- filepath: c:\Users\00010654\Documents\Git\ReViewPoint\docs\backend\repositories\user.py.md -->
# `repositories/user.py`

| Item | Value |
|------|-------|
| **Layer** | Repositories |
| **Responsibility** | CRUD operations and queries for user records in the database |
| **Status** | 🟢 Done |

## 1. Purpose  
Implements async CRUD operations for users, encapsulating all user-related database access logic.

## 2. Public API  
- `UserRepository.get_user_by_email(session, email)` → Fetch a user by email (returns `User | None`)
- `UserRepository.create_user(session, email, hashed_password, is_active=True)` → Create and persist a new user (returns `User`)
- `UserRepository.update_user(session, user, **kwargs)` → Update user fields and persist changes (returns `User`)
- `UserRepository.delete_user(session, user)` → Delete a user from the database (returns `None`)

## 3. Behaviour & Edge-Cases  
- All methods are async and require an `AsyncSession`.
- `get_user_by_email` returns `None` if no user is found.
- `update_user` only updates fields present on the model.
- All changes are committed and refreshed before returning.

## 4. Dependencies  
- **Internal**: `backend.models.user`, `backend.core.database`
- **External**: `sqlalchemy.ext.asyncio.AsyncSession`, `sqlalchemy.select`

## 5. Tests  
| Test file | Scenario |
|-----------|----------|
| `backend/tests/models/test_user.py` | Full CRUD coverage for repository methods |

## 6. Open TODOs  
- [ ] Add more query helpers as needed (e.g., by id)
- [ ] Add pagination and filtering helpers if required

> **Update this page whenever the implementation changes.**

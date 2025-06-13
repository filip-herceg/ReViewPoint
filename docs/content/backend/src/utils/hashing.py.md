<!-- filepath: c:\Users\00010654\Documents\Git\ReViewPoint\docs\backend\utils\hashing.py.md -->

# `utils/hashing.py`

| Item               | Value                                              |
| ------------------ | -------------------------------------------------- |
| **Layer**          | Utils                                              |
| **Responsibility** | Secure password hashing and verification utilities |
| **Status**         | 🟢 Implemented                                     |

## 1. Purpose

Provides secure password hashing and verification using [passlib]'s bcrypt algorithm.

## 2. Public API

- `hash_password(password: str) -> str`
  - Hashes a plain password using bcrypt.
  - Returns the hashed password as a string.
  - Example:

    ```python
    from backend.utils.hashing import hash_password
    hashed = hash_password('mysecret')
    ```

- `verify_password(plain: str, hashed: str) -> bool`
  - Verifies a plain password against a bcrypt hash.
  - Returns `True` if the password matches, `False` otherwise.
  - Example:

    ```python
    from backend.utils.hashing import verify_password
    is_valid = verify_password('mysecret', hashed)
    ```

## 3. Behaviour & Edge-Cases

- Plain passwords are never logged or stored.
- Only the hash should be stored in the database.
- Use `verify_password` for authentication checks.

## 4. Dependencies

- **External**: [passlib] (with `bcrypt` extra): `hatch run pip install 'passlib[bcrypt]'`

## 5. Tests

| Test file | Scenario |
| `backend/tests/utils/test_hashing.py` | Hashing and verifying passwords |

## 6. Open TODOs

- [ ] Integrate with user registration/authentication

[passlib]: https://passlib.readthedocs.io/en/stable/

> **Update this page whenever the implementation changes.**

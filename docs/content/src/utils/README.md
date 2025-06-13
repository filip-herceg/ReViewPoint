# Backend Utilities Documentation

This document provides a comprehensive overview of utility modules in the backend of the ReViewPoint project.

## Main Utilities

### hashing.py

- **Purpose:** Secure password hashing and verification.
- **Key Functions:**
  - `hash_password(password: str) -> str`: Hashes a plain password.
  - `verify_password(plain: str, hashed: str) -> bool`: Verifies a password against a hash.
- **Best Practices:**
  - Always use a strong, salted hash (e.g., bcrypt, argon2).
  - Never store plain-text passwords.

### validation.py

- **Purpose:** Input validation helpers for API and forms.
- **Key Functions:**
  - `validate_email(email: str) -> bool`: Checks if an email is valid.
  - `validate_password(password: str) -> bool`: Checks password strength.
- **Best Practices:**
  - Validate all user input at both client and server.

### cache.py

- **Purpose:** In-memory or persistent caching for performance.
- **Key Functions:**
  - `get(key: str) -> Any`: Retrieve cached value.
  - `set(key: str, value: Any, ttl: int)`: Store value with time-to-live.
- **Best Practices:**
  - Use cache for expensive or frequent queries.

### rate_limit.py

- **Purpose:** Rate limiting logic to prevent abuse.
- **Key Functions:**
  - `is_allowed(user_id: int) -> bool`: Checks if user can perform action.
- **Best Practices:**
  - Apply rate limits to sensitive endpoints (login, registration).

### errors.py

- **Purpose:** Custom error types and handlers for consistent error responses.
- **Key Classes:**
  - `ValidationError`, `AuthenticationError`, etc.
- **Best Practices:**
  - Use custom exceptions for clarity and maintainability.

## Usage Example

```python
from utils.hashing import hash_password, verify_password

hashed = hash_password('mysecret')
assert verify_password('mysecret', hashed)
```

## Related Documentation

- [Backend Source Guide](../../backend-source-guide.md)
- [API Reference](../../api-reference.md)
- [Backend Models](../models/README.md)

---

*Update this document as utilities evolve and new modules are added.*

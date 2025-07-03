# Backend Models Documentation

This document provides a comprehensive overview of all database models and schemas used in the backend of the ReViewPoint project.

## Main Models

### User

- **Purpose:** Represents a user account, authentication credentials, and profile information.
- **Fields:**
  - `id`: Unique identifier (UUID or integer)
  - `username`: User's login name (unique)
  - `email`: User's email address (unique)
  - `hashed_password`: Securely hashed password
  - `is_active`: Boolean flag for account status
  - `is_admin`: Boolean flag for admin privileges
  - `created_at`: Timestamp of account creation
- **Relationships:**
  - May have many files (see File model)

### File

- **Purpose:** Represents uploaded files and associated metadata.
- **Fields:**
  - `id`: Unique identifier
  - `owner_id`: Foreign key to User
  - `filename`: Original file name
  - `content_type`: MIME type
  - `size`: File size in bytes
  - `uploaded_at`: Timestamp
- **Relationships:**
  - Belongs to a User

### Token

- **Purpose:** Represents authentication and password reset tokens.
- **Fields:**
  - `id`: Unique identifier
  - `user_id`: Foreign key to User
  - `token`: Token string (JWT or random)
  - `type`: Token type (access, refresh, reset)
  - `created_at`: Timestamp
  - `expires_at`: Expiry timestamp

## Best Practices

- Use Pydantic for data validation and serialization.
- Keep models in sync with database migrations.
- Document all fields, types, and relationships.
- Use clear naming conventions and docstrings.

## Example (Pydantic Model)

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class User(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    is_admin: bool
    created_at: datetime
```

## Related Documentation

- [Backend Source Guide](../../backend-source-guide.md)
- [API Reference](../../api-reference.md)
- [Backend Utilities](../utils/README.md)

---

*Update this document as models evolve and new models are added.*

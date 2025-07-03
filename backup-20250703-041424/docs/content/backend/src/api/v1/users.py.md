# API Reference: `users.py`

This document provides a comprehensive reference for the backend API module `users.py`.

## Overview

The `users.py` module implements the user-related API endpoints for the backend. It is responsible for user registration, authentication, profile management, password reset, and user listing. The endpoints are designed to be secure, robust, and follow RESTful best practices.

## Main Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/users/` | GET | List all users (admin only) |
| `/api/v1/users/` | POST | Register a new user |
| `/api/v1/users/{user_id}` | GET | Retrieve user details by ID |
| `/api/v1/users/{user_id}` | PUT | Update user details |
| `/api/v1/users/{user_id}` | DELETE | Delete a user (admin only) |
| `/api/v1/users/login` | POST | Authenticate a user and return a token |
| `/api/v1/users/reset-password` | POST | Initiate password reset |
| `/api/v1/users/reset-password/confirm` | POST | Confirm password reset |

## Key Functions and Classes

- **UserCreate**: Pydantic model for user registration.
- **UserRead**: Pydantic model for user output.
- **UserUpdate**: Pydantic model for updating user info.
- **UserInDB**: Internal model for DB operations.
- **get_current_user**: Dependency for extracting the current user from the request.
- **get_user_by_id**: Retrieve a user by their unique ID.
- **authenticate_user**: Validate user credentials and return user object if valid.

## Security

- All endpoints require authentication except registration and login.
- Admin-only endpoints are protected by role-based access control.
- Passwords are hashed using a secure algorithm (see [hashing.py](../../utils/hashing.py.md)).
- JWT tokens are used for authentication.

## Error Handling

- Returns appropriate HTTP status codes for all error conditions.
- Uses custom error responses for validation and authentication errors.

## Related Documentation

- [User Model](../../models/user.py.md)
- [Authentication](../../utils/hashing.py.md)
- [API Reference](../../../api-reference.md)
- [Backend Source Guide](../../../../backend-source-guide.md)

---

*This file is auto-generated and should be updated as the API evolves. For implementation details, see the source code and related test documentation.*

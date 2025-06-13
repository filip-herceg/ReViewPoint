# users.py

## Purpose

Defines user-related API endpoints (registration, login, profile, etc.).

## API Endpoints

- **POST /api/v1/users/register**

  - Registers a new user.
  - **Request:** JSON body with user details (username, email, password, etc.)
  - **Response:** User info, auth token
  - **Auth:** None
  - **Errors:** 400 (validation), 409 (duplicate)

- **POST /api/v1/users/login**

  - Authenticates a user and returns a token.
  - **Request:** JSON body (username/email, password)
  - **Response:** Auth token
  - **Auth:** None
  - **Errors:** 401 (invalid credentials)

- **GET /api/v1/users/me**

  - Retrieves the current user's profile.
  - **Request:** Auth token in header
  - **Response:** User profile data
  - **Auth:** Required
  - **Errors:** 401 (unauthenticated)

- **PUT /api/v1/users/me**
  - Updates the current user's profile.
  - **Request:** Auth token, JSON body with updated fields
  - **Response:** Updated user profile
  - **Auth:** Required
  - **Errors:** 401 (unauthenticated), 400 (validation)

## Related Files

- [test_users.py](../../../../tests/api/v1/test_users.py.md)

---

_Expand this doc as endpoints evolve or are added._

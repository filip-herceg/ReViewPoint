<!-- filepath: c:\Users\00010654\Documents\Git\ReViewPoint\docs\backend\repositories\user.py.md -->

# `repositories/user.py`

| Item               | Value                                                        |
| ------------------ | ------------------------------------------------------------ |
| **Layer**          | Repositories                                                 |
| **Responsibility** | CRUD operations and queries for user records in the database |
| **Status**         | 🟢 Updated                                                   |

## 1. Purpose

Provides async functions to create, read, update, delete, and query users, encapsulating all user-related database access.

## 2. Public API

- `get_user_by_id(session, user_id)`
- `get_users_by_ids(session, user_ids)`
- `list_users_paginated(session, offset, limit)`
- `search_users_by_name_or_email(session, query, offset, limit)`
- `filter_users_by_status(session, is_active)`
- `filter_users_by_role(session, role)` _(stub: not implemented, no role field)_
- `get_users_created_within(session, start, end)`
- `count_users(session, is_active=None)`
- `get_active_users(session)`
- `get_inactive_users(session)`
- `get_users_by_custom_field(session, field, value)` _(stub: not implemented, no such field)_
- `bulk_create_users(session, users)`
- `bulk_update_users(session, user_ids, update_data)`
- `bulk_delete_users(session, user_ids)`
- `soft_delete_user(session, user_id)`
- `restore_user(session, user_id)`
- `upsert_user(session, email, defaults)`
- `partial_update_user(session, user_id, update_data)`
- `user_exists(session, user_id)`
- `is_email_unique(session, email, exclude_user_id=None)`
- `audit_log_user_change(session, user_id, action, details="")`
- `change_user_password(session, user_id, new_hashed_password)`
- `assign_role_to_user(session, user_id, role)` _(stub: not implemented, no role field)_
- `revoke_role_from_user(session, user_id, role)` _(stub: not implemented, no role field)_
- `db_session_context()` _(async context manager)_
- `db_transaction(session)` _(async context manager)_
- `get_user_with_files(session, user_id)` _(eager loads files)_
- `export_users_to_csv(session)` _(export all users as CSV)_
- `export_users_to_json(session)` _(export all users as JSON)_
- `import_users_from_dicts(session, user_dicts)` _(bulk import users from dicts)_
- `deactivate_user(session, user_id)` _(set is_active=False)_
- `reactivate_user(session, user_id)` _(set is_active=True)_
- `update_last_login(session, user_id, login_time=None)` _(update last_login_at)_
- `safe_get_user_by_id(session, user_id)` _(raises if not found)_
- `create_user_with_validation(session, email, password)` _(validates and creates user, raises on error)_
- `sensitive_user_action(session, user_id, action)` _(rate-limited action)_
- `anonymize_user(session, user_id)` _(irreversibly anonymizes user for privacy/GDPR)_
- `user_signups_per_month(session, year)` _(returns {month: count} for signups)_

## 2b. Summary Table of Actions

| Action Type | Method/Function                                                | Description / Return Value                                                     |
| ----------- | -------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| **Create**  | `create_user_with_validation(session, email, password)`        | Validates and creates a new user. Returns the created user or raises on error. |
|             | `bulk_create_users(session, users)`                            | Creates multiple users at once. Returns created users with IDs.                |
|             | `import_users_from_dicts(session, user_dicts)`                 | Bulk import users from dicts. Returns created users.                           |
|             | `upsert_user(session, email, defaults)`                        | Insert or update user by email. Returns the upserted user.                     |
| **Read**    | `get_user_by_id(session, user_id)`                             | Fetch a user by ID. Returns user or None.                                      |
|             | `safe_get_user_by_id(session, user_id)`                        | Fetch user by ID, raises if not found.                                         |
|             | `get_users_by_ids(session, user_ids)`                          | Fetch multiple users by IDs. Returns list of users.                            |
|             | `list_users_paginated(session, offset, limit)`                 | List users with pagination. Returns list of users.                             |
|             | `search_users_by_name_or_email(session, query, offset, limit)` | Search users by name/email. Returns list of users.                             |
|             | `filter_users_by_status(session, is_active)`                   | Filter users by active status. Returns list of users.                          |
|             | `filter_users_by_role(session, role)`                          | (Stub) Filter by role. Not implemented.                                        |
|             | `get_users_created_within(session, start, end)`                | Users created in a date range. Returns list of users.                          |
|             | `count_users(session, is_active=None)`                         | Count users, optionally by status. Returns integer.                            |
|             | `get_active_users(session)`                                    | List active users. Returns list of users.                                      |
|             | `get_inactive_users(session)`                                  | List inactive users. Returns list of users.                                    |
|             | `get_users_by_custom_field(session, field, value)`             | (Stub) Filter by custom field. Not implemented.                                |
|             | `get_user_with_files(session, user_id)`                        | Fetch user and their files (eager load). Returns user with files.              |
|             | `user_signups_per_month(session, year)`                        | Get user signup counts per month. Returns dict {month: count}.                 |
|             | `export_users_to_csv(session)`                                 | Export all users as CSV. Returns CSV data.                                     |
|             | `export_users_to_json(session)`                                | Export all users as JSON. Returns JSON data.                                   |
| **Update**  | `bulk_update_users(session, user_ids, update_data)`            | Update multiple users by IDs. Returns updated users.                           |
|             | `partial_update_user(session, user_id, update_data)`           | Update only provided fields for a user. Returns updated user.                  |
|             | `change_user_password(session, user_id, new_hashed_password)`  | Change a user's password. Returns None.                                        |
|             | `deactivate_user(session, user_id)`                            | Set user as inactive. Returns updated user.                                    |
|             | `reactivate_user(session, user_id)`                            | Set user as active. Returns updated user.                                      |
|             | `restore_user(session, user_id)`                               | Restore a soft-deleted user. Returns updated user.                             |
|             | `soft_delete_user(session, user_id)`                           | Soft-delete a user (set is_deleted). Returns updated user.                     |
|             | `update_last_login(session, user_id, login_time=None)`         | Update last login timestamp. Returns updated user.                             |
|             | `anonymize_user(session, user_id)`                             | Irreversibly anonymize user for privacy/GDPR. Returns None.                    |
|             | `audit_log_user_change(session, user_id, action, details="")`  | Log/audit a user change. Returns None.                                         |
|             | `assign_role_to_user(session, user_id, role)`                  | (Stub) Assign role. Not implemented.                                           |
|             | `revoke_role_from_user(session, user_id, role)`                | (Stub) Revoke role. Not implemented.                                           |
| **Delete**  | `bulk_delete_users(session, user_ids)`                         | Delete multiple users by IDs. Returns None.                                    |
|             | `soft_delete_user(session, user_id)`                           | Soft-delete a user. Returns updated user.                                      |
| **Helpers** | `user_exists(session, user_id)`                                | Check if user exists. Returns bool.                                            |
|             | `is_email_unique(session, email, exclude_user_id=None)`        | Check if email is unique. Returns bool.                                        |
|             | `sensitive_user_action(session, user_id, action)`              | Perform a rate-limited sensitive action. Returns None or raises.               |
|             | `db_session_context()`                                         | Async context manager for DB session.                                          |
|             | `db_transaction(session)`                                      | Async context manager for DB transaction.                                      |

> See the function docstrings and implementation for details on arguments, return values, and exceptions.

## 3. Behaviour & Edge-Cases

- Filtering by role and custom field are stubs (no such fields in model)
- Bulk update and delete operate only on provided IDs
- Bulk create returns users with IDs after commit
- Soft delete sets `is_deleted` flag, restore unsets it
- Upsert inserts or updates by email
- Partial update only updates provided fields
- Existence and uniqueness checks are available
- Audit logging uses Python logging
- Password change expects a hashed password
- Role/permission management is a stub (no such field in model)
- Session/context and transaction helpers simplify DB usage
- Eager loading uses SQLAlchemy relationship backref
- **Export/import**: CSV/JSON export all users, import creates users from dicts
- **Deactivate/reactivate**: Sets or unsets `is_active` flag
- **Last login tracking**: `last_login_at` is updated on login
- **Validation helpers**: Email and password validation with clear error messages
- **Async caching**: Frequently accessed users are cached by id (not ORM instance)
- **Rate limiting**: Sensitive actions are rate-limited per user/action
- **Error handling**: Standardized exceptions for not found, already exists, validation, and rate limit errors
- **Data anonymization**: Overwrites all PII, disables and soft-deletes user, cannot be reversed
- **User statistics**: Aggregates signups per month for analytics/compliance

## 4. Dependencies

- **Internal**: `src.models.user`, `src.models.file`, `src.core.database`
- **External**: `sqlalchemy`, `contextlib`, `datetime`, `logging`

## 5. Tests

| Test file                                      | Scenario                                                                              |
| ---------------------------------------------- | ------------------------------------------------------------------------------------- |
| `backend/tests/models/test_user_repository.py` | All repository methods, including session, transaction, eager loading, and role stubs |

## 6. Open TODOs

- [ ] Add support for user roles/permissions if/when added
- [ ] Extend eager loading for more relationships as needed
- [ ] Remove stub methods or implement them when the model is updated

> **Note:** Some methods in this repository (such as role management and custom field filtering) are present as stubs. These are intentionally left unimplemented and will remain so until the user model is extended to support roles, permissions, or additional fields. This is to provide a clear extension point for future features and to maintain API consistency.

## 2a. Possible Future Actions & Extensions

- User role and permission management (assign/revoke/check roles, permission checks)
- Advanced audit logging (field-level, external sinks)
- Multi-factor authentication support
- User profile fields and preferences
- OAuth/social login integration
- User group/organization management
- API key/token management
- User activity and login history
- Custom user metadata fields
- Soft/hard delete policies
- Bulk import/export with validation and error reporting
- Advanced statistics (retention, churn, cohort analysis)
- GDPR/CCPA compliance extensions
- Notification preferences and delivery
- Integration with external identity providers

---

> **Environment & Tooling:**
>
> - This project uses **Hatch** for all Python environment and dependency management. Poetry is no longer used—ignore any old references.
> - See [setup.md](../../../setup.md) and [test-instructions.md](../../../test-instructions.md) for up-to-date instructions on environment setup, running tests, and coverage.
>
> **Update this page whenever the implementation changes.**

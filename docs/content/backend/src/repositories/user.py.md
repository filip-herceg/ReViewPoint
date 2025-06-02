<!-- filepath: c:\Users\00010654\Documents\Git\ReViewPoint\docs\backend\repositories\user.py.md -->
# `repositories/user.py`

| Item | Value |
|------|-------|
| **Layer** | Repositories |
| **Responsibility** | CRUD operations and queries for user records in the database |
| **Status** | 🟢 Updated |

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
| Test file | Scenario |
|-----------|----------|
| `backend/tests/models/test_user_repository.py` | All repository methods, including session, transaction, eager loading, and role stubs |

## 6. Open TODOs  
- [ ] Add support for user roles/permissions if/when added
- [ ] Extend eager loading for more relationships as needed

> **Update this page whenever the implementation changes.**

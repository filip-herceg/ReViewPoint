# `test_user_repository.py`

| Item               | Value                                              |
| ------------------ | -------------------------------------------------- |
| **Layer**          | Model/Repository Tests                             |
| **Responsibility** | Test advanced repository operations for User model |
| **Status**         | 🟢 Complete                                        |

## 1. Purpose

This file tests advanced repository and model operations for the User model, including bulk operations, soft delete/restore, import/export, audit logging, and async utilities.

## 2. Key Test Scenarios

- Bulk create, update, delete users
- Soft delete and restore users
- Import/export users to CSV/JSON
- Audit logging for user changes
- Async caching and rate limiting
- Edge cases: invalid/duplicate data, error handling

## 3. Notes

- Ensures advanced repository features for the User model are robust and reliable.
- Tests are automated and run in CI.
- See the test file for implementation details and specific scenarios.

## 4. Test-by-Test Coverage (Detailed)

### Fixtures

- **`cleanup_users`**: Automatically runs before each test to delete all users from the database, ensuring a clean state for isolation and repeatability.

### CRUD and Query Tests

- **`test_get_user_by_id`**: Creates a user, fetches by ID, and asserts the correct user is returned.
- **`test_get_users_by_ids`**: Creates multiple users, fetches them by their IDs, and checks all are returned.
- **`test_list_users_paginated`**: Inserts 10 users, fetches a paginated slice (offset/limit), and checks the correct users are returned.
- **`test_search_users_by_name_or_email`**: Inserts users with a common substring, searches by that substring, and checks all matches are returned. Also tests a search with no results.
- **`test_filter_users_by_status`**: Inserts active and inactive users, fetches by status, and asserts correct filtering.
- **`test_get_users_created_within`**: Inserts users with different creation dates, fetches users within a date range, and checks only the correct ones are returned.
- **`test_count_users`**: Inserts users with mixed active status, counts total, active, and inactive users, and asserts correct counts.
- **`test_get_active_inactive_users`**: Inserts one active and one inactive user, fetches each group, and asserts correct membership.
- **`test_filter_users_by_role_stub`**: Inserts a user, calls the stub role filter (not implemented), and asserts it returns an empty list.
- **`test_get_users_by_custom_field_stub`**: Inserts a user, calls the stub custom field filter (not implemented), and asserts it returns an empty list.

### Bulk and Patch Operations

- **`test_bulk_create_users`**: Bulk creates users, checks all are assigned IDs, and verifies emails.
- **`test_bulk_update_users`**: Bulk creates users, updates a field for all, and asserts the update is applied.
- **`test_bulk_delete_users`**: Bulk creates users, deletes them by IDs, and asserts they are removed from the DB.
- **`test_soft_delete_and_restore_user`**: Creates a user, soft-deletes (sets is_deleted), then restores, and checks the flags.
- **`test_upsert_user`**: Inserts a user (upsert), then updates the same user (upsert again), and checks the update is applied.
- **`test_partial_update_user`**: Creates a user, partially updates a field, and checks the update. Also tries to update a non-existent field and asserts it is ignored.

### Existence and Validation

- **`test_user_exists`**: Creates a user, checks existence by ID, and checks a non-existent ID returns False.
- **`test_is_email_unique`**: Creates a user, checks that the email is not unique, checks a new email is unique, and checks that excluding the user's own ID makes the email unique.
- **`test_change_user_password`**: Creates a user, changes the password hash, and asserts the change is persisted.

### Logging, Files, and Context

- **`test_audit_log_user_change`**: Calls the audit log function for a user change, captures the log output, and asserts the correct log message is present.
- **`test_get_user_with_files`**: Creates a user and files, fetches the user with files eagerly loaded, and asserts the files are attached.
- **`test_db_session_context_and_transaction`**: Uses the DB transaction context manager to add a user, commits, and asserts the user is present in the DB.

### Import/Export and Advanced Features

- **`test_export_users_to_csv_and_json`**: Creates users, exports to CSV and JSON, and asserts the output is correct and contains all users.
- **`test_import_users_from_dicts`**: Imports users from dicts, checks they are created, and verifies by fetching from the DB.
- **`test_deactivate_and_reactivate_user`**: Creates a user, deactivates (sets is_active=False), then reactivates, and checks the flags.
- **`test_update_last_login`**: Creates a user, updates the last login timestamp, and asserts the value is set and close to the expected time.
- **`test_validate_email_and_password`**: Runs email and password validation on various cases, checks for correct error messages and validation results.

### Utilities and Edge Cases

- **`test_async_in_memory_cache`**: Tests the async in-memory cache by setting, getting, expiring, and clearing values.
- **`test_async_rate_limiter`**: Tests the async rate limiter by making allowed and disallowed calls, then waiting for the period to reset.
- **`test_error_handling_utilities`**: Tests error handling for validation errors, duplicate users, not found, and rate limiting by triggering each error and asserting the correct exception is raised.
- **`test_anonymize_user`**: Creates a user, anonymizes them (GDPR), and checks all PII is removed and flags are set.
- **`test_user_signups_per_month`**: Creates users with different creation months, aggregates signups per month, and asserts the counts are correct for each month.

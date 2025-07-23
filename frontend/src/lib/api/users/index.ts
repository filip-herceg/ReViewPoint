/**
 * Users API Module - Main Entry Point
 *
 * Provides a unified interface for all user-related API operations.
 * This module aggregates the various user sub-modules (core, exports, test-only)
 * into a single convenient API object while also providing individual access
 * to each sub-module.
 *
 * ## Structure
 * The users API is organized into three main sub-modules:
 * - `core` - Core user CRUD operations (create, read, update, delete, list)
 * - `exports` - User data export functionality (CSV exports)
 * - `testOnly` - Test-only endpoints for development and testing
 *
 * ## Usage
 *
 * ### Using the Combined API Object
 * ```typescript
 * import { usersApi } from '@/lib/api';
 *
 * // Core operations
 * const users = await usersApi.core.listUsers();
 * const user = await usersApi.core.createUser(userData);
 *
 * // Export operations
 * const csvBlob = await usersApi.exports.exportUsersCsv();
 *
 * // Test operations (development only)
 * const status = await usersApi.testOnly.testAlive();
 * ```
 *
 * ### Using Individual Sub-modules
 * ```typescript
 * import { usersCoreApi, usersExportsApi, usersTestOnlyApi } from '@/lib/api';
 *
 * // Direct access to core operations
 * const users = await usersCoreApi.listUsers();
 *
 * // Direct access to export operations
 * const csvBlob = await usersExportsApi.exportUsersCsv();
 *
 * // Direct access to test operations
 * const status = await usersTestOnlyApi.testAlive();
 * ```
 *
 * ## Complete API Reference
 *
 * ### Core Operations (usersApi.core)
 * - `createUser(userData)` - Create a new user (admin only)
 * - `listUsers(params?)` - List users with filtering and pagination
 * - `getUser(userId)` - Get specific user by ID
 * - `updateUser(userId, updateData)` - Update user information
 * - `deleteUser(userId)` - Delete user (admin only)
 *
 * ### Export Operations (usersApi.exports)
 * - `exportUsersCsv(params?)` - Export users as CSV with filtering
 * - `exportUsersFullCsv()` - Export all users as CSV
 * - `exportAlive()` - Test export service availability
 * - `exportSimple()` - Simple export test
 *
 * ### Test Operations (usersApi.testOnly) ⚠️ Development Only
 * - `testAlive()` - Test endpoint availability
 * - `createTestUser(userData)` - Create test user without validation
 * - `deleteAllUsers()` - Delete all users (DANGEROUS)
 * - `getUserCount()` - Get user count for testing
 *
 * ## Error Handling
 * All user API functions use consistent error handling:
 * - Throw errors for failed requests
 * - Log appropriate messages for debugging
 * - Return typed responses for successful requests
 *
 * ## Type Safety
 * All functions are fully typed with interfaces that match backend schemas:
 * - `User` - Complete user object
 * - `UserCreateRequest` - User creation data
 * - `UserUpdateRequest` - User update data
 * - `UserListResponse` - Paginated user list
 * - `UserSearchParams` - Search and filter parameters
 *
 * ## Security Considerations
 * - Admin privileges required for user creation and deletion
 * - Authentication required for all operations
 * - Test endpoints should be disabled in production
 * - Role-based access control enforced
 *
 * @see backend/src/api/v1/users/ for corresponding backend implementation
 */

// Users API module aggregation
// Provides unified access to all user-related APIs

export { usersCoreApi } from "./core";
export { usersExportsApi } from "./exports";
export { usersTestOnlyApi } from "./test_only_router";

// Create a combined users API object
import { usersCoreApi } from "./core";
import { usersExportsApi } from "./exports";
import { usersTestOnlyApi } from "./test_only_router";

export const usersApi = {
  ...usersCoreApi,
  exports: usersExportsApi,
  testOnly: usersTestOnlyApi,
};

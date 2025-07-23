# users/index.ts - Users API Module Entry Point

## Purpose

The `users/index.ts` file serves as the main entry point for all user-related API operations in the ReViewPoint frontend application. This module provides a unified interface that aggregates various user sub-modules (core operations, data exports, and test-only endpoints) into a single convenient API object while maintaining access to individual sub-modules for specialized use cases.

## Key Features

### Modular Architecture

- **Core Operations**: Essential user CRUD operations (create, read, update, delete, list)
- **Export Functionality**: User data export capabilities (CSV exports)
- **Test Endpoints**: Development and testing utilities (test-only operations)
- **Unified Interface**: Single API object combining all user operations
- **Individual Access**: Direct access to specialized sub-modules

### Type Safety

- **Complete TypeScript Integration**: Fully typed interfaces matching backend schemas
- **Consistent Error Handling**: Standardized error patterns across all operations
- **Request/Response Types**: Type-safe API interactions with validation

## Module Structure

### Sub-Module Organization

```typescript
export const usersApi = {
  // Core CRUD operations
  ...usersCoreApi,

  // Specialized sub-modules
  exports: usersExportsApi, // Data export operations
  testOnly: usersTestOnlyApi, // Test-only endpoints
};
```

### Individual Sub-Module Exports

```typescript
export { usersCoreApi } from "./core"; // Core user operations
export { usersExportsApi } from "./exports"; // Export functionality
export { usersTestOnlyApi } from "./test_only_router"; // Test operations
```

## API Reference

### Core Operations (usersApi.core)

#### User Management

- **`createUser(userData)`**: Create a new user account (admin only)
- **`listUsers(params?)`**: List users with filtering and pagination
- **`getUser(userId)`**: Retrieve specific user by ID
- **`updateUser(userId, updateData)`**: Update user information
- **`deleteUser(userId)`**: Delete user account (admin only)

#### Search and Filtering

- **Advanced Search**: Search users with multiple filter criteria
- **Pagination Support**: Configurable pagination for large user sets
- **Date Filtering**: Filter users by creation date ranges
- **Role-Based Access**: Respect user permissions and roles

### Export Operations (usersApi.exports)

#### Data Export Functions

- **`exportUsersCsv(params?)`**: Export filtered users as CSV
- **`exportUsersFullCsv()`**: Export all users as CSV
- **`exportAlive()`**: Test export service availability
- **`exportSimple()`**: Simple export functionality test

#### Export Features

- **Filtering Support**: Apply same filters as user listing
- **Custom Fields**: Select specific fields for export
- **Format Options**: Multiple export formats available
- **Streaming Support**: Efficient handling of large datasets

### Test Operations (usersApi.testOnly) ⚠️ Development Only

#### Test Utilities

- **`testAlive()`**: Test endpoint availability
- **`createTestUser(userData)`**: Create test user without validation
- **`deleteAllUsers()`**: Delete all users (DANGEROUS - test only)
- **`getUserCount()`**: Get total user count for testing

#### Security Warnings

- **Production Disabled**: Test endpoints should be disabled in production
- **Destructive Operations**: Some operations permanently delete data
- **No Validation**: Test user creation bypasses normal validation
- **Admin Required**: Test operations require administrative privileges

## Usage Examples

### Combined API Object Usage

```typescript
import { usersApi } from "@/lib/api";

// Core user operations
async function manageUsers() {
  try {
    // List users with pagination and filtering
    const userList = await usersApi.listUsers({
      limit: 20,
      offset: 0,
      email: "search@example.com",
      created_after: "2024-01-01T00:00:00Z",
    });

    console.log("Users found:", userList.users.length);
    console.log("Total users:", userList.total);

    // Get specific user
    const user = await usersApi.getUser(userList.users[0].id);
    console.log("User details:", user);

    // Update user
    const updatedUser = await usersApi.updateUser(user.id, {
      name: "Updated Name",
    });
    console.log("User updated:", updatedUser);
  } catch (error) {
    console.error("User operation failed:", error.message);
  }
}

// Export operations
async function exportUserData() {
  try {
    // Export filtered users as CSV
    const csvBlob = await usersApi.exports.exportUsersCsv({
      created_after: "2024-01-01T00:00:00Z",
      limit: 1000,
    });

    // Download CSV file
    const url = URL.createObjectURL(csvBlob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "users-export.csv";
    link.click();
    URL.revokeObjectURL(url);
  } catch (error) {
    console.error("Export failed:", error.message);
  }
}
```

### Individual Sub-Module Usage

```typescript
import { usersCoreApi, usersExportsApi, usersTestOnlyApi } from "@/lib/api";

// Direct core operations
async function coreUserOperations() {
  const users = await usersCoreApi.listUsers();
  const newUser = await usersCoreApi.createUser({
    email: "user@example.com",
    name: "New User",
    password: "securePassword123",
  });
}

// Direct export operations
async function exportOperations() {
  const csvData = await usersExportsApi.exportUsersCsv();
  const availability = await usersExportsApi.exportAlive();
}

// Test operations (development only)
async function testOperations() {
  if (process.env.NODE_ENV === "development") {
    const status = await usersTestOnlyApi.testAlive();
    const testUser = await usersTestOnlyApi.createTestUser({
      email: "test@example.com",
      name: "Test User",
    });
  }
}
```

### Admin User Creation

```typescript
import { usersApi } from "@/lib/api";

async function createAdminUser() {
  try {
    const adminUserData = {
      email: "admin@reviewpoint.com",
      name: "Administrator",
      password: "secureAdminPassword123",
      role: "admin",
      permissions: ["user_management", "system_admin"],
    };

    const newAdmin = await usersApi.createUser(adminUserData);

    console.log("Admin user created:", newAdmin.id);
    console.log("Admin permissions:", newAdmin.permissions);

    return newAdmin;
  } catch (error) {
    if (error.message.includes("insufficient permissions")) {
      console.error("Admin privileges required for user creation");
    } else if (error.message.includes("email already exists")) {
      console.error("User with this email already exists");
    } else {
      console.error("Admin creation failed:", error.message);
    }
    throw error;
  }
}
```

### Advanced User Search

```typescript
import { usersApi } from "@/lib/api";

async function advancedUserSearch() {
  try {
    const searchParams = {
      // Text search
      email: "domain.com", // Email contains domain.com
      name: "John", // Name contains John

      // Date filtering
      created_after: "2024-01-01T00:00:00Z",
      created_before: "2024-12-31T23:59:59Z",

      // Pagination
      limit: 50,
      offset: 0,

      // Sorting
      sort_by: "created_at",
      sort_order: "desc",
    };

    const searchResults = await usersApi.listUsers(searchParams);

    console.log(`Found ${searchResults.users.length} users`);
    console.log(`Total matching users: ${searchResults.total}`);

    return searchResults;
  } catch (error) {
    console.error("User search failed:", error.message);
    throw error;
  }
}
```

## Error Handling

### Consistent Error Patterns

All user API functions follow standardized error handling:

```typescript
try {
  const result = await usersApi.someOperation();
  // Handle success
} catch (error) {
  // Error types and handling
  if (error.message.includes("401")) {
    // Authentication required
    redirectToLogin();
  } else if (error.message.includes("403")) {
    // Insufficient permissions
    showPermissionError();
  } else if (error.message.includes("404")) {
    // User not found
    showUserNotFoundError();
  } else if (error.message.includes("409")) {
    // Conflict (e.g., email already exists)
    showConflictError(error.message);
  } else {
    // Generic error handling
    showGenericError(error.message);
  }
}
```

### Error Categories

- **Authentication Errors (401)**: User not logged in
- **Authorization Errors (403)**: Insufficient permissions
- **Not Found Errors (404)**: User does not exist
- **Conflict Errors (409)**: Duplicate email or username
- **Validation Errors (422)**: Invalid input data
- **Server Errors (5xx)**: Backend issues

## Type Definitions

### Core Types

```typescript
// User object structure
interface User {
  id: string;
  email: string;
  name: string;
  role: "user" | "admin";
  permissions: string[];
  created_at: string;
  updated_at: string;
  last_login?: string;
  is_active: boolean;
}

// User creation request
interface UserCreateRequest {
  email: string;
  name: string;
  password: string;
  role?: "user" | "admin";
  permissions?: string[];
}

// User update request
interface UserUpdateRequest {
  name?: string;
  email?: string;
  role?: "user" | "admin";
  permissions?: string[];
  is_active?: boolean;
}

// User list response
interface UserListResponse {
  users: User[];
  total: number;
  limit: number;
  offset: number;
}

// Search parameters
interface UserSearchParams {
  email?: string;
  name?: string;
  role?: "user" | "admin";
  created_after?: string;
  created_before?: string;
  is_active?: boolean;
  limit?: number;
  offset?: number;
  sort_by?: "created_at" | "name" | "email";
  sort_order?: "asc" | "desc";
}
```

## Security Considerations

### Access Control

- **Admin Privileges**: User creation and deletion require admin role
- **Authentication Required**: All operations require valid JWT token
- **Role-Based Access**: Operations respect user role and permissions
- **Audit Logging**: All operations are logged for security tracking

### Data Protection

- **Password Security**: Passwords never returned in API responses
- **Input Validation**: All input data validated before processing
- **SQL Injection Prevention**: Parameterized queries protect against injection
- **Rate Limiting**: API endpoints protected against abuse

### Production Safety

- **Test Endpoint Isolation**: Test endpoints disabled in production
- **Destructive Operation Protection**: Dangerous operations require confirmation
- **Error Message Security**: Error messages don't expose sensitive information
- **Session Management**: Proper session handling and cleanup

## Integration Points

### Backend Endpoints

This module integrates with the following backend endpoints:

- `POST /api/v1/users` - User creation (core.py)
- `GET /api/v1/users` - User listing (core.py)
- `GET /api/v1/users/{user_id}` - User retrieval (core.py)
- `PUT /api/v1/users/{user_id}` - User updates (core.py)
- `DELETE /api/v1/users/{user_id}` - User deletion (core.py)
- `GET /api/v1/users/exports/csv` - CSV export (exports.py)
- `GET /api/v1/users/test-only/*` - Test endpoints (test_only_router.py)

### State Management Integration

```typescript
// Zustand store integration
import { create } from "zustand";
import { usersApi } from "@/lib/api";

const useUserStore = create((set, get) => ({
  users: [],
  currentUser: null,
  loading: false,
  error: null,

  loadUsers: async (params) => {
    set({ loading: true, error: null });
    try {
      const response = await usersApi.listUsers(params);
      set({ users: response.users, loading: false });
      return response;
    } catch (error) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  createUser: async (userData) => {
    set({ loading: true, error: null });
    try {
      const newUser = await usersApi.createUser(userData);
      set((state) => ({
        users: [...state.users, newUser],
        loading: false,
      }));
      return newUser;
    } catch (error) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },
}));
```

## Dependencies

### External Dependencies

- **@/lib/api/types**: TypeScript type definitions for user operations
- **@/lib/api/base**: Base HTTP client for API communication
- **@/logger**: Application logging service for debugging

### Internal Dependencies

- **./core**: Core user CRUD operations module
- **./exports**: User data export functionality module
- **./test_only_router**: Test-only endpoints module

## Related Files

- **[core.ts](core.ts.md)**: Core user CRUD operations implementation
- **[exports.ts](exports.ts.md)**: User data export functionality
- **[test_only_router.ts](test_only_router.ts.md)**: Test-only endpoints
- **[types/user.ts](../types/user.ts.md)**: User type definitions
- **[auth.ts](../auth.ts.md)**: Authentication API integration
- **Backend**: `backend/src/api/v1/users/` - corresponding backend implementation

## Best Practices

### API Usage Patterns

- **Error Handling**: Always wrap API calls in try-catch blocks
- **Type Safety**: Use TypeScript types for all operations
- **Pagination**: Handle pagination properly for large user sets
- **Loading States**: Implement proper loading indicators

### Performance Optimization

- **Efficient Queries**: Use filtering to reduce data transfer
- **Caching**: Implement intelligent caching for frequently accessed data
- **Batch Operations**: Group multiple operations when possible
- **Lazy Loading**: Load user data on demand

### Security Best Practices

- **Input Validation**: Validate all user input before API calls
- **Permission Checks**: Verify user permissions before sensitive operations
- **Secure Storage**: Never store sensitive data in local storage
- **Audit Trails**: Log all administrative operations for security tracking

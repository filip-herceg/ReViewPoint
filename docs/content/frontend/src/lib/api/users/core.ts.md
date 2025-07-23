# users/core.ts - Users Core API Module

## Purpose

The `users/core.ts` file provides the core user management functionality for the ReViewPoint application. This module serves as the primary interface for user CRUD (Create, Read, Update, Delete) operations, directly mirroring the backend user core endpoints while providing a consistent TypeScript interface for user management, search, and administrative operations.

## Key Features

### Core User Operations

- **User Creation**: Create new user accounts (admin-only operation)
- **User Listing**: Retrieve paginated lists of users with filtering
- **User Retrieval**: Get specific users by ID
- **User Updates**: Modify existing user information
- **User Deletion**: Remove users from the system (admin-only operation)

### Advanced Functionality

- **Search and Filtering**: Advanced user search with multiple criteria
- **Pagination Support**: Efficient handling of large user datasets
- **Date Filtering**: Filter users by creation timestamps
- **Type Safety**: Complete TypeScript integration with validation

## API Functions

### User Creation (`createUser`)

Creates a new user account in the system. This operation requires administrative privileges.

```typescript
async function createUser(userData: UserCreateRequest): Promise<User>;
```

**Parameters:**

- `userData: UserCreateRequest` - User creation data including email, name, and password

**Returns:**

- `Promise<User>` - Created user object with generated ID and timestamps

**Example Usage:**

```typescript
import { usersCoreApi } from "@/lib/api";

async function createNewUser() {
  try {
    const userData = {
      email: "newuser@example.com",
      name: "New User",
      password: "securePassword123",
    };

    const user = await usersCoreApi.createUser(userData);
    console.log("User created:", user.id, user.email);
    return user;
  } catch (error) {
    if (error.message.includes("403")) {
      console.error("Admin privileges required for user creation");
    } else if (error.message.includes("409")) {
      console.error("User with this email already exists");
    } else {
      console.error("User creation failed:", error.message);
    }
    throw error;
  }
}
```

### User Listing (`listUsers`)

Retrieves a paginated list of users with optional filtering parameters.

```typescript
async function listUsers(params?: UserSearchParams): Promise<UserListResponse>;
```

**Parameters:**

- `params?: UserSearchParams` - Optional search and pagination parameters

**Returns:**

- `Promise<UserListResponse>` - Object containing users array and total count

**Example Usage:**

```typescript
async function getUserList() {
  try {
    // Basic listing
    const allUsers = await usersCoreApi.listUsers();

    // Advanced filtering with pagination
    const filteredUsers = await usersCoreApi.listUsers({
      limit: 20,
      offset: 0,
      email: "domain.com",
      name: "John",
      created_after: "2024-01-01T00:00:00Z",
    });

    console.log(`Found ${filteredUsers.users.length} users`);
    console.log(`Total users matching criteria: ${filteredUsers.total}`);

    return filteredUsers;
  } catch (error) {
    console.error("Failed to list users:", error.message);
    throw error;
  }
}
```

### User Retrieval (`getUserById`)

Retrieves a specific user by their unique identifier.

```typescript
async function getUserById(userId: number): Promise<User>;
```

**Parameters:**

- `userId: number` - Unique user identifier

**Returns:**

- `Promise<User>` - Complete user object with all available fields

**Example Usage:**

```typescript
async function getSpecificUser(userId: number) {
  try {
    const user = await usersCoreApi.getUserById(userId);
    console.log("User details:", {
      id: user.id,
      email: user.email,
      name: user.name,
      created: user.created_at,
    });
    return user;
  } catch (error) {
    if (error.message.includes("404")) {
      console.error("User not found:", userId);
    } else if (error.message.includes("403")) {
      console.error("Access denied to user:", userId);
    } else {
      console.error("Failed to get user:", error.message);
    }
    throw error;
  }
}
```

### User Updates (`updateUser`)

Updates existing user information with new data.

```typescript
async function updateUser(
  userId: number,
  userData: UserCreateRequest,
): Promise<User>;
```

**Parameters:**

- `userId: number` - Unique user identifier
- `userData: UserCreateRequest` - Updated user data

**Returns:**

- `Promise<User>` - Updated user object with new values

**Example Usage:**

```typescript
async function updateUserInfo(userId: number) {
  try {
    const updateData = {
      name: "Updated Name",
      email: "updated@example.com",
      password: "newSecurePassword123",
    };

    const updatedUser = await usersCoreApi.updateUser(userId, updateData);
    console.log("User updated successfully:", updatedUser.id);
    return updatedUser;
  } catch (error) {
    if (error.message.includes("404")) {
      console.error("User not found for update:", userId);
    } else if (error.message.includes("409")) {
      console.error("Email already exists for another user");
    } else if (error.message.includes("403")) {
      console.error("Insufficient permissions to update user");
    } else {
      console.error("User update failed:", error.message);
    }
    throw error;
  }
}
```

### User Deletion (`deleteUser`)

Permanently removes a user from the system. This operation requires administrative privileges.

```typescript
async function deleteUser(userId: number): Promise<void>;
```

**Parameters:**

- `userId: number` - Unique user identifier

**Returns:**

- `Promise<void>` - No return value on successful deletion

**Example Usage:**

```typescript
async function removeUser(userId: number) {
  try {
    await usersCoreApi.deleteUser(userId);
    console.log("User deleted successfully:", userId);
  } catch (error) {
    if (error.message.includes("404")) {
      console.error("User not found for deletion:", userId);
    } else if (error.message.includes("403")) {
      console.error("Admin privileges required for user deletion");
    } else if (error.message.includes("409")) {
      console.error("Cannot delete user with active dependencies");
    } else {
      console.error("User deletion failed:", error.message);
    }
    throw error;
  }
}
```

## Type Definitions

### Core User Interface

```typescript
interface User {
  id: number; // Unique user identifier
  email: string; // User's email address (unique)
  name: string; // User's display name
  bio?: string; // Optional user biography
  avatar_url?: string; // Optional avatar image URL
  created_at?: string; // ISO timestamp of user creation
  updated_at?: string; // ISO timestamp of last update
}
```

### User Creation Request

```typescript
interface UserCreateRequest {
  email: string; // Valid email address (required)
  name: string; // User's display name (required)
  password: string; // Secure password (required)
}
```

### User List Response

```typescript
interface UserListResponse {
  users: User[]; // Array of user objects
  total: number; // Total number of users matching criteria
}
```

### Search Parameters

```typescript
interface UserSearchParams {
  offset?: number; // Number of users to skip (pagination)
  limit?: number; // Maximum number of users to return
  email?: string; // Filter by email address (exact match)
  name?: string; // Filter by name (partial match)
  created_after?: string; // Filter by creation date (ISO string)
}
```

## Advanced Usage Examples

### Comprehensive User Management System

```typescript
import { usersCoreApi } from "@/lib/api";

class UserManager {
  // Create multiple users with validation
  async createUsersFromData(usersData: UserCreateRequest[]): Promise<User[]> {
    const createdUsers: User[] = [];
    const errors: string[] = [];

    for (const userData of usersData) {
      try {
        const user = await usersCoreApi.createUser(userData);
        createdUsers.push(user);
        console.log(`Created user: ${user.email}`);
      } catch (error) {
        errors.push(`Failed to create ${userData.email}: ${error.message}`);
      }
    }

    if (errors.length > 0) {
      console.warn("Some users failed to create:", errors);
    }

    return createdUsers;
  }

  // Paginated user listing with search
  async searchUsers(
    searchTerm: string,
    page: number = 0,
    pageSize: number = 20,
  ) {
    try {
      const searchParams = {
        offset: page * pageSize,
        limit: pageSize,
        name: searchTerm,
        email: searchTerm, // Note: Backend may support OR search
      };

      const response = await usersCoreApi.listUsers(searchParams);

      return {
        users: response.users,
        total: response.total,
        page,
        pageSize,
        totalPages: Math.ceil(response.total / pageSize),
        hasNext: (page + 1) * pageSize < response.total,
        hasPrev: page > 0,
      };
    } catch (error) {
      console.error("User search failed:", error.message);
      throw error;
    }
  }

  // Bulk user operations
  async deleteMultipleUsers(
    userIds: number[],
  ): Promise<{ success: number[]; failed: number[] }> {
    const success: number[] = [];
    const failed: number[] = [];

    for (const userId of userIds) {
      try {
        await usersCoreApi.deleteUser(userId);
        success.push(userId);
      } catch (error) {
        failed.push(userId);
        console.error(`Failed to delete user ${userId}:`, error.message);
      }
    }

    return { success, failed };
  }

  // User data synchronization
  async syncUserData(userId: number, externalData: Partial<UserCreateRequest>) {
    try {
      const currentUser = await usersCoreApi.getUserById(userId);

      const updateData: UserCreateRequest = {
        email: externalData.email || currentUser.email,
        name: externalData.name || currentUser.name,
        password: externalData.password || "keepExisting", // Backend may handle this
      };

      const updatedUser = await usersCoreApi.updateUser(userId, updateData);
      console.log("User data synchronized:", updatedUser.id);
      return updatedUser;
    } catch (error) {
      console.error("User sync failed:", error.message);
      throw error;
    }
  }
}
```

### Date-Based User Analytics

```typescript
async function analyzeUserRegistrations() {
  try {
    // Get users from different time periods
    const lastWeek = new Date();
    lastWeek.setDate(lastWeek.getDate() - 7);

    const lastMonth = new Date();
    lastMonth.setMonth(lastMonth.getMonth() - 1);

    const [recentUsers, olderUsers] = await Promise.all([
      usersCoreApi.listUsers({
        created_after: lastWeek.toISOString(),
        limit: 1000,
      }),
      usersCoreApi.listUsers({
        created_after: lastMonth.toISOString(),
        limit: 1000,
      }),
    ]);

    const analytics = {
      recentRegistrations: recentUsers.users.length,
      totalRecentUsers: recentUsers.total,
      monthlyRegistrations: olderUsers.users.length,
      totalMonthlyUsers: olderUsers.total,
      growthRate:
        ((recentUsers.total - olderUsers.total) / olderUsers.total) * 100,
    };

    console.log("User analytics:", analytics);
    return analytics;
  } catch (error) {
    console.error("Analytics generation failed:", error.message);
    throw error;
  }
}
```

## Error Handling Patterns

### Comprehensive Error Management

```typescript
class UserApiErrorHandler {
  static handleUserCreationError(error: Error): string {
    if (error.message.includes("403")) {
      return "Administrative privileges required to create users";
    } else if (error.message.includes("409")) {
      return "A user with this email address already exists";
    } else if (error.message.includes("422")) {
      return "Invalid user data provided. Please check email format and password requirements";
    } else if (error.message.includes("500")) {
      return "Server error occurred during user creation. Please try again later";
    }
    return `User creation failed: ${error.message}`;
  }

  static handleUserRetrievalError(error: Error, userId?: number): string {
    if (error.message.includes("404")) {
      return userId ? `User with ID ${userId} not found` : "User not found";
    } else if (error.message.includes("403")) {
      return "Access denied. Insufficient permissions to view user data";
    } else if (error.message.includes("401")) {
      return "Authentication required. Please log in to view user data";
    }
    return `Failed to retrieve user: ${error.message}`;
  }

  static handleUserUpdateError(error: Error, userId: number): string {
    if (error.message.includes("404")) {
      return `User with ID ${userId} not found for update`;
    } else if (error.message.includes("409")) {
      return "Email address already exists for another user";
    } else if (error.message.includes("403")) {
      return "Insufficient permissions to update user";
    } else if (error.message.includes("422")) {
      return "Invalid update data provided";
    }
    return `User update failed: ${error.message}`;
  }

  static handleUserDeletionError(error: Error, userId: number): string {
    if (error.message.includes("404")) {
      return `User with ID ${userId} not found for deletion`;
    } else if (error.message.includes("403")) {
      return "Administrative privileges required to delete users";
    } else if (error.message.includes("409")) {
      return "Cannot delete user with active dependencies (uploads, reviews, etc.)";
    }
    return `User deletion failed: ${error.message}`;
  }
}

// Usage in application code
async function safeUserOperation() {
  try {
    const user = await usersCoreApi.createUser({
      email: "test@example.com",
      name: "Test User",
      password: "securePass123",
    });
    return user;
  } catch (error) {
    const userMessage = UserApiErrorHandler.handleUserCreationError(error);
    console.error(userMessage);
    throw new Error(userMessage);
  }
}
```

## Logging and Monitoring

### Integrated Logging

The module includes comprehensive logging for all operations:

```typescript
// Example logging output for user operations
logger.info("Creating user", { email: userData.email });
logger.warn("User creation failed", {
  error: response.error,
  email: userData.email,
});
logger.info("User created successfully", {
  id: response.data?.id,
  email: response.data?.email,
});

logger.info("Fetching users list", { params });
logger.info("Users fetched successfully", {
  total: response.data?.total,
  count: response.data?.users.length,
});

logger.info("Updating user", { userId, email: userData.email });
logger.warn("User update failed", { error: response.error, userId });
logger.info("User updated successfully", {
  id: response.data?.id,
  email: response.data?.email,
});
```

### Monitoring Integration

```typescript
// Custom monitoring wrapper
function withMonitoring<T extends any[], R>(
  func: (...args: T) => Promise<R>,
  operationName: string,
) {
  return async (...args: T): Promise<R> => {
    const startTime = Date.now();
    try {
      const result = await func(...args);
      const duration = Date.now() - startTime;
      console.log(`${operationName} completed in ${duration}ms`);
      return result;
    } catch (error) {
      const duration = Date.now() - startTime;
      console.error(
        `${operationName} failed after ${duration}ms:`,
        error.message,
      );
      throw error;
    }
  };
}

// Monitored API functions
export const monitoredUsersCoreApi = {
  createUser: withMonitoring(usersCoreApi.createUser, "createUser"),
  listUsers: withMonitoring(usersCoreApi.listUsers, "listUsers"),
  getUserById: withMonitoring(usersCoreApi.getUserById, "getUserById"),
  updateUser: withMonitoring(usersCoreApi.updateUser, "updateUser"),
  deleteUser: withMonitoring(usersCoreApi.deleteUser, "deleteUser"),
};
```

## Security Considerations

### Access Control

- **Admin-Only Operations**: User creation and deletion require administrative privileges
- **Authentication Required**: All operations require valid JWT authentication token
- **Permission Validation**: Backend validates user permissions before executing operations
- **Role-Based Access**: Different user roles have different access levels

### Data Protection

- **Input Validation**: All user input is validated before sending to backend
- **Password Security**: Passwords are never returned in API responses
- **Email Uniqueness**: System enforces unique email addresses
- **SQL Injection Prevention**: Backend uses parameterized queries

### Audit and Compliance

- **Operation Logging**: All user operations are logged with user context
- **Error Tracking**: Failed operations are tracked for security monitoring
- **Data Privacy**: User data access is logged and controlled
- **Session Management**: Proper session handling and token validation

## Backend Integration

### Corresponding Backend Endpoints

This module integrates with the following backend endpoints in `backend/src/api/v1/users/core.py`:

- `POST /api/v1/users` - User creation endpoint
- `GET /api/v1/users` - User listing with filtering
- `GET /api/v1/users/{user_id}` - Individual user retrieval
- `PUT /api/v1/users/{user_id}` - User information updates
- `DELETE /api/v1/users/{user_id}` - User deletion

### Data Synchronization

- **Type Consistency**: Frontend types match backend data models
- **Validation Alignment**: Frontend validation mirrors backend rules
- **Error Code Mapping**: Error responses are consistently handled
- **Schema Compatibility**: API requests/responses follow OpenAPI schema

## Dependencies

### External Dependencies

- **@/logger**: Application logging service for operation tracking
- **../base**: Base HTTP client providing the `request` function
- **TypeScript**: Type safety and interface definitions

### Related Modules

- **users/index.ts**: Main entry point that exports this module
- **users/exports.ts**: User data export functionality
- **users/test_only_router.ts**: Test-only endpoints
- **auth.ts**: Authentication API for user session management

## Performance Considerations

### Efficient Data Handling

- **Pagination Support**: Large user lists are handled with offset/limit pagination
- **Selective Loading**: Only required user fields are transmitted
- **Response Caching**: Consider implementing caching for frequently accessed user data
- **Batch Operations**: Multiple operations can be optimized with proper batching

### Optimization Strategies

- **Lazy Loading**: Load user details on demand rather than with initial list
- **Search Debouncing**: Implement debouncing for real-time user search
- **Memory Management**: Properly cleanup large user datasets
- **Network Efficiency**: Minimize API calls with intelligent data management

## Testing Considerations

### Unit Testing

```typescript
// Example test structure for user core operations
describe("usersCoreApi", () => {
  beforeEach(() => {
    // Mock the request function
    jest.mock("../base");
  });

  describe("createUser", () => {
    it("should create user successfully", async () => {
      const mockUser = { id: 1, email: "test@example.com", name: "Test User" };
      mockRequest.mockResolvedValue({ data: mockUser, error: null });

      const result = await usersCoreApi.createUser({
        email: "test@example.com",
        name: "Test User",
        password: "password123",
      });

      expect(result).toEqual(mockUser);
    });

    it("should handle creation errors", async () => {
      mockRequest.mockResolvedValue({
        data: null,
        error: "Email already exists",
      });

      await expect(
        usersCoreApi.createUser({
          email: "test@example.com",
          name: "Test User",
          password: "password123",
        }),
      ).rejects.toThrow("Email already exists");
    });
  });
});
```

## Related Files

- **[users/index.ts](index.ts.md)**: Main users API module entry point
- **[users/exports.ts](exports.ts.md)**: User data export functionality
- **[users/test_only_router.ts](test_only_router.ts.md)**: Test-only endpoints
- **[types/index.ts](../types/index.ts.md)**: Type definitions for user operations
- **[base.ts](../base.ts.md)**: Base HTTP client functionality
- **Backend**: `backend/src/api/v1/users/core.py` - corresponding backend implementation

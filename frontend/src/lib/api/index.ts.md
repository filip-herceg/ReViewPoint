# index.ts - Main API Entry Point

## Purpose

The `index.ts` file serves as the central entry point and orchestration layer for the entire ReViewPoint frontend API system. It provides a unified interface that aggregates all API modules (authentication, user management, file uploads, health checks) and establishes both named exports for modern usage and a default export for backwards compatibility. This module acts as the primary interface between the frontend application and the backend API services.

## Key Components

### Primary Exports

- **Named Module Exports** - Individual API modules (`authApi`, `usersApi`, `uploadsApi`, `healthApi`)
- **Utility Exports** - Base request function and generated clients
- **Legacy Compatibility** - Flattened default export for backwards compatibility
- **Type Integration** - Seamless integration with the comprehensive type system

### API Module Structure

The module organizes APIs to mirror the backend router structure:

- `auth` - Authentication and authorization endpoints
- `health` - Health check and system status endpoints
- `uploads` - File upload and management endpoints
- `users` - User management endpoints (core, exports, test-only)

## Named Exports Architecture

### Authentication API

```typescript
export { authApi } from "./auth";

// Usage
import { authApi } from "@/lib/api";

const user = await authApi.login({ email, password });
const current = await authApi.getCurrentUser();
const tokens = await authApi.refreshToken();
await authApi.logout();
```

**Authentication Operations:**

- User login and registration
- JWT token management and refresh
- Password reset workflows
- User session management
- Current user retrieval

### User Management API

```typescript
export { usersApi } from "./users";
export { usersCoreApi } from "./users/core";
export { usersExportsApi } from "./users/exports";
export { usersTestOnlyApi } from "./users/test_only_router";

// Usage
import { usersApi } from "@/lib/api";

const users = await usersApi.core.listUsers();
const user = await usersApi.core.createUser(userData);
const updated = await usersApi.core.updateUser(id, updates);
```

**User Management Features:**

- **Core Operations**: CRUD operations for user management
- **Data Exports**: User data export functionality
- **Test Utilities**: Testing-specific user operations
- **Profile Management**: User preferences and profile updates

### File Upload API

```typescript
export { uploadsApi, createUpload } from "./uploads";
export { uploadApiClient } from "./clients/uploads";

// Usage
import { uploadsApi } from "@/lib/api";

const files = await uploadsApi.listFiles();
const result = await uploadsApi.uploadFile(file);
const deleted = await uploadsApi.deleteFile(fileId);
```

**Upload Operations:**

- File upload with progress tracking
- File listing and search
- File download and deletion
- Bulk file operations
- Upload status management

### Health Check API

```typescript
export { healthApi } from "./health";

// Usage
import { healthApi } from "@/lib/api";

const status = await healthApi.getHealthStatus();
const detailed = await healthApi.getDetailedHealth();
```

**Health Monitoring:**

- System health status checks
- Service availability monitoring
- Performance metrics retrieval
- Error rate monitoring

### Base Utilities

```typescript
export { request } from "./base";
export { generatedApiClient } from "./generated/client";

// Usage
import { request } from "@/lib/api";

const response = await request<CustomType>("/api/custom/endpoint");
```

**Utility Features:**

- Generic HTTP request wrapper
- Generated API clients from OpenAPI schemas
- Type-safe request/response handling
- Comprehensive error management

## Default Export (Backwards Compatibility)

### Flattened API Interface

```typescript
const api = {
  ...authApi,
  ...uploadsApi,
  ...usersApi,
  ...healthApi,
  createUpload,
};

export default api;
```

**Legacy Usage Pattern:**

```typescript
import api from "@/lib/api";

// All APIs available as flat methods
const user = await api.login({ email, password });
const files = await api.listFiles();
const users = await api.listUsers();
const status = await api.getHealthStatus();
```

**Backwards Compatibility Benefits:**

- Seamless migration for existing code
- No breaking changes for legacy implementations
- Maintains existing developer workflows
- Gradual migration path to named exports

## Usage Examples

### Modern Named Exports (Recommended)

```typescript
import { authApi, usersApi, uploadsApi, healthApi } from "@/lib/api";
import type { User, AuthTokens, FileListResponse } from "@/lib/api/types";

class ApiService {
  // Authentication
  async authenticateUser(email: string, password: string): Promise<User> {
    const response = await authApi.login({ email, password });
    return response.user;
  }

  // User Management
  async fetchUsers(page: number = 1): Promise<User[]> {
    const response = await usersApi.core.listUsers({ page, per_page: 20 });
    return response.items;
  }

  // File Operations
  async uploadFile(file: File): Promise<string> {
    const response = await uploadsApi.uploadFile(file);
    return response.file_id;
  }

  // Health Monitoring
  async checkSystemHealth(): Promise<boolean> {
    const response = await healthApi.getHealthStatus();
    return response.status === "healthy";
  }
}
```

### Specialized Module Usage

```typescript
import { usersCoreApi, usersExportsApi } from "@/lib/api";
import type { UserExportParams } from "@/lib/api/types";

class UserManagementService {
  // Core user operations
  async createUser(userData: UserCreateRequest): Promise<User> {
    return await usersCoreApi.createUser(userData);
  }

  // Export operations
  async exportUserData(params: UserExportParams): Promise<Blob> {
    return await usersExportsApi.exportUsers(params);
  }
}
```

### Error Handling Patterns

```typescript
import { authApi, usersApi } from "@/lib/api";
import type { ApiError } from "@/lib/api/types";

class ErrorHandlingService {
  async safeLogin(credentials: LoginCredentials): Promise<User | null> {
    try {
      const response = await authApi.login(credentials);
      return response.user;
    } catch (error) {
      if (error instanceof Error) {
        console.error("Login failed:", error.message);
        // Handle specific error types
        if (error.message.includes("Invalid credentials")) {
          throw new Error("Please check your email and password");
        }
      }
      return null;
    }
  }

  async safeUserOperation<T>(operation: () => Promise<T>): Promise<T | null> {
    try {
      return await operation();
    } catch (error) {
      console.error("User operation failed:", error);
      return null;
    }
  }
}
```

### React Component Integration

```typescript
import { authApi, usersApi } from '@/lib/api';
import type { User } from '@/lib/api/types';
import { useState, useEffect } from 'react';

function UserDashboard() {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        // Load current user
        const current = await authApi.getCurrentUser();
        setCurrentUser(current);

        // Load user list if admin
        if (current.is_admin) {
          const userList = await usersApi.core.listUsers();
          setUsers(userList.items);
        }
      } catch (error) {
        console.error('Failed to load data:', error);
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h1>Welcome, {currentUser?.display_name}</h1>
      {users.length > 0 && (
        <UserList users={users} />
      )}
    </div>
  );
}
```

## Type Safety Integration

### Comprehensive Type Support

```typescript
import type {
  User,
  AuthTokens,
  FileListResponse,
  ApiResponse,
  PaginatedResponse,
} from "@/lib/api/types";

// All API functions are fully typed
const login: (
  credentials: AuthLoginRequest,
) => Promise<ApiResponse<AuthTokens>>;
const listUsers: (
  params?: PaginationParams,
) => Promise<ApiResponse<PaginatedResponse<User>>>;
const uploadFile: (file: File) => Promise<ApiResponse<FileUploadResponse>>;
```

### Type-Safe Error Handling

```typescript
import { authApi } from "@/lib/api";
import type { ApiError, AuthError } from "@/lib/api/types";

async function handleAuthOperation(): Promise<void> {
  try {
    await authApi.login({ email: "user@example.com", password: "password" });
  } catch (error) {
    // Error is properly typed
    if (error instanceof Error) {
      console.error("Auth error:", error.message);
    }
  }
}
```

## API Organization Patterns

### Module-Based Organization

The API follows a clear module-based organization that mirrors the backend structure:

```typescript
// Authentication Module
authApi = {
  login,
  register,
  logout,
  refreshToken,
  forgotPassword,
  resetPassword,
  getCurrentUser,
};

// Users Module (with sub-modules)
usersApi = {
  core: { listUsers, createUser, updateUser, deleteUser },
  exports: { exportUsers, getExportStatus },
  testOnly: { promoteAdmin, demoteAdmin },
};

// Uploads Module
uploadsApi = {
  listFiles,
  uploadFile,
  downloadFile,
  deleteFile,
  searchFiles,
};

// Health Module
healthApi = {
  getHealthStatus,
  getDetailedHealth,
  checkDependencies,
};
```

### Consistent Interface Patterns

All API modules follow consistent patterns:

```typescript
// Standard response format
interface StandardResponse<T> {
  data: T | null;
  error?: string;
}

// Pagination support
interface PaginatedRequest {
  page?: number;
  per_page?: number;
}

// Error handling
interface ErrorResponse {
  message: string;
  field_errors?: FieldError[];
}
```

## Advanced Usage Patterns

### Custom API Clients

```typescript
import { request } from "@/lib/api";
import type { ApiResponse } from "@/lib/api/types";

class CustomApiClient {
  async customEndpoint<T>(data: unknown): Promise<ApiResponse<T>> {
    return await request<T>("/api/custom/endpoint", {
      method: "POST",
      data,
    });
  }
}
```

### API Composition

```typescript
import { authApi, usersApi, uploadsApi } from "@/lib/api";

class CompositeApiService {
  async setupNewUser(userData: UserCreateRequest, avatarFile?: File) {
    // Create user
    const user = await usersApi.core.createUser(userData);

    // Upload avatar if provided
    if (avatarFile) {
      await uploadsApi.uploadFile(avatarFile);
    }

    // Return complete user data
    return user;
  }
}
```

### Middleware Integration

```typescript
import { authApi } from "@/lib/api";

// Add request logging
const originalLogin = authApi.login;
authApi.login = async (credentials) => {
  console.log("Attempting login for:", credentials.email);
  const result = await originalLogin(credentials);
  console.log("Login successful for:", credentials.email);
  return result;
};
```

## Performance Considerations

### Efficient Module Loading

- **Named Exports**: Enable tree shaking for unused modules
- **Selective Imports**: Import only needed API functions
- **Code Splitting**: Supports dynamic imports for large modules

```typescript
// Tree-shakeable imports
import { authApi } from "@/lib/api"; // Only auth module loaded

// Dynamic imports for performance
const { uploadsApi } = await import("@/lib/api");
```

### Request Optimization

- **Connection Reuse**: Single axios instance across all modules
- **Request Deduplication**: Automatic handling of duplicate requests
- **Caching Integration**: Compatible with React Query and SWR

### Bundle Size Management

- **Modular Architecture**: Individual modules can be loaded on demand
- **Type-Only Imports**: Type definitions don't increase bundle size
- **Utility Functions**: Shared utilities minimize code duplication

## Development Workflow Integration

### Hot Reload Support

```typescript
// Development-only features
if (process.env.NODE_ENV === "development") {
  // Add development utilities
  (window as any).__api = api;
  console.log("API modules loaded:", Object.keys(api));
}
```

### Testing Integration

```typescript
import { authApi, usersApi } from "@/lib/api";

// Easy mocking for tests
jest.mock("@/lib/api", () => ({
  authApi: {
    login: jest.fn(),
    getCurrentUser: jest.fn(),
  },
  usersApi: {
    core: {
      listUsers: jest.fn(),
    },
  },
}));
```

### Debug Utilities

```typescript
import { request } from "@/lib/api";

// Debug wrapper
const debugRequest = async <T>(url: string, options?: any) => {
  console.log("API Request:", url, options);
  const response = await request<T>(url, options);
  console.log("API Response:", response);
  return response;
};
```

## Error Handling Strategy

### Centralized Error Management

All API modules use consistent error handling:

```typescript
// Standard error format
interface ApiError {
  message: string;
  status?: number;
  field_errors?: FieldError[];
}

// Error propagation
try {
  await authApi.login(credentials);
} catch (error) {
  // Error is standardized across all modules
  handleApiError(error);
}
```

### Error Recovery Patterns

```typescript
import { authApi } from "@/lib/api";

class RobustApiService {
  async loginWithRetry(
    credentials: LoginCredentials,
    maxRetries = 3,
  ): Promise<User> {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        return await authApi.login(credentials);
      } catch (error) {
        if (attempt === maxRetries) throw error;
        await new Promise((resolve) => setTimeout(resolve, 1000 * attempt));
      }
    }
    throw new Error("Max retries exceeded");
  }
}
```

## Migration Guide

### From Legacy Default Export

```typescript
// Old pattern
import api from "@/lib/api";
const user = await api.login({ email, password });

// New pattern (recommended)
import { authApi } from "@/lib/api";
const user = await authApi.login({ email, password });
```

### Gradual Migration Strategy

1. **Phase 1**: Use named exports for new code
2. **Phase 2**: Gradually update existing modules
3. **Phase 3**: Remove default export usage
4. **Phase 4**: Optimize bundle with tree shaking

## Dependencies

### Core Dependencies

```typescript
// API module imports
import { authApi } from "./auth";
import { healthApi } from "./health";
import { uploadsApi } from "./uploads";
import { usersApi } from "./users";
```

### Sub-module Dependencies

```typescript
// Specialized exports
import { usersCoreApi } from "./users/core";
import { usersExportsApi } from "./users/exports";
import { usersTestOnlyApi } from "./users/test_only_router";
```

### Utility Dependencies

```typescript
// Base functionality
import { request } from "./base";
import { uploadApiClient } from "./clients/uploads";
import { generatedApiClient } from "./generated/client";
```

## Related Files

- [`auth.ts`](./auth.ts.md) - Authentication API module
- [`users/index.ts`](./users/index.ts.md) - User management API module
- [`uploads.ts`](./uploads.ts.md) - File upload API module
- [`health.ts`](./health.ts.md) - Health check API module
- [`base.ts`](./base.ts.md) - HTTP client foundation
- [`types/index.ts`](./types/index.ts.md) - Type system definitions
- [`users/core.ts`](./users/core.ts.md) - Core user operations
- [`users/exports.ts`](./users/exports.ts.md) - User data export operations
- [`users/test_only_router.ts`](./users/test_only_router.ts.md) - Testing utilities

## Backend Integration

### API Structure Alignment

The frontend API structure directly mirrors the FastAPI backend organization:

```typescript
// Frontend modules          // Backend routers
authApi-- > /api/1v / auth.py;
usersApi.core-- > /api/1v / users / core.py;
usersApi.exports-- > /api/1v / users / exports.py;
uploadsApi-- > /api/1v / uploads.py;
healthApi-- > /api/1v / health.py;
```

### Endpoint Mapping

Each frontend API function maps to specific backend endpoints:

```typescript
// Frontend: authApi.login()
// Backend: POST /api/v1/auth/login

// Frontend: usersApi.core.listUsers()
// Backend: GET /api/v1/users/

// Frontend: uploadsApi.uploadFile()
// Backend: POST /api/v1/uploads/
```

### Type Consistency

Frontend types align with backend Pydantic models to ensure consistency across the full stack.

This main API entry point provides a well-organized, type-safe, and maintainable interface for all frontend-backend communication in the ReViewPoint application.

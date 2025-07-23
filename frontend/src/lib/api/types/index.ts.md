# types/index.ts - Central Type System Export

## Purpose

The `types/index.ts` file serves as the central aggregation point for all TypeScript type definitions used throughout the ReViewPoint frontend API system. It provides a unified export interface that brings together authentication, user management, file upload, and common API types, along with powerful utility types and helper functions. This module establishes the complete type safety foundation for all API communications in the application.

## Key Components

### Primary Exports

- **Authentication Types** - Complete JWT authentication and authorization type system
- **User Management Types** - User profiles, preferences, roles, and CRUD operations
- **File Upload Types** - File management, upload progress, and storage operations
- **Common API Types** - Base response formats, pagination, and error handling
- **Utility Types** - Advanced TypeScript utilities for type manipulation
- **Type Guards & Helpers** - Runtime type checking and validation functions

### Type System Architecture

The module aggregates types from four specialized modules:

- `auth.ts` - Authentication and authorization types
- `user.ts` - User management and profile types  
- `upload.ts` - File upload and management types
- `common.ts` - Foundational API communication types

## Authentication Type System

### Core Authentication Types

```typescript
// JWT Token Management
export type {
  AuthTokens,           // Access and refresh token pair
  AuthUser,            // Authenticated user information
  JWTPayload,          // JWT token payload structure
  TokenType,           // Token type enumeration
  AuthState,           // Authentication state management
} from "./auth";
```

### Authentication Operations

```typescript
// API Request/Response Types
export type {
  AuthLoginRequest,                    // Login credentials
  AuthLoginResponse,                   // Login success response
  AuthRegisterRequest,                 // User registration data
  AuthRegisterResponse,                // Registration success response
  AuthPasswordResetRequest,            // Password reset initiation
  AuthPasswordResetResponse,           // Password reset confirmation
  AuthPasswordResetConfirmRequest,     // Password reset completion
  AuthPasswordResetConfirmResponse,    // Password reset success
  AuthLogoutResponse,                  // Logout confirmation
  AuthTokenRefreshResponse,            // Token refresh response
} from "./auth";
```

### Authentication Utilities

```typescript
// Helper Functions and Constants
export {
  isAuthError,                // Type guard for auth errors
  isAuthTokens,              // Type guard for token pairs
  isTokenExpired,            // JWT expiration checker
  extractUserFromToken,      // User extraction from JWT
  decodeJWTPayload,         // JWT payload decoder
  EMAIL_REGEX,              // Email validation regex
  DEFAULT_PASSWORD_REQUIREMENTS,  // Password policy constants
  AuthErrorType,            // Authentication error enumeration
} from "./auth";
```

## User Management Type System

### User Data Types

```typescript
// User Profile and Management
export type {
  User,                     // Complete user profile
  UserWithRoles,           // User with role information
  UserPreferences,         // User settings and preferences
  UserActivity,            // User activity tracking
  UserSession,             // User session information
  UserStats,               // User statistics
  UserInvitation,          // User invitation system
} from "./user";
```

### User Operations

```typescript
// CRUD Operation Types
export type {
  UserCreateRequest,           // User creation data
  UserUpdateRequest,           // User profile updates
  UserResponse,               // Single user response
  UserListResponse,           // User list response
  PaginatedUserListResponse,  // Paginated user listing
  UserSearchParams,           // User search filters
  UserInvitationRequest,      // User invitation data
  UserPreferencesUpdateRequest, // Preference updates
  UserAvatarResponse,         // Avatar upload response
} from "./user";
```

### User System Utilities

```typescript
// Helper Functions and Enums
export {
  isUser,                    // Type guard for user objects
  isUserAdmin,              // Admin role checker
  isUserPreferences,        // Type guard for preferences
  isUserRole,               // Role validation
  userHasRole,              // Role permission checker
  getUserDisplayName,       // Display name formatter
  getUserInitials,          // User initials generator
  formatUserCreatedAt,      // Date formatter
  UserRole,                 // User role enumeration
  UserTheme,                // Theme preference enum
  DEFAULT_USER_PREFERENCES, // Default preference values
} from "./user";
```

## File Upload Type System

### File Management Types

```typescript
// Core File Types
export type {
  File,                     // File entity structure
  FileListItem,            // File list item representation
  Upload,                  // Upload operation data
  FileUploadResponse,      // Upload success response
  FileListResponse,        // File listing response
  PaginatedFileListResponse, // Paginated file listing
} from "./upload";
```

### Upload Operations

```typescript
// Upload Process Management
export type {
  FileUploadConfig,        // Upload configuration options
  UploadCreateRequest,     // Upload initiation data
  FileDeleteRequest,       // File deletion request
  FileDownloadRequest,     // File download request
  FileSearchParams,        // File search filters
  BulkFileOperation,       // Batch operations
  FileActionResult,        // Operation result data
} from "./upload";
```

### File Management Features

```typescript
// Advanced File Management
export type {
  FileManagementState,     // File manager state
  FileManagementConfig,    // Manager configuration
  FilePreviewConfig,       // Preview settings
  FileSharing,            // File sharing options
  FileUpdateEvent,        // File change events
  UploadStatus,           // Upload progress states
  UploadError,            // Upload error types
} from "./upload";
```

### Upload System Utilities

```typescript
// Helper Functions and Validation
export {
  isUpload,                // Type guard for uploads
  isUploadCompleted,       // Completion status checker
  isUploadInProgress,      // Progress status checker
  isUploadFailed,          // Failure status checker
  isUploadError,           // Error type guard
  validateUploadStatus,    // Status validation
  calculateUploadProgress, // Progress calculation
  formatUploadSize,        // Size formatting
  UploadErrorType,         // Upload error enumeration
} from "./upload";
```

## Common API Type System

### Base Response Types

```typescript
// Foundation Response Types
export type {
  ApiResponse,             // Standard API response wrapper
  PaginatedResponse,       // Paginated data response
  ListResponse,           // Simple list response
  MessageResponse,        // Text message response
  ApiError,              // Structured error response
  FieldError,            // Field validation error
} from "./common";
```

### Request/Response Infrastructure

```typescript
// HTTP Communication Types
export type {
  HttpMethod,             // HTTP method enumeration
  ApiEndpoint,           // Endpoint configuration
  RequestBody,           // Request payload types
  RequestMetadata,       // Request tracking data
  PaginationParams,      // Pagination parameters
  UploadProgress,        // File upload progress
  TypedAxiosError,       // Enhanced Axios error
  ISODateString,         // ISO 8601 date strings
} from "./common";
```

### Common Utilities

```typescript
// Helper Functions and Validation
export {
  isApiError,            // API error type guard
  isApiResponse,         // Response type guard
  isPaginatedResponse,   // Pagination type guard
  extractApiData,        // Data extraction utility
  createApiResponse,     // Response factory
  createApiErrorResponse, // Error response factory
  buildApiUrl,           // URL construction utility
  HttpStatusCode,        // HTTP status enumeration
} from "./common";
```

## Advanced Utility Types

### Type Manipulation Utilities

```typescript
// Deep Type Operations
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

// Selective Required Fields
export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>;

// Property Exclusion
export type OmitFields<T, K extends keyof T> = Omit<T, K>;

// Required Property Selection
export type PickRequired<T, K extends keyof T> = Required<Pick<T, K>>;
```

### Key Analysis Types

```typescript
// Optional Key Detection
export type OptionalKeys<T> = {
  [K in keyof T]-?: Record<string, never> extends Pick<T, K> ? K : never;
}[keyof T];

// Required Key Detection
export type RequiredKeys<T> = {
  [K in keyof T]-?: Record<string, never> extends Pick<T, K> ? never : K;
}[keyof T];
```

### Data Extraction Types

```typescript
// Response Data Extraction
export type ExtractApiData<T> = T extends ApiResponse<infer U> ? U : never;

// Paginated Item Extraction
export type ExtractPaginatedItem<T> = T extends PaginatedResponse<infer U> 
  ? U : never;

// List Item Extraction  
export type ExtractListItem<T> = T extends ListResponse<infer U> ? U : never;
```

### Union Type Aggregations

```typescript
// Error Type Union
export type AnyApiError = ApiError | AuthError | UploadError;

// Response Type Union
export type AnyApiResponse<T = unknown> = ApiResponse<T>;

// Form Data Union
export type ApiFormData = 
  | AuthRegisterRequest 
  | AuthLoginRequest
  | UserUpdateRequest
  | UserCreateRequest
  | FileUploadConfig;
```

### Response Type Specializations

```typescript
// Data-Present Response
export type DataApiResponse<T> = ApiResponse<T> & { data: T };

// Error Response
export type ErrorApiResponse = ApiResponse<never> & { error: string };
```

## API Handler Type System

### Handler Function Types

```typescript
// Generic API Handler
export type ApiHandler<TRequest = unknown, TResponse = unknown> = (
  request: TRequest,
) => Promise<ApiResponse<TResponse>>;

// Paginated Handler
export type PaginatedApiHandler<TItem, TParams = unknown> = (
  params: TParams & PaginationParams,
) => Promise<ApiResponse<PaginatedResponse<TItem>>>;
```

### State Management Types

```typescript
// API Status States
export type ApiStatus = "idle" | "loading" | "success" | "error";

// Generic API State
export interface ApiState<T> {
  data: T | null;
  status: ApiStatus;
  error: string | null;
  lastUpdated: ISODateString | null;
}
```

### State Management Utilities

```typescript
// State Factory
export function createDefaultApiState<T>(): ApiState<T> {
  return {
    data: null,
    status: "idle", 
    error: null,
    lastUpdated: null,
  };
}

// State Type Guards
export function isApiStateLoading<T>(state: ApiState<T>): boolean;
export function isApiStateError<T>(state: ApiState<T>): boolean;
export function isApiStateSuccess<T>(state: ApiState<T>): state is ApiState<T> & { data: T };
```

## Usage Examples

### Type-Safe API Response Handling

```typescript
import type { ApiResponse, User } from "@/lib/api/types";

async function fetchUser(id: string): Promise<User | null> {
  const response: ApiResponse<User> = await apiClient.get(`/api/v1/users/${id}`);
  
  if (response.data) {
    return response.data;
  } else {
    console.error("Failed to fetch user:", response.error);
    return null;
  }
}
```

### Advanced Type Manipulation

```typescript
import type { RequiredFields, User, DeepPartial } from "@/lib/api/types";

// Make email required for user updates
type UserUpdateWithEmail = RequiredFields<User, 'email'>;

// Create partial user for form state
type UserFormState = DeepPartial<User>;

// Extract user data from API response
type UserData = ExtractApiData<ApiResponse<User>>;
```

### State Management Integration

```typescript
import { ApiState, createDefaultApiState, isApiStateSuccess } from "@/lib/api/types";

interface UserStore {
  users: ApiState<User[]>;
  currentUser: ApiState<User>;
}

const initialState: UserStore = {
  users: createDefaultApiState<User[]>(),
  currentUser: createDefaultApiState<User>(),
};

// Type-safe state checking
if (isApiStateSuccess(store.users)) {
  console.log("Users loaded:", store.users.data);
}
```

### Utility Type Usage

```typescript
import type { PaginatedResponse, ExtractPaginatedItem } from "@/lib/api/types";

// Extract item type from paginated response
type UserListResponse = PaginatedResponse<User>;
type UserItem = ExtractPaginatedItem<UserListResponse>; // User

// Create form data type union
const submitForm = (data: ApiFormData) => {
  // TypeScript knows data can be any of the form types
};
```

## Type System Integration

### Store Integration

The type system integrates seamlessly with Zustand stores:

```typescript
import type { ApiState, User, AuthState } from "@/lib/api/types";

interface AppStore {
  auth: AuthState;
  users: ApiState<User[]>;
  currentUser: ApiState<User>;
}
```

### Component Integration

React components benefit from comprehensive type safety:

```typescript
import type { User, ApiResponse } from "@/lib/api/types";

interface UserProfileProps {
  user: User;
  onUpdate: (updates: Partial<User>) => Promise<ApiResponse<User>>;
}
```

### API Client Integration

All API functions are fully typed through this system:

```typescript
import type { AuthLoginRequest, AuthLoginResponse } from "@/lib/api/types";

export const login = async (credentials: AuthLoginRequest): Promise<ApiResponse<AuthLoginResponse>> => {
  // Implementation with full type safety
};
```

## Performance Considerations

### Type Compilation

- **Efficient Re-exports**: Centralized exports minimize compilation overhead
- **Selective Imports**: Import only needed types to reduce bundle size
- **Type-Only Imports**: Uses `import type` to prevent runtime inclusion

### Bundle Optimization

- **Tree Shaking**: Utility functions are properly tree-shakeable
- **Minimal Runtime**: Types compile away, only utilities included in bundle
- **Lazy Loading**: Complex types can be imported on-demand

### Development Experience

- **IntelliSense Support**: Comprehensive autocomplete and validation
- **Error Prevention**: Compile-time type checking prevents runtime errors
- **Refactoring Safety**: Type system ensures safe code modifications

## Advanced Patterns

### Conditional Types

```typescript
// Conditional response types based on success/error
type ConditionalResponse<T> = T extends { error: string }
  ? ErrorApiResponse 
  : DataApiResponse<T>;
```

### Mapped Types

```typescript
// Create update request types from entity types
type UpdateRequest<T> = {
  [K in keyof T]?: T[K];
};
```

### Template Literal Types

```typescript
// API endpoint path types
type ApiPath = `/api/v1/${string}`;
type AuthPath = `/api/v1/auth/${string}`;
```

## Error Handling Strategy

### Type-Safe Error Handling

The type system provides comprehensive error type safety:

```typescript
import type { AnyApiError, isApiError } from "@/lib/api/types";

function handleError(error: unknown): string {
  if (isApiError(error)) {
    return error.message;
  }
  return "An unknown error occurred";
}
```

### Field-Level Validation

Field errors are strongly typed for form validation:

```typescript
import type { FieldError } from "@/lib/api/types";

function displayFieldErrors(errors: FieldError[]) {
  return errors.map(error => `${error.field}: ${error.message}`);
}
```

## Dependencies

### TypeScript Core

The module relies on advanced TypeScript features:

- Conditional types for type extraction
- Mapped types for utility functions  
- Template literal types for string validation
- Type guards for runtime validation

### External Dependencies

```typescript
import type { AxiosError } from "axios";
```

### Internal Dependencies

```typescript
// Specialized type modules
import type { ... } from "./auth";
import type { ... } from "./common"; 
import type { ... } from "./upload";
import type { ... } from "./user";
```

## Related Files

- [`auth.ts`](./auth.ts.md) - Authentication and JWT token types
- [`user.ts`](./user.ts.md) - User management and profile types
- [`upload.ts`](./upload.ts.md) - File upload and management types
- [`common.ts`](./common.ts.md) - Foundational API communication types
- [`../base.ts`](../base.ts.md) - HTTP client using these type definitions
- [`../auth.ts`](../auth.ts.md) - Authentication API using these types
- [`../uploads.ts`](../uploads.ts.md) - Upload API using these types
- [`../users/index.ts`](../users/index.ts.md) - User API using these types

## Backend Integration

### Schema Alignment

Types are designed to match FastAPI backend schemas:

```typescript
// Matches FastAPI Pydantic models
interface User {
  id: string;
  email: string;
  created_at: ISODateString;  // Matches datetime serialization
  updated_at: ISODateString;
}
```

### Response Format Consistency

All response types align with backend patterns:

```typescript
// Matches FastAPI response format
interface ApiResponse<T> {
  data: T | null;
  error?: string;
}
```

This comprehensive type system provides the foundation for type-safe, reliable API communication throughout the ReViewPoint frontend application, ensuring consistency, preventing errors, and enhancing the development experience.

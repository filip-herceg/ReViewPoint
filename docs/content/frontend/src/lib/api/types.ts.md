# types/index.ts - Central API Type Definitions

## Purpose

The `types/index.ts` file serves as the central export point for all API type definitions in the ReViewPoint frontend. This module consolidates and re-exports type definitions from specialized type modules (auth, common, upload, user) and provides additional utility types and helper functions for type-safe API interactions.

## Key Components

### Type Categories

- **Authentication Types**: User authentication, JWT tokens, and auth state management
- **Common API Types**: Standard API responses, pagination, and HTTP utilities
- **Upload Types**: File upload configurations, progress tracking, and file management
- **User Types**: User profiles, preferences, roles, and management operations
- **Utility Types**: Advanced TypeScript utilities for type manipulation

### Core Exports

#### Authentication Types

```typescript
export type {
  AuthError, AuthLoginRequest, AuthRegisterRequest,
  AuthLoginResponse, AuthLogoutResponse, AuthTokens,
  AuthUser, JWTPayload, TokenType
} from "./auth";
```

#### Common API Types

```typescript
export type {
  ApiResponse, ApiError, PaginatedResponse,
  PaginationParams, ISODateString, HttpMethod
} from "./common";
```

#### Upload & File Types

```typescript
export type {
  File, FileUploadConfig, FileUploadResponse,
  UploadStatus, UploadError, FileListResponse
} from "./upload";
```

#### User Management Types

```typescript
export type {
  User, UserCreateRequest, UserUpdateRequest,
  UserPreferences, UserRole, UserStats
} from "./user";
```

## Advanced Type Utilities

### Data Extraction Types

```typescript
// Extract data type from API responses
export type ExtractApiData<T> = T extends ApiResponse<infer U> ? U : never;

// Extract item type from paginated responses
export type ExtractPaginatedItem<T> = T extends PaginatedResponse<infer U> ? U : never;

// Extract item type from list responses
export type ExtractListItem<T> = T extends ListResponse<infer U> ? U : never;
```

### TypeScript Utility Types

```typescript
// Deep partial - make all properties optional recursively
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

// Require specific fields
export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>;

// Omit specific fields
export type OmitFields<T, K extends keyof T> = Omit<T, K>;

// Pick and require specific fields
export type PickRequired<T, K extends keyof T> = Required<Pick<T, K>>;
```

### Key Analysis Types

```typescript
// Get optional property keys
export type OptionalKeys<T> = {
  [K in keyof T]-?: Record<string, never> extends Pick<T, K> ? K : never;
}[keyof T];

// Get required property keys
export type RequiredKeys<T> = {
  [K in keyof T]-?: Record<string, never> extends Pick<T, K> ? never : K;
}[keyof T];
```

## API Integration Types

### Error Handling

```typescript
// Union of all possible API errors
export type AnyApiError = ApiError | AuthError | UploadError;

// Standardized error response type
export type ErrorApiResponse = ApiResponse<never> & { error: string };
```

### Form Data Types

```typescript
// Union type for all form data that can be sent to API
export type ApiFormData =
  | AuthRegisterRequest
  | AuthLoginRequest
  | UserUpdateRequest
  | UserCreateRequest
  | FileUploadConfig;
```

### Handler Types

```typescript
// Generic API endpoint handler
export type ApiHandler<TRequest = unknown, TResponse = unknown> = (
  request: TRequest,
) => Promise<ApiResponse<TResponse>>;

// Paginated API endpoint handler
export type PaginatedApiHandler<TItem, TParams = unknown> = (
  params: TParams & PaginationParams,
) => Promise<ApiResponse<PaginatedResponse<TItem>>>;
```

## API State Management

### State Types

```typescript
export type ApiStatus = "idle" | "loading" | "success" | "error";

export interface ApiState<T> {
  data: T | null;
  status: ApiStatus;
  error: string | null;
  lastUpdated: ISODateString | null;
}
```

### State Helper Functions

```typescript
// Create default API state
export function createDefaultApiState<T>(): ApiState<T> {
  return {
    data: null,
    status: "idle",
    error: null,
    lastUpdated: null,
  };
}

// Type guards for API state
export function isApiStateLoading<T>(state: ApiState<T>): boolean;
export function isApiStateError<T>(state: ApiState<T>): boolean;
export function isApiStateSuccess<T>(state: ApiState<T>): state is ApiState<T> & { data: T };
```

## Usage Examples

### Basic Type Usage

```typescript
import type { User, ApiResponse, PaginatedResponse } from '@/lib/api/types';

// Type-safe API response handling
function handleUserResponse(response: ApiResponse<User>) {
  if (response.success) {
    console.log('User:', response.data.name);
  } else {
    console.error('Error:', response.error);
  }
}

// Working with paginated data
function handleUserList(response: ApiResponse<PaginatedResponse<User>>) {
  if (response.success) {
    const users = response.data.items;
    const totalPages = response.data.meta.totalPages;
    console.log(`${users.length} users, ${totalPages} pages total`);
  }
}
```

### Type Utility Usage Examples

```typescript
import type { DeepPartial, RequiredFields, ExtractApiData } from '@/lib/api/types';

// Partial update types
type UserUpdate = DeepPartial<User>;

// Ensure required fields
type UserCreation = RequiredFields<User, 'name' | 'email'>;

// Extract response data type
type UserApiResponse = ApiResponse<User>;
type UserData = ExtractApiData<UserApiResponse>; // User
```

### Form Integration

```typescript
import type { AuthLoginRequest, UserCreateRequest } from '@/lib/api/types';

// Type-safe form handling
function handleLoginForm(formData: AuthLoginRequest) {
  // TypeScript ensures email and password are present
  return authApi.login(formData);
}

function handleUserCreation(userData: UserCreateRequest) {
  // TypeScript validates all required user fields
  return userApi.create(userData);
}
```

### State Management Integration

```typescript
import { createDefaultApiState, isApiStateSuccess } from '@/lib/api/types';

// Zustand store with type-safe API state
interface UserStore {
  users: ApiState<User[]>;
  currentUser: ApiState<User>;
}

const useUserStore = create<UserStore>(() => ({
  users: createDefaultApiState<User[]>(),
  currentUser: createDefaultApiState<User>(),
}));

// Type-safe state checking
function UserProfile() {
  const currentUser = useUserStore(state => state.currentUser);
  
  if (isApiStateSuccess(currentUser)) {
    // TypeScript knows currentUser.data is User
    return <div>Hello, {currentUser.data.name}!</div>;
  }
  
  return <div>Loading...</div>;
}
```

## Integration Points

### Type Validation

- **Runtime Validation**: Works with validation libraries for runtime type checking
- **Form Libraries**: Compatible with React Hook Form, Formik, and other form libraries
- **State Management**: Integrates with Zustand, Redux Toolkit, and other state managers
- **API Clients**: Type-safe integration with Axios and other HTTP clients

### Error Management Integration

- **Unified Error Types**: Consistent error handling across all API modules
- **Type Guards**: Helper functions for type-safe error checking
- **Error Recovery**: Structured error types for implementing retry logic

### Development Experience

- **IntelliSense**: Full TypeScript autocomplete for all API types
- **Type Safety**: Compile-time checking for API request/response types
- **Documentation**: JSDoc comments provide inline documentation
- **Refactoring**: Safe refactoring with TypeScript's type system

## Dependencies

### External Dependencies

- **TypeScript**: Advanced type system features for utility types
- **Date Handling**: ISODateString type for consistent date formatting

### Internal Dependencies

- **Auth Types**: Authentication and authorization type definitions
- **Common Types**: Shared API response and utility types
- **Upload Types**: File upload and management type definitions
- **User Types**: User management and profile type definitions

## Related Files

- **[auth.ts](auth.ts.md)**: Authentication type definitions and utilities
- **[common.ts](common.ts.md)**: Common API response and utility types
- **[upload.ts](upload.ts.md)**: File upload and management types
- **[user.ts](user.ts.md)**: User profile and management types
- **[base.ts](../base.ts.md)**: Base API client implementation using these types

## Best Practices

### Type Organization

- **Centralized Exports**: All types exported from single entry point for consistency
- **Module Separation**: Related types grouped in specialized modules
- **Re-export Pattern**: Clean API surface with selective re-exports

### Type Safety

- **Strict Types**: No `any` types - everything is strictly typed
- **Utility Types**: Advanced TypeScript features for type manipulation
- **Type Guards**: Runtime type checking with compile-time guarantees

### API Integration

- **Consistent Patterns**: Standardized request/response patterns across all endpoints
- **Error Handling**: Unified error types for consistent error handling
- **State Management**: Compatible with popular state management libraries

### Performance

- **Tree Shaking**: Modular exports enable efficient bundle optimization
- **Type-Only Imports**: Uses `type` imports to avoid runtime overhead
- **Lazy Loading**: Compatible with dynamic imports for code splitting

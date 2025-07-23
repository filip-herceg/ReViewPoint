# base.ts - HTTP Client Foundation

## Purpose

The `base.ts` module provides the foundational HTTP client infrastructure for the entire ReViewPoint frontend application. It implements a sophisticated Axios-based client with automatic token management, request/response interception, error handling, and authentication state synchronization. This module serves as the core networking layer that all other API modules depend on.

## Key Components

### Primary Exports

- **`apiClient`** - Configured Axios instance with interceptors and authentication
- **`request<T>()`** - Generic request wrapper with comprehensive error handling

### Core Features

- **Automatic Token Management** - JWT token injection and refresh handling
- **Request/Response Interception** - Authentication and error handling middleware
- **401 Unauthorized Recovery** - Automatic token refresh on authentication failures
- **Comprehensive Error Handling** - Standardized error processing and logging
- **Authentication State Integration** - Synchronization with Zustand auth store

## HTTP Client Configuration

### Axios Instance Setup

```typescript
export const apiClient = axios.create({
  baseURL: API_BASE, // Empty string - explicit endpoint calls
  timeout: 10000, // 10 second timeout
  withCredentials: true, // Include cookies for CORS
  headers: {
    "Content-Type": "application/json",
  },
});
```

**Design Decisions:**

- **No API prefix**: Endpoints must be explicitly specified (e.g., `/api/v1/auth/login`)
- **10-second timeout**: Balances user experience with network reliability
- **Credentials included**: Supports cookie-based authentication where needed
- **JSON by default**: Standard content type for REST API communication

## Request Interceptor System

### Token Injection Logic

```typescript
apiClient.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    // Skip token injection for auth endpoints to prevent loops
    if (config.url?.includes("/auth/")) {
      return config;
    }

    try {
      const token = await tokenService.getValidAccessToken();
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch (error) {
      // Continue with request even if token fetch fails
    }

    return config;
  },
);
```

**Key Features:**

- **Smart Token Management**: Automatically retrieves valid tokens (with refresh if needed)
- **Auth Endpoint Exclusion**: Prevents circular dependencies on authentication routes
- **Graceful Degradation**: Continues requests even if token retrieval fails
- **Bearer Token Format**: Standard JWT authentication header format

### Error Recovery and Logging

The request interceptor includes comprehensive error handling and debug logging for token management operations.

## Response Interceptor System

### 401 Unauthorized Handling

```typescript
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean;
    };

    if (error.response?.status === 401 && !originalRequest._retry) {
      // Automatic token refresh and request retry logic
    }

    return Promise.reject(error);
  },
);
```

**401 Recovery Process:**

1. **Detection**: Identifies 401 Unauthorized responses
2. **Loop Prevention**: Uses `_retry` flag and `isRefreshingToken` guard
3. **Token Refresh**: Attempts to refresh access token via `tokenService`
4. **Request Retry**: Re-executes original request with new token
5. **Fallback Handling**: Logs out user if refresh fails

### Refresh Loop Prevention

```typescript
let isRefreshingToken = false;

// In response interceptor
if (isRefreshingToken) {
  logger.warn("[API] Token refresh already in progress - rejecting request");
  return Promise.reject(error);
}
```

**Protection Mechanisms:**

- **Global flag**: Prevents concurrent refresh attempts
- **Request retry flag**: Prevents infinite retry loops
- **Auth endpoint exclusion**: Avoids refresh on authentication failures

## Generic Request Wrapper

### Type-Safe Request Function

```typescript
export async function request<T>(
  url: string,
  config: AxiosRequestConfig = {},
): Promise<ApiResponse<T>> {
  try {
    const res = await apiClient.request<T>({ url, ...config });
    return { data: res.data as T };
  } catch (error: unknown) {
    // Sophisticated error handling and type checking
    return { data: null, error: errorMessage };
  }
}
```

**Generic Benefits:**

- **Type Safety**: Full TypeScript support for request/response types
- **Consistent Interface**: Standardized `ApiResponse<T>` return format
- **Error Normalization**: Converts all errors to consistent format
- **Logging Integration**: Comprehensive request/response/error logging

### Error Processing Logic

The request wrapper implements sophisticated error type checking and message extraction:

```typescript
// Type guard for axios-like errors
const isAxiosError = (
  err: unknown,
): err is { response?: { data?: Record<string, unknown> } } => {
  return typeof err === "object" && err !== null && "response" in err;
};

// Error message extraction from response data
const errorMessage =
  typeof data === "string"
    ? data
    : typeof (data as Record<string, unknown>).error === "string"
      ? ((data as Record<string, unknown>).error as string)
      : typeof (data as Record<string, unknown>).message === "string"
        ? ((data as Record<string, unknown>).message as string)
        : "Unknown error";
```

## Authentication Integration

### Token Service Coordination

```typescript
import { tokenService } from "@/lib/auth/tokenService";

// In request interceptor
const token = await tokenService.getValidAccessToken();

// In response interceptor for 401 handling
const newToken = await tokenService.refreshAccessToken();
```

**Integration Points:**

- **Valid Token Retrieval**: Automatic token validation and refresh
- **Refresh Token Usage**: Seamless token renewal on expiration
- **Error Propagation**: Proper handling of token service failures

### Auth Store Synchronization

```typescript
import { useAuthStore } from "@/lib/store/authStore";

// Update refresh state
useAuthStore.getState().setRefreshing(true);

// Logout on refresh failure
useAuthStore.getState().logout();

// Emit logout event for app-wide handling
window.dispatchEvent(new CustomEvent("auth:logout"));
```

**State Management:**

- **Refresh Indicators**: Updates UI refresh state during token operations
- **Logout Coordination**: Triggers app-wide logout on authentication failures
- **Event System**: Uses custom events to avoid circular import dependencies

## Usage Examples

### Basic API Request

```typescript
import { request } from "@/lib/api/base";

// Type-safe GET request
const response = await request<User[]>("/api/v1/users");
if (response.data) {
  console.log("Users:", response.data);
} else {
  console.error("Error:", response.error);
}
```

### Advanced Request Configuration

```typescript
import { apiClient } from "@/lib/api/base";

// Direct axios usage with interceptors
const response = await apiClient.post("/api/v1/files/upload", formData, {
  headers: {
    "Content-Type": "multipart/form-data",
  },
  timeout: 30000, // Extended timeout for file uploads
  onUploadProgress: (progressEvent) => {
    // Upload progress handling
  },
});
```

### Error Handling Pattern

```typescript
import { request, ApiResponse } from "@/lib/api/base";

async function fetchUserData(userId: string): Promise<User | null> {
  const response: ApiResponse<User> = await request(`/api/v1/users/${userId}`);

  if (response.data) {
    return response.data;
  } else {
    // Error already logged by base client
    toast.error(`Failed to load user: ${response.error}`);
    return null;
  }
}
```

## Advanced Integration Patterns

### Custom Interceptor Addition

```typescript
import { apiClient } from "@/lib/api/base";

// Add request timing interceptor
apiClient.interceptors.request.use((config) => {
  config.metadata = { startTime: Date.now() };
  return config;
});

apiClient.interceptors.response.use((response) => {
  const duration = Date.now() - response.config.metadata.startTime;
  logger.info(`Request completed in ${duration}ms`);
  return response;
});
```

### Request Cancellation

```typescript
import { apiClient } from "@/lib/api/base";

const cancelToken = axios.CancelToken.source();

const response = await apiClient.get("/api/v1/data", {
  cancelToken: cancelToken.token,
});

// Cancel if needed
cancelToken.cancel("Request cancelled by user");
```

### Retry Configuration

```typescript
import { request } from "@/lib/api/base";

async function requestWithRetry<T>(
  url: string,
  maxRetries = 3,
): Promise<ApiResponse<T>> {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    const response = await request<T>(url);

    if (response.data || attempt === maxRetries) {
      return response;
    }

    // Exponential backoff
    await new Promise((resolve) =>
      setTimeout(resolve, Math.pow(2, attempt) * 1000),
    );
  }
}
```

## Performance Considerations

### Request Optimization

- **Connection Reuse**: Single axios instance for connection pooling
- **Timeout Management**: Appropriate timeouts prevent hanging requests
- **Credential Handling**: Efficient cookie management for session persistence

### Memory Management

- **Error Handling**: Proper cleanup in error scenarios
- **Event Listeners**: Careful event management to prevent memory leaks
- **Interceptor Efficiency**: Minimal processing in hot paths

### Concurrent Request Handling

- **Token Refresh Coordination**: Prevents multiple simultaneous refresh attempts
- **Request Queuing**: Implicit queuing through axios for rate limiting
- **State Synchronization**: Efficient auth store updates

## Security Features

### Token Security

- **Automatic Injection**: Secure token attachment to authenticated requests
- **Refresh Handling**: Secure token renewal without credential exposure
- **Logout on Failure**: Immediate logout on authentication compromise

### Request Validation

- **URL Filtering**: Smart handling of authentication endpoints
- **Header Management**: Secure header injection and cleanup
- **Error Sanitization**: Safe error message extraction and logging

## Error Handling Strategy

### Error Type Hierarchy

1. **Network Errors**: Connection failures, timeouts, DNS issues
2. **HTTP Errors**: 4xx/5xx status codes with server error messages
3. **Authentication Errors**: 401/403 with automatic recovery attempts
4. **Validation Errors**: 422 with field-specific error details
5. **Application Errors**: Custom error types from backend services

### Logging Strategy

- **Request Logging**: URL, configuration, and timing information
- **Response Logging**: Success/failure status and data summaries
- **Error Logging**: Comprehensive error details with context
- **Debug Information**: Token management and interceptor operations

## Dependencies

### Core Dependencies

```typescript
import axios, {
  type AxiosError,
  type AxiosRequestConfig,
  type AxiosResponse,
} from "axios";
```

### Internal Dependencies

```typescript
import type { ApiResponse } from "@/lib/api/types";
import { tokenService } from "@/lib/auth/tokenService";
import { useAuthStore } from "@/lib/store/authStore";
import logger from "@/logger";
import { handleApiError } from "./errorHandling";
```

### Integration Points

- **Token Service**: JWT token management and refresh logic
- **Auth Store**: Authentication state and user session management
- **Error Handling**: Centralized error processing and normalization
- **Logger**: Comprehensive logging for debugging and monitoring
- **Type System**: TypeScript definitions for API responses and requests

## Related Files

- [`types.ts`](./types.ts.md) - TypeScript definitions for API responses
- [`errorHandling.ts`](./errorHandling.ts.md) - Centralized error processing
- [`auth.ts`](./auth.ts.md) - Authentication API using base client
- [`uploads.ts`](./uploads.ts.md) - File upload API using base client
- [`users/index.ts`](./users/index.ts.md) - User management API using base client
- [`../auth/tokenService.ts`](../auth/tokenService.ts.md) - JWT token management
- [`../store/authStore.ts`](../store/authStore.ts.md) - Authentication state management

## Backend Integration

### API Endpoint Structure

The base client is designed to work with ReViewPoint's FastAPI backend:

- **Base URL**: No prefix - endpoints specify full paths
- **Authentication**: JWT Bearer tokens with automatic refresh
- **Error Format**: Standardized error responses with `error` or `message` fields
- **CORS**: Configured for cross-origin requests with credentials

### Expected Response Format

```typescript
// Success response
{
  data: T; // Actual response data
}

// Error response
{
  error: string; // Error message
  // or
  message: string; // Alternative error field
}
```

This foundational HTTP client provides the robust, secure, and efficient networking infrastructure that powers all API communication in the ReViewPoint frontend application.

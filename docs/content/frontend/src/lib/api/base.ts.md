# base.ts - HTTP API Client Foundation

## Purpose

The `base.ts` file provides the foundational HTTP client for the ReViewPoint frontend application. This module establishes the core Axios configuration, implements request/response interceptors for authentication and error handling, and provides a standardized interface for making API requests. It serves as the backbone for all API communications in the application.

## Key Features

### Core Functionality

- **Axios Configuration**: Pre-configured HTTP client with base URL and timeout settings
- **Authentication Integration**: Automatic JWT token handling and refresh logic
- **Request Interceptors**: Automatic token attachment to authenticated requests
- **Response Interceptors**: Intelligent 401 error handling with token refresh
- **Error Handling**: Comprehensive error processing and logging
- **Type Safety**: Full TypeScript integration with generic response types

### Security Features

- **Token Management**: Secure JWT token attachment and refresh
- **Authentication State**: Integration with auth store for state management
- **Error Recovery**: Automatic token refresh on authentication failures
- **Request Retry**: Intelligent retry logic for failed authenticated requests

## Core Components

### HTTP Client Configuration

```typescript
const apiClient = axios.create({
  baseURL: API_URL || "http://localhost:8000",
  timeout: 15000,
  headers: {
    "Content-Type": "application/json",
  },
});
```

**Configuration Details**:

- **Base URL**: Configurable API endpoint (defaults to localhost:8000)
- **Timeout**: 15-second request timeout for reliable error handling
- **Content Type**: JSON content type for API communication
- **Headers**: Standardized headers for consistent requests

### Request Interceptor

**Purpose**: Automatically attach JWT tokens to authenticated requests

```typescript
apiClient.interceptors.request.use(
  async (config) => {
    try {
      const token = await tokenService.getValidAccessToken();
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
        logger.debug("[API] Token attached to request", { url: config.url });
      }
    } catch (error) {
      logger.warn("[API] Failed to get valid token for request", { error });
    }
    return config;
  },
  (error) => Promise.reject(error)
);
```

**Features**:

- **Automatic Token Attachment**: Seamlessly adds JWT tokens to requests
- **Token Validation**: Ensures only valid tokens are used
- **Error Resilience**: Continues requests even if token fetch fails
- **Debug Logging**: Comprehensive logging for debugging

### Response Interceptor

**Purpose**: Handle authentication errors and implement automatic token refresh

```typescript
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401 && !originalRequest._retry) {
      // Implement token refresh logic
      const newToken = await tokenService.refreshAccessToken();
      if (newToken) {
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return apiClient(originalRequest);
      }
    }
    return Promise.reject(error);
  }
);
```

**Features**:

- **401 Error Detection**: Identifies authentication failures
- **Token Refresh**: Automatic token refresh on authentication errors
- **Request Retry**: Retries original request with new token
- **Infinite Loop Prevention**: Prevents endless refresh attempts
- **Auth Store Integration**: Updates authentication state

## API Functions

### Primary Request Function

```typescript
export async function request<T>(
  url: string,
  config: AxiosRequestConfig = {}
): Promise<ApiResponse<T>>
```

**Purpose**: Standardized API request function with comprehensive error handling

**Parameters**:

- `url` (string, required): API endpoint URL (relative to base URL)
- `config` (AxiosRequestConfig, optional): Axios configuration options

**Returns**: Promise resolving to standardized API response

**Usage Examples**:

```typescript
import { request } from '@/lib/api/base';

// GET request
const response = await request<User>('/api/v1/users/me');
if (response.data) {
  console.log('User:', response.data);
} else {
  console.error('Error:', response.error);
}

// POST request with data
const loginResponse = await request<AuthLoginResponse>('/api/v1/auth/login', {
  method: 'POST',
  data: { email: 'user@example.com', password: 'password' }
});

// PUT request with parameters
const updateResponse = await request<User>('/api/v1/users/123', {
  method: 'PUT',
  data: { name: 'Updated Name' }
});

// DELETE request
const deleteResponse = await request<void>('/api/v1/users/123', {
  method: 'DELETE'
});
```

### Response Format

All API responses follow a consistent format:

```typescript
interface ApiResponse<T> {
  data: T | null;
  error?: string;
}

// Success response
{ data: { id: 1, name: "John Doe" } }

// Error response
{ data: null, error: "Invalid credentials" }
```

## Error Handling

### Error Processing Flow

1. **Axios Error Detection**: Identifies HTTP errors and network issues
2. **Response Analysis**: Extracts error messages from response data
3. **Error Transformation**: Converts errors to standardized format
4. **Logging**: Comprehensive error logging for debugging
5. **User-Friendly Messages**: Returns actionable error messages

### Error Types Handled

```typescript
// Network errors
{ data: null, error: "Network error - please check your connection" }

// Authentication errors
{ data: null, error: "Invalid credentials" }

// Validation errors
{ data: null, error: "Email is required" }

// Server errors
{ data: null, error: "Internal server error" }

// Timeout errors
{ data: null, error: "Request timeout - please try again" }
```

## Authentication Integration

### Token Service Integration

The base client integrates closely with the token service for authentication:

```typescript
import { tokenService } from '@/lib/token';

// Get valid token for requests
const token = await tokenService.getValidAccessToken();

// Refresh token on 401 errors
const newToken = await tokenService.refreshAccessToken();
```

### Auth Store Integration

```typescript
import { useAuthStore } from '@/store/auth';

// Update refresh state
useAuthStore.getState().setRefreshing(true);

// Logout on refresh failure
useAuthStore.getState().logout();
```

### Authentication Flow

1. **Request Initiated**: User makes API request
2. **Token Attachment**: Request interceptor adds JWT token
3. **Response Received**: Response interceptor checks for errors
4. **401 Detected**: Authentication error triggers refresh flow
5. **Token Refresh**: New token obtained from refresh endpoint
6. **Request Retry**: Original request retried with new token
7. **Success/Failure**: Response returned or user logged out

## Logging and Debugging

### Logging Configuration

The module provides comprehensive logging for debugging:

```typescript
import logger from '@/logger';

// Request logging
logger.info("[API] request", { url, config, response: res.data });

// Error logging
logger.error("[API] request ERROR", { url, config, error: handled.message });

// Debug logging
logger.debug("[API] Token attached to request", { url: config.url });

// Warning logging
logger.warn("[API] Failed to get valid token for request", { error });
```

## Integration Patterns

### React Hook Integration

```typescript
import { useState, useCallback } from 'react';
import { request } from '@/lib/api/base';

export function useApiRequest<T>() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<T | null>(null);

  const makeRequest = useCallback(async (url: string, config?: AxiosRequestConfig) => {
    setLoading(true);
    setError(null);

    try {
      const response = await request<T>(url, config);
      
      if (response.error) {
        setError(response.error);
        setData(null);
      } else {
        setData(response.data);
        setError(null);
      }
      
      return response;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
      setData(null);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { data, loading, error, makeRequest };
}
```

## Dependencies

### External Dependencies

- **Axios**: HTTP client library for making API requests
- **@/logger**: Application logging service for debugging
- **@/lib/token**: Token service for JWT management
- **@/store/auth**: Authentication state management
- **@/lib/api/types**: TypeScript type definitions for API responses

### Type Dependencies

```typescript
import type { AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import type { ApiResponse } from '@/lib/api/types';
```

## Related Files

- **[auth.ts](auth.ts.md)**: Authentication API functions using this client
- **[users.ts](users.ts.md)**: User management API functions
- **[types/index.ts](types.ts.md)**: TypeScript type definitions
- **[tokenService](../token.ts.md)**: JWT token management service
- **[authStore](../../store/auth.ts.md)**: Authentication state management

## Best Practices

### Request Patterns

- **Consistent Error Handling**: Always check for response.error before using response.data
- **Type Safety**: Use generic types for request/response data
- **Timeout Configuration**: Set appropriate timeouts for different request types
- **Request Cancellation**: Implement request cancellation for long-running operations

### Security Best Practices

- **Token Security**: Secure token storage and transmission
- **Request Validation**: Validate request data before sending
- **Error Information**: Avoid exposing sensitive information in error messages
- **HTTPS Only**: Ensure all API communications use HTTPS in production

### Performance Best Practices

- **Request Debouncing**: Implement debouncing for frequent requests
- **Response Caching**: Cache responses where appropriate
- **Request Batching**: Batch multiple requests when possible
- **Connection Management**: Optimize connection pooling and keepalive settings

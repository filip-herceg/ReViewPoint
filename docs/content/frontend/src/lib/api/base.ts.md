# base.ts - API Base Client & Request Management

## Purpose

Foundation API client using Axios with comprehensive request/response handling, authentication token management, and automatic token refresh capabilities. Provides centralized HTTP client for all API communications.

## Key Components

### Axios Client Configuration

- **Base Configuration**: Centralized HTTP client with timeout and credential settings
- **Request Interceptors**: Automatic token attachment and authentication handling
- **Response Interceptors**: Global error handling and token refresh logic
- **Timeout Management**: 10-second request timeout for optimal UX

### Authentication Integration

#### Token Management
- **Automatic Token Injection**: Attaches Bearer tokens to authenticated requests
- **Refresh Token Logic**: Automatic token refresh on 401 responses
- **Loop Prevention**: Prevents infinite refresh cycles with request retry tracking
- **Auth Endpoint Bypass**: Skips token injection for authentication endpoints

#### Token Refresh Flow
```typescript
// Response interceptor handles 401 with token refresh
if (error.response?.status === 401 && !originalRequest._retry) {
  // Attempt token refresh and retry original request
  isRefreshingToken = true;
  originalRequest._retry = true;
  // Refresh token and retry request
}
```

## Request/Response Pipeline

### Request Preprocessing
1. **URL Construction**: Clean base URL configuration without automatic prefixes
2. **Authentication**: Token validation and attachment via tokenService
3. **Header Management**: Content-Type and Authorization header handling
4. **Error Prevention**: Defensive programming for token fetch failures

### Response Processing
1. **Success Handling**: Pass-through for successful responses
2. **Error Interception**: Global error handling and classification
3. **Token Refresh**: Automatic retry with refreshed tokens
4. **State Management**: Integration with auth store for refresh state

## Error Handling Strategy

### Token-Related Errors
- **401 Unauthorized**: Automatic token refresh and request retry
- **Auth Endpoint Errors**: Bypass refresh for authentication failures
- **Refresh Loop Prevention**: Global refresh state tracking
- **Graceful Degradation**: Continue requests even if token fetch fails

### Network & API Errors
- **Timeout Handling**: Configurable request timeout (10 seconds)
- **Retry Logic**: Single retry for token-related failures
- **Error Logging**: Comprehensive error logging with context
- **Error Propagation**: Structured error handling for components

## Integration Points

### Authentication Services
- **Token Service**: Direct integration with tokenService for token management
- **Auth Store**: State synchronization with Zustand auth store
- **Refresh State**: Global refresh state management

### API Modules
- **Base Client**: Exported apiClient used by all API modules
- **Error Handling**: Centralized error handling via errorHandling module
- **Type Safety**: Full TypeScript integration with ApiResponse types

## Performance Optimizations

### Request Efficiency
- **Credential Management**: Persistent credentials with withCredentials
- **Header Optimization**: Efficient header management
- **Timeout Configuration**: Balanced timeout for UX and reliability

### Caching & State
- **Token Caching**: Efficient token reuse across requests
- **Refresh Optimization**: Prevents concurrent refresh requests
- **State Synchronization**: Efficient auth state updates

## Security Considerations

### Token Security
- **Bearer Token Protection**: Secure token transmission
- **Refresh Token Safety**: Secure refresh token handling
- **Auth Bypass**: Prevents token loops on auth endpoints
- **Error Isolation**: Prevents token leakage in error responses

### Request Security
- **HTTPS Enforcement**: Production HTTPS requirement
- **Credential Handling**: Secure cookie and credential management
- **Header Validation**: Secure header management

## Usage Patterns

### API Module Integration
```typescript
// Used by all API modules
import { apiClient } from './base';
const response = await apiClient.get('/api/v1/users');
```

### Error Handling
- **Global Interceptors**: Centralized error processing
- **Component Integration**: Error propagation to UI components
- **Logging Integration**: Comprehensive request/response logging

## Related Files

- [`tokenService`](../auth/tokenService.ts.md) - Token management service
- [`authStore`](../store/authStore.ts.md) - Authentication state management
- [`errorHandling.ts`](errorHandling.ts.md) - Error processing utilities
- [`types/`](types/) - API response type definitions

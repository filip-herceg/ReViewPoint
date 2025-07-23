# tokenService.ts - JWT Token Management Service

## Purpose

The `tokenService.ts` file provides centralized JWT token management for the ReViewPoint application. It handles token storage, automatic refresh, expiration detection, and secure token operations with comprehensive error handling and logging.

## Key Components

### **TokenService Class**

Central service class that manages all token-related operations:

```typescript
class TokenService {
  // Token refresh state management
  private refreshState: TokenRefreshState;

  // Token expiration buffer (5 minutes before expiry)
  private readonly EXPIRATION_BUFFER = 5 * 60;
}
```

### **Token Refresh State**

```typescript
interface TokenRefreshState {
  isRefreshing: boolean; // Current refresh status
  refreshPromise: Promise<string> | null; // Active refresh promise
  refreshQueue: Array<{
    // Queued refresh requests
    resolve: (token: string) => void;
    reject: (error: Error) => void;
  }>;
}
```

### **Core Features**

- **Automatic Token Refresh**: Proactive token renewal before expiration
- **Concurrent Request Handling**: Queues multiple refresh requests during active refresh
- **Expiration Detection**: Smart detection with configurable buffer time
- **Secure Storage**: Safe token storage and retrieval mechanisms
- **Error Recovery**: Comprehensive error handling with fallback strategies

## Key Methods

### **Token Decoding**

```typescript
decodeJWTPayload(token: string): JWTPayload | null
```

- Safely decodes JWT payload without verification
- Extracts expiration time and user information
- Handles malformed tokens gracefully

### **Expiration Checking**

```typescript
isTokenExpired(token: string): boolean
```

- Checks if token is expired or near expiration
- Uses configurable buffer time (5 minutes default)
- Handles invalid or malformed tokens

### **Token Refresh**

```typescript
refreshAccessToken(): Promise<string>
```

- Automatic token refresh using refresh token
- Handles concurrent refresh requests
- Updates auth store with new tokens
- Manages refresh queue for pending requests

### **Secure Token Storage**

```typescript
getStoredTokens(): AuthTokens | null
setStoredTokens(tokens: AuthTokens): void
clearStoredTokens(): void
```

- Secure localStorage-based token storage
- Automatic cleanup on logout
- Error handling for storage failures

## Dependencies

### **Core Dependencies**

- `@/lib/api/auth` - Authentication API client
- `@/lib/store/authStore` - Authentication state management
- `@/logger` - Service logging and error tracking

### **Type Definitions**

- [AuthTokens](../api/types.ts.md) - Token structure definitions
- [JWTPayload](../api/types.ts.md) - JWT payload interface

## Implementation Details

### **Automatic Token Refresh**

```typescript
// Proactive refresh with buffer time
const isNearExpiry = currentTime + EXPIRATION_BUFFER >= payload.exp;

if (isNearExpiry) {
  return await this.refreshAccessToken();
}
```

### **Concurrent Refresh Handling**

```typescript
// Queue multiple refresh requests during active refresh
if (this.refreshState.isRefreshing) {
  return new Promise((resolve, reject) => {
    this.refreshState.refreshQueue.push({ resolve, reject });
  });
}
```

### **Error Recovery Strategy**

```typescript
// Comprehensive error handling with cleanup
catch (error) {
  logger.error('[TokenService] Token refresh failed', error);
  this.clearRefreshState();
  useAuthStore.getState().logout();
  throw new Error('Token refresh failed');
}
```

## Usage Examples

### **Token Validation**

```typescript
import { tokenService } from "@/lib/auth/tokenService";

// Check if token is still valid
const token = localStorage.getItem("accessToken");
if (token && tokenService.isTokenExpired(token)) {
  // Token expired, need to refresh
  const newToken = await tokenService.refreshAccessToken();
}
```

### **API Request Integration**

```typescript
// Automatic token refresh in API interceptor
api.interceptors.request.use(async (config) => {
  const token = tokenService.getValidAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### **Authentication Flow**

```typescript
// Login flow with token storage
async function login(credentials) {
  const tokens = await authApi.login(credentials);
  tokenService.setStoredTokens(tokens);
  return tokens;
}

// Logout flow with cleanup
async function logout() {
  tokenService.clearStoredTokens();
  // Additional cleanup...
}
```

## Security Features

### **Token Expiration Buffer**

- **5-minute buffer**: Refreshes tokens before actual expiration
- **Prevents race conditions**: Avoids expired token usage in API calls
- **Configurable timing**: Buffer can be adjusted based on requirements

### **Secure Storage Management**

```typescript
// Secure token storage with error handling
try {
  localStorage.setItem("refreshToken", tokens.refreshToken);
  localStorage.setItem("accessToken", tokens.accessToken);
} catch (error) {
  logger.error("Token storage failed", error);
  // Handle storage quota exceeded or other issues
}
```

### **Refresh Token Protection**

- **Single refresh process**: Prevents multiple concurrent refresh attempts
- **Queue management**: Handles multiple API calls during token refresh
- **Automatic cleanup**: Clears tokens on refresh failure

## Performance Optimization

### **Efficient Token Operations**

```typescript
// Cached token validation
private cachedTokenValidation = new Map<string, boolean>();

isTokenExpired(token: string): boolean {
  if (this.cachedTokenValidation.has(token)) {
    return this.cachedTokenValidation.get(token)!;
  }
  // Perform validation and cache result
}
```

### **Memory Management**

- **Automatic cleanup**: Refresh queue is cleared after completion
- **Limited caching**: Token validation cache prevents repeated parsing
- **State management**: Minimal memory footprint for refresh state

## Error Handling

### **Token Refresh Errors**

```typescript
// Comprehensive error classification
if (error.response?.status === 401) {
  // Refresh token expired - force logout
  this.clearStoredTokens();
  useAuthStore.getState().logout();
} else if (error.response?.status >= 500) {
  // Server error - retry with backoff
  await this.retryRefreshWithBackoff();
}
```

### **Storage Errors**

```typescript
// Graceful storage error handling
try {
  return JSON.parse(localStorage.getItem("authTokens") || "{}");
} catch (error) {
  logger.warn("Token storage corrupted, clearing", error);
  this.clearStoredTokens();
  return null;
}
```

## Related Files

- [authStore.ts](../store/authStore.ts.md) - Authentication state management
- [auth.ts](../api/auth.ts.md) - Authentication API client
- [types.ts](../api/types.ts.md) - Authentication type definitions
- [api/base.ts](../api/base.ts.md) - API client with token integration

## Development Notes

### **Testing Token Service**

```typescript
// Mock token for testing
const mockToken = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...";

// Test expiration detection
expect(tokenService.isTokenExpired(expiredToken)).toBe(true);
expect(tokenService.isTokenExpired(validToken)).toBe(false);

// Test refresh queue handling
const refreshPromise1 = tokenService.refreshAccessToken();
const refreshPromise2 = tokenService.refreshAccessToken();
// Both should resolve to the same token
```

### **Configuration Options**

```typescript
// Configurable expiration buffer
const EXPIRATION_BUFFER =
  process.env.NODE_ENV === "development"
    ? 1 * 60 // 1 minute for development
    : 5 * 60; // 5 minutes for production
```

### **Debugging and Monitoring**

- **Comprehensive logging**: All token operations are logged
- **Error tracking**: Failed refresh attempts are monitored
- **Performance metrics**: Token refresh timing and success rates
- **Security auditing**: Token access patterns and expiration events

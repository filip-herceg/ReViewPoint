# authStore.ts - Authentication State Management

## Purpose

Centralized authentication state management using Zustand store. Manages user authentication data, tokens, loading states, and provides actions for login/logout operations with comprehensive error handling.

## Key Components

### Authentication Data Models

#### AuthUser Interface
```typescript
interface AuthUser {
  id: string;
  email: string;
  name: string;
  roles: string[];
  bio?: string;
  avatar_url?: string;
  created_at?: string;
}
```

#### AuthTokens Interface
```typescript
interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}
```

### State Management

#### Core State Properties
- **user**: Current authenticated user data (AuthUser | null)
- **tokens**: Authentication tokens (AuthTokens | null)
- **isAuthenticated**: Boolean authentication status
- **isRefreshing**: Token refresh operation status
- **isLoading**: Authentication operation loading state
- **error**: Error message for failed operations

#### State Actions
- **login()**: Authenticates user with tokens and user data
- **logout()**: Clears all authentication data
- **setTokens()**: Updates authentication tokens
- **setRefreshing()**: Controls refresh operation state
- **setLoading()**: Manages loading state
- **setError()**: Sets error messages
- **clearError()**: Clears error state
- **clearTokens()**: Removes token data

## Authentication Flow

### Login Process
```typescript
login: (user, tokens) => {
  if (!user || !tokens) {
    throw new Error("User and tokens required for login");
  }
  
  logger.info("[AuthStore] User login successful", {
    userId: user.id,
    email: user.email,
  });
  
  set({
    user,
    tokens,
    isAuthenticated: true,
    isRefreshing: false,
    isLoading: false,
    error: null,
  });
}
```

### Logout Process
- **Complete State Reset**: Clears all user data and tokens
- **State Normalization**: Resets all flags to initial state
- **Logging**: Comprehensive logout event logging

## Token Management

### Token Storage
- **In-Memory Storage**: Tokens stored in Zustand state
- **Token Validation**: Validates token structure before storage
- **Automatic Cleanup**: Tokens cleared on logout or errors

### Token Refresh Integration
- **Refresh State Tracking**: `isRefreshing` flag prevents concurrent refreshes
- **API Integration**: Works with API base client for automatic refresh
- **Error Handling**: Proper error states during refresh failures

## Error Handling Strategy

### Validation Errors
- **Input Validation**: Validates user and token data on login
- **Required Field Checking**: Ensures critical fields are present
- **Type Safety**: TypeScript interfaces prevent invalid data

### State Error Management
- **Error Storage**: Centralized error message storage
- **Error Clearing**: Manual and automatic error clearing
- **Error Logging**: Comprehensive error logging with context

## Integration Points

### API Layer Integration
- **Token Service**: Provides tokens for API authentication
- **API Base Client**: Supplies authentication data for requests
- **Refresh Coordination**: Coordinates with API refresh logic

### Component Integration
- **Authentication Guards**: Used by route protection components
- **UI State**: Drives authentication-related UI states
- **Form Integration**: Connects with login/register forms

### Storage Integration
- **Persistence**: Works with localStorage for token persistence
- **Session Management**: Handles session restoration
- **Security**: Secure token handling practices

## Performance Optimizations

### State Updates
- **Selective Updates**: Only updates changed state properties
- **Batched Updates**: Efficient state change batching
- **Memory Management**: Efficient object reference handling

### Computed Values
- **Derived State**: `isAuthenticated` computed from user/token presence
- **Memoization**: Efficient state selector patterns
- **Update Optimization**: Minimal re-renders on state changes

## Security Considerations

### Token Security
- **Memory-Only Storage**: Tokens not persisted to localStorage by default
- **Automatic Cleanup**: Tokens cleared on logout
- **Validation**: Token structure validation before storage

### User Data Protection
- **Minimal Exposure**: Only necessary user data stored
- **Data Sanitization**: Safe handling of user profile data
- **Error Information**: Prevents sensitive data in error messages

## Usage Patterns

### Component Usage
```typescript
const { user, isAuthenticated, login, logout } = useAuthStore();

// Authentication check
if (!isAuthenticated) {
  return <LoginForm onLogin={login} />;
}
```

### Token Access
```typescript
const tokens = useAuthStore(state => state.tokens);
const accessToken = tokens?.access_token;
```

## Related Files

- [`tokenService`](../auth/tokenService.ts.md) - Token management and refresh logic
- [`api/base.ts`](../api/base.ts.md) - API client authentication integration
- [`components/auth/`](../../components/auth/) - Authentication UI components
- [`pages/auth/`](../../pages/auth/) - Authentication page components

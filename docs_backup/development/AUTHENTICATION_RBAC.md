# Authentication & Role-Based Access Control (RBAC) Documentation

## Overview

ReViewPoint frontend implements a comprehensive authentication system with role-based access control (RBAC) using JWT tokens, Zustand state management, and declarative React components.

## Architecture

### Core Components

1. **Authentication Store** (`src/lib/store/authStore.ts`)
   - Zustand-based state management
   - Persistent token storage
   - User session management

2. **Authentication Hook** (`src/hooks/useAuth.ts`)
   - High-level interface for auth operations
   - Role checking utilities
   - Session management

3. **Token Service** (`src/lib/auth/tokenService.ts`)
   - JWT token management
   - Automatic token refresh
   - Concurrent request handling

4. **AuthGuard Components** (`src/components/auth/AuthGuard.tsx`)
   - Declarative access control
   - Role-based conditional rendering
   - Fallback UI management

## Authentication Flow

### Login Process

```typescript
import { useAuth } from '@/hooks/useAuth';

function LoginForm() {
  const { login, isLoading, error } = useAuth();

  const handleSubmit = async (credentials) => {
    await login(credentials, rememberMe);
  };
}
```

### Token Management

- **Access Token**: Short-lived (15 minutes), used for API requests
- **Refresh Token**: Long-lived (7 days), used to obtain new access tokens
- **Auto-refresh**: Tokens are automatically refreshed before expiration
- **Concurrent Requests**: Multiple simultaneous refresh attempts are handled gracefully

### Session Persistence

- Tokens are stored in localStorage (if "Remember Me" is checked)
- Session state persists across browser restarts
- Automatic cleanup on logout or token expiration

## Role-Based Access Control

### User Roles

```typescript
enum UserRole {
  ADMIN = 'admin',
  MODERATOR = 'moderator', 
  USER = 'user',
  GUEST = 'guest'
}
```

### Role Checking

```typescript
import { useAuth } from '@/hooks/useAuth';

function Component() {
  const { hasRole, hasAnyRole } = useAuth();
  
  // Check single role
  if (hasRole('admin')) {
    // Admin-only logic
  }
  
  // Check multiple roles
  if (hasAnyRole(['admin', 'moderator'])) {
    // Admin or moderator logic
  }
}
```

## AuthGuard Components

### Basic Authentication Guards

#### RequireAuth

Renders children only if user is authenticated:

```tsx
import { RequireAuth } from '@/components/auth/AuthGuard';

<RequireAuth fallback={<LoginPrompt />}>
  <UserDashboard />
</RequireAuth>
```

#### RequireRole

Renders children only if user has specific role:

```tsx
import { RequireRole } from '@/components/auth/AuthGuard';

<RequireRole role="admin" fallback={<AccessDenied />}>
  <AdminPanel />
</RequireRole>
```

#### RequireAnyRole

Renders children if user has any of the specified roles:

```tsx
import { RequireAnyRole } from '@/components/auth/AuthGuard';

<RequireAnyRole roles={['admin', 'moderator']} fallback={<AccessDenied />}>
  <ModerationTools />
</RequireAnyRole>
```

#### RequireAllRoles

Renders children only if user has all specified roles:

```tsx
import { RequireAllRoles } from '@/components/auth/AuthGuard';

<RequireAllRoles roles={['admin', 'superuser']} fallback={<AccessDenied />}>
  <SuperAdminPanel />
</RequireAllRoles>
```

### Conditional Display Components

#### ShowForAuth / ShowForGuest

Simple conditional rendering without fallbacks:

```tsx
import { ShowForAuth, ShowForGuest } from '@/components/auth/AuthGuard';

<ShowForAuth>
  <UserMenu />
</ShowForAuth>

<ShowForGuest>
  <LoginButton />
</ShowForGuest>
```

#### ShowForRole / ShowForRoles

Role-based conditional rendering:

```tsx
import { ShowForRole, ShowForRoles } from '@/components/auth/AuthGuard';

<ShowForRole role="admin">
  <AdminButton />
</ShowForRole>

<ShowForRoles roles={['admin', 'moderator']} requireAll={false}>
  <ModerationButton />
</ShowForRoles>
```

### General Purpose AuthGuard

Flexible component for complex requirements:

```tsx
import { AuthGuard } from '@/components/auth/AuthGuard';

<AuthGuard 
  requireAuth={true}
  requireAnyRole={['admin', 'moderator']}
  fallback={<AccessDenied />}
>
  <SensitiveContent />
</AuthGuard>
```

## Route Protection

### ProtectedRoute Component

Enhanced with RBAC support:

```tsx
import { ProtectedRoute } from '@/lib/router/ProtectedRoute';

// Basic authentication
<ProtectedRoute>
  <DashboardPage />
</ProtectedRoute>

// Role-based protection
<ProtectedRoute roles={['admin']}>
  <AdminPage />
</ProtectedRoute>

// Require all roles
<ProtectedRoute roles={['admin', 'superuser']} requireAllRoles={true}>
  <SuperAdminPage />
</ProtectedRoute>
```

### Route Configuration

Routes can specify role requirements:

```typescript
// src/lib/router/routes.ts
{
  path: '/admin',
  title: 'Admin Panel',
  requiresAuth: true,
  roles: ['admin'],
  icon: 'Shield'
}
```

### Navigation Integration

Navigation automatically filters routes based on user roles:

```tsx
// Navigation component uses getRoleBasedNavigationRoutes()
const userRoles = user?.roles || [];
const navigationRoutes = getRoleBasedNavigationRoutes(userRoles);
```

## API Integration

### Authenticated Requests

All API requests automatically include authentication headers:

```typescript
// Automatic token inclusion via axios interceptors
const response = await authApi.getUser();
```

### Error Handling

Authentication errors trigger automatic logout:

- 401 Unauthorized: Invalid or expired token
- 403 Forbidden: Insufficient permissions
- Token refresh failures: Automatic logout and redirect

## Testing

### Authentication Tests

```typescript
// src/hooks/__tests__/useAuth.test.ts
describe('useAuth', () => {
  it('should login user successfully', async () => {
    // Test implementation
  });
  
  it('should check user roles correctly', () => {
    // Test role checking
  });
});
```

### AuthGuard Tests

```typescript
// src/components/auth/__tests__/AuthGuard.test.tsx
describe('AuthGuard', () => {
  it('should render children for authenticated users', () => {
    // Test authentication guard
  });
  
  it('should respect role requirements', () => {
    // Test role-based access
  });
});
```

## Security Considerations

### Token Security

- Access tokens are short-lived (15 minutes)
- Refresh tokens are HTTP-only when possible
- Automatic token cleanup on logout
- CSRF protection via SameSite cookies

### Role Validation

- Role checks are performed on both client and server
- Client-side role checks are for UX only
- Server-side validation is the source of truth
- Regular role validation on sensitive operations

### Session Management

- Automatic logout on token expiration
- Session timeout handling
- Concurrent session management
- Secure token storage practices

## Configuration

### Environment Variables

```env
# Token expiration times
VITE_ACCESS_TOKEN_EXPIRES_IN=900  # 15 minutes
VITE_REFRESH_TOKEN_EXPIRES_IN=604800  # 7 days

# API endpoints
VITE_API_BASE_URL=http://localhost:8000
VITE_AUTH_ENDPOINT=/api/auth
```

### Feature Flags

```typescript
// src/lib/config/featureFlags.ts
export const authFeatureFlags = {
  enableRememberMe: true,
  enableAutoRefresh: true,
  enableRoleBasedRouting: true,
  enableSessionPersistence: true,
};
```

## Troubleshooting

### Common Issues

1. **Token Refresh Loops**
   - Check token expiration times
   - Verify refresh endpoint functionality
   - Review concurrent request handling

2. **Role Check Failures**
   - Verify user roles are properly set
   - Check role string matching (case-sensitive)
   - Ensure role data is included in JWT payload

3. **Route Access Issues**
   - Check ProtectedRoute configuration
   - Verify role requirements in route config
   - Review navigation route filtering logic

4. **Session Persistence Problems**
   - Check localStorage permissions
   - Verify token serialization/deserialization
   - Review browser storage quotas

### Debug Mode

```typescript
// Enable debug logging
localStorage.setItem('debug', 'auth:*');

// Check authentication state
console.log('Auth state:', useAuthStore.getState());

// Verify token validity
console.log('Token valid:', tokenService.isTokenValid());
```

## Migration & Upgrades

### From Basic Auth to RBAC

1. Update user types to include roles
2. Modify authentication responses to include roles
3. Update route configurations with role requirements
4. Replace basic auth checks with role-based checks
5. Test role assignments and permissions

### Adding New Roles

1. Update UserRole enum
2. Add role to backend user model
3. Update role-based route configurations
4. Add role-specific UI components
5. Update tests for new role scenarios

## Best Practices

1. **Always validate roles on the server side**
2. **Use declarative AuthGuard components over imperative checks**
3. **Implement graceful fallbacks for unauthorized access**
4. **Keep role hierarchies simple and well-documented**
5. **Regularly audit role assignments and permissions**
6. **Test authentication flows thoroughly**
7. **Monitor authentication errors and failures**
8. **Keep tokens short-lived and refresh frequently**
9. **Implement proper logout and session cleanup**
10. **Use TypeScript for type safety in role checks**

## Examples

### Complete Login Component

```tsx
import React from 'react';
import { useAuth } from '@/hooks/useAuth';
import { RequireUnauthenticated } from '@/components/auth/AuthGuard';

function LoginPage() {
  const { login, isLoading, error } = useAuth();
  
  return (
    <RequireUnauthenticated fallback={<Navigate to="/dashboard" />}>
      <form onSubmit={handleLogin}>
        {/* Login form implementation */}
      </form>
    </RequireUnauthenticated>
  );
}
```

### Admin Dashboard with RBAC

```tsx
import React from 'react';
import { RequireRole, ShowForRole } from '@/components/auth/AuthGuard';

function AdminDashboard() {
  return (
    <RequireRole role="admin">
      <div>
        <h1>Admin Dashboard</h1>
        
        <ShowForRole role="admin">
          <AdminControls />
        </ShowForRole>
        
        <UserManagement />
        <SystemSettings />
      </div>
    </RequireRole>
  );
}
```

### Multi-Role Component

```tsx
import React from 'react';
import { RequireAnyRole, ShowForRoles } from '@/components/auth/AuthGuard';

function ModerationPanel() {
  return (
    <RequireAnyRole roles={['admin', 'moderator']}>
      <div>
        <h1>Moderation Panel</h1>
        
        <ShowForRoles roles={['admin']} requireAll={true}>
          <SuperAdminTools />
        </ShowForRoles>
        
        <ShowForRoles roles={['admin', 'moderator']} requireAll={false}>
          <ModerationTools />
        </ShowForRoles>
      </div>
    </RequireAnyRole>
  );
}
```

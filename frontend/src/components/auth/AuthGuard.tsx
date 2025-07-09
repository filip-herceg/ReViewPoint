/**
 * Authentication Guard Components
 * 
 * React components for conditional rendering based on authentication state and user roles.
 * Provides declarative authentication checks throughout the application.
 * 
 * @example
 * ```tsx
 * import { AuthGuard, RequireRole, RequireAuth } from '@/components/auth/AuthGuard';
 * 
 * // Render content only if authenticated
 * <RequireAuth fallback={<LoginPrompt />}>
 *   <UserDashboard />
 * </RequireAuth>
 * 
 * // Render content only if user has specific role
 * <RequireRole role="admin" fallback={<AccessDenied />}>
 *   <AdminPanel />
 * </RequireRole>
 * 
 * // General purpose auth guard with multiple options
 * <AuthGuard 
 *   requireAuth={true}
 *   roles={['admin', 'moderator']}
 *   fallback={<AccessDenied />}
 * >
 *   <ModeratorTools />
 * </AuthGuard>
 * ```
 */

import React from 'react';
import { useAuth } from '@/hooks/useAuth';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { ShieldX, LogIn } from 'lucide-react';
import { Link } from 'react-router-dom';

// ===========================
// Core Auth Guard Component
// ===========================

interface AuthGuardProps {
    children: React.ReactNode;
    requireAuth?: boolean;
    requireAnyRole?: string[];
    requireAllRoles?: string[];
    fallback?: React.ReactNode;
    showFallback?: boolean;
}

/**
 * General purpose authentication guard component
 * Supports both authentication and role-based checks
 */
export function AuthGuard({
    children,
    requireAuth = true,
    requireAnyRole,
    requireAllRoles,
    fallback,
    showFallback = true
}: AuthGuardProps) {
    const { isAuthenticated, hasRole, hasAnyRole } = useAuth();

    // Check authentication requirement
    if (requireAuth && !isAuthenticated) {
        if (!showFallback) return null;
        return fallback || <DefaultAuthFallback />;
    }

    // Check if user needs ANY of the specified roles
    if (requireAnyRole && requireAnyRole.length > 0) {
        if (!hasAnyRole(requireAnyRole)) {
            if (!showFallback) return null;
            return fallback || <DefaultRoleFallback requiredRoles={requireAnyRole} />;
        }
    }

    // Check if user needs ALL of the specified roles
    if (requireAllRoles && requireAllRoles.length > 0) {
        const hasAllRoles = requireAllRoles.every(role => hasRole(role));
        if (!hasAllRoles) {
            if (!showFallback) return null;
            return fallback || <DefaultRoleFallback requiredRoles={requireAllRoles} />;
        }
    }

    return <>{children}</>;
}

// ===========================
// Specialized Auth Components
// ===========================

interface RequireAuthProps {
    children: React.ReactNode;
    fallback?: React.ReactNode;
    showFallback?: boolean;
}

/**
 * Renders children only if user is authenticated
 */
export function RequireAuth({ children, fallback, showFallback = true }: RequireAuthProps) {
    return (
        <AuthGuard
            requireAuth={true}
            fallback={fallback}
            showFallback={showFallback}
        >
            {children}
        </AuthGuard>
    );
}

interface RequireRoleProps {
    children: React.ReactNode;
    role: string;
    fallback?: React.ReactNode;
    showFallback?: boolean;
}

/**
 * Renders children only if user has the specified role
 */
export function RequireRole({ children, role, fallback, showFallback = true }: RequireRoleProps) {
    return (
        <AuthGuard
            requireAuth={true}
            requireAnyRole={[role]}
            fallback={fallback}
            showFallback={showFallback}
        >
            {children}
        </AuthGuard>
    );
}

interface RequireAnyRoleProps {
    children: React.ReactNode;
    roles: string[];
    fallback?: React.ReactNode;
    showFallback?: boolean;
}

/**
 * Renders children only if user has any of the specified roles
 */
export function RequireAnyRole({ children, roles, fallback, showFallback = true }: RequireAnyRoleProps) {
    return (
        <AuthGuard
            requireAuth={true}
            requireAnyRole={roles}
            fallback={fallback}
            showFallback={showFallback}
        >
            {children}
        </AuthGuard>
    );
}

interface RequireAllRolesProps {
    children: React.ReactNode;
    roles: string[];
    fallback?: React.ReactNode;
    showFallback?: boolean;
}

/**
 * Renders children only if user has all of the specified roles
 */
export function RequireAllRoles({ children, roles, fallback, showFallback = true }: RequireAllRolesProps) {
    return (
        <AuthGuard
            requireAuth={true}
            requireAllRoles={roles}
            fallback={fallback}
            showFallback={showFallback}
        >
            {children}
        </AuthGuard>
    );
}

interface RequireUnauthenticatedProps {
    children: React.ReactNode;
    fallback?: React.ReactNode;
    showFallback?: boolean;
}

/**
 * Renders children only if user is NOT authenticated
 * Useful for login/register forms that shouldn't show to authenticated users
 */
export function RequireUnauthenticated({ children, fallback, showFallback = true }: RequireUnauthenticatedProps) {
    const { isAuthenticated } = useAuth();

    if (isAuthenticated) {
        if (!showFallback) return null;
        return fallback || <DefaultAlreadyAuthenticatedFallback />;
    }

    return <>{children}</>;
}

// ===========================
// Conditional Content Components
// ===========================

interface ShowForRoleProps {
    role: string;
    children: React.ReactNode;
}

/**
 * Simple conditional rendering for role-specific content
 * No fallback UI, just shows/hides content
 */
export function ShowForRole({ role, children }: ShowForRoleProps) {
    return (
        <RequireRole role={role} showFallback={false}>
            {children}
        </RequireRole>
    );
}

interface ShowForRolesProps {
    roles: string[];
    children: React.ReactNode;
    requireAll?: boolean;
}

/**
 * Simple conditional rendering for multiple roles
 */
export function ShowForRoles({ roles, children, requireAll = false }: ShowForRolesProps) {
    if (requireAll) {
        return (
            <RequireAllRoles roles={roles} showFallback={false}>
                {children}
            </RequireAllRoles>
        );
    }

    return (
        <RequireAnyRole roles={roles} showFallback={false}>
            {children}
        </RequireAnyRole>
    );
}

interface ShowForAuthProps {
    children: React.ReactNode;
}

/**
 * Simple conditional rendering for authenticated users
 */
export function ShowForAuth({ children }: ShowForAuthProps) {
    return (
        <RequireAuth showFallback={false}>
            {children}
        </RequireAuth>
    );
}

interface ShowForGuestProps {
    children: React.ReactNode;
}

/**
 * Simple conditional rendering for non-authenticated users (guests)
 */
export function ShowForGuest({ children }: ShowForGuestProps) {
    return (
        <RequireUnauthenticated showFallback={false}>
            {children}
        </RequireUnauthenticated>
    );
}

// ===========================
// Default Fallback Components
// ===========================

function DefaultAuthFallback() {
    return (
        <Alert className="border-blue-200 bg-blue-50">
            <LogIn className="h-4 w-4 text-blue-600" />
            <AlertDescription className="text-blue-800">
                <div className="flex items-center justify-between">
                    <span>Please sign in to access this content.</span>
                    <Button asChild size="sm" variant="outline" className="ml-4">
                        <Link to="/auth/login">Sign In</Link>
                    </Button>
                </div>
            </AlertDescription>
        </Alert>
    );
}

interface DefaultRoleFallbackProps {
    requiredRoles: string[];
}

function DefaultRoleFallback({ requiredRoles }: DefaultRoleFallbackProps) {
    const roleText = requiredRoles.length === 1
        ? `"${requiredRoles[0]}" role`
        : `one of these roles: ${requiredRoles.map(r => `"${r}"`).join(', ')}`;

    return (
        <Alert variant="destructive" className="border-red-200 bg-red-50">
            <ShieldX className="h-4 w-4" />
            <AlertDescription>
                <strong>Access Denied:</strong> You need {roleText} to access this content.
            </AlertDescription>
        </Alert>
    );
}

function DefaultAlreadyAuthenticatedFallback() {
    return (
        <Alert className="border-yellow-200 bg-yellow-50">
            <AlertDescription className="text-yellow-800">
                <div className="flex items-center justify-between">
                    <span>You are already signed in.</span>
                    <Button asChild size="sm" variant="outline" className="ml-4">
                        <Link to="/dashboard">Go to Dashboard</Link>
                    </Button>
                </div>
            </AlertDescription>
        </Alert>
    );
}

// ===========================
// Utility Hook for Auth Status
// ===========================

/**
 * Hook for getting user authentication status in components
 * Returns commonly needed auth state for conditional rendering
 */
export function useAuthStatus() {
    const auth = useAuth();

    return {
        ...auth,
        // Additional computed properties for common use cases
        isGuest: !auth.isAuthenticated,
        isAdmin: auth.hasRole('admin'),
        isModerator: auth.hasRole('moderator'),
        isUser: auth.hasRole('user'),
        canModerate: auth.hasAnyRole(['admin', 'moderator']),
        canAdministrate: auth.hasRole('admin'),
    };
}

// ===========================
// Type Exports
// ===========================

export type {
    AuthGuardProps,
    RequireAuthProps,
    RequireRoleProps,
    RequireAnyRoleProps,
    RequireAllRolesProps,
    ShowForRoleProps,
    ShowForRolesProps,
    ShowForAuthProps,
    ShowForGuestProps,
};

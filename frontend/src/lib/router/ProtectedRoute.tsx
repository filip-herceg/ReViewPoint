import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';

interface ProtectedRouteProps {
    children: React.ReactNode;
    /** Required roles (user must have ANY of these roles) */
    roles?: string[];
    /** Require ALL specified roles instead of ANY */
    requireAllRoles?: boolean;
    /** Redirect URL for unauthenticated users */
    redirectTo?: string;
    /** Redirect URL for unauthorized users (wrong role) */
    unauthorizedRedirectTo?: string;
}

/**
 * ProtectedRoute component that checks authentication and authorization before rendering children
 * Redirects to login page if user is not authenticated
 * Redirects to unauthorized page if user doesn't have required roles
 */
export function ProtectedRoute({
    children,
    roles,
    requireAllRoles = false,
    redirectTo = '/auth/login',
    unauthorizedRedirectTo = '/dashboard'
}: ProtectedRouteProps) {
    const { isAuthenticated, hasRole, hasAnyRole } = useAuth();
    const location = useLocation();

    // If not authenticated, redirect to login with return path
    if (!isAuthenticated) {
        return (
            <Navigate
                to={redirectTo}
                state={{ from: location.pathname }}
                replace
            />
        );
    }

    // If roles are specified, check if user has required role(s)
    if (roles && roles.length > 0) {
        let hasRequiredRole = false;

        if (requireAllRoles) {
            // User must have ALL specified roles
            hasRequiredRole = roles.every(role => hasRole(role));
        } else {
            // User must have ANY of the specified roles
            hasRequiredRole = hasAnyRole(roles);
        }

        if (!hasRequiredRole) {
            return (
                <Navigate
                    to={unauthorizedRedirectTo}
                    state={{
                        from: location.pathname,
                        error: `Access denied. Required role${roles.length > 1 ? 's' : ''}: ${roles.join(', ')}`
                    }}
                    replace
                />
            );
        }
    }

    return <>{children}</>;
}

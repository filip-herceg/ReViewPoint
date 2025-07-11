/**
 * Route configuration for ReViewPoint frontend
 * Defines all routes and their metadata for the application
 */

export interface RouteConfig {
    path: string;
    title: string;
    description?: string;
    requiresAuth?: boolean;
    roles?: string[];
    icon?: string;
    children?: RouteConfig[];
}

export const routes: RouteConfig[] = [
    {
        path: '/',
        title: 'Home',
        description: 'ReViewPoint dashboard and file upload interface',
        requiresAuth: false,
        icon: 'Home'
    },
    {
        path: '/dashboard',
        title: 'Dashboard',
        description: 'Overview of your uploads and reviews',
        requiresAuth: true,
        icon: 'LayoutDashboard'
    },
    {
        path: '/uploads',
        title: 'Uploads',
        description: 'Manage your file uploads',
        requiresAuth: true,
        icon: 'Upload',
        children: [
            {
                path: '/uploads/new',
                title: 'New Upload',
                description: 'Upload a new file for review'
            },
            {
                path: '/uploads/:id',
                title: 'Upload Details',
                description: 'View upload details and status'
            }
        ]
    },
    {
        path: '/reviews',
        title: 'Reviews',
        description: 'View and manage your reviews',
        requiresAuth: true,
        icon: 'FileText',
        children: [
            {
                path: '/reviews/:id',
                title: 'Review Details',
                description: 'View detailed review results'
            }
        ]
    },
    {
        path: '/admin',
        title: 'Admin Panel',
        description: 'Administrative tools and user management',
        requiresAuth: true,
        roles: ['admin'],
        icon: 'Shield',
        children: [
            {
                path: '/admin/users',
                title: 'User Management',
                description: 'Manage system users',
                requiresAuth: true,
                roles: ['admin']
            },
            {
                path: '/admin/settings',
                title: 'System Settings',
                description: 'Configure system-wide settings',
                requiresAuth: true,
                roles: ['admin']
            }
        ]
    },
    {
        path: '/moderation',
        title: 'Moderation',
        description: 'Content moderation tools',
        requiresAuth: true,
        roles: ['admin', 'moderator'],
        icon: 'UserCheck',
        children: [
            {
                path: '/moderation/flagged',
                title: 'Flagged Content',
                description: 'Review flagged uploads and content',
                requiresAuth: true,
                roles: ['admin', 'moderator']
            }
        ]
    },
    {
        path: '/auth',
        title: 'Authentication',
        description: 'Login and registration pages',
        requiresAuth: false,
        children: [
            {
                path: '/auth/login',
                title: 'Login',
                description: 'Sign in to your account'
            },
            {
                path: '/auth/register',
                title: 'Register',
                description: 'Create a new account'
            },
            {
                path: '/auth/forgot-password',
                title: 'Forgot Password',
                description: 'Reset your password'
            },
            {
                path: '/auth/reset-password',
                title: 'Reset Password',
                description: 'Set a new password'
            }
        ]
    },
    {
        path: '/profile',
        title: 'Profile',
        description: 'Manage your account settings',
        requiresAuth: true,
        icon: 'User'
    },
    {
        path: '/settings',
        title: 'Settings',
        description: 'Application preferences and configuration',
        requiresAuth: true,
        icon: 'Settings'
    },
    {
        path: '/file-dashboard-test',
        title: 'File Dashboard Test',
        description: 'Test page for file management dashboard',
        requiresAuth: true,
        icon: 'FileDigit'
    }
];

// Helper functions for route management
export function findRouteByPath(path: string): RouteConfig | undefined {
    function searchRoutes(routes: RouteConfig[]): RouteConfig | undefined {
        for (const route of routes) {
            if (route.path === path) {
                return route;
            }
            if (route.children) {
                const found = searchRoutes(route.children);
                if (found) return found;
            }
        }
        return undefined;
    }
    return searchRoutes(routes);
}

export function getAllRoutes(): RouteConfig[] {
    function flattenRoutes(routes: RouteConfig[]): RouteConfig[] {
        const result: RouteConfig[] = [];
        for (const route of routes) {
            result.push(route);
            if (route.children) {
                result.push(...flattenRoutes(route.children));
            }
        }
        return result;
    }
    return flattenRoutes(routes);
}

export function getPublicRoutes(): RouteConfig[] {
    return getAllRoutes().filter(route => !route.requiresAuth);
}

export function getProtectedRoutes(): RouteConfig[] {
    return getAllRoutes().filter(route => route.requiresAuth);
}

export function getNavigationRoutes(): RouteConfig[] {
    return routes.filter(route =>
        route.icon &&
        !route.path.startsWith('/auth') &&
        !route.path.includes(':')
    );
}

export function getRoleBasedNavigationRoutes(userRoles: string[] = []): RouteConfig[] {
    return routes.filter(route => {
        // Must have an icon to be in navigation
        if (!route.icon) return false;

        // Skip auth routes and dynamic routes
        if (route.path.startsWith('/auth') || route.path.includes(':')) {
            return false;
        }

        // If route requires roles, check if user has any required role
        if (route.roles && route.roles.length > 0) {
            return route.roles.some(requiredRole => userRoles.includes(requiredRole));
        }

        // If no specific roles required, allow
        return true;
    });
}

export function getProtectedRoutesByRole(roles: string[]): RouteConfig[] {
    return getAllRoutes().filter(route => {
        if (!route.requiresAuth) return false;
        if (!route.roles || route.roles.length === 0) return true;
        return route.roles.some(requiredRole => roles.includes(requiredRole));
    });
}



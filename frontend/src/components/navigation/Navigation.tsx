import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { getRoleBasedNavigationRoutes } from '@/lib/router/routes';
import { cn } from '@/lib/utils';
import * as Icons from 'lucide-react';

const iconMap: Record<string, React.ComponentType<any>> = {
    Home: Icons.Home,
    LayoutDashboard: Icons.LayoutDashboard,
    Upload: Icons.Upload,
    FileText: Icons.FileText,
    User: Icons.User,
    Settings: Icons.Settings,
    Shield: Icons.Shield,
    UserCheck: Icons.UserCheck,
};

export function Navigation() {
    const location = useLocation();
    const { isAuthenticated, user, logout } = useAuth();
    const userRoles = user?.roles || [];
    const navigationRoutes = getRoleBasedNavigationRoutes(userRoles);

    return (
        <nav className="flex items-center space-x-4">
            {/* Main Navigation Links */}
            <div className="hidden md:flex space-x-1">
                {navigationRoutes.map((route) => {
                    // Only show authenticated routes if user is logged in
                    if (route.requiresAuth && !isAuthenticated) {
                        return null;
                    }

                    const Icon = route.icon ? iconMap[route.icon] : null;
                    const isActive = location.pathname === route.path ||
                        (route.path !== '/' && location.pathname.startsWith(route.path));

                    return (
                        <Link
                            key={route.path}
                            to={route.path}
                            className={cn(
                                'flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors',
                                isActive
                                    ? 'bg-blue-100 text-blue-700'
                                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                            )}
                        >
                            {Icon && <Icon className="h-4 w-4 mr-2" />}
                            {route.title}
                        </Link>
                    );
                })}
            </div>

            {/* User Menu */}
            {isAuthenticated ? (
                <div className="flex items-center space-x-2">
                    <span className="text-sm text-gray-600">
                        Welcome, {user?.name || user?.email}
                    </span>
                    <Link
                        to="/profile"
                        className="flex items-center px-3 py-2 rounded-md text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100"
                    >
                        <Icons.User className="h-4 w-4 mr-1" />
                        Profile
                    </Link>
                    <button
                        onClick={logout}
                        className="px-3 py-2 text-sm font-medium text-red-600 hover:text-red-700 hover:bg-red-50 rounded-md transition-colors"
                    >
                        Logout
                    </button>
                </div>
            ) : (
                <div className="flex items-center space-x-2">
                    <Link
                        to="/auth/login"
                        className="px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
                    >
                        Login
                    </Link>
                    <Link
                        to="/auth/register"
                        className="px-3 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md transition-colors"
                    >
                        Register
                    </Link>
                </div>
            )}
        </nav>
    );
}

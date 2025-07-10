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
                                'flex items-center px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 group hover:scale-105',
                                isActive
                                    ? 'bg-primary text-primary-foreground shadow-lg shadow-primary/25'
                                    : 'text-muted-foreground hover:text-foreground hover:bg-accent/50 hover:shadow-md'
                            )}
                        >
                            {Icon && (
                                <Icon className={cn(
                                    "h-5 w-5 mr-3 transition-transform duration-200",
                                    isActive ? "text-primary-foreground" : "text-muted-foreground group-hover:text-foreground group-hover:scale-110"
                                )} />
                            )}
                            {route.title}
                        </Link>
                    );
                })}
            </div>

            {/* User Menu */}
            {isAuthenticated ? (
                <div className="flex items-center space-x-2">
                    <span className="text-sm text-muted-foreground">
                        Welcome, {user?.name || user?.email}
                    </span>
                    <Link
                        to="/profile"
                        className="flex items-center px-3 py-2 rounded-xl text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-accent/70 transition-all duration-200 hover:scale-105"
                    >
                        <Icons.User className="h-4 w-4 mr-1" />
                        Profile
                    </Link>
                    <button
                        onClick={logout}
                        className="px-3 py-2 text-sm font-medium text-destructive hover:text-destructive-foreground hover:bg-destructive/10 rounded-xl transition-all duration-200 hover:scale-105"
                    >
                        Logout
                    </button>
                </div>
            ) : (
                <div className="flex items-center space-x-2">
                    <Link
                        to="/auth/login"
                        className="px-3 py-2 text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-accent/70 rounded-xl transition-all duration-200 hover:scale-105"
                    >
                        Login
                    </Link>
                    <Link
                        to="/auth/register"
                        className="px-3 py-2 text-sm font-medium text-primary-foreground bg-primary hover:bg-primary/90 rounded-xl transition-all duration-200 hover:scale-105 hover:shadow-lg hover:shadow-primary/25"
                    >
                        Register
                    </Link>
                </div>
            )}
        </nav>
    );
}

/**
 * Enhanced AppShell Component with Sidebar
 * Responsive layout with collapsible sidebar
 * Part of Phase 4: Core UI Components
 */

import React, { useState } from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Navigation } from '@/components/navigation/Navigation';
import { Breadcrumbs } from '@/components/navigation/Breadcrumbs';
import { WebSocketStatus } from '@/components/websocket/WebSocketStatus';
import { ThemeToggle } from '@/components/ui/theme-toggle';
import { SkipLinks } from '@/components/ui/skip-links';
import { useAuth } from '@/hooks/useAuth';
import { useUIStore } from '@/lib/store/uiStore';
import { getRoleBasedNavigationRoutes } from '@/lib/router/routes';
import { ErrorBoundary } from 'react-error-boundary';
import { getErrorMessage } from '@/lib/utils/errorHandling';
import logger from '@/logger';
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

function ErrorFallback({ error }: { error: unknown }) {
    return (
        <div className="p-4 bg-red-100 border border-red-200 rounded-lg">
            <h2 className="text-lg font-semibold text-red-800 mb-2">Something went wrong</h2>
            <p className="text-red-600 mb-4">{getErrorMessage(error)}</p>
            <button
                onClick={() => window.location.reload()}
                className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
            >
                Reload page
            </button>
        </div>
    );
}

interface AppShellProps {
    children: React.ReactNode;
}

/**
 * Enhanced AppShell with Sidebar
 * Provides responsive layout with collapsible sidebar navigation
 */
export function AppShell({ children }: AppShellProps) {
    const location = useLocation();
    const { isAuthenticated, user, logout } = useAuth();
    const { sidebarOpen, setSidebarOpen } = useUIStore();
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    const userRoles = user?.roles || [];
    const navigationRoutes = getRoleBasedNavigationRoutes(userRoles);

    const toggleSidebar = () => {
        setSidebarOpen(!sidebarOpen);
        logger.info('AppShell: Sidebar toggled', { sidebarOpen: !sidebarOpen });
    };

    const toggleMobileMenu = () => {
        setMobileMenuOpen(!mobileMenuOpen);
        logger.info('AppShell: Mobile menu toggled', { mobileMenuOpen: !mobileMenuOpen });
    };

    const closeMobileMenu = () => {
        setMobileMenuOpen(false);
    };

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
            {/* Skip Links for Accessibility */}
            <SkipLinks />

            {/* Header */}
            <header
                id="header"
                className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700 fixed top-0 left-0 right-0 z-40"
            >
                <div className="px-4 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between h-16">
                        {/* Logo and Title */}
                        <div className="flex items-center">
                            {isAuthenticated && (
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={toggleSidebar}
                                    className="mr-3 md:hidden"
                                    aria-label="Toggle sidebar"
                                >
                                    <Icons.Menu className="h-5 w-5" />
                                </Button>
                            )}

                            <Link to="/" className="flex items-center space-x-2">
                                <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                                    ReViewPoint
                                </h1>
                            </Link>
                        </div>

                        {/* Desktop Navigation */}
                        <div className="hidden md:block">
                            <Navigation />
                        </div>

                        {/* Header Actions */}
                        <div className="flex items-center space-x-2">
                            <ThemeToggle variant="icon" />
                            <WebSocketStatus inline />

                            {/* Mobile Menu Button */}
                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={toggleMobileMenu}
                                className="md:hidden"
                                aria-label="Toggle mobile menu"
                            >
                                <Icons.MoreVertical className="h-5 w-5" />
                            </Button>
                        </div>
                    </div>
                </div>

                {/* Mobile Menu */}
                {mobileMenuOpen && (
                    <div className="md:hidden border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
                        <div className="px-4 py-2 space-y-1">
                            <Navigation />
                        </div>
                    </div>
                )}
            </header>

            {/* Layout Container */}
            <div className="flex pt-16">
                {/* Sidebar */}
                {isAuthenticated && (
                    <>
                        {/* Desktop Sidebar */}
                        <aside
                            id="sidebar"
                            className={cn(
                                'hidden md:flex flex-col bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 transition-all duration-200',
                                sidebarOpen ? 'w-64' : 'w-16'
                            )}
                        >
                            {/* Sidebar Header */}
                            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={toggleSidebar}
                                    className="w-full justify-start"
                                    aria-label={sidebarOpen ? 'Collapse sidebar' : 'Expand sidebar'}
                                >
                                    <Icons.PanelLeftClose className={cn(
                                        'h-5 w-5 transition-transform',
                                        !sidebarOpen && 'rotate-180'
                                    )} />
                                    {sidebarOpen && <span className="ml-2">Collapse</span>}
                                </Button>
                            </div>

                            {/* Sidebar Navigation */}
                            <nav id="navigation" className="flex-1 p-4 space-y-2">
                                {navigationRoutes.map((route) => {
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
                                                    ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-100'
                                                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-300 dark:hover:text-white dark:hover:bg-gray-700'
                                            )}
                                            title={sidebarOpen ? undefined : route.title}
                                        >
                                            {Icon && (
                                                <Icon className={cn(
                                                    'h-5 w-5 flex-shrink-0',
                                                    sidebarOpen && 'mr-3'
                                                )} />
                                            )}
                                            {sidebarOpen && (
                                                <span className="truncate">{route.title}</span>
                                            )}
                                        </Link>
                                    );
                                })}
                            </nav>

                            {/* Sidebar Footer */}
                            {sidebarOpen && (
                                <div className="p-4 border-t border-gray-200 dark:border-gray-700">
                                    <div className="flex items-center space-x-3">
                                        <div className="flex-1 min-w-0">
                                            <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                                                {user?.name || user?.email}
                                            </p>
                                            <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                                                {user?.email}
                                            </p>
                                        </div>
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            onClick={logout}
                                            aria-label="Logout"
                                        >
                                            <Icons.LogOut className="h-4 w-4" />
                                        </Button>
                                    </div>
                                </div>
                            )}
                        </aside>

                        {/* Mobile Sidebar Overlay */}
                        {sidebarOpen && (
                            <div className="md:hidden fixed inset-0 z-30 bg-black bg-opacity-50" onClick={toggleSidebar}>
                                <aside className="fixed left-0 top-16 bottom-0 w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700">
                                    <nav className="p-4 space-y-2">
                                        {navigationRoutes.map((route) => {
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
                                                    onClick={closeMobileMenu}
                                                    className={cn(
                                                        'flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors',
                                                        isActive
                                                            ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-100'
                                                            : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-300 dark:hover:text-white dark:hover:bg-gray-700'
                                                    )}
                                                >
                                                    {Icon && <Icon className="h-5 w-5 mr-3" />}
                                                    {route.title}
                                                </Link>
                                            );
                                        })}
                                    </nav>
                                </aside>
                            </div>
                        )}
                    </>
                )}

                {/* Main Content */}
                <main
                    id="main-content"
                    className={cn(
                        'flex-1 transition-all duration-200',
                        isAuthenticated && sidebarOpen ? 'md:ml-0' : '',
                        !isAuthenticated && 'w-full'
                    )}
                >
                    <div className="px-4 sm:px-6 lg:px-8 py-6">
                        {/* Breadcrumbs */}
                        <Breadcrumbs />

                        {/* Page Content */}
                        <ErrorBoundary FallbackComponent={ErrorFallback}>
                            {children}
                        </ErrorBoundary>
                    </div>
                </main>
            </div>

            {/* Footer */}
            <footer
                id="footer"
                className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 mt-12"
            >
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                    <div className="flex items-center justify-between">
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                            © 2025 ReViewPoint. All rights reserved.
                        </p>
                        <WebSocketStatus showDetails />
                    </div>
                </div>
            </footer>
        </div>
    );
}

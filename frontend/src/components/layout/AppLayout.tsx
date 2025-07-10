import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { WebSocketStatus } from '@/components/websocket/WebSocketStatus';
import { Navigation } from '@/components/navigation/Navigation';
import { Breadcrumbs } from '@/components/navigation/Breadcrumbs';
import { useWebSocketStore } from '@/lib/store/webSocketStore';
import { ErrorBoundary } from 'react-error-boundary';
import { getErrorMessage } from '@/lib/utils/errorHandling';

function ErrorFallback({ error }: { error: unknown }) {
    return (
        <div className="p-4 bg-destructive/10 border border-destructive rounded-lg">
            <h2 className="text-lg font-semibold text-destructive mb-2">Something went wrong</h2>
            <p className="text-destructive mb-4">{getErrorMessage(error)}</p>
            <button
                onClick={() => window.location.reload()}
                className="bg-destructive text-destructive-foreground hover:bg-destructive/80 px-4 py-2 rounded transition-colors"
            >
                Reload page
            </button>
        </div>
    );
}

interface AppLayoutProps {
    children: React.ReactNode;
}

export function AppLayout({ children }: AppLayoutProps) {
    const location = useLocation();
    const { connect } = useWebSocketStore();

    // Initialize WebSocket connection on layout mount
    React.useEffect(() => {
        connect();
    }, [connect]);

    return (
        <div className="min-h-screen bg-muted">
            {/* Header */}
            <header className="bg-background shadow-sm border-b border-border">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between h-16">
                        {/* Logo and Title */}
                        <div className="flex items-center">
                            <Link to="/" className="flex items-center space-x-2">
                                <h1 className="text-xl font-bold text-foreground">ReViewPoint</h1>
                            </Link>
                        </div>

                        {/* Navigation */}
                        <Navigation />

                        {/* WebSocket Status */}
                        <div className="flex items-center space-x-2">
                            <WebSocketStatus inline />
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                {/* Breadcrumbs */}
                <Breadcrumbs />

                {/* Page Content */}
                <ErrorBoundary FallbackComponent={ErrorFallback}>
                    {children}
                </ErrorBoundary>
            </main>

            {/* Footer */}
            <footer className="bg-background border-t border-border mt-12">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                    <div className="flex items-center justify-between">
                        <p className="text-sm text-muted-foreground">
                            © 2025 ReViewPoint. All rights reserved.
                        </p>
                        <WebSocketStatus showDetails />
                    </div>
                </div>
            </footer>
        </div>
    );
}

import React, { useEffect } from 'react';
import { AppRouter } from '@/lib/router/AppRouter';
import { useWebSocketStore } from '@/lib/store/webSocketStore';
import { ThemeProvider } from '@/lib/theme/theme-provider';
import { ErrorBoundary } from '@/components/ui/error-boundary';
import { Toaster } from '@/components/ui/sonner';

export default function App() {
    const { connect } = useWebSocketStore();

    // Initialize WebSocket connection on app start
    useEffect(() => {
        connect();
    }, [connect]);

    return (
        <ThemeProvider defaultTheme="light">
            <ErrorBoundary>
                <AppRouter />
                <Toaster />
            </ErrorBoundary>
        </ThemeProvider>
    );
}

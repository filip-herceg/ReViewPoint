import React, { useEffect } from 'react';
import { AppRouter } from '@/lib/router/AppRouter';
import { useWebSocketStore } from '@/lib/store/webSocketStore';
import { ErrorBoundary } from 'react-error-boundary';
import { getErrorMessage } from '@/lib/utils/errorHandling';

function ErrorFallback({ error }: { error: unknown }) {
    return (
        <div className="p-4 bg-red-100 text-red-800 rounded">
            <h2 className="font-bold">Something went wrong</h2>
            <pre className="whitespace-pre-wrap break-all">{getErrorMessage(error)}</pre>
        </div>
    );
}

export default function App() {
    const { connect } = useWebSocketStore();

    // Initialize WebSocket connection on app start
    useEffect(() => {
        connect();
    }, [connect]);

    return (
        <ErrorBoundary FallbackComponent={ErrorFallback}>
            <AppRouter />
        </ErrorBoundary>
    );
}

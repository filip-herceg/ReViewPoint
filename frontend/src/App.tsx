import React, { useEffect } from 'react';
import UploadList from '@/components/UploadList';
import UploadForm from '@/components/UploadForm';
import { WebSocketStatus } from '@/components/websocket/WebSocketStatus';
import { useWebSocketConnection } from '@/lib/websocket/hooks';
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
            <div className="p-4 max-w-2xl mx-auto">
                <div className="flex items-center justify-between mb-4">
                    <h1 className="text-2xl font-bold">ReViewPoint</h1>
                    <WebSocketStatus inline />
                </div>
                <UploadForm />
                <UploadList />
                <div className="mt-6">
                    <WebSocketStatus showDetails />
                </div>
            </div>
        </ErrorBoundary>
    );
}

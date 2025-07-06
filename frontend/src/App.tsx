import React from 'react';
import UploadList from '@/components/UploadList';
import UploadForm from '@/components/UploadForm';
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
    return (
        <ErrorBoundary FallbackComponent={ErrorFallback}>
            <div className="p-4 max-w-2xl mx-auto">
                <h1 className="text-2xl font-bold mb-4">ReViewPoint</h1>
                <UploadForm />
                <UploadList />
            </div>
        </ErrorBoundary>
    );
}

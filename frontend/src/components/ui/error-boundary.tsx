import React, { Component, ReactNode } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import logger from '@/logger';

interface ErrorBoundaryState {
    hasError: boolean;
    error?: Error;
    errorInfo?: React.ErrorInfo;
}

interface ErrorBoundaryProps {
    children: ReactNode;
    /** Custom fallback component */
    fallback?: (error: Error, errorInfo: React.ErrorInfo, retry: () => void) => ReactNode;
    /** Callback when an error occurs */
    onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
    /** Test ID for testing */
    testId?: string;
    /** Custom retry button text */
    retryText?: string;
    /** Show detailed error information (dev mode) */
    showDetails?: boolean;
}

/**
 * ErrorBoundary component to catch and handle React errors gracefully
 * Provides a fallback UI and error recovery mechanism
 */
export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
    constructor(props: ErrorBoundaryProps) {
        super(props);
        this.state = { hasError: false };
    }

    static getDerivedStateFromError(error: Error): ErrorBoundaryState {
        return {
            hasError: true,
            error,
        };
    }

    componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
        try {
            logger.error('Error boundary caught an error', {
                error: error.message,
                stack: error.stack,
                componentStack: errorInfo.componentStack,
            });

            this.setState({
                error,
                errorInfo,
            });

            this.props.onError?.(error, errorInfo);
        } catch (err) {
            // Fallback logging in case logger fails
            console.error('ErrorBoundary: Failed to log error', err);
            console.error('Original error:', error);
        }
    }

    handleRetry = () => {
        try {
            logger.info('Error boundary retry attempted');
            this.setState({ hasError: false, error: undefined, errorInfo: undefined });
        } catch (err) {
            logger.error('Error in error boundary retry', err);
        }
    };

    renderDefaultFallback() {
        const { error, errorInfo } = this.state;
        const { testId = 'error-boundary', retryText = 'Try Again', showDetails = false } = this.props;

        return (
            <div className="min-h-[200px] flex items-center justify-center p-4 bg-background text-foreground" data-testid={testId}>
                <Card className="max-w-lg w-full p-6 bg-background text-foreground border border-border">
                    <Alert variant="destructive">
                        <svg
                            className="h-4 w-4 text-destructive-foreground"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                            xmlns="http://www.w3.org/2000/svg"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.958-.833-2.728 0L4.186 18.5c-.77.833.192 2.5 1.732 2.5z"
                            />
                        </svg>
                        <AlertTitle data-testid={`${testId}-title`}>
                            Something went wrong
                        </AlertTitle>
                        <AlertDescription data-testid={`${testId}-description`}>
                            An unexpected error occurred. Please try again, and if the problem persists, contact support.
                        </AlertDescription>
                    </Alert>

                    {showDetails && error && (
                        <div className="mt-4 p-4 bg-muted text-muted-foreground rounded-md">
                            <details>
                                <summary className="text-sm font-medium cursor-pointer mb-2">
                                    Error Details
                                </summary>
                                <div className="text-xs font-mono space-y-2">
                                    <div>
                                        <strong>Error:</strong> {error.message}
                                    </div>
                                    {error.stack && (
                                        <div>
                                            <strong>Stack:</strong>
                                            <pre className="whitespace-pre-wrap mt-1">{error.stack}</pre>
                                        </div>
                                    )}
                                    {errorInfo?.componentStack && (
                                        <div>
                                            <strong>Component Stack:</strong>
                                            <pre className="whitespace-pre-wrap mt-1">{errorInfo.componentStack}</pre>
                                        </div>
                                    )}
                                </div>
                            </details>
                        </div>
                    )}

                    <div className="flex gap-2 mt-4">
                        <Button
                            onClick={this.handleRetry}
                            variant="outline"
                            data-testid={`${testId}-retry`}
                        >
                            {retryText}
                        </Button>
                        <Button
                            onClick={() => window.location.reload()}
                            variant="destructive"
                            data-testid={`${testId}-reload`}
                        >
                            Reload Page
                        </Button>
                    </div>
                </Card>
            </div>
        );
    }

    render() {
        if (this.state.hasError) {
            if (this.props.fallback && this.state.error && this.state.errorInfo) {
                return this.props.fallback(this.state.error, this.state.errorInfo, this.handleRetry);
            }
            return this.renderDefaultFallback();
        }

        return this.props.children;
    }
}

export default ErrorBoundary;

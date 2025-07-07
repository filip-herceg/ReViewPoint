import { onCLS, onINP, onLCP } from 'web-vitals';

// Sentry initialization (replace 'YOUR_DSN' with your actual DSN)
import * as Sentry from '@sentry/react';
Sentry.init({
    dsn: 'YOUR_DSN',
    tracesSampleRate: 1.0,
});

// Web Vitals reporting


import logger from './logger';
import { createTestError } from '../tests/test-templates';

function safeLogWebVital(metric: any) {
    try {
        logger.info(metric);
    } catch (err) {
        logger.error(createTestError('Web Vitals log error'));
    }
}
onCLS(safeLogWebVital);
onINP(safeLogWebVital);
onLCP(safeLogWebVital);


import './analytics';
import './index.css';


import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import { QueryClientProvider } from '@tanstack/react-query';
import { queryClient } from './lib/queryClient';

window.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('root');
    if (container) {
        const root = createRoot(container);
        root.render(
            <QueryClientProvider client={queryClient}>
                <App />
            </QueryClientProvider>
        );
    }
});

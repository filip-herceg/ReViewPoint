import { onCLS, onINP, onLCP } from 'web-vitals';

// Sentry initialization (replace 'YOUR_DSN' with your actual DSN)
import * as Sentry from '@sentry/react';
Sentry.init({
    dsn: 'YOUR_DSN',
    tracesSampleRate: 1.0,
});

// Web Vitals reporting
onCLS(console.log);
onINP(console.log);
onLCP(console.log);


import './analytics';
import './index.css';

import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';

window.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('root');
    if (container) {
        const root = createRoot(container);
        root.render(<App />);
    }
});

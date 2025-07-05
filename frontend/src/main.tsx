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
// ...existing React app bootstrap code (e.g., createRoot, render App, etc.)

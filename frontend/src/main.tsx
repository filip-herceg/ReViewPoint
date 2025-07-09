import React from 'react';
import { createRoot } from 'react-dom/client';
import { QueryClientProvider } from '@tanstack/react-query';

// Core imports
import App from './App';
import { queryClient } from '@/lib/queryClient';
import logger from '@/logger';

// Environment & Configuration
import { env, getEnvironmentConfig } from '@/lib/config/environment';
import { features, getFeatureFlags } from '@/lib/config/featureFlags';

// Monitoring systems
import { errorMonitoringService, initializeErrorMonitoring } from '@/lib/monitoring/errorMonitoring';
import { performanceMonitoringService, initializePerformanceMonitoring } from '@/lib/monitoring/performanceMonitoring';

// CSS
import './index.css';

/**
 * Initialize all core systems before app starts
 */
async function initializeApp() {
    try {
        logger.info('Starting ReViewPoint application initialization');

        // 1. Initialize environment config first
        const envConfig = getEnvironmentConfig();
        logger.debug('Environment config loaded', {
            env: envConfig.NODE_ENV,
            api: envConfig.API_BASE_URL,
            monitoring: {
                error: !!envConfig.ENABLE_ERROR_REPORTING,
                performance: !!envConfig.ENABLE_PERFORMANCE_MONITORING,
                sentry: !!envConfig.SENTRY_DSN
            }
        });

        // 2. Initialize feature flags (they are already loaded via singleton)
        const currentFeatures = getFeatureFlags();
        logger.debug('Feature flags initialized', {
            count: Object.keys(currentFeatures).length
        });

        // 3. Initialize error monitoring
        initializeErrorMonitoring();
        logger.debug('Error monitoring initialized');

        // 4. Initialize performance monitoring
        initializePerformanceMonitoring();
        logger.debug('Performance monitoring initialized');

        logger.info('Application initialization completed successfully');

    } catch (error) {
        logger.error('Failed to initialize application', error);
        // Continue with app startup even if monitoring fails
    }
}

/**
 * Render the React application
 */
function renderApp() {
    const container = document.getElementById('root');
    if (!container) {
        logger.error('Root container not found');
        return;
    }

    const root = createRoot(container);
    root.render(
        <QueryClientProvider client={queryClient}>
            <App />
        </QueryClientProvider>
    );

    logger.info('React application rendered');
}

/**
 * Main app startup
 */
window.addEventListener('DOMContentLoaded', async () => {
    await initializeApp();
    renderApp();
});

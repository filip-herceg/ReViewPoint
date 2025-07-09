import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

import { resolve } from 'path';

export default defineConfig({
    plugins: [react()],
    resolve: {
        alias: {
            '@': resolve(__dirname, 'src'),
            '@/logger': resolve(__dirname, 'src/logger.ts'),
        },
    },
    test: {
        environment: 'jsdom',
        globals: true,
        setupFiles: ['./tests/react-query-feature-flag.js', './tests/setup.ts'],
        include: ['tests/**/*.{test,spec}.{ts,tsx}'], // Restrict to test files only
        exclude: [
            'e2e/**',
            'node_modules/**',
            'dist/**',
            '**/node_modules/**',
            '**/dist/**',
            '**/.*/**',
            // PERMANENTLY EXCLUDED - DO NOT REMOVE
            'tests/lib/monitoring/errorMonitoring.test.ts', // Causes infinite loops
        ],
        env: {
            LOG_LEVEL: 'error', // Only show errors during tests
        },
        coverage: {
            reporter: ['text', 'html'],
        },
        // Remove verbose console logging
        silent: false,
        logHeapUsage: false,
        // Only show console logs for failed tests
        onConsoleLog: () => false,
        // Add timeout to prevent hanging tests
        testTimeout: 10000, // 10 seconds
        hookTimeout: 5000,  // 5 seconds for setup/teardown
    },
});

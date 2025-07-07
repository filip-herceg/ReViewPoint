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
        ],
        coverage: {
            reporter: ['text', 'html'],
        },
        onConsoleLog: (log) => {
            if (log.includes('@/')) {
                console.log('Alias resolution debug log:', log);
                console.log('Alias @ resolves to:', resolve(__dirname, 'src'));
                console.log('Alias @/logger resolves to:', resolve(__dirname, 'src/logger.ts'));
            }
        },
    },
});

import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

import { resolve } from 'path';

export default defineConfig({
    plugins: [react()],
    resolve: {
        alias: {
            '@': resolve(__dirname, 'src'),
        },
    },
    test: {
        environment: 'jsdom',
        globals: true,
        setupFiles: './tests/setup.ts',
        include: ['tests/**/*.{test,spec}.{ts,tsx}'],
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
    },
});

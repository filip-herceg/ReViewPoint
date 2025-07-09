import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tsconfigPaths from 'vite-tsconfig-paths';
import { resolve } from 'path';

export default defineConfig({
    resolve: {
        alias: {
            '@': resolve(__dirname, 'src'),
        },
    },
    plugins: [
        react(),
        tsconfigPaths(), // Add tsconfigPaths plugin for alias resolution
    ],
    server: {
        port: 5173,
        host: true
    }
});

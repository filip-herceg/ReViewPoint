import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tsconfigPaths from 'vite-tsconfig-paths';
import { resolve } from 'path';

export default defineConfig(({ mode }) => ({
    resolve: {
        alias: {
            '@': resolve(__dirname, 'src'),
        },
    },
    plugins: [
        react({
            // Configure React plugin for better development experience
            babel: {
                plugins: mode === 'development' ? [] : [],
            }
        }),
        tsconfigPaths(), // Add tsconfigPaths plugin for alias resolution
    ],
    server: {
        port: 5173,
        host: true,
    },
    build: {
        sourcemap: mode === 'development' ? 'inline' : true,
        rollupOptions: {
            output: {
                sourcemapExcludeSources: false
            }
        }
    },
    define: {
        __DEV__: JSON.stringify(mode === 'development'),
        'process.env.NODE_ENV': JSON.stringify(mode),
    },
    // Optimize dependencies to avoid source map issues
    optimizeDeps: {
        include: ['react', 'react-dom', 'react-router-dom'],
        exclude: []
    }
}));

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
        proxy: {
            '^/api/.*': {
                target: 'http://localhost:8000',
                changeOrigin: true,
                secure: false,
                ws: true,
                logLevel: 'debug',
                configure: (proxy, _options) => {
                    proxy.on('error', (err, _req, _res) => {
                        console.error('Proxy Error:', err);
                    });
                    proxy.on('proxyReq', (proxyReq, req, _res) => {
                        console.log(`[PROXY] → ${req.method} ${req.url} → ${proxyReq.getHeader('host')}${proxyReq.path}`);
                    });
                    proxy.on('proxyRes', (proxyRes, req, _res) => {
                        console.log(`[PROXY] ← ${proxyRes.statusCode} ${req.url}`);
                    });
                },
            },
        },
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

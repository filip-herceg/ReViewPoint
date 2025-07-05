import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import federation from '@originjs/vite-plugin-federation';
import { visualizer } from 'rollup-plugin-visualizer';
import csp from 'vite-plugin-csp';


import { resolve } from 'path';

export default defineConfig({
    resolve: {
        alias: {
            '@': resolve(__dirname, 'src'),
        },
    },
    plugins: [
        react(),
        federation({
            name: 'app',
            filename: 'remoteEntry.js',
            exposes: { './Button': './src/components/ui/Button.tsx' },
            remotes: {},
            shared: ['react', 'react-dom']
        }),
        visualizer({ gzipSize: true }),
        csp({
            enabled: true,
            policy: {
                'default-src': ["self"],
                'script-src': ["self"],
                'object-src': ["none"],
            }
        }),
        // Bundle analyzer removed: use visualizer for bundle analysis
    ]
});

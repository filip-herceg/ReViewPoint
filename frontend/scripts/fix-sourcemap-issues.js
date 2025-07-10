#!/usr/bin/env node

/**
 * Script to fix common source map issues in development
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

console.log('🔧 Fixing source map issues...');

// Clear Vite cache
const viteCacheDir = path.join(__dirname, '..', 'node_modules', '.vite');
if (fs.existsSync(viteCacheDir)) {
    console.log('🗑️  Clearing Vite cache...');
    fs.rmSync(viteCacheDir, { recursive: true, force: true });
}

// Clear dist directory
const distDir = path.join(__dirname, '..', 'dist');
if (fs.existsSync(distDir)) {
    console.log('🗑️  Clearing dist directory...');
    fs.rmSync(distDir, { recursive: true, force: true });
}

// Clear browser cache instructions
console.log(`
✅ Cache cleared successfully!

Next steps:
1. Restart your development server: pnpm run dev
2. Hard refresh your browser (Ctrl+Shift+R on Windows/Linux, Cmd+Shift+R on Mac)
3. Open DevTools and disable cache while DevTools is open:
   - Open DevTools (F12)
   - Go to Network tab
   - Check "Disable cache"

If the issue persists:
- Try opening your app in an incognito/private window
- Disable browser extensions temporarily
- Check if React DevTools extension is causing the issue
`);

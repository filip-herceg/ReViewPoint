#!/usr/bin/env node

import { spawn } from 'child_process';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';
import { ensurePostgresReady } from './start-postgres.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const rootDir = join(__dirname, '..');

// Set colors for output
const colors = {
    backend: '\x1b[34m', // Blue
    frontend: '\x1b[32m', // Green
    postgres: '\x1b[36m', // Cyan
    info: '\x1b[32m',     // Green
    warn: '\x1b[33m',     // Yellow
    reset: '\x1b[0m'
};

function logWithPrefix(prefix, color, data) {
    const lines = data.toString().split('\n').filter(line => line.trim());
    lines.forEach(line => {
        console.log(`${color}[${prefix}]${colors.reset} ${line}`);
    });
}

async function startServices() {
    // Check for --postgres flag
    const usePostgres = process.argv.includes('--postgres') || process.argv.includes('--pg');

    if (usePostgres) {
        console.log(`${colors.info}[INFO]${colors.reset} Starting with PostgreSQL support...`);

        try {
            await ensurePostgresReady();
        } catch (error) {
            console.log(`${colors.warn}[WARN]${colors.reset} PostgreSQL setup failed, continuing with SQLite`);
        }
    } else {
        console.log(`${colors.info}[INFO]${colors.reset} Starting with SQLite (use --postgres to enable PostgreSQL)`);
    }

    // Set environment based on database choice
    const backendEnv = {
        ...process.env,
        REVIEWPOINT_ENVIRONMENT: 'dev',
        ENV_FILE: 'config/.env'
    };

    if (usePostgres) {
        backendEnv.REVIEWPOINT_DB_URL = 'postgresql+asyncpg://postgres:postgres@localhost:5432/reviewpoint';
    }

    // Start backend
    const backend = spawn('python', ['-m', 'uvicorn', 'src.main:app', '--reload', '--host', '0.0.0.0', '--port', '8000'], {
        cwd: join(rootDir, 'backend'),
        env: backendEnv,
        shell: true
    });

    // Start frontend
    const frontend = spawn('pnpm', ['run', 'dev'], {
        cwd: join(rootDir, 'frontend'),
        shell: true
    });

    return { backend, frontend };
}

// Start services
const { backend, frontend } = await startServices();

// Handle backend output
backend.stdout.on('data', (data) => logWithPrefix('BACKEND', colors.backend, data));
backend.stderr.on('data', (data) => logWithPrefix('BACKEND', colors.backend, data));

// Handle frontend output
frontend.stdout.on('data', (data) => logWithPrefix('FRONTEND', colors.frontend, data));
frontend.stderr.on('data', (data) => logWithPrefix('FRONTEND', colors.frontend, data));

// Handle process exit
backend.on('close', (code) => {
    console.log(`${colors.backend}[BACKEND]${colors.reset} Process exited with code ${code}`);
    frontend.kill();
    process.exit(code);
});

frontend.on('close', (code) => {
    console.log(`${colors.frontend}[FRONTEND]${colors.reset} Process exited with code ${code}`);
    backend.kill();
    process.exit(code);
});

// Handle Ctrl+C
process.on('SIGINT', () => {
    console.log('\nShutting down...');
    backend.kill();
    frontend.kill();
    process.exit(0);
});

console.log(`${colors.backend}[BACKEND]${colors.reset} Starting backend server...`);
console.log(`${colors.frontend}[FRONTEND]${colors.reset} Starting frontend server...`);

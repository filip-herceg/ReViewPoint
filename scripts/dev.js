#!/usr/bin/env node

import { spawn } from 'child_process';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';
import { ensurePostgresReady } from './start-postgres.js';
import logger, { colors } from './logger.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const rootDir = join(__dirname, '..');

async function startServices() {
    // Check for --postgres flag
    let usePostgres = process.argv.includes('--postgres') || process.argv.includes('--pg');

    if (usePostgres) {
        logger.info('Starting with PostgreSQL support...');

        const postgresReady = await ensurePostgresReady();
        if (!postgresReady) {
            logger.warn('PostgreSQL setup failed, continuing with SQLite');
            usePostgres = false;
        }
    } else {
        logger.info('Starting with SQLite (use --postgres to enable PostgreSQL)');
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
    const host = process.env.HOST || 'localhost';
    const backend = spawn('hatch', ['run', 'python', '-m', 'uvicorn', 'src.main:app', '--reload', '--host', host, '--port', '8000'], {
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
backend.stdout.on('data', (data) => logger.logOutput('BACKEND', colors.backend, data));
backend.stderr.on('data', (data) => logger.logOutput('BACKEND', colors.backend, data));

// Handle frontend output
frontend.stdout.on('data', (data) => logger.logOutput('FRONTEND', colors.frontend, data));
frontend.stderr.on('data', (data) => logger.logOutput('FRONTEND', colors.frontend, data));

// Handle process exit
backend.on('close', (code) => {
    logger.backend(`Process exited with code ${code}`);
    frontend.kill();
    process.exit(code);
});

frontend.on('close', (code) => {
    logger.frontend(`Process exited with code ${code}`);
    backend.kill();
    process.exit(code);
});

// Handle Ctrl+C
process.on('SIGINT', () => {
    logger.info('Shutting down...');
    backend.kill();
    frontend.kill();
    process.exit(0);
});

logger.backend('Starting backend server...');
logger.frontend('Starting frontend server...');

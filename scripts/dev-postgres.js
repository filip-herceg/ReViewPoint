#!/usr/bin/env node

import { spawn } from 'child_process';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';
import { ensurePostgresReady } from './start-postgres.js';
import logger, { colors } from './logger.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const rootDir = join(__dirname, '..');

async function main() {
    try {
        logger.info('Starting ReViewPoint with PostgreSQL...');

        // Ensure PostgreSQL is ready
        await ensurePostgresReady();

        // Set PostgreSQL environment variables for this session
        const postgresEnv = {
            ...process.env,
            REVIEWPOINT_DB_URL: 'postgresql+asyncpg://postgres:postgres@localhost:5432/reviewpoint',
            REVIEWPOINT_ENVIRONMENT: 'dev',
            ENV_FILE: 'config/.env',
            // Feature flags - manually set to ensure they're loaded
            REVIEWPOINT_FEATURES: 'auth:register,auth:login,auth:logout,auth:refresh_token,auth:request_password_reset,auth:reset_password,auth:me,health:read',
            REVIEWPOINT_FEATURE_AUTH: 'true',
            REVIEWPOINT_FEATURE_AUTH_LOGIN: 'true',
            REVIEWPOINT_FEATURE_AUTH_REGISTER: 'true',
            REVIEWPOINT_FEATURE_HEALTH: 'true',
            REVIEWPOINT_FEATURE_HEALTH_READ: 'true',
            REVIEWPOINT_FEATURE_AUTH_REFRESH: 'true',
            REVIEWPOINT_FEATURE_AUTH_LOGOUT: 'true',
            REVIEWPOINT_FEATURE_AUTH_PASSWORD_RESET: 'true',
            REVIEWPOINT_FEATURE_AUTH_PASSWORD_RESET_CONFIRM: 'true',
            REVIEWPOINT_FEATURE_AUTH_PROFILE: 'true',
            REVIEWPOINT_FEATURE_HEALTH: 'true',
            REVIEWPOINT_FEATURE_HEALTH_READ: 'true'
        };

        // Start backend with PostgreSQL environment
        const backend = spawn('python', ['-m', 'uvicorn', 'src.main:app', '--reload', '--host', '0.0.0.0', '--port', '8000'], {
            cwd: join(rootDir, 'backend'),
            env: postgresEnv,
            shell: true
        });

        // Start frontend
        const frontend = spawn('pnpm', ['run', 'dev'], {
            cwd: join(rootDir, 'frontend'),
            shell: true
        });

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

        logger.backend('Starting backend server with PostgreSQL...');
        logger.frontend('Starting frontend server...');
        logger.info('Use Ctrl+C to stop both servers');

    } catch (error) {
        logger.error(`Failed to start with PostgreSQL: ${error.message}`);
        logger.info('Try running \'pnpm dev\' for SQLite mode instead');
        process.exit(1);
    }
}

main().catch((error) => {
    logger.error(error.message);
    process.exit(1);
});

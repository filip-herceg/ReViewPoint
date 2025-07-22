#!/usr/bin/env node

import { spawn } from 'child_process';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';
import { readFileSync } from 'fs';
import { ensurePostgresReady } from './start-postgres.js';
import logger from './logger.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const rootDir = join(__dirname, '..');

async function runMigrationsWithAutoSetup(migrationArgs = ['upgrade', 'head']) {
    try {
        logger.info('Preparing to run database migrations...');

        // Check if we should use PostgreSQL by reading the .env file
        const envPath = join(rootDir, 'backend/config/.env');
        let usePostgres = false;

        try {
            const envContent = readFileSync(envPath, 'utf8');
            usePostgres = envContent.includes('postgresql+asyncpg://');

            if (usePostgres) {
                logger.info('PostgreSQL detected in configuration');
            } else {
                logger.info('SQLite detected in configuration');
            }
        } catch (error) {
            logger.warn('Could not read .env file, assuming SQLite mode');
        }

        let migrationEnv = { ...process.env };

        if (usePostgres) {
            logger.info('Ensuring PostgreSQL container is ready...');

            try {
                await ensurePostgresReady();
                logger.success('PostgreSQL container is ready!');

                // Set PostgreSQL environment variables for migrations
                migrationEnv = {
                    ...process.env,
                    REVIEWPOINT_DB_URL: 'postgresql+asyncpg://postgres:postgres@localhost:5432/reviewpoint',
                    REVIEWPOINT_ENVIRONMENT: 'dev',
                    ENV_FILE: 'config/.env'
                };

                logger.backend('Running migrations with PostgreSQL environment...');
            } catch (error) {
                logger.error(`PostgreSQL setup failed: ${error.message}`);
                logger.warn('Falling back to current configuration...');
            }
        } else {
            logger.backend('Running migrations with current configuration...');
        }

        // Run migrations
        const alembicArgs = ['run', 'python', '-m', 'alembic', ...migrationArgs];
        const migration = spawn('hatch', alembicArgs, {
            cwd: join(rootDir, 'backend'),
            env: migrationEnv,
            stdio: 'inherit'
        });

        migration.on('close', (code) => {
            if (code === 0) {
                logger.success('Migrations completed successfully!');
            } else {
                logger.error(`Migrations failed with exit code ${code}`);
            }
            process.exit(code);
        });

        migration.on('error', (error) => {
            logger.error(`Migration process error: ${error.message}`);
            process.exit(1);
        });

        // Handle Ctrl+C gracefully
        process.on('SIGINT', () => {
            logger.info('Stopping migrations...');
            migration.kill('SIGINT');
            process.exit(0);
        });

    } catch (error) {
        logger.error(`Failed to run migrations: ${error.message}`);
        process.exit(1);
    }
}

// Parse command line arguments
const args = process.argv.slice(2);
const migrationArgs = args.length > 0 ? args : ['upgrade', 'head'];

runMigrationsWithAutoSetup(migrationArgs).catch((error) => {
    logger.error(error.message);
    process.exit(1);
});

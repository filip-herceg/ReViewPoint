#!/usr/bin/env node

import { spawn, exec } from 'child_process';
import { promisify } from 'util';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';
import logger from './logger.js';

const execAsync = promisify(exec);

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const rootDir = join(__dirname, '..');

async function checkDockerRunning() {
    try {
        await execAsync('docker info');
        return true;
    } catch (error) {
        return false;
    }
}

async function checkPostgresContainer() {
    try {
        const { stdout } = await execAsync('docker ps --format "{{.Names}}" | grep reviewpoint_postgres');
        return stdout.trim() === 'reviewpoint_postgres';
    } catch (error) {
        return false;
    }
}

async function isPostgresHealthy() {
    try {
        // Check if container is healthy
        const { stdout } = await execAsync('docker inspect reviewpoint_postgres --format="{{.State.Health.Status}}"');
        return stdout.trim() === 'healthy';
    } catch (error) {
        return false;
    }
}

async function startPostgresContainer() {
    return new Promise((resolve, reject) => {
        logger.postgres('Starting PostgreSQL container...');

        const dockerCompose = spawn('docker', [
            'compose',
            '-f', 'backend/deployment/docker-compose.yml',
            'up', '-d', 'postgres'
        ], {
            cwd: rootDir,
            stdio: 'pipe'
        });

        let output = '';
        dockerCompose.stdout.on('data', (data) => {
            output += data.toString();
        });

        dockerCompose.stderr.on('data', (data) => {
            output += data.toString();
        });

        dockerCompose.on('close', (code) => {
            if (code === 0) {
                logger.postgres('Container started successfully');
                resolve();
            } else {
                logger.error(`Container failed to start (exit code: ${code})`);
                logger.error(output);
                reject(new Error(`Docker compose failed with exit code ${code}`));
            }
        });
    });
}

async function waitForPostgresHealthy() {
    logger.postgres('Waiting for PostgreSQL to be healthy...');

    for (let i = 0; i < 30; i++) {
        if (await isPostgresHealthy()) {
            logger.success('PostgreSQL is healthy and ready!');
            return true;
        }

        if (i % 5 === 0) {
            logger.postgres(`Still waiting for PostgreSQL... (${i}/30)`);
        }

        await new Promise(resolve => setTimeout(resolve, 1000));
    }

    throw new Error('PostgreSQL did not become healthy within 30 seconds');
}

async function runMigrations() {
    return new Promise((resolve, reject) => {
        logger.postgres('Running database migrations...');

        const migration = spawn('python', ['-m', 'alembic', 'upgrade', 'head'], {
            cwd: join(rootDir, 'backend'),
            env: {
                ...process.env,
                REVIEWPOINT_DB_URL: 'postgresql+asyncpg://postgres:postgres@localhost:5432/reviewpoint',
                REVIEWPOINT_ENVIRONMENT: 'dev'
            },
            stdio: 'pipe'
        });

        let output = '';
        migration.stdout.on('data', (data) => {
            output += data.toString();
        });

        migration.stderr.on('data', (data) => {
            output += data.toString();
        });

        migration.on('close', (code) => {
            if (code === 0) {
                logger.success('Database migrations completed successfully');
                resolve();
            } else {
                // Check if this is just a "no changes" or "already applied" scenario
                if (output.includes('No new upgrade operations to perform') ||
                    output.includes('already exists')) {
                    logger.info('Database schema is already up to date');
                    resolve();
                } else {
                    logger.error(`Migration failed (exit code: ${code})`);
                    logger.error(output);
                    reject(new Error(`Migration failed with exit code ${code}`));
                }
            }
        });
    });
}

export async function ensurePostgresReady() {
    try {
        // Check if Docker is running
        if (!(await checkDockerRunning())) {
            logger.error('Docker is not running. Please start Docker Desktop.');
            throw new Error('Docker is not running');
        }

        // Check if PostgreSQL container is already running
        if (await checkPostgresContainer()) {
            logger.info('PostgreSQL container already running');

            // Check if it's healthy
            if (await isPostgresHealthy()) {
                logger.info('PostgreSQL is healthy');
            } else {
                await waitForPostgresHealthy();
            }
        } else {
            // Start the container
            await startPostgresContainer();
            await waitForPostgresHealthy();
        }

        // Run migrations with explicit environment
        await runMigrations();

        logger.success('PostgreSQL setup complete! 🐘');
        return true;

    } catch (error) {
        logger.error(`PostgreSQL setup failed: ${error.message}`);
        logger.warn('Falling back to SQLite for development');
        return false;
    }
}

// If this script is run directly
if (import.meta.url === `file://${process.argv[1]}`) {
    ensurePostgresReady()
        .then(() => {
            process.exit(0);
        })
        .catch(() => {
            process.exit(1);
        });
}

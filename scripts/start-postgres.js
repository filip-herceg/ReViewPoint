#!/usr/bin/env node

import { spawn, exec } from 'child_process';
import { promisify } from 'util';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';
import { readFileSync, writeFileSync } from 'fs';

const execAsync = promisify(exec);

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const rootDir = join(__dirname, '..');

const colors = {
    postgres: '\x1b[36m', // Cyan
    info: '\x1b[32m',     // Green
    warn: '\x1b[33m',     // Yellow
    error: '\x1b[31m',    // Red
    reset: '\x1b[0m'
};

function log(prefix, color, message) {
    console.log(`${color}[${prefix}]${colors.reset} ${message}`);
}

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
        log('POSTGRES', colors.postgres, 'Starting PostgreSQL container...');

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
                log('POSTGRES', colors.postgres, 'Container started successfully');
                resolve();
            } else {
                log('POSTGRES', colors.error, `Container failed to start (exit code: ${code})`);
                log('POSTGRES', colors.error, output);
                reject(new Error(`Docker compose failed with exit code ${code}`));
            }
        });
    });
}

async function waitForPostgresHealthy() {
    log('POSTGRES', colors.postgres, 'Waiting for PostgreSQL to be healthy...');

    for (let i = 0; i < 30; i++) {
        if (await isPostgresHealthy()) {
            log('POSTGRES', colors.info, 'PostgreSQL is healthy and ready!');
            return true;
        }

        if (i % 5 === 0) {
            log('POSTGRES', colors.postgres, `Still waiting for PostgreSQL... (${i}/30)`);
        }

        await new Promise(resolve => setTimeout(resolve, 1000));
    }

    throw new Error('PostgreSQL did not become healthy within 30 seconds');
}

async function updateEnvToPostgreSQL() {
    const envPath = join(rootDir, 'backend/config/.env');

    try {
        let envContent = readFileSync(envPath, 'utf8');

        // Replace SQLite URL with PostgreSQL URL
        const postgresUrl = 'postgresql+asyncpg://postgres:postgres@localhost:5432/reviewpoint';
        envContent = envContent.replace(
            /^REVIEWPOINT_DB_URL=.*$/m,
            `REVIEWPOINT_DB_URL=${postgresUrl}`
        );

        writeFileSync(envPath, envContent, 'utf8');
        log('POSTGRES', colors.info, 'Updated .env to use PostgreSQL');

        return postgresUrl;
    } catch (error) {
        log('POSTGRES', colors.error, `Failed to update .env file: ${error.message}`);
        throw error;
    }
}

async function runMigrations() {
    return new Promise((resolve, reject) => {
        log('POSTGRES', colors.postgres, 'Running database migrations...');

        const migration = spawn('python', ['-m', 'alembic', 'upgrade', 'head'], {
            cwd: join(rootDir, 'backend'),
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
                log('POSTGRES', colors.info, 'Database migrations completed successfully');
                resolve();
            } else {
                log('POSTGRES', colors.error, `Migration failed (exit code: ${code})`);
                log('POSTGRES', colors.error, output);
                reject(new Error(`Migration failed with exit code ${code}`));
            }
        });
    });
}

export async function ensurePostgresReady() {
    try {
        // Check if Docker is running
        if (!(await checkDockerRunning())) {
            log('POSTGRES', colors.error, 'Docker is not running. Please start Docker Desktop.');
            throw new Error('Docker is not running');
        }

        // Check if PostgreSQL container is already running
        if (await checkPostgresContainer()) {
            log('POSTGRES', colors.info, 'PostgreSQL container already running');

            // Check if it's healthy
            if (await isPostgresHealthy()) {
                log('POSTGRES', colors.info, 'PostgreSQL is healthy');
            } else {
                await waitForPostgresHealthy();
            }
        } else {
            // Start the container
            await startPostgresContainer();
            await waitForPostgresHealthy();
        }

        // Update environment to use PostgreSQL
        await updateEnvToPostgreSQL();

        // Run migrations
        await runMigrations();

        log('POSTGRES', colors.info, 'PostgreSQL setup complete! 🐘');
        return true;

    } catch (error) {
        log('POSTGRES', colors.error, `PostgreSQL setup failed: ${error.message}`);
        log('POSTGRES', colors.warn, 'Falling back to SQLite for development');
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

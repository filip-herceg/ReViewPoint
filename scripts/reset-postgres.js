#!/usr/bin/env node

import { spawn } from 'child_process';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

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

async function runCommand(command, args, description) {
    return new Promise((resolve, reject) => {
        log('POSTGRES', colors.postgres, description);

        const process = spawn(command, args, {
            cwd: rootDir,
            stdio: 'pipe',
            shell: true
        });

        let output = '';
        process.stdout.on('data', (data) => {
            output += data.toString();
        });

        process.stderr.on('data', (data) => {
            output += data.toString();
        });

        process.on('close', (code) => {
            if (code === 0) {
                log('POSTGRES', colors.info, `${description} - Success`);
                resolve();
            } else {
                log('POSTGRES', colors.error, `${description} - Failed (exit code: ${code})`);
                log('POSTGRES', colors.error, output);
                reject(new Error(`Command failed with exit code ${code}`));
            }
        });
    });
}

async function resetPostgres() {
    try {
        log('POSTGRES', colors.warn, 'WARNING: This will completely reset the PostgreSQL database and remove all data!');

        // Stop and remove containers with volumes
        await runCommand('docker', [
            'compose', '-f', 'backend/deployment/docker-compose.yml',
            'down', '-v'
        ], 'Stopping containers and removing volumes...');

        // Start fresh PostgreSQL container
        await runCommand('docker', [
            'compose', '-f', 'backend/deployment/docker-compose.yml',
            'up', '-d', 'postgres'
        ], 'Starting fresh PostgreSQL container...');

        log('POSTGRES', colors.info, 'PostgreSQL database has been completely reset! 🐘');
        log('POSTGRES', colors.info, 'You can now run your development tasks with a clean database.');

    } catch (error) {
        log('POSTGRES', colors.error, `Failed to reset PostgreSQL: ${error.message}`);
        process.exit(1);
    }
}

resetPostgres();

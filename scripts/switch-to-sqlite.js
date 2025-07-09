#!/usr/bin/env node

import { readFileSync, writeFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const rootDir = join(__dirname, '..');

const colors = {
    info: '\x1b[32m',     // Green
    warn: '\x1b[33m',     // Yellow
    reset: '\x1b[0m'
};

function log(message) {
    console.log(`${colors.info}[SQLITE]${colors.reset} ${message}`);
}

function updateEnvToSQLite() {
    const envPath = join(rootDir, 'backend/config/.env');

    try {
        let envContent = readFileSync(envPath, 'utf8');

        // Replace PostgreSQL URL with SQLite URL
        const sqliteUrl = 'sqlite+aiosqlite:///./reviewpoint_dev.db';
        envContent = envContent.replace(
            /^REVIEWPOINT_DB_URL=.*$/m,
            `REVIEWPOINT_DB_URL=${sqliteUrl}`
        );

        writeFileSync(envPath, envContent, 'utf8');
        log('Updated .env to use SQLite');

        return sqliteUrl;
    } catch (error) {
        console.log(`${colors.warn}[SQLITE]${colors.reset} Failed to update .env file: ${error.message}`);
        throw error;
    }
}

export function switchToSQLite() {
    updateEnvToSQLite();
    log('Switched to SQLite database configuration');
}

// If this script is run directly
if (import.meta.url === `file://${process.argv[1]}`) {
    try {
        switchToSQLite();
        process.exit(0);
    } catch (error) {
        console.error(`${colors.warn}[SQLITE]${colors.reset} Failed: ${error.message}`);
        process.exit(1);
    }
}

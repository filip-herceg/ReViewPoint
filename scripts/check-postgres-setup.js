#!/usr/bin/env node

import { execSync } from 'child_process';

const colors = {
    info: '\x1b[32m',     // Green
    warn: '\x1b[33m',     // Yellow
    error: '\x1b[31m',    // Red
    reset: '\x1b[0m'
};

function log(level, message) {
    console.log(`${colors[level]}[${level.toUpperCase()}]${colors.reset} ${message}`);
}

function checkRequirement(name, command, expectedText = '') {
    try {
        const output = execSync(command, { encoding: 'utf8', stdio: 'pipe' });
        if (expectedText && !output.includes(expectedText)) {
            throw new Error(`Unexpected output: ${output}`);
        }
        log('info', `✅ ${name} is available`);
        return true;
    } catch (error) {
        log('error', `❌ ${name} is not available: ${error.message}`);
        return false;
    }
}

console.log('🔍 Checking PostgreSQL Auto-Setup Prerequisites...\n');

let allGood = true;

// Check Node.js
allGood &= checkRequirement('Node.js', 'node --version', 'v');

// Check Docker
allGood &= checkRequirement('Docker', 'docker --version', 'Docker version');

// Check if Docker is running
allGood &= checkRequirement('Docker daemon', 'docker info');

// Check if docker-compose is available
allGood &= checkRequirement('Docker Compose', 'docker compose version');

// Check Python
allGood &= checkRequirement('Python', 'python --version', 'Python');

// Check if backend directory exists
try {
    const fs = await import('fs');
    if (!fs.existsSync('./backend')) {
        throw new Error('Backend directory not found');
    }
    log('info', '✅ Backend directory exists');
} catch (error) {
    log('error', `❌ Backend directory check failed: ${error.message}`);
    allGood = false;
}

console.log();

if (allGood) {
    log('info', '🎉 All prerequisites are met! You can use:');
    console.log('   - pnpm dev:postgres  (Auto PostgreSQL + development)');
    console.log('   - pnpm postgres:start  (PostgreSQL only)');
    console.log('   - pnpm dev  (SQLite development)');
} else {
    log('warn', '⚠️  Some prerequisites are missing. PostgreSQL auto-setup may not work.');
    log('info', 'You can still use SQLite development with: pnpm dev');
}

console.log('\nFor more info, see: docs/POSTGRES_SETUP.md');

#!/usr/bin/env node

import { execSync } from 'child_process';
import logger from './logger.js';

function checkRequirement(name, command, expectedText = '') {
    try {
        const output = execSync(command, { encoding: 'utf8', stdio: 'pipe' });
        if (expectedText && !output.includes(expectedText)) {
            throw new Error(`Unexpected output: ${output}`);
        }
        logger.success(`✅ ${name} is available`);
        return true;
    } catch (error) {
        logger.error(`❌ ${name} is not available: ${error.message}`);
        return false;
    }
}

logger.info('🔍 Checking PostgreSQL Auto-Setup Prerequisites...\n');

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
    logger.success('✅ Backend directory exists');
} catch (error) {
    logger.error(`❌ Backend directory check failed: ${error.message}`);
    allGood = false;
}

if (allGood) {
    logger.success('🎉 All prerequisites are met! You can use:');
    logger.info('   - pnpm dev:postgres  (Auto PostgreSQL + development)');
    logger.info('   - pnpm postgres:start  (PostgreSQL only)');
    logger.info('   - pnpm dev  (SQLite development)');
} else {
    logger.warn('⚠️  Some prerequisites are missing. PostgreSQL auto-setup may not work.');
    logger.info('You can still use SQLite development with: pnpm dev');
}

logger.info('\nFor more info, see: docs/POSTGRES_SETUP.md');

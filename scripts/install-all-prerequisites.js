#!/usr/bin/env node

/**
 * Complete Prerequisites Installer for Windows
 * Installs ALL required tools for ReViewPoint on a fresh Windows machine
 * 
 * This script is designed to run on a completely fresh Windows machine
 * with only Node.js installed (which is needed to run this script)
 */

import { execSync, spawn } from 'child_process';
import { promisify } from 'util';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// ANSI color codes for Windows PowerShell
const colors = {
    red: '\x1b[31m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    magenta: '\x1b[35m',
    cyan: '\x1b[36m',
    white: '\x1b[37m',
    reset: '\x1b[0m',
    bold: '\x1b[1m'
};

class Logger {
    static success(message) {
        console.log(`${colors.green}✅ ${message}${colors.reset}`);
    }
    
    static error(message) {
        console.log(`${colors.red}❌ ${message}${colors.reset}`);
    }
    
    static warning(message) {
        console.log(`${colors.yellow}⚠️  ${message}${colors.reset}`);
    }
    
    static info(message) {
        console.log(`${colors.blue}ℹ️  ${message}${colors.reset}`);
    }
    
    static step(message) {
        console.log(`${colors.cyan}🔧 ${message}${colors.reset}`);
    }
    
    static header(message) {
        console.log(`\n${colors.bold}${colors.magenta}=== ${message} ===${colors.reset}\n`);
    }
}

class PrerequisiteInstaller {
    constructor() {
        this.isWindows = process.platform === 'win32';
        this.installedTools = new Set();
        this.failedTools = new Set();
    }

    async checkCommand(command, name) {
        try {
            execSync(command, { stdio: 'pipe', encoding: 'utf8' });
            Logger.success(`${name} is already installed`);
            this.installedTools.add(name);
            return true;
        } catch (error) {
            Logger.warning(`${name} is not installed or not in PATH`);
            return false;
        }
    }

    async installViaPowerShell(command, name) {
        try {
            Logger.step(`Installing ${name}...`);
            execSync(`powershell -Command "${command}"`, { 
                stdio: 'inherit',
                encoding: 'utf8'
            });
            Logger.success(`${name} installed successfully`);
            this.installedTools.add(name);
            return true;
        } catch (error) {
            Logger.error(`Failed to install ${name}: ${error.message}`);
            this.failedTools.add(name);
            return false;
        }
    }

    async installViaChocolatey(packageName, name) {
        try {
            Logger.step(`Installing ${name} via Chocolatey...`);
            execSync(`choco install ${packageName} -y`, { 
                stdio: 'inherit',
                encoding: 'utf8'
            });
            Logger.success(`${name} installed successfully via Chocolatey`);
            this.installedTools.add(name);
            return true;
        } catch (error) {
            Logger.error(`Failed to install ${name} via Chocolatey: ${error.message}`);
            this.failedTools.add(name);
            return false;
        }
    }

    async installChocolatey() {
        if (await this.checkCommand('choco --version', 'Chocolatey')) {
            return true;
        }

        Logger.step('Installing Chocolatey package manager...');
        const chocoInstallCommand = `
            Set-ExecutionPolicy Bypass -Scope Process -Force; 
            [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; 
            iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        `;

        return await this.installViaPowerShell(chocoInstallCommand, 'Chocolatey');
    }

    async checkAndInstallGit() {
        if (await this.checkCommand('git --version', 'Git')) return true;
        
        Logger.info('Git is required for cloning repositories');
        return await this.installViaChocolatey('git', 'Git');
    }

    async checkAndInstallNodeJS() {
        if (await this.checkCommand('node --version', 'Node.js')) {
            // Check if version is >= 18
            try {
                const version = execSync('node --version', { encoding: 'utf8' }).trim();
                const majorVersion = parseInt(version.replace('v', '').split('.')[0]);
                if (majorVersion >= 18) {
                    Logger.success(`Node.js ${version} is compatible`);
                    return true;
                } else {
                    Logger.warning(`Node.js ${version} is too old, need >= 18`);
                }
            } catch (error) {
                Logger.error('Could not determine Node.js version');
            }
        }
        
        Logger.info('Node.js 18+ is required for the frontend');
        return await this.installViaChocolatey('nodejs', 'Node.js');
    }

    async checkAndInstallPnpm() {
        if (await this.checkCommand('pnpm --version', 'pnpm')) return true;
        
        Logger.step('Installing pnpm package manager...');
        try {
            execSync('npm install -g pnpm', { stdio: 'inherit' });
            Logger.success('pnpm installed successfully');
            this.installedTools.add('pnpm');
            return true;
        } catch (error) {
            Logger.error(`Failed to install pnpm: ${error.message}`);
            this.failedTools.add('pnpm');
            return false;
        }
    }

    async checkAndInstallPython() {
        if (await this.checkCommand('python --version', 'Python')) {
            // Check if version is >= 3.11
            try {
                const version = execSync('python --version', { encoding: 'utf8' }).trim();
                const versionMatch = version.match(/Python (\d+)\.(\d+)/);
                if (versionMatch) {
                    const major = parseInt(versionMatch[1]);
                    const minor = parseInt(versionMatch[2]);
                    if (major === 3 && minor >= 11) {
                        Logger.success(`${version} is compatible`);
                        return true;
                    } else {
                        Logger.warning(`${version} is too old, need Python 3.11+`);
                    }
                }
            } catch (error) {
                Logger.error('Could not determine Python version');
            }
        }
        
        Logger.info('Python 3.11+ is required for the backend');
        return await this.installViaChocolatey('python', 'Python');
    }

    async checkAndInstallPipx() {
        if (await this.checkCommand('pipx --version', 'pipx')) return true;
        
        Logger.step('Installing pipx...');
        try {
            execSync('python -m pip install --user pipx', { stdio: 'inherit' });
            execSync('python -m pipx ensurepath', { stdio: 'inherit' });
            Logger.success('pipx installed successfully');
            this.installedTools.add('pipx');
            return true;
        } catch (error) {
            Logger.error(`Failed to install pipx: ${error.message}`);
            this.failedTools.add('pipx');
            return false;
        }
    }

    async checkAndInstallHatch() {
        if (await this.checkCommand('hatch --version', 'Hatch')) return true;
        
        Logger.step('Installing Hatch...');
        try {
            execSync('pipx install hatch', { stdio: 'inherit' });
            Logger.success('Hatch installed successfully');
            this.installedTools.add('Hatch');
            return true;
        } catch (error) {
            Logger.error(`Failed to install Hatch: ${error.message}`);
            this.failedTools.add('Hatch');
            return false;
        }
    }

    async checkAndInstallDocker() {
        if (await this.checkCommand('docker --version', 'Docker')) {
            // Check if Docker daemon is running
            try {
                execSync('docker info', { stdio: 'pipe' });
                Logger.success('Docker is installed and running');
                return true;
            } catch (error) {
                Logger.warning('Docker is installed but not running');
                Logger.info('Please start Docker Desktop manually');
                return false;
            }
        }
        
        Logger.info('Docker Desktop is required for PostgreSQL (optional)');
        Logger.warning('Docker Desktop cannot be installed automatically');
        Logger.info('Please download and install from: https://docker.com/products/docker-desktop/');
        this.failedTools.add('Docker Desktop');
        return false;
    }

    async refreshEnvironment() {
        Logger.step('Refreshing environment variables...');
        
        if (this.isWindows) {
            try {
                // Refresh PATH for current session
                execSync('refreshenv', { stdio: 'pipe' });
            } catch (error) {
                // refreshenv might not be available, that's ok
                Logger.info('Environment refresh completed (restart terminal if needed)');
            }
        }
    }

    async verifyInstallation() {
        Logger.header('Verification Phase');
        
        const tools = [
            { command: 'git --version', name: 'Git' },
            { command: 'node --version', name: 'Node.js' },
            { command: 'pnpm --version', name: 'pnpm' },
            { command: 'python --version', name: 'Python' },
            { command: 'pipx --version', name: 'pipx' },
            { command: 'hatch --version', name: 'Hatch' },
            { command: 'docker --version', name: 'Docker' }
        ];

        let allVerified = true;
        for (const tool of tools) {
            const verified = await this.checkCommand(tool.command, tool.name);
            if (!verified) allVerified = false;
        }

        return allVerified;
    }

    async installAllPrerequisites() {
        Logger.header('ReViewPoint Prerequisites Installer');
        Logger.info('This will install ALL required tools for ReViewPoint development');
        Logger.warning('Administrator privileges may be required');
        
        if (!this.isWindows) {
            Logger.error('This installer is designed for Windows only');
            process.exit(1);
        }

        // Phase 1: Install package managers
        Logger.header('Phase 1: Package Managers');
        await this.installChocolatey();
        
        // Phase 2: Core development tools
        Logger.header('Phase 2: Core Development Tools');
        await this.checkAndInstallGit();
        await this.checkAndInstallNodeJS();
        await this.checkAndInstallPnpm();
        await this.checkAndInstallPython();
        await this.checkAndInstallPipx();
        await this.checkAndInstallHatch();
        
        // Phase 3: Optional tools
        Logger.header('Phase 3: Optional Tools');
        await this.checkAndInstallDocker();
        
        // Phase 4: Environment refresh
        await this.refreshEnvironment();
        
        // Phase 5: Verification
        const allVerified = await this.verifyInstallation();
        
        // Summary
        Logger.header('Installation Summary');
        
        if (this.installedTools.size > 0) {
            Logger.success(`Successfully installed: ${Array.from(this.installedTools).join(', ')}`);
        }
        
        if (this.failedTools.size > 0) {
            Logger.error(`Failed to install: ${Array.from(this.failedTools).join(', ')}`);
            Logger.info('Please install these tools manually:');
            
            if (this.failedTools.has('Docker Desktop')) {
                Logger.info('- Docker Desktop: https://docker.com/products/docker-desktop/');
            }
        }
        
        if (allVerified) {
            Logger.success('🎉 All prerequisites are now installed!');
            Logger.info('You can now run: pnpm run dev:postgres');
        } else {
            Logger.warning('Some tools may need manual installation or PATH refresh');
            Logger.info('Try restarting your terminal and running this script again');
        }
        
        return allVerified;
    }
}

// Main execution
async function main() {
    const installer = new PrerequisiteInstaller();
    
    try {
        await installer.installAllPrerequisites();
    } catch (error) {
        Logger.error(`Installation failed: ${error.message}`);
        process.exit(1);
    }
}

// Only run if this file is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
    main();
}

export default PrerequisiteInstaller;

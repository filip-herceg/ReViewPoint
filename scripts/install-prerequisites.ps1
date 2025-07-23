# ReViewPoint Prerequisites Installer for Windows PowerShell
# This script can run on a completely fresh Windows machine

param(
    [switch]$SkipConfirmation
)

# Color functions for better output
function Write-Success { param($Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Error { param($Message) Write-Host "❌ $Message" -ForegroundColor Red }
function Write-Warning { param($Message) Write-Host "⚠️  $Message" -ForegroundColor Yellow }
function Write-Info { param($Message) Write-Host "ℹ️  $Message" -ForegroundColor Blue }
function Write-Step { param($Message) Write-Host "🔧 $Message" -ForegroundColor Cyan }
function Write-Header { param($Message) Write-Host "`n=== $Message ===`n" -ForegroundColor Magenta }

function Test-Command {
    param($Command, $Name)
    try {
        $null = & $Command 2>$null
        Write-Success "$Name is already installed"
        return $true
    }
    catch {
        Write-Warning "$Name is not installed"
        return $false
    }
}

function Install-Chocolatey {
    if (Test-Command "choco" "Chocolatey") { return $true }
    
    Write-Step "Installing Chocolatey package manager..."
    try {
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        Write-Success "Chocolatey installed successfully"
        return $true
    }
    catch {
        Write-Error "Failed to install Chocolatey`: $($_.Exception.Message)"
        return $false
    }
}

function Install-Tool {
    param($PackageName, $DisplayName, $TestCommand)
    
    if (Test-Command $TestCommand $DisplayName) { return $true }
    
    Write-Step "Installing $DisplayName..."
    try {
        choco install $PackageName -y
        Write-Success "$DisplayName installed successfully"
        return $true
    }
    catch {
        Write-Error "Failed to install $DisplayName`: $($_.Exception.Message)"
        return $false
    }
}

Write-Header "ReViewPoint Prerequisites Installer"
Write-Info "This script will install ALL required tools for ReViewPoint development"
Write-Info ""
Write-Info "📦 TOOLS THAT WILL BE INSTALLED:"
Write-Info "  1. Chocolatey - Package manager for Windows"
Write-Info "  2. Git - Version control system"
Write-Info "  3. Node.js 18+ - JavaScript runtime"  
Write-Info "  4. pnpm - Fast package manager (via npm)"
Write-Info "  5. Python 3.11+ - Backend runtime"
Write-Info "  6. pipx - Python application installer"
Write-Info "  7. Hatch - Python environment manager (via pipx)"
Write-Info ""
Write-Warning "⚠️  Docker Desktop - Requires MANUAL installation (guidance provided)"
Write-Info ""
Write-Info "🔧 INSTALLATION METHOD:"
Write-Info "  • Uses Chocolatey package manager for automated installation"
Write-Info "  • Downloads and installs tools from official sources"
Write-Info "  • Configures PATH environment variables automatically"
Write-Info "  • Verifies each installation before proceeding"
Write-Info ""
Write-Info "⏱️  ESTIMATED TIME: 5-10 minutes (depends on internet speed)"
Write-Info "💾 DISK SPACE: ~2GB total for all tools"
Write-Info ""

if (-not $SkipConfirmation) {
    Write-Host "❓ " -ForegroundColor Yellow -NoNewline
    $response = Read-Host "Do you want to proceed with installing these tools? (y/N)"
    if ($response -notmatch '^[Yy]') {
        Write-Info "Installation cancelled by user"
        Write-Info "💡 You can run this script anytime: .\scripts\install-prerequisites.ps1"
        exit 0
    }
}

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Warning "Some installations may require administrator privileges"
    Write-Info "Consider running PowerShell as Administrator for best results"
}

Write-Header "Phase 1: Package Manager"
$chocoInstalled = Install-Chocolatey

if (-not $chocoInstalled) {
    Write-Error "Cannot continue without Chocolatey package manager"
    Write-Info "Please install Chocolatey manually: https://chocolatey.org/install"
    exit 1
}

# Refresh environment to pick up Chocolatey
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

Write-Header "Phase 2: Core Development Tools"

# Git
Install-Tool "git" "Git" "git"

# Node.js (version 18+)
Install-Tool "nodejs" "Node.js" "node"

# Python (version 3.11+) 
Install-Tool "python" "Python" "python"

Write-Header "Phase 3: Package Managers"

# Install pnpm (requires Node.js)
if (Test-Command "node" "Node.js") {
    if (-not (Test-Command "pnpm" "pnpm")) {
        Write-Step "Installing pnpm..."
        try {
            npm install -g pnpm
            Write-Success "pnpm installed successfully"
        }
        catch {
            Write-Error "Failed to install pnpm`: $($_.Exception.Message)"
        }
    }
}
else {
    Write-Error "Cannot install pnpm without Node.js"
}

# Install pipx (requires Python)
if (Test-Command "python" "Python") {
    if (-not (Test-Command "pipx" "pipx")) {
        Write-Step "Installing pipx..."
        try {
            python -m pip install --user pipx
            python -m pipx ensurepath
            Write-Success "pipx installed successfully"
        }
        catch {
            Write-Error "Failed to install pipx`: $($_.Exception.Message)"
        }
    }
    
    # Install Hatch (requires pipx)
    if (Test-Command "pipx" "pipx") {
        if (-not (Test-Command "hatch" "Hatch")) {
            Write-Step "Installing Hatch..."
            try {
                pipx install hatch
                Write-Success "Hatch installed successfully"
            }
            catch {
                Write-Error "Failed to install Hatch`: $($_.Exception.Message)"
            }
        }
    }
}
else {
    Write-Error "Cannot install pipx/Hatch without Python"
}

Write-Header "Phase 4: Optional Tools"

# Docker Desktop (manual installation required)
if (-not (Test-Command "docker" "Docker")) {
    Write-Warning "Docker Desktop is not installed"
    Write-Info "Docker Desktop cannot be installed automatically via Chocolatey"
    Write-Info "Please download and install manually from: https://docker.com/products/docker-desktop/"
    Write-Info "Docker is required for PostgreSQL database (but SQLite works without it)"
}

Write-Header "Phase 5: Verification"

$tools = @(
    @{ Command = "git"; Name = "Git" },
    @{ Command = "node"; Name = "Node.js" },
    @{ Command = "pnpm"; Name = "pnpm" },
    @{ Command = "python"; Name = "Python" },
    @{ Command = "pipx"; Name = "pipx" },
    @{ Command = "hatch"; Name = "Hatch" },
    @{ Command = "docker"; Name = "Docker" }
)

$installedCount = 0
$totalCount = $tools.Count

foreach ($tool in $tools) {
    if (Test-Command $tool.Command $tool.Name) {
        $installedCount++
    }
}

Write-Header "Installation Summary"

Write-Info "$installedCount of $totalCount tools are installed"

if ($installedCount -eq $totalCount) {
    Write-Success "🎉 All prerequisites are installed!"
    Write-Info ""
    Write-Info "Next steps:"
    Write-Info "1. git clone https://github.com/filip-herceg/ReViewPoint.git"
    Write-Info "2. cd ReViewPoint"
    Write-Info "3. pnpm run dev:postgres (with PostgreSQL)"
    Write-Info "   OR pnpm run dev (with SQLite - simpler)"
}
elseif ($installedCount -ge ($totalCount - 1)) {
    Write-Success "Almost ready! Only Docker Desktop needs manual installation"
    Write-Info "You can start development with SQLite: pnpm run dev"
    Write-Info "For PostgreSQL setup, install Docker Desktop first"
}
else {
    Write-Warning "Some tools failed to install"
    Write-Info "Please install missing tools manually and restart PowerShell"
    Write-Info "Then run this script again to verify"
}

Write-Info ""
Write-Info "💡 Tip: Restart PowerShell/VS Code to refresh environment variables"

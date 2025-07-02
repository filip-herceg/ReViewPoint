#!/usr/bin/env pwsh

<#
.SYNOPSIS
    Fast upload test runner with optimized patterns
.DESCRIPTION
    Runs the optimized upload tests using the fastest available method.
    Automatically checks for Hatch and uses the backend virtual environment.
    
    MODES EXPLAINED:
    - fast: Uses SQLite in-memory DB (8.5s) - FASTEST, ideal for CI/development
    - parallel: 4 workers with SQLite (12s) - Good for development, tests run in parallel
    - regular: PostgreSQL with single thread (8.5s) - Tests real DB but slower startup
    
.PARAMETER Mode
    Test execution mode: fast, parallel, or regular
.EXAMPLE
    .\run_upload_tests.ps1 fast
.EXAMPLE
    .\run_upload_tests.ps1 parallel
#>

param(
    [Parameter(Position=0)]
    [ValidateSet("fast", "parallel", "regular")]
    [string]$Mode = "fast"
)

Write-Host "🚀 ReViewPoint Upload Tests - Optimized Test Runner" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Check if Hatch is installed
Write-Host "🔍 Checking environment setup..." -ForegroundColor Yellow
try {
    $hatchVersion = hatch --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Hatch found: $hatchVersion" -ForegroundColor Green
        $useHatch = $true
    } else {
        throw "Hatch not found"
    }
} catch {
    Write-Host "❌ Hatch not found. Please install Hatch: https://hatch.pypa.io/latest/install/" -ForegroundColor Red
    Write-Host "   Alternative: pip install hatch" -ForegroundColor Yellow
    $useHatch = $false
}

# Explain the modes
Write-Host ""
Write-Host "📋 Available Test Modes:" -ForegroundColor Cyan
Write-Host "  🚀 fast     - SQLite in-memory DB, single thread (~8.5s)" -ForegroundColor Green
Write-Host "               ✓ FASTEST execution, no PostgreSQL overhead" -ForegroundColor Gray
Write-Host "               ✓ Perfect for CI/CD and quick development cycles" -ForegroundColor Gray
Write-Host "               ✓ Uses FAST_TESTS=1 environment variable" -ForegroundColor Gray
Write-Host ""
Write-Host "  ⚡ parallel - SQLite in-memory DB, 4 workers (~12s)" -ForegroundColor Yellow
Write-Host "               ✓ Tests run in true parallel (good for development)" -ForegroundColor Gray
Write-Host "               ✓ Slightly slower due to worker coordination overhead" -ForegroundColor Gray
Write-Host "               ✓ Uses pytest-xdist for parallel execution" -ForegroundColor Gray
Write-Host ""
Write-Host "  🐘 regular  - PostgreSQL testcontainer, single thread (~8.5s)" -ForegroundColor Blue
Write-Host "               ✓ Tests against real PostgreSQL database" -ForegroundColor Gray
Write-Host "               ✓ Most realistic but slower container startup" -ForegroundColor Gray
Write-Host "               ✓ Good for integration testing" -ForegroundColor Gray
Write-Host ""
Write-Host "🎯 Running in '$Mode' mode..." -ForegroundColor Magenta

# Execute tests based on mode
Write-Host ""
Write-Host "⚙️  Executing tests..." -ForegroundColor Yellow

if ($useHatch) {
    # Use Hatch to run in the proper virtual environment
    switch ($Mode) {
        "fast" {
            Write-Host "⚡ FAST mode: SQLite in-memory database (fastest)" -ForegroundColor Green
            $env:FAST_TESTS = "1"
            hatch run pytest tests/api/v1/test_uploads_fast.py -v
        }
        "parallel" {
            Write-Host "⚡ PARALLEL mode: 4 workers with SQLite coordination" -ForegroundColor Yellow
            $env:FAST_TESTS = "1"
            hatch run pytest tests/api/v1/test_uploads_fast.py -v -n 4
        }
        "regular" {
            Write-Host "⚡ REGULAR mode: PostgreSQL testcontainer" -ForegroundColor Blue
            hatch run pytest tests/api/v1/test_uploads_fast.py -v
        }
    }
} else {
    Write-Host "⚠️  Running without Hatch (may not use correct virtual environment)" -ForegroundColor Yellow
    switch ($Mode) {
        "fast" {
            Write-Host "⚡ FAST mode: SQLite in-memory database (fastest)" -ForegroundColor Green
            $env:FAST_TESTS = "1"
            python -m pytest tests/api/v1/test_uploads_fast.py -v
        }
        "parallel" {
            Write-Host "⚡ PARALLEL mode: 4 workers with SQLite coordination" -ForegroundColor Yellow
            python -m pytest tests/api/v1/test_uploads_fast.py -v -n 4
        }
        "regular" {
            Write-Host "⚡ REGULAR mode: PostgreSQL testcontainer" -ForegroundColor Blue
            python -m pytest tests/api/v1/test_uploads_fast.py -v
        }
    }
}

Write-Host ""
Write-Host "✅ Upload tests completed in $Mode mode" -ForegroundColor Green
Write-Host ""
Write-Host "💡 Tips:" -ForegroundColor Cyan
Write-Host "   • Use 'fast' mode for quick development cycles" -ForegroundColor Gray
Write-Host "   • Use 'parallel' mode when testing multiple features" -ForegroundColor Gray
Write-Host "   • Use 'regular' mode for comprehensive integration testing" -ForegroundColor Gray
Write-Host "   • All modes test the same functionality with different performance profiles" -ForegroundColor Gray

# PowerShell script to set test log levels easily
# Usage: .\set-log-level.ps1 DEBUG
# Usage: .\set-log-level.ps1 INFO
# Usage: .\set-log-level.ps1 (shows current and available levels)

param(
    [string]$Level = ""
)

$LogLevels = @{
    "CRITICAL" = "Only critical errors (application crashes)"
    "ERROR" = "Error messages (failed operations, exceptions)"
    "WARNING" = "Warning messages (deprecated features, recoverable issues)"
    "INFO" = "General information (test progress, basic operations)"
    "DEBUG" = "Detailed debugging information (SQL queries, internal state)"
}

function Show-LogLevels {
    Write-Host "Available pytest log levels:" -ForegroundColor Cyan
    Write-Host ("=" * 50) -ForegroundColor Gray
    
    foreach ($level in $LogLevels.GetEnumerator()) {
        $name = $level.Key.PadRight(8)
        Write-Host "$name - $($level.Value)" -ForegroundColor White
    }
    
    Write-Host ""
    Write-Host "Current configuration:" -ForegroundColor Yellow
    $current = $env:REVIEWPOINT_TEST_LOG_LEVEL
    if (-not $current) { $current = "INFO (default)" }
    Write-Host "  Test log level: $current" -ForegroundColor Green
}

function Set-LogLevel {
    param([string]$RequestedLevel)
    
    $RequestedLevel = $RequestedLevel.ToUpper()
    
    if (-not $LogLevels.ContainsKey($RequestedLevel)) {
        Write-Host "Error: Invalid log level '$RequestedLevel'" -ForegroundColor Red
        Write-Host "Valid levels are: $($LogLevels.Keys -join ', ')" -ForegroundColor Yellow
        return
    }
    
    $env:REVIEWPOINT_TEST_LOG_LEVEL = $RequestedLevel
    Write-Host "✓ Log level set to $RequestedLevel for current session." -ForegroundColor Green
    
    Write-Host ""
    Write-Host "To make this permanent, add to your PowerShell profile:" -ForegroundColor Yellow
    Write-Host "  `$env:REVIEWPOINT_TEST_LOG_LEVEL = '$RequestedLevel'" -ForegroundColor Gray
    
    Write-Host ""
    Write-Host "Or set it when running tests:" -ForegroundColor Yellow
    Write-Host "  `$env:REVIEWPOINT_TEST_LOG_LEVEL='$RequestedLevel'; python run-fast-tests.py" -ForegroundColor Gray
    Write-Host "  `$env:REVIEWPOINT_TEST_LOG_LEVEL='$RequestedLevel'; hatch run test" -ForegroundColor Gray
}

# Main logic
if (-not $Level) {
    Show-LogLevels
} elseif ($Level -eq "--help" -or $Level -eq "-h" -or $Level -eq "help") {
    Write-Host "Test Log Level Configuration Helper" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\set-log-level.ps1              # Show current levels"
    Write-Host "  .\set-log-level.ps1 DEBUG        # Set to DEBUG level"
    Write-Host "  .\set-log-level.ps1 INFO         # Set to INFO level"
    Write-Host "  .\set-log-level.ps1 --help       # Show this help"
} elseif ($Level -eq "--show" -or $Level -eq "-s") {
    Show-LogLevels
} else {
    Set-LogLevel -RequestedLevel $Level
}

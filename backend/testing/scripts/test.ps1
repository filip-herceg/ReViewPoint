# ReViewPoint Backend Test Runner
# Provides easy access to both fast and full test suites

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("fast", "full", "watch", "coverage")]
    [string]$Mode,
    
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Args
)

function Run-Command {
    param(
        [string[]]$Command,
        [string]$Description = ""
    )
    
    if ($Description) {
        Write-Host "🚀 $Description" -ForegroundColor Green
        Write-Host "📁 Running: $($Command -join ' ')" -ForegroundColor Cyan
        Write-Host ("=" * 60) -ForegroundColor Gray
    }
    
    $startTime = Get-Date
    $process = Start-Process -FilePath $Command[0] -ArgumentList $Command[1..$Command.Length] -Wait -PassThru -NoNewWindow
    $duration = (Get-Date) - $startTime
    
    Write-Host ("=" * 60) -ForegroundColor Gray
    Write-Host "⏱️  Duration: $([math]::Round($duration.TotalSeconds, 2)) seconds" -ForegroundColor Yellow
    
    if ($process.ExitCode -eq 0) {
        Write-Host "✅ Tests completed successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Tests failed" -ForegroundColor Red
    }
    
    return $process.ExitCode
}

# Set working directory to script location
Set-Location $PSScriptRoot

switch ($Mode) {
    "fast" {
        $cmd = @("hatch", "run", "fast:test") + $Args
        exit (Run-Command -Command $cmd -Description "Running fast tests")
    }
    "full" {
        $cmd = @("hatch", "run", "pytest") + $Args  
        exit (Run-Command -Command $cmd -Description "Running full test suite")
    }
    "watch" {
        $cmd = @("hatch", "run", "fast:watch") + $Args
        exit (Run-Command -Command $cmd -Description "Running fast tests in watch mode")
    }
    "coverage" {
        $cmd = @("hatch", "run", "fast:coverage") + $Args
        exit (Run-Command -Command $cmd -Description "Running fast tests with coverage")
    }
}

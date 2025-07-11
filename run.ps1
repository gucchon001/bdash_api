# PowerShell Main Runner Script
# This script handles both development and production environments
param(
    [string]$Environment = "prd",
    [string]$Module = "",
    [switch]$Test,
    [switch]$Help,
    [switch]$NoInstall,
    [switch]$Force
)

# Help display
if ($Help) {
    Write-Host "Usage:"
    Write-Host "  .\run.ps1 [-Environment <dev|prd>] [-Module <module_name>] [options]"
    Write-Host ""
    Write-Host "Parameters:"
    Write-Host "  -Environment : Execution environment (dev=development, prd=production) [Default: prd]"
    Write-Host "  -Module      : Specific module to run (e.g., spreadsheet, bdash_api_sync)"
    Write-Host "  -Test        : Run in test mode with additional logging"
    Write-Host "  -NoInstall   : Skip package installation check"
    Write-Host "  -Force       : Force recreate virtual environment"
    Write-Host "  -Help        : Show this help"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\run.ps1                              # Run main module in production"
    Write-Host "  .\run.ps1 -Environment dev -Test       # Run in development with test mode"
    Write-Host "  .\run.ps1 -Module spreadsheet          # Run specific module"
    Write-Host "  .\run.ps1 -Force                       # Force recreate virtual environment"
    exit 0
}

# Variables
$VenvPath = ".\venv"
$DefaultScript = "src.main"
$ScriptToRun = $DefaultScript
$TestMode = ""

Write-Host "=== PowerShell Application Runner ===" -ForegroundColor Cyan
Write-Host ""

# Environment configuration
switch ($Environment.ToLower()) {
    "dev" { 
        $AppEnv = "development"
        if ($Test) {
            $TestMode = "--test"
        }
        Write-Host "[CONFIG] Environment: Development" -ForegroundColor Yellow
    }
    "prd" { 
        $AppEnv = "production"
        Write-Host "[CONFIG] Environment: Production" -ForegroundColor Green
    }
    default {
        Write-Error "Invalid environment. Please specify 'dev' or 'prd'."
        exit 1
    }
}

# Module specification
if ($Module) {
    $ScriptToRun = "src.$Module"
    Write-Host "[CONFIG] Module: $Module" -ForegroundColor Blue
} else {
    Write-Host "[CONFIG] Module: main (default)" -ForegroundColor Blue
}

# Python verification
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed"
    }
    Write-Host "[CHECK] Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Error "Python is not installed or not in PATH."
    Write-Host "Please install Python and ensure it's added to your PATH environment variable."
    exit 1
}

# Force recreation of virtual environment
if ($Force -and (Test-Path $VenvPath)) {
    Write-Host "[FORCE] Removing existing virtual environment..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $VenvPath
}

# Virtual environment creation if it doesn't exist
if (-not (Test-Path "$VenvPath\Scripts\Activate.ps1")) {
    Write-Host "[SETUP] Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv $VenvPath
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create virtual environment."
        exit 1
    }
    Write-Host "[SETUP] Virtual environment created successfully." -ForegroundColor Green
}

# Activate virtual environment
Write-Host "[VENV] Activating virtual environment..." -ForegroundColor Blue
if (Test-Path "$VenvPath\Scripts\Activate.ps1") {
    & "$VenvPath\Scripts\Activate.ps1"
    Write-Host "[VENV] Virtual environment activated." -ForegroundColor Green
} else {
    Write-Error "Failed to activate virtual environment. Activate.ps1 not found."
    exit 1
}

# Install packages if needed (unless NoInstall is specified)
if (-not $NoInstall) {
    if (-not (Test-Path "requirements.txt")) {
        Write-Warning "requirements.txt not found. Skipping package installation."
    } else {
        # Check if packages need to be installed
        $CurrentHash = (Get-FileHash requirements.txt -Algorithm SHA256).Hash
        $HashFile = ".req_hash"
        
        $NeedInstall = $false
        if (Test-Path $HashFile) {
            $StoredHash = Get-Content $HashFile -Raw -ErrorAction SilentlyContinue
            if ($CurrentHash -ne $StoredHash.Trim()) {
                $NeedInstall = $true
            }
        } else {
            $NeedInstall = $true
        }
        
        if ($NeedInstall) {
            Write-Host "[DEPS] Installing required packages..." -ForegroundColor Yellow
            pip install --upgrade pip
            pip install -r requirements.txt
            if ($LASTEXITCODE -ne 0) {
                Write-Error "Failed to install packages. Check your requirements.txt file."
                exit 1
            }
            $CurrentHash | Out-File $HashFile -Encoding utf8
            Write-Host "[DEPS] Packages installed successfully." -ForegroundColor Green
        } else {
            Write-Host "[DEPS] Packages are up to date." -ForegroundColor Green
        }
    }
} else {
    Write-Host "[DEPS] Skipping package installation (NoInstall flag set)." -ForegroundColor Yellow
}

# Display execution information
Write-Host ""
Write-Host "=== Execution Information ===" -ForegroundColor Cyan
Write-Host "Environment: $AppEnv"
Write-Host "Script: $ScriptToRun"
if ($TestMode) {
    Write-Host "Test Mode: Enabled" -ForegroundColor Yellow
}
Write-Host ""

# Run the script
Write-Host "[RUN] Starting execution..." -ForegroundColor Blue

try {
    if ($TestMode) {
        python -m $ScriptToRun $TestMode
    } else {
        python -m $ScriptToRun
    }
    
    if ($LASTEXITCODE -ne 0) {
        throw "Script execution returned error code: $LASTEXITCODE"
    }
    
    Write-Host ""
    Write-Host "[SUCCESS] Execution completed successfully." -ForegroundColor Green
} catch {
    Write-Host ""
    Write-Error "Script execution failed: $_"
    Write-Host ""
    Write-Host "Troubleshooting tips:" -ForegroundColor Yellow
    Write-Host "  1. Check if all required modules are in src/ directory"
    Write-Host "  2. Verify your configuration files in config/ directory"
    Write-Host "  3. Run with -Environment dev -Test for more detailed logging"
    Write-Host "  4. Use -Force to recreate virtual environment if needed"
    exit 1
}

Write-Host ""
Write-Host "=== Execution Complete ===" -ForegroundColor Cyan 
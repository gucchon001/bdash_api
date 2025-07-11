# PowerShell Development Runner Script
param(
    [string]$Environment = "",
    [string]$Module = "",
    [switch]$Help
)

# Help display
if ($Help) {
    Write-Host "Usage:"
    Write-Host "  .\run_dev.ps1 [-Environment <dev|prd>] [-Module <module_name>] [-Help]"
    Write-Host ""
    Write-Host "Parameters:"
    Write-Host "  -Environment : Specify execution environment (dev=development, prd=production)"
    Write-Host "  -Module      : Specify module to run"
    Write-Host "  -Help        : Show this help"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\run_dev.ps1 -Environment dev"
    Write-Host "  .\run_dev.ps1 -Environment prd -Module spreadsheet"
    exit 0
}

# Variable initialization
$VenvPath = ".\venv"
$DefaultScript = "src.main"
$ScriptToRun = $DefaultScript
$TestMode = ""

# Interactive environment selection if not specified
if (-not $Environment) {
    Write-Host "Select execution environment:"
    Write-Host "  1. Development (dev)"
    Write-Host "  2. Production (prd)"
    $Choice = Read-Host "Enter your choice (1/2)"
    
    switch ($Choice) {
        "1" { 
            $Environment = "dev"
            $TestMode = "--test"
        }
        "2" { 
            $Environment = "prd"
            $TestMode = ""
        }
        default {
            Write-Error "Invalid choice. Please run again."
            exit 1
        }
    }
}

# Environment configuration
switch ($Environment.ToLower()) {
    "dev" { 
        $AppEnv = "development"
        $TestMode = "--test"
    }
    "prd" { 
        $AppEnv = "production"
        $TestMode = ""
    }
    default {
        Write-Error "Invalid environment. Please specify 'dev' or 'prd'."
        exit 1
    }
}

# Module specification
if ($Module) {
    $ScriptToRun = "src.$Module"
}

# Python verification
try {
    python --version | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed"
    }
} catch {
    Write-Error "Python is not installed or not in PATH."
    exit 1
}

# Virtual environment creation if it doesn't exist
if (-not (Test-Path "$VenvPath\Scripts\Activate.ps1")) {
    Write-Host "[LOG] Virtual environment not found. Creating..."
    python -m venv $VenvPath
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create virtual environment."
        exit 1
    }
    Write-Host "[LOG] Virtual environment created successfully."
}

# Activate virtual environment
if (Test-Path "$VenvPath\Scripts\Activate.ps1") {
    Write-Host "[LOG] Activating virtual environment..."
    & "$VenvPath\Scripts\Activate.ps1"
} else {
    Write-Error "Failed to activate virtual environment. Activate.ps1 not found."
    exit 1
}

# Check requirements.txt
if (-not (Test-Path "requirements.txt")) {
    Write-Error "requirements.txt not found."
    exit 1
}

# Install packages if needed
$CurrentHash = (Get-FileHash requirements.txt -Algorithm SHA256).Hash
$HashFile = ".req_hash"

if (Test-Path $HashFile) {
    $StoredHash = Get-Content $HashFile -Raw
} else {
    $StoredHash = ""
}

if ($CurrentHash -ne $StoredHash.Trim()) {
    Write-Host "[LOG] Installing required packages..."
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to install packages."
        exit 1
    }
    $CurrentHash | Out-File $HashFile -Encoding utf8
}

# Run the script
Write-Host "[LOG] Environment: $AppEnv"
Write-Host "[LOG] Running script: $ScriptToRun"

if ($TestMode) {
    python -m $ScriptToRun $TestMode
} else {
    python -m $ScriptToRun
}

if ($LASTEXITCODE -ne 0) {
    Write-Error "Script execution failed."
    exit 1
}

Write-Host "[LOG] Execution completed successfully." 
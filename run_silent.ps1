# PowerShell Silent Runner for Task Scheduler
# Non-interactive script optimized for automated execution
param(
    [string]$Environment = "prd",
    [string]$Module = "",
    [switch]$Test,
    [switch]$NoInstall,
    [switch]$Force
)

# Variables
$VenvPath = ".\venv"
$DefaultScript = "src.main"
$ScriptToRun = $DefaultScript
$TestMode = ""
$LogFile = "logs\scheduler_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

# Create logs directory if it doesn't exist
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" -Force | Out-Null
}

# Function to write timestamped log
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] [$Level] $Message"
    Write-Output $LogMessage
    Add-Content -Path $LogFile -Value $LogMessage -Encoding UTF8
}

Write-Log "Task Scheduler execution started"

# Environment configuration
switch ($Environment.ToLower()) {
    "dev" { 
        $AppEnv = "development"
        if ($Test) {
            $TestMode = "--test"
        }
        Write-Log "Environment: Development"
    }
    "prd" { 
        $AppEnv = "production"
        Write-Log "Environment: Production"
    }
    default {
        Write-Log "Invalid environment. Using production as default." "WARN"
        $AppEnv = "production"
    }
}

# Module specification
if ($Module) {
    $ScriptToRun = "src.$Module"
    Write-Log "Module: $Module"
} else {
    Write-Log "Module: main (default)"
}

# Python verification
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed"
    }
    Write-Log "Python found: $pythonVersion"
} catch {
    Write-Log "Python is not installed or not in PATH." "ERROR"
    exit 1
}

# Force recreation of virtual environment
if ($Force -and (Test-Path $VenvPath)) {
    Write-Log "Removing existing virtual environment..." "WARN"
    Remove-Item -Recurse -Force $VenvPath
}

# Virtual environment creation if it doesn't exist
if (-not (Test-Path "$VenvPath\Scripts\Activate.ps1")) {
    Write-Log "Virtual environment not found. Creating..."
    python -m venv $VenvPath
    if ($LASTEXITCODE -ne 0) {
        Write-Log "Failed to create virtual environment." "ERROR"
        exit 1
    }
    Write-Log "Virtual environment created successfully."
}

# Activate virtual environment
Write-Log "Activating virtual environment..."
if (Test-Path "$VenvPath\Scripts\Activate.ps1") {
    & "$VenvPath\Scripts\Activate.ps1"
    Write-Log "Virtual environment activated."
} else {
    Write-Log "Failed to activate virtual environment. Activate.ps1 not found." "ERROR"
    exit 1
}

# Install packages if needed (unless NoInstall is specified)
if (-not $NoInstall) {
    if (-not (Test-Path "requirements.txt")) {
        Write-Log "requirements.txt not found. Skipping package installation." "WARN"
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
            Write-Log "Installing required packages..."
            pip install --upgrade pip --quiet
            pip install -r requirements.txt --quiet
            if ($LASTEXITCODE -ne 0) {
                Write-Log "Failed to install packages." "ERROR"
                exit 1
            }
            $CurrentHash | Out-File $HashFile -Encoding utf8
            Write-Log "Packages installed successfully."
        } else {
            Write-Log "Packages are up to date."
        }
    }
} else {
    Write-Log "Skipping package installation (NoInstall flag set)."
}

# Run the script
Write-Log "Starting execution of $ScriptToRun..."
Write-Log "Environment: $AppEnv"

try {
    if ($TestMode) {
        python -m $ScriptToRun $TestMode
    } else {
        python -m $ScriptToRun
    }
    
    if ($LASTEXITCODE -ne 0) {
        throw "Script execution returned error code: $LASTEXITCODE"
    }
    
    Write-Log "Execution completed successfully."
} catch {
    Write-Log "Script execution failed: $_" "ERROR"
    Write-Log "Check the log file for details: $LogFile" "ERROR"
    exit 1
}

Write-Log "Task Scheduler execution completed"
exit 0 
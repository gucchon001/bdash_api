# PowerShell Main Runner Script
# This script handles both development and production environments
# Default behavior is Silent mode (Task Scheduler friendly)
param(
    [string]$Environment = "prd",
    [string]$Module = "",
    [switch]$Test,
    [switch]$Help,
    [switch]$NoInstall,
    [switch]$Force,
    [switch]$Interactive  # Use this flag for interactive mode with colors and pause
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
    Write-Host "  -Interactive : Interactive mode with colors and pause (default is silent mode)"
    Write-Host "  -Help        : Show this help"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\run.ps1                              # Run in silent mode (Task Scheduler friendly)"
    Write-Host "  .\run.ps1 -Interactive                 # Run in interactive mode with colors"
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
$LogFile = ""

# Initialize logging for Silent mode (default behavior)
if (-not $Interactive) {
    # Create logs directory if it doesn't exist
    if (-not (Test-Path "logs")) {
        New-Item -ItemType Directory -Path "logs" -Force | Out-Null
    }
    $LogFile = "logs\run_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
}

# Function to write output (console or log file based on Interactive mode)
function Write-Output-Message {
    param([string]$Message, [string]$Color = "White")
    if (-not $Interactive) {
        # Silent mode: write to log file
        $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        $LogMessage = "[$Timestamp] $Message"
        Add-Content -Path $LogFile -Value $LogMessage -Encoding UTF8
    } else {
        # Interactive mode: write to console with colors
        if ($Color -ne "White") {
            Write-Host $Message -ForegroundColor $Color
        } else {
            Write-Host $Message
        }
    }
}

if ($Interactive) {
    Write-Host "=== PowerShell Application Runner ===" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Output-Message "=== PowerShell Application Runner - Silent Mode ==="
}

# Environment configuration
switch ($Environment.ToLower()) {
    "dev" { 
        $AppEnv = "development"
        if ($Test) {
            $TestMode = "--test"
        }
        Write-Output-Message "[CONFIG] Environment: Development" "Yellow"
    }
    "prd" { 
        $AppEnv = "production"
        Write-Output-Message "[CONFIG] Environment: Production" "Green"
    }
    default {
        if (-not $Interactive) {
            Write-Output-Message "[ERROR] Invalid environment. Please specify 'dev' or 'prd'."
        } else {
            Write-Error "Invalid environment. Please specify 'dev' or 'prd'."
        }
        exit 1
    }
}

# Module specification
if ($Module) {
    $ScriptToRun = "src.$Module"
    Write-Output-Message "[CONFIG] Module: $Module" "Blue"
} else {
    Write-Output-Message "[CONFIG] Module: main (default)" "Blue"
}

# Python verification
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed"
    }
    Write-Output-Message "[CHECK] Python found: $pythonVersion" "Green"
} catch {
    if (-not $Interactive) {
        Write-Output-Message "[ERROR] Python is not installed or not in PATH."
        Write-Output-Message "[ERROR] Please install Python and ensure it's added to your PATH environment variable."
    } else {
        Write-Error "Python is not installed or not in PATH."
        Write-Host "Please install Python and ensure it's added to your PATH environment variable."
    }
    exit 1
}

# Force recreation of virtual environment
if ($Force -and (Test-Path $VenvPath)) {
    Write-Output-Message "[FORCE] Removing existing virtual environment..." "Yellow"
    Remove-Item -Recurse -Force $VenvPath
}

# Virtual environment creation if it doesn't exist
if (-not (Test-Path "$VenvPath\Scripts\Activate.ps1")) {
    Write-Output-Message "[SETUP] Virtual environment not found. Creating..." "Yellow"
    python -m venv $VenvPath
    if ($LASTEXITCODE -ne 0) {
        if (-not $Interactive) {
            Write-Output-Message "[ERROR] Failed to create virtual environment."
        } else {
            Write-Error "Failed to create virtual environment."
        }
        exit 1
    }
    Write-Output-Message "[SETUP] Virtual environment created successfully." "Green"
}

# Activate virtual environment
Write-Output-Message "[VENV] Activating virtual environment..." "Blue"
if (Test-Path "$VenvPath\Scripts\Activate.ps1") {
    & "$VenvPath\Scripts\Activate.ps1"
    Write-Output-Message "[VENV] Virtual environment activated." "Green"
} else {
    if (-not $Interactive) {
        Write-Output-Message "[ERROR] Failed to activate virtual environment. Activate.ps1 not found."
    } else {
        Write-Error "Failed to activate virtual environment. Activate.ps1 not found."
    }
    exit 1
}

# Install packages if needed (unless NoInstall is specified)
if (-not $NoInstall) {
    if (-not (Test-Path "requirements.txt")) {
        if (-not $Interactive) {
            Write-Output-Message "[WARN] requirements.txt not found. Skipping package installation."
        } else {
            Write-Warning "requirements.txt not found. Skipping package installation."
        }
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
            Write-Output-Message "[DEPS] Installing required packages..." "Yellow"
            if (-not $Interactive) {
                pip install --upgrade pip --quiet
                pip install -r requirements.txt --quiet
            } else {
                pip install --upgrade pip
                pip install -r requirements.txt
            }
            if ($LASTEXITCODE -ne 0) {
                if (-not $Interactive) {
                    Write-Output-Message "[ERROR] Failed to install packages. Check your requirements.txt file."
                } else {
                    Write-Error "Failed to install packages. Check your requirements.txt file."
                }
                exit 1
            }
            $CurrentHash | Out-File $HashFile -Encoding utf8
            Write-Output-Message "[DEPS] Packages installed successfully." "Green"
        } else {
            Write-Output-Message "[DEPS] Packages are up to date." "Green"
        }
    }
} else {
    Write-Output-Message "[DEPS] Skipping package installation (NoInstall flag set)." "Yellow"
}

# Display execution information
if ($Interactive) {
    Write-Host ""
    Write-Host "=== Execution Information ===" -ForegroundColor Cyan
    Write-Host "Environment: $AppEnv"
    Write-Host "Script: $ScriptToRun"
    if ($TestMode) {
        Write-Host "Test Mode: Enabled" -ForegroundColor Yellow
    }
    Write-Host ""
} else {
    Write-Output-Message "=== Execution Information ==="
    Write-Output-Message "Environment: $AppEnv"
    Write-Output-Message "Script: $ScriptToRun"
    if ($TestMode) {
        Write-Output-Message "Test Mode: Enabled"
    }
}

# Run the script
Write-Output-Message "[RUN] Starting execution..." "Blue"

try {
    $pythonArgs = @()
    if ($TestMode) {
        $pythonArgs += $TestMode
    }
    if (-not $Interactive) {
        $pythonArgs += "--silent"
    }
    
    if ($pythonArgs.Count -gt 0) {
        python -m $ScriptToRun @pythonArgs
    } else {
        python -m $ScriptToRun
    }
    
    if ($LASTEXITCODE -ne 0) {
        throw "Script execution returned error code: $LASTEXITCODE"
    }
    
    if ($Interactive) {
        Write-Host ""
    }
    Write-Output-Message "[SUCCESS] Execution completed successfully." "Green"
} catch {
    if (-not $Interactive) {
        Write-Output-Message "[ERROR] Script execution failed: $_"
        Write-Output-Message "[ERROR] Check the log file for details: $LogFile"
    } else {
        Write-Host ""
        Write-Error "Script execution failed: $_"
        Write-Host ""
        Write-Host "Troubleshooting tips:" -ForegroundColor Yellow
        Write-Host "  1. Check if all required modules are in src/ directory"
        Write-Host "  2. Verify your configuration files in config/ directory"
        Write-Host "  3. Run with -Environment dev -Test for more detailed logging"
        Write-Host "  4. Use -Force to recreate virtual environment if needed"
        Write-Host "  5. Use -Interactive for interactive mode with colors"
    }
    exit 1
}

if ($Interactive) {
    Write-Host ""
    Write-Host "=== Execution Complete ===" -ForegroundColor Cyan
} else {
    Write-Output-Message "=== Execution Complete ==="
    Write-Output-Message "Log file: $LogFile"
} 
$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "       Installing VoxType v2.0...        " -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check for Python
Write-Host "[1/4] Checking prerequisites..."
    $pythonExe = Get-Command "python" -ErrorAction SilentlyContinue
    if (-not $pythonExe) {
        Write-Host "Error: Python is not installed." -ForegroundColor Red
        Write-Host "Please install Python 3.10+ from https://www.python.org/downloads/ and try again." -ForegroundColor Yellow
        exit 1
    }
    
    # Check for the Microsoft Store alias trap
    $pythonVersion = & python --version 2>&1
    if ($LASTEXITCODE -ne 0 -or "$pythonVersion" -match "was not found") {
        Write-Host "Error: Python is not properly installed or is blocked by a Microsoft Store App Execution Alias." -ForegroundColor Red
        Write-Host "To fix this:`n1. Open Windows Settings > Apps > Advanced app settings > App execution aliases`n2. Turn OFF 'App Installer' for python.exe and python3.exe`n3. Try running this installer again." -ForegroundColor Yellow
        Write-Host "Alternatively, download Python directly from https://www.python.org/downloads/" -ForegroundColor Yellow
        exit 1
    }

$installDir = "$HOME\VoxType"
Write-Host "[2/4] Downloading VoxType to $installDir..."

# Clone or update
if (Test-Path "$installDir\.git") {
    Write-Host "VoxType directory already exists, pulling latest changes..."
    Set-Location $installDir
    git pull
} else {
    if (Get-Command "git" -ErrorAction SilentlyContinue) {
        git clone https://github.com/bennyjoel/Vox.git $installDir
    } else {
        # Fallback to downloading zip if git is not installed
        $zipPath = "$HOME\VoxType.zip"
        Invoke-WebRequest -Uri "https://github.com/bennyjoel/Vox/archive/refs/heads/main.zip" -OutFile $zipPath
        Expand-Archive -Path $zipPath -DestinationPath $HOME -Force
        Rename-Item -Path "$HOME\Vox-main" -NewName "VoxType"
        Remove-Item -Path $zipPath
    }
}

Set-Location $installDir

Write-Host "[3/4] Setting up Python virtual environment..."
# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    python -m venv venv
}

Write-Host "Installing dependencies (this might take a minute)..."
# Use the full path to the virtual environment pip to avoid activation script issues
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\pip.exe install -r requirements.txt

Write-Host "[4/4] Creating Desktop Shortcut..."
$WshShell = New-Object -comObject WScript.Shell
$desktopPath = [Environment]::GetFolderPath("Desktop")
$Shortcut = $WshShell.CreateShortcut("$desktopPath\VoxType.lnk")
$Shortcut.TargetPath = "$installDir\venv\Scripts\pythonw.exe"
$Shortcut.Arguments = "main.py"
$Shortcut.WorkingDirectory = $installDir
# $Shortcut.IconLocation = "$installDir\assets\icon_idle.png" # Optional icon
$Shortcut.Save()

Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "   Installation Complete! 🎉             " -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host "A shortcut has been placed on your desktop."
Write-Host "Starting VoxType now..." -ForegroundColor Cyan

# Launch the app in the background
Start-Process -FilePath "$installDir\venv\Scripts\pythonw.exe" -ArgumentList "main.py" -WorkingDirectory $installDir

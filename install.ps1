$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "       Installing VoxType v2.0...        " -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check for Python
Write-Host "[1/4] Checking prerequisites..."
function Get-RealPython {
    # 1. Check if standard python command works (and isn't the store alias)
    $pythonExe = Get-Command "python" -ErrorAction SilentlyContinue
    if ($pythonExe) {
        $version = & python --version 2>&1
        if ($LASTEXITCODE -eq 0 -and "$version" -notmatch "was not found") { return "python" }
    }
    # 2. Check for Python Launcher for Windows
    if (Get-Command "py" -ErrorAction SilentlyContinue) { return "py" }
    # 3. Check common installation paths
    $paths = @("$env:LOCALAPPDATA\Programs\Python\Python*\python.exe", "$env:ProgramFiles\Python*\python.exe", "C:\Python*\python.exe")
    foreach ($p in $paths) {
        $found = Resolve-Path $p -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Path -First 1
        if ($found) { return $found }
    }
    return $null
}

$pythonCmd = Get-RealPython

if (-not $pythonCmd) {
    Write-Host "Python not found. Attempting to install Python 3.11 automatically..." -ForegroundColor Yellow
    if (Get-Command "winget" -ErrorAction SilentlyContinue) {
        winget install --id Python.Python.3.11 --exact --silent --accept-package-agreements --accept-source-agreements
        # Refresh env path
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        $pythonCmd = Get-RealPython
    }
    
    if (-not $pythonCmd) {
        Write-Host "Automatic installation failed." -ForegroundColor Red
        Write-Host "Please install Python 3.10+ manually from https://www.python.org/downloads/" -ForegroundColor Yellow
        exit 1
    }
}
Write-Host "Using Python at: $pythonCmd"

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
if (-not (Test-Path "venv")) {
    & $pythonCmd -m venv venv
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

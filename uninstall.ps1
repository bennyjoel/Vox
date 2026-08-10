$ErrorActionPreference = "Continue"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "       Uninstalling VoxType...           " -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check if VoxType is running and kill it
Write-Host "Checking for running VoxType processes..."
Get-Process -Name "pythonw" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match "VoxType" -or $_.Path -match "VoxType" } | Stop-Process -Force -ErrorAction SilentlyContinue

# 2. Remove Installation Directory
$installDir = "$HOME\VoxType"
if (Test-Path $installDir) {
    Write-Host "Removing installation directory: $installDir"
    Remove-Item -Path $installDir -Recurse -Force -ErrorAction SilentlyContinue
}

# 3. Remove Desktop Shortcut
$shortcutPath = "$HOME\Desktop\VoxType.lnk"
if (Test-Path $shortcutPath) {
    Write-Host "Removing desktop shortcut..."
    Remove-Item -Path $shortcutPath -Force -ErrorAction SilentlyContinue
}

# 4. Remove AppData (Settings, History, Downloaded Models)
$appDataDir = "$env:LOCALAPPDATA\VoxType"
if (Test-Path $appDataDir) {
    Write-Host "Removing application data and models: $appDataDir"
    Remove-Item -Path $appDataDir -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "   VoxType has been successfully uninstalled!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green

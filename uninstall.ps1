$ErrorActionPreference = "SilentlyContinue"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "       Uninstalling VoxType v2.1...      " -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

$installDir = "$HOME\VoxType"
$appDataDir = "$env:LOCALAPPDATA\VoxType"

Write-Host "[1/4] Stopping background processes..." -ForegroundColor Yellow
# Find and kill python/pythonw processes running from the installation directory
$processes = Get-WmiObject Win32_Process | Where-Object { $_.Name -match "^pythonw?\.exe$" -and $_.ExecutablePath -like "$installDir\*" }
foreach ($p in $processes) {
    Stop-Process -Id $p.ProcessId -Force
}
Start-Sleep -Seconds 2

Write-Host "[2/4] Removing shortcuts..." -ForegroundColor Yellow
$userDesktop = [Environment]::GetFolderPath("Desktop")
$publicDesktop = [Environment]::GetFolderPath("CommonDesktopDirectory")
$onedriveDesktop = "$HOME\OneDrive\Desktop"

$shortcuts = @(
    "$userDesktop\VoxType.lnk",
    "$publicDesktop\VoxType.lnk",
    "$onedriveDesktop\VoxType.lnk"
)

foreach ($sc in $shortcuts) {
    if (Test-Path $sc) {
        Remove-Item -Path $sc -Force
    }
}

Write-Host "[3/4] Deleting application files..." -ForegroundColor Yellow
if (Test-Path $installDir) {
    Remove-Item -Path $installDir -Recurse -Force
}

if (Test-Path "$HOME\VoxType.zip") {
    Remove-Item -Path "$HOME\VoxType.zip" -Force
}

Write-Host "[4/4] Deleting models and app data..." -ForegroundColor Yellow
if (Test-Path $appDataDir) {
    Remove-Item -Path $appDataDir -Recurse -Force
}

Write-Host ""
Write-Host "VoxType has been completely uninstalled. Zero traces remain." -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Start-Sleep -Seconds 3

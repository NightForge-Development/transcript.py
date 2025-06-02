<#
.SYNOPSIS
    Installs development tools without admin privileges.
.DESCRIPTION
    This script installs:
    - Git
    - Chocolatey (portable)
    - Python 3.11.9
    - FFmpeg (via Chocolatey)
    - openai-whisper (via PIP)
.NOTES
    File Name      : Install-DevTools.ps1
    Prerequisite   : PowerShell 5.1+
    No admin rights required
#>

# Set Error Action Preference
$ErrorActionPreference = "Stop"

# Function to add to PATH if not already present
function Add-ToPath {
    param (
        [string]$PathToAdd
    )
    
    $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    if ($currentPath -notlike "*$PathToAdd*") {
        $newPath = $currentPath + [IO.Path]::PathSeparator + $PathToAdd
        [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
        $env:PATH += [IO.Path]::PathSeparator + $PathToAdd
    }
}

# 1. Install Git (standalone portable version)
Write-Host "Downloading and installing Git..." -ForegroundColor Cyan
$gitUrl = "https://github.com/git-for-windows/git/releases/download/v2.45.1.windows.1/PortableGit-2.45.1-64-bit.7z.exe"
$gitInstaller = "$env:TEMP\PortableGit.7z.exe"
$gitInstallDir = "$env:USERPROFILE\git"

try {
    # Download Git portable
    (New-Object System.Net.WebClient).DownloadFile($gitUrl, $gitInstaller)
    
    # Extract to user directory
    if (-not (Test-Path $gitInstallDir)) {
        New-Item -ItemType Directory -Path $gitInstallDir | Out-Null
    }
    
    # Using 7z to extract (built into Windows 10+)
    Start-Process -Wait -FilePath $gitInstaller -ArgumentList "-o$gitInstallDir -y"
    
    # Add to PATH
    Add-ToPath -PathToAdd "$gitInstallDir\bin"
    
    Write-Host "Git installed successfully" -ForegroundColor Green
}
catch {
    Write-Host "Failed to install Git: $_" -ForegroundColor Red
    exit 1
}

# 2. Install Chocolatey (portable)
Write-Host "Installing Chocolatey (portable)..." -ForegroundColor Cyan
$chocoInstallDir = "$env:USERPROFILE\chocoportable"
$env:ChocolateyInstall = $chocoInstallDir

try {
    # Create installation directory if it doesn't exist
    if (-not (Test-Path $chocoInstallDir)) {
        New-Item -ItemType Directory -Path $chocoInstallDir | Out-Null
    }
    
    # Set execution policy for this process
    Set-ExecutionPolicy Bypass -Scope Process -Force
    
    # Install Chocolatey
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    
    # Add Chocolatey to PATH
    Add-ToPath -PathToAdd "$chocoInstallDir\bin"
    
    Write-Host "Chocolatey installed successfully" -ForegroundColor Green
}
catch {
    Write-Host "Failed to install Chocolatey: $_" -ForegroundColor Red
    exit 1
}

# 3. Install Python 3.11.9 (user installation)
Write-Host "Installing Python 3.11.9..." -ForegroundColor Cyan
$pythonUrl = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
$pythonInstaller = "$env:TEMP\python-3.11.9.exe"

try {
    # Download Python installer
    (New-Object System.Net.WebClient).DownloadFile($pythonUrl, $pythonInstaller)
    
    # Install Python for current user
    $pythonInstallArgs = @(
        "/quiet",
        "InstallAllUsers=0",
        "PrependPath=1",
        "Include_test=0",
        "Include_launcher=0",
        "SimpleInstall=1"
    )
    
    Start-Process -Wait -FilePath $pythonInstaller -ArgumentList $pythonInstallArgs
    
    Write-Host "Python 3.11.9 installed successfully" -ForegroundColor Green
    
    # Refresh PATH to ensure Python is available
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
}
catch {
    Write-Host "Failed to install Python: $_" -ForegroundColor Red
    exit 1
}

# 4. Install FFmpeg using Chocolatey
Write-Host "Installing FFmpeg via Chocolatey..." -ForegroundColor Cyan
try {
    & "$chocoInstallDir\bin\choco.exe" install ffmpeg -y --no-progress
    Write-Host "FFmpeg installed successfully" -ForegroundColor Green
}
catch {
    Write-Host "Failed to install FFmpeg: $_" -ForegroundColor Red
    exit 1
}

# 5. Install openai-whisper using pip
Write-Host "Installing openai-whisper via pip..." -ForegroundColor Cyan
try {
    # Ensure pip is up to date
    python -m pip install --upgrade pip
    
    # Install whisper
    python -m pip install git+https://github.com/openai/whisper.git
    
    Write-Host "openai-whisper installed successfully" -ForegroundColor Green
}
catch {
    Write-Host "Failed to install openai-whisper: $_" -ForegroundColor Red
    exit 1
}

Write-Host "All components installed successfully!" -ForegroundColor Green

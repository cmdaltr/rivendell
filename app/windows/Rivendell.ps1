<#
.SYNOPSIS
    What the Rivendell shortcut runs: start the Docker stack if the web UI isn't
    answering, then open the UI in its own Edge (or Chrome) app window.
.NOTES
    The bash launcher doesn't run on Windows, so this does what 'rivendell start'
    does there: make sure Docker Desktop is up, then 'docker compose up -d' in the repo,
    with docker-compose.local.yml (the installer's evidence folders) when it exists.
    A copy the installer put down (.rivendell-version) gets a .env with its own
    SECRET_KEY on first start and an image rebuild after each upgrade.
#>
[CmdletBinding()]
param(
    [switch]$Stop
)

$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$Url = 'http://localhost:5687'
$State = Join-Path $env:LOCALAPPDATA 'Rivendell'
$BrowserProfile = Join-Path $State 'browser'
New-Item -ItemType Directory -Force -Path $BrowserProfile | Out-Null
$Host.UI.RawUI.WindowTitle = 'Rivendell'

function Test-Frontend {
    try {
        Invoke-WebRequest -Uri $Url -Method Head -TimeoutSec 2 -UseBasicParsing | Out-Null
        return $true
    } catch {
        # Any HTTP answer, even an error status, means the frontend is listening
        return $null -ne $_.Exception.Response
    }
}

function Test-Docker {
    # Windows PowerShell turns a native command's redirected stderr into a terminating
    # error under 'Stop', so the probe runs under 'Continue'
    $ErrorActionPreference = 'Continue'
    docker info *> $null
    return $LASTEXITCODE -eq 0
}

function Wait-Docker {
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        throw 'The docker command isn''t on PATH. Install Docker Desktop and retry.'
    }
    if (Test-Docker) { return }
    $desktop = Join-Path $env:ProgramFiles 'Docker\Docker\Docker Desktop.exe'
    if (-not (Test-Path $desktop)) {
        throw "Docker isn't running and Docker Desktop isn't installed at $desktop. Start Docker and retry."
    }
    Write-Host 'Starting Docker Desktop...'
    Start-Process $desktop
    for ($i = 0; $i -lt 120; $i++) {
        Start-Sleep -Seconds 2
        if (Test-Docker) { Write-Host 'Docker started.'; return }
    }
    throw 'Docker did not start in time. Start it manually and retry.'
}

function Invoke-Compose {
    param([string[]]$Arguments)
    $files = @('-f', 'docker-compose.yml')
    if (Test-Path (Join-Path $Root 'docker-compose.local.yml')) { $files += @('-f', 'docker-compose.local.yml') }
    Push-Location $Root
    try {
        docker compose @files @Arguments
        if ($LASTEXITCODE -ne 0) { throw "docker compose $($Arguments -join ' ') exited with status $LASTEXITCODE" }
    } finally {
        Pop-Location
    }
}

function Initialize-AppCopy {
    # Returns the extra 'up' arguments: --build once after the installer upgraded the copy
    $versionFile = Join-Path $Root '.rivendell-version'
    if (-not (Test-Path $versionFile)) { return @() }
    $envFile = Join-Path $Root '.env'
    $example = Join-Path $Root '.env.example'
    if (-not (Test-Path $envFile) -and (Test-Path $example)) {
        $bytes = New-Object byte[] 32
        [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
        $key = ($bytes | ForEach-Object { $_.ToString('x2') }) -join ''
        (Get-Content $example) -replace '^SECRET_KEY=.*', "SECRET_KEY=$key" | Set-Content -Path $envFile -Encoding ASCII
        Write-Host 'Created .env with a new SECRET_KEY.'
    }
    $built = Join-Path $Root '.rivendell-built'
    $version = (Get-Content $versionFile -Raw).Trim()
    if ((Test-Path $built) -and (Get-Content $built -Raw).Trim() -eq $version) { return @() }
    Write-Host 'New Rivendell version: rebuilding the images (this takes a while)...'
    return @('--build')
}

function Open-Window {
    # Edge ships with Windows 10 and 11; Chrome is the fallback, then the default browser
    $browsers = @(
        "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe",
        "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
        "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
        "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
    )
    $browser = $browsers | Where-Object { Test-Path $_ } | Select-Object -First 1
    if ($browser) {
        Start-Process $browser -ArgumentList "--app=$Url", "--user-data-dir=`"$BrowserProfile`"", '--no-first-run'
    } else {
        Start-Process $Url
    }
}

try {
    if ($Stop) {
        Wait-Docker
        Write-Host 'Stopping Rivendell...'
        Invoke-Compose @('down', '--remove-orphans')
        Write-Host 'Stopped.'
        Start-Sleep -Seconds 2
        exit 0
    }

    if (-not (Test-Frontend)) {
        Wait-Docker
        $extra = @(Initialize-AppCopy)
        Write-Host 'Starting Rivendell (the first start builds the images and takes a while)...'
        Invoke-Compose (@('up', '-d') + $extra)
        if ($extra -contains '--build') {
            Copy-Item (Join-Path $Root '.rivendell-version') (Join-Path $Root '.rivendell-built') -Force
        }
        Write-Host "Waiting for the web UI on $Url..."
        $deadline = (Get-Date).AddMinutes(15)
        while (-not (Test-Frontend)) {
            if ((Get-Date) -gt $deadline) {
                throw "The stack started but nothing answered on $Url. Try 'docker compose ps' in $Root."
            }
            Start-Sleep -Seconds 2
        }
    }
    Open-Window
} catch {
    Write-Host ''
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host 'Press Enter to close'
    exit 1
}

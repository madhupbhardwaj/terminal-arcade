# Terminal Arcade installer for Windows.
#   irm https://raw.githubusercontent.com/madhupbhardwaj/terminal-arcade/main/install.ps1 | iex
$ErrorActionPreference = 'Stop'

$Source = if ($env:ARCADE_SOURCE) { $env:ARCADE_SOURCE } else { 'https://github.com/madhupbhardwaj/terminal-arcade/archive/refs/heads/main.zip' }
$AppDir = Join-Path $env:USERPROFILE '.terminal-arcade'
$BinDir = Join-Path $AppDir 'bin'

function Say($msg) { Write-Host "==> $msg" -ForegroundColor Cyan }

# 1. Find Python 3.9+ ---------------------------------------------------------
function Find-Python {
    foreach ($c in @('py -3', 'python', 'python3')) {
        $parts = $c -split ' '
        $exe = $parts[0]
        if (-not (Get-Command $exe -ErrorAction SilentlyContinue)) { continue }
        $pyArgs = @($parts | Select-Object -Skip 1) + @('-c', 'import sys; print(sys.executable) if sys.version_info >= (3, 9) else None')
        try {
            $out = (& $exe @pyArgs 2>$null | Select-Object -Last 1)
            if ($LASTEXITCODE -eq 0 -and $out -and (Test-Path ([string]$out).Trim())) { return ([string]$out).Trim() }
        } catch { }
    }
    # Freshly installed by winget but not yet on this window's PATH
    $found = Get-ChildItem "$env:LOCALAPPDATA\Programs\Python\Python3*\python.exe" -ErrorAction SilentlyContinue |
             Sort-Object FullName -Descending | Select-Object -First 1
    if ($found) { return $found.FullName }
    return $null
}

$Python = Find-Python
if (-not $Python) {
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
        throw 'Python 3.9+ is needed. Install it from https://www.python.org/downloads/ and run this command again.'
    }
    Say 'Installing Python (this can take a minute)...'
    winget install -e --id Python.Python.3.13 --scope user --silent --accept-package-agreements --accept-source-agreements | Out-Host
    $Python = Find-Python
    if (-not $Python) { throw 'Python was installed but could not be found. Open a new terminal and run this command again.' }
}
Say "Using $(& $Python --version)"

# 2. Install into a private environment ---------------------------------------
Say 'Installing Terminal Arcade...'
$Venv = Join-Path $AppDir 'venv'
if (Test-Path $Venv) { Remove-Item -Recurse -Force $Venv }
New-Item -ItemType Directory -Force -Path $BinDir | Out-Null
& $Python -m venv $Venv
if ($LASTEXITCODE -ne 0) { throw 'Could not create a Python environment.' }
$VenvPy = Join-Path $Venv 'Scripts\python.exe'
& $VenvPy -m pip install --quiet --disable-pip-version-check --upgrade pip
& $VenvPy -m pip install --quiet --disable-pip-version-check $Source
if ($LASTEXITCODE -ne 0) { throw 'Installing Terminal Arcade failed (see the messages above).' }

# A small launcher, so only "arcade" goes on PATH (not the private Python)
Set-Content -Path (Join-Path $BinDir 'arcade.cmd') -Encoding ASCII -Value "@`"$VenvPy`" -m terminal_arcade %*"

# 3. Put the launcher folder on PATH ------------------------------------------
$UserPath = [Environment]::GetEnvironmentVariable('Path', 'User')
if (-not $UserPath) { $UserPath = '' }
if (($UserPath -split ';') -notcontains $BinDir) {
    [Environment]::SetEnvironmentVariable('Path', ($UserPath.TrimEnd(';') + ";$BinDir").TrimStart(';'), 'User')
}
if (($env:Path -split ';') -notcontains $BinDir) { $env:Path = "$env:Path;$BinDir" }

Write-Host ''
Say 'Done! Terminal Arcade is installed.'
Write-Host '    Type:  arcade'

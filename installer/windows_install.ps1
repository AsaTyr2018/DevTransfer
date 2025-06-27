# Installs DevTrans CLI on Windows and configures system-wide environment variables
param(
    [Parameter(Mandatory=$true)]
    [string]$Token,
    [string]$BaseUrl = "http://localhost:8000"
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootDir = Join-Path $scriptDir '..'
$cliDir = Join-Path $rootDir 'cli'

Write-Host 'Building DevTrans CLI...'
Push-Location $cliDir
& go build -o devtrans.exe
Pop-Location

$installDir = "$env:ProgramFiles\DevTrans"
if (-not (Test-Path $installDir)) { New-Item -ItemType Directory -Path $installDir | Out-Null }
Copy-Item (Join-Path $cliDir 'devtrans.exe') $installDir -Force

$path = [Environment]::GetEnvironmentVariable('Path', 'Machine')
if ($path -notlike "*$installDir*") {
    [Environment]::SetEnvironmentVariable('Path', "$path;$installDir", 'Machine')
}

[Environment]::SetEnvironmentVariable('DEVTRANS_TOKEN', $Token, 'Machine')
[Environment]::SetEnvironmentVariable('DEVTRANS_BASE_URL', $BaseUrl, 'Machine')

Write-Host 'DevTrans installed. Restart your command prompt to use devtrans.'

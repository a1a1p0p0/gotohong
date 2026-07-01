$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$MobileRoot = Join-Path $ProjectRoot "mobile"
$Port = 3000

$env:Path += ";C:\Program Files\nodejs;C:\Users\Administrator\AppData\Roaming\npm"

$Existing = netstat -ano | Select-String ":$Port" | ForEach-Object {
    ($_ -split "\s+")[-1]
} | Select-Object -Unique

foreach ($ProcId in $Existing) {
    if ($ProcId -match "^\d+$" -and $ProcId -ne "0") {
        Stop-Process -Id ([int]$ProcId) -Force -ErrorAction SilentlyContinue
    }
}

$NextCache = Join-Path $MobileRoot ".next"
if (Test-Path $NextCache) {
    Remove-Item -LiteralPath $NextCache -Recurse -Force
}

$LogDir = Join-Path $ProjectRoot "logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$OutLog = Join-Path $LogDir "mobile_next.out.log"
$ErrLog = Join-Path $LogDir "mobile_next.err.log"

Start-Process `
    -FilePath npm.cmd `
    -ArgumentList @("run", "dev") `
    -WorkingDirectory $MobileRoot `
    -RedirectStandardOutput $OutLog `
    -RedirectStandardError $ErrLog `
    -WindowStyle Hidden

Start-Sleep -Seconds 18

$Listening = netstat -ano | Select-String ":$Port"
if (-not $Listening) {
    Write-Host "Mobile failed to start. See logs\mobile_next.err.log"
    exit 1
}

Write-Host "Mobile running: http://127.0.0.1:$Port"

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$Port = 8000
$LogDir = Join-Path $ProjectRoot "logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

$Existing = netstat -ano | Select-String ":$Port" | ForEach-Object {
    ($_ -split "\s+")[-1]
} | Select-Object -Unique

foreach ($ProcId in $Existing) {
    if ($ProcId -match "^\d+$" -and $ProcId -ne "0") {
        Stop-Process -Id ([int]$ProcId) -Force -ErrorAction SilentlyContinue
    }
}

$OutLog = Join-Path $LogDir "fastapi_backend.out.log"
$ErrLog = Join-Path $LogDir "fastapi_backend.err.log"

Start-Process `
    -FilePath python `
    -ArgumentList @("-m", "uvicorn", "wuxing_stock_app.backend.main:app", "--host", "127.0.0.1", "--port", "$Port") `
    -WorkingDirectory $ProjectRoot `
    -RedirectStandardOutput $OutLog `
    -RedirectStandardError $ErrLog `
    -WindowStyle Hidden

Start-Sleep -Seconds 3

$Listening = netstat -ano | Select-String ":$Port"
if (-not $Listening) {
    Write-Host "Backend failed to start. See logs\fastapi_backend.err.log"
    exit 1
}

Write-Host "Backend running: http://127.0.0.1:$Port"
Write-Host "Docs: http://127.0.0.1:$Port/docs"

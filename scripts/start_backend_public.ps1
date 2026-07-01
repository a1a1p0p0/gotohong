$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$Port = if ($env:WUXING_BACKEND_PORT) { $env:WUXING_BACKEND_PORT } else { "8000" }
$HostIp = if ($env:WUXING_BACKEND_HOST) { $env:WUXING_BACKEND_HOST } else { "0.0.0.0" }
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

Start-Process `
    -FilePath python `
    -ArgumentList @("-m", "uvicorn", "wuxing_stock_app.backend.main:app", "--host", "$HostIp", "--port", "$Port") `
    -WorkingDirectory $ProjectRoot `
    -RedirectStandardOutput (Join-Path $LogDir "fastapi_backend_public.out.log") `
    -RedirectStandardError (Join-Path $LogDir "fastapi_backend_public.err.log") `
    -WindowStyle Hidden

Start-Sleep -Seconds 3
Write-Host "Backend public running: http://$HostIp`:$Port"

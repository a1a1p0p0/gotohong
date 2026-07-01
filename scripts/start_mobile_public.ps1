$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$MobileRoot = Join-Path $ProjectRoot "mobile"
$Port = if ($env:WUXING_MOBILE_PORT) { $env:WUXING_MOBILE_PORT } else { "3000" }
$HostIp = if ($env:WUXING_MOBILE_HOST) { $env:WUXING_MOBILE_HOST } else { "0.0.0.0" }
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

Push-Location $MobileRoot
npm.cmd run build
Pop-Location

Start-Process `
    -FilePath npx.cmd `
    -ArgumentList @("next", "start", "-H", "$HostIp", "-p", "$Port") `
    -WorkingDirectory $MobileRoot `
    -RedirectStandardOutput (Join-Path $LogDir "mobile_public.out.log") `
    -RedirectStandardError (Join-Path $LogDir "mobile_public.err.log") `
    -WindowStyle Hidden

Start-Sleep -Seconds 8
Write-Host "Mobile public running: http://$HostIp`:$Port"

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

$LogDir = Join-Path $ProjectRoot "logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

Push-Location $MobileRoot
npm.cmd run build
Pop-Location

Start-Process `
    -FilePath npm.cmd `
    -ArgumentList @("run", "start") `
    -WorkingDirectory $MobileRoot `
    -RedirectStandardOutput (Join-Path $LogDir "mobile_prod.out.log") `
    -RedirectStandardError (Join-Path $LogDir "mobile_prod.err.log") `
    -WindowStyle Hidden

Start-Sleep -Seconds 8
Write-Host "Mobile production running: http://127.0.0.1:$Port"

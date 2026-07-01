$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$env:Path += ";C:\Program Files\nodejs;C:\Users\Administrator\AppData\Roaming\npm"

powershell -ExecutionPolicy Bypass -File scripts\start_backend.ps1
powershell -ExecutionPolicy Bypass -File scripts\start_mobile.ps1

python scripts\smoke_test.py --base-url http://127.0.0.1:8000
node scripts\check_mobile_pages.js

Push-Location mobile
npm.cmd run build
Pop-Location

python -m unittest discover -s wuxing_stock_app\tests

Write-Host "verify_all completed"

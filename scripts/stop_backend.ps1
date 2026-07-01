$ErrorActionPreference = "Stop"

$Port = 8000
$Existing = netstat -ano | Select-String ":$Port" | ForEach-Object {
    ($_ -split "\s+")[-1]
} | Select-Object -Unique

$Stopped = 0
foreach ($ProcId in $Existing) {
    if ($ProcId -match "^\d+$" -and $ProcId -ne "0") {
        Stop-Process -Id ([int]$ProcId) -Force -ErrorAction SilentlyContinue
        $Stopped += 1
    }
}

Write-Host "Stopped backend processes: $Stopped"

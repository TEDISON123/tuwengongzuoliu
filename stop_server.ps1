# ============================================================================
#  tuwengongzuoliu - Stop local preview server
#  Usage: Double-click
# ============================================================================

$Port = 8765

Write-Host ""
Write-Host "[INFO] Checking port $Port..." -ForegroundColor Cyan

$conn = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue

if ($null -eq $conn) {
    Write-Host "[OK]   Port $Port is free. No server is running." -ForegroundColor Green
} else {
    $pid_target = $conn.OwningProcess | Select-Object -First 1
    Write-Host "[INFO] Found PID $pid_target, stopping..." -ForegroundColor Cyan

    try {
        Stop-Process -Id $pid_target -Force -ErrorAction Stop
        Write-Host "[OK]   Stopped PID $pid_target" -ForegroundColor Green
    } catch {
        Write-Host "[ERR]  Failed: $_" -ForegroundColor Red
    }

    # Fallback cleanup
    $stillRunning = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if ($null -ne $stillRunning) {
        Write-Host "[WARN] Port still in use, force-clearing..." -ForegroundColor Yellow
        Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue |
            ForEach-Object { try { Stop-Process -Id $_.OwningProcess -Force } catch {} }
    }
}

Write-Host ""
Write-Host "[HINT] Manual: Get-Process python | Stop-Process" -ForegroundColor DarkGray
Write-Host ""
Read-Host "Press Enter to exit"

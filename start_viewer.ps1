# ============================================================================
#  tuwengongzuoliu - One-click local preview server
#  Usage: Double-click this .ps1, or run from PowerShell
# ============================================================================

$ErrorActionPreference = "Stop"
$Host.UI.RawUI.WindowTitle = "tuwengongzuoliu Preview"

# ---- Config ----
$ProjectRoot = "D:\cadabra_tools003\AgentPro\tuwengongzuoliu"
$Port        = 8765
$ServerDir   = $ProjectRoot

Set-Location $ProjectRoot

# ---- Check if port is already in use ----
function Test-PortInUse($port) {
    $conn = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    return $null -ne $conn
}

if (Test-PortInUse $Port) {
    Write-Host ""
    Write-Host "[WARN] Port $Port is already in use. Server may already be running." -ForegroundColor Yellow
    Write-Host "       Open browser directly: http://localhost:$Port/" -ForegroundColor Yellow
    Write-Host ""
} else {
    # ---- Start background HTTP server ----
    Write-Host ""
    Write-Host "[INFO] Starting local static file server..." -ForegroundColor Cyan
    Write-Host "       Port : $Port"
    Write-Host "       Root : $ServerDir"
    Write-Host ""

    $serverArgs = "-m http.server $Port --bind 127.0.0.1"
    $serverProcess = Start-Process `
        -FilePath "python" `
        -ArgumentList $serverArgs `
        -WorkingDirectory $ServerDir `
        -WindowStyle Hidden `
        -RedirectStandardOutput "$env:TEMP\tuwengongzuoliu_server.log" `
        -RedirectStandardError  "$env:TEMP\tuwengongzuoliu_server.err.log" `
        -PassThru

    Start-Sleep -Seconds 1.5

    if (Test-PortInUse $Port) {
        Write-Host "[OK]   Server started: http://localhost:$Port/" -ForegroundColor Green
    } else {
        Write-Host "[ERR]  Server failed to start. Check if Python is installed." -ForegroundColor Red
        Write-Host "       Log: $env:TEMP\tuwengongzuoliu_server.err.log" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# ---- Menu: select page to open ----
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  tuwengongzuoliu Preview Launcher" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  [1] 6-Card Panorama (Recommended - Main deliverable)"
Write-Host "      examples/mortgage_vs_invest/all_pages_viewer.html"
Write-Host ""
Write-Host "  [2] Pipeline Controller (Interactive)"
Write-Host "      templates/pipeline_controller.html"
Write-Host ""
Write-Host "  [3] Incentive Calculator (Interactive)"
Write-Host "      templates/incentive_calculator.html"
Write-Host ""
Write-Host "  [4] Finance Knowledge Graph (Interactive)"
Write-Host "      templates/finance_graph_explorer.html"
Write-Host ""
Write-Host "  [5] Single Card - Cover"
Write-Host "  [6] Single Card - Pain Point"
Write-Host "  [7] Single Card - Cognitive Gap"
Write-Host "  [8] Single Card - Pro Side"
Write-Host "  [9] Single Card - Con Side"
Write-Host "  [10] Single Card - Stand"
Write-Host ""
Write-Host "  [0] Start server only, no browser"
Write-Host ""

$choice = Read-Host "Enter choice (1-10, 0, or Enter for default [1])"

$relPath = switch ($choice) {
    "1"  { "examples/mortgage_vs_invest/all_pages_viewer.html" }
    "2"  { "templates/pipeline_controller.html" }
    "3"  { "templates/incentive_calculator.html" }
    "4"  { "templates/finance_graph_explorer.html" }
    "5"  { "examples/mortgage_vs_invest/page_1.html" }
    "6"  { "examples/mortgage_vs_invest/page_2.html" }
    "7"  { "examples/mortgage_vs_invest/page_3.html" }
    "8"  { "examples/mortgage_vs_invest/page_4.html" }
    "9"  { "examples/mortgage_vs_invest/page_5.html" }
    "10" { "examples/mortgage_vs_invest/page_6.html" }
    "0"  { $null }
    default { "examples/mortgage_vs_invest/all_pages_viewer.html" }
}

if ($null -ne $relPath) {
    $url = "http://localhost:${Port}/$relPath"
    Write-Host ""
    Write-Host "[INFO] Opening browser..." -ForegroundColor Cyan
    Write-Host "       $url" -ForegroundColor Cyan
    Start-Process $url
} else {
    Write-Host ""
    Write-Host "[INFO] Server running at http://localhost:$Port/" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "[HINT] To stop server: double-click stop_server.ps1" -ForegroundColor DarkGray
Write-Host "       Or run: Get-Process python | Stop-Process" -ForegroundColor DarkGray
Write-Host ""
Write-Host "Window can be closed. Server keeps running in background." -ForegroundColor DarkGray
Write-Host ""

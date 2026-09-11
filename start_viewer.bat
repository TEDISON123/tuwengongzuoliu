@echo off
chcp 65001 >nul
REM ============================================================================
REM  tuwengongzuoliu 一键启动 (双击即用)
REM  内部用 PowerShell 执行 start_viewer.ps1
REM ============================================================================

setlocal
cd /d "%~dp0"

echo.
echo ============================================
echo   tuwengongzuoliu 一键启动
echo ============================================
echo   正在启动本地预览服务器并打开浏览器...
echo.

set "PS_EXE=powershell.exe"
set "PS_FLAGS=-NoProfile -ExecutionPolicy Bypass -File"

"%PS_EXE%" %PS_FLAGS% "%~dp0start_viewer.ps1"

endlocal

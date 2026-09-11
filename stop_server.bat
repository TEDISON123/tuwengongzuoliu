@echo off
chcp 65001 >nul
REM ============================================================================
REM  tuwengongzuoliu 一键关闭服务器 (双击即用)
REM ============================================================================

setlocal
cd /d "%~dp0"

set "PS_EXE=powershell.exe"
set "PS_FLAGS=-NoProfile -ExecutionPolicy Bypass -File"

"%PS_EXE%" %PS_FLAGS% "%~dp0stop_server.ps1"

endlocal

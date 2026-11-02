@echo off
setlocal
cd /d "%~dp0"
set "PYTHONUTF8=1"
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\setup_environment.ps1"
set "PPS_EXIT_CODE=%ERRORLEVEL%"
if not "%PPS_NO_PAUSE%"=="1" pause
exit /b %PPS_EXIT_CODE%

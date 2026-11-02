@echo off
setlocal
cd /d "%~dp0"
set "PYTHONUTF8=1"
call "%~dp0scripts\check_environment.bat"
if errorlevel 1 goto fail
"%PPS_PYTHON%" -m unittest discover -s tests -v
set "PPS_EXIT_CODE=%ERRORLEVEL%"
if not "%PPS_NO_PAUSE%"=="1" pause
exit /b %PPS_EXIT_CODE%
:fail
if not "%PPS_NO_PAUSE%"=="1" pause
exit /b 1

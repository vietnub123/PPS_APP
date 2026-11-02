@echo off
setlocal
cd /d "%~dp0"
set "PYTHONUTF8=1"
if "%~1"=="" (
    echo Cach dung: CHAY_CONSOLE.bat examples\02_bessel.json
    exit /b 2
)
call "%~dp0scripts\check_environment.bat"
if errorlevel 1 exit /b 1
"%PPS_PYTHON%" exam_cli.py "%~1"
exit /b %ERRORLEVEL%

@echo off
setlocal
cd /d "%~dp0"
set "PYTHONUTF8=1"
echo Dang khoi dong PPS Python, vui long cho...
call "%~dp0scripts\check_environment.bat"
if errorlevel 1 goto fail
"%PPS_PYTHON%" main.py
set "PPS_EXIT_CODE=%ERRORLEVEL%"
if "%PPS_EXIT_CODE%"=="0" exit /b 0
echo Khong khoi dong duoc. Chay lai CAI_DAT.bat de kiem tra moi truong.
if not "%PPS_NO_PAUSE%"=="1" pause
exit /b %PPS_EXIT_CODE%
:fail
if not "%PPS_NO_PAUSE%"=="1" pause
exit /b 1

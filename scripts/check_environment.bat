@echo off
for %%I in ("%~dp0..\.venv\Scripts\python.exe") do set "PPS_PYTHON=%%~fI"
if not exist "%PPS_PYTHON%" goto missing
"%PPS_PYTHON%" -c "import sys; sys.exit(0 if sys.version_info >= (3,12) and sys.maxsize > 2**32 else 1)" >nul 2>&1
if errorlevel 1 goto incompatible
exit /b 0

:missing
echo Khong tim thay moi truong .venv cua ung dung.
echo Cai Python 3.12 64-bit, sau do chay CAI_DAT.bat.
exit /b 1

:incompatible
echo Moi truong .venv hien tai khong dung duoc. Ung dung can Python 3.12 tro len, 64-bit.
echo Chay CAI_DAT.bat de tao lai .venv bang Python 3.12; ban cu se duoc sao luu.
exit /b 1

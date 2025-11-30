@echo off
echo Starting NPTEL Video Search Engine Backend...
echo.

REM Change to the directory where this batch file is located
cd /d "%~dp0"

REM Run the Python server
python start_backend.py

pause

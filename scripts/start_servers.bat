@echo off
echo ========================================
echo   Amagi Video Search Engine
echo   Knowledge Graph Feature
echo ========================================
echo.
echo Starting servers...
echo.
echo [1/2] Starting Backend Server (Port 8000)...
start "Backend Server" cmd /k "cd /d "%~dp0.." && .venv\Scripts\python.exe run_server.py"
timeout /t 3 /nobreak > nul

echo [2/2] Starting Frontend Server (Port 8080)...
start "Frontend Server" cmd /k "cd /d "%~dp0..\frontend" && python -m http.server 8080"
timeout /t 3 /nobreak > nul

echo.
echo ========================================
echo   SERVERS STARTED SUCCESSFULLY!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:8080
echo.
echo Opening application in browser...
timeout /t 2 /nobreak > nul

start http://localhost:8080/index.html

echo.
echo ========================================
echo   Instructions:
echo   - Main Page: http://localhost:8080/index.html
echo   - Knowledge Graph: http://localhost:8080/knowledge-graph.html
echo   - Backend API: http://localhost:8000
echo.
echo   Keep both terminal windows open!
echo   Close them when you're done.
echo ========================================
echo.
pause

@echo off
cd /d "%~dp0"
echo Switch GUI wird gestartet...
echo Oeffne http://localhost:8000 im Browser.
echo Beenden mit STRG+C
echo.
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
pause

@echo off
echo Starting quality_control application with Waitress...
echo This will run in the background as a Windows service
echo.
echo Application will be available at: http://localhost:8000
echo Press Ctrl+C to stop the server

REM Run the waitress deployment script
python deploy_waitress_production.py

pause

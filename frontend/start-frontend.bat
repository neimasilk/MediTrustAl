@echo off
echo Starting MediTrustAl Frontend using Python HTTP Server...
echo.
echo Frontend will be available at: http://localhost:8080
echo Backend API is at: http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo.
python -m http.server 8080
pause
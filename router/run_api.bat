@echo off
REM run_api.bat - Start the Axeane Automation API server

echo.
echo ========================================
echo  AXEANE AUTOMATION API SERVER
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo [ERROR] Virtual environment not found!
    echo Please run install.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

echo Starting API server on http://localhost:8000
echo API docs available at http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the API server
python endpoint.py

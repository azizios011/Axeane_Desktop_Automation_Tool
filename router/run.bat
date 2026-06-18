@echo off
REM run.bat - Axeane Kompta Automation Engine Launcher
echo.
echo ========================================
echo  AXEANE KOMPTA AUTOMATION ENGINE
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo [ERROR] Virtual environment not found!
    echo Please run install.bat first to set up the application.
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)

echo Starting application...
echo.

REM Run the application
python run.py

REM If the script exits, pause to show any error messages
if errorlevel 1 (
    echo.
    echo [ERROR] Application exited with errors
    pause
) else (
    echo.
    echo Application closed successfully
    pause
)

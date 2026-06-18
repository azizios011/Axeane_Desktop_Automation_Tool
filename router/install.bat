@echo off
REM install.bat - Axeane Kompta Automation Engine Setup
echo.
echo ========================================
echo  AXEANE AUTOMATION - INSTALLATION
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo [1/5] Python detected successfully
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo [2/5] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
) else (
    echo [2/5] Virtual environment already exists
)
echo.

REM Activate virtual environment
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo.

REM Install Python dependencies
echo [4/5] Installing Python dependencies...
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install Python dependencies
    pause
    exit /b 1
)
echo.

REM Install Playwright browsers
echo [5/5] Installing Playwright browsers (this may take a few minutes)...
python -m playwright install chromium
if errorlevel 1 (
    echo [ERROR] Failed to install Playwright browsers
    pause
    exit /b 1
)
echo.

echo ========================================
echo  INSTALLATION COMPLETE!
echo ========================================
echo.
echo You can now run the application using: run.bat
echo.
pause

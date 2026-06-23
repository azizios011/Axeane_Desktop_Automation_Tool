@echo off
REM uninstall.bat - Axeane Kompta Automation Engine Cleanup
echo.
echo ========================================
echo  AXEANE AUTOMATION - UNINSTALLATION
echo ========================================
echo.

REM Step 1: Remove virtual environment
if exist "venv" (
    echo [1/4] Removing virtual environment...
    rmdir /s /q venv
    if errorlevel 1 (
        echo [ERROR] Failed to remove virtual environment
        pause
        exit /b 1
    )
) else (
    echo [1/4] No virtual environment found
)
echo.

REM Step 2: Remove Playwright browsers cache
echo [2/4] Removing Playwright browsers...
setlocal
set PLAYWRIGHT_BROWSERS_PATH=%USERPROFILE%\AppData\Local\ms-playwright
if exist "%PLAYWRIGHT_BROWSERS_PATH%" (
    rmdir /s /q "%PLAYWRIGHT_BROWSERS_PATH%"
    if errorlevel 1 (
        echo [ERROR] Failed to remove Playwright browsers
        pause
        exit /b 1
    )
) else (
    echo No Playwright browsers found
)
endlocal
echo.

REM Step 3: Uninstall globally installed requirements (if any)
if exist "requirements.txt" (
    echo [3/4] Uninstalling globally installed Python packages...
    for /f %%i in (requirements.txt) do (
        pip uninstall -y %%i >nul 2>&1
    )
    echo Global packages from requirements.txt removed (if they were installed).
) else (
    echo No requirements.txt found, skipping global uninstall.
)
echo.

REM Step 4: Clean Python cache files
echo [4/4] Cleaning Python cache files...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
del /s /q *.pyc >nul 2>&1
echo.

echo ========================================
echo  UNINSTALLATION COMPLETE!
echo ========================================
echo.
pause

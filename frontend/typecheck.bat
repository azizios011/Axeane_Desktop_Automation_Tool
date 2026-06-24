@echo off
REM Check TypeScript types
cd /d "%~dp0"
call node_modules\.bin\tsc --noEmit
pause

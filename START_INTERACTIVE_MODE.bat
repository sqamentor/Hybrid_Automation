@echo off
REM Quick Start Script - Launch Interactive Test Launcher
REM This script provides an easy way to start the interactive CLI

echo.
echo ================================================================================
echo    HYBRID AUTOMATION FRAMEWORK - Interactive Test Launcher
echo ================================================================================
echo.
echo    Starting interactive mode...
echo    Follow the on-screen prompts to run your tests!
echo.
echo ================================================================================
echo.echo    Clearing Python cache...
powershell -Command "Get-ChildItem -Path . -Recurse -Filter '__pycache__' -Directory -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force"
echo    Cache cleared!
echo.
automation

echo.
echo ================================================================================
echo    Thank you for using the Hybrid Automation Framework!
echo ================================================================================
echo.

pause

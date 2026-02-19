@echo off
REM ============================================================================
REM POM Test Runner - Windows Batch Launcher
REM Simple double-click execution for POM tests
REM ============================================================================

echo.
echo ================================================================================
echo    POM TEST EXECUTION LAUNCHER
echo    Interactive Page Object Model Test Runner
echo ================================================================================
echo.

REM Check if Python is available
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.8 or higher.
    echo.
    pause
    exit /b 1
)

REM Launch the interactive CLI
python run_pom_tests_cli.py

REM Check exit code
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Test execution failed with exit code: %errorlevel%
    echo.
)

echo.
echo ================================================================================
echo    Execution Complete
echo ================================================================================
echo.

pause

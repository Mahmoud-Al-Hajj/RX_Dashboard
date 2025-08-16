@echo off
echo 🚀 RemotelyX Job Automation Service
echo =====================================

echo.
echo Choose an option:
echo 1. Start API Server
echo 2. Start Dashboard
echo 3. Test System
echo 4. Run Workflow (with sample URLs)
echo 5. Export to Excel
echo 6. Show Statistics
echo.

set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" (
    echo Starting API Server...
    python main.py api
) else if "%choice%"=="2" (
    echo Starting Dashboard...
    python main.py dashboard
) else if "%choice%"=="3" (
    echo Testing System...
    python test_system.py
    pause
) else if "%choice%"=="4" (
    echo Running Workflow with sample URLs...
    python main.py workflow --urls "https://example.com/job1" "https://example.com/job2"
    pause
) else if "%choice%"=="5" (
    echo Exporting to Excel...
    python main.py export
    pause
) else if "%choice%"=="6" (
    echo Showing Statistics...
    python main.py stats
    pause
) else (
    echo Invalid choice. Please run the script again.
    pause
) 
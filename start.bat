@echo off
echo.
echo ========================================
echo    🚀 RemotelyX Job Intel Dashboard
echo ========================================
echo.
echo Starting RemotelyX Job Intelligence System...
echo.

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    echo.
    pause
    exit /b 1
)

echo ✅ Docker is running
echo.

REM Check if docker-compose.yml exists
if not exist "docker-compose.yml" (
    echo ❌ docker-compose.yml not found in current directory
    echo.
    pause
    exit /b 1
)

echo 📋 Found docker-compose.yml
echo.

REM Stop any existing containers
echo 🛑 Stopping any existing containers...
docker-compose down
echo.

REM Build and start the services
echo 🏗️  Building and starting services...
docker-compose up --build -d

if %errorlevel% neq 0 (
    echo ❌ Failed to start services
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Services started successfully!
echo.

REM Wait a moment for services to initialize
echo ⏳ Waiting for services to initialize...
timeout /t 10 /nobreak >nul

REM Check if services are running
echo 🔍 Checking service status...
docker-compose ps

echo.
echo ========================================
echo    🎉 RemotelyX Job Intel is Ready!
echo ========================================
echo.
echo 📊 Dashboard: http://localhost:8501
echo 🔌 API Docs:  http://localhost:8000/docs
echo 🗄️  MongoDB:   localhost:27017
echo.
echo 💡 Quick Start:
echo    1. Open http://localhost:8501 in your browser
echo    2. Add some job URLs in the sidebar
echo    3. Click "Process Jobs" to start scraping
echo    4. View real-time analytics and insights
echo.
echo 🛑 To stop services: docker-compose down
echo 🔄 To restart: docker-compose restart
echo.
echo Press any key to open the dashboard...
pause >nul

REM Open dashboard in default browser
start http://localhost:8501

echo.
echo 🌐 Dashboard opened in your browser!
echo.
echo Press any key to exit...
pause >nul 
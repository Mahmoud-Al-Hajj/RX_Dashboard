@echo off
echo ========================================
echo RemotelyX Job Automation Service
echo ========================================
echo.

REM Check if .env file exists
if not exist ".env" (
    echo Creating .env file from template...
    copy "env.example" ".env"
    echo.
    echo Please edit .env file with your Gmail credentials before running!
    echo.
    pause
    exit /b 1
)

REM Check if MongoDB is running (optional)
echo Checking MongoDB connection...
python -c "import pymongo; client = pymongo.MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=3000); client.admin.command('ping'); print('MongoDB: Connected')" 2>nul
if errorlevel 1 (
    echo MongoDB: Not connected (will use default settings)
    echo To start MongoDB with Docker: docker run -d -p 27017:27017 mongo:6.0
    echo.
)

echo.
echo Starting RemotelyX API Server...
echo API will be available at: http://localhost:8000
echo API docs at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python main.py api

pause 
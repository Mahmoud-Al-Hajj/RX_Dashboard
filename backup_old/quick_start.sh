#!/bin/bash

# RemotelyX Job Automation Service - Quick Start Script

set -e

echo "🚀 RemotelyX Job Automation Service - Quick Start"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
check_python() {
    print_status "Checking Python installation..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python 3 is not installed. Please install Python 3.8+ first."
        exit 1
    fi
}

# Check if pip is installed
check_pip() {
    print_status "Checking pip installation..."
    if command -v pip3 &> /dev/null; then
        print_success "pip3 found"
    else
        print_error "pip3 is not installed. Please install pip first."
        exit 1
    fi
}

# Install dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    if pip3 install -r requirements.txt; then
        print_success "Dependencies installed successfully"
    else
        print_error "Failed to install dependencies"
        exit 1
    fi
}

# Setup environment file
setup_env() {
    print_status "Setting up environment configuration..."
    
    if [ ! -f .env ]; then
        if [ -f env.example ]; then
            cp env.example .env
            print_success "Created .env file from template"
            print_warning "Please edit .env file with your configuration before running the service"
        else
            print_error "env.example file not found"
            exit 1
        fi
    else
        print_warning ".env file already exists"
    fi
}

# Check MongoDB
check_mongodb() {
    print_status "Checking MongoDB connection..."
    
    # Try to connect to MongoDB
    if python3 -c "
import pymongo
try:
    client = pymongo.MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print('MongoDB connection successful')
except Exception as e:
    print('MongoDB connection failed:', e)
    exit(1)
" 2>/dev/null; then
        print_success "MongoDB connection successful"
    else
        print_warning "MongoDB connection failed"
        print_status "You can:"
        print_status "1. Install MongoDB locally"
        print_status "2. Use MongoDB Atlas (cloud)"
        print_status "3. Use Docker: docker run -d -p 27017:27017 --name mongodb mongo:6.0"
    fi
}

# Run tests
run_tests() {
    print_status "Running setup tests..."
    if python3 test_setup.py; then
        print_success "All tests passed"
    else
        print_warning "Some tests failed. Please check your configuration."
    fi
}

# Show usage instructions
show_usage() {
    echo ""
    echo "📖 Usage Instructions:"
    echo "======================"
    echo ""
    echo "1. Edit the .env file with your configuration:"
    echo "   - GMAIL_EMAIL: Your Gmail address"
    echo "   - GMAIL_PASSWORD: Your Gmail app password"
    echo "   - SENDER_EMAIL: Email address to monitor"
    echo "   - MONGODB_URI: MongoDB connection string"
    echo ""
    echo "2. Run the service in different modes:"
    echo "   - API Server:     python3 main.py api"
    echo "   - Scheduler:      python3 main.py scheduler"
    echo "   - One-time:       python3 main.py process"
    echo "   - Test mode:      python3 main.py test"
    echo ""
    echo "3. Using Docker:"
    echo "   - Start services: docker-compose up -d"
    echo "   - View logs:      docker-compose logs -f"
    echo "   - Stop services:  docker-compose down"
    echo ""
    echo "4. API Documentation:"
    echo "   - When running API server, visit: http://localhost:8000/docs"
    echo ""
}

# Main execution
main() {
    echo ""
    check_python
    check_pip
    install_dependencies
    setup_env
    check_mongodb
    run_tests
    show_usage
    
    echo ""
    print_success "Setup completed! 🎉"
    echo ""
    print_status "Next steps:"
    print_status "1. Edit .env file with your credentials"
    print_status "2. Ensure MongoDB is running"
    print_status "3. Run: python3 main.py api"
    echo ""
}

# Run main function
main "$@" 
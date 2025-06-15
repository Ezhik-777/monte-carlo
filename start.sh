#!/bin/bash

# Monte Carlo Investment Calculator - Quick Start Script

set -e

echo "🚀 Monte Carlo Investment Calculator - Quick Start"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8 or later."
    exit 1
fi

print_status "Python 3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is not installed. Please install pip3."
    exit 1
fi

print_status "pip3 found"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_info "Creating virtual environment..."
    python3 -m venv venv
    print_status "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_info "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
print_info "Installing dependencies..."
if [ -f "requirements-web.txt" ]; then
    pip install -r requirements-web.txt
    print_status "Dependencies installed successfully"
else
    print_error "requirements-web.txt not found"
    exit 1
fi

# Create necessary directories
print_info "Creating directories..."
mkdir -p logs
mkdir -p static/images
print_status "Directories created"

# Check if all required files exist
required_files=("app.py" "templates/index.html" "static/css/style.css" "static/js/app.js")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        print_error "Required file missing: $file"
        exit 1
    fi
done

print_status "All required files present"

# Run some basic tests
print_info "Running basic tests..."

# Test Python imports
python3 -c "
import sys
required_modules = ['flask', 'numpy', 'scipy', 'matplotlib', 'seaborn', 'pandas', 'joblib']
missing = []
for module in required_modules:
    try:
        __import__(module)
    except ImportError:
        missing.append(module)

if missing:
    print('Missing modules:', missing)
    sys.exit(1)
else:
    print('All required modules available')
"

if [ $? -eq 0 ]; then
    print_status "All Python modules available"
else
    print_error "Some Python modules are missing"
    exit 1
fi

# Start the application
echo ""
echo "🎉 Setup completed successfully!"
echo ""
print_info "Starting Monte Carlo Investment Calculator..."
echo ""
echo "📱 The application will be available at: http://localhost:5000"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Start the app
if [ -f "run.py" ]; then
    python3 run.py
else
    python3 app.py
fi
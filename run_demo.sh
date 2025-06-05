#!/bin/bash

# AI Chat Downloader - Demo Version Startup Script
# For macOS and Linux users (runs web_app.py)

echo "🚀 AI Chat Downloader - Demo Version Setup & Run Script"
echo "========================================================"

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
print_status "Checking Python installation..."
if ! command -v python3 &>/dev/null; then
  print_error "Python 3 is not installed. Please install Python 3.8+ first."
  echo "Visit: https://www.python.org/downloads/"
  exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
print_success "Python $PYTHON_VERSION found"

# Check if pip is available
if ! command -v pip3 &>/dev/null; then
  print_error "pip3 is not available. Please install pip first."
  exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
  print_status "Creating virtual environment..."
  python3 -m venv venv
  if [ $? -eq 0 ]; then
    print_success "Virtual environment created"
  else
    print_error "Failed to create virtual environment"
    exit 1
  fi
else
  print_success "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip >/dev/null 2>&1

# Install/update requirements
print_status "Installing/updating dependencies..."
if [ -f "requirements.txt" ]; then
  pip install -r requirements.txt >/dev/null 2>&1
  if [ $? -eq 0 ]; then
    print_success "Dependencies installed successfully"
  else
    print_error "Failed to install dependencies"
    exit 1
  fi
else
  print_error "requirements.txt not found"
  exit 1
fi

# Check if Playwright browsers are installed
print_status "Checking Playwright browsers..."
python -c "from playwright.sync_api import sync_playwright; sync_playwright().start()" 2>/dev/null
if [ $? -ne 0 ]; then
  print_warning "Playwright browsers not installed. Installing..."
  playwright install >/dev/null 2>&1
  if [ $? -eq 0 ]; then
    print_success "Playwright browsers installed"
  else
    print_error "Failed to install Playwright browsers"
    exit 1
  fi
else
  print_success "Playwright browsers are ready"
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "🔥 Starting AI Chat Downloader Demo..."
echo "📱 The demo will open in your default browser"
echo "⚡ Demo features: Queue management (max 3 users)"
echo "🛑 Press Ctrl+C to stop the server"
echo ""
echo "========================================================"

# Run the Streamlit demo app
streamlit run web_app.py

# Deactivate virtual environment when done
deactivate

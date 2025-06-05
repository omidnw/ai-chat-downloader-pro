@echo off
REM AI Chat Downloader - Local Startup Script for Windows

echo 🚀 AI Chat Downloader - Local Setup ^& Run Script
echo ==================================================

REM Check if Python is installed
echo [INFO] Checking Python installation...
python --version >NUL 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [SUCCESS] Python %PYTHON_VERSION% found

REM Check if pip is available
echo [INFO] Checking pip installation...
python -m pip --version >NUL 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] pip is not available.
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv\" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [SUCCESS] Virtual environment created
) else (
    echo [SUCCESS] Virtual environment already exists
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip >NUL 2>&1

REM Install/update requirements
echo [INFO] Installing/updating dependencies...
if exist "requirements.txt" (
    python -m pip install -r requirements.txt >NUL 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
    echo [SUCCESS] Dependencies installed successfully
) else (
    echo [ERROR] requirements.txt not found
    pause
    exit /b 1
)

REM Check if Playwright browsers are installed
echo [INFO] Checking Playwright browsers...
python -c "from playwright.sync_api import sync_playwright; sync_playwright().start()" >NUL 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Playwright browsers not installed. Installing...
    playwright install >NUL 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install Playwright browsers
        pause
        exit /b 1
    )
    echo [SUCCESS] Playwright browsers installed
) else (
    echo [SUCCESS] Playwright browsers are ready
)

echo.
echo 🎉 Setup completed successfully!
echo.
echo 🔥 Starting AI Chat Downloader...
echo 📱 The app will open in your default browser
echo 🛑 Press Ctrl+C to stop the server
echo.
echo ==================================================

REM Run the Streamlit app
streamlit run app.py --server.port 8501 --server.address localhost

REM Deactivate virtual environment when done
call deactivate

pause 
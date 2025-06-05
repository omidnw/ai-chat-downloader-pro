#!/usr/bin/env python3
"""
Setup script for ChatGPT Chat Downloader
Handles Playwright browser installation for different environments
Supports Persian/Farsi, Arabic, and other RTL languages with advanced text direction detection
"""
import os
import subprocess
import sys
from pathlib import Path


def install_playwright_browsers():
    """Install Playwright browsers for web scraping ChatGPT conversations"""
    try:
        print("Installing Playwright browsers...")
        result = subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            capture_output=True,
            text=True,
            check=True,
        )
        print("✅ Playwright browsers installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Playwright browsers: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error installing Playwright browsers: {e}")
        return False


def check_environment():
    """Check if we're running in a deployment environment"""
    # Common deployment environment variables
    deployment_envs = [
        "STREAMLIT_SHARING",  # Streamlit Cloud
        "HEROKU",  # Heroku
        "RENDER",  # Render
        "RAILWAY_ENVIRONMENT",  # Railway
    ]

    for env in deployment_envs:
        if os.getenv(env):
            return env

    return None


def main():
    """Main setup function"""
    print("🚀 Setting up ChatGPT Chat Downloader with Persian/Farsi RTL support...")

    # Check environment
    env = check_environment()
    if env:
        print(f"📡 Detected deployment environment: {env}")
    else:
        print("💻 Running in local development environment")

    # Install Playwright browsers
    success = install_playwright_browsers()

    if success:
        print("✅ Setup completed successfully!")
        print("📝 Ready to download ChatGPT conversations with RTL/LTR detection")
        return 0
    else:
        print("❌ Setup failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())

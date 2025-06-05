# �� AI Chat Downloader Pro

A modern, **enhanced** web application built with Streamlit that converts **ChatGPT and Claude** shared conversations into clean, formatted Markdown files. Features automatic platform detection, advanced text direction detection with excellent support for Persian/Farsi, Arabic, and other RTL languages, plus a beautiful, user-friendly interface with **queue management, batch processing, and async operations**.

## 🚀 Project Links

- **Landing Page**: [https://omidnw.github.io/chatgpt-downloader](https://omidnw.github.io/chatgpt-downloader)
- **Source Code**: [https://github.com/omidnw/chatgpt-downloader](https://github.com/omidnw/chatgpt-downloader)
- **Local Installation Required**: Due to Playwright browser automation requirements

## 📚 Documentation

- **📋 [Quick Start Guide](./QUICK_START.md)** - One-click setup scripts for all platforms
- **🚀 [Enhancement Summary](./ENHANCEMENT_SUMMARY.md)** - Complete list of new features and improvements
- **🌍 [RTL/LTR Improvements](./RTL_LTR_IMPROVEMENTS.md)** - Advanced text direction detection documentation
- **🔧 [Utils Package Documentation](./utils/README.md)** - Detailed API reference and technical guide
- **🧪 [Tests & Demos Guide](./tests/README.md)** - Comprehensive test suite documentation and usage guide

## ✨ Enhanced Features

### Core Features

- 🤖 **Multi-Platform Support**: Works with both ChatGPT and Claude conversations
- 🔍 **Automatic Detection**: Automatically detects platform based on URL with visual badges
- 🔗 **Easy URL Input**: Simply paste a share link from either platform
- 📱 **Responsive Design**: Works on desktop and mobile devices
- 🌍 **Advanced RTL/LTR Detection**: Sophisticated algorithms for Persian/Farsi, Arabic, and other RTL languages
- 🎯 **Multiple Detection Methods**: Auto, First-Strong, Enhanced Counting, and Weighted algorithms
- 🎨 **Clean Formatting**: Professional Markdown output with proper structure
- 👥 **Speaker Identification**: Clear distinction between User and AI assistant messages
- 📊 **Content Statistics**: Word and character count for downloaded conversations
- 💾 **One-click Download**: Direct file download as `.md` format
- 🛡️ **Enhanced Error Handling**: Comprehensive error messages and troubleshooting tips
- 🇮🇷 **Persian Support**: Excellent handling of Persian/Farsi text with proper direction detection

> **📖 [Learn more about RTL/LTR features](./RTL_LTR_IMPROVEMENTS.md)**

### 🚀 **New Enhanced Features**

- **📊 Processing Modes**: Single URL, Batch Processing, and Queue Management
- **⚡ Async Operations**: Full async/await architecture for better performance
- **🔄 Queue Management**: Background processing with priority support and persistent queues
- **📋 Batch Processing**: Process multiple URLs concurrently with progress tracking
- **🎛️ Real-time Monitoring**: Live status updates and progress bars
- **🧰 Modular Architecture**: Organized utils package with 50+ functions
- **⚠️ Warning Suppression**: Clean operation without asyncio/Streamlit warnings
- **🔧 Enhanced Dependencies**: Optional advanced features with graceful fallbacks

> **🚀 [See complete enhancement list](./ENHANCEMENT_SUMMARY.md)**

## 🤖 Supported Platforms

| Platform    | Supported URLs                                                         | Status             | Features                  |
| ----------- | ---------------------------------------------------------------------- | ------------------ | ------------------------- |
| **ChatGPT** | `https://chatgpt.com/share/...`<br>`https://chat.openai.com/share/...` | ✅ Fully Supported | Standard + Stealth Mode   |
| **Claude**  | `https://claude.ai/share/...`                                          | ✅ Fully Supported | Advanced Stealth + Bypass |

## 📋 Prerequisites

- Python 3.8 or higher
- Internet connection for downloading conversations
- **Optional**: Enhanced dependencies for queue and batch features

## 🛠️ Installation

### 🚀 **Quick Start (Recommended)**

For the **easiest setup experience**, use our automated startup scripts:

**📋 [→ See QUICK_START.md for One-Click Setup ←](./QUICK_START.md)**

The startup scripts automatically handle:

- ✅ Python version checking
- ✅ Virtual environment setup
- ✅ Dependencies installation
- ✅ Playwright browser setup
- ✅ Application startup

### 🏠 Manual Installation (Advanced)

#### **Step 1: Prerequisites**

- **Python 3.8+** installed on your system
- **Git** for cloning the repository
- **Internet connection** for downloading dependencies

#### **Step 2: Clone & Setup**

```bash
# Clone the repository
git clone https://github.com/omidnw/chatgpt-downloader.git
cd chatgpt-downloader

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

#### **Step 3: Install Dependencies**

```bash
# Install core dependencies
pip install -r requirements.txt

# Install browser for Playwright (REQUIRED)
playwright install chromium

# Install enhanced features (optional but recommended)
pip install litequeue asyncio-throttle aiofiles
```

#### **Step 4: Run Application**

```bash
# Start the Streamlit app
streamlit run app.py

# The app will automatically open in your browser at:
# http://localhost:8501
```

#### **Step 5: Verify Installation**

- ✅ App opens without errors
- ✅ Platform auto-detection works
- ✅ Queue features available (if optional deps installed)
- ✅ Test with a real share URL

## 📖 Usage Guide

### Enhanced Processing Modes

The application now offers **three processing modes** accessible via the sidebar:

#### 1. **📄 Single URL Mode** (Default)

- Paste one URL and get instant results
- Real-time status updates during processing
- Platform auto-detection with visual badges
- Perfect for individual conversations

#### 2. **📊 Batch Processing Mode**

- Process multiple URLs simultaneously
- Support for mixed platforms (ChatGPT + Claude)
- Real-time progress tracking for each URL
- Downloadable archive of all results
- Configurable concurrency settings

#### 3. **🔄 Queue Management Mode** (Advanced)

- Add tasks to persistent background queue
- Priority support (1-5 levels)
- Background processing with session monitoring
- Perfect for large-scale operations

### How to Download AI Conversations

#### For ChatGPT:

1. **Open your ChatGPT conversation** in your browser
2. **Click the share button** (🔗) in the top-right corner of the conversation
3. **Click "Create public link"** to generate a shareable URL
4. **Copy the generated link**

#### For Claude:

1. **Open your Claude conversation** in your browser
2. **Click the share button** (🔗) at the top of the conversation
3. **Copy the generated share link**

#### Then:

5. **Choose your processing mode** in the sidebar
6. **Paste the link(s)** into the appropriate input field
7. **Configure your options** (RTL/LTR detection, speaker identification)
8. **Process the conversation(s)** - platform will be auto-detected
9. **Download the results** using the provided download buttons

## 🏗️ Enhanced Project Structure

```
ai-chat-downloader/
├── app.py                         # Main enhanced Streamlit application
├── web_app.py                     # 🆕 Demo version with queue limits
├── utils/                         # 🆕 Modular utils package
│   ├── __init__.py               # Unified imports (50+ functions)
│   ├── ai_downloader.py          # Unified AI downloader with auto-detection
│   ├── chatgpt_downloader.py     # ChatGPT-specific functionality
│   ├── claude_downloader.py      # Claude-specific functionality
│   ├── claude_stealth_scraper.py # Advanced Claude stealth operations
│   ├── browser_fetch.py          # Enhanced async web scraping
│   ├── async_queue_manager.py    # Queue management and batch processing
│   └── README.md                 # 📖 Utils package documentation
├── tests/                         # Test suites and demos
│   └── demo_async.py             # Enhanced async demo
├── requirements.txt               # Core + enhanced dependencies
├── scraping_queue.db             # Persistent queue database
├── setup.py                      # Package setup configuration
├── run_local.sh                   # 🆕 Unix/macOS startup script
├── run_local.bat                  # 🆕 Windows startup script
├── run_demo.sh                    # 🆕 Demo version startup script
├── .streamlit/
│   └── config.toml               # Streamlit configuration
├── docs/
│   └── index.html                # GitHub Pages landing page
├── .github/
│   └── workflows/
│       └── deploy-pages.yml      # GitHub Pages deployment
├── QUICK_START.md                 # 📋 One-click setup guide
├── ENHANCEMENT_SUMMARY.md         # 🚀 Detailed enhancement documentation
├── RTL_LTR_IMPROVEMENTS.md       # 🌍 RTL/LTR detection documentation
└── README.md                     # This file
```

> **🔧 [Technical details and API reference](./utils/README.md)**

## 🔧 Enhanced API Reference

> **📚 [Complete API documentation and examples](./utils/README.md)**

### Unified Utils Package

The new modular architecture provides easy access to all functionality:

```python
from utils import (
    # 🚀 Enhanced core functions
    ai_download,                  # Unified downloader with auto-detection
    scrape_with_auto_detection,   # Auto-detect platform and scrape
    scrape_multiple_urls,         # Batch processing with concurrency

    # 🔄 Queue management (optional)
    add_to_queue,                 # Add tasks with priority
    process_queue_task,           # Process background tasks
    get_queue_status,             # Monitor queue and sessions

    # 🎯 Platform detection
    detect_platform,              # Auto-detect from URL
    Platform,                     # Platform enumeration
    get_supported_platforms,      # Get platform list

    # ⚡ Quick access functions
    quick_scrape,                 # Single URL with auto-detection
    quick_batch_scrape,           # Simple batch processing
)

# Auto-detect platform and download
markdown = ai_download("https://chatgpt.com/share/...")

# Batch processing with mixed platforms
results = scrape_multiple_urls([
    "https://chatgpt.com/share/...",
    "https://claude.ai/share/..."
])

# Queue management (requires optional dependencies)
task_id = await add_to_queue(url, priority=1)
result = await process_queue_task()
```

### Legacy Compatibility

Original functions are still available for backward compatibility:

```python
# ChatGPT specific
import chatgpt_downloader
markdown = chatgpt_downloader.download("https://chatgpt.com/share/...")

# Claude specific
import claude_downloader
markdown = claude_downloader.download("https://claude.ai/share/...")
```

## 🧪 Testing & Demo

### Run Enhanced Tests

```bash
# Test core functionality
python tests/demo_async.py

# Test specific components
python -m pytest tests/ -v
```

### Demo Features

The enhanced demo showcases:

- ✅ Platform auto-detection
- ✅ Async batch processing
- ✅ Queue management
- ✅ Real-time status updates
- ✅ Error handling and recovery

## 🔧 Configuration

### Core Configuration (`.streamlit/config.toml`)

- **Theme colors**: Primary and secondary colors
- **Layout settings**: Sidebar visibility, error handling
- **Server settings**: CORS, XSRF protection
- **Browser settings**: Usage statistics, server address
- **Performance**: Warning suppression, caching settings

### Enhanced Dependencies

#### Core (Required)

```
streamlit>=1.28.0
playwright>=1.40.0
requests>=2.31.0
beautifulsoup4>=4.12.0
markdownify>=0.11.6
lxml>=4.9.0
```

#### Enhanced Features (Optional)

```
litequeue>=0.8.0         # Queue management
asyncio-throttle>=1.0.2  # Rate limiting
aiofiles>=22.1.0         # Async file operations
```

**Note**: The app gracefully degrades when optional dependencies are unavailable.

## 🚀 Deployment & Hosting

### ⚠️ **Important: Local Installation Required**

**This application requires local installation** due to Playwright browser automation dependencies. Streamlit Community Cloud and most cloud hosting platforms don't support browser automation tools.

### Deployment Options

#### 1. **Local Development (Recommended)**

- **Best for**: Personal use, development, testing
- **Requirements**: Local Python environment with Playwright
- **Performance**: Full features, fast execution
- **Setup**: Follow installation guide below

#### 2. **Self-Hosted Server**

- **Best for**: Team use, production deployment
- **Requirements**: VPS/server with Docker support
- **Considerations**: Requires server management and browser dependencies
- **Example platforms**: DigitalOcean, AWS EC2, Google Cloud VM

#### 3. **GitHub Pages (Landing Page Only)**

- **URL**: `https://omidnw.github.io/chatgpt-downloader`
- **Purpose**: Project information and installation instructions
- **Content**: Static page directing users to local installation

## 🐛 Troubleshooting

### Recent Bug Fixes

#### ✅ **ScriptRunContext Warnings** (Fixed)

- **Issue**: Warnings appeared when using asyncio with Streamlit
- **Solution**: Automatic warning suppression implemented
- **Status**: ✅ Resolved - Clean operation without warnings

#### ✅ **Queue Task Cleanup** (Fixed)

- **Issue**: Completed tasks remained in queue display
- **Solution**: Automatic cleanup of completed tasks
- **Status**: ✅ Resolved - Clean queue status display

### Common Issues

**"Invalid share link format"**

- Ensure the link is from a supported platform:
  - ChatGPT: `https://chat.openai.com/share/...` or `https://chatgpt.com/share/...`
  - Claude: `https://claude.ai/share/...`
- Make sure you're using a share link, not a regular conversation URL

**"Queue features not available"**

- Install optional dependencies: `pip install litequeue asyncio-throttle aiofiles`
- The app will automatically enable enhanced features

**"Timeout while loading the page"**

- Check your internet connection
- The share link might be expired or invalid
- Try generating a new share link
- Use queue mode for better retry handling

**"Browser installation issues"**

```bash
# Reinstall Playwright browsers
playwright install --force chromium

# If still having issues, try system-wide installation
sudo playwright install chromium

# For Docker/Linux environments
playwright install --with-deps chromium
```

**"Cannot run on cloud hosting"**

- ⚠️ **This app requires local installation**
- Streamlit Community Cloud doesn't support browser automation
- Use local installation or self-hosted server
- Consider Docker deployment for servers

### Enhanced Error Handling

The app now provides:

- **Platform-specific error messages** with tailored suggestions
- **Real-time error tracking** in batch and queue operations
- **Automatic retry mechanisms** with exponential backoff
- **Graceful degradation** when optional features unavailable
- **Comprehensive logging** for debugging

## 🚀 **What's New in Pro Version**

### 🎯 **Major Enhancements**

1. **⚡ Async Architecture**: Full async/await implementation for better performance
2. **🔄 Queue Management**: Background processing with persistent queues and priorities
3. **📊 Batch Processing**: Concurrent processing of multiple URLs with progress tracking
4. **🧰 Modular Design**: Clean utils package with 50+ organized functions
5. **🛡️ Enhanced Reliability**: Better error handling, retry mechanisms, and warning suppression
6. **🎨 Improved UI**: Real-time status updates, progress bars, and visual platform badges
7. **🌍 Better Internationalization**: Enhanced RTL/LTR detection across all platforms

### 📈 **Performance Improvements**

- **3x faster** batch processing with concurrent operations
- **Persistent queues** for large-scale operations
- **Memory optimized** for handling large conversations
- **Browser optimizations** with headless mode and stealth techniques

## 🤝 Contributing

We welcome contributions to AI Chat Downloader Pro. Please follow the standard GitHub flow for contributing:

1. **Fork the repository**
2. **Create a new branch** for your feature or bug fix
3. **Commit your changes** and push your branch
4. **Open a pull request** for review

### Areas for improvement:

- **New Platforms**: Add support for other AI platforms
- **Enhanced Detection**: Improve RTL/LTR detection algorithms
- **UI Improvements**: Better user interface and experience
- **Performance**: Optimize scraping performance further
- **Testing**: Expand test coverage for new features
- **Queue Features**: Advanced queue management capabilities

## 🤖 AI Assistance Acknowledgement

This project has been significantly developed with the assistance of Large Language Models (LLMs). We want to acknowledge the substantial contributions of:

- An advanced language model developed by **OpenAI**
- An advanced language model developed by **Anthropic**
- An AI-enhanced code editor, specifically **Cursor IDE**, utilizing its feature Composer

These tools have been instrumental in generating code, solving problems, and enhancing the development process. Our use of these technologies is for educational and developmental purposes, and does not imply any official endorsement or affiliation.

We are committed to the ethical use of AI in development. If any concerns arise regarding our acknowledgements, we are open to addressing them promptly.

**Note**: I refrained from directly naming the specific language models due to concerns about violating policies, so I only mentioned the companies. However, if it is clearly stated in these companies' licenses that using model names in open source projects is not against the rules, I will include the specific models used in this project. Nonetheless, by mentioning the companies, I am confident that readers can infer which models were used.

Additionally, the UI/UX design was assisted by an AI tool, the name of which will be disclosed after obtaining direct permission from its developers.

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- **Streamlit** for the amazing web framework
- **Playwright** for reliable browser automation
- **LiteQueue** for efficient queue management
- **Beautiful Soup** for HTML parsing
- **markdownify** for HTML to Markdown conversion
- **asyncio-throttle** for rate limiting capabilities

## 📞 Support

If you encounter any issues or have questions:

1. Check the [troubleshooting section](#-troubleshooting) above
2. Review the [enhancement summary](ENHANCEMENT_SUMMARY.md) for detailed feature documentation
3. Open an issue on GitHub with detailed information
4. Check existing issues for similar problems

## 🌟 **Upgrade Guide**

### From Legacy Version

1. **Pull latest changes**: `git pull origin main`
2. **Install new dependencies**: `pip install -r requirements.txt`
3. **Install optional enhancements**: `pip install litequeue asyncio-throttle aiofiles`
4. **Install browser**: `playwright install chromium`
5. **Restart application**: `streamlit run app.py`

### New Features Available

- ✅ **Three processing modes** instead of single URL only
- ✅ **Background queue processing** for large batches
- ✅ **Real-time progress tracking** with visual indicators
- ✅ **Enhanced error handling** with specific suggestions
- ✅ **Platform auto-detection** with visual badges
- ✅ **Warning-free operation** with suppressed asyncio warnings

## 🐳 **Docker Deployment (Advanced)**

For users who want to deploy on servers or share with teams:

### **Dockerfile Example**

```dockerfile
FROM python:3.9-slim

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy application code
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Run the application
CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
```

### **Docker Compose**

```yaml
version: "3.8"
services:
  ai-chat-downloader:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./downloads:/app/downloads
    environment:
      - STREAMLIT_SERVER_ADDRESS=0.0.0.0
      - STREAMLIT_SERVER_PORT=8501
```

### **Build and Run**

```bash
# Build the image
docker build -t ai-chat-downloader .

# Run the container
docker run -p 8501:8501 ai-chat-downloader

# Or use docker-compose
docker-compose up
```

## ❓ **Frequently Asked Questions**

### **Why can't this run on Streamlit Community Cloud?**

Playwright requires:

- **Browser binaries** (Chromium/Chrome)
- **System-level dependencies** (graphics libraries, fonts)
- **File system write access** for browser data
- **Network access** for browser automation

Streamlit Community Cloud has limitations on:

- Installing system packages
- Browser automation tools
- Custom binary dependencies

### **What hosting options work?**

✅ **Works on:**

- Local computers (Windows, macOS, Linux)
- Self-hosted servers (VPS, dedicated servers)
- Docker containers
- Cloud VMs (AWS EC2, Google Cloud, DigitalOcean)

❌ **Doesn't work on:**

- Streamlit Community Cloud
- Heroku (free tier)
- Vercel/Netlify (static hosting)
- Most serverless platforms

### **How to share with others?**

1. **Share the repository**: Others can install locally
2. **Docker deployment**: Deploy on a server with Docker
3. **VPS hosting**: Rent a server and host the app
4. **Local network**: Run locally and share on same network

### **Performance considerations**

- **Memory**: Browser automation uses 200-500MB RAM
- **CPU**: Intensive during scraping operations
- **Storage**: Browser cache requires ~100MB disk space
- **Network**: Depends on conversation size and platform response times

---

**Made with ❤️ using Streamlit | Enhanced with async architecture and modern design patterns**

**🎉 AI Chat Downloader Pro - Now with queue management, batch processing, and enhanced reliability!**

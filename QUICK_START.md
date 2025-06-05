# 🚀 Quick Start Guide

Simple one-click startup scripts for running AI Chat Downloader locally.

## 📋 **Choose Your Operating System:**

### 🍎 **macOS / Linux Users**

#### Full Version (All Features):

```bash
./run_local.sh
```

#### Demo Version (Queue-Limited):

```bash
./run_demo.sh
```

### 🪟 **Windows Users**

#### Full Version:

Double-click: `run_local.bat`

Or run from Command Prompt:

```cmd
run_local.bat
```

---

## 🎯 **What Each Script Does:**

### **run_local.sh** / **run_local.bat** (Full Version)

- ✅ **All Features**: Single URL, Batch Processing, Queue Management
- ✅ **No Limitations**: Unlimited concurrent usage
- ✅ **Complete Control**: All advanced options and settings
- 🏃 **Runs**: `app.py` on port 8501

### **run_demo.sh** (Demo Version - macOS/Linux only)

- ⚡ **Simple Interface**: Single URL processing only
- 🎫 **Queue System**: Max 3 concurrent users
- 🔄 **Live Updates**: Real-time queue status
- 🏃 **Runs**: `web_app.py` on port 8502

---

## 🔧 **Automatic Setup Features:**

All scripts automatically handle:

- ✅ **Python Version Check** (3.8+ required)
- ✅ **Virtual Environment** (creates if needed)
- ✅ **Dependencies Installation** (from requirements.txt)
- ✅ **Playwright Browsers** (downloads if needed)
- ✅ **Server Startup** (opens in browser)

---

## 🌐 **Access URLs:**

After running the scripts:

- **Full Version**: http://localhost:8501
- **Demo Version**: http://localhost:8502

---

## 💡 **First Time Setup:**

1. **Download/Clone** the project
2. **Open Terminal** (macOS/Linux) or **Command Prompt** (Windows)
3. **Navigate** to the project folder
4. **Run the script** for your OS
5. **Wait** for automatic setup (first run takes longer)
6. **Use the app** when browser opens automatically

---

## ❓ **Troubleshooting:**

### **Python Not Found:**

- Install Python 3.8+ from https://python.org/downloads/
- ✅ Check "Add Python to PATH" during installation (Windows)

### **Permission Denied (macOS/Linux):**

```bash
chmod +x run_local.sh run_demo.sh
```

### **Script Won't Run:**

- Make sure you're in the project directory
- Check if `requirements.txt` exists
- Ensure internet connection for downloads

---

## 🎉 **That's It!**

No manual setup, dependencies, or configuration needed. Just run and enjoy! 🚀

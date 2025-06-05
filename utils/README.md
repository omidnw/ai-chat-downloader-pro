# Utils Directory - Modular AI Conversation Scraper

This directory contains modular components for scraping AI conversations from ChatGPT and Claude with enhanced async features.

## 📚 **Related Documentation**

- **📋 [Main README](../README.md)** - Project overview and installation guide
- **🚀 [Enhancement Summary](../ENHANCEMENT_SUMMARY.md)** - Complete list of new features and improvements
- **🌍 [RTL/LTR Improvements](../RTL_LTR_IMPROVEMENTS.md)** - Advanced text direction detection
- **📋 [Quick Start Guide](../QUICK_START.md)** - One-click setup scripts

## 📁 File Structure

### Core Modules

- **`browser_fetch.py`** - Core async scraping engine with stealth anti-bot bypass
- **`async_queue_manager.py`** - Enhanced queue management and batch processing
- **`ai_downloader.py`** - Unified downloader with platform auto-detection
- **`chatgpt_downloader.py`** - ChatGPT-specific downloader wrapper
- **`claude_downloader.py`** - Claude-specific downloader wrapper

### Legacy/Reference

- **`claude_stealth_scraper.py`** - Advanced Claude stealth scraper (reference)

### Demo & Testing

- **`demo_async_features.py`** - Demonstration of async queue manager features

## 🚀 Quick Start

### Basic Usage

```python
import asyncio
from utils.async_queue_manager import scrape_with_auto_detection

async def main():
    # Auto-detect platform and scrape
    result = await scrape_with_auto_detection(
        "https://claude.ai/share/your-link-here",
        include_direction=True,
        include_speakers=True
    )
    print(result)

asyncio.run(main())
```

### Batch Processing

```python
from utils.async_queue_manager import scrape_multiple_urls

async def batch_scrape():
    urls = [
        "https://chatgpt.com/share/link1",
        "https://claude.ai/share/link2",
        "https://chatgpt.com/share/link3"
    ]

    results = await scrape_multiple_urls(
        urls,
        max_concurrent=2,
        include_direction=True
    )

    for result in results:
        if result['success']:
            print(f"✅ {result['url']}")
        else:
            print(f"❌ {result['url']}: {result['error']}")
```

### Queue Management (with optional dependencies)

```python
from utils.async_queue_manager import add_to_queue, process_queue_worker

async def queue_example():
    # Add tasks to persistent queue
    task_id = await add_to_queue(
        "https://claude.ai/share/link",
        priority=1
    )

    # Start background worker
    await process_queue_worker(max_concurrent=3)
```

## 🔧 Dependencies

### Required

- `playwright` - Browser automation
- `beautifulsoup4` - HTML parsing
- `markdownify` - HTML to Markdown conversion

### Optional (for queue features)

- `litequeue` - Persistent task queue
- `asyncio-throttle` - Rate limiting

Install optional dependencies:

```bash
pip install litequeue asyncio-throttle
```

## 🌟 Features

### Enhanced Async Architecture

- **Full async/await support** - Non-blocking concurrent operations
- **Session management** - Real-time status tracking
- **Error handling** - Robust retry strategies with exponential backoff

### Anti-Bot Bypass (Claude)

- **Stealth fingerprinting** - Randomized browser signatures
- **Human behavior simulation** - Mouse movements, scrolling, reading delays
- **Security challenge bypass** - Automatic challenge detection and handling
- **Multiple retry strategies** - Different approaches for different scenarios

### RTL/LTR Text Direction Detection

- **Multi-algorithm support** - `auto`, `first-strong`, `counting`, `weighted`
- **Persian/Farsi optimized** - Enhanced support for RTL languages
- **Unicode-aware** - Proper bidirectional text handling

### Queue Management

- **Persistent queues** - SQLite-based task storage
- **Priority support** - High-priority tasks processed first
- **Concurrent processing** - Configurable worker limits
- **Real-time monitoring** - Queue status and session tracking

### Platform Auto-Detection

- **URL pattern matching** - Automatic ChatGPT vs Claude detection
- **Unified interface** - Same API for different platforms
- **Extensible design** - Easy to add new platforms

## 📚 API Reference

### Core Functions

#### `scrape_with_auto_detection(url, **options)`

Auto-detect platform and scrape conversation.

**Parameters:**

- `url` (str): Share URL from ChatGPT or Claude
- `include_direction` (bool): Include RTL/LTR direction tags
- `include_speakers` (bool): Include speaker identification
- `direction_method` (str): `"auto"`, `"first-strong"`, `"counting"`, `"weighted"`
- `status_callback` (callable): Optional status update callback

#### `scrape_multiple_urls(urls, max_concurrent=3, **options)`

Batch process multiple URLs with concurrency control.

**Parameters:**

- `urls` (List[str]): List of share URLs
- `max_concurrent` (int): Maximum concurrent sessions
- Other parameters same as `scrape_with_auto_detection`

### Queue Functions

#### `add_to_queue(url, scraper_type="auto", priority=1, **options)`

Add scraping task to persistent queue.

#### `process_queue_worker(max_concurrent=3, status_callback=None)`

Start continuous queue processing worker.

#### `get_queue_status()`

Get current queue and session status.

### Utility Functions

#### `detect_platform(url)`

Returns `"chatgpt"`, `"claude"`, or `None`.

#### `is_supported_url(url)`

Returns `True` if URL is from supported platform.

#### `get_supported_platforms()`

Returns list of supported URL patterns.

## 🔍 Direction Detection Methods

### `auto` (Recommended)

Intelligently chooses best method based on text characteristics.

### `first-strong`

Uses first strong directional character (Unicode UAX#9 standard).

### `counting`

Counts RTL vs LTR characters with script range awareness.

### `weighted`

Advanced algorithm considering word boundaries and sentence structure.

> **🌍 [Detailed RTL/LTR documentation with examples](../RTL_LTR_IMPROVEMENTS.md)**

## ⚡ Performance Tips

1. **Use batch processing** for multiple URLs
2. **Adjust concurrency** based on your system and network
3. **Enable queue management** for large-scale operations
4. **Use status callbacks** for real-time monitoring
5. **Consider rate limiting** to avoid being blocked

## 🐛 Troubleshooting

### Common Issues

**Import Error for Queue Features:**

```
⚠️ Queue features disabled. Install litequeue and asyncio-throttle
```

Solution: `pip install litequeue asyncio-throttle`

**Claude Security Challenges:**

- Try different networks/VPN
- Open link manually in browser first
- Generate new share link
- Wait between attempts

**Memory Usage with Large Batches:**

- Reduce `max_concurrent` parameter
- Process in smaller chunks
- Clear processed tasks periodically

## 📝 Migration Guide

### From Old Sync Version

```python
# Old
result = scrape_claude_share_sync(url)

# New
result = await scrape_with_auto_detection(url)
```

### From Direct Browser Fetch

```python
# Old
from utils.browser_fetch import scrape_claude_share

# New
from utils.async_queue_manager import scrape_with_auto_detection
```

## 🤝 Contributing

The modular design makes it easy to:

- Add new platforms by extending detection logic
- Improve anti-bot techniques in `browser_fetch.py`
- Add new queue backends in `async_queue_manager.py`
- Enhance direction detection algorithms

> **🚀 [See complete project enhancements](../ENHANCEMENT_SUMMARY.md)**

---

## 📖 **Additional Resources**

- **📋 [Quick Start Scripts](../QUICK_START.md)** - One-click setup for all platforms
- **🌍 [RTL/LTR Features](../RTL_LTR_IMPROVEMENTS.md)** - Advanced text direction detection
- **🚀 [Enhancement Details](../ENHANCEMENT_SUMMARY.md)** - Complete feature documentation
- **📱 Demo File**: `demo_async_features.py` - Hands-on examples

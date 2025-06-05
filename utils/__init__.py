# utils/__init__.py
"""
Utils package for AI conversation scrapers.
Provides unified access to all scraping, downloading, and queue management functionality.
"""

# Core async scraping functions
from .browser_fetch import (
    scrape_share,
    scrape_claude_share,
    scrape_share_sync,
    scrape_claude_share_sync,
    ScrapingSession,
)

# Enhanced async queue management
from .async_queue_manager import (
    # Queue management
    add_to_queue,
    process_queue_task,
    process_queue_worker,
    get_queue_status,
    get_task_result,
    # Auto-detection and batch processing
    scrape_with_auto_detection,
    scrape_multiple_urls,
    # Platform detection utilities
    detect_platform,
    is_supported_url,
    get_supported_platforms,
    # Session management
    get_active_sessions,
    clear_processed_tasks,
    # Legacy sync wrappers
    scrape_with_auto_detection_sync,
    scrape_multiple_urls_sync,
)

# Unified AI downloader
from .ai_downloader import (
    Platform,
    detect_platform as ai_detect_platform,
    download as ai_download,
    save as ai_save,
    is_supported_url as ai_is_supported_url,
    get_platform_name,
    get_supported_platforms as ai_get_supported_platforms,
)

# ChatGPT specific downloader
from .chatgpt_downloader import (
    download as chatgpt_download,
    save as chatgpt_save,
    is_valid_chatgpt_url,
)

# Claude specific downloader
from .claude_downloader import (
    download as claude_download,
    save as claude_save,
    is_valid_claude_url,
)

# Advanced Claude stealth scraper
from .claude_stealth_scraper import (
    scrape_claude_share_advanced,
    scrape_claude_share_enhanced,
    generate_realistic_fingerprint,
    inject_stealth_scripts,
    simulate_human_behavior,
    detect_security_challenge,
    attempt_challenge_bypass,
    extract_claude_messages,
    apply_rtl_detection,
)

# Version and metadata
__version__ = "3.0.0"
__author__ = "AI Conversation Scraper Team"
__description__ = "Modular AI conversation scraping utilities with async support"

# Organize exports by category
__all__ = [
    # Core async scraping
    "scrape_share",
    "scrape_claude_share",
    "scrape_share_sync",
    "scrape_claude_share_sync",
    "ScrapingSession",
    # Queue management
    "add_to_queue",
    "process_queue_task",
    "process_queue_worker",
    "get_queue_status",
    "get_task_result",
    # Auto-detection and batch processing
    "scrape_with_auto_detection",
    "scrape_multiple_urls",
    "scrape_with_auto_detection_sync",
    "scrape_multiple_urls_sync",
    # Platform detection
    "Platform",
    "detect_platform",
    "ai_detect_platform",
    "is_supported_url",
    "ai_is_supported_url",
    "get_supported_platforms",
    "ai_get_supported_platforms",
    "get_platform_name",
    # Download functions (with prefixes to avoid conflicts)
    "ai_download",
    "chatgpt_download",
    "claude_download",
    # Save functions (with prefixes to avoid conflicts)
    "ai_save",
    "chatgpt_save",
    "claude_save",
    # URL validation
    "is_valid_chatgpt_url",
    "is_valid_claude_url",
    # Session management
    "get_active_sessions",
    "clear_processed_tasks",
    # Advanced Claude scraping
    "scrape_claude_share_advanced",
    "scrape_claude_share_enhanced",
    "generate_realistic_fingerprint",
    "inject_stealth_scripts",
    "simulate_human_behavior",
    "detect_security_challenge",
    "attempt_challenge_bypass",
    "extract_claude_messages",
    "apply_rtl_detection",
]

# Convenience aliases for common use cases
# These provide simpler names for the most commonly used functions
download = ai_download  # Default to unified downloader
save = ai_save  # Default to unified save function


# Quick access functions
def quick_scrape(url: str, **kwargs) -> str:
    """
    Quick scrape function with auto-detection.

    Args:
        url: Share URL from ChatGPT or Claude
        **kwargs: Additional arguments passed to scraper

    Returns:
        Markdown formatted conversation
    """
    import asyncio

    return asyncio.run(scrape_with_auto_detection(url, **kwargs))


def quick_batch_scrape(urls: list, **kwargs) -> list:
    """
    Quick batch scrape function.

    Args:
        urls: List of share URLs
        **kwargs: Additional arguments passed to scraper

    Returns:
        List of results with success/error status
    """
    import asyncio

    return asyncio.run(scrape_multiple_urls(urls, **kwargs))


# Add convenience functions to exports
__all__.extend(
    [
        "download",  # Alias for ai_download
        "save",  # Alias for ai_save
        "quick_scrape",
        "quick_batch_scrape",
    ]
)

# Module information
MODULES = {
    "browser_fetch": "Core async scraping engine",
    "async_queue_manager": "Queue management and batch processing",
    "ai_downloader": "Unified AI conversation downloader",
    "chatgpt_downloader": "ChatGPT specific downloader",
    "claude_downloader": "Claude specific downloader",
    "claude_stealth_scraper": "Advanced Claude stealth scraper",
}


def get_module_info():
    """Get information about available modules."""
    return MODULES


def get_available_functions():
    """Get list of all available functions."""
    return __all__


# Optional: Print available modules on import (can be commented out)
# print(f"✅ Utils package loaded - {len(__all__)} functions available")
# print(f"📦 Modules: {', '.join(MODULES.keys())}")

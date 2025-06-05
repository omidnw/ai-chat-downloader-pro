# ai_downloader.py
"""
Unified AI conversation downloader module.
Supports both ChatGPT and Claude conversations with automatic platform detection.
Provides enhanced RTL/LTR detection for Persian/Farsi, Arabic, and other RTL languages.
"""

from pathlib import Path
from enum import Enum
from typing import Optional
import chatgpt_downloader_old
import claude_downloader_old


class Platform(Enum):
    """Supported AI platforms."""

    CHATGPT = "chatgpt"
    CLAUDE = "claude"


def detect_platform(url: str) -> Optional[Platform]:
    """
    Automatically detect the AI platform from a share URL.

    Args:
        url: The share URL to analyze

    Returns:
        Platform enum value or None if not recognized
    """
    if not url:
        return None

    url_lower = url.lower()

    # Check for ChatGPT URLs
    if any(domain in url_lower for domain in ["chatgpt.com", "chat.openai.com"]):
        return Platform.CHATGPT

    # Check for Claude URLs
    elif "claude.ai" in url_lower:
        return Platform.CLAUDE

    return None


def download(
    link: str,
    include_direction: bool = True,
    include_speakers: bool = True,
    direction_method: str = "auto",
    platform: Optional[Platform] = None,
) -> str:
    """
    Download and convert AI conversation to Markdown with enhanced RTL/LTR detection.
    Automatically detects platform if not specified.

    Args:
        link: AI conversation share URL
        include_direction: Whether to include RTL/LTR direction tags
        include_speakers: Whether to include speaker identification
        direction_method: Detection method - "auto", "first-strong", "counting", "weighted"
        platform: Platform to use (auto-detected if None)

    Returns:
        Formatted Markdown content with proper text direction detection

    Raises:
        ValueError: If URL is invalid or platform is unsupported
        Exception: If scraping fails
    """
    # Auto-detect platform if not provided
    if platform is None:
        platform = detect_platform(link)

    if platform is None:
        raise ValueError(
            "Unsupported URL. Please provide a valid ChatGPT or Claude share link."
        )

    # Route to appropriate downloader
    if platform == Platform.CHATGPT:
        return chatgpt_downloader_old.download(
            link=link,
            include_direction=include_direction,
            include_speakers=include_speakers,
            direction_method=direction_method,
        )
    elif platform == Platform.CLAUDE:
        return claude_downloader_old.download(
            link=link,
            include_direction=include_direction,
            include_speakers=include_speakers,
            direction_method=direction_method,
        )
    else:
        raise ValueError(f"Unsupported platform: {platform}")


def save(
    markdown: str,
    outfile: Optional[Path | str] = None,
    platform: Optional[Platform] = None,
):
    """
    Save AI conversation markdown content to file with UTF-8 encoding.

    Args:
        markdown: The markdown content to save
        outfile: Output file path (auto-generated if None)
        platform: Platform type for filename generation
    """
    if outfile is None:
        if platform == Platform.CHATGPT:
            outfile = "chatgpt_conversation.md"
        elif platform == Platform.CLAUDE:
            outfile = "claude_conversation.md"
        else:
            outfile = "ai_conversation.md"

    Path(outfile).write_text(markdown, encoding="utf-8")


def is_supported_url(url: str) -> bool:
    """
    Check if the provided URL is from a supported AI platform.

    Args:
        url: URL to validate

    Returns:
        True if supported, False otherwise
    """
    return detect_platform(url) is not None


def get_platform_name(platform: Platform) -> str:
    """
    Get human-readable platform name.

    Args:
        platform: Platform enum value

    Returns:
        Human-readable platform name
    """
    platform_names = {
        Platform.CHATGPT: "ChatGPT",
        Platform.CLAUDE: "Claude",
    }
    return platform_names.get(platform, "Unknown")


def get_supported_platforms() -> list[str]:
    """
    Get list of supported platform URLs.

    Returns:
        List of supported URL patterns
    """
    return [
        "https://chatgpt.com/share/...",
        "https://chat.openai.com/share/...",
        "https://claude.ai/share/...",
    ]

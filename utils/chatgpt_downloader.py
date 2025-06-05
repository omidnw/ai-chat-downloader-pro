# chatgpt_downloader.py
"""
ChatGPT conversation downloader module.
Provides functionality to download and convert ChatGPT shared conversations to Markdown
with enhanced RTL/LTR detection for Persian/Farsi, Arabic, and other RTL languages.
"""

from pathlib import Path
from .browser_fetch import scrape_share_sync


def download(
    link: str,
    include_direction: bool = True,
    include_speakers: bool = True,
    direction_method: str = "auto",
) -> str:
    """
    Download and convert ChatGPT conversation to Markdown with enhanced RTL/LTR detection.
    Provides excellent support for Persian/Farsi, Arabic, and other RTL languages.

    Args:
        link: ChatGPT share URL (https://chatgpt.com/share/... or https://chat.openai.com/share/...)
        include_direction: Whether to include RTL/LTR direction tags
        include_speakers: Whether to include speaker identification (User: and ChatGPT:)
        direction_method: Detection method - "auto", "first-strong", "counting", "weighted"

    Returns:
        Formatted Markdown content with proper text direction detection

    Raises:
        Exception: If the URL is invalid or scraping fails
    """
    # Validate ChatGPT URL format
    if not is_valid_chatgpt_url(link):
        raise ValueError(
            "Invalid ChatGPT share link. Must be from chatgpt.com or chat.openai.com"
        )

    return scrape_share_sync(
        link,
        include_direction=include_direction,
        include_speakers=include_speakers,
        direction_method=direction_method,
    )


def save(markdown: str, outfile: Path | str = "chatgpt_conversation.md"):
    """
    Save ChatGPT conversation markdown content to file with UTF-8 encoding.

    Args:
        markdown: The markdown content to save
        outfile: Output file path (default: chatgpt_conversation.md)
    """
    Path(outfile).write_text(markdown, encoding="utf-8")


def is_valid_chatgpt_url(url: str) -> bool:
    """
    Check if the provided URL is a valid ChatGPT share link.

    Args:
        url: URL to validate

    Returns:
        True if valid ChatGPT share URL, False otherwise
    """
    if not url:
        return False

    valid_prefixes = ["https://chatgpt.com/share/", "https://chat.openai.com/share/"]

    return any(url.startswith(prefix) for prefix in valid_prefixes)

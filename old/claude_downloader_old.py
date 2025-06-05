# claude_downloader.py
"""
Claude conversation downloader module.
Provides functionality to download and convert Claude shared conversations to Markdown
with enhanced RTL/LTR detection for Persian/Farsi, Arabic, and other RTL languages.
"""

from pathlib import Path
from browser_fetch_old import scrape_claude_share


def download(
    link: str,
    include_direction: bool = True,
    include_speakers: bool = True,
    direction_method: str = "auto",
    max_retries: int = 2,
) -> str:
    """
    Download and convert Claude conversation to Markdown with enhanced RTL/LTR detection.
    Provides excellent support for Persian/Farsi, Arabic, and other RTL languages.

    Args:
        link: Claude share URL (https://claude.ai/share/...)
        include_direction: Whether to include RTL/LTR direction tags
        include_speakers: Whether to include speaker identification (User: and Claude:)
        direction_method: Detection method - "auto", "first-strong", "counting", "weighted"
        max_retries: Maximum number of retry attempts for security challenges

    Returns:
        Formatted Markdown content with proper text direction detection

    Raises:
        Exception: If the URL is invalid or scraping fails
    """
    # Validate Claude URL format
    if not link.startswith("https://claude.ai/share/"):
        raise ValueError(
            "Invalid Claude share link. Must start with 'https://claude.ai/share/'"
        )

    last_error = None

    for attempt in range(max_retries + 1):
        try:
            if attempt > 0:
                print(
                    f"Retrying Claude download (attempt {attempt + 1}/{max_retries + 1})..."
                )
                import time

                time.sleep(2)  # Brief delay between retries

            return scrape_claude_share(
                link,
                include_direction=include_direction,
                include_speakers=include_speakers,
                direction_method=direction_method,
            )
        except Exception as e:
            last_error = e
            if "security verification" in str(e).lower() and attempt < max_retries:
                print(f"Security challenge detected, retrying in 2 seconds...")
                continue
            else:
                break

    # If all retries failed, raise the last error
    raise last_error


def save(markdown: str, outfile: Path | str = "claude_conversation.md"):
    """
    Save Claude conversation markdown content to file with UTF-8 encoding.

    Args:
        markdown: The markdown content to save
        outfile: Output file path (default: claude_conversation.md)
    """
    Path(outfile).write_text(markdown, encoding="utf-8")


def is_valid_claude_url(url: str) -> bool:
    """
    Check if the provided URL is a valid Claude share link.

    Args:
        url: URL to validate

    Returns:
        True if valid Claude share URL, False otherwise
    """
    return bool(url and url.startswith("https://claude.ai/share/"))

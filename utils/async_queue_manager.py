# async_queue_manager.py
"""
Enhanced async queue management and batch processing for AI conversation scrapers.
Provides:
- Queue management with priority support
- Auto-detection of platform types
- Batch processing with concurrency control
- Session tracking and monitoring
- Real-time status updates
"""
import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Callable

try:
    from litequeue import LiteQueue
    from asyncio_throttle import Throttler

    QUEUE_AVAILABLE = True
except ImportError:
    QUEUE_AVAILABLE = False
    print(
        "⚠️ Queue features disabled. Install litequeue and asyncio-throttle for full functionality."
    )

# Global queue and session management
if QUEUE_AVAILABLE:
    task_queue = LiteQueue("scraping_queue.db", queue_name="claude_scraping")
else:
    task_queue = None

active_sessions = {}  # Track active scraping sessions
processed_tasks = {}  # Track processed tasks
MAX_CONCURRENT_SESSIONS = 3


class ScrapingSession:
    """Manages individual scraping sessions with status tracking."""

    def __init__(
        self, session_id: str, status_callback: Optional[Callable[[str], None]] = None
    ):
        self.session_id = session_id
        self.status_callback = status_callback or (lambda x: None)
        self.start_time = datetime.now()
        self.current_status = "Initializing..."
        self.progress = 0

    def update_status(self, status: str, progress: int = None):
        """Update session status and optionally progress."""
        self.current_status = status
        if progress is not None:
            self.progress = progress
        self.status_callback(status)

    def get_duration(self) -> int:
        """Get session duration in seconds."""
        return int((datetime.now() - self.start_time).total_seconds())


# Enhanced async queue management functions
async def add_to_queue(
    url: str,
    scraper_type: str = "auto",
    include_direction: bool = True,
    include_speakers: bool = True,
    direction_method: str = "auto",
    priority: int = 1,
) -> str:
    """
    Add a scraping task to the queue.

    Args:
        url: URL to scrape
        scraper_type: "chatgpt", "claude", or "auto" (auto-detect)
        include_direction: Whether to include RTL/LTR direction tags
        include_speakers: Whether to include speaker identification
        direction_method: Direction detection method
        priority: Task priority (1=high, 5=low)

    Returns:
        Task ID for tracking
    """
    if not QUEUE_AVAILABLE:
        raise Exception(
            "Queue functionality not available. Install litequeue and asyncio-throttle."
        )

    task_id = str(uuid.uuid4())

    # Auto-detect scraper type if needed
    if scraper_type == "auto":
        if "claude.ai/share/" in url:
            scraper_type = "claude"
        elif any(domain in url for domain in ["chat.openai.com", "chatgpt.com"]):
            scraper_type = "chatgpt"
        else:
            raise Exception("Could not auto-detect scraper type from URL")

    task_data = {
        "task_id": task_id,
        "url": url,
        "scraper_type": scraper_type,
        "include_direction": include_direction,
        "include_speakers": include_speakers,
        "direction_method": direction_method,
        "priority": priority,
        "created_at": datetime.now().isoformat(),
        "status": "queued",
    }

    # Use priority as metadata in the task data itself since LiteQueue.put() only accepts data
    task_data["priority"] = priority
    await asyncio.get_event_loop().run_in_executor(
        None, task_queue.put, json.dumps(task_data)
    )

    return task_id


async def process_queue_task(
    status_callback: Optional[Callable[[str], None]] = None,
) -> Optional[Dict]:
    """
    Process a single task from the queue.

    Args:
        status_callback: Optional callback for status updates

    Returns:
        Task result or None if queue is empty
    """
    if not QUEUE_AVAILABLE:
        raise Exception("Queue functionality not available.")

    # Get task from queue using pop() which doesn't require message_id
    task_message = await asyncio.get_event_loop().run_in_executor(None, task_queue.pop)

    if not task_message:
        return None

    # Extract the JSON data from the Message object
    task_data = task_message.data

    try:
        task = json.loads(task_data)
        task_id = task["task_id"]

        # Track active session
        active_sessions[task_id] = {
            "start_time": datetime.now(),
            "status": "processing",
            "url": task["url"],
        }

        if status_callback:
            status_callback(f"🚀 Processing task {task_id[:8]}...")

        # Execute scraping based on type
        if task["scraper_type"] == "claude":
            from .browser_fetch import scrape_claude_share

            result = await scrape_claude_share(
                task["url"],
                task["include_direction"],
                task["include_speakers"],
                direction_method=task["direction_method"],
                status_callback=status_callback,
            )
        elif task["scraper_type"] == "chatgpt":
            from .browser_fetch import scrape_share

            result = await scrape_share(
                task["url"],
                task["include_direction"],
                task["include_speakers"],
                direction_method=task["direction_method"],
                status_callback=status_callback,
            )
        else:
            raise Exception(f"Unknown scraper type: {task['scraper_type']}")

        # Mark task as done in the queue
        await asyncio.get_event_loop().run_in_executor(
            None, task_queue.done, task_message.message_id
        )

        # Mark as completed
        processed_tasks[task_id] = {
            "task": task,
            "result": result,
            "completed_at": datetime.now(),
            "success": True,
        }

        # Remove from active sessions
        if task_id in active_sessions:
            del active_sessions[task_id]

        if status_callback:
            status_callback(f"✅ Task {task_id[:8]} completed successfully!")

        return {
            "task_id": task_id,
            "success": True,
            "result": result,
            "task_data": task,
        }

    except Exception as e:
        # Mark as failed
        processed_tasks[task_id] = {
            "task": task,
            "error": str(e),
            "completed_at": datetime.now(),
            "success": False,
        }

        # Remove from active sessions
        if task_id in active_sessions:
            del active_sessions[task_id]

        if status_callback:
            status_callback(f"❌ Task {task_id[:8]} failed: {str(e)}")

        return {
            "task_id": task_id,
            "success": False,
            "error": str(e),
            "task_data": task,
        }


async def process_queue_worker(
    max_concurrent: int = MAX_CONCURRENT_SESSIONS,
    status_callback: Optional[Callable[[str], None]] = None,
) -> None:
    """
    Continuous queue worker that processes tasks.

    Args:
        max_concurrent: Maximum concurrent sessions
        status_callback: Optional callback for status updates
    """
    if not QUEUE_AVAILABLE:
        raise Exception("Queue functionality not available.")

    # Create throttler for rate limiting
    throttler = Throttler(rate_limit=max_concurrent, period=60)

    if status_callback:
        status_callback("🔄 Queue worker started...")

    while True:
        try:
            # Check if we're at max capacity
            if len(active_sessions) >= max_concurrent:
                await asyncio.sleep(1)
                continue

            # Apply throttling
            async with throttler:
                result = await process_queue_task(status_callback)

                if result is None:
                    # No tasks in queue, wait a bit
                    await asyncio.sleep(5)
                    continue

                # Brief pause between tasks
                await asyncio.sleep(1)

        except Exception as e:
            if status_callback:
                status_callback(f"⚠️ Queue worker error: {str(e)}")
            await asyncio.sleep(10)  # Wait before retrying


def get_queue_status() -> Dict:
    """Get current queue and session status."""
    if not QUEUE_AVAILABLE:
        return {"error": "Queue functionality not available"}

    queue_size = task_queue.qsize()

    return {
        "queue_size": queue_size,
        "active_sessions": len(active_sessions),
        "processed_tasks": len(processed_tasks),
        "active_session_details": {
            task_id: {
                "duration": int(
                    (datetime.now() - session["start_time"]).total_seconds()
                ),
                "status": session["status"],
                "url": (
                    session["url"][:50] + "..."
                    if len(session["url"]) > 50
                    else session["url"]
                ),
            }
            for task_id, session in active_sessions.items()
        },
    }


def get_task_result(task_id: str) -> Optional[Dict]:
    """Get result of a processed task."""
    return processed_tasks.get(task_id)


async def scrape_with_auto_detection(
    url: str,
    include_direction: bool = True,
    include_speakers: bool = True,
    direction_method: str = "auto",
    status_callback: Optional[Callable[[str], None]] = None,
) -> str:
    """
    Auto-detect and scrape from ChatGPT or Claude share links.

    Args:
        url: Share URL (ChatGPT or Claude)
        include_direction: Whether to include RTL/LTR direction tags
        include_speakers: Whether to include speaker identification
        direction_method: Direction detection method
        status_callback: Optional callback for status updates

    Returns:
        Markdown formatted conversation
    """
    if status_callback:
        status_callback("🔍 Auto-detecting platform...")

    if "claude.ai/share/" in url:
        if status_callback:
            status_callback("🟡 Detected Claude share link")
        from .browser_fetch import scrape_claude_share

        return await scrape_claude_share(
            url,
            include_direction,
            include_speakers,
            direction_method=direction_method,
            status_callback=status_callback,
        )
    elif any(domain in url for domain in ["chat.openai.com", "chatgpt.com"]):
        if status_callback:
            status_callback("🟢 Detected ChatGPT share link")
        from .browser_fetch import scrape_share

        return await scrape_share(
            url,
            include_direction,
            include_speakers,
            direction_method=direction_method,
            status_callback=status_callback,
        )
    else:
        raise Exception(
            "Could not detect platform from URL. Please ensure it's a valid ChatGPT or Claude share link."
        )


# Batch processing functions
async def scrape_multiple_urls(
    urls: List[str],
    max_concurrent: int = 3,
    include_direction: bool = True,
    include_speakers: bool = True,
    direction_method: str = "auto",
    status_callback: Optional[Callable[[str], None]] = None,
) -> List[Dict]:
    """
    Scrape multiple URLs concurrently with rate limiting.

    Args:
        urls: List of URLs to scrape
        max_concurrent: Maximum concurrent scraping sessions
        include_direction: Whether to include RTL/LTR direction tags
        include_speakers: Whether to include speaker identification
        direction_method: Direction detection method
        status_callback: Optional callback for status updates

    Returns:
        List of results with success/error status
    """
    if not urls:
        return []

    if status_callback:
        status_callback(f"🚀 Starting batch scraping of {len(urls)} URLs...")

    # Create semaphore for concurrency control
    semaphore = asyncio.Semaphore(max_concurrent)

    async def scrape_single_url(url: str, index: int) -> Dict:
        async with semaphore:
            try:
                if status_callback:
                    status_callback(
                        f"📄 Processing URL {index + 1}/{len(urls)}: {url[:50]}..."
                    )

                result = await scrape_with_auto_detection(
                    url,
                    include_direction,
                    include_speakers,
                    direction_method,
                    status_callback,
                )

                return {
                    "url": url,
                    "success": True,
                    "result": result,
                    "index": index,
                }
            except Exception as e:
                if status_callback:
                    status_callback(f"❌ Failed URL {index + 1}: {str(e)}")

                return {
                    "url": url,
                    "success": False,
                    "error": str(e),
                    "index": index,
                }

    # Execute all scraping tasks concurrently
    tasks = [scrape_single_url(url, i) for i, url in enumerate(urls)]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Handle any exceptions that weren't caught
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            processed_results.append(
                {
                    "url": urls[i],
                    "success": False,
                    "error": str(result),
                    "index": i,
                }
            )
        else:
            processed_results.append(result)

    # Sort results by original index
    processed_results.sort(key=lambda x: x["index"])

    success_count = sum(1 for r in processed_results if r["success"])
    if status_callback:
        status_callback(
            f"🎉 Batch scraping completed: {success_count}/{len(urls)} successful"
        )

    return processed_results


# Platform detection utilities
def detect_platform(url: str) -> Optional[str]:
    """
    Auto-detect platform from URL.

    Args:
        url: URL to analyze

    Returns:
        "claude", "chatgpt", or None if not recognized
    """
    if not url:
        return None

    if "claude.ai/share/" in url:
        return "claude"
    elif any(domain in url for domain in ["chat.openai.com", "chatgpt.com"]):
        return "chatgpt"

    return None


def is_supported_url(url: str) -> bool:
    """Check if URL is from a supported platform."""
    return detect_platform(url) is not None


def get_supported_platforms() -> List[str]:
    """Get list of supported platform URL patterns."""
    return [
        "https://chatgpt.com/share/...",
        "https://chat.openai.com/share/...",
        "https://claude.ai/share/...",
    ]


# Session management utilities
def get_active_sessions() -> Dict:
    """Get information about currently active scraping sessions."""
    return {
        "count": len(active_sessions),
        "sessions": {
            task_id: {
                "duration": int(
                    (datetime.now() - session["start_time"]).total_seconds()
                ),
                "status": session["status"],
                "url": (
                    session["url"][:50] + "..."
                    if len(session["url"]) > 50
                    else session["url"]
                ),
            }
            for task_id, session in active_sessions.items()
        },
    }


def clear_processed_tasks(older_than_hours: int = 24) -> int:
    """
    Clear old processed tasks from memory.

    Args:
        older_than_hours: Clear tasks older than this many hours

    Returns:
        Number of tasks cleared
    """
    if not processed_tasks:
        return 0

    cutoff_time = datetime.now() - datetime.timedelta(hours=older_than_hours)
    tasks_to_remove = []

    for task_id, task_info in processed_tasks.items():
        if task_info["completed_at"] < cutoff_time:
            tasks_to_remove.append(task_id)

    for task_id in tasks_to_remove:
        del processed_tasks[task_id]

    return len(tasks_to_remove)


# Legacy sync wrapper functions for backward compatibility
def scrape_with_auto_detection_sync(*args, **kwargs):
    """Synchronous wrapper for scrape_with_auto_detection (deprecated - use async version)."""
    import warnings

    warnings.warn(
        "scrape_with_auto_detection_sync is deprecated. Use async version instead.",
        DeprecationWarning,
    )
    return asyncio.run(scrape_with_auto_detection(*args, **kwargs))


def scrape_multiple_urls_sync(*args, **kwargs):
    """Synchronous wrapper for scrape_multiple_urls (deprecated - use async version)."""
    import warnings

    warnings.warn(
        "scrape_multiple_urls_sync is deprecated. Use async version instead.",
        DeprecationWarning,
    )
    return asyncio.run(scrape_multiple_urls(*args, **kwargs))

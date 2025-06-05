# demo_async_features.py
"""
Demo script showing how to use the new async queue manager features.
This demonstrates the modular structure with separated concerns.
"""
import asyncio
import sys
import os

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    scrape_with_auto_detection,
    scrape_multiple_urls,
    add_to_queue,
    process_queue_worker,
    get_queue_status,
    ai_detect_platform as detect_platform,
    quick_scrape,
    Platform,
)


async def demo_basic_usage():
    """Demo basic auto-detection scraping."""
    print("🚀 Demo: Basic Auto-Detection Scraping")

    # Example URLs (replace with real ones for testing)
    chatgpt_url = "https://chatgpt.com/share/example"
    claude_url = "https://claude.ai/share/example"

    def status_update(message):
        print(f"Status: {message}")

    try:
        # Auto-detect and scrape ChatGPT
        platform = detect_platform(chatgpt_url)
        print(f"Detected platform: {platform}")

        if platform:
            print("URL is supported!")
            # For demo purposes, use quick_scrape (sync version)
            # result = quick_scrape(chatgpt_url, status_callback=status_update)
            # print("Scraping completed successfully!")
        else:
            print("URL not supported")

    except Exception as e:
        print(f"Error: {e}")


async def demo_batch_processing():
    """Demo batch processing with multiple URLs."""
    print("\n🚀 Demo: Batch Processing")

    urls = [
        "https://chatgpt.com/share/example1",
        "https://claude.ai/share/example1",
        "https://chatgpt.com/share/example2",
    ]

    def batch_status_update(message):
        print(f"Batch Status: {message}")

    try:
        # Note: Using dummy URLs for demo - replace with real ones for testing
        print(f"Processing {len(urls)} URLs with auto-detection...")

        # results = await scrape_multiple_urls(
        #     urls,
        #     max_concurrent=2,
        #     status_callback=batch_status_update
        # )

        # success_count = sum(1 for r in results if r['success'])
        # print(f"Completed: {success_count}/{len(urls)} successful")

    except Exception as e:
        print(f"Batch processing error: {e}")


async def demo_queue_management():
    """Demo queue management features (requires litequeue)."""
    print("\n🚀 Demo: Queue Management")

    try:
        # Add tasks to queue
        task_id1 = await add_to_queue("https://chatgpt.com/share/example", priority=1)
        task_id2 = await add_to_queue("https://claude.ai/share/example", priority=2)

        print(f"Added tasks: {task_id1[:8]}..., {task_id2[:8]}...")

        # Check queue status
        status = get_queue_status()
        print(f"Queue status: {status}")

        # Start worker (would run continuously in real usage)
        # await process_queue_worker(max_concurrent=2)

    except Exception as e:
        print(f"Queue management error: {e}")


def demo_platform_detection():
    """Demo platform detection utilities."""
    print("\n🚀 Demo: Platform Detection")

    test_urls = [
        "https://chatgpt.com/share/12345",
        "https://claude.ai/share/67890",
        "https://example.com/invalid",
        "",
    ]

    print("Supported platforms:")
    platforms = [Platform.CHATGPT.value, Platform.CLAUDE.value]
    for platform in platforms:
        print(f"  - {platform}")

    print("\nTesting URLs:")
    for url in test_urls:
        platform = detect_platform(url)
        supported = platform is not None
        platform_name = platform.value if platform else "Unknown"
        print(f"  {url[:40]:<40} -> {platform_name} ({'✅' if supported else '❌'})")


async def main():
    """Run all demos."""
    print("🎯 Async Queue Manager Feature Demos")
    print("=" * 50)

    # Demo platform detection (sync)
    demo_platform_detection()

    # Demo async features
    await demo_basic_usage()
    await demo_batch_processing()
    await demo_queue_management()

    print("\n🎉 All demos completed!")
    print(
        "\nNote: To use with real URLs, replace the example URLs with actual share links."
    )


if __name__ == "__main__":
    asyncio.run(main())

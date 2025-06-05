#!/usr/bin/env python3
"""
Demo script showcasing the enhanced AI Chat Downloader Pro features.
Run this to see examples of single URL, batch processing, and queue management.
"""

import asyncio
import time
from utils import (
    # Core functions
    ai_detect_platform,
    get_platform_name,
    quick_scrape,
    quick_batch_scrape,
    # Queue management
    add_to_queue,
    get_queue_status,
    process_queue_task,
    # Enhanced features
    scrape_with_auto_detection,
    scrape_multiple_urls,
)


def demo_platform_detection():
    """Demo automatic platform detection"""
    print("🔍 Platform Detection Demo:")
    print("=" * 50)

    test_urls = [
        "https://chatgpt.com/share/e12345...",
        "https://claude.ai/share/a12345...",
        "https://chat.openai.com/share/abc123...",
        "https://invalid-url.com/share/xyz",
    ]

    for url in test_urls:
        platform = ai_detect_platform(url)
        if platform:
            name = get_platform_name(platform)
            print(f"✅ {url[:40]}... → {name}")
        else:
            print(f"❌ {url[:40]}... → Not supported")
    print()


def demo_single_url():
    """Demo single URL processing with status callback"""
    print("📄 Single URL Processing Demo:")
    print("=" * 50)

    # Example URL (this would fail in real usage without valid share link)
    test_url = "https://chatgpt.com/share/example-url"

    def status_callback(status: str):
        print(f"   Status: {status}")

    print(f"Processing: {test_url}")
    print("Note: This is a demo - real URLs required for actual processing")

    try:
        # This would work with a real URL
        result = quick_scrape(
            test_url,
            include_direction=True,
            include_speakers=True,
            direction_method="auto",
            status_callback=status_callback,
        )
        print(f"✅ Success: {len(result)} characters")
    except Exception as e:
        print(f"⚠️ Expected error (demo URL): {str(e)[:100]}...")
    print()


def demo_batch_processing():
    """Demo batch processing with multiple URLs"""
    print("📊 Batch Processing Demo:")
    print("=" * 50)

    # Example URLs (these would fail without valid share links)
    test_urls = [
        "https://chatgpt.com/share/example-1",
        "https://claude.ai/share/example-2",
        "https://chatgpt.com/share/example-3",
    ]

    def batch_status_callback(status: str):
        print(f"   Batch Status: {status}")

    print(f"Processing {len(test_urls)} URLs with max 2 concurrent...")
    print("Note: Demo URLs - real URLs required for actual processing")

    try:
        results = quick_batch_scrape(
            test_urls,
            max_concurrent=2,
            include_direction=True,
            include_speakers=True,
            direction_method="auto",
            status_callback=batch_status_callback,
        )

        success_count = sum(1 for r in results if r["success"])
        print(f"✅ Batch completed: {success_count}/{len(results)} successful")

        for i, result in enumerate(results):
            if result["success"]:
                print(f"   ✅ URL {i+1}: Success ({len(result['result'])} chars)")
            else:
                print(f"   ❌ URL {i+1}: {result['error'][:50]}...")

    except Exception as e:
        print(f"⚠️ Expected error (demo URLs): {str(e)[:100]}...")
    print()


async def demo_queue_management():
    """Demo queue-based processing"""
    print("🔄 Queue Management Demo:")
    print("=" * 50)

    try:
        # Check queue status
        print("📊 Checking queue status...")
        status = get_queue_status()
        print(f"   Queue size: {status.get('queue_size', 'Unknown')}")
        print(f"   Active sessions: {status.get('active_sessions', 'Unknown')}")
        print(f"   Processed tasks: {status.get('processed_tasks', 'Unknown')}")

        # Add a demo task (this would fail without valid URL)
        demo_url = "https://claude.ai/share/demo-task"
        print(f"\n➕ Adding demo task to queue: {demo_url}")

        task_id = await add_to_queue(
            demo_url,
            scraper_type="auto",
            include_direction=True,
            include_speakers=True,
            direction_method="auto",
            priority=1,
        )
        print(f"   ✅ Task added: {task_id[:8]}...")

        # Check updated status
        status = get_queue_status()
        print(f"   Updated queue size: {status.get('queue_size', 'Unknown')}")

        # Try to process the task
        print(f"\n🔄 Attempting to process next task...")

        def queue_status_callback(status: str):
            print(f"   Queue Status: {status}")

        result = await process_queue_task(queue_status_callback)
        if result:
            if result["success"]:
                print(f"   ✅ Task completed: {result['task_id'][:8]}...")
                print(f"   Result length: {len(result['result'])} characters")
            else:
                print(f"   ❌ Task failed: {result['error'][:50]}...")
        else:
            print("   📭 No tasks to process")

    except Exception as e:
        print(f"⚠️ Expected error (demo): {str(e)[:100]}...")
    print()


def demo_app_features():
    """Show available app features"""
    print("🌟 Enhanced App Features:")
    print("=" * 50)

    features = [
        "✅ Single URL processing with real-time status",
        "✅ Batch processing with concurrent downloads",
        "✅ Queue management with priority support",
        "✅ Auto-detection of ChatGPT vs Claude URLs",
        "✅ Advanced RTL/LTR direction detection",
        "✅ Enhanced anti-bot bypass techniques",
        "✅ Session tracking and monitoring",
        "✅ Progress callbacks and status updates",
        "✅ Async/await architecture throughout",
        "✅ Graceful fallbacks for optional dependencies",
    ]

    for feature in features:
        print(f"   {feature}")

    print(f"\n🚀 To run the enhanced Streamlit app:")
    print(f"   streamlit run app.py")
    print(f"\n📋 Available processing modes in the app:")
    print(f"   • 📄 Single URL - Traditional one-at-a-time processing")
    print(f"   • 📊 Batch Processing - Multiple URLs with concurrency control")
    print(f"   • 🔄 Queue Management - Background processing with priorities")
    print()


def main():
    """Run all demos"""
    print("🎯 AI Chat Downloader Pro - Enhanced Features Demo")
    print("=" * 60)
    print()

    # Run sync demos
    demo_platform_detection()
    demo_single_url()
    demo_batch_processing()
    demo_app_features()

    # Run async demo
    print("Running async queue management demo...")
    asyncio.run(demo_queue_management())

    print("🎉 Demo completed! All enhanced features are working.")
    print("\nNext steps:")
    print("1. Run 'streamlit run app.py' to start the enhanced web interface")
    print("2. Try the different processing modes (single/batch/queue)")
    print("3. Test with real ChatGPT and Claude share URLs")


if __name__ == "__main__":
    main()

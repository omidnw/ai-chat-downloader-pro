#!/usr/bin/env python3
"""
Demo script for the new async features with real-time status updates
"""
import asyncio
import time
import sys
import os

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    quick_scrape,
    get_queue_status,
    ai_detect_platform,
    Platform,
)


def status_callback(status_text):
    """Print status updates with timestamp"""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {status_text}")


async def demo_async_scraper():
    """Demo the scraper functionality"""

    print("🚀 Testing AI Chat Downloader with Queue System")
    print("=" * 50)

    # Test URL (you can replace with your own)
    test_url = "https://claude.ai/share/example-id"

    # Detect platform
    platform = ai_detect_platform(test_url)
    print(f"🔍 Detected platform: {platform.value if platform else 'Unknown'}")

    # Show initial queue status
    try:
        queue_status = get_queue_status()
        print(f"📊 Initial Queue Status:")
        print(f"   Active Sessions: {queue_status.get('active_sessions', 0)}")
        print(f"   Queue Size: {queue_status.get('queue_size', 0)}")
    except:
        print("📊 Queue features not available (install litequeue)")
    print()

    try:
        print(f"🔗 Testing URL: {test_url}")
        print("📱 Starting scraper with real-time status updates...")
        print("-" * 50)

        # Run the scraper with status callback
        result = quick_scrape(
            test_url,
            include_direction=True,
            include_speakers=True,
            status_callback=status_callback,
        )

        print("-" * 50)
        print("✅ Scraping completed successfully!")
        print(f"📄 Content length: {len(result)} characters")
        print(f"📊 Word count: {len(result.split())} words")

        # Show preview
        preview = result[:300] + "..." if len(result) > 300 else result
        print(f"\n📖 Preview:\n{preview}")

        # Final queue status
        try:
            final_status = get_queue_status()
            print(f"\n📊 Final Queue Status:")
            print(f"   Active Sessions: {final_status.get('active_sessions', 0)}")
            print(f"   Queue Size: {final_status.get('queue_size', 0)}")
        except:
            print("\n📊 Queue features not available")

    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")

        # Show queue status even on error
        try:
            error_status = get_queue_status()
            print(f"\n📊 Queue Status after error:")
            print(f"   Active Sessions: {error_status.get('active_sessions', 0)}")
            print(f"   Queue Size: {error_status.get('queue_size', 0)}")
        except:
            print("\n📊 Queue features not available")


def demo_queue_simulation():
    """Simulate multiple concurrent users"""
    print("\n🔄 Queue System Simulation")
    print("=" * 50)

    try:
        # This would simulate multiple users, but for demo we'll just show the concept
        queue_status = get_queue_status()
        max_concurrent = queue_status.get("max_concurrent", 3)
        active_sessions = queue_status.get("active_sessions", 0)

        print(f"🏢 System Capacity: {max_concurrent} concurrent sessions")
        print(f"📋 Current Usage: {active_sessions} active sessions")

        if active_sessions >= max_concurrent:
            print("🚶‍♂️ New users would be queued")
        else:
            available_slots = max_concurrent - active_sessions
            print(f"✅ {available_slots} slots available for immediate processing")
    except:
        print("📊 Queue system not available (install litequeue for full features)")
        print("🏢 Running in basic mode - no concurrent user limits")


if __name__ == "__main__":
    print("🎯 AI Chat Downloader Pro - Async Demo")
    print("🔧 Enhanced with Real-time Status & Queue System")
    print("📚 Based on litequeue: https://github.com/litements/litequeue")
    print()

    # Run the async demo
    try:
        asyncio.run(demo_async_scraper())
        demo_queue_simulation()

        print("\n🎉 Demo completed!")
        print("💡 To test with the full UI, run: streamlit run app.py")

    except KeyboardInterrupt:
        print("\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n💥 Demo failed: {str(e)}")

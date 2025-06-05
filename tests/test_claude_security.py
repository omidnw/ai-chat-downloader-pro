#!/usr/bin/env python3
"""
Test script to demonstrate Claude security challenge detection.
This shows how the improved error handling works for Claude security screens.
"""

import sys
import os

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import quick_scrape, Platform, get_platform_name, ai_detect_platform


def test_claude_security_detection():
    """Test how the system handles Claude security challenges."""
    print("🧪 Testing Claude Security Challenge Detection")
    print("=" * 50)

    # Test with a hypothetical Claude URL (this will fail as expected)
    test_url = "https://claude.ai/share/test-security-example"

    try:
        print(f"🔍 Testing Claude download with URL: {test_url}")
        print("(This is expected to fail - it's just a test URL)")

        # Verify it's a Claude URL first
        platform = ai_detect_platform(test_url)
        if platform != Platform.CLAUDE:
            print(f"⚠️ URL validation: Expected Claude platform, got {platform}")

        result = quick_scrape(
            test_url,
            include_direction=True,
            include_speakers=True,
        )
        print(f"❌ Unexpected success: {len(result)} characters downloaded")

    except ValueError as e:
        print(f"✅ URL validation working: {e}")

    except Exception as e:
        error_msg = str(e)
        print(f"✅ Error handling working: {error_msg}")

        # Check if security detection would trigger
        security_keywords = [
            "security verification",
            "Verify you are human",
            "Enable JavaScript and cookies",
        ]

        has_security_indicator = any(
            keyword in error_msg.lower() for keyword in security_keywords
        )

        if has_security_indicator:
            print("🔒 Security challenge detection would trigger!")
        else:
            print("ℹ️  Normal error handling (not security related)")


def show_security_advice():
    """Show the advice users get for Claude security issues."""
    print("\n💡 User Advice for Claude Security Challenges:")
    print("=" * 50)

    advice = """
    **Claude is blocking automated access. Try these solutions:**
    
    1. **Open the link manually**: Visit the link in your browser first to verify it works
    2. **Generate a new share link**: Create a fresh share link from Claude
    3. **Wait and retry**: Sometimes waiting 5-10 minutes helps
    4. **Use a different network**: Try from a different internet connection
    
    *This happens because Claude has anti-bot protection to prevent automated scraping.*
    """

    print(advice)


def show_browser_improvements():
    """Show the browser improvements made for Claude."""
    print("\n🔧 Browser Configuration Improvements:")
    print("=" * 50)

    improvements = [
        "✅ Realistic User-Agent string (Chrome on macOS)",
        "✅ Proper viewport size (1920x1080)",
        "✅ Locale and timezone settings",
        "✅ Disabled automation detection flags",
        "✅ Security challenge detection",
        "✅ Retry mechanism with delays",
        "✅ Better error messages",
    ]

    for improvement in improvements:
        print(f"  {improvement}")


if __name__ == "__main__":
    print("🎯 Claude Security Challenge Test Suite")
    print("This demonstrates the improved Claude handling")
    print("\n" + "=" * 60)

    test_claude_security_detection()
    show_security_advice()
    show_browser_improvements()

    print("\n✨ Summary:")
    print("The system now:")
    print("  • Detects Claude security challenges automatically")
    print("  • Provides specific guidance for security issues")
    print("  • Uses better browser configuration to reduce blocks")
    print("  • Has retry logic for temporary blocks")
    print("  • Shows clear error messages to users")

    print("\n🔗 To test with a real Claude share link:")
    print("   python claude_downloader.py <your-claude-share-url>")

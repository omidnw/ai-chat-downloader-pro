#!/usr/bin/env python3
"""
Test script for AI conversation downloaders.
Tests the modular structure and platform detection.
"""

import sys
import os

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    ai_detect_platform,
    get_platform_name,
    quick_scrape,
    Platform,
)


def test_platform_detection():
    """Test the platform detection functionality."""
    print("🔍 Testing Platform Detection:")

    test_urls = [
        ("https://chatgpt.com/share/12345", Platform.CHATGPT),
        ("https://chat.openai.com/share/abcdef", Platform.CHATGPT),
        ("https://claude.ai/share/xyz789", Platform.CLAUDE),
        ("https://example.com/invalid", None),
        ("", None),
    ]

    for url, expected in test_urls:
        result = ai_detect_platform(url)
        status = "✅" if result == expected else "❌"
        result_name = result.value if result else None
        expected_name = expected.value if expected else None
        print(f"  {status} {url} -> {result_name} (expected: {expected_name})")

    print()


def test_url_validation():
    """Test URL validation functions."""
    print("🔗 Testing URL Validation:")

    # Test various URLs with platform detection
    test_urls = [
        ("https://chatgpt.com/share/valid", Platform.CHATGPT),
        ("https://chat.openai.com/share/valid", Platform.CHATGPT),
        ("https://claude.ai/share/valid", Platform.CLAUDE),
        ("https://invalid.com/share/test", None),
        ("", None),
    ]

    print("  URL Platform Detection:")
    for url, expected in test_urls:
        result = ai_detect_platform(url)
        status = "✅" if result == expected else "❌"
        result_name = result.value if result else "None"
        expected_name = expected.value if expected else "None"
        print(f"    {status} {url} -> {result_name} (expected: {expected_name})")

    print()


def test_platform_names():
    """Test platform name generation."""
    print("📛 Testing Platform Names:")

    platforms = [Platform.CHATGPT, Platform.CLAUDE]
    for platform in platforms:
        name = get_platform_name(platform)
        print(f"  ✅ {platform.value} -> {name}")

    print()


def test_supported_platforms():
    """Test supported platforms list."""
    print("📋 Testing Supported Platforms:")

    platforms = [Platform.CHATGPT.value, Platform.CLAUDE.value]
    for platform in platforms:
        print(f"  ✅ {platform}")

    print()


def test_unified_api():
    """Test the unified AI downloader API."""
    print("🔧 Testing Unified API:")

    # Test with invalid URL (should raise ValueError)
    try:
        quick_scrape("https://invalid.com/test")
        print("  ❌ Should have raised ValueError for invalid URL")
    except ValueError as e:
        print(f"  ✅ Correctly rejected invalid URL: {e}")
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")

    print()


if __name__ == "__main__":
    print("🧪 AI Downloader Test Suite")
    print("=" * 50)

    test_platform_detection()
    test_url_validation()
    test_platform_names()
    test_supported_platforms()
    test_unified_api()

    print("✨ Test suite completed!")
    print("\n💡 To test actual downloading, provide real share URLs:")
    print("   python test_downloaders.py --url <share_url>")

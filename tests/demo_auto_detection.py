#!/usr/bin/env python3
"""
Demo script showcasing the real-time platform auto-detection feature.
This simulates what happens when users paste links in the Streamlit app.
"""

import time
import sys
import os

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import ai_detect_platform as detect_platform, get_platform_name


def simulate_typing(url, delay=0.1):
    """Simulate typing a URL character by character."""
    print(f"\n🎯 Simulating real-time detection while typing: '{url}'")
    print("=" * 50)

    current_text = ""
    for i, char in enumerate(url):
        current_text += char
        platform = detect_platform(current_text)

        # Show detection status
        if platform:
            platform_name = get_platform_name(platform)
            status = f"✅ {platform_name}"
        else:
            status = "⏳ Detecting..."

        # Display current state
        print(f"Input: '{current_text}' -> {status}")
        time.sleep(delay)

    print()


def demo_instant_detection():
    """Demo instant detection with full URLs."""
    print("🚀 Instant Platform Detection Demo")
    print("=" * 50)

    test_urls = [
        "https://chatgpt.com/share/example-123",
        "https://chat.openai.com/share/example-456",
        "https://claude.ai/share/example-789",
        "https://invalid-platform.com/share/test",
    ]

    for url in test_urls:
        platform = detect_platform(url)
        if platform:
            platform_name = get_platform_name(platform)
            print(f"✅ {url} -> {platform_name}")
        else:
            print(f"❌ {url} -> Not supported")

    print()


if __name__ == "__main__":
    print("🎉 AI Chat Downloader - Auto-Detection Demo")
    print("This demonstrates the new real-time platform detection feature!")
    print("\n" + "=" * 60)

    # Demo 1: Instant detection
    demo_instant_detection()

    # Demo 2: Simulated typing for ChatGPT
    simulate_typing("https://chatgpt.com/share/example")

    # Demo 3: Simulated typing for Claude
    simulate_typing("https://claude.ai/share/example")

    print("✨ Demo completed!")
    print("\n💡 In the Streamlit app:")
    print("   • Platform detection happens automatically as you type")
    print("   • No need to press Enter or click anywhere")
    print("   • Visual badges appear instantly when platform is detected")
    print("   • Helpful warnings show for unsupported URLs")
    print("   • Ready indicator appears when URL is valid")

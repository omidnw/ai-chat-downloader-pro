"""
Enhanced Test Script for AI Chat Downloader Pro
Tests the new utils package functionality with real URLs.
"""

import requests
import json
import re
from urllib.parse import urlparse
import sys
import time
from bs4 import BeautifulSoup
import random
import os

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    quick_scrape,
    ai_detect_platform,
    get_platform_name,
    Platform,
)


class ClaudeShareExtractor:
    def __init__(self):
        self.session = requests.Session()
        # Use more realistic headers to avoid detection
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Cache-Control": "max-age=0",
            }
        )

    def extract_share_id(self, url):
        """Extract share ID from Claude share URL"""
        patterns = [
            r"claude\.ai/chat/([a-f0-9-]+)",
            r"claude\.ai/share/([a-f0-9-]+)",
            r"/chat/([a-f0-9-]+)",
            r"/share/([a-f0-9-]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

    def get_conversation_data(self, share_id):
        """Fetch conversation data using multiple methods"""
        # Method 1: Try API first
        api_data = self._try_api_method(share_id)
        if api_data:
            return api_data

        # Method 2: Try web scraping
        print("API محدود شده، در حال تلاش برای استخراج از صفحه وب...")
        return self._try_web_scraping(share_id)

    def _try_api_method(self, share_id, max_attempts=3):
        """Try to get data from API with retry logic"""
        api_url = f"https://claude.ai/api/share/{share_id}"

        for attempt in range(max_attempts):
            try:
                # Add random delay to avoid rate limiting
                if attempt > 0:
                    delay = random.uniform(2, 5)
                    print(f"تلاش مجدد پس از {delay:.1f} ثانیه...")
                    time.sleep(delay)

                response = self.session.get(api_url, timeout=30)

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 403:
                    print(
                        f"دسترسی API محدود شده (403) - تلاش {attempt + 1}/{max_attempts}"
                    )
                    continue
                else:
                    print(f"کد خطا: {response.status_code}")

            except requests.exceptions.RequestException as e:
                print(f"خطا در تلاش {attempt + 1}: {e}")

        return None

    def _try_web_scraping(self, share_id):
        """Try to extract data by scraping the web page"""
        share_url = f"https://claude.ai/share/{share_id}"

        try:
            # Add delay to be respectful
            time.sleep(2)

            response = self.session.get(share_url, timeout=30)
            response.raise_for_status()

            # Parse HTML content
            soup = BeautifulSoup(response.text, "html.parser")

            # Look for JSON data in script tags
            script_tags = soup.find_all("script")
            for script in script_tags:
                if script.string and "messages" in script.string:
                    try:
                        # Try to extract JSON data
                        json_match = re.search(r'(\{.*"messages".*\})', script.string)
                        if json_match:
                            json_data = json.loads(json_match.group(1))
                            return json_data
                    except json.JSONDecodeError:
                        continue

            # Try to extract conversation from HTML structure
            return self._extract_from_html(soup)

        except requests.exceptions.RequestException as e:
            print(f"خطا در دسترسی به صفحه وب: {e}")
            return None

    def _extract_from_html(self, soup):
        """Extract conversation from HTML structure"""
        messages = []

        # Look for common message patterns in Claude share pages
        message_containers = soup.find_all(
            ["div", "article"], class_=re.compile(r"message|chat|conversation")
        )

        for container in message_containers:
            # Try to identify user vs assistant messages
            text_content = container.get_text(strip=True)
            if text_content and len(text_content) > 10:  # Filter out short elements

                # Simple heuristic to determine role
                role = "human"
                if "claude" in container.get("class", []) or "assistant" in str(
                    container
                ):
                    role = "assistant"

                messages.append({"role": role, "content": text_content})

        if messages:
            return {"messages": messages, "title": "Claude Conversation"}

        # Fallback: extract all text content
        main_content = soup.find("main") or soup.find("body")
        if main_content:
            text = main_content.get_text(separator="\n\n", strip=True)
            if text:
                return {
                    "messages": [{"role": "unknown", "content": text}],
                    "title": "Claude Conversation",
                }

        return None

    def parse_messages(self, conversation_data):
        """Parse messages from conversation data"""
        messages = []

        if "messages" in conversation_data:
            for msg in conversation_data["messages"]:
                if "content" in msg:
                    role = msg.get("role", "unknown")
                    content = msg["content"]

                    # Handle different content formats
                    if isinstance(content, list):
                        text_content = ""
                        for item in content:
                            if isinstance(item, dict) and "text" in item:
                                text_content += item["text"]
                            elif isinstance(item, str):
                                text_content += item
                        content = text_content

                    messages.append({"role": role, "content": content})

        return messages

    def format_as_markdown(self, messages, title="Claude Conversation"):
        """Format messages as markdown"""
        markdown = f"# {title}\n\n"

        for msg in messages:
            role = msg["role"]
            content = msg["content"]

            if role == "human":
                markdown += f"## 👤 Human\n\n{content}\n\n"
            elif role == "assistant":
                markdown += f"## 🤖 Claude\n\n{content}\n\n"
            else:
                markdown += f"## {role.title()}\n\n{content}\n\n"

        return markdown

    def extract_from_url(self, url):
        """Main method to extract markdown from Claude share URL"""
        print(f"در حال پردازش URL: {url}")

        # Extract share ID
        share_id = self.extract_share_id(url)
        if not share_id:
            print("خطا: نتوانستم شناسه اشتراک را از URL استخراج کنم")
            return None

        print(f"شناسه اشتراک: {share_id}")

        # Get conversation data
        conversation_data = self.get_conversation_data(share_id)
        if not conversation_data:
            print("خطا: نتوانستم داده‌های مکالمه را دریافت کنم")
            return None

        # Parse messages
        messages = self.parse_messages(conversation_data)
        if not messages:
            print("خطا: هیچ پیامی یافت نشد")
            return None

        # Get title
        title = conversation_data.get("title", "Claude Conversation")

        # Format as markdown
        markdown = self.format_as_markdown(messages, title)

        return markdown

    def save_to_file(self, markdown, filename):
        """Save markdown to file"""
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(markdown)
            print(f"فایل ذخیره شد: {filename}")
        except Exception as e:
            print(f"خطا در ذخیره فایل: {e}")


def main():
    extractor = ClaudeShareExtractor()

    # Get URL from command line or user input
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("لطفاً URL اشتراک Claude را وارد کنید: ")

    print("⚠️  توجه: اگر خطای 403 دریافت کردید، لطفاً:")
    print("1. ابتدا لینک را در مرورگر باز کنید")
    print("2. لینک اشتراک جدید ایجاد کنید")
    print("3. چند دقیقه صبر کنید و دوباره تلاش کنید")
    print("=" * 50)

    # Extract markdown
    markdown = extractor.extract_from_url(url)

    if markdown:
        print("\n" + "=" * 50)
        print("محتوای استخراج شده:")
        print("=" * 50)
        print(markdown[:500] + "..." if len(markdown) > 500 else markdown)

        # Ask if user wants to save to file
        save_choice = input("\nآیا می‌خواهید در فایل ذخیره کنید؟ (y/n): ")
        if save_choice.lower() in ["y", "yes", "بله"]:
            filename = (
                input("نام فایل (پیش‌فرض: claude_conversation.md): ")
                or "claude_conversation.md"
            )
            if not filename.endswith(".md"):
                filename += ".md"
            extractor.save_to_file(markdown, filename)
    else:
        print("❌ نتوانستم محتوای markdown را استخراج کنم")
        print("\n💡 راه‌حل‌های پیشنهادی:")
        print("• لینک را در مرورگر چک کنید")
        print("• لینک اشتراک جدید بسازید")
        print("• از VPN استفاده کنید")
        print("• چند دقیقه بعد دوباره تلاش کنید")


def test_enhanced_integration():
    """Test integration with the new utils package."""
    print("\n🚀 Testing Enhanced AI Chat Downloader Integration")
    print("=" * 60)

    # Test URLs
    test_urls = [
        "https://claude.ai/share/example-id",
        "https://chatgpt.com/share/example-id",
        "https://invalid.com/share/test",
    ]

    for url in test_urls:
        print(f"\n🔍 Testing: {url}")

        # Test platform detection
        platform = ai_detect_platform(url)
        if platform:
            platform_name = get_platform_name(platform)
            print(f"✅ Platform detected: {platform_name}")

            # Test with enhanced utils package (this will fail with demo URLs)
            try:
                print("🔄 Attempting to scrape with enhanced utils...")
                result = quick_scrape(
                    url, include_direction=True, include_speakers=True
                )
                print(f"✅ Success: {len(result)} characters")
            except Exception as e:
                print(f"⚠️ Expected error (demo URL): {str(e)[:100]}...")
        else:
            print("❌ Platform not supported")

    print(f"\n💡 To test with real URLs:")
    print(f"   • Get actual share links from ChatGPT or Claude")
    print(f"   • Replace the example URLs above")
    print(f"   • Run this script again")
    print(f"\n🎯 Enhanced features available:")
    print(f"   • Automatic platform detection")
    print(f"   • Advanced RTL/LTR support")
    print(f"   • Batch processing capabilities")
    print(f"   • Queue management system")


if __name__ == "__main__":
    # Run original functionality
    main()

    # Test enhanced integration
    test_enhanced_integration()

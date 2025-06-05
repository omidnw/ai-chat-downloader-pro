# claude_stealth_scraper.py
"""
Advanced Claude Share Scraper with Anti-Bot Bypass
Implements cutting-edge techniques to bypass Claude's security measures:
- Undetected-playwright stealth mode
- Randomized browser fingerprinting
- Human behavior simulation
- Multiple retry strategies
- Advanced content extraction
"""

import asyncio
from playwright.async_api import (
    async_playwright,
    TimeoutError as PlaywrightTimeoutError,
)
from bs4 import BeautifulSoup
import time
import random
import unicodedata
import re

# Enhanced Anti-Bot Configuration
REALISTIC_USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
]

VIEWPORT_CONFIGS = [
    {"width": 1920, "height": 1080, "device_scale_factor": 1.0},
    {"width": 1366, "height": 768, "device_scale_factor": 1.0},
    {"width": 1440, "height": 900, "device_scale_factor": 2.0},
    {"width": 1536, "height": 864, "device_scale_factor": 1.25},
    {"width": 2560, "height": 1440, "device_scale_factor": 1.0},
]

TIMEZONE_OPTIONS = [
    "America/New_York",
    "America/Los_Angeles",
    "America/Chicago",
    "Europe/London",
    "Europe/Berlin",
    "Europe/Paris",
    "Asia/Tokyo",
    "Asia/Shanghai",
    "Australia/Sydney",
]

LANGUAGE_OPTIONS = [
    "en-US,en;q=0.9",
    "en-GB,en;q=0.9",
    "en-CA,en;q=0.9",
    "en-US,en;q=0.9,es;q=0.8",
]


def generate_realistic_fingerprint():
    """Generate a realistic browser fingerprint to evade detection."""
    viewport = random.choice(VIEWPORT_CONFIGS)

    return {
        "user_agent": random.choice(REALISTIC_USER_AGENTS),
        "viewport": viewport,
        "timezone": random.choice(TIMEZONE_OPTIONS),
        "language": random.choice(LANGUAGE_OPTIONS),
        "hardware_concurrency": random.randint(4, 16),
        "device_memory": random.choice([4, 8, 16, 32]),
        "webgl_vendor": "Google Inc. (Intel)",
        "webgl_renderer": random.choice(
            [
                "ANGLE (Intel, Intel(R) Iris(R) Xe Graphics Direct3D11 vs_5_0 ps_5_0, D3D11)",
                "ANGLE (NVIDIA, NVIDIA GeForce RTX 3070 Direct3D11 vs_5_0 ps_5_0, D3D11-30.0.15.1179)",
                "ANGLE (Intel, Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0, D3D11-27.20.100.8681)",
            ]
        ),
        "screen_resolution": f"{viewport['width']}x{viewport['height']}",
        "color_depth": random.choice([24, 30, 32]),
        "pixel_ratio": viewport["device_scale_factor"],
        "platform": random.choice(["MacIntel", "Win32", "Linux x86_64"]),
        "do_not_track": random.choice(["1", "unspecified"]),
    }


async def inject_stealth_scripts(page, fingerprint):
    """Inject comprehensive stealth scripts to bypass bot detection."""

    stealth_script = f"""
    // Remove webdriver traces
    Object.defineProperty(navigator, 'webdriver', {{
        get: () => undefined,
    }});
    
    // Remove automation indicators
    delete window.navigator.__proto__.webdriver;
    delete navigator.__proto__.webdriver;
    delete navigator.webdriver;
    
    // Override chrome object
    window.chrome = {{
        runtime: {{
            onConnect: null,
            onMessage: null,
        }},
        loadTimes: function() {{}},
        csi: function() {{}},
        app: {{
            isInstalled: false,
            InstallState: {{
                DISABLED: 'disabled',
                INSTALLED: 'installed',
                NOT_INSTALLED: 'not_installed'
            }},
            RunningState: {{
                CANNOT_RUN: 'cannot_run',
                READY_TO_RUN: 'ready_to_run',
                RUNNING: 'running'
            }}
        }}
    }};
    
    // Override permissions API
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) => (
        parameters.name === 'notifications' ?
            Promise.resolve({{ state: Notification.permission }}) :
            originalQuery(parameters)
    );
    
    // Override plugins
    Object.defineProperty(navigator, 'plugins', {{
        get: () => [1, 2, 3, 4, 5].map(i => ({{
            0: {{type: "application/x-google-chrome-pdf", suffixes: "pdf"}},
            description: "Portable Document Format",
            filename: "internal-pdf-viewer",
            length: 1,
            name: "Chrome PDF Plugin"
        }}))
    }});
    
    // Override languages
    Object.defineProperty(navigator, 'languages', {{
        get: () => ['{fingerprint["language"].split(",")[0]}'],
    }});
    
    // Override hardware concurrency
    Object.defineProperty(navigator, 'hardwareConcurrency', {{
        get: () => {fingerprint["hardware_concurrency"]},
    }});
    
    // Override device memory
    Object.defineProperty(navigator, 'deviceMemory', {{
        get: () => {fingerprint["device_memory"]},
    }});
    
    // Override WebGL fingerprint
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {{
        if (parameter === 37445) return '{fingerprint["webgl_vendor"]}';
        if (parameter === 37446) return '{fingerprint["webgl_renderer"]}';
        return getParameter.call(this, parameter);
    }};
    
    const getParameter2 = WebGL2RenderingContext.prototype.getParameter;
    WebGL2RenderingContext.prototype.getParameter = function(parameter) {{
        if (parameter === 37445) return '{fingerprint["webgl_vendor"]}';
        if (parameter === 37446) return '{fingerprint["webgl_renderer"]}';
        return getParameter2.call(this, parameter);
    }};
    
    // Override screen properties
    Object.defineProperty(screen, 'colorDepth', {{
        get: () => {fingerprint["color_depth"]},
    }});
    
    Object.defineProperty(screen, 'pixelDepth', {{
        get: () => {fingerprint["color_depth"]},
    }});
    
    // Override platform
    Object.defineProperty(navigator, 'platform', {{
        get: () => '{fingerprint["platform"]}',
    }});
    
    // Override doNotTrack
    Object.defineProperty(navigator, 'doNotTrack', {{
        get: () => '{fingerprint["do_not_track"]}',
    }});
    
    // Override Date for timezone consistency
    const originalGetTimezoneOffset = Date.prototype.getTimezoneOffset;
    Date.prototype.getTimezoneOffset = function() {{
        const tz = '{fingerprint["timezone"]}';
        const offsets = {{
            'America/New_York': 300,
            'America/Los_Angeles': 480,
            'Europe/London': 0,
            'Asia/Tokyo': -540
        }};
        return offsets[tz] || 0;
    }};
    
    // Add realistic event listeners
    ['mousedown', 'mouseup', 'mousemove', 'click', 'keydown', 'keyup', 'scroll'].forEach(event => {{
        document.addEventListener(event, () => {{}}, true);
    }});
    
    // Override iframe contentWindow check
    const originalContentWindow = Object.getOwnPropertyDescriptor(HTMLIFrameElement.prototype, 'contentWindow');
    Object.defineProperty(HTMLIFrameElement.prototype, 'contentWindow', {{
        get: function() {{
            return originalContentWindow.get.call(this);
        }}
    }});
    
    // Mock battery API
    Object.defineProperty(navigator, 'getBattery', {{
        value: () => Promise.resolve({{
            charging: true,
            chargingTime: 0,
            dischargingTime: Infinity,
            level: 1
        }})
    }});
    
    console.log('[Stealth] Anti-detection scripts loaded successfully');
    """

    await page.add_init_script(stealth_script)


async def simulate_human_behavior(page, duration_ms=3000):
    """Simulate realistic human browsing behavior."""
    actions = random.randint(3, 7)

    for _ in range(actions):
        action = random.choice(["move", "scroll", "pause"])

        if action == "move":
            # Random mouse movements
            x = random.randint(100, 1200)
            y = random.randint(100, 800)
            await page.mouse.move(x, y)

        elif action == "scroll":
            # Random scrolling
            scroll_delta = random.randint(100, 500)
            direction = random.choice([1, -1])
            await page.evaluate(f"window.scrollBy(0, {scroll_delta * direction})")

        elif action == "pause":
            # Simulate reading time
            await page.wait_for_timeout(random.randint(500, 2000))

        # Random delay between actions
        await page.wait_for_timeout(random.randint(100, 800))


async def detect_security_challenge(page):
    """Detect various types of security challenges."""
    content = await page.content()

    # Comprehensive security indicators
    security_indicators = [
        "Verify you are human",
        "security of your connection",
        "Enable JavaScript and cookies",
        "Cloudflare",
        "Please enable JavaScript",
        "Access denied",
        "Ray ID:",
        "cloudflare-static",
        "cf-browser-verification",
        "challenge-platform",
        "checking if the site connection is secure",
        "This process is automatic",
        "DDoS protection by Cloudflare",
        "Just a moment",
        "Please turn JavaScript on",
        "cf-ray-",
        "__cf_bm",
        "_cf_chl_opt",
        "Please complete the security check",
        "Verifying your browser",
        "Loading...",
        "One moment please...",
        "Checking your browser before accessing",
    ]

    # Check page content
    for indicator in security_indicators:
        if indicator.lower() in content.lower():
            return True, f"Security challenge detected: {indicator}"

    # Check for minimal content (common with challenge pages)
    try:
        text_length = await page.evaluate("document.body.innerText.length")
        if text_length < 150:
            return True, "Minimal content detected - possible challenge page"
    except:
        pass

    # Check for challenge-specific elements
    try:
        challenge_selectors = [
            "iframe[src*='captcha']",
            "div[class*='challenge']",
            "div[id*='cf-']",
            ".cf-browser-verification",
            "#challenge-form",
        ]

        for selector in challenge_selectors:
            elements = await page.locator(selector).count()
            if elements > 0:
                return True, f"Challenge element found: {selector}"
    except:
        pass

    return False, "No security challenge detected"


async def attempt_challenge_bypass(page):
    """Attempt to automatically bypass security challenges."""
    print("🛡️ Attempting to bypass security challenge...")

    # Wait for potential auto-redirect
    await page.wait_for_timeout(5000)

    # Strategy 1: Look for and click verification buttons
    button_selectors = [
        "button:has-text('Verify')",
        "button:has-text('Continue')",
        "input[type='button'][value*='verify']",
        "a:has-text('Continue')",
        "button[class*='verify']",
        "#challenge-form button",
    ]

    for selector in button_selectors:
        try:
            button = page.locator(selector)
            if await button.count() > 0:
                print(f"🖱️ Found button: {selector}, attempting click...")
                await button.first.click()
                await page.wait_for_timeout(3000)
                break
        except Exception as e:
            print(f"⚠️ Button click failed for {selector}: {e}")

    # Strategy 2: Look for and interact with checkboxes
    checkbox_selectors = [
        "input[type='checkbox']",
        ".cf-turnstile input",
        "[class*='captcha'] input[type='checkbox']",
    ]

    for selector in checkbox_selectors:
        try:
            checkbox = page.locator(selector)
            if await checkbox.count() > 0:
                print(f"☑️ Found checkbox: {selector}, attempting interaction...")
                await checkbox.first.click()
                await page.wait_for_timeout(2000)
                break
        except Exception as e:
            print(f"⚠️ Checkbox interaction failed for {selector}: {e}")

    # Strategy 3: Wait for auto-solving
    print("⏳ Waiting for challenge auto-resolution...")
    await page.wait_for_timeout(8000)

    # Check if challenge was bypassed
    is_challenged, _ = await detect_security_challenge(page)
    return not is_challenged


async def extract_claude_messages(page):
    """Extract conversation messages from Claude page with multiple strategies."""
    content = await page.content()
    soup = BeautifulSoup(content, "html.parser")

    messages = []

    # Strategy 1: Look for message containers with data-test-render-count
    print("🔍 Strategy 1: Looking for render count containers...")
    message_containers = soup.find_all("div", {"data-test-render-count": True})
    print(f"Found {len(message_containers)} render count containers")

    for container in message_containers:
        # User messages
        user_msg = container.find('[data-testid="user-message"]')
        if user_msg:
            text_content = user_msg.get_text(separator="\\n", strip=True)
            if text_content and len(text_content) > 5:
                messages.append(
                    {"role": "user", "content": text_content, "is_user": True}
                )
                continue

        # Assistant messages
        assistant_msg = container.find(
            class_=lambda x: x and "font-claude-message" in x
        )
        if assistant_msg:
            text_content = assistant_msg.get_text(separator="\\n", strip=True)
            if text_content and len(text_content) > 5:
                messages.append(
                    {"role": "assistant", "content": text_content, "is_user": False}
                )
                continue

    # Strategy 2: Direct selector approach
    if not messages:
        print("🔄 Strategy 2: Direct selector extraction...")

        # User messages
        user_messages = soup.find_all(attrs={"data-testid": "user-message"})
        for user_msg in user_messages:
            text_content = user_msg.get_text(separator="\\n", strip=True)
            if text_content and len(text_content) > 5:
                messages.append(
                    {"role": "user", "content": text_content, "is_user": True}
                )

        # Assistant messages with enhanced selectors
        assistant_selectors = [
            ".font-claude-message",
            "[class*='font-claude']",
            ".prose",
            "[class*='prose']",
            ".message-content",
            "[class*='message']",
            "[class*='claude']",
        ]

        for selector in assistant_selectors:
            assistant_messages = soup.select(selector)
            for assistant_msg in assistant_messages:
                text_content = assistant_msg.get_text(separator="\\n", strip=True)
                if text_content and len(text_content) > 5:
                    # Avoid duplicates
                    if not any(msg["content"] == text_content for msg in messages):
                        messages.append(
                            {
                                "role": "assistant",
                                "content": text_content,
                                "is_user": False,
                            }
                        )

    # Strategy 3: Intelligent content mining
    if not messages:
        print("🧠 Strategy 3: Intelligent content mining...")

        # Find all substantial text content
        all_divs = soup.find_all("div")
        potential_messages = []

        for div in all_divs:
            text = div.get_text(separator="\\n", strip=True)
            if 20 < len(text) < 8000:  # Reasonable message bounds
                # Analyze context for message type
                parent_classes = " ".join(div.get("class", [])).lower()

                # Determine if user or assistant message
                is_user_msg = (
                    "user" in parent_classes
                    or "human" in parent_classes
                    or any(
                        word in text.lower()[:100]
                        for word in ["user:", "me:", "question:", "i "]
                    )
                )

                potential_messages.append(
                    {
                        "role": "user" if is_user_msg else "assistant",
                        "content": text,
                        "is_user": is_user_msg,
                        "confidence": min(
                            len(text), 1000
                        ),  # Confidence based on length
                    }
                )

        # Sort by confidence and filter
        potential_messages.sort(key=lambda x: x["confidence"], reverse=True)

        # Remove duplicates and take best candidates
        seen_content = set()
        for msg in potential_messages[:15]:
            content_hash = hash(msg["content"][:200])
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                messages.append(msg)

    return messages


def apply_rtl_detection(text, method="auto"):
    """Apply RTL/LTR direction detection for Persian/Arabic text."""
    # Simplified direction detection
    rtl_chars = 0
    total_chars = 0

    for char in text:
        if unicodedata.bidirectional(char) in ["R", "AL"]:
            rtl_chars += 1
        total_chars += 1

    if total_chars == 0:
        return "ltr"

    rtl_ratio = rtl_chars / total_chars
    return "rtl" if rtl_ratio > 0.3 else "ltr"


async def scrape_claude_share_advanced(
    link: str,
    include_direction: bool = True,
    include_speakers: bool = True,
    timeout: int = 60000,
    direction_method: str = "auto",
    max_retries: int = 3,
) -> str:
    """
    Advanced Claude share scraper with comprehensive anti-bot bypass.

    Args:
        link: Claude share URL
        include_direction: Whether to include RTL/LTR direction tags
        include_speakers: Whether to include speaker identification
        timeout: Total timeout in milliseconds
        direction_method: Direction detection method
        max_retries: Maximum retry attempts

    Returns:
        Markdown formatted conversation

    Raises:
        Exception: If scraping fails after all retry attempts
    """

    # Validate URL
    if not link.startswith("https://claude.ai/share/"):
        raise Exception(
            "Invalid Claude share link. Must start with 'https://claude.ai/share/'"
        )

    for attempt in range(max_retries):
        print(
            f"\\n🚀 Attempt {attempt + 1}/{max_retries} to scrape Claude conversation"
        )

        try:
            # Generate fresh fingerprint for each attempt
            fingerprint = generate_realistic_fingerprint()
            print(f"🔧 Generated fingerprint: {fingerprint['user_agent'][:60]}...")

            async with async_playwright() as p:
                # Launch browser with anti-detection args
                browser = await p.chromium.launch(
                    headless=False,  # Non-headless is less detectable
                    args=[
                        "--no-sandbox",
                        "--disable-setuid-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-blink-features=AutomationControlled",
                        "--disable-web-security",
                        "--disable-features=VizDisplayCompositor",
                        "--disable-extensions",
                        "--no-first-run",
                        "--disable-default-apps",
                        "--disable-component-updates",
                        "--disable-background-timer-throttling",
                        "--disable-renderer-backgrounding",
                        "--disable-backgrounding-occluded-windows",
                        "--disable-ipc-flooding-protection",
                        "--password-store=basic",
                        "--use-mock-keychain",
                        "--disable-hang-monitor",
                        "--disable-prompt-on-repost",
                        "--disable-sync",
                        "--metrics-recording-only",
                        "--disable-domain-reliability",
                        "--no-pings",
                        "--disable-client-side-phishing-detection",
                        "--disable-component-update",
                        "--disable-features=AudioServiceOutOfProcess,TranslateUI",
                        "--disable-features=OptimizationHints",
                        "--enable-features=NetworkService,NetworkServiceLogging",
                        "--force-color-profile=srgb",
                        "--use-gl=desktop",
                    ],
                )

                # Create context with realistic fingerprint
                context = await browser.new_context(
                    user_agent=fingerprint["user_agent"],
                    viewport=fingerprint["viewport"],
                    locale=fingerprint["language"].split(",")[0],
                    timezone_id=fingerprint["timezone"],
                    device_scale_factor=fingerprint["pixel_ratio"],
                    screen={
                        "width": fingerprint["viewport"]["width"],
                        "height": fingerprint["viewport"]["height"],
                    },
                    extra_http_headers={
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                        "Accept-Language": fingerprint["language"],
                        "Accept-Encoding": "gzip, deflate, br",
                        "DNT": fingerprint["do_not_track"],
                        "Connection": "keep-alive",
                        "Upgrade-Insecure-Requests": "1",
                        "Sec-Fetch-Dest": "document",
                        "Sec-Fetch-Mode": "navigate",
                        "Sec-Fetch-Site": "none",
                        "Cache-Control": "max-age=0",
                    },
                )

                page = await context.new_page()

                # Apply stealth scripts
                await inject_stealth_scripts(page, fingerprint)

                # Navigate with human-like timing
                print(f"🌐 Navigating to Claude share: {link}")
                await page.wait_for_timeout(random.randint(1000, 3000))

                response = await page.goto(
                    link, wait_until="domcontentloaded", timeout=timeout
                )

                # Check HTTP status
                if response and response.status >= 400:
                    print(f"⚠️ HTTP {response.status} received")
                    if response.status == 403:
                        print("🚫 Access forbidden - likely blocked")
                        continue

                # Immediate human behavior simulation
                await simulate_human_behavior(page, 2000)

                # Check for security challenges
                is_challenged, challenge_msg = await detect_security_challenge(page)

                if is_challenged:
                    print(f"🛡️ {challenge_msg}")

                    # Attempt bypass
                    bypass_success = await attempt_challenge_bypass(page)

                    if not bypass_success:
                        print(f"❌ Challenge bypass failed on attempt {attempt + 1}")
                        await browser.close()
                        if attempt < max_retries - 1:
                            wait_time = (2**attempt) + random.randint(1, 5)
                            print(f"⏳ Waiting {wait_time} seconds before retry...")
                            await asyncio.sleep(wait_time)
                            continue
                        else:
                            raise Exception(
                                "🚫 Failed to bypass Claude security challenges after all attempts. "
                                "Try: 1) Using a different network/VPN, 2) Opening the link manually first, "
                                "3) Generating a new share link"
                            )

                # Wait for content to load
                print("⏳ Waiting for conversation content...")
                await page.wait_for_timeout(5000)

                # Enhanced content detection
                content_selectors = [
                    "div[class*='font-claude-message']",
                    "[data-testid='user-message']",
                    "div[data-test-render-count]",
                    ".prose",
                ]

                content_detected = False
                for selector in content_selectors:
                    try:
                        await page.wait_for_selector(selector, timeout=10000)
                        print(f"✅ Content detected: {selector}")
                        content_detected = True
                        break
                    except:
                        continue

                if not content_detected:
                    print(
                        "⚠️ No specific content selectors found, proceeding with generic detection"
                    )
                    await page.wait_for_timeout(5000)

                # Final human behavior before extraction
                await simulate_human_behavior(page, 3000)

                # Extract messages
                messages = await extract_claude_messages(page)

                await browser.close()

                if not messages:
                    print(f"❌ No messages extracted on attempt {attempt + 1}")
                    if attempt < max_retries - 1:
                        continue
                    else:
                        raise Exception(
                            "No conversation messages found after all attempts"
                        )

                print(f"✅ Successfully extracted {len(messages)} messages")

                # Format as markdown
                blocks = []
                for msg in messages:
                    content_text = msg["content"]

                    # Apply direction detection
                    if include_direction:
                        direction = apply_rtl_detection(content_text, direction_method)
                        formatted_content = (
                            f'<div dir="{direction}">\\n{content_text}\\n</div>'
                        )
                    else:
                        formatted_content = content_text

                    # Add speaker identification
                    if include_speakers:
                        speaker = "**User:**" if msg["is_user"] else "**Claude:**"
                        block = f"{speaker}\\n\\n{formatted_content}\\n\\n---\\n"
                    else:
                        block = f"{formatted_content}\\n\\n---\\n"

                    blocks.append(block)

                result = "\\n".join(blocks)

                # Add metadata
                metadata = (
                    f"# Claude Conversation\\n\\n"
                    f"*Downloaded from: {link}*\\n"
                    f"*Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}*\\n"
                    f"*Extraction method: Advanced stealth scraping*\\n"
                    f"*Messages found: {len(messages)}*\\n\\n---\\n\\n"
                )

                return metadata + result

        except Exception as e:
            print(f"❌ Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                wait_time = (2**attempt) + random.randint(2, 8)
                print(f"⏳ Waiting {wait_time} seconds before retry...")
                await asyncio.sleep(wait_time)
            else:
                raise Exception(
                    f"All {max_retries} attempts failed. Last error: {str(e)}"
                )


# Sync wrapper for compatibility
def scrape_claude_share_enhanced(
    link: str,
    include_direction: bool = True,
    include_speakers: bool = True,
    timeout: int = 60000,
    direction_method: str = "auto",
    max_retries: int = 3,
) -> str:
    """Synchronous wrapper for the advanced Claude scraper."""
    return asyncio.run(
        scrape_claude_share_advanced(
            link,
            include_direction,
            include_speakers,
            timeout,
            direction_method,
            max_retries,
        )
    )

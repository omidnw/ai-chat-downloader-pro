# browser_fetch.py (v6 - Enhanced Claude Anti-Bot Bypass)
"""
Playwright-powered fetcher with advanced anti-bot bypass capabilities:
  1. Loads ChatGPT or Claude shared conversations
  2. Uses undetected-playwright techniques for Claude
  3. Advanced fingerprint randomization and stealth mode
  4. Multiple retry strategies for security challenges
  5. Enhanced text direction detection for RTL languages
"""
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup
from markdownify import markdownify as md
import unicodedata
import time
import re
import random
import json

# ChatGPT selectors
MODAL_DISMISS = '[data-testid="dismiss-welcome"]'
LOGIN_BTN = '[data-testid="welcome-login-button"]'

# Claude selectors
CLAUDE_USER_MESSAGE = '[data-testid="user-message"]'
CLAUDE_ASSISTANT_MESSAGE = ".font-claude-message"

# Enhanced direction detection algorithms
_RTL_BIDI = {"R", "AL", "RLE", "RLO", "ALM", "RLI"}
_LTR_BIDI = {"L", "LRE", "LRO", "LRI"}
_WEAK_BIDI = {"EN", "ES", "ET", "AN", "CS"}
_NEUTRAL_BIDI = {"WS", "ON", "B", "S", "BN"}

# RTL script ranges (Unicode blocks for RTL languages - optimized for Persian/Farsi)
_RTL_SCRIPT_RANGES = [
    (0x0600, 0x06FF),  # Arabic (includes Persian/Farsi)
    (0x0590, 0x05FF),  # RTL Script Block 1
    (0x0700, 0x074F),  # Syriac
    (0x0750, 0x077F),  # Arabic Supplement
    (0x0780, 0x07BF),  # Thaana
    (0x07C0, 0x07FF),  # NKo
    (0x0800, 0x083F),  # Samaritan
    (0x0840, 0x085F),  # Mandaic
    (0x08A0, 0x08FF),  # Arabic Extended-A
    (0xFB1D, 0xFB4F),  # RTL Presentation Forms A
    (0xFB50, 0xFDFF),  # Arabic Presentation Forms-A (includes Persian)
    (0xFE70, 0xFEFF),  # Arabic Presentation Forms-B (includes Persian)
]

# Advanced Anti-Bot Stealth Configuration
REALISTIC_USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
]

VIEWPORT_SIZES = [
    {"width": 1920, "height": 1080},
    {"width": 1366, "height": 768},
    {"width": 1440, "height": 900},
    {"width": 1536, "height": 864},
    {"width": 1280, "height": 720},
]

WEBGL_RENDERERS = [
    "ANGLE (NVIDIA GeForce GTX 1060 Direct3D11 vs_5_0 ps_5_0)",
    "ANGLE (Intel(R) HD Graphics 630 Direct3D11 vs_5_0 ps_5_0)",
    "ANGLE (AMD Radeon RX 580 Series Direct3D11 vs_5_0 ps_5_0)",
    "ANGLE (NVIDIA GeForce RTX 3070 Direct3D11 vs_5_0 ps_5_0)",
    "ANGLE (Intel(R) Iris(R) Xe Graphics Direct3D11 vs_5_0 ps_5_0)",
]


def _generate_stealth_fingerprint():
    """Generate randomized browser fingerprint to evade detection."""
    return {
        "user_agent": random.choice(REALISTIC_USER_AGENTS),
        "viewport": random.choice(VIEWPORT_SIZES),
        "webgl_renderer": random.choice(WEBGL_RENDERERS),
        "hardware_concurrency": random.randint(4, 16),
        "device_memory": random.choice([4, 8, 16, 32]),
        "screen_depth": random.choice([24, 30, 32]),
        "timezone": random.choice(
            [
                "America/New_York",
                "America/Los_Angeles",
                "Europe/London",
                "Europe/Berlin",
                "Asia/Tokyo",
                "Australia/Sydney",
            ]
        ),
        "language": random.choice(["en-US", "en-GB", "en-CA"]),
    }


def _apply_stealth_to_page(page, fingerprint):
    """Apply stealth modifications to bypass bot detection."""

    # Stealth script to inject before page load
    stealth_script = f"""
    // Override webdriver property
    Object.defineProperty(navigator, 'webdriver', {{
        get: () => undefined,
    }});
    
    // Override automation properties
    delete window.navigator.__proto__.webdriver;
    
    // Override chrome property
    window.chrome = {{
        runtime: {{
            onConnect: null,
            onMessage: null,
        }},
        loadTimes: function() {{}},
        csi: function() {{}},
        app: {{}}
    }};
    
    // Override permissions
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) => (
        parameters.name === 'notifications' ?
            Promise.resolve({{ state: Notification.permission }}) :
            originalQuery(parameters)
    );
    
    // Override plugins
    Object.defineProperty(navigator, 'plugins', {{
        get: () => [
            {{
                0: {{type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format", enabledPlugin: Plugin}},
                description: "Portable Document Format",
                filename: "internal-pdf-viewer",
                length: 1,
                name: "Chrome PDF Plugin"
            }},
            {{
                0: {{type: "application/pdf", suffixes: "pdf", description: "", enabledPlugin: Plugin}},
                description: "",
                filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                length: 1,
                name: "Chrome PDF Viewer"
            }},
            {{
                0: {{type: "application/x-nacl", suffixes: "", description: "Native Client Executable", enabledPlugin: Plugin}},
                1: {{type: "application/x-pnacl", suffixes: "", description: "Portable Native Client Executable", enabledPlugin: Plugin}},
                description: "",
                filename: "internal-nacl-plugin",
                length: 2,
                name: "Native Client"
            }}
        ]
    }});
    
    // Override languages
    Object.defineProperty(navigator, 'languages', {{
        get: () => ['{fingerprint["language"]}'],
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
        if (parameter === 37445) {{
            return 'Intel Inc.';
        }}
        if (parameter === 37446) {{
            return '{fingerprint["webgl_renderer"]}';
        }}
        return getParameter.call(this, parameter);
    }};
    
    // Override screen properties
    Object.defineProperty(screen, 'colorDepth', {{
        get: () => {fingerprint["screen_depth"]},
    }});
    
    // Override Date timezone
    const originalGetTimezoneOffset = Date.prototype.getTimezoneOffset;
    Date.prototype.getTimezoneOffset = function() {{
        return -{random.randint(-12, 12) * 60};
    }};
    
    // Add realistic mouse and keyboard events
    ['mousedown', 'mouseup', 'mousemove', 'click', 'keydown', 'keyup'].forEach(event => {{
        document.addEventListener(event, () => {{}}, true);
    }});
    
    // Override iframe contentWindow
    const originalContentWindow = Object.getOwnPropertyDescriptor(HTMLIFrameElement.prototype, 'contentWindow');
    Object.defineProperty(HTMLIFrameElement.prototype, 'contentWindow', {{
        get: function() {{
            return originalContentWindow.get.call(this);
        }}
    }});
    
    console.log('Stealth mode activated');
    """

    # Add stealth script to page
    page.add_init_script(stealth_script)


def _simulate_human_behavior(page):
    """Simulate human-like browsing behavior."""
    # Random mouse movements
    for _ in range(random.randint(2, 5)):
        x = random.randint(100, 800)
        y = random.randint(100, 600)
        page.mouse.move(x, y)
        page.wait_for_timeout(random.randint(100, 300))

    # Random scrolling
    for _ in range(random.randint(1, 3)):
        scroll_amount = random.randint(100, 500)
        page.evaluate(f"window.scrollBy(0, {scroll_amount})")
        page.wait_for_timeout(random.randint(200, 500))

    # Simulate reading time
    page.wait_for_timeout(random.randint(1000, 3000))


def _get_bidi_type(char):
    """Get the bidirectional type of a character according to Unicode."""
    return unicodedata.bidirectional(char)


def _is_rtl_script(char):
    """Check if character belongs to an RTL script."""
    code_point = ord(char)
    return any(start <= code_point <= end for start, end in _RTL_SCRIPT_RANGES)


def _first_strong_direction(text: str) -> str:
    """
    Determine direction based on first strong directional character.
    This is the algorithm recommended by Unicode Standard Annex #9.
    """
    for char in text:
        bidi_type = _get_bidi_type(char)
        if bidi_type in _RTL_BIDI:
            return "rtl"
        elif bidi_type in _LTR_BIDI:
            return "ltr"
    return "ltr"  # Default to LTR if no strong characters found


def _character_counting_direction(text: str) -> str:
    """
    Enhanced character counting method that considers script ranges
    and bidirectional character properties.
    """
    rtl_count = 0
    ltr_count = 0

    for char in text:
        bidi_type = _get_bidi_type(char)

        # Count strong RTL characters
        if bidi_type in _RTL_BIDI or _is_rtl_script(char):
            rtl_count += 1
        # Count strong LTR characters (excluding numbers and neutrals)
        elif bidi_type in _LTR_BIDI:
            ltr_count += 1

    # If we have a clear majority, use it
    if rtl_count > ltr_count:
        return "rtl"
    elif ltr_count > rtl_count:
        return "ltr"

    # Fallback to first-strong if counts are equal
    return _first_strong_direction(text)


def _weighted_direction(text: str) -> str:
    """
    Weighted algorithm that gives more importance to certain character types
    and considers text structure.
    """
    rtl_weight = 0
    ltr_weight = 0

    # Split into words to analyze structure
    words = text.split()

    for word in words:
        word_rtl = 0
        word_ltr = 0

        for char in word:
            bidi_type = _get_bidi_type(char)

            if bidi_type in _RTL_BIDI or _is_rtl_script(char):
                word_rtl += 2  # Higher weight for RTL
            elif bidi_type in _LTR_BIDI:
                word_ltr += 1
            elif bidi_type in _WEAK_BIDI:
                # Numbers get neutral weight
                pass

        # Add word-level bias
        if word_rtl > word_ltr:
            rtl_weight += word_rtl + 1  # Bonus for RTL-dominant words
        elif word_ltr > word_rtl:
            ltr_weight += word_ltr

    # Consider sentence-level patterns
    # RTL languages often have punctuation at the beginning when displayed
    if text.strip().endswith(("!", "?", ".")):
        first_char_bidi = _get_bidi_type(text.strip()[0]) if text.strip() else ""
        if first_char_bidi in _RTL_BIDI:
            rtl_weight += 2

    return "rtl" if rtl_weight > ltr_weight else "ltr"


def _smart_direction_detection(text: str, method: str = "auto") -> str:
    """
    Advanced direction detection using multiple algorithms.

    Args:
        text: Text to analyze
        method: Detection method - "auto", "first-strong", "counting", "weighted"

    Returns:
        "rtl" or "ltr"
    """
    if not text or not text.strip():
        return "ltr"

    # Clean text for analysis (remove HTML tags if present, keep content)
    clean_text = re.sub(r"<[^>]+>", " ", text)
    clean_text = re.sub(r"\s+", " ", clean_text).strip()

    if not clean_text:
        return "ltr"

    if method == "first-strong":
        return _first_strong_direction(clean_text)
    elif method == "counting":
        return _character_counting_direction(clean_text)
    elif method == "weighted":
        return _weighted_direction(clean_text)
    else:  # auto - use best method based on text characteristics
        # For short texts (< 10 chars), use first-strong
        if len(clean_text) < 10:
            return _first_strong_direction(clean_text)

        # For mixed content, use weighted algorithm
        has_mixed_scripts = any(_is_rtl_script(c) for c in clean_text) and any(
            _get_bidi_type(c) in _LTR_BIDI for c in clean_text
        )

        if has_mixed_scripts:
            return _weighted_direction(clean_text)

        # For pure text, use enhanced counting
        return _character_counting_direction(clean_text)


# Legacy function for backward compatibility
def _guess_dir(text: str) -> str:
    """Legacy direction detection - now uses smart detection."""
    return _smart_direction_detection(text, method="auto")


# --- Role util -------------------------------------------------------------
def _role(div):
    """Extract role from message element."""
    role = div.get("data-message-author-role", "").lower()
    return "🔵 **User:**" if role == "user" else "🟢 **ChatGPT:**"


def _claude_role(element, is_user=False):
    """Extract role for Claude message element."""
    return "🔵 **User:**" if is_user else "🟡 **Claude:**"


# --- Main scraper ----------------------------------------------------------
def scrape_share(
    link: str,
    include_direction: bool = True,
    include_speakers: bool = True,
    timeout: int = 30_000,
    direction_method: str = "auto",
) -> str:
    """
    Scrape a ChatGPT shared conversation with enhanced RTL/LTR detection.

    Args:
        link: ChatGPT share URL
        include_direction: Whether to include RTL/LTR direction tags
        include_speakers: Whether to include speaker identification
        timeout: Total timeout in milliseconds
        direction_method: Direction detection method - "auto", "first-strong", "counting", "weighted"

    Returns:
        Markdown formatted conversation

    Raises:
        Exception: If scraping fails with descriptive error message
    """
    # Validate URL format
    if not re.match(r"https://(chat\.openai\.com|chatgpt\.com)/share/.+", link):
        raise Exception(
            "Invalid ChatGPT share link format. Please ensure it's a valid share URL."
        )

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page()

            # Navigate to the page
            try:
                page.goto(link, wait_until="domcontentloaded", timeout=timeout)
            except PlaywrightTimeoutError:
                raise Exception(
                    "Timeout while loading the page. Please check your internet connection and try again."
                )

            # Try to dismiss modal dialogs
            try:
                if page.locator(MODAL_DISMISS).is_visible(timeout=3000):
                    page.locator(MODAL_DISMISS).click()
                elif page.locator(LOGIN_BTN).is_visible(timeout=3000):
                    page.locator(LOGIN_BTN).click()
            except:
                pass  # Continue if modal dismissal fails

            # Wait for content to load
            try:
                page.wait_for_selector("div.markdown", timeout=timeout)
            except PlaywrightTimeoutError:
                # Try alternative selectors
                try:
                    page.wait_for_selector("[data-message-author-role]", timeout=10000)
                except PlaywrightTimeoutError:
                    raise Exception(
                        "The conversation content didn't load properly. The share link might be invalid or expired."
                    )

            html = page.content()
            browser.close()

    except PlaywrightTimeoutError:
        raise Exception(
            "Request timed out. Please try again or check if the share link is still valid."
        )
    except Exception as e:
        if "net::" in str(e) or "ERR_" in str(e):
            raise Exception(
                "Network error occurred. Please check your internet connection."
            )
        if (
            "Invalid ChatGPT share link" in str(e)
            or "Timeout while loading" in str(e)
            or "conversation content didn't load" in str(e)
        ):
            raise e
        raise Exception(f"Browser error: {str(e)}")

    # Parse HTML content
    try:
        soup = BeautifulSoup(html, "html.parser")
        messages = soup.select("[data-message-author-role]")

        if not messages:
            raise Exception(
                "No conversation messages found. The page might not have loaded properly or the share link might be invalid."
            )

        blocks = []

        for msg in messages:
            try:
                # Get speaker role (optional)
                if include_speakers:
                    header = _role(msg)
                else:
                    header = ""

                md_container = msg.select_one("div.markdown")
                raw_text = (
                    md_container.get_text(separator=" ", strip=True)
                    if md_container
                    else msg.get_text(separator=" ", strip=True)
                )

                if not raw_text.strip():
                    continue  # Skip empty messages

                # Get markdown content
                if md_container:
                    body_md = md(str(md_container))
                else:
                    body_md = raw_text

                # Apply direction wrapping with enhanced detection (optional)
                if include_direction:
                    direction = _smart_direction_detection(
                        raw_text, method=direction_method
                    )
                    wrapper_open = f'<div dir="{direction}">'
                    wrapper_close = "</div>"
                    formatted_content = f"{wrapper_open}\n{body_md}\n{wrapper_close}"
                else:
                    formatted_content = body_md

                # Build the block
                if include_speakers and header:
                    block = f"{header}\n\n{formatted_content}\n\n---\n"
                else:
                    block = f"{formatted_content}\n\n---\n"

                blocks.append(block)

            except Exception as e:
                # Skip individual message errors but continue processing
                continue

        if not blocks:
            raise Exception("No readable content found in the conversation.")

        result = "\n".join(blocks)

        # Add metadata header with algorithm info
        options_info = []
        if include_direction:
            options_info.append(
                f"RTL/LTR detection enabled (method: {direction_method})"
            )
        if include_speakers:
            options_info.append("Speaker identification enabled")

        options_text = (
            f" ({', '.join(options_info)})" if options_info else " (Plain text mode)"
        )

        metadata = f"# ChatGPT Conversation\n\n*Downloaded from: {link}*\n*Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}*\n*Options:{options_text}*\n\n---\n\n"

        return metadata + result

    except Exception as e:
        if "No conversation" in str(e) or "No readable content" in str(e):
            raise e
        raise Exception(f"Error parsing conversation content: {str(e)}")


def scrape_claude_share(
    link: str,
    include_direction: bool = True,
    include_speakers: bool = True,
    timeout: int = 60_000,
    direction_method: str = "auto",
) -> str:
    """
    Scrape a Claude share link with advanced anti-bot bypass techniques.

    Uses undetected-playwright methods, stealth fingerprinting, and multiple retry strategies
    to successfully bypass Claude's security measures.

    Args:
        link: Claude share URL
        include_direction: Whether to wrap text with RTL/LTR direction tags
        include_speakers: Whether to include speaker identification
        timeout: Playwright timeout in milliseconds (increased for stealth mode)
        direction_method: Direction detection method

    Returns:
        Markdown string with conversation content
    """
    # Validate Claude URL format
    if not link.startswith("https://claude.ai/share/"):
        raise Exception(
            "Invalid Claude share link format. Please ensure it's a valid Claude share URL."
        )

    # Generate randomized fingerprint for stealth
    fingerprint = _generate_stealth_fingerprint()
    print(f"🕵️ Using stealth mode: {fingerprint['user_agent'][:50]}...")

    # Retry logic for multiple attempts
    max_retries = 3
    for attempt in range(max_retries):
        print(f"🚀 Attempt {attempt + 1}/{max_retries}")

        try:
            with sync_playwright() as pw:
                # Advanced anti-detection browser launch
                browser = pw.chromium.launch(
                    headless=True,  # Headless mode for better performance
                    args=[
                        "--no-sandbox",
                        "--disable-setuid-sandbox",
                        "--disable-blink-features=AutomationControlled",
                        "--disable-dev-shm-usage",
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

                # Create context with advanced stealth fingerprint
                context = browser.new_context(
                    user_agent=fingerprint["user_agent"],
                    viewport=fingerprint["viewport"],
                    locale=fingerprint["language"],
                    timezone_id=fingerprint["timezone"],
                    device_scale_factor=1.0,
                    screen={
                        "width": fingerprint["viewport"]["width"],
                        "height": fingerprint["viewport"]["height"],
                    },
                    extra_http_headers={
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                        "Accept-Language": f"{fingerprint['language']},en;q=0.5",
                        "Accept-Encoding": "gzip, deflate, br",
                        "DNT": "1",
                        "Connection": "keep-alive",
                        "Upgrade-Insecure-Requests": "1",
                        "Sec-Fetch-Dest": "document",
                        "Sec-Fetch-Mode": "navigate",
                        "Sec-Fetch-Site": "none",
                        "Cache-Control": "max-age=0",
                    },
                )

                page = context.new_page()

                # Apply stealth modifications
                _apply_stealth_to_page(page, fingerprint)

                # Simulate human behavior before navigation
                print("🤖 Simulating human behavior...")
                _simulate_human_behavior(page)

                # Navigate to the page with more lenient settings
                try:
                    print(f"🌐 Loading Claude share with stealth: {link}")
                    page.wait_for_timeout(
                        random.randint(1000, 3000)
                    )  # Human-like delay

                    response = page.goto(
                        link, wait_until="domcontentloaded", timeout=timeout
                    )

                    # Check response status
                    if response and response.status >= 400:
                        print(f"⚠️ HTTP {response.status} received")
                        if response.status == 403:
                            raise Exception(
                                "Access forbidden - likely blocked by security"
                            )

                except PlaywrightTimeoutError:
                    raise Exception(
                        "Timeout while loading the Claude page. Please check your internet connection and try again."
                    )

                # Additional human simulation after page load
                _simulate_human_behavior(page)

                # Enhanced security challenge detection
                page.wait_for_timeout(3000)  # Give page time to load
                page_content = page.content()

                # Specific security challenge indicators (excluding normal popups)
                security_indicators = [
                    "Verify you are human",
                    "checking if the site connection is secure",
                    "This process is automatic",
                    "DDoS protection by Cloudflare",
                    "Just a moment",
                    "Ray ID:",
                    "cloudflare-static",
                    "cf-browser-verification",
                    "challenge-platform",
                    "Access denied",
                    "Forbidden",
                    "Please turn JavaScript on and reload the page",
                ]

                # Exclude normal cookie/settings popups
                normal_popups = [
                    "Cookie settings",
                    "We use cookies",
                    "customize or personalize your experience",
                    "Accept All Cookies",
                    "Reject All Cookies",
                ]

                # Only detect as security challenge if we have security indicators but no normal popups
                has_security_indicators = any(
                    indicator in page_content for indicator in security_indicators
                )
                has_normal_popups = any(
                    popup in page_content for popup in normal_popups
                )

                challenge_detected = has_security_indicators and not has_normal_popups

                # Handle normal cookie popup automatically
                if has_normal_popups and not has_security_indicators:
                    print("🍪 Cookie popup detected, attempting to accept...")
                    try:
                        # Try to find and click "Accept All Cookies" button
                        accept_buttons = page.locator(
                            "button:has-text('Accept All Cookies'), button:has-text('Accept All'), button:has-text('Accept')"
                        )
                        if accept_buttons.count() > 0:
                            print("✅ Clicking Accept All Cookies...")
                            accept_buttons.first.click()
                            page.wait_for_timeout(2000)
                        else:
                            # Try to dismiss the popup by clicking outside or escape
                            page.keyboard.press("Escape")
                            page.wait_for_timeout(1000)
                    except Exception as cookie_error:
                        print(f"⚠️ Cookie popup handling failed: {cookie_error}")

                if challenge_detected:
                    print("🛡️ Security challenge detected, attempting bypass...")

                    # Wait for potential auto-redirect
                    page.wait_for_timeout(5000)

                    # Try clicking through simple challenges
                    try:
                        verify_buttons = page.locator(
                            "button:has-text('Verify'), input[type='button'][value*='verify'], a:has-text('Continue')"
                        )
                        if verify_buttons.count() > 0:
                            print("🖱️ Found verify button, attempting click...")
                            verify_buttons.first.click()
                            page.wait_for_timeout(3000)

                        checkboxes = page.locator("input[type='checkbox']")
                        if checkboxes.count() > 0:
                            print("☑️ Found checkbox, attempting interaction...")
                            checkboxes.first.click()
                            page.wait_for_timeout(2000)
                    except Exception as bypass_error:
                        print(f"⚠️ Challenge bypass attempt failed: {bypass_error}")

                    # Re-check after bypass attempts
                    page_content = page.content()
                    still_blocked = any(
                        indicator in page_content for indicator in security_indicators
                    )

                    if still_blocked:
                        print(
                            f"❌ Attempt {attempt + 1} failed - security challenge not bypassed"
                        )
                        browser.close()
                        if attempt < max_retries - 1:
                            wait_time = (2**attempt) + random.randint(1, 5)
                            print(f"⏳ Waiting {wait_time} seconds before retry...")
                            time.sleep(wait_time)
                            continue
                        else:
                            raise Exception(
                                "🚫 Failed to bypass Claude security challenges after all attempts. "
                                "Please try:\n"
                                "1. Opening the link in your browser first and completing any challenges\n"
                                "2. Using a different network/VPN if possible\n"
                                "3. Waiting a few minutes and trying again\n"
                                "4. Generating a new share link from Claude"
                            )

                # Enhanced content waiting strategies
                content_loaded = False
                print("⏳ Waiting for conversation content...")

                # Strategy 1: Wait for Claude-specific conversation elements
                try:
                    page.wait_for_selector(
                        "div[class*='font-claude-message'], [data-testid='user-message'], div[data-test-render-count], .prose",
                        timeout=15000,
                    )
                    content_loaded = True
                    print(
                        "✅ Claude conversation content detected via primary selectors"
                    )
                except PlaywrightTimeoutError:
                    print(
                        "🔍 Primary selectors not found, trying alternative approaches..."
                    )

                # Strategy 2: Wait for substantial text content
                if not content_loaded:
                    try:
                        page.wait_for_function(
                            "document.body.innerText.length > 200", timeout=10000
                        )
                        content_loaded = True
                        print("✅ Substantial content detected")
                    except PlaywrightTimeoutError:
                        print("📄 Minimal text content, proceeding...")

                # Strategy 3: Give page more time to fully render
                if not content_loaded:
                    print("⏱️ Final wait for content rendering...")
                    page.wait_for_timeout(8000)

                # Final human simulation
                _simulate_human_behavior(page)

                # Get final page content
                content = page.content()

                # Final security check - use the same improved logic
                final_has_security_indicators = any(
                    indicator in content for indicator in security_indicators
                )
                final_has_normal_popups = any(
                    popup in content for popup in normal_popups
                )

                # If content was loaded successfully, don't do final security check
                final_security_check = (
                    final_has_security_indicators
                    and not final_has_normal_popups
                    and not content_loaded
                )

                # Debug output
                if content_loaded:
                    print(f"🎯 Content successfully loaded, skipping security check")

                if final_security_check:
                    print(
                        f"❌ Attempt {attempt + 1} failed - still blocked after bypass"
                    )
                    browser.close()
                    if attempt < max_retries - 1:
                        continue
                    else:
                        raise Exception(
                            "🔒 Claude is still blocking automated access after all bypass attempts. "
                            "Please try accessing the link manually in your browser first."
                        )

                print(f"✅ Attempt {attempt + 1} successful - extracting content...")
                browser.close()
                break  # Success - exit retry loop

        except PlaywrightTimeoutError:
            print(f"⏰ Attempt {attempt + 1} timed out")
            if attempt < max_retries - 1:
                continue
            else:
                raise Exception(
                    "Request timed out after all attempts. Please check if the Claude share link is still valid."
                )
        except Exception as e:
            print(f"❌ Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                wait_time = (2**attempt) + random.randint(1, 3)
                print(f"⏳ Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
                continue
            else:
                if "net::" in str(e) or "ERR_" in str(e):
                    raise Exception(
                        "Network error occurred. Please check your internet connection."
                    )
                if "Invalid Claude share link" in str(
                    e
                ) or "Timeout while loading" in str(e):
                    raise e
                raise Exception(
                    f"All {max_retries} attempts failed. Last error: {str(e)}"
                )

    # Parse HTML content
    try:
        soup = BeautifulSoup(content, "html.parser")

        # Find conversation messages
        messages = []

        # Strategy 1: Look for message containers with data-test-render-count
        message_containers = soup.find_all("div", {"data-test-render-count": True})

        for container in message_containers:
            # Check if this is a user message
            user_msg = container.find('[data-testid="user-message"]')
            if user_msg:
                # Extract user message text
                text_content = user_msg.get_text(strip=True)
                if text_content:
                    messages.append(
                        {"role": "user", "content": text_content, "is_user": True}
                    )
                continue

            # Check if this is an assistant message
            assistant_msg = container.find(".font-claude-message")
            if assistant_msg:
                # Extract assistant message text
                text_content = assistant_msg.get_text(strip=True)
                if text_content:
                    messages.append(
                        {
                            "role": "assistant",
                            "content": text_content,
                            "is_user": False,
                        }
                    )
                continue

        # Strategy 2: If no messages found, try simpler approach
        if not messages:
            print("Trying alternative message extraction...")

            # Look for user messages with simpler selectors
            user_messages = soup.find_all(attrs={"data-testid": "user-message"})
            for user_msg in user_messages:
                text_content = user_msg.get_text(strip=True)
                if text_content:
                    messages.append(
                        {"role": "user", "content": text_content, "is_user": True}
                    )

            # Look for assistant messages with font-claude-message class
            assistant_messages = soup.find_all(
                class_=lambda x: x and "font-claude-message" in x
            )
            for assistant_msg in assistant_messages:
                text_content = assistant_msg.get_text(strip=True)
                if text_content:
                    messages.append(
                        {
                            "role": "assistant",
                            "content": text_content,
                            "is_user": False,
                        }
                    )

        # Strategy 3: Last resort - look for any conversation content
        if not messages:
            print("Trying final fallback extraction...")
            # Look for any text content that might be conversation
            all_text_divs = soup.find_all("div")
            potential_messages = []

            for div in all_text_divs:
                text = div.get_text(strip=True)
                if text and len(text) > 10:  # Only consider substantial text
                    # Try to determine if it's a user or assistant message based on context
                    parent_classes = div.get("class", [])
                    parent_str = " ".join(parent_classes) if parent_classes else ""

                    if "user" in parent_str.lower():
                        potential_messages.append(
                            {"role": "user", "content": text, "is_user": True}
                        )
                    elif len(potential_messages) % 2 == 0:  # Assume alternating pattern
                        potential_messages.append(
                            {"role": "user", "content": text, "is_user": True}
                        )
                    else:
                        potential_messages.append(
                            {"role": "assistant", "content": text, "is_user": False}
                        )

            # Only use if we found some content
            if potential_messages:
                messages = potential_messages[:10]  # Limit to prevent too much noise

        if not messages:
            raise Exception(
                "No conversation messages found. The Claude share link may be invalid or the conversation may be empty."
            )

        # Convert messages to markdown
        blocks = []

        for msg in messages:
            content_text = msg["content"]

            # Apply direction detection if enabled
            if include_direction:
                direction = _smart_direction_detection(content_text, direction_method)
                formatted_content = f'<div dir="{direction}">\n{content_text}\n</div>'
            else:
                formatted_content = content_text

            # Add speaker identification if enabled
            if include_speakers:
                speaker_label = _claude_role(None, msg["is_user"])
                block = f"{speaker_label}\n\n{formatted_content}\n\n---\n"
            else:
                block = f"{formatted_content}\n\n---\n"

            blocks.append(block)

        if not blocks:
            raise Exception("No readable content found in the conversation.")

        result = "\n".join(blocks)

        # Add metadata header with algorithm info
        options_info = []
        if include_direction:
            options_info.append(
                f"RTL/LTR detection enabled (method: {direction_method})"
            )
        if include_speakers:
            options_info.append("Speaker identification enabled")

        options_text = (
            f" ({', '.join(options_info)})" if options_info else " (Plain text mode)"
        )

        metadata = f"# Claude Conversation\n\n*Downloaded from: {link}*\n*Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}*\n*Options:{options_text}*\n\n---\n\n"

        print(
            f"Successfully extracted {len(messages)} messages from Claude conversation"
        )
        return metadata + result

    except Exception as e:
        if "No conversation" in str(e) or "No readable content" in str(e):
            raise e
        raise Exception(f"Error parsing conversation content: {str(e)}")

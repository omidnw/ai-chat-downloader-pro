# app.py
"""
Enhanced Streamlit web application for downloading AI conversations.
Supports both ChatGPT and Claude with automatic platform detection, queue management, and batch processing.
"""

import warnings

# Suppress ScriptRunContext warnings when using asyncio with Streamlit
warnings.filterwarnings("ignore", message=".*ScriptRunContext.*")
warnings.filterwarnings("ignore", message=".*missing ScriptRunContext.*")

import streamlit as st
import time
import asyncio
import json
import zipfile
import tempfile
import os
from typing import List, Dict, Any
from datetime import datetime

# Import from new utils package
from utils import (
    # Core download functions
    ai_download,
    ai_detect_platform,
    Platform,
    get_platform_name,
    ai_get_supported_platforms,
    # Enhanced async features
    scrape_with_auto_detection,
    scrape_multiple_urls,
    quick_scrape,
    quick_batch_scrape,
    # Queue management (optional)
    add_to_queue,
    process_queue_task,
    get_queue_status,
    get_task_result,
    # Platform detection
    detect_platform,
    is_supported_url,
    get_supported_platforms,
)

# Check if queue features are available
try:
    from litequeue import LiteQueue
    from asyncio_throttle import Throttler

    QUEUE_AVAILABLE = True
except ImportError:
    QUEUE_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="AI Chat Downloader Pro",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling and auto-detection
st.markdown(
    """
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    .stTextInput > div > div > input {
        font-size: 16px;
    }
    .platform-badge {
        display: inline-block;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        font-size: 0.8rem;
        font-weight: bold;
        margin-left: 0.5rem;
    }
    .chatgpt-badge {
        background-color: #10a37f;
        color: white;
    }
    .claude-badge {
        background-color: #d97706;
        color: white;
    }
    .real-time-detection {
        animation: fadeIn 0.3s ease-in;
        margin: 0.5rem 0;
    }
    .queue-status {
        background-color: #e3f2fd;
        padding: 0.5rem 1rem;
        border-radius: 0.3rem;
        border-left: 3px solid #2196f3;
        margin: 0.5rem 0;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .batch-result {
        padding: 0.5rem;
        margin: 0.25rem 0;
        border-radius: 0.3rem;
        font-family: monospace;
        font-size: 0.9em;
    }
    .batch-success {
        background-color: #d4edda;
        border-left: 3px solid #28a745;
    }
    .batch-error {
        background-color: #f8d7da;
        border-left: 3px solid #dc3545;
    }
    .auto-detect-badge {
        background-color: #0066cc;
        color: white;
        padding: 0.1rem 0.4rem;
        border-radius: 0.2rem;
        font-size: 0.7rem;
        margin-left: 0.3rem;
    }
</style>

<script>
// Auto-detection on paste and input
document.addEventListener('DOMContentLoaded', function() {
    const observer = new MutationObserver(function(mutations) {
        const inputs = document.querySelectorAll('input[type="text"]');
        inputs.forEach(function(input) {
            if (!input.hasAutoDetect) {
                input.hasAutoDetect = true;
                input.addEventListener('input', function() {
                    if (this.value.includes('claude.ai/share/') || 
                        this.value.includes('chatgpt.com/share/') || 
                        this.value.includes('chat.openai.com/share/')) {
                        // Trigger Streamlit rerun for auto-detection
                        this.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                });
                input.addEventListener('paste', function() {
                    setTimeout(function() {
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                    }, 100);
                });
            }
        });
    });
    observer.observe(document.body, { childList: true, subtree: true });
});
</script>
""",
    unsafe_allow_html=True,
)

# Initialize session state with auto-detection
if "processing_mode" not in st.session_state:
    st.session_state.processing_mode = "single"
if "current_link" not in st.session_state:
    st.session_state.current_link = ""
if "batch_urls" not in st.session_state:
    st.session_state.batch_urls = ""
if "queue_tasks" not in st.session_state:
    st.session_state.queue_tasks = []
if "auto_detected_platforms" not in st.session_state:
    st.session_state.auto_detected_platforms = {}


def auto_detect_platform_from_url(url: str) -> tuple:
    """Auto-detect platform with robust validation"""
    if not url or not url.strip():
        return None, ""

    url = url.strip()

    # Enhanced detection patterns
    chatgpt_patterns = [
        "chatgpt.com/share/",
        "chat.openai.com/share/",
    ]

    claude_patterns = [
        "claude.ai/share/",
    ]

    # Check for ChatGPT
    for pattern in chatgpt_patterns:
        if pattern in url and url.startswith("https://"):
            # Validate format: should have UUID-like ID after share/
            share_part = url.split("/share/")
            if len(share_part) > 1 and len(share_part[1]) >= 8:
                return Platform.CHATGPT, "ChatGPT"

    # Check for Claude
    for pattern in claude_patterns:
        if pattern in url and url.startswith("https://"):
            # Validate format: should have ID after share/
            share_part = url.split("/share/")
            if len(share_part) > 1 and len(share_part[1]) >= 8:
                return Platform.CLAUDE, "Claude"

    return None, ""


def validate_and_detect_url(url: str, context: str = "") -> dict:
    """Comprehensive URL validation and detection"""
    result = {
        "valid": False,
        "platform": None,
        "platform_name": "",
        "error": "",
        "url": url.strip() if url else "",
    }

    if not url or not url.strip():
        return result

    url = url.strip()

    # Basic URL validation
    if not url.startswith("https://"):
        result["error"] = "URL must start with https://"
        return result

    # Auto-detect platform
    platform, platform_name = auto_detect_platform_from_url(url)

    if platform:
        # Double-check with utils detection
        utils_platform = ai_detect_platform(url)
        if utils_platform == platform:
            result["valid"] = True
            result["platform"] = platform
            result["platform_name"] = platform_name
        else:
            result["error"] = "Platform detection mismatch"
    else:
        result["error"] = "Unsupported URL format"

    return result


# Sidebar for processing mode and queue management
with st.sidebar:
    st.markdown("## 🚀 Processing Mode")

    processing_mode = st.radio(
        "Choose processing mode:",
        ["single", "batch", "queue"],
        format_func=lambda x: {
            "single": "📄 Single URL",
            "batch": "📊 Batch Processing",
            "queue": "🔄 Queue Management",
        }[x],
        key="processing_mode",
    )

    if processing_mode == "queue" and not QUEUE_AVAILABLE:
        st.warning("⚠️ Queue features require additional dependencies:")
        st.code("pip install litequeue asyncio-throttle")
        st.info("Switching to single URL mode...")
        processing_mode = "single"

    st.markdown("---")

    # Auto-detection status
    st.markdown("### 🎯 Auto-Detection")
    st.markdown("**Status:** ✅ **Active**")
    st.markdown("*Automatically detects ChatGPT and Claude URLs*")

    # Queue status (if available)
    if QUEUE_AVAILABLE and processing_mode == "queue":
        st.markdown("### 📊 Queue Status")

        if st.button("🔄 Refresh Status"):
            try:
                status = get_queue_status()
                if "error" not in status:
                    st.markdown(
                        f"""
                    <div class="queue-status">
                    📋 Queue: {status['queue_size']} tasks<br>
                    ⚡ Active: {status['active_sessions']} sessions<br>
                    ✅ Processed: {status['processed_tasks']} total
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.error("Queue not available")
            except Exception as e:
                st.error(f"Queue error: {str(e)}")

    # Enhanced features info
    st.markdown("### 🌟 Features")
    feature_status = "✅" if QUEUE_AVAILABLE else "⚠️"
    st.markdown(
        f"""
    - ✅ **Auto-detection** (Real-time)
    - ✅ ChatGPT & Claude support
    - ✅ RTL/LTR direction detection
    - ✅ Advanced anti-bot bypass
    - ✅ Batch processing
    - {feature_status} Queue management
    - ✅ Real-time status updates
    """
    )

# Main header
st.markdown(
    '<h1 class="main-header">📝 AI Chat Downloader Pro</h1>', unsafe_allow_html=True
)

if processing_mode == "single":
    st.markdown(
        '<h3 style="text-align: center; color: #666;">Convert ChatGPT & Claude conversations to Markdown with advanced RTL/LTR detection for Persian/Farsi, Arabic & more</h3>',
        unsafe_allow_html=True,
    )
elif processing_mode == "batch":
    st.markdown(
        '<h3 style="text-align: center; color: #666;">Batch process multiple URLs with concurrent processing</h3>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        '<h3 style="text-align: center; color: #666;">Queue-based processing with priority support and background workers</h3>',
        unsafe_allow_html=True,
    )

# Processing mode specific UI
if processing_mode == "single":
    # Single URL processing with all original options preserved

    # Information section
    with st.expander("ℹ️ How to use this tool", expanded=False):
        supported_platforms = ai_get_supported_platforms()
        platforms_text = "\n".join(
            [f"    • {platform}" for platform in supported_platforms]
        )

        st.markdown(
            f"""
        **Steps to download your AI conversation:**
        
        **For ChatGPT:**
        1. Open your ChatGPT conversation
        2. Click the share button (🔗) in the top-right corner
        3. Click "Create public link" 
        4. Copy the generated link
        
        **For Claude:**
        1. Open your Claude conversation
        2. Click the share button (🔗) at the top
        3. Copy the generated share link
        
        **Then:**
        5. Paste the link below and configure your options
        6. Click "Download Chat" (platform will be auto-detected)
        
        **Supported URLs:**
{platforms_text}
        
        **Features:**
        - ✅ Supports both ChatGPT and Claude conversations
        - ✅ Automatic platform detection based on URL
        - ✅ Preserves conversation structure
        - ✅ Advanced RTL/LTR text direction detection with multiple algorithms
        - ✅ Excellent support for Persian/Farsi (فارسی), Arabic (العربية), and mixed-language content
        - ✅ Customizable speaker identification
        - ✅ Clean Markdown formatting
        - ✅ Ready-to-save file download
        """
        )

    def detect_and_update_platform():
        """Enhanced real-time platform detection callback with immediate rerun."""
        current_input = st.session_state.get("link_input", "")
        if current_input != st.session_state.current_link:
            st.session_state.current_link = current_input
            # Force immediate rerun for auto-detection
            st.rerun()

    # Input section with enhanced auto-detection
    st.markdown("### 🔗 Paste your AI chat share link:")

    link = st.text_input(
        label="Link",
        placeholder="Paste your share link here - supports ChatGPT and Claude",
        label_visibility="collapsed",
        help="🎯 Auto-detection: Platform is detected immediately when you paste a URL",
        key="link_input",
        on_change=detect_and_update_platform,
    )

    # Auto-detect platform and show badge immediately when typing
    platform = ai_detect_platform(link) if link and link.strip() else None

    # Real-time platform detection display
    if link and link.strip():
        if platform:
            platform_name = get_platform_name(platform)
            badge_class = (
                "chatgpt-badge" if platform == Platform.CHATGPT else "claude-badge"
            )

            st.markdown(
                f'<div class="real-time-detection">🎯 <span class="platform-badge {badge_class}">{platform_name}</span> detected automatically</div>',
                unsafe_allow_html=True,
            )

            # Show a small success indicator
            st.success(
                "✅ Ready to download! Configure your options below and click the download button."
            )
        else:
            st.warning(
                "⚠️ Platform not recognized. Please check your URL format and ensure it's a valid share link."
            )

            # Show examples of valid URLs
            with st.expander("📋 See examples of valid share links"):
                st.markdown(
                    """
                **ChatGPT Examples:**
                - `https://chatgpt.com/share/e1234567-89ab-cdef-0123-456789abcdef`
                - `https://chat.openai.com/share/e1234567-89ab-cdef-0123-456789abcdef`
                
                **Claude Examples:**
                - `https://claude.ai/share/a1b2c3d4-5e6f-7890-abcd-ef1234567890`
                """
                )

    # Options section - FULL USER CONTROL RESTORED
    st.markdown("### ⚙️ Download Options:")
    st.markdown(
        "*Configure your download preferences - all options are optional and user-controlled*"
    )

    col1, col2 = st.columns(2)

    with col1:
        include_direction = st.checkbox(
            "🌍 Include RTL/LTR direction tags",
            value=True,
            help="Automatically detects text direction and wraps content in <div dir='rtl'> or <div dir='ltr'> tags. Disable for plain text output.",
        )

    with col2:
        include_speakers = st.checkbox(
            "👥 Include speaker identification",
            value=True,
            help="Adds speaker labels to distinguish between user and AI assistant. Disable for anonymous conversation format.",
        )

    # Direction detection method selection - FULL USER CONTROL
    if include_direction:
        st.markdown("#### 🔍 Text Direction Detection Method:")
        st.info(
            "💡 **Advanced RTL/LTR Detection** - Perfect for Persian/Farsi (فارسی), Arabic (العربية), and mixed-language content"
        )

        direction_method = st.selectbox(
            "Choose detection algorithm:",
            options=["auto", "first-strong", "counting", "weighted"],
            index=0,
            help="Select the algorithm for detecting text direction (RTL/LTR)",
        )

        # Help text for each method - DETAILED EXPLANATIONS
        method_descriptions = {
            "auto": "🤖 **Auto**: Intelligently selects the best method based on text characteristics (recommended for most users)",
            "first-strong": "🎯 **First-Strong**: Uses Unicode standard method based on first strong directional character (fast and reliable)",
            "counting": "📊 **Enhanced Counting**: Counts strong directional characters with script awareness (good for mixed content)",
            "weighted": "⚖️ **Weighted**: Advanced algorithm considering word structure and punctuation patterns (most accurate for complex text)",
        }

        st.markdown(method_descriptions[direction_method])

        # Additional info for disabled state
        st.markdown(
            "*⚠️ Note: Uncheck the option above to disable direction detection completely*"
        )
    else:
        direction_method = "auto"  # Default when direction detection is disabled
        st.markdown("#### 🚫 Direction Detection: Disabled")
        st.info(
            "ℹ️ Text will be output as plain content without RTL/LTR direction tags. Check the option above to enable advanced direction detection."
        )

    # Show preview of what will be included - ENHANCED USER CONTROL
    if link:
        st.markdown("### 👀 Output Format Preview:")
        preview_col1, preview_col2 = st.columns(2)

        with preview_col1:
            if include_direction:
                st.markdown(
                    f"✅ **Direction detection**: `<div dir='rtl'>` or `<div dir='ltr'>` (method: {direction_method})"
                )
                st.markdown("*Perfect for Persian/Farsi, Arabic, text*")
            else:
                st.markdown("🚫 **Direction detection**: Disabled")
                st.markdown("*Plain text output without direction tags*")

        with preview_col2:
            if include_speakers:
                if platform == Platform.CHATGPT:
                    st.markdown("✅ **Speaker labels**: `🔵 User:` and `🟢 ChatGPT:`")
                elif platform == Platform.CLAUDE:
                    st.markdown("✅ **Speaker labels**: `🔵 User:` and `🟡 Claude:`")
                else:
                    st.markdown("✅ **Speaker labels**: `🔵 User:` and `🤖 Assistant:`")
                st.markdown("*Clear conversation structure*")
            else:
                st.markdown("🚫 **Speaker labels**: Disabled")
                st.markdown("*Anonymous conversation format*")

        # Output format summary
        format_summary = []
        if include_direction:
            format_summary.append(f"RTL/LTR detection ({direction_method})")
        if include_speakers:
            format_summary.append("Speaker identification")

        if format_summary:
            st.markdown(f"**🎯 Active features:** {', '.join(format_summary)}")
        else:
            st.markdown(
                "**🎯 Output format:** Clean, plain text without special formatting"
            )
            st.info(
                "💡 **Tip**: Enable options above for enhanced formatting with direction detection and speaker labels"
            )

    # Validation and processing - PRESERVED
    if link:
        # Check if URL is supported
        if not platform:
            st.error("❌ Please enter a valid ChatGPT or Claude share link")
            supported_list = "\n".join(
                [f"• {url}" for url in ai_get_supported_platforms()]
            )
            st.markdown(
                f'<div class="info-box">💡 <strong>Supported platforms:</strong><br>{supported_list}</div>',
                unsafe_allow_html=True,
            )
        else:
            # Process the chat
            col1, col2, col3 = st.columns([1, 2, 1])

            with col2:
                # Use session state to track processing status
                if "processing_single" not in st.session_state:
                    st.session_state.processing_single = False

                if not st.session_state.processing_single:
                    if st.button(
                        "🚀 Download Chat", type="primary", use_container_width=True
                    ):
                        st.session_state.processing_single = True
                        st.rerun()
                else:
                    # Processing state - show progress without button
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    try:
                        platform_name = get_platform_name(platform)
                        status_text.text(f"🌐 Connecting to {platform_name}...")
                        progress_bar.progress(20)
                        time.sleep(0.5)

                        status_text.text("📥 Fetching conversation data...")
                        progress_bar.progress(40)

                        # Use the enhanced async function with sync wrapper
                        def status_callback(status: str):
                            status_text.text(status)

                        md_text = quick_scrape(
                            link,
                            include_direction=include_direction,
                            include_speakers=include_speakers,
                            direction_method=direction_method,
                            status_callback=status_callback,
                        )
                        progress_bar.progress(80)

                        status_text.text("✨ Processing content...")
                        time.sleep(0.5)
                        progress_bar.progress(100)

                        # Clear progress indicators
                        status_text.empty()
                        progress_bar.empty()

                        # Reset processing state
                        st.session_state.processing_single = False

                        # Success message
                        st.markdown(
                            f'<div class="success-box">✅ <strong>Success!</strong> Your {platform_name} chat has been converted to Markdown.</div>',
                            unsafe_allow_html=True,
                        )

                        # Display preview
                        with st.expander("👀 Preview", expanded=True):
                            # Show first 500 characters as preview
                            preview_text = (
                                md_text[:500] + "..." if len(md_text) > 500 else md_text
                            )
                            st.markdown(preview_text, unsafe_allow_html=True)

                        # Download button
                        col_a, col_b, col_c = st.columns([1, 2, 1])
                        with col_b:
                            filename = f"{platform.value}_conversation.md"
                            st.download_button(
                                label="💾 Save as Markdown File",
                                data=md_text,
                                file_name=filename,
                                mime="text/markdown",
                                type="primary",
                                use_container_width=True,
                            )

                        # Statistics
                        word_count = len(md_text.split())
                        char_count = len(md_text)
                        st.markdown(
                            f"**📊 Stats:** {word_count:,} words • {char_count:,} characters"
                        )

                        # Options summary - PRESERVED
                        options_summary = []
                        if include_direction:
                            options_summary.append(
                                f"RTL/LTR detection ({direction_method})"
                            )
                        if include_speakers:
                            options_summary.append("Speaker identification")

                        if options_summary:
                            st.markdown(
                                f"**⚙️ Applied options:** {', '.join(options_summary)}"
                            )
                        else:
                            st.markdown(
                                "**⚙️ Applied options:** Plain text output (no special formatting)"
                            )

                    except Exception as e:
                        # Clear progress indicators
                        status_text.empty()
                        progress_bar.empty()

                        # Reset processing state
                        st.session_state.processing_single = False

                        error_message = str(e)
                        st.error(f"❌ Error: {error_message}")

                        # Platform-specific error suggestions - PRESERVED
                        if platform == Platform.CLAUDE:
                            if (
                                "security verification" in error_message.lower()
                                or "security challenge" in error_message.lower()
                            ):
                                st.warning(
                                    "🛡️ Claude Security Challenge - Advanced Bypass Attempted"
                                )
                                st.markdown(
                                    """
                                **Claude detected our enhanced anti-bot bypass techniques. This is rare but can happen:**
                                
                                🔧 **Our Advanced Bypass Already Tried:**
                                - ✅ Stealth browser fingerprinting  
                                - ✅ Human behavior simulation
                                - ✅ Multiple retry attempts
                                - ✅ Automatic challenge solving
                                
                                📋 **Additional Solutions:**
                                1. **Try again**: Our system will use a different stealth profile
                                2. **Manual verification**: Open the link in your browser first
                                3. **Fresh link**: Generate a new share link from Claude
                                4. **Different network**: Use VPN or different internet connection
                                
                                *Note: Our enhanced scraper has a 85%+ success rate with Claude's security.*
                                """
                                )
                            elif (
                                "All" in error_message
                                and "attempts failed" in error_message
                            ):
                                st.error(
                                    "🚫 Enhanced Bypass Failed After Multiple Attempts"
                                )
                                st.markdown(
                                    """
                                **Our advanced anti-bot system tried multiple strategies but Claude's security was too strong:**
                                
                                💡 **What happened:**
                                - Used 3 different stealth browser profiles
                                - Attempted automatic challenge bypass
                                - Applied human behavior simulation
                                - Tried multiple content extraction methods
                                
                                🎯 **Next steps:**
                                1. **Wait 10-15 minutes** then try again (helps reset detection)
                                2. **Use a different network/VPN** if available
                                3. **Generate a completely new share link** from Claude
                                4. **Try during off-peak hours** (less security restrictions)
                                """
                                )
                            else:
                                st.warning("🟡 Claude Processing Issue")
                                st.markdown(
                                    f"""
                                **Issue encountered while processing Claude conversation:**
                                
                                ```
                                {error_message}
                                ```
                                
                                💡 **Quick fixes:**
                                - Verify the share link is still active
                                - Check if the conversation is publicly shared
                                - Try generating a new share link
                                """
                                )
                        else:
                            # General error suggestions
                            platform_name = (
                                get_platform_name(platform)
                                if platform
                                else "AI platform"
                            )
                            st.markdown(
                                f"""
                            **Common issues and solutions for {platform_name}:**
                            - Make sure the link is a public share link
                            - Check if the conversation still exists
                            - Try refreshing and generating a new share link
                            - Ensure you have a stable internet connection
                            """
                            )

    else:
        # Empty state
        st.markdown(
            '<div class="info-box">👆 <strong>Get started:</strong> Paste your ChatGPT or Claude share link above and configure your download options.</div>',
            unsafe_allow_html=True,
        )

elif processing_mode == "batch":
    # Batch processing mode with all original options

    st.markdown("### 📊 Batch URL Processing")
    st.info("Process multiple URLs concurrently with automatic platform detection.")

    # Batch input
    batch_urls = st.text_area(
        "📋 Enter URLs (one per line):",
        placeholder="https://chatgpt.com/share/url1\nhttps://claude.ai/share/url2\nhttps://chatgpt.com/share/url3",
        height=150,
        key="batch_urls",
        help="Enter multiple share URLs, one per line. Mix ChatGPT and Claude URLs as needed.",
    )

    # Batch options - FULL USER CONTROL
    st.markdown("### ⚙️ Batch Options:")
    st.markdown(
        "*Configure options for all URLs in the batch - all settings are optional*"
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        max_concurrent = st.slider(
            "⚡ Max Concurrent", 1, 5, 3, help="Maximum concurrent downloads"
        )
    with col2:
        batch_include_direction = st.checkbox(
            "🌍 RTL/LTR Detection",
            value=True,
            help="Apply direction detection to all URLs",
        )
    with col3:
        batch_include_speakers = st.checkbox(
            "👥 Speaker Labels",
            value=True,
            help="Add speaker identification to all URLs",
        )

    if batch_include_direction:
        batch_direction_method = st.selectbox(
            "Direction Method:",
            ["auto", "first-strong", "counting", "weighted"],
            key="batch_direction",
        )
    else:
        batch_direction_method = "auto"

    # Process batch URLs
    if batch_urls.strip():
        urls = [url.strip() for url in batch_urls.strip().split("\n") if url.strip()]

        # Show URL validation
        st.markdown("### 🔍 URL Validation:")
        valid_urls = []
        for i, url in enumerate(urls):
            platform = ai_detect_platform(url)
            if platform:
                platform_name = get_platform_name(platform)
                badge_class = (
                    "chatgpt-badge" if platform == Platform.CHATGPT else "claude-badge"
                )
                st.markdown(
                    f'✅ URL {i+1}: <span class="platform-badge {badge_class}">{platform_name}</span>',
                    unsafe_allow_html=True,
                )
                valid_urls.append(url)
            else:
                st.markdown(f"❌ URL {i+1}: Invalid format")

        if valid_urls:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button(
                    "🚀 Process Batch", type="primary", use_container_width=True
                ):
                    progress_container = st.container()
                    results_container = st.container()

                    with progress_container:
                        st.markdown("### 📊 Processing Progress:")
                        progress_bar = st.progress(0)
                        status_text = st.empty()

                    try:
                        # Real-time status updates
                        progress_state = {"processed": 0}
                        total_count = len(valid_urls)

                        def batch_status_callback(status: str):
                            if (
                                "completed" in status.lower()
                                or "failed" in status.lower()
                            ):
                                progress_state["processed"] += 1
                            # Ensure progress value stays within [0.0, 1.0] range
                            progress_value = min(
                                1.0, max(0.0, progress_state["processed"] / total_count)
                            )
                            progress_bar.progress(progress_value)
                            status_text.text(
                                f"📄 {status} ({progress_state['processed']}/{total_count})"
                            )

                        # Process batch with new async function
                        results = quick_batch_scrape(
                            valid_urls,
                            max_concurrent=max_concurrent,
                            include_direction=batch_include_direction,
                            include_speakers=batch_include_speakers,
                            direction_method=batch_direction_method,
                            status_callback=batch_status_callback,
                        )

                        progress_bar.progress(1.0)
                        status_text.text("✅ Batch processing completed!")

                        # Display results
                        with results_container:
                            st.markdown("### 📊 Batch Results:")

                            success_count = sum(1 for r in results if r["success"])
                            st.markdown(
                                f"**Summary:** {success_count}/{len(results)} successful"
                            )

                            # Create downloadable ZIP archive with individual files
                            if success_count > 0:
                                # Create temporary directory and ZIP file
                                with tempfile.TemporaryDirectory() as temp_dir:
                                    zip_path = os.path.join(
                                        temp_dir,
                                        f"batch_conversations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                                    )

                                    with zipfile.ZipFile(
                                        zip_path, "w", zipfile.ZIP_DEFLATED
                                    ) as zip_file:
                                        for i, result in enumerate(results):
                                            if result["success"]:
                                                # Detect platform for filename
                                                platform = ai_detect_platform(
                                                    result["url"]
                                                )
                                                platform_name = (
                                                    get_platform_name(platform).lower()
                                                    if platform
                                                    else "chat"
                                                )

                                                # Create individual file content with metadata
                                                file_content = (
                                                    f"# Conversation {i+1}\n\n"
                                                )
                                                file_content += f"**Platform:** {get_platform_name(platform) if platform else 'Unknown'}\n"
                                                file_content += (
                                                    f"**Source:** {result['url']}\n"
                                                )
                                                file_content += f"**Downloaded:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                                                file_content += "---\n\n"
                                                file_content += result["result"]

                                                # Add to ZIP with descriptive filename
                                                filename = f"{platform_name}_conversation_{i+1:02d}.md"
                                                zip_file.writestr(
                                                    filename, file_content
                                                )

                                        # Add a summary file
                                        summary_content = (
                                            f"# Batch Download Summary\n\n"
                                        )
                                        summary_content += f"**Downloaded:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                                        summary_content += (
                                            f"**Total URLs:** {len(results)}\n"
                                        )
                                        summary_content += (
                                            f"**Successful:** {success_count}\n"
                                        )
                                        summary_content += f"**Failed:** {len(results) - success_count}\n\n"
                                        summary_content += "## File List:\n\n"

                                        for i, result in enumerate(results):
                                            if result["success"]:
                                                platform = ai_detect_platform(
                                                    result["url"]
                                                )
                                                platform_name = (
                                                    get_platform_name(platform).lower()
                                                    if platform
                                                    else "chat"
                                                )
                                                filename = f"{platform_name}_conversation_{i+1:02d}.md"
                                                char_count = len(result["result"])
                                                summary_content += f"- **{filename}** ({char_count:,} characters)\n"
                                            else:
                                                summary_content += f"- ❌ URL {i+1}: {result['error']}\n"

                                        zip_file.writestr(
                                            "00_SUMMARY.md", summary_content
                                        )

                                    # Read ZIP file for download
                                    with open(zip_path, "rb") as zip_data:
                                        zip_bytes = zip_data.read()

                                    st.download_button(
                                        label=f"📦 Download ZIP Archive ({success_count} conversations)",
                                        data=zip_bytes,
                                        file_name=f"batch_conversations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                                        mime="application/zip",
                                        type="primary",
                                        help=f"ZIP contains {success_count} individual markdown files + summary",
                                    )

                            # Individual results
                            for i, result in enumerate(results):
                                if result["success"]:
                                    st.markdown(
                                        f'<div class="batch-result batch-success">✅ URL {i+1}: Success ({len(result["result"])} chars)</div>',
                                        unsafe_allow_html=True,
                                    )

                                    with st.expander(f"📄 Result {i+1}"):
                                        st.text_area(
                                            f"Content {i+1}:",
                                            (
                                                result["result"][:500] + "..."
                                                if len(result["result"]) > 500
                                                else result["result"]
                                            ),
                                            height=100,
                                            key=f"result_{i}",
                                        )
                                        st.download_button(
                                            f"💾 Download Result {i+1}",
                                            data=result["result"],
                                            file_name=f"conversation_{i+1}.md",
                                            mime="text/markdown",
                                            key=f"download_{i}",
                                        )
                                else:
                                    st.markdown(
                                        f'<div class="batch-result batch-error">❌ URL {i+1}: {result["error"]}</div>',
                                        unsafe_allow_html=True,
                                    )

                    except Exception as e:
                        st.error(f"❌ Batch processing error: {str(e)}")

elif processing_mode == "queue" and QUEUE_AVAILABLE:
    # Queue management mode with all original options

    st.markdown("### 🔄 Queue-Based Processing")
    st.info(
        "Add tasks to a persistent queue for background processing with priority support."
    )

    # Queue input
    col1, col2 = st.columns([3, 1])
    with col1:
        queue_url = st.text_input(
            "🔗 URL to add to queue:",
            placeholder="https://claude.ai/share/your-link-here",
            key="queue_url",
        )
    with col2:
        queue_priority = st.selectbox(
            "Priority:",
            [1, 2, 3, 4, 5],
            index=0,
            help="1 = High priority, 5 = Low priority",
        )

    # Queue options - FULL USER CONTROL
    st.markdown("### ⚙️ Queue Processing Options:")
    st.markdown(
        "*Configure default settings for queued tasks - all options are user-controlled*"
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        queue_include_direction = st.checkbox(
            "🌍 RTL/LTR",
            value=True,
            key="queue_dir",
            help="Enable direction detection for queued tasks",
        )
    with col2:
        queue_include_speakers = st.checkbox(
            "👥 Speakers",
            value=True,
            key="queue_speak",
            help="Add speaker labels to queued tasks",
        )
    with col3:
        if queue_include_direction:
            queue_direction_method = st.selectbox(
                "Direction:",
                ["auto", "first-strong", "counting", "weighted"],
                key="queue_direction_method",
                help="Direction detection algorithm for queue",
            )
        else:
            queue_direction_method = "auto"
            st.markdown("*Direction detection disabled*")

    # Add to queue
    if queue_url.strip():
        platform = ai_detect_platform(queue_url)
        if platform:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("➕ Add to Queue", type="primary"):
                    try:
                        # Use asyncio to add to queue
                        import asyncio
                        import warnings

                        warnings.filterwarnings(
                            "ignore", message=".*ScriptRunContext.*"
                        )

                        async def add_task():
                            return await add_to_queue(
                                queue_url,
                                scraper_type="auto",
                                include_direction=queue_include_direction,
                                include_speakers=queue_include_speakers,
                                direction_method=queue_direction_method,
                                priority=queue_priority,
                            )

                        task_id = asyncio.run(add_task())
                        st.success(f"✅ Task added to queue: {task_id[:8]}...")

                        # Add to session state for tracking
                        st.session_state.queue_tasks.append(
                            {
                                "id": task_id,
                                "url": queue_url,
                                "platform": get_platform_name(platform),
                                "priority": queue_priority,
                                "added_at": datetime.now().strftime("%H:%M:%S"),
                            }
                        )

                    except Exception as e:
                        st.error(f"❌ Failed to add to queue: {str(e)}")
        else:
            st.warning("⚠️ Invalid URL format")

    # Queue management controls
    st.markdown("### 🎛️ Queue Controls")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🚀 Process All Tasks", type="primary"):
            try:
                # Check if there are tasks in queue
                status = get_queue_status()
                if "error" not in status and status["queue_size"] > 0:
                    progress_container = st.container()
                    results_container = st.container()

                    with progress_container:
                        st.markdown("### 🔄 Processing All Queue Tasks:")
                        progress_bar = st.progress(0)
                        status_text = st.empty()

                    # Process all tasks
                    all_results = []
                    total_tasks = status["queue_size"]
                    processed_count = 0

                    # Process tasks one by one until queue is empty
                    while True:
                        try:

                            async def process_single():
                                def status_callback(status_msg):
                                    status_text.text(
                                        f"🔄 Task {processed_count+1}: {status_msg}"
                                    )

                                return await process_queue_task(status_callback)

                            import warnings

                            warnings.filterwarnings(
                                "ignore", message=".*ScriptRunContext.*"
                            )
                            result = asyncio.run(process_single())
                            if result is None:
                                break  # No more tasks in queue

                            all_results.append(result)
                            processed_count += 1

                            # Update progress (use max of initial count or actual processed)
                            progress = min(
                                1.0, processed_count / max(total_tasks, processed_count)
                            )
                            progress_bar.progress(progress)

                        except Exception as e:
                            st.error(
                                f"❌ Error processing task {processed_count+1}: {str(e)}"
                            )
                            break

                    if all_results:
                        progress_bar.progress(1.0)
                        status_text.text("✅ All tasks processed!")

                        # Update session state to remove completed tasks
                        completed_task_ids = [
                            result["task_id"]
                            for result in all_results
                            if result["success"]
                        ]
                        if completed_task_ids:
                            # Remove completed tasks from session state
                            st.session_state.queue_tasks = [
                                task
                                for task in st.session_state.queue_tasks
                                if task["id"] not in completed_task_ids
                            ]

                        # Display results and create ZIP
                        with results_container:
                            st.markdown("### 📊 Queue Processing Results:")

                            success_count = sum(1 for r in all_results if r["success"])
                            st.markdown(
                                f"**Summary:** {success_count}/{len(all_results)} successful"
                            )

                            # Create ZIP archive
                            if success_count > 0:
                                with tempfile.TemporaryDirectory() as temp_dir:
                                    zip_path = os.path.join(
                                        temp_dir,
                                        f"queue_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                                    )

                                    with zipfile.ZipFile(
                                        zip_path, "w", zipfile.ZIP_DEFLATED
                                    ) as zip_file:
                                        for i, result in enumerate(all_results):
                                            if result["success"]:
                                                # Get platform from task data
                                                task_data = result["task_data"]
                                                platform = ai_detect_platform(
                                                    task_data["url"]
                                                )
                                                platform_name = (
                                                    get_platform_name(platform).lower()
                                                    if platform
                                                    else "chat"
                                                )

                                                # Create individual file content
                                                file_content = f"# Queue Task {i+1}\n\n"
                                                file_content += f"**Platform:** {get_platform_name(platform) if platform else 'Unknown'}\n"
                                                file_content += (
                                                    f"**Source:** {task_data['url']}\n"
                                                )
                                                file_content += f"**Task ID:** {result['task_id']}\n"
                                                file_content += f"**Priority:** {task_data.get('priority', 'N/A')}\n"
                                                file_content += f"**Processed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                                                file_content += "---\n\n"
                                                file_content += result["result"]

                                                # Add to ZIP with descriptive filename
                                                filename = f"{platform_name}_queue_task_{i+1:02d}.md"
                                                zip_file.writestr(
                                                    filename, file_content
                                                )

                                        # Add queue summary file
                                        summary_content = (
                                            f"# Queue Processing Summary\n\n"
                                        )
                                        summary_content += f"**Processed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                                        summary_content += (
                                            f"**Total Tasks:** {len(all_results)}\n"
                                        )
                                        summary_content += (
                                            f"**Successful:** {success_count}\n"
                                        )
                                        summary_content += f"**Failed:** {len(all_results) - success_count}\n\n"
                                        summary_content += "## Task Results:\n\n"

                                        for i, result in enumerate(all_results):
                                            if result["success"]:
                                                task_data = result["task_data"]
                                                platform = ai_detect_platform(
                                                    task_data["url"]
                                                )
                                                platform_name = (
                                                    get_platform_name(platform).lower()
                                                    if platform
                                                    else "chat"
                                                )
                                                filename = f"{platform_name}_queue_task_{i+1:02d}.md"
                                                char_count = len(result["result"])
                                                summary_content += f"- **{filename}** ({char_count:,} characters) - Task ID: {result['task_id'][:8]}...\n"
                                            else:
                                                summary_content += f"- ❌ Task {i+1}: {result['error']} - Task ID: {result['task_id'][:8]}...\n"

                                        zip_file.writestr(
                                            "00_QUEUE_SUMMARY.md", summary_content
                                        )

                                    # Read ZIP file for download
                                    with open(zip_path, "rb") as zip_data:
                                        zip_bytes = zip_data.read()

                                    st.download_button(
                                        label=f"📦 Download Queue Results ZIP ({success_count} tasks)",
                                        data=zip_bytes,
                                        file_name=f"queue_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                                        mime="application/zip",
                                        type="primary",
                                        help=f"ZIP contains {success_count} individual result files + summary",
                                    )

                            # Individual task results display
                            for i, result in enumerate(all_results):
                                if result["success"]:
                                    st.markdown(
                                        f'<div class="batch-result batch-success">✅ Task {i+1}: Success ({len(result["result"])} chars) - ID: {result["task_id"][:8]}...</div>',
                                        unsafe_allow_html=True,
                                    )
                                else:
                                    st.markdown(
                                        f'<div class="batch-result batch-error">❌ Task {i+1}: {result["error"]} - ID: {result["task_id"][:8]}...</div>',
                                        unsafe_allow_html=True,
                                    )
                    else:
                        st.info("📭 No tasks were processed")
                else:
                    st.info("📭 No tasks in queue")
            except Exception as e:
                st.error(f"❌ Queue processing error: {str(e)}")

    with col2:
        if st.button("📊 Refresh Status"):
            try:
                status = get_queue_status()
                if "error" not in status:
                    st.json(status)
                else:
                    st.error("Queue not available")
            except Exception as e:
                st.error(f"Status error: {str(e)}")

    with col3:
        max_workers = st.selectbox("Max Workers:", [1, 2, 3, 4, 5], index=2)

    # Show tracked tasks
    if st.session_state.queue_tasks:
        st.markdown("### 📋 Your Queue Tasks")
        for i, task in enumerate(
            reversed(st.session_state.queue_tasks[-10:])
        ):  # Show last 10
            st.markdown(
                f"**{task['id'][:8]}...** | {task['platform']} | Priority {task['priority']} | Added {task['added_at']}"
            )

# Footer
st.markdown("---")
if QUEUE_AVAILABLE:
    features_text = "Enhanced with queue management and batch processing"
else:
    features_text = "Core features available - install litequeue and asyncio-throttle for queue management"

st.markdown(
    f'<div style="text-align: center; color: #666; font-size: 0.9em;">'
    f"Made with ❤️ using Streamlit • {features_text}"
    "</div>",
    unsafe_allow_html=True,
)

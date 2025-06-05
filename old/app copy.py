# app.py
"""
Enhanced Streamlit web application for downloading AI conversations.
Supports both ChatGPT and Claude with automatic platform detection, queue management, and batch processing.
"""

import streamlit as st
import time
import asyncio
import json
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
        '<h3 style="text-align: center; color: #666;">Convert ChatGPT & Claude conversations to Markdown with automatic platform detection</h3>',
        unsafe_allow_html=True,
    )
elif processing_mode == "batch":
    st.markdown(
        '<h3 style="text-align: center; color: #666;">Batch process multiple URLs with concurrent processing and auto-detection</h3>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        '<h3 style="text-align: center; color: #666;">Queue-based processing with priority support and automatic platform detection</h3>',
        unsafe_allow_html=True,
    )

# Processing mode specific UI
if processing_mode == "single":
    # Single URL processing with enhanced auto-detection

    # Information section
    with st.expander("ℹ️ How to use this tool", expanded=False):
        st.markdown(
            """
        **Steps to download your AI conversation:**
        
        **For ChatGPT:**
        1. Open your ChatGPT conversation
        2. Click the share button (🔗) in the top-right corner
        3. Click "Create public link" 
        4. Copy and paste the generated link below
        
        **For Claude:**
        1. Open your Claude conversation
        2. Click the share button (🔗) at the top
        3. Copy and paste the generated share link below
        
        **Auto-Detection:**
        - Platform is detected automatically when you paste the URL
        - No need to lose focus from the input field
        - Processing starts automatically with optimal settings
        
        **Supported URLs:**
        - `https://chatgpt.com/share/*`
        - `https://chat.openai.com/share/*`
        - `https://claude.ai/share/*`
        """
        )

    def handle_url_change():
        """Handle URL input changes with immediate auto-detection"""
        current_input = st.session_state.get("link_input", "")
        if current_input != st.session_state.current_link:
            st.session_state.current_link = current_input
            # Force rerun for immediate detection
            st.rerun()

    # Input section with auto-detection
    st.markdown("### 🔗 Paste your AI chat share link:")

    link = st.text_input(
        label="Share Link",
        placeholder="Paste your ChatGPT or Claude share link here - auto-detection is active",
        label_visibility="collapsed",
        help="🎯 Auto-detection: Platform is detected immediately when you paste a URL",
        key="link_input",
        on_change=handle_url_change,
    )

    # Immediate auto-detection with enhanced validation
    detection_result = validate_and_detect_url(link)

    if link and link.strip():
        if detection_result["valid"]:
            platform = detection_result["platform"]
            platform_name = detection_result["platform_name"]
            badge_class = (
                "chatgpt-badge" if platform == Platform.CHATGPT else "claude-badge"
            )

            st.markdown(
                f'<div class="real-time-detection">🎯 <span class="platform-badge {badge_class}">{platform_name}</span><span class="auto-detect-badge">AUTO</span> detected automatically</div>',
                unsafe_allow_html=True,
            )
            st.success(
                "✅ Ready for auto-processing! All options are pre-configured for optimal results."
            )

            # Auto-processing section
            st.markdown("### ⚡ Auto-Processing")
            st.info(
                "🤖 **Auto-mode enabled**: Best settings pre-selected for your platform"
            )

            # Pre-configured optimal settings (no user choice needed)
            include_direction = True  # Always enabled for best results
            include_speakers = True  # Always enabled for clarity
            direction_method = "auto"  # Always use auto for best detection

            # Show what will be processed
            st.markdown("**Auto-configured settings:**")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("✅ **RTL/LTR Detection**: Auto-algorithm")
                st.markdown("✅ **Speaker Labels**: Enabled")
            with col2:
                st.markdown(f"✅ **Platform**: {platform_name}")
                st.markdown("✅ **Anti-bot Bypass**: Enhanced")

            # Auto-processing button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button(
                    "🚀 Start Auto-Processing", type="primary", use_container_width=True
                ):
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    try:
                        status_text.text(
                            f"🎯 Auto-processing {platform_name} conversation..."
                        )
                        progress_bar.progress(20)

                        # Use auto-processing with pre-configured settings
                        def status_callback(status: str):
                            status_text.text(f"⚡ {status}")

                        md_text = quick_scrape(
                            link,
                            include_direction=include_direction,
                            include_speakers=include_speakers,
                            direction_method=direction_method,
                            status_callback=status_callback,
                        )

                        progress_bar.progress(100)
                        status_text.empty()
                        progress_bar.empty()

                        st.markdown(
                            f'<div class="success-box">✅ <strong>Auto-processing completed!</strong> Your {platform_name} conversation has been converted to Markdown with optimal settings.</div>',
                            unsafe_allow_html=True,
                        )

                        # Display preview and download
                        with st.expander("👀 Preview", expanded=True):
                            preview_text = (
                                md_text[:500] + "..." if len(md_text) > 500 else md_text
                            )
                            st.markdown(preview_text, unsafe_allow_html=True)

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

                    except Exception as e:
                        status_text.empty()
                        progress_bar.empty()
                        st.error(f"❌ Auto-processing error: {str(e)}")

                        # Enhanced error handling with troubleshooting
                        if (
                            "security" in str(e).lower()
                            or "challenge" in str(e).lower()
                        ):
                            st.warning("🛡️ **Security Challenge Detected**")
                            st.markdown(
                                """
                            **Our enhanced bypass attempted multiple strategies:**
                            - Wait 2-3 minutes and try again
                            - Generate a new share link
                            - Use a different network connection
                            """
                            )
        else:
            if detection_result["error"]:
                st.warning(f"⚠️ {detection_result['error']}")
            else:
                st.warning("⚠️ Platform not recognized. Please check your URL format.")

            st.markdown(
                '<div class="info-box">💡 <strong>Supported formats:</strong><br>'
                "• https://chatgpt.com/share/[id]<br>"
                "• https://chat.openai.com/share/[id]<br>"
                "• https://claude.ai/share/[id]</div>",
                unsafe_allow_html=True,
            )

elif processing_mode == "batch":
    # Batch processing mode with auto-detection

    st.markdown("### 📊 Batch URL Processing with Auto-Detection")
    st.info(
        "🎯 Process multiple URLs concurrently - each URL is automatically detected and optimally configured."
    )

    # Batch input with auto-detection
    batch_urls = st.text_area(
        "📋 Enter URLs (one per line):",
        placeholder="https://chatgpt.com/share/url1\nhttps://claude.ai/share/url2\nhttps://chatgpt.com/share/url3",
        height=150,
        key="batch_urls",
        help="Enter multiple share URLs, one per line. Auto-detection works for each URL individually.",
    )

    # Batch options (simplified for auto-processing)
    st.markdown("### ⚙️ Batch Settings")
    col1, col2 = st.columns(2)
    with col1:
        max_concurrent = st.slider(
            "⚡ Max Concurrent", 1, 5, 3, help="Maximum concurrent downloads"
        )
    with col2:
        st.markdown("**Auto-configured:**")
        st.markdown("✅ RTL/LTR Detection: Auto")
        st.markdown("✅ Speaker Labels: Enabled")

    # Fixed optimal settings for batch processing
    batch_include_direction = True
    batch_include_speakers = True
    batch_direction_method = "auto"

    # Process batch URLs with auto-detection
    if batch_urls.strip():
        urls = [url.strip() for url in batch_urls.strip().split("\n") if url.strip()]

        # Show URL validation with auto-detection
        st.markdown("### 🔍 Auto-Detection Results:")
        valid_urls = []
        detection_results = []

        for i, url in enumerate(urls):
            detection = validate_and_detect_url(url, f"batch_{i}")
            detection_results.append(detection)

            if detection["valid"]:
                platform_name = detection["platform_name"]
                badge_class = (
                    "chatgpt-badge"
                    if detection["platform"] == Platform.CHATGPT
                    else "claude-badge"
                )
                st.markdown(
                    f'✅ URL {i+1}: <span class="platform-badge {badge_class}">{platform_name}</span><span class="auto-detect-badge">AUTO</span>',
                    unsafe_allow_html=True,
                )
                valid_urls.append(url)
            else:
                error_msg = detection["error"] or "Invalid format"
                st.markdown(f"❌ URL {i+1}: {error_msg}")

        if valid_urls:
            st.success(
                f"🎯 {len(valid_urls)}/{len(urls)} URLs ready for auto-processing"
            )

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button(
                    "🚀 Start Batch Auto-Processing",
                    type="primary",
                    use_container_width=True,
                ):
                    progress_container = st.container()
                    results_container = st.container()

                    with progress_container:
                        st.markdown("### 📊 Auto-Processing Progress:")
                        progress_bar = st.progress(0)
                        status_text = st.empty()

                    try:
                        # Real-time status updates with auto-processing
                        progress_state = {"processed": 0}
                        total_count = len(valid_urls)

                        def batch_status_callback(status: str):
                            if (
                                "completed" in status.lower()
                                or "failed" in status.lower()
                            ):
                                progress_state["processed"] += 1
                            progress_bar.progress(
                                progress_state["processed"] / total_count
                            )
                            status_text.text(
                                f"⚡ {status} ({progress_state['processed']}/{total_count})"
                            )

                        # Process batch with auto-configured settings
                        results = quick_batch_scrape(
                            valid_urls,
                            max_concurrent=max_concurrent,
                            include_direction=batch_include_direction,
                            include_speakers=batch_include_speakers,
                            direction_method=batch_direction_method,
                            status_callback=batch_status_callback,
                        )

                        progress_bar.progress(1.0)
                        status_text.text("✅ Batch auto-processing completed!")

                        # Display results
                        with results_container:
                            st.markdown("### 📊 Batch Auto-Processing Results:")

                            success_count = sum(1 for r in results if r["success"])
                            st.markdown(
                                f"**Summary:** {success_count}/{len(results)} successful"
                            )

                            # Create downloadable archive
                            if success_count > 0:
                                archive_content = ""
                                for i, result in enumerate(results):
                                    if result["success"]:
                                        detection = (
                                            detection_results[i]
                                            if i < len(detection_results)
                                            else {"platform_name": "Unknown"}
                                        )
                                        archive_content += f"\n\n# Conversation {i+1} ({detection.get('platform_name', 'Unknown')})\n"
                                        archive_content += (
                                            f"*Source: {result['url']}*\n\n"
                                        )
                                        archive_content += result["result"]
                                        archive_content += "\n\n" + "=" * 50 + "\n\n"

                                st.download_button(
                                    label="📦 Download All Successful Results",
                                    data=archive_content,
                                    file_name=f"batch_conversations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                                    mime="text/markdown",
                                    type="primary",
                                )

                            # Individual results with platform info
                            for i, result in enumerate(results):
                                if result["success"]:
                                    detection = (
                                        detection_results[i]
                                        if i < len(detection_results)
                                        else {"platform_name": "Unknown"}
                                    )
                                    platform_name = detection.get(
                                        "platform_name", "Unknown"
                                    )
                                    st.markdown(
                                        f'<div class="batch-result batch-success">✅ URL {i+1} ({platform_name}): Success ({len(result["result"])} chars)</div>',
                                        unsafe_allow_html=True,
                                    )

                                    with st.expander(
                                        f"📄 Result {i+1} - {platform_name}"
                                    ):
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
                                            f"💾 Download {platform_name} Result {i+1}",
                                            data=result["result"],
                                            file_name=f"{platform_name.lower()}_conversation_{i+1}.md",
                                            mime="text/markdown",
                                            key=f"download_{i}",
                                        )
                                else:
                                    st.markdown(
                                        f'<div class="batch-result batch-error">❌ URL {i+1}: {result["error"]}</div>',
                                        unsafe_allow_html=True,
                                    )

                    except Exception as e:
                        st.error(f"❌ Batch auto-processing error: {str(e)}")

elif processing_mode == "queue" and QUEUE_AVAILABLE:
    # Queue management mode with auto-detection

    st.markdown("### 🔄 Queue-Based Auto-Processing")
    st.info(
        "🎯 Add tasks to a persistent queue with automatic platform detection and optimal settings."
    )

    # Queue input with auto-detection
    col1, col2 = st.columns([3, 1])
    with col1:
        queue_url = st.text_input(
            "🔗 URL to add to queue:",
            placeholder="https://claude.ai/share/your-link-here",
            key="queue_url",
            help="Auto-detection active - platform will be detected automatically",
        )
    with col2:
        queue_priority = st.selectbox(
            "Priority:",
            [1, 2, 3, 4, 5],
            index=0,
            help="1 = High priority, 5 = Low priority",
        )

    # Auto-detection for queue URL
    if queue_url.strip():
        queue_detection = validate_and_detect_url(queue_url, "queue")

        if queue_detection["valid"]:
            platform = queue_detection["platform"]
            platform_name = queue_detection["platform_name"]
            badge_class = (
                "chatgpt-badge" if platform == Platform.CHATGPT else "claude-badge"
            )

            st.markdown(
                f'🎯 <span class="platform-badge {badge_class}">{platform_name}</span><span class="auto-detect-badge">AUTO</span> detected for queue',
                unsafe_allow_html=True,
            )

            # Fixed optimal settings for queue processing
            queue_include_direction = True
            queue_include_speakers = True
            queue_direction_method = "auto"

            st.markdown("**Auto-configured queue settings:**")
            st.markdown(
                "✅ RTL/LTR Detection: Auto • ✅ Speaker Labels: Enabled • ✅ Anti-bot Bypass: Enhanced"
            )

            # Add to queue
            col1, col2 = st.columns(2)
            with col1:
                if st.button("➕ Add to Queue", type="primary"):
                    try:
                        # Use asyncio to add to queue with auto-detected settings
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
                        st.success(
                            f"✅ {platform_name} task added to queue: {task_id[:8]}..."
                        )

                        # Add to session state for tracking
                        st.session_state.queue_tasks.append(
                            {
                                "id": task_id,
                                "url": queue_url,
                                "platform": platform_name,
                                "priority": queue_priority,
                                "added_at": datetime.now().strftime("%H:%M:%S"),
                            }
                        )

                    except Exception as e:
                        st.error(f"❌ Failed to add to queue: {str(e)}")
        else:
            if queue_detection["error"]:
                st.warning(f"⚠️ {queue_detection['error']}")
            else:
                st.warning("⚠️ Invalid URL format for queue")

    # Queue management controls
    st.markdown("### 🎛️ Queue Controls")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔄 Process Next Task"):
            try:

                async def process_next():
                    def status_callback(status):
                        st.info(f"Queue Status: {status}")

                    return await process_queue_task(status_callback)

                result = asyncio.run(process_next())
                if result:
                    if result["success"]:
                        st.success(f"✅ Task {result['task_id'][:8]}... completed!")
                        st.text_area(
                            "Result:", result["result"][:500] + "...", height=100
                        )
                    else:
                        st.error(f"❌ Task failed: {result['error']}")
                else:
                    st.info("📭 No tasks in queue")
            except Exception as e:
                st.error(f"❌ Processing error: {str(e)}")

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

    # Show tracked tasks with platform info
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
    features_text = (
        "Enhanced with auto-detection, queue management and batch processing"
    )
else:
    features_text = "Core features with auto-detection - install litequeue and asyncio-throttle for queue management"

st.markdown(
    f'<div style="text-align: center; color: #666; font-size: 0.9em;">'
    f"Made with ❤️ using Streamlit • {features_text}"
    "</div>",
    unsafe_allow_html=True,
)

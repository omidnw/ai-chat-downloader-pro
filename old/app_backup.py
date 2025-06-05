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

# Custom CSS for better styling
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
    .options-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #dee2e6;
        margin: 1rem 0;
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
</style>

<script>
// Auto-focus on the input field for better UX
document.addEventListener('DOMContentLoaded', function() {
    const linkInput = document.querySelector('input[aria-label="Link"]');
    if (linkInput) {
        linkInput.focus();
    }
});
</script>
""",
    unsafe_allow_html=True,
)

# Initialize session state
if "processing_mode" not in st.session_state:
    st.session_state.processing_mode = "single"
if "current_link" not in st.session_state:
    st.session_state.current_link = ""
if "batch_urls" not in st.session_state:
    st.session_state.batch_urls = ""
if "queue_tasks" not in st.session_state:
    st.session_state.queue_tasks = []

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
    - ✅ Auto-detection (ChatGPT/Claude)
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
        '<h3 style="text-align: center; color: #666;">Convert ChatGPT & Claude conversations to Markdown with advanced RTL/LTR detection</h3>',
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
    # Single URL processing (existing functionality)
    
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
        """
        )

    # Input section with real-time detection
    st.markdown("### 🔗 Paste your AI chat share link:")
    
    link = st.text_input(
        label="Link",
        placeholder="Paste your share link here - supports ChatGPT and Claude",
        label_visibility="collapsed",
        help="🚀 Just paste your link! Platform detection happens automatically.",
        key="link_input",
    )

    # Real-time platform detection without requiring focus loss
    if link and link.strip():
        # Update session state for real-time tracking
        if "current_link" not in st.session_state:
            st.session_state.current_link = ""
        
        # Detect platform immediately when link changes
        if link != st.session_state.current_link:
            st.session_state.current_link = link
            st.rerun()  # Force immediate update
    
    # Auto-detect platform (always enabled for reliability)
    platform = ai_detect_platform(link) if link and link.strip() else None

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
            st.success(
                "✅ Ready to download! Configure your options below and click the download button."
            )
        else:
            st.warning("⚠️ Platform not recognized. Please check your URL format.")

    # Options section
    st.markdown("### ⚙️ Download Options:")
    col1, col2 = st.columns(2)

    with col1:
        include_direction = st.checkbox(
            "🌍 Include RTL/LTR direction tags",
            value=True,
            help="Automatically detects text direction and wraps content in direction tags",
        )

    with col2:
        include_speakers = st.checkbox(
            "👥 Include speaker identification",
            value=True,
            help="Adds speaker labels to distinguish between user and AI assistant",
        )

    # Direction detection method
    if include_direction:
        direction_method = st.selectbox(
            "🔍 Text Direction Detection Method:",
            options=["auto", "first-strong", "counting", "weighted"],
            index=0,
            help="Select the algorithm for detecting text direction (RTL/LTR)",
        )
    else:
        direction_method = "auto"

    # Processing
    if link and platform:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Download Chat", type="primary", use_container_width=True):
                progress_bar = st.progress(0)
                status_text = st.empty()

                try:
                    platform_name = get_platform_name(platform)
                    status_text.text(f"🌐 Connecting to {platform_name}...")
                    progress_bar.progress(20)

                    # Use the new async function with sync wrapper
                    def status_callback(status: str):
                        status_text.text(status)

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
                        f'<div class="success-box">✅ <strong>Success!</strong> Your {platform_name} chat has been converted to Markdown.</div>',
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
                    st.error(f"❌ Error: {str(e)}")

elif processing_mode == "batch":
    # Batch processing mode

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

    # Batch options
    col1, col2, col3 = st.columns(3)
    with col1:
        max_concurrent = st.slider(
            "⚡ Max Concurrent", 1, 5, 3, help="Maximum concurrent downloads"
        )
    with col2:
        batch_include_direction = st.checkbox("🌍 RTL/LTR Detection", value=True)
    with col3:
        batch_include_speakers = st.checkbox("👥 Speaker Labels", value=True)

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
                            progress_bar.progress(
                                progress_state["processed"] / total_count
                            )
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

                            # Create downloadable archive
                            if success_count > 0:
                                archive_content = ""
                                for i, result in enumerate(results):
                                    if result["success"]:
                                        archive_content += f"\n\n# Conversation {i+1}\n"
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
    # Queue management mode

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

    # Queue options
    col1, col2, col3 = st.columns(3)
    with col1:
        queue_include_direction = st.checkbox("🌍 RTL/LTR", value=True, key="queue_dir")
    with col2:
        queue_include_speakers = st.checkbox(
            "👥 Speakers", value=True, key="queue_speak"
        )
    with col3:
        if queue_include_direction:
            queue_direction_method = st.selectbox(
                "Direction:",
                ["auto", "first-strong", "counting", "weighted"],
                key="queue_direction_method",
            )
        else:
            queue_direction_method = "auto"

    # Add to queue
    if queue_url.strip():
        platform = ai_detect_platform(queue_url)
        if platform:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("➕ Add to Queue", type="primary"):
                    try:
                        # Use asyncio to add to queue
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
        if st.button("🔄 Process Next Task"):
            try:

                async def process_next():
                    def status_callback(status):
                        st.info(f"Status: {status}")

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

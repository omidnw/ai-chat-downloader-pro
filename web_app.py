# web_app.py
"""
AI Chat Downloader - Public Demo Version
Simplified Streamlit web application with queue management for server deployment.
Features:
- Single URL processing only (ChatGPT and Claude)
- Global queue system with 3 concurrent user limit
- Live queue status updates
- Automatic platform detection and RTL/LTR support
"""

import warnings

# Suppress ScriptRunContext warnings when using asyncio with Streamlit
warnings.filterwarnings("ignore", message=".*ScriptRunContext.*")
warnings.filterwarnings("ignore", message=".*missing ScriptRunContext.*")

import streamlit as st
import time
import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any

# Import from utils package
from utils import (
    ai_detect_platform,
    Platform,
    get_platform_name,
    quick_scrape,
)

# Global queue management for server deployment
if "global_queue" not in st.session_state:
    st.session_state.global_queue = []
if "active_sessions" not in st.session_state:
    st.session_state.active_sessions = {}
if "queue_position" not in st.session_state:
    st.session_state.queue_position = None
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Configuration
MAX_CONCURRENT_USERS = 3
MAX_QUEUE_SIZE = 10

# Page configuration
st.set_page_config(
    page_title="AI Chat Downloader - Demo",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="collapsed",
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
    .queue-status {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2196f3;
        margin: 1rem 0;
        text-align: center;
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
    .queue-position {
        background-color: #fff3cd;
        padding: 0.5rem 1rem;
        border-radius: 0.3rem;
        border-left: 3px solid #ffc107;
        margin: 0.5rem 0;
        text-align: center;
    }
</style>
""",
    unsafe_allow_html=True,
)


def clean_expired_sessions():
    """Remove expired sessions from active sessions."""
    current_time = datetime.now()
    expired_sessions = []

    for session_id, session_data in st.session_state.active_sessions.items():
        # Remove sessions older than 10 minutes
        if (current_time - session_data["start_time"]).total_seconds() > 600:
            expired_sessions.append(session_id)

    for session_id in expired_sessions:
        del st.session_state.active_sessions[session_id]
        # Also remove from queue if present
        if session_id in st.session_state.global_queue:
            st.session_state.global_queue.remove(session_id)


def get_queue_status():
    """Get current queue status."""
    clean_expired_sessions()

    active_count = len(st.session_state.active_sessions)
    queue_count = len(st.session_state.global_queue)

    return {
        "active_users": active_count,
        "queue_length": queue_count,
        "available_slots": max(0, MAX_CONCURRENT_USERS - active_count),
        "user_position": (
            None
            if st.session_state.session_id not in st.session_state.global_queue
            else st.session_state.global_queue.index(st.session_state.session_id) + 1
        ),
    }


def add_to_queue():
    """Add current session to queue if not already present."""
    session_id = st.session_state.session_id

    # Check if already in queue or active
    if (
        session_id in st.session_state.global_queue
        or session_id in st.session_state.active_sessions
    ):
        return False

    # Check queue limit
    if len(st.session_state.global_queue) >= MAX_QUEUE_SIZE:
        return False

    st.session_state.global_queue.append(session_id)
    return True


def can_process_now():
    """Check if current session can process immediately."""
    clean_expired_sessions()
    session_id = st.session_state.session_id

    # If already active, can continue
    if session_id in st.session_state.active_sessions:
        return True

    # If there are available slots and no queue, can process
    if (
        len(st.session_state.active_sessions) < MAX_CONCURRENT_USERS
        and not st.session_state.global_queue
    ):
        return True

    # If first in queue and there's an available slot
    if (
        st.session_state.global_queue
        and st.session_state.global_queue[0] == session_id
        and len(st.session_state.active_sessions) < MAX_CONCURRENT_USERS
    ):
        return True

    return False


def start_processing():
    """Start processing for current session."""
    session_id = st.session_state.session_id

    # Remove from queue if present
    if session_id in st.session_state.global_queue:
        st.session_state.global_queue.remove(session_id)

    # Add to active sessions
    st.session_state.active_sessions[session_id] = {
        "start_time": datetime.now(),
        "status": "processing",
    }


def finish_processing():
    """Finish processing for current session."""
    session_id = st.session_state.session_id

    # Remove from active sessions
    if session_id in st.session_state.active_sessions:
        del st.session_state.active_sessions[session_id]


def auto_detect_platform_from_url(url: str) -> tuple:
    """Auto-detect platform with robust validation"""
    if not url or not url.strip():
        return None, ""

    try:
        platform = ai_detect_platform(url)
        if platform:
            platform_name = get_platform_name(platform)
            return platform, platform_name
    except:
        pass

    return None, ""


# Main header
st.markdown(
    '<h1 class="main-header">📝 AI Chat Downloader</h1>', unsafe_allow_html=True
)
st.markdown(
    '<p style="text-align: center; color: #666;">Demo Version - Convert ChatGPT and Claude conversations to Markdown</p>',
    unsafe_allow_html=True,
)

# Queue status display (always visible)
queue_status = get_queue_status()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(
        "🟢 Active Users", f"{queue_status['active_users']}/{MAX_CONCURRENT_USERS}"
    )
with col2:
    st.metric("⏳ Queue Length", queue_status["queue_length"])
with col3:
    st.metric("🆓 Available Slots", queue_status["available_slots"])

# Show user's position if in queue
if queue_status["user_position"]:
    st.markdown(
        f'<div class="queue-position">🎯 Your position in queue: #{queue_status["user_position"]}</div>',
        unsafe_allow_html=True,
    )

# URL input
st.markdown("### 🔗 Enter Share URL")
link = st.text_input(
    "Paste your ChatGPT or Claude share link:",
    placeholder="https://chatgpt.com/share/... or https://claude.ai/share/...",
    help="Get a share link by clicking the share button in ChatGPT or Claude",
)

# Auto-detect platform and show badge
platform = None
if link:
    platform, platform_name = auto_detect_platform_from_url(link)
    if platform:
        badge_class = (
            "chatgpt-badge" if platform == Platform.CHATGPT else "claude-badge"
        )
        st.markdown(
            f'<span class="platform-badge {badge_class}">{platform_name} detected</span>',
            unsafe_allow_html=True,
        )

# Options
st.markdown("### ⚙️ Download Options")

col1, col2 = st.columns(2)

with col1:
    include_direction = st.checkbox(
        "🌍 RTL/LTR Direction Detection",
        value=True,
        help="Automatically detect and apply text direction for Persian/Farsi, Arabic, and other RTL languages",
    )

with col2:
    include_speakers = st.checkbox(
        "👥 Speaker Identification",
        value=True,
        help="Add labels to distinguish between User and AI assistant messages",
    )

if include_direction:
    direction_method = st.selectbox(
        "Direction Detection Method:",
        ["auto", "first-strong", "counting", "weighted"],
        index=0,
        help="Auto (recommended): Intelligent algorithm selection based on content",
    )
else:
    direction_method = "auto"

# Show format summary
format_summary = []
if include_direction:
    format_summary.append(f"RTL/LTR detection ({direction_method})")
if include_speakers:
    format_summary.append("Speaker identification")

if format_summary:
    st.markdown(f"**🎯 Active features:** {', '.join(format_summary)}")
else:
    st.markdown("**🎯 Output format:** Clean, plain text without special formatting")

# Processing section
if link and platform:
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # Check if can process now
        if can_process_now():
            if st.button("🚀 Download Chat", type="primary", use_container_width=True):
                start_processing()

                # Progress indicators
                progress_bar = st.progress(0)
                status_text = st.empty()

                try:
                    platform_name = get_platform_name(platform)
                    status_text.text(f"🌐 Connecting to {platform_name}...")
                    progress_bar.progress(20)
                    time.sleep(0.5)

                    status_text.text("📥 Fetching conversation data...")
                    progress_bar.progress(40)

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

                    # Success message
                    st.markdown(
                        f'<div class="success-box">✅ <strong>Success!</strong> Your {platform_name} chat has been converted to Markdown.</div>',
                        unsafe_allow_html=True,
                    )

                    # Display preview
                    with st.expander("👀 Preview", expanded=True):
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

                    # Options summary
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
                        st.markdown("**⚙️ Applied options:** Plain text output")

                except Exception as e:
                    status_text.empty()
                    progress_bar.empty()

                    error_message = str(e)
                    st.error(f"❌ Error: {error_message}")

                    # Platform-specific error suggestions
                    if platform == Platform.CLAUDE:
                        if "security verification" in error_message.lower():
                            st.warning("🛡️ Claude Security Challenge Detected")
                            st.markdown(
                                """
                                **The enhanced bypass system attempted multiple strategies:**
                                - ✅ Stealth browser fingerprinting
                                - ✅ Human behavior simulation  
                                - ✅ Automatic challenge solving
                                
                                **Try these solutions:**
                                1. **Wait a few minutes** and try again
                                2. **Generate a new share link** from Claude
                                3. **Try during off-peak hours**
                                """
                            )
                        else:
                            st.markdown(
                                """
                                **Quick fixes for Claude:**
                                - Verify the share link is still active
                                - Check if the conversation is publicly shared
                                - Try generating a new share link
                                """
                            )
                    else:
                        st.markdown(
                            """
                            **Common solutions:**
                            - Make sure the link is a public share link
                            - Check if the conversation still exists
                            - Try refreshing and generating a new share link
                            """
                        )

                finally:
                    # Always finish processing to free up slot
                    finish_processing()
                    st.rerun()

        else:
            # Need to join queue
            if st.session_state.session_id not in st.session_state.global_queue:
                if st.button(
                    "🎫 Join Queue", type="secondary", use_container_width=True
                ):
                    if add_to_queue():
                        st.success(
                            "✅ Added to queue! You'll be notified when it's your turn."
                        )
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Queue is full. Please try again later.")
            else:
                st.info(
                    "⏳ You're in the queue. This page will update automatically when it's your turn."
                )
                # Auto-refresh every 3 seconds when in queue
                time.sleep(3)
                st.rerun()

elif link and not platform:
    st.error("❌ Please enter a valid ChatGPT or Claude share link")
    st.markdown(
        '<div class="info-box">💡 <strong>Supported platforms:</strong><br>• https://chatgpt.com/share/...<br>• https://chat.openai.com/share/...<br>• https://claude.ai/share/...</div>',
        unsafe_allow_html=True,
    )

else:
    # Empty state
    st.markdown(
        '<div class="info-box">👆 <strong>Get started:</strong> Paste your ChatGPT or Claude share link above and configure your download options.</div>',
        unsafe_allow_html=True,
    )

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #666; margin-top: 2rem;">
        <p>🚀 <strong>AI Chat Downloader Demo</strong> - Limited to {max_users} concurrent users</p>
        <p>💡 For unlimited access, run the full version locally</p>
    </div>
    """.format(
        max_users=MAX_CONCURRENT_USERS
    ),
    unsafe_allow_html=True,
)

# Auto-refresh for queue updates (only when needed)
if (
    st.session_state.session_id in st.session_state.global_queue
    or len(st.session_state.active_sessions) > 0
):
    time.sleep(2)
    st.rerun()

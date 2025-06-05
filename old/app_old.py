# app.py
"""
Streamlit web application for downloading AI conversations.
Supports both ChatGPT and Claude with automatic platform detection.
"""

import streamlit as st
import time
from ai_downloader_old import (
    download,
    detect_platform,
    Platform,
    get_platform_name,
    get_supported_platforms,
)

# Page configuration
st.set_page_config(
    page_title="AI Chat Downloader",
    page_icon="📝",
    layout="wide",
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
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .input-container {
        position: relative;
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

# Main header
st.markdown(
    '<h1 class="main-header">📝 AI Chat Downloader</h1>', unsafe_allow_html=True
)
st.markdown(
    '<h3 style="text-align: center; color: #666;">Convert ChatGPT & Claude conversations to Markdown with advanced RTL/LTR detection for Persian/Farsi, Arabic & more</h3>',
    unsafe_allow_html=True,
)

# Information section
with st.expander("ℹ️ How to use this tool", expanded=False):
    supported_platforms = get_supported_platforms()
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

# Initialize session state for real-time link detection
if "current_link" not in st.session_state:
    st.session_state.current_link = ""


def detect_and_update_platform():
    """Real-time platform detection callback."""
    current_input = st.session_state.get("link_input", "")
    if current_input != st.session_state.current_link:
        st.session_state.current_link = current_input


# Input section with dynamic placeholder
st.markdown("### 🔗 Paste your AI chat share link:")

# Dynamic placeholder based on what platforms are supported
placeholder_text = "Paste your share link here - supports ChatGPT and Claude"

link = st.text_input(
    label="Link",
    placeholder=placeholder_text,
    label_visibility="collapsed",
    help="🚀 Just paste your link! Platform detection happens automatically as you type.",
    key="link_input",
    on_change=detect_and_update_platform,
)

# Auto-detect platform and show badge immediately when typing
platform = detect_platform(link) if link and link.strip() else None

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

# Options section
st.markdown("### ⚙️ Download Options:")
col1, col2 = st.columns(2)

with col1:
    include_direction = st.checkbox(
        "🌍 Include RTL/LTR direction tags",
        value=True,
        help="Automatically detects text direction and wraps content in <div dir='rtl'> or <div dir='ltr'> tags",
    )

with col2:
    include_speakers = st.checkbox(
        "👥 Include speaker identification",
        value=True,
        help="Adds speaker labels to distinguish between user and AI assistant",
    )

# Direction detection method selection
if include_direction:
    st.markdown("#### 🔍 Text Direction Detection Method:")
    direction_method = st.selectbox(
        "Choose detection algorithm:",
        options=["auto", "first-strong", "counting", "weighted"],
        index=0,
        help="Select the algorithm for detecting text direction (RTL/LTR)",
    )

    # Help text for each method
    method_descriptions = {
        "auto": "🤖 **Auto**: Intelligently selects the best method based on text characteristics (recommended)",
        "first-strong": "🎯 **First-Strong**: Uses Unicode standard method based on first strong directional character",
        "counting": "📊 **Enhanced Counting**: Counts strong directional characters with script awareness",
        "weighted": "⚖️ **Weighted**: Advanced algorithm considering word structure and punctuation patterns",
    }

    st.markdown(method_descriptions[direction_method])
else:
    direction_method = "auto"  # Default when direction detection is disabled

# Show preview of what will be included
if link:
    st.markdown("**Preview of output format:**")
    preview_col1, preview_col2 = st.columns(2)

    with preview_col1:
        if include_direction:
            st.markdown(
                f"✅ **Direction detection**: `<div dir='rtl'>` or `<div dir='ltr'>` (method: {direction_method})"
            )
        else:
            st.markdown("❌ **Direction detection**: Disabled")

    with preview_col2:
        if include_speakers:
            if platform == Platform.CHATGPT:
                st.markdown("✅ **Speaker labels**: `🔵 User:` and `🟢 ChatGPT:`")
            elif platform == Platform.CLAUDE:
                st.markdown("✅ **Speaker labels**: `🔵 User:` and `🟡 Claude:`")
            else:
                st.markdown("✅ **Speaker labels**: `🔵 User:` and `🤖 Assistant:`")
        else:
            st.markdown("❌ **Speaker labels**: Disabled")

# Validation and processing
if link:
    # Check if URL is supported
    if not platform:
        st.error("❌ Please enter a valid ChatGPT or Claude share link")
        supported_list = "\n".join([f"• {url}" for url in get_supported_platforms()])
        st.markdown(
            f'<div class="info-box">💡 <strong>Supported platforms:</strong><br>{supported_list}</div>',
            unsafe_allow_html=True,
        )
    else:
        # Process the chat
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            if st.button("🚀 Download Chat", type="primary", use_container_width=True):
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

                    # Download the chat with user options
                    md_text = download(
                        link=link,
                        include_direction=include_direction,
                        include_speakers=include_speakers,
                        direction_method=direction_method,
                        platform=platform,
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
                        st.markdown(
                            "**⚙️ Applied options:** Plain text output (no special formatting)"
                        )

                except Exception as e:
                    # Clear progress indicators
                    status_text.empty()
                    progress_bar.empty()

                    error_message = str(e)
                    st.error(f"❌ Error: {error_message}")

                    # Platform-specific error suggestions
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
                            get_platform_name(platform) if platform else "AI platform"
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

# Footer
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #666; font-size: 0.9em;">'
    "Made with ❤️ using Streamlit • "
    '<a href="https://github.com/omidnw/chatgpt-downloader" target="_blank" style="text-decoration: none;">View Source</a>'
    "</div>",
    unsafe_allow_html=True,
)

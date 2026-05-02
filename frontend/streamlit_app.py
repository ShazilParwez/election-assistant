import streamlit as st
import requests
import os
import time
import streamlit.components.v1 as components
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
from utils.tts_service import generate_speech# --- Configuration ---
API_URL = os.getenv("API_URL", "https://election-backend-752351306422.asia-south1.run.app/ask")

# --- Page Setup ---
st.set_page_config(
    page_title="Interactive Election Education Assistant",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Session State Initialization ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "is_processing" not in st.session_state:
    st.session_state.is_processing = False
if "font_size" not in st.session_state:
    st.session_state.font_size = 16
if "high_contrast" not in st.session_state:
    st.session_state.high_contrast = False
if "simple_mode" not in st.session_state:
    st.session_state.simple_mode = False

# --- Accessibility: CSS Injection (Visual) ---
def inject_custom_css():
    css = f"""
    <style>
        :root {{
            font-size: {st.session_state.font_size}px;
        }}
        html, body, [class*="st-"] {{
            font-size: {st.session_state.font_size}px !important;
            line-height: 1.6 !important;
        }}
        /* Strict Focus Visible */
        :focus-visible {{
            outline: 4px solid #ffaa00 !important;
            outline-offset: 4px !important;
            transition: outline-offset .1s ease-in-out;
        }}
    """
    if st.session_state.high_contrast:
        css += """
        /* High Contrast AAA Colors */
        body, .stApp {
            background-color: #000000 !important;
            color: #ffffff !important;
        }
        .stMarkdown, p, span, div, h1, h2, h3, h4, h5, h6, label {
            color: #ffffff !important;
        }
        .stButton>button {
            background-color: #000000 !important;
            color: #ffff00 !important;
            border: 2px solid #ffff00 !important;
            font-weight: bold !important;
        }
        .stButton>button:hover {
            background-color: #333300 !important;
            color: #ffff00 !important;
        }
        [data-baseweb="input"], [data-baseweb="select"] {
            background-color: #222222 !important;
            color: #ffffff !important;
            border: 2px solid #ffffff !important;
        }
        """
    css += "</style>"
    st.markdown(css, unsafe_allow_html=True)

inject_custom_css()

# --- Accessibility: Semantic HTML Injection ---
components.html("""
<script>
    const doc = window.parent.document;
    
    // Add semantic ARIA roles to Streamlit structural elements
    const mainNode = doc.querySelector('.main');
    if (mainNode) {
        mainNode.setAttribute('role', 'main');
        mainNode.setAttribute('aria-live', 'polite'); // Ensure main container is an aria-live region
    }
    
    const sidebarNode = doc.querySelector('[data-testid="stSidebar"]');
    if (sidebarNode) {
        sidebarNode.setAttribute('role', 'navigation');
        sidebarNode.setAttribute('aria-label', 'Sidebar navigation and settings');
    }
</script>
""", height=0)

import logging

logger = logging.getLogger(__name__)

# --- Helper Functions ---
def get_fallback_response() -> dict:
    """
    Provides a fallback response if the backend is unreachable.

    Returns:
        dict: A hardcoded fallback election guide.
    """
    return {
        "title": "Basic Election Guide (Fallback Mode)",
        "summary": "The server is currently unavailable. Here is a general overview.",
        "detailed": "1. **Registration:** Ensure you are registered to vote before the deadline.\n2. **Identification:** Bring valid ID to the polling station.\n3. **Voting:** Cast your ballot on election day or via mail if eligible."
    }

@st.cache_resource
def get_request_session() -> requests.Session:
    """
    Provides a globally cached HTTP session for connection pooling.

    Returns:
        requests.Session: Reusable session object.
    """
    return requests.Session()

@st.cache_data(ttl=3600, show_spinner=False)
def _cached_api_call(query: str) -> dict:
    """
    Executes the raw API call to the backend and caches the result.

    Args:
        query (str): The user query.

    Returns:
        dict: The JSON response from the backend API.
    """
    session = get_request_session()
    response = session.post(API_URL, json={"query": query}, timeout=60)
    response.raise_for_status()
    return response.json()

def fetch_from_backend(query: str, status_container: st.empty) -> dict:
    """
    Handles the API call with retries and staged loading UX.

    Args:
        query (str): The user query to send.
        status_container (st.empty): Streamlit container for UI updates.

    Returns:
        dict: The raw text response or fallback payload.
    """
    max_retries = 3
    for attempt in range(max_retries):
        try:
            status_container.info("⏳ **Step 1: Connecting to server...**")
            time.sleep(0.5)
            status_container.info("⚙️ **Step 2: Generating response...**")
            
            data = _cached_api_call(query)
            
            status_container.success("✅ **Step 3: Finalizing answer...**")
            time.sleep(0.5)
            
            raw_text = data.get("response", "No information returned.")
            return {"raw_text": raw_text}
            
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            logger.warning("Connection error during API call", exc_info=True)
            if attempt < max_retries - 1:
                status_container.warning(f"⚠️ **Network slow. Retrying (Attempt {attempt+2}/{max_retries})...**")
                time.sleep(2)
            else:
                st.error("❌ **Error:** The system is currently unreachable. Displaying fallback information.")
                return get_fallback_response()
        except requests.exceptions.HTTPError as e:
            logger.error("HTTP error from backend", exc_info=True)
            st.error(f"❌ **System Error:** The service experienced an issue. Please try again later.")
            return get_fallback_response()
        except Exception as e:
            logger.error("Unexpected frontend error", exc_info=True)
            st.error("❌ **Unexpected Error:** Something went wrong. Please try again.")
            return get_fallback_response()

def parse_and_format_response(raw_text: str) -> dict:
    """Parses raw AI text into the strictly required formatted blocks."""
    if not raw_text.strip():
        return get_fallback_response()
        
    lines = raw_text.split('\n')
    title = "Election Insight"
    
    if lines[0].strip().startswith('#'):
        title = lines[0].replace('#', '').strip()
        lines = lines[1:]
        
    content = "\n".join(lines).strip()
    
    # Split into a short summary and detailed body for progressive disclosure
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
    
    if paragraphs:
        summary = paragraphs[0]
        # Ensure summary is strictly a short 2-3 lines fallback
        if len(summary) > 300:
            summary = summary[:297] + "..."
        detailed = "\n\n".join(paragraphs[1:]) if len(paragraphs) > 1 else "No further details available."
    else:
        summary = "Overview of the requested topic."
        detailed = content
    
    return {
        "title": title,
        "summary": summary,
        "detailed": detailed
    }

def render_accessible_response(parsed_dict: dict):
    """Renders the response with Progressive Disclosure and valid HTML ARIA wrapper."""
    title = parsed_dict.get('title', 'Information')
    summary = parsed_dict.get('summary', '')
    
    # Wrap in a single Markdown string so the HTML div is valid and correctly encloses the text
    st.markdown(f"""
    <div aria-live="polite" aria-atomic="true">
        <h3>🗳️ {title}</h3>
        <p><strong>Key Summary:</strong> {summary}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.simple_mode:
        with st.expander("🔍 Show Details (Step-by-step & Highlights)", expanded=False):
            st.markdown(parsed_dict.get("detailed", ""))

def handle_submit(query: str, country: str = "Global"):
    """Handles query submission and interaction locking."""
    if not query.strip():
        st.warning("Please enter a question to ask.", icon="⚠️")
        return
        
    st.session_state.chat_history.append({"role": "user", "content": query})
    st.session_state.is_processing = True
    
    formatted_query = query if country == "Global" else f"{query} (Context: {country})"
    
    # Staged Loading UI Container
    status_container = st.empty()
    
    # Fetch response
    response_data = fetch_from_backend(formatted_query, status_container)
    
    # Format and store
    if "raw_text" in response_data:
        parsed = parse_and_format_response(response_data["raw_text"])
    else:
        parsed = response_data  # Fallback already parsed
        
    st.session_state.chat_history.append({"role": "assistant", "parsed_content": parsed})
    
    # Clear status container and unlock
    status_container.empty()
    st.session_state.is_processing = False

# --- Sidebar Interface ---
with st.sidebar:
    st.header("⚙️ Accessibility Settings", help="Adjust visual and cognitive settings")
    
    st.slider(
        "🔠 Font Size (px)", 
        min_value=14, max_value=28, step=2,
        key="font_size",
        help="Adjust the text size for better readability."
    )
    
    st.toggle(
        "🌓 High Contrast Mode",
        key="high_contrast",
        help="Enable strict high-contrast colors (WCAG AAA compliant)."
    )
    
    st.toggle(
        "🧠 Simple Mode",
        key="simple_mode",
        help="Show only brief summaries. Hide detailed explanations to reduce cognitive load."
    )
    
    st.markdown("---")
    
    st.header("🌍 Country Context", help="Select a country to tailor the election information to your specific region.")
    country_selection = st.selectbox(
        "Select Country for Election Context",
        options=["Global", "India", "USA", "UK", "Canada", "Australia", "Other"],
        help="The selected country will be automatically appended to your query to provide region-specific context."
    )
    
    st.markdown("---")
    
    st.header("📌 Quick Topics", help="Select a topic to automatically ask a question.")
    quick_topic = st.selectbox(
        "Choose a topic:",
        ["How to vote?", "Election stages", "Voter registration", "Candidate process"],
        label_visibility="visible",
        help="Select a predefined election topic."
    )
    
    if st.button("⚡ Ask Quick Topic", use_container_width=True, type="primary", disabled=st.session_state.is_processing):
        handle_submit(quick_topic, country_selection)
        st.rerun()

# --- Main Interface ---
st.markdown("<header aria-label='Application Header'>", unsafe_allow_html=True)
st.title("🗳️ Interactive Election Education Assistant")
st.info("👋 **Welcome!** I am here to help you understand election processes simply and clearly.", icon="ℹ️")
st.warning("⚠️ **System Note:** The first request may take up to 30 seconds due to server startup.", icon="⚠️")

# Accessibility feature announcement
st.markdown('<div role="note" aria-label="Accessibility feature: audio support for visually impaired users">', unsafe_allow_html=True)
st.info("🔊 **Audio Accessibility Feature:** This assistant supports visually impaired users through real-time AI-generated audio using **Google Cloud Text-to-Speech**.")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("</header><hr>", unsafe_allow_html=True)

# Main Content Area
st.markdown("<section aria-label='Chat History'>", unsafe_allow_html=True)
st.markdown("### Step 1: View the conversation", help="This area shows your questions and the system's responses.")

for i, message in enumerate(st.session_state.chat_history):
    if message["role"] == "user":
        with st.chat_message("user", avatar="👤"):
            st.markdown(f"**You asked:** {message['content']}")
    else:
        with st.chat_message("assistant", avatar="🗳️"):
            render_accessible_response(message.get("parsed_content", {}))
            
            # Voice Output System
            audio_status_key = f"audio_status_{i}"
            if audio_status_key not in st.session_state:
                st.session_state[audio_status_key] = "idle"

            if "audio_bytes" in message:
                st.markdown(
                    "<div aria-live='polite' style='position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0;'>Audio ready to play</div>", 
                    unsafe_allow_html=True
                )
                st.caption("🔊 This audio is generated using Google Cloud Text-to-Speech.")
                st.caption(f"🔧 Debug Info: Audio size: {len(message['audio_bytes'])} bytes")
                
                # FORCE CORRECT AUDIO FORMAT and REMOVE AUTOPLAY
                st.audio(message["audio_bytes"], format="audio/mp3", autoplay=False)
            else:
                if st.session_state[audio_status_key] in ["idle", "error"]:
                    if st.session_state[audio_status_key] == "error":
                        st.error("⚠️ Audio could not be generated. Showing text instead.")
                    
                    btn_label = "🔊 Listen to Answer" if st.session_state[audio_status_key] == "idle" else "🔁 Retry Audio"
                    
                    if st.button(
                        btn_label, 
                        key=f"tts_btn_{i}", 
                        help="Generates audio using Google Cloud Text-to-Speech"
                    ):
                        st.session_state[audio_status_key] = "loading"
                        st.rerun()
                
                elif st.session_state[audio_status_key] == "loading":
                    status_box = st.empty()
                    status_box.info("⏳ Preparing audio...")
                    time.sleep(0.3)
                    status_box.info("⚙️ Generating speech using Google Cloud Text-to-Speech...")
                    
                    text_to_speak = message.get("parsed_content", {}).get("summary", "")
                    if not st.session_state.simple_mode:
                        detailed = message.get("parsed_content", {}).get("detailed", "")
                        text_to_speak += "\n" + detailed
                    
                    audio = generate_speech(text_to_speak, country_selection)
                    
                    status_box.info("🎵 Loading player...")
                    time.sleep(0.3)
                    status_box.empty()
                    
                    # Validation Layer
                    if audio is not None and len(audio) >= 1000:
                        message["audio_bytes"] = audio
                        st.session_state[audio_status_key] = "success"
                    else:
                        st.session_state[audio_status_key] = "error"
                    st.rerun()

st.markdown("</section>", unsafe_allow_html=True)
st.markdown("<br><br>", unsafe_allow_html=True) # Spacer

# Input Section
st.markdown("<section aria-label='User Input Area'>", unsafe_allow_html=True)
st.markdown("### Step 2: Ask your question")

col1, col2 = st.columns([8, 2])
with col1:
    prompt = st.chat_input(
        "Type your election question here... (e.g., How do I register to vote?)", 
        disabled=st.session_state.is_processing
    )
with col2:
    if st.button("🎤 Use Voice Input (Coming Soon)", disabled=st.session_state.is_processing, help="Record your voice to ask a question. This feature is currently in development and will convert your speech to text."):
        st.toast("🎤 Voice Input is currently in development. Please use the text input.", icon="ℹ️")

if prompt:
    handle_submit(prompt, country_selection)
    st.rerun()

st.markdown("</section>", unsafe_allow_html=True)

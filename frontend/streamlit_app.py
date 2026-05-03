import logging
import os
import time
from typing import Any, Dict

import requests  # type: ignore
import streamlit as st
import streamlit.components.v1 as components

from utils.tts_service import generate_speech
from styles.theme import get_base_styles, get_high_contrast_styles

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration ---
API_URL: str = os.getenv(
    "API_URL", "https://election-backend-752351306422.asia-south1.run.app/ask"
)

# --- Page Setup ---
st.set_page_config(
    page_title="Interactive Election Education Assistant",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --- Session State Initialization ---
def init_session_state() -> None:
    """Initializes the Streamlit session state variables."""
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


init_session_state()


# --- Accessibility: Style Management ---
def apply_styles() -> None:
    """
    Applies the theme styles based on the current session state.
    Ensures high-contrast and font-size settings are respected dynamically.
    """
    # 1. Base styles with current font size
    st.markdown(get_base_styles(st.session_state.font_size), unsafe_allow_html=True)

    # 2. High-contrast overrides if enabled
    if st.session_state.get("high_contrast"):
        st.markdown(get_high_contrast_styles(), unsafe_allow_html=True)


apply_styles()


# --- Accessibility: Semantic HTML Injection ---
def inject_accessibility_elements() -> None:
    """Injects ARIA live regions and semantic structure hints."""
    # 1. Screen Reader Live Region
    status_text = "Processing..." if st.session_state.is_processing else "Ready"
    if st.session_state.chat_history:
        status_text = "Response Received"
        
    st.markdown(
        f"""
        <div aria-live="polite" id="screen-reader-status" style="position:absolute;left:-9999px;">
            {status_text}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2. ARIA Landmarks (Main Content)
    components.html(
        """
    <script>
        const doc = window.parent.document;
        const mainNode = doc.querySelector('.main');
        if (mainNode) {
            mainNode.setAttribute('role', 'main');
            mainNode.setAttribute('aria-label', 'Election Education Assistant Main Content');
        }
        const sidebarNode = doc.querySelector('[data-testid="stSidebar"]');
        if (sidebarNode) {
            sidebarNode.setAttribute('role', 'navigation');
            sidebarNode.setAttribute('aria-label', 'Settings and Context Selection');
        }
    </script>
    """,
        height=0,
    )


inject_accessibility_elements()


# --- Helper Functions ---
@st.cache_resource
def get_request_session() -> requests.Session:
    """
    Provides a globally cached HTTP session for connection pooling.

    Returns:
        requests.Session: Reusable session object.
    """
    return requests.Session()


@st.cache_data(ttl=3600, show_spinner=False)
def _cached_api_call(query: str) -> Dict[str, str]:
    """
    Executes the API call to the backend and caches the result.

    Args:
        query (str): The user query.

    Returns:
        Dict[str, str]: The structured JSON response from the backend.
    """
    session = get_request_session()
    response = session.post(API_URL, json={"query": query}, timeout=60)
    response.raise_for_status()
    return response.json()


def fetch_from_backend(query: str, status_container: Any) -> Dict[str, str]:
    """
    Handles the API call with retries and staged loading UX.

    Args:
        query (str): The user query to send.
        status_container (st.empty): Streamlit container for UI updates.

    Returns:
        Dict[str, str]: The structured response payload or fallback.
    """
    max_retries = 3
    for attempt in range(max_retries):
        try:
            status_container.info("⏳ Connecting to server...")
            time.sleep(0.5)
            status_container.info("⚙️ Generating response...")

            data = _cached_api_call(query)

            status_container.success("✅ Finalizing answer...")
            time.sleep(0.5)
            return data

        except Exception as e:
            logger.error(f"Error during API call (Attempt {attempt+1}): {e}")
            if attempt < max_retries - 1:
                status_container.warning(
                    f"⚠️ Network slow. Retrying ({attempt+2}/3)..."
                )
                time.sleep(2)
            else:
                st.error("❌ System Error: Could not reach the server.")
                return {
                    "title": "Error",
                    "summary": "The service is currently unavailable.",
                    "detailed": str(e),
                }
    return {"title": "Error", "summary": "Failed after retries.", "detailed": ""}


def render_accessible_response(parsed_dict: Dict[str, str]) -> None:
    """
    Renders the response with Progressive Disclosure and ARIA wrappers.

    Args:
        parsed_dict (Dict[str, str]): The structured response data.
    """
    title = parsed_dict.get("title", "Information")
    summary = parsed_dict.get("summary", "")

    st.markdown(
        f"""
    <div aria-live="polite" aria-atomic="true">
        <h3>🗳️ {title}</h3>
        <p><strong>Key Summary:</strong> {summary}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    if not st.session_state.simple_mode:
        with st.expander("🔍 Show Details", expanded=False):
            st.markdown(parsed_dict.get("detailed", ""))


def handle_submit(query: str, country: str = "Global") -> None:
    """
    Handles query submission and interaction locking.

    Args:
        query (str): The user input.
        country (str): The selected country context.
    """
    if not query.strip():
        st.warning("Please enter a question.")
        return

    st.session_state.chat_history.append({"role": "user", "content": query})
    st.session_state.is_processing = True

    formatted_query = query if country == "Global" else f"{query} (Context: {country})"
    status_container = st.empty()

    response_data = fetch_from_backend(formatted_query, status_container)

    st.session_state.chat_history.append(
        {"role": "assistant", "parsed_content": response_data}
    )

    status_container.empty()
    st.session_state.is_processing = False


# --- Sidebar Interface ---
with st.sidebar:
    st.header("⚙️ Settings")
    st.slider(
        "🔠 Font Size",
        14,
        28,
        key="font_size",
        help="Adjust the application text size for better readability.",
    )
    st.toggle(
        "🌓 High Contrast",
        key="high_contrast",
        help="Enable high contrast mode for improved visual clarity.",
    )
    st.toggle(
        "🧠 Simple Mode",
        key="simple_mode",
        help="Hide detailed explanations for a simplified cognitive experience.",
    )

    st.markdown("---")
    country_selection = st.selectbox(
        "🌍 Country Context",
        ["Global", "India", "USA", "UK", "Canada", "Australia", "Other"],
        help="Select a country to get localized election information.",
    )

    st.markdown("---")
    quick_topic = st.selectbox(
        "📌 Quick Topics",
        ["How to vote?", "Election stages", "Voter registration", "Candidate process"],
        help="Choose a frequently asked topic to learn about quickly.",
    )

    if st.button(
        "⚡ Ask Quick Topic",
        disabled=st.session_state.is_processing,
        help="Submit the selected quick topic to the assistant.",
    ):
        handle_submit(quick_topic, country_selection)
        st.rerun()

# --- Main Interface ---
st.title("🗳️ Election Education Assistant")
st.info("👋 Welcome! Ask me any election-related question.")

for i, message in enumerate(st.session_state.chat_history):
    if message["role"] == "user":
        with st.chat_message("user", avatar="👤"):
            st.markdown(message["content"])
    else:
        with st.chat_message("assistant", avatar="🗳️"):
            parsed = message.get("parsed_content", {})
            render_accessible_response(parsed)

            audio_key = f"audio_status_{i}"
            if audio_key not in st.session_state:
                st.session_state[audio_key] = "idle"

            if "audio_bytes" in message:
                st.audio(message["audio_bytes"], format="audio/mp3")
                st.caption("🔊 Audio version of the assistant's response.")
            elif st.button(
                "🔊 Listen",
                key=f"tts_{i}",
                help="Generate and play an audio version of this response.",
            ):
                with st.spinner("Generating audio..."):
                    text = f"{parsed.get('summary', '')}. {parsed.get('detailed', '')}"
                    audio = generate_speech(text, country_selection)
                    if audio:
                        message["audio_bytes"] = audio
                        st.rerun()

prompt = st.chat_input(
    "Ask a question...",
    disabled=st.session_state.is_processing,
)
if prompt:
    handle_submit(prompt, country_selection)
    st.rerun()

# Accessibility: Visual indication for screen reader users
st.caption("Press Enter to submit your question.")

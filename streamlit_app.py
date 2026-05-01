import streamlit as st
import requests
import os

# --- Configuration ---
# Use the deployed Cloud Run backend
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

# --- Helper Functions ---
def get_backend_response(query: str) -> str:
    """Sends the user query to the FastAPI backend and retrieves the response."""
    try:
        response = requests.post(
            API_URL,
            json={"query": query},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "No response returned from the server.")
    except requests.exceptions.ConnectionError:
        return "⚠️ **Error:** Could not connect to the backend server. Please ensure the FastAPI server is running."
    except requests.exceptions.Timeout:
        return "⚠️ **Error:** The backend server took too long to respond."
    except requests.exceptions.HTTPError as e:
        # Handle graceful errors from our validator
        if response.status_code == 400:
            error_data = response.json()
            return f"⚠️ **Security/Validation:** {error_data.get('detail', 'Bad Request')}"
        return f"⚠️ **HTTP Error:** {e}"
    except Exception as e:
        return f"⚠️ **An unexpected error occurred:** {e}"

def handle_submit(query: str):
    """Handles the query submission, updating state and calling the API."""
    if not query.strip():
        st.warning("Please enter a question to ask.")
        return
        
    # Append user message
    st.session_state.chat_history.append({"role": "user", "content": query})
    
    # Get response with a spinner
    with st.spinner("Analyzing election processes..."):
        response_text = get_backend_response(query)
        
    # Append assistant message
    st.session_state.chat_history.append({"role": "assistant", "content": response_text})

def format_response_content(content: str):
    """
    Renders the response cleanly using markdown.
    The response should already be structured by the backend's system prompt.
    """
    st.markdown(content)

# --- Sidebar Interface ---
with st.sidebar:
    st.header("⚙️ Settings")
    
    country = st.selectbox(
        "🌍 Select your Country (Optional)",
        options=["Global (General)", "USA", "India", "UK", "Canada", "Australia", "Other"]
    )
    
    st.markdown("---")
    
    st.header("📌 Quick Topics")
    st.write("Not sure what to ask? Select a topic below:")
    
    quick_topic = st.selectbox(
        "Choose a topic:",
        ["How to vote?", "Election stages", "Voter registration", "Candidate process"],
        label_visibility="collapsed"
    )
    
    if st.button("⚡ Ask Quick Topic", use_container_width=True, type="primary"):
        # Formulate query based on topic and country
        country_context = "" if country == "Global (General)" else f" in {country}"
        query = f"{quick_topic}{country_context}"
        handle_submit(query)

# --- Main Interface ---
st.title("🗳️ Interactive Election Education Assistant")
st.markdown("Welcome! I am here to help you understand election processes clearly and simply. Ask me any question related to voting, elections, or timelines.")
st.markdown("---")

# Display Chat History
for message in st.session_state.chat_history:
    if message["role"] == "user":
        with st.chat_message("user", avatar="👤"):
            st.markdown(f"{message['content']}")
    else:
        with st.chat_message("assistant", avatar="🗳️"):
            # Check if it's an error message
            if message["content"].startswith("⚠️"):
                st.error(message["content"])
            else:
                # Add success toast if it's the latest successful message
                if message == st.session_state.chat_history[-1] and not message["content"].startswith("⚠️"):
                    st.toast("✅ Response generated successfully!")
                format_response_content(message["content"])

st.markdown("<br>", unsafe_allow_html=True) # Spacer

# Input Section
prompt = st.chat_input("Ask a question about elections... (e.g., How do I register to vote?)")
if prompt:
    country_context = "" if country == "Global (General)" else f" (Context: {country})"
    full_query = f"{prompt}{country_context}" if country_context else prompt
    handle_submit(full_query)
    st.rerun()

import pytest
from unittest.mock import MagicMock, patch
import sys

# Mock Streamlit to prevent UI execution during logic tests
sys.modules['streamlit'] = MagicMock()
sys.modules['streamlit'].columns.return_value = [MagicMock(), MagicMock()]
sys.modules['streamlit.components.v1'] = MagicMock()

import streamlit_app

def test_parse_and_format_response_valid():
    """Test standard response parsing with title, summary, and details."""
    raw = "# Election Process\n\nThis is a short summary.\n\nHere are the detailed steps."
    res = streamlit_app.parse_and_format_response(raw)
    
    assert res["title"] == "Election Process"
    assert res["summary"] == "This is a short summary."
    assert res["detailed"] == "Here are the detailed steps."

def test_parse_and_format_response_empty():
    """Test empty input handling."""
    res = streamlit_app.parse_and_format_response("")
    assert res["title"] == "Basic Election Guide (Fallback Mode)"
    assert "Registration" in res["detailed"]

def test_parse_and_format_response_no_title():
    """Test response parsing when no markdown title is provided."""
    raw = "Just a plain text response.\n\nWith some details."
    res = streamlit_app.parse_and_format_response(raw)
    
    assert res["title"] == "Election Insight"
    assert res["summary"] == "Just a plain text response."

def test_get_fallback_response():
    """Test fallback generator logic."""
    res = streamlit_app.get_fallback_response()
    assert "Fallback Mode" in res["title"]
    assert "server is currently unavailable" in res["summary"]

def test_integration_flow():
    """Simulates: User input → API → formatted response → UI output state storage."""
    # Reset mock state
    streamlit_app.st.session_state.chat_history = []
    streamlit_app.st.session_state.is_processing = False
    
    with patch('streamlit_app.fetch_from_backend') as mock_fetch:
        # Mock API returning raw text with title, summary, and bullets
        mock_fetch.return_value = {
            "raw_text": "# Integrated Title\n\nShort summ.\n\n- Bullet 1\n- Bullet 2\n- Bullet 3"
        }
        
        # Trigger UI flow
        streamlit_app.handle_submit("How do I vote?", "USA")
        
        # Validate state updates (UI output side-effects)
        history = streamlit_app.st.session_state.chat_history
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "How do I vote?"
        
        # Explicit Structural Formatting Assertions
        parsed = history[1]["parsed_content"]
        assert "Title" in parsed["title"]                  # Validates Title exists
        assert parsed["summary"] == "Short summ."          # Validates Summary exists
        assert "- Bullet 1" in parsed["detailed"]          # Validates Bullet points exist
        assert "- Bullet 3" in parsed["detailed"]

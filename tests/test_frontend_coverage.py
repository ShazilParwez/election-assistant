import importlib
import sys
from unittest.mock import MagicMock, patch
import pytest
import requests

# Robust decorator that handles both @st.cache_data and @st.cache_data()
def robust_mock_decorator(*args, **kwargs):
    if args and callable(args[0]):
        return args[0]
    return lambda f: f

@pytest.fixture
def mock_streamlit():
    """Provides a clean, isolated Streamlit mock for each test."""
    mock = MagicMock()
    mock.session_state = MagicMock()
    mock.cache_resource = robust_mock_decorator
    mock.cache_data = robust_mock_decorator
    return mock

# --- Line 65 ---
def test_line_65_high_contrast_css(mock_streamlit):
    """Surgically triggers line 65 by enabling high contrast."""
    with patch.dict(sys.modules, {"streamlit": mock_streamlit}):
        from frontend import streamlit_app
        importlib.reload(streamlit_app)
        
        # Setup state
        mock_streamlit.session_state.font_size = 16
        mock_streamlit.session_state.high_contrast = True
        
        streamlit_app.inject_custom_css()
        
        # Verify markdown was called with high-contrast styles
        calls = [str(c) for c in mock_streamlit.markdown.call_args_list]
        assert any("background-color: #000000" in c for c in calls)

# --- Line 122 ---
def test_line_122_get_request_session(mock_streamlit):
    """Surgically triggers line 122."""
    with patch.dict(sys.modules, {"streamlit": mock_streamlit}):
        from frontend import streamlit_app
        importlib.reload(streamlit_app)
        
        func = streamlit_app.get_request_session
        if hasattr(func, "__wrapped__"):
            func = func.__wrapped__
        
        # If reload worked, func should be the real function
        session = func()
        assert isinstance(session, requests.Session)

# --- Line 277 ---
def test_line_277_audio_display(mock_streamlit):
    """Surgically triggers line 277."""
    with patch.dict(sys.modules, {"streamlit": mock_streamlit}):
        # Setup state for the main loop BEFORE reload
        mock_streamlit.session_state.chat_history = [
            {"role": "assistant", "audio_bytes": b"fake_audio", "parsed_content": {"summary": "test"}}
        ]
        mock_streamlit.session_state.is_processing = False
        mock_streamlit.session_state.font_size = 16
        mock_streamlit.session_state.high_contrast = False
        mock_streamlit.session_state.simple_mode = False
        mock_streamlit.session_state.__contains__.return_value = True
        
        mock_streamlit.sidebar = MagicMock()
        mock_streamlit.columns.return_value = [MagicMock(), MagicMock()]
        
        from frontend import streamlit_app
        importlib.reload(streamlit_app)
        
        # Verify st.audio was rendered
        mock_streamlit.audio.assert_any_call(b"fake_audio", format="audio/mp3")

import pytest
from unittest.mock import patch, MagicMock
import sys
import requests

# Mock Streamlit to prevent UI execution during logic tests
sys.modules['streamlit'] = MagicMock()
sys.modules['streamlit'].columns.return_value = [MagicMock(), MagicMock()]
sys.modules['streamlit.components.v1'] = MagicMock()

def pass_through_decorator(*args, **kwargs):
    def decorator(func):
        return func
    return decorator

sys.modules['streamlit'].cache_data = pass_through_decorator
sys.modules['streamlit'].cache_resource = pass_through_decorator

import streamlit_app

@patch('streamlit_app.get_request_session')
def test_fetch_from_backend_success(mock_get_session):
    """Test successful API response parsing."""
    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_response.json.return_value = {"response": "Mocked AI Response"}
    mock_session.post.return_value = mock_response
    mock_get_session.return_value = mock_session
    
    mock_status_container = MagicMock()
    
    res = streamlit_app.fetch_from_backend("How to vote?", mock_status_container)
    
    assert res == {"raw_text": "Mocked AI Response"}
    assert mock_session.post.called

@patch('streamlit_app.get_request_session')
def test_fetch_from_backend_timeout(mock_get_session):
    """Test timeout fallback and retry logic."""
    mock_session = MagicMock()
    mock_session.post.side_effect = requests.exceptions.Timeout("Timeout")
    mock_get_session.return_value = mock_session
    mock_status_container = MagicMock()
    
    res = streamlit_app.fetch_from_backend("How to vote?", mock_status_container)
    
    assert "Fallback Mode" in res["title"]
    assert mock_session.post.call_count == 3  # Validates the max_retries = 3 logic

@patch('streamlit_app.get_request_session')
def test_fetch_from_backend_invalid_json(mock_get_session):
    """Test handling of invalid JSON from API."""
    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_session.post.return_value = mock_response
    mock_get_session.return_value = mock_session
    mock_status_container = MagicMock()
    
    res = streamlit_app.fetch_from_backend("Test", mock_status_container)
    
    assert "Fallback Mode" in res["title"]

@patch('streamlit_app.get_request_session')
def test_fetch_from_backend_http_error(mock_get_session):
    """Test handling of HTTP errors like 500."""
    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Server Error")
    mock_session.post.return_value = mock_response
    mock_get_session.return_value = mock_session
    mock_status_container = MagicMock()
    
    res = streamlit_app.fetch_from_backend("Test", mock_status_container)
    
    assert "Fallback Mode" in res["title"]

import sys
from unittest.mock import MagicMock, patch

import requests  # type: ignore

# Mock Streamlit to prevent UI execution during logic tests
sys.modules["streamlit"] = MagicMock()
sys.modules["streamlit"].columns.return_value = [MagicMock(), MagicMock()]
sys.modules["streamlit.components.v1"] = MagicMock()


def pass_through_decorator(*args, **kwargs):  # type: ignore
    """Simple pass-through decorator for mocking."""

    def decorator(func):  # type: ignore
        return func

    return decorator


sys.modules["streamlit"].cache_data = pass_through_decorator  # type: ignore
sys.modules["streamlit"].cache_resource = pass_through_decorator  # type: ignore

# Fix E402 by importing after mocking
from frontend import streamlit_app  # noqa: E402


@patch("frontend.streamlit_app.get_request_session")
def test_fetch_from_backend_success(mock_get_session):
    """
    Test successful API response parsing.
    """
    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "title": "Success",
        "summary": "Short",
        "detailed": "Detailed",
    }
    mock_session.post.return_value = mock_response
    mock_get_session.return_value = mock_session

    mock_status_container = MagicMock()

    res = streamlit_app.fetch_from_backend("How to vote?", mock_status_container)

    assert res["title"] == "Success"
    assert mock_session.post.called


@patch("frontend.streamlit_app.get_request_session")
def test_fetch_from_backend_timeout(mock_get_session):
    """
    Test timeout fallback and retry logic.
    """
    mock_session = MagicMock()
    mock_session.post.side_effect = requests.exceptions.Timeout("Timeout")
    mock_get_session.return_value = mock_session
    mock_status_container = MagicMock()

    res = streamlit_app.fetch_from_backend("How to vote?", mock_status_container)

    assert res["title"] == "Error"
    assert mock_session.post.call_count == 3


@patch("frontend.streamlit_app.get_request_session")
def test_fetch_from_backend_invalid_json(mock_get_session):
    """
    Test handling of invalid JSON from API.
    """
    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_session.post.return_value = mock_response
    mock_get_session.return_value = mock_session
    mock_status_container = MagicMock()

    res = streamlit_app.fetch_from_backend("Test", mock_status_container)

    assert res["title"] == "Error"


@patch("frontend.streamlit_app.get_request_session")
def test_fetch_from_backend_http_error(mock_get_session):
    """
    Test handling of HTTP errors like 500.
    """
    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "500 Server Error"
    )
    mock_session.post.return_value = mock_response
    mock_get_session.return_value = mock_session
    mock_status_container = MagicMock()

    res = streamlit_app.fetch_from_backend("Test", mock_status_container)

    assert res["title"] == "Error"


def test_init_session_state():
    """Test initialization of session state variables."""
    mock_st = MagicMock()
    # Use a real dict-like object but allow dot access
    mock_st.session_state = MagicMock()
    mock_st.session_state.__contains__.side_effect = lambda x: False
    
    with patch("frontend.streamlit_app.st", mock_st):
        from frontend.streamlit_app import init_session_state
        init_session_state()
        # Verify it was initialized (dot access on MagicMock works fine)
        assert mock_st.session_state.chat_history == []
        assert mock_st.session_state.font_size == 16


def test_handle_submit_empty():
    """Test handle_submit with empty query."""
    mock_st = MagicMock()
    # Mock chat_history to avoid KeyError if it's accessed
    mock_st.session_state = {"chat_history": [], "is_processing": False}
    with patch("frontend.streamlit_app.st", mock_st):
        from frontend.streamlit_app import handle_submit
        handle_submit("   ")
        mock_st.warning.assert_called_with("Please enter a question.")


@patch("frontend.streamlit_app._cached_api_call")
def test_fetch_from_backend_total_failure(mock_api_call):
    """Test total failure after retries in fetch_from_backend."""
    mock_api_call.side_effect = Exception("Permanent failure")
    mock_status = MagicMock()

    res = streamlit_app.fetch_from_backend("query", mock_status)
    assert res["title"] == "Error"
    assert mock_api_call.call_count == 3


def test_init_session_state_existing():
    """Test init_session_state when values already exist."""
    mock_st = MagicMock()
    # Mock __contains__ to return True
    mock_st.session_state.__contains__.return_value = True
    
    with patch("frontend.streamlit_app.st", mock_st):
        from frontend.streamlit_app import init_session_state
        init_session_state()
        # Should not have called set on any of these
        assert mock_st.session_state.chat_history.call_count == 0


@patch("frontend.streamlit_app.time.sleep")
def test_fetch_from_backend_unreachable_return(mock_sleep):
    """Test the 'unreachable' return at the end of fetch_from_backend by forcing loop exit."""
    # Force range(3) to be empty for this test
    with patch("frontend.streamlit_app.range", return_value=[]):
        mock_status = MagicMock()
        res = streamlit_app.fetch_from_backend("query", mock_status)
        assert res["summary"] == "Failed after retries."

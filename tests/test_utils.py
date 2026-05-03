import sys
from unittest.mock import MagicMock, patch

# Mock Streamlit to prevent UI execution during logic tests
sys.modules["streamlit"] = MagicMock()
sys.modules["streamlit"].columns.return_value = [MagicMock(), MagicMock()]
sys.modules["streamlit.components.v1"] = MagicMock()

# Fix E402 by importing after mocking
from backend.services import formatter  # noqa: E402
from frontend import streamlit_app  # noqa: E402


def test_parse_and_format_response_valid() -> None:
    """
    Test standard response parsing with title, summary, and details.
    """
    raw = (
        "# Election Process\n\nThis is a short summary.\n\nHere are the detailed steps."
    )
    res = formatter.parse_and_format_response(raw)

    assert res["title"] == "Election Process"
    assert res["summary"] == "This is a short summary."
    assert res["detailed"] == "Here are the detailed steps."


def test_parse_and_format_response_empty() -> None:
    """
    Test empty input handling.
    """
    res = formatter.parse_and_format_response("")
    assert res["title"] == "Election Insight"
    assert "not return any valid information" in res["detailed"]


def test_parse_and_format_response_long_summary() -> None:
    """Test truncation of long summaries."""
    long_text = "A" * 400
    res = formatter.parse_and_format_response(long_text)
    assert len(res["summary"]) == 300
    assert res["summary"].endswith("...")


def test_parse_and_format_response_no_paragraphs() -> None:
    """Test handling of content with no paragraphs (only a title)."""
    res = formatter.parse_and_format_response("# Title Only")
    assert res["title"] == "Title Only"
    assert res["summary"] == "Overview of the requested topic."
    raw = "Just a plain text response.\n\nWith some details."
    res = formatter.parse_and_format_response(raw)

    assert res["title"] == "Election Insight"
    assert res["summary"] == "Just a plain text response."


def test_get_fallback_response() -> None:
    """
    Test fallback generator logic.
    """
    res = formatter.get_fallback_response()
    assert "Fallback Mode" in res["title"]
    assert "server is currently unavailable" in res["summary"]


def test_integration_flow() -> None:
    """
    Simulates: User input -> API -> formatted response -> UI output state storage.
    """
    # Reset mock state
    streamlit_app.st.session_state.chat_history = []
    streamlit_app.st.session_state.is_processing = False

    with patch("frontend.streamlit_app.fetch_from_backend") as mock_fetch:
        # Mock API returning structured data directly
        mock_fetch.return_value = {
            "title": "Integrated Title",
            "summary": "Short summ.",
            "detailed": "- Bullet 1\n- Bullet 2\n- Bullet 3",
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
        assert "Title" in parsed["title"]
        assert parsed["summary"] == "Short summ."
        assert "- Bullet 1" in parsed["detailed"]
        assert "- Bullet 3" in parsed["detailed"]

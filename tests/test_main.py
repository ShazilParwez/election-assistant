from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app, raise_server_exceptions=False)


def test_read_root():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome" in response.json()["message"]


def test_global_exception_handler():
    """Test that unhandled exceptions are caught and returned as 500."""
    # Mock a route that raises an exception
    @app.get("/trigger-error")
    async def trigger_error():
        raise RuntimeError("Test exception")
    
    response = client.get("/trigger-error")
    assert response.status_code == 500
    assert response.json()["detail"] == "Internal Server Error"
    assert response.json()["error"] == "Test exception"


def test_middleware_logging():
    """Test that middleware logs requests and responses."""
    with patch("backend.main.logger") as mock_logger:
        client.get("/")
        # Check if the response status code was logged
        any_status_log = any(
            "Response Status Code: 200" in str(call) for call in mock_logger.info.call_args_list
        )
        assert any_status_log is True

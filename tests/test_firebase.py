import json
import os
from unittest.mock import MagicMock, patch

import pytest

from backend.services.firebase_service import initialize_firebase, save_query


@pytest.fixture
def mock_firebase_admin():
    with patch("backend.services.firebase_service.firebase_admin") as mock:
        mock._apps = []
        yield mock


@pytest.fixture
def mock_firestore():
    with patch("backend.services.firebase_service.firestore") as mock:
        yield mock


def test_initialize_firebase_env_var(mock_firebase_admin, mock_firestore):
    """Test initialization using FIREBASE_SERVICE_ACCOUNT env var."""
    key_dict = {"project_id": "test-project", "type": "service_account"}
    with patch.dict(os.environ, {"FIREBASE_SERVICE_ACCOUNT": json.dumps(key_dict)}):
        initialize_firebase()
        mock_firebase_admin.initialize_app.assert_called_once()
        mock_firestore.client.assert_called_once()


def test_initialize_firebase_local_file(mock_firebase_admin, mock_firestore):
    """Test initialization using local file."""
    with patch.dict(os.environ, {}, clear=True):
        with patch("os.path.exists", return_value=True):
            with patch("backend.services.firebase_service.credentials.Certificate") as mock_cred:
                initialize_firebase()
                mock_cred.assert_called_with("firebase_key.json")
                mock_firebase_admin.initialize_app.assert_called_once()


def test_initialize_firebase_adc(mock_firebase_admin, mock_firestore):
    """Test initialization using Application Default Credentials."""
    with patch.dict(os.environ, {}, clear=True):
        with patch("os.path.exists", return_value=False):
            initialize_firebase()
            mock_firebase_admin.initialize_app.assert_called_with()
            mock_firestore.client.assert_called_once()


def test_initialize_firebase_error(mock_firebase_admin):
    """Test initialization failure."""
    mock_firebase_admin.initialize_app.side_effect = Exception("Auth failed")
    with patch.dict(os.environ, {}, clear=True):
        with patch("os.path.exists", return_value=False):
            with pytest.raises(Exception):
                initialize_firebase()


def test_save_query_success():
    """Test successful query saving to Firestore."""
    mock_db = MagicMock()
    mock_collection = MagicMock()
    mock_doc = MagicMock()
    
    mock_db.collection.return_value = mock_collection
    mock_collection.document.return_value = mock_doc
    
    with patch("backend.services.firebase_service.db", mock_db):
        save_query("test query", "test response", latency_ms=100)
        
        mock_db.collection.assert_called_with("queries")
        mock_doc.set.assert_called_once()
        data = mock_doc.set.call_args[0][0]
        assert data["query"] == "test query"
        assert data["latency_ms"] == 100


def test_save_query_no_latency():
    """Test save_query without latency_ms."""
    mock_db = MagicMock()
    mock_collection = MagicMock()
    mock_doc = MagicMock()
    mock_db.collection.return_value = mock_collection
    mock_collection.document.return_value = mock_doc
    with patch("backend.services.firebase_service.db", mock_db):
        save_query("test query", "test response")
        mock_doc.set.assert_called_once()
        data = mock_doc.set.call_args[0][0]
        assert "latency_ms" not in data


def test_save_query_error():
    """Test error handling when saving query fails."""
    mock_db = MagicMock()
    mock_db.collection.side_effect = Exception("Firestore down")
    
    with patch("backend.services.firebase_service.db", mock_db):
        # Should not raise exception, just log it
        save_query("test", "test")
        mock_db.collection.assert_called()

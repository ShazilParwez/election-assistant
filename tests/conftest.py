import os
from unittest.mock import MagicMock
import sys

# Mock firebase_admin BEFORE any imports that might trigger it
mock_firebase = MagicMock()
mock_firestore = MagicMock()
sys.modules["firebase_admin"] = mock_firebase
sys.modules["firebase_admin.credentials"] = MagicMock()
sys.modules["firebase_admin.firestore"] = mock_firestore

# Set dummy environment variables for tests to prevent Settings() from failing
os.environ["GOOGLE_API_KEY"] = "fake-test-key-123"
os.environ["FIREBASE_SERVICE_ACCOUNT"] = '{"type": "service_account", "project_id": "test-project"}'

import logging
import os
import json
import datetime
import firebase_admin
from firebase_admin import credentials, firestore

logger = logging.getLogger(__name__)

# --------------------------------------------
# 🔥 Firebase Initialization (runs only once)
# --------------------------------------------

if not firebase_admin._apps:
    try:
        # 👉 Try to get Firebase JSON from environment variable (Cloud Run optional)
        key_json = os.getenv("FIREBASE_SERVICE_ACCOUNT")

        if key_json:
            # ✅ Case 1: Using env variable (if you explicitly pass it)
            key_dict = json.loads(key_json)
            cred = credentials.Certificate(key_dict)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase initialized using ENV variable")

        elif os.path.exists("firebase_key.json"):
            # ✅ Case 2: Local development using JSON file
            cred = credentials.Certificate("firebase_key.json")
            firebase_admin.initialize_app(cred)
            logger.info("Firebase initialized using local file")

        else:
            # ✅ Case 3: Cloud Run default (BEST for your case)
            firebase_admin.initialize_app()
            logger.info("Firebase initialized using ADC (Cloud Run default)")

    except Exception as e:
        logger.error("Firebase initialization failed", exc_info=True)
        raise e  # crash early if something is actually wrong


# --------------------------------------------
# 📦 Firestore Client Initialization
# --------------------------------------------

db = firestore.client()


# --------------------------------------------
# 💾 Function to Save Query + Response
# --------------------------------------------

def save_query(query: str, response: str, country: str = "Global", latency_ms: int = None) -> None:
    """
    Saves user query, AI response, and metadata into Firestore.

    Args:
        query (str): The user's input query.
        response (str): The AI-generated response.
        country (str, optional): Contextual country setting. Defaults to "Global".
        latency_ms (int, optional): Response generation latency in milliseconds.
    """

    try:
        # 👉 Create new document (auto ID)
        doc_ref = db.collection("queries").document()

        # 👉 Current UTC timestamp
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # 👉 Data structure
        data = {
            "query": query,
            "response": response,
            "country": country,
            "timestamp": timestamp
        }

        if latency_ms is not None:
            data["latency_ms"] = latency_ms

        # 👉 Save to Firestore
        doc_ref.set(data)
        logger.debug(f"Query saved with ID: {doc_ref.id}")

    except Exception as e:
        logger.error("Failed to save query to Firestore", exc_info=True)
import datetime
import json
import logging
import os
from typing import Any, Dict, Optional

import firebase_admin  # type: ignore
from firebase_admin import credentials, firestore  # type: ignore

logger = logging.getLogger(__name__)

# Constants
QUERIES_COLLECTION = "queries"


def initialize_firebase() -> Any:
    """
    Initializes the Firebase Admin SDK using the best available method.

    Returns:
        Any: The initialized Firestore client.
    """
    if not firebase_admin._apps:
        try:
            key_json = os.getenv("FIREBASE_SERVICE_ACCOUNT")

            if key_json:
                key_dict = json.loads(key_json)
                cred = credentials.Certificate(key_dict)
                firebase_admin.initialize_app(cred)
                logger.info("Firebase initialized using ENV variable")

            elif os.path.exists("firebase_key.json"):
                cred = credentials.Certificate("firebase_key.json")
                firebase_admin.initialize_app(cred)
                logger.info("Firebase initialized using local file")

            else:
                firebase_admin.initialize_app()
                logger.info("Firebase initialized using ADC (Cloud Run default)")

        except Exception as e:
            logger.error(f"Firebase initialization failed: {e}", exc_info=True)
            raise e

    return firestore.client()


# Firestore Client Singleton
db = initialize_firebase()


def save_query(
    query: str, response: str, country: str = "Global", latency_ms: Optional[int] = None
) -> None:
    """
    Saves user query, AI response, and metadata into Firestore.

    Args:
        query (str): The user's input query.
        response (str): The AI-generated response.
        country (str): Contextual country setting. Defaults to "Global".
        latency_ms (int, optional): Response generation latency in milliseconds.
    """

    try:
        doc_ref = db.collection(QUERIES_COLLECTION).document()
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        data: Dict[str, Any] = {
            "query": query,
            "response": response,
            "country": country,
            "timestamp": timestamp,
        }

        if latency_ms is not None:
            data["latency_ms"] = latency_ms

        doc_ref.set(data)
        logger.debug(f"Query saved with ID: {doc_ref.id}")

    except Exception as e:
        logger.error(f"Failed to save query to Firestore: {e}", exc_info=True)

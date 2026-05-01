import os
import json
import datetime
import firebase_admin
from firebase_admin import credentials, firestore

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

            print("✅ [DEBUG] Firebase initialized using ENV variable")

        elif os.path.exists("firebase_key.json"):
            # ✅ Case 2: Local development using JSON file
            cred = credentials.Certificate("firebase_key.json")
            firebase_admin.initialize_app(cred)

            print("✅ [DEBUG] Firebase initialized using local file")

        else:
            # ✅ Case 3: Cloud Run default (BEST for your case)
            # Uses Application Default Credentials automatically
            firebase_admin.initialize_app()

            print("✅ [DEBUG] Firebase initialized using ADC (Cloud Run default)")

    except Exception as e:
        print(f"❌ [DEBUG] Firebase initialization failed: {e}")
        raise e  # crash early if something is actually wrong


# --------------------------------------------
# 📦 Firestore Client Initialization
# --------------------------------------------

db = firestore.client()


# --------------------------------------------
# 💾 Function to Save Query + Response
# --------------------------------------------

def save_query(query: str, response: str, country: str = "Global", latency_ms: int = None):
    """
    Saves user query, AI response, and metadata into Firestore.
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

        print(f"✅ [DEBUG] Query saved with ID: {doc_ref.id}")

    except Exception as e:
        print(f"❌ [DEBUG] Failed to save query: {e}")
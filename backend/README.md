# Election Assistant - Backend

This is the FastAPI backend for the Interactive Election Education Assistant. It handles incoming queries, validates them for safety, communicates securely with the Google Gemini API, and logs operations into Firebase Firestore.

## 🏗️ Architecture

- **FastAPI**: Handles high-performance HTTP request processing.
- **Gemini 2.5 Flash-Lite**: Powers the AI-based election knowledge extraction.
- **Firestore**: Logs query history and response latencies asynchronously.
- **Strict Separation**: The backend does NOT handle any frontend UI logic or Text-to-Speech generation. It exclusively returns structured JSON responses.

## 🚀 Running Locally

1. Create a virtual environment and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the server:
   ```bash
   python main.py
   ```
   Or via Uvicorn:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8080 --reload
   ```

## 📦 Deployment (Cloud Run)

To deploy explicitly to Google Cloud Run:
```bash
cd backend
gcloud run deploy election-backend --source . --region asia-south1 --allow-unauthenticated
```

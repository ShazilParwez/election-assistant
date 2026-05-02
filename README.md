# 🗳️ Interactive Election Education Assistant

An AI-powered assistant that helps users understand elections, voting processes, and timelines.

## 🚀 Live Demo
Frontend: https://election-frontend-752351306422.asia-south1.run.app  
Backend API: https://election-backend-752351306422.asia-south1.run.app

## 🧠 Features
- Ask election-related questions
- AI-powered responses (Gemini)
- Stores queries in Firestore
- FastAPI backend + Streamlit frontend

## ⚙️ Tech Stack
- Frontend: Streamlit
- Backend: FastAPI (Cloud Run)
- AI: Gemini API
- Database: Firebase Firestore
- Deployment: Google Cloud Run

## 🏗️ Architecture
User → Streamlit → FastAPI → Gemini → Firestore

## 📌 Example Query
"How to vote in India?"

## 🧪 Testing

### ✅ Test Status
✔ **All tests passing**  
✔ **Coverage enabled**  

Command used:
```bash
pytest --cov=. --cov-report=term
```

We use `pytest` for robust unit testing, with a focus on API client robustness, formatting logic, and TTS fallback behaviors.

### Test Folder Structure
```text
/tests
  ├── test_api_client.py
  ├── test_routes.py
  ├── test_services.py
  ├── test_tts_service.py
  └── test_utils.py
```

### Prerequisites
Install the development dependencies:
```bash
pip install -r requirements-dev.txt
```

### Running Tests
To run all tests and verify the logic pipeline:
```bash
pytest tests/ -v
```

### Coverage Report
To view the test coverage across the logic modules:
```bash
pytest --cov=. --cov-report=term
```
**Expected Output Example:**
```text
Name                               Stmts   Miss  Cover
------------------------------------------------------
app\services\tts_service.py           49     14    71%
streamlit_app.py                     174     34    80%
tests\test_api_client.py              40      0   100%
tests\test_tts_service.py             30      0   100%
tests\test_utils.py                   40      0   100%
------------------------------------------------------
TOTAL                                564     99    82%
```
This confirms robust error handling and reliable UI fallback states with ≥80% total logic coverage.
# Election Assistant - Frontend

This is the Streamlit frontend for the Interactive Election Education Assistant. It provides a highly accessible (WCAG 2.1 AA/AAA), keyboard-friendly interface for visually impaired users and general citizens to learn about election processes.

## 🏗️ Architecture

- **Streamlit**: Renders the UI and manages session state.
- **Accessibility Engine**: Uses custom CSS and JS injection for ARIA labels, focus rings, and high contrast modes.
- **Google Cloud TTS**: Converts election answers to speech securely on the frontend to avoid backend bottlenecking.
- **St.Cache**: Uses Streamlit's `@st.cache_data` and session state for intelligent connection pooling and response caching.

## 🚀 Running Locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the application:
   ```bash
   streamlit run streamlit_app.py
   ```

## 📦 Deployment (Cloud Run)

To deploy explicitly to Google Cloud Run:
```bash
cd frontend
gcloud run deploy election-frontend --source . --region asia-south1 --allow-unauthenticated
```

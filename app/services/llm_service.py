import os
import traceback
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv
from app.core.prompts import SYSTEM_PROMPT
from app.services.firebase_service import save_query

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable is not set")

client = genai.Client(api_key=api_key)

def get_response(user_query: str) -> str:
    """
    Calls the Gemini API to generate an election education response.
    Combines the system prompt and the user query securely.
    """
    print(f"🚀 [DEBUG] Initiating Gemini API call for query: '{user_query}'")
    
    if not user_query or not user_query.strip():
        raise ValueError("Query cannot be empty.")

    try:
        print("🚀 [DEBUG] BEFORE Gemini call")
        start_time = time.time()
        
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=f"{SYSTEM_PROMPT}\n\nUser Query: {user_query}"
        )
        
        end_time = time.time()
        latency_ms = int((end_time - start_time) * 1000)
        print(f"🚀 [DEBUG] AFTER Gemini call. Latency: {latency_ms} ms")
        
        if hasattr(response, "text") and response.text:
            print("✅ [DEBUG] Successfully received response from Gemini")
            final_text = response.text
            
            # Save to Firebase
            save_query(
                query=user_query,
                response=final_text,
                country="Global",
                latency_ms=latency_ms
            )
            
            return final_text
        else:
            print("❌ [DEBUG] Received empty response from Gemini")
            return "Sorry, I couldn't generate a response."

    except Exception as e:
        print(f"❌ [DEBUG] Gemini API Exception occurred: {str(e)}")
        print(f"❌ [DEBUG] Traceback: {traceback.format_exc()}")
        raise RuntimeError(f"Failed to generate response from Gemini: {str(e)}")

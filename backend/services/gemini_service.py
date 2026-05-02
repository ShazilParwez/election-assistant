import os
import traceback
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv
from core.prompts import SYSTEM_PROMPT
from services.firebase_service import save_query

import logging

load_dotenv()

logger = logging.getLogger(__name__)

_client_instance = None

def get_gemini_client() -> genai.Client:
    """
    Singleton pattern for lazy-loading the Gemini API client.

    Returns:
        genai.Client: A globally shared instance of the Gemini client.
    
    Raises:
        ValueError: If GOOGLE_API_KEY is not set.
    """
    global _client_instance
    if _client_instance is None:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.error("GOOGLE_API_KEY environment variable is missing.")
            raise ValueError("GOOGLE_API_KEY environment variable is not set")
        _client_instance = genai.Client(api_key=api_key)
        logger.info("Initialized new Gemini API client instance.")
    return _client_instance

def get_response(user_query: str) -> str:
    """
    Calls the Gemini API to generate an election education response.
    Combines the system prompt and the user query securely.

    Args:
        user_query (str): The specific question asked by the user.

    Returns:
        str: The AI-generated educational response.

    Raises:
        ValueError: If the input query is empty.
        RuntimeError: If the Gemini API fails.
    """
    logger.info(f"Initiating Gemini API call for query", extra={"query_length": len(user_query)})
    
    if not user_query or not user_query.strip():
        raise ValueError("Query cannot be empty.")

    try:
        logger.debug("Executing synchronous Gemini call...")
        start_time = time.time()
        
        client = get_gemini_client()
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=f"{SYSTEM_PROMPT}\n\nUser Query: {user_query}"
        )
        
        end_time = time.time()
        latency_ms = int((end_time - start_time) * 1000)
        logger.info(f"Received Gemini response. Latency: {latency_ms} ms")
        
        if hasattr(response, "text") and response.text:
            logger.debug("Successfully extracted text from Gemini response")
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
            logger.warning("Received empty or invalid text response from Gemini")
            return "Sorry, I couldn't generate a response."

    except Exception as e:
        logger.error("Gemini API Exception occurred", exc_info=True)
        raise RuntimeError(f"Failed to generate response from Gemini: {str(e)}")

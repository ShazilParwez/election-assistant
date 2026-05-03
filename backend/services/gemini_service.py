import logging
import os
import time

from dotenv import load_dotenv
from google import genai

from backend.core.config import settings
from backend.core.prompts import SYSTEM_PROMPT
from backend.interfaces.llm_interface import LLMInterface
from backend.services.firebase_service import save_query

load_dotenv()

logger = logging.getLogger(__name__)


class GeminiService(LLMInterface):
    """
    Implementation of the LLMInterface using Google's Gemini API.
    """

    def __init__(self) -> None:
        """
        Initializes the GeminiService and authenticates the client.

        Raises:
            ValueError: If GOOGLE_API_KEY environment variable is missing.
        """
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.error("GOOGLE_API_KEY environment variable is missing.")
            raise ValueError("GOOGLE_API_KEY environment variable is not set")
        self._client = genai.Client(api_key=api_key)
        logger.info("Initialized Gemini API client instance.")

    def get_response(self, user_query: str) -> str:
        """
        Calls the Gemini API to generate an election education response.

        Args:
            user_query (str): The specific question asked by the user.

        Returns:
            str: The AI-generated educational response.

        Raises:
            ValueError: If the input query is empty.
            RuntimeError: If the Gemini API fails.
        """
        if not user_query or not user_query.strip():
            raise ValueError("Query cannot be empty.")

        logger.info(
            "Initiating Gemini API call",
            extra={"query_length": len(user_query)},
        )

        try:
            start_time = time.time()
            final_text = self._execute_generation(user_query)
            latency_ms = int((time.time() - start_time) * 1000)

            logger.info(f"Gemini response received. Latency: {latency_ms} ms")

            save_query(
                query=user_query,
                response=final_text,
                country="Global",
                latency_ms=latency_ms,
            )

            return final_text

        except Exception as e:
            logger.error("Gemini API Exception occurred", exc_info=True)
            raise RuntimeError(f"Failed to generate response: {str(e)}")

    def _execute_generation(self, user_query: str) -> str:
        """Executes the raw API call and extracts text."""
        logger.debug(f"Executing Gemini call with model: {settings.GEMINI_MODEL}")
        response = self._client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=f"{SYSTEM_PROMPT}\n\nUser Query: {user_query}",
        )

        if hasattr(response, "text") and response.text:
            return response.text

        logger.warning("Received empty text response from Gemini")
        return "Sorry, I couldn't generate a response."


def get_llm_service() -> LLMInterface:
    """
    Dependency injection provider for the LLM service.

    Returns:
        LLMInterface: An instance of the Gemini service.
    """
    return GeminiService()

import logging
import os
import re
from typing import Dict, Optional

from google.cloud import texttospeech

logger = logging.getLogger(__name__)

# Constants
DEFAULT_LANGUAGE_CODE = "en-US"
DEFAULT_VOICE_NAME = "en-US-Standard-A"

COUNTRY_VOICE_MAP: Dict[str, Dict[str, str]] = {
    "india": {"language_code": "en-IN", "name": "en-IN-Standard-A"},
    "uk": {"language_code": "en-GB", "name": "en-GB-Standard-A"},
    "canada": {"language_code": "en-CA", "name": "en-CA-Standard-A"},
    "australia": {"language_code": "en-AU", "name": "en-AU-Standard-A"},
}


def generate_speech(text: str, country: str) -> Optional[bytes]:
    """
    Generates audio from text using Google Cloud Text-to-Speech.

    Args:
        text (str): The text to synthesize into speech.
        country (str): Contextual country setting for accent selection.

    Returns:
        Optional[bytes]: The audio data as MP3 bytes, or None if failed.
    """
    logger.info(
        f"TTS Start: Generating speech. Text length: {len(text)}, Country: {country}"
    )

    try:
        # 1. Clean markdown and special characters
        clean_text = re.sub(r"[*_`~]", "", text)
        clean_text = re.sub(r"#+\s*", "", clean_text)

        # 2. Initialize Client with fallback logic
        client = _get_tts_client()
        if not client:
            return None

        # 3. Configure Synthesis Input
        synthesis_input = texttospeech.SynthesisInput(text=clean_text)

        # 4. Select Voice based on Country
        voice_params = COUNTRY_VOICE_MAP.get(
            country.lower(),
            {"language_code": DEFAULT_LANGUAGE_CODE, "name": DEFAULT_VOICE_NAME},
        )

        voice = texttospeech.VoiceSelectionParams(
            language_code=voice_params["language_code"], name=voice_params["name"]
        )

        # 5. Audio Configuration
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        # 6. Perform Synthesis
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        logger.info(f"TTS Success: Generated {len(response.audio_content)} bytes.")
        return response.audio_content

    except Exception as e:
        logger.error(f"TTS Failure: {e}", exc_info=True)
        return None


def _get_tts_client() -> Optional[texttospeech.TextToSpeechClient]:
    """
    Helper to initialize the TTS client with fallback credential handling.

    Returns:
        Optional[texttospeech.TextToSpeechClient]: The initialized client or None.
    """
    try:
        # Remove dummy Windows path if detected
        dummy_path = r"C:\full\path\to\key.json"
        if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") == dummy_path:
            logger.warning("Detected dummy credentials path. Clearing.")
            del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]

        return texttospeech.TextToSpeechClient()

    except Exception as auth_e:
        logger.warning(f"ADC initialization failed: {auth_e}. Trying local fallback.")
        # Attempt to find local firebase_key.json
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        key_path = os.path.join(base_dir, "firebase_key.json")

        if os.path.exists(key_path):
            return texttospeech.TextToSpeechClient.from_service_account_file(key_path)

        logger.error("No valid credentials found for Text-to-Speech.")
        return None

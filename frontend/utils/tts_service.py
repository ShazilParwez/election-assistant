import re
import logging
from google.cloud import texttospeech
import os

logger = logging.getLogger(__name__)

def generate_speech(text: str, country: str) -> bytes | None:
    """
    Generates audio from text using Google Cloud TTS.

    Args:
        text (str): The text to synthesize.
        country (str): Contextual country setting to define language accents.

    Returns:
        bytes | None: The audio data as in-memory bytes, or None if the request failed.
    """
    logger.info(f"TTS Start: Generating speech for text length {len(text)}, country: {country}")
    try:
        # Clean markdown safely (remove bold/italic markers but keep structure)
        clean_text = re.sub(r'[*_`~]', '', text)
        clean_text = re.sub(r'#+\s*', '', clean_text) # Remove headers
        
        # Initialize client. 
        # Attempt to use Application Default Credentials first, or explicitly load firebase_key.json 
        # if the environment variable is broken (e.g. C:\\full\\path\\to\\key.json).
        client = None
        
        # Check if GOOGLE_APPLICATION_CREDENTIALS is set to a dummy path and remove it locally
        dummy_path = r"C:\full\path\to\key.json"
        if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") == dummy_path:
            logger.warning(f"Detected dummy GOOGLE_APPLICATION_CREDENTIALS '{dummy_path}'. Ignoring it.")
            del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]

        try:
            client = texttospeech.TextToSpeechClient()
        except Exception as auth_e:
            logger.warning(f"ADC failed: {auth_e}. Trying firebase_key.json fallback.")
            key_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "firebase_key.json")
            if os.path.exists(key_path):
                client = texttospeech.TextToSpeechClient.from_service_account_file(key_path)
            else:
                raise auth_e # Re-raise if no fallback available

        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(text=clean_text)

        # Build the voice request, select the language code based on country
        language_code = "en-US"
        name = "en-US-Standard-A"
        
        country_lower = country.lower()
        if country_lower == "india":
            language_code = "en-IN"
            name = "en-IN-Standard-A"
        elif country_lower == "uk":
            language_code = "en-GB"
            name = "en-GB-Standard-A"
        elif country_lower == "canada":
            language_code = "en-CA"
            name = "en-CA-Standard-A"
        elif country_lower == "australia":
            language_code = "en-AU"
            name = "en-AU-Standard-A"

        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=name
        )

        # Select the type of audio file you want returned
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        # Perform the text-to-speech request
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        audio_bytes = response.audio_content
        logger.info(f"TTS Success: Generated {len(audio_bytes)} bytes of audio.")
        return audio_bytes
        
    except Exception as e:
        logger.error("TTS Failure: Error generating speech", exc_info=True)
        return None

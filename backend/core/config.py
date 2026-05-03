import logging
import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables and .env file.
    """

    PROJECT_NAME: str = "Interactive Election Education Assistant"
    VERSION: str = "1.0.0"
    API_V1_STR: str = ""

    HOST: str = "127.0.0.1"
    PORT: int = 8080
    DEBUG: bool = True

    LLM_API_KEY: str = ""
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()

if not settings.GOOGLE_API_KEY:
    logger.error("GOOGLE_API_KEY is missing in settings.")
    raise ValueError(
        "GOOGLE_API_KEY environment variable is missing. "
        "Please set it in your .env file."
    )

import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Interactive Election Education Assistant"
    VERSION: str = "1.0.0"
    API_V1_STR: str = ""
    
    HOST: str = "127.0.0.1"
    PORT: int = 8080
    DEBUG: bool = True
    
    LLM_API_KEY: str = ""
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True
    }

settings = Settings()

if not settings.GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is missing. Please set it in your .env file.")

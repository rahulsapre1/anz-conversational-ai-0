import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class Config:
    """Application configuration loaded from environment variables."""
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_VECTOR_STORE_ID_CUSTOMER: Optional[str] = os.getenv("OPENAI_VECTOR_STORE_ID_CUSTOMER")
    OPENAI_VECTOR_STORE_ID_BANKER: Optional[str] = os.getenv("OPENAI_VECTOR_STORE_ID_BANKER")
    
    # Supabase Configuration
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    
    # Application Configuration
    CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.68"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Authentication
    SESSION_PASSWORD: str = os.getenv("SESSION_PASSWORD", "rahul")
    
    # Timeouts
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "30"))  # 30 seconds default
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present."""
        required = [
            cls.OPENAI_API_KEY,
            cls.SUPABASE_URL,
            cls.SUPABASE_KEY,
        ]
        return all(required)
    
    @classmethod
    def get_missing_config(cls) -> list[str]:
        """Get list of missing required configuration keys."""
        missing = []
        if not cls.OPENAI_API_KEY:
            missing.append("OPENAI_API_KEY")
        if not cls.SUPABASE_URL:
            missing.append("SUPABASE_URL")
        if not cls.SUPABASE_KEY:
            missing.append("SUPABASE_KEY")
        return missing

# Note: Validation is checked in main.py to allow graceful error handling
# The app will display a helpful error message if configuration is missing

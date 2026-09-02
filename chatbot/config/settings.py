"""Chatbot configuration settings."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=_env_path)


class ChatbotConfig:
    """Chatbot configuration class."""

    # API Configuration
    API_KEY = os.environ.get("API_KEY", "")

    # Authentication
    SECRET_KEY = os.environ.get("secret", "your-secret-key-change-me")
    ALGORITHM = os.environ.get("algorithm", "HS256")

    # Gemini Model Configuration
    GEMINI_MODEL = "gemini-3.5-flash"
    GEMINI_TEMPERATURE = 0.7

    # RAG Configuration
    RAG_TOP_K = 3
    RAG_SIMILARITY_THRESHOLD = 0.4
    RAG_COLLECTION_NAME = "prescription_vectors"

    # Ollama Configuration
    OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/embed")
    OLLAMA_MODEL = "nomic-embed-text"

    # Database Configuration
    MONGODB_URL = os.environ.get("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_NAME = os.environ.get("MONGODB_NAME", "citycare")

    # Logging
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

    # Feature Flags
    ENABLE_RAG = True
    ENABLE_STREAMING = True
    ENABLE_TOOL_CALLING = True

    @classmethod
    def from_dict(cls, config_dict: dict):
        """Create config from dictionary."""
        for key, value in config_dict.items():
            if hasattr(cls, key):
                setattr(cls, key, value)
        return cls


# Default config instance
config = ChatbotConfig()

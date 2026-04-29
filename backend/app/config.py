"""Application configuration via pydantic-settings."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # LLM
    google_api_key: str
    google_model_name: str = "gemma-4-31b-it"

    # Security
    secret_key: str

    # App
    environment: str = "development"

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore",
    }


settings = Settings()

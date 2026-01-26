from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings configuration."""
    
    # API Keys
    OPENAI_API_KEY: str
    GOOGLE_API_KEY: str | None = None
    
    # Database - Pointing to the new sales.db
    DATABASE_URL: str = "sqlite:///./sales.db"
    
    # App Config
    APP_TITLE: str = "GenAI Text-to-SQL API (Sales Data)"
    APP_VERSION: str = "1.0.0"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()

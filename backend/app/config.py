"""Application configuration and settings."""
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # App
    APP_NAME: str = "AI Learning Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Server
    BACKEND_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:3000"
    
    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_CHAT_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSION: int = 1536
    
    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_KEY: Optional[str] = None
    
    # Perplexity
    PERPLEXITY_API_KEY: Optional[str] = None
    PERPLEXITY_RATE_LIMIT: int = 5  # searches per minute
    PERPLEXITY_CACHE_TTL: int = 604800  # 7 days in seconds
    
    # Search
    SEARCH_TOP_K: int = 5
    WEB_SEARCH_RELEVANCE_THRESHOLD: float = 0.40
    
    # Generation
    MAX_GENERATION_TOKENS: int = 4096
    GENERATION_TEMPERATURE: float = 0.7
    
    # Upload
    MAX_UPLOAD_SIZE: int = 52428800  # 50MB
    ALLOWED_EXTENSIONS: list = [
        ".pdf", ".pptx", ".docx", ".doc",
        ".py", ".js", ".ts", ".java", ".cpp", ".c", ".cs",
        ".md", ".txt", ".json", ".yaml", ".yml"
    ]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()

"""Application configuration."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    APP_NAME: str = "Transaction Ranking System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/transaction_ranking"
    
    # Redis (optional)
    REDIS_URL: Optional[str] = None
    
    # Security
    API_KEY_HEADER: str = "X-API-Key"
    MAX_TRANSACTION_AMOUNT: float = 1_000_000.0
    
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds
    
    # Abuse prevention
    MAX_TRANSACTIONS_PER_MINUTE: int = 10
    DUPLICATE_CHECK_WINDOW: int = 300  # seconds
    
    # Ranking
    POINTS_WEIGHT: float = 0.6
    ACTIVITY_WEIGHT: float = 20.0
    CONSISTENCY_WEIGHT: float = 20.0
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

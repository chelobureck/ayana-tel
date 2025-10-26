from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    TOKEN: str
    
    # FastAPI settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_TITLE: str = "Ayana Bot API"
    
    # Database settings
    USE_POSTGRES: Optional[str] = "false"
    DATABASE_URL: Optional[str] = None
    POSTGRES_USER: Optional[str] = "postgres"
    POSTGRES_PASSWORD: Optional[str] = ""
    POSTGRES_SERVER: Optional[str] = "localhost"
    POSTGRES_PORT: Optional[str] = "5432"
    POSTGRES_DB: Optional[str] = "ayana_db"
    
    # Redis settings
    REDIS_URL: Optional[str] = "redis://localhost:6379/0"
    USE_REDIS: Optional[str] = "true"
    
    # Environment
    ENVIRONMENT: str = "development"
    POSTGRES_SSL_VERIFY: Optional[str] = "true"

    model_config = SettingsConfigDict(env_file='.env', case_sensitive=True)

@lru_cache()
def get_settings() -> Settings:
    return Settings()  #type: ignore
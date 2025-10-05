from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    TOKEN: str

    model_config = SettingsConfigDict(env_file='.env', case_sensitive=True)

@lru_cache()
def get_settings() -> Settings:
    return Settings()  #type: ignore
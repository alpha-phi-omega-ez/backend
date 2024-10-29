from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
import os


class Settings(BaseSettings):
    ORIGINS: str = "http://localhost:3000"
    MONGO_DETAILS: str = "mongodb://localhost:27017"
    FRONTEND_URL: str = "http://localhost:3000"
    BACKEND_URL: str = "http://localhost:8000"
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 4
    SECRET_KEY: str = str(os.urandom(32))
    ALGORITHM: str = "HS256"

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings() -> Settings:
    return Settings()
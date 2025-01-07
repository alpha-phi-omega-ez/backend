import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ORIGINS: str = "http://localhost:3000"
    MONGO_DETAILS: str = "mongodb://localhost:27017"
    FRONTEND_URL: str = "http://localhost:3000"
    BACKEND_URL: str = "http://localhost:9000"
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 4
    SECRET_KEY: str = str(os.urandom(32))
    ALGORITHM: str = "HS256"
    TESTING: bool = os.getenv("TESTING", "False").lower() in ("true", "1", "t")

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

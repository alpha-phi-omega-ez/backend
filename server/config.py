import os
from functools import lru_cache

from pydantic import field_validator
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
    TESTING: bool = False

    @field_validator("TESTING", mode="before")
    @classmethod
    def parse_testing(cls, v):
        if isinstance(v, str):
            # Strip quotes if present
            v = v.strip("\"'")
            # Convert string to boolean
            return v.lower() in ("true", "1", "t", "yes")
        return bool(v)

    ROOT_PATH: str = os.getenv("ROOT_PATH", "")
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")
    SENTRY_TRACE_RATE: float = float(os.getenv("SENTRY_TRACE_RATE", 1.0))
    SENTRY_PROFILE_RATE: float = float(os.getenv("SENTRY_PROFILE_RATE", 1.0))
    VALKEY_ADDRESS: str = os.getenv("VALKEY_ADDRESS", "127.0.0.1")

    # Define routes to exclude from tracing and profiling
    EXCLUDED_ROUTES: set = {"/", "/openapi.json", "/docs"}

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

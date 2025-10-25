import os
from pydantic import BaseSettings


class Settings(BaseSettings):
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "sqlite+aiosqlite:///./app/data/wazfini.db"
    )
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")
    INGEST_INTERVAL_MIN: int = int(os.getenv("INGEST_INTERVAL_MIN", "10"))


settings = Settings()

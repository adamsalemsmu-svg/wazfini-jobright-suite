from __future__ import annotations

from datetime import timedelta
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )

    # App / runtime
    APP_ENV: str = Field(default="local")
    BASE_URL: str | None = None
    LOG_LEVEL: str = Field(default="INFO")

    # Security / auth
    SECRET_KEY: str = Field(default="0123456789abcdef0123456789abcdef", min_length=32)
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15, ge=1)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=15, ge=1)
    LOGIN_ATTEMPT_LIMIT: int = Field(default=5, ge=1)
    LOGIN_LOCKOUT_MINUTES: int = Field(default=15, ge=1)
    PASSWORD_MIN_LENGTH: int = Field(default=10, ge=8)
    PASSWORD_PASSPHRASE_LENGTH: int = Field(default=16, ge=12)
    PASSWORD_RESET_TOKEN_MINUTES: int = Field(default=30, ge=5)

    # Persistence / infra
    DATABASE_URL: str = Field(default="sqlite:///./app.db")
    REDIS_URL: str = Field(default="redis://localhost:6379/0")

    # Email / notifications
    EMAIL_SENDER: str = Field(default="noreply@example.com")
    SMTP_HOST: str | None = None
    SMTP_PORT: int = Field(default=587)
    SMTP_USER: str | None = None
    SMTP_PASS: str | None = None
    SENDGRID_API_KEY: str | None = None
    SENDGRID_FROM_EMAIL: str | None = None
    TWILIO_ACCOUNT_SID: str | None = None
    TWILIO_AUTH_TOKEN: str | None = None
    TWILIO_FROM_NUMBER: str | None = None

    # CORS / API
    CORS_ALLOW_ORIGINS: List[str] | None = None

    # Observability
    SENTRY_DSN: str | None = None

    # Feature flags
    AUTH_V2_ENABLED: bool = Field(default=True)

    @property
    def access_token_ttl(self) -> timedelta:
        return timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)

    @property
    def refresh_token_ttl(self) -> timedelta:
        return timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)

    @property
    def login_lockout_ttl(self) -> timedelta:
        return timedelta(minutes=self.LOGIN_LOCKOUT_MINUTES)

    @property
    def password_reset_token_ttl(self) -> timedelta:
        return timedelta(minutes=self.PASSWORD_RESET_TOKEN_MINUTES)

    @property
    def cors_origins(self) -> List[str]:
        if not self.CORS_ALLOW_ORIGINS:
            return []
        return [value.strip() for value in self.CORS_ALLOW_ORIGINS if value.strip()]


settings = Settings()

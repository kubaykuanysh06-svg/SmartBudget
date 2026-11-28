"""Application settings loaded from environment / .env file."""

from __future__ import annotations

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_INSECURE_SECRETS = {
    "",
    "change-me",
    "change-me-to-a-random-string",
    "secret",
}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Database ──────────────────────────────────────────
    DATABASE_URL: str = (
        "postgresql+asyncpg://smartbudget:smartbudget@localhost:5432/smartbudget"
    )

    # ── Redis ─────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── Auth / JWT ────────────────────────────────────────
    SECRET_KEY: str = "change-me-to-a-random-string"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── Gemini AI ─────────────────────────────────────────
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.5-flash-lite"

    # ── CORS ──────────────────────────────────────────────
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

    # ── App ───────────────────────────────────────────────
    APP_ENV: str = "development"
    DEBUG: bool = True

    @model_validator(mode="after")
    def _validate_production_secret(self) -> Settings:
        secret = self.SECRET_KEY.strip()
        if not self.DEBUG and (secret in _INSECURE_SECRETS or len(secret) < 32):
            raise ValueError(
                "SECRET_KEY must be a strong random string (>= 32 chars) when DEBUG is false"
            )
        return self


settings = Settings()

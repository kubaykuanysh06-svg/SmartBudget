"""Application settings loaded from environment / .env file."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


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

    # ── CORS ──────────────────────────────────────────────
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

    # ── App ───────────────────────────────────────────────
    APP_ENV: str = "development"
    DEBUG: bool = True


settings = Settings()

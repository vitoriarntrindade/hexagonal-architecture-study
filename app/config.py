"""Application settings loaded from environment variables or .env file.

All adapters and dependencies should import `get_settings()` and read
configuration from the returned instance — never hard-code secrets.

Example .env::

    JWT_SECRET=your-super-secret-key-with-at-least-32-chars
    JWT_ALGORITHM=HS256
    JWT_TTL_SECONDS=3600
    DATABASE_URL=sqlite:///./app.db
    ENV=development
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for the application.

    Attributes:
        jwt_secret: Secret key used to sign/verify JWT tokens.
            Must be at least 32 bytes for HS256 per RFC 7518.
        jwt_algorithm: HMAC algorithm used for token encoding.
        jwt_ttl_seconds: Token time-to-live in seconds.
        database_url: SQLAlchemy-compatible database URL.
        env: Runtime environment name (development, test, production).
    """

    jwt_secret: str = "dev-secret-key-change-me-in-production-please"
    jwt_algorithm: str = "HS256"
    jwt_ttl_seconds: int = 3600
    database_url: str = "sqlite:///./app.db"
    env: str = "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance.

    The cache is per-process so settings are read once from the environment.
    In tests, call ``get_settings.cache_clear()`` after patching env vars.

    Returns:
        A fully populated ``Settings`` instance.
    """
    return Settings()

"""Centralised runtime configuration for ReViewPoint.

Exposes a cached *singleton* named ``settings`` which the rest of the backend
imports::

    from core.config import settings

Values come from real environment variables or an ``.env`` file (path can be
changed via the ``ENV_FILE`` variable). Real env vars always win – matching the
12-factor rule.
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import List, Literal

from pydantic import Field, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ["Settings", "get_settings", "settings"]

ENV_PREFIX = "REVIEWPOINT_"

# Determine which .env to load *at import time* (not via a lambda).
ENV_FILE_PATH: Path | None = None
if env_file := os.getenv("ENV_FILE"):
    ENV_FILE_PATH = Path(env_file)
elif Path(".env").exists():
    ENV_FILE_PATH = Path(".env")


class Settings(BaseSettings):
    """Typed runtime configuration for the backend."""

    # ------------------------------------------------------------------
    # Meta / Environment
    # ------------------------------------------------------------------
    app_name: str = "ReViewPoint"
    environment: Literal["dev", "test", "prod"] = "dev"
    debug: bool = False

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    log_level: Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"] = "INFO"

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------
    db_url: str = Field(..., description="Async SQLAlchemy database URL")

    # ------------------------------------------------------------------
    # Security / Auth
    # ------------------------------------------------------------------
    jwt_secret: str = Field(..., repr=False)
    jwt_algorithm: str = "HS256"
    jwt_exp_minutes: int = 30

    # Password hashing
    pwd_hash_scheme: str = "pbkdf2_sha256"
    pwd_rounds: int = 100_000

    # ------------------------------------------------------------------
    # Uploads
    # ------------------------------------------------------------------
    upload_dir: Path = Path("uploads")
    max_upload_mb: int = 50

    # ------------------------------------------------------------------
    # CORS / Networking
    # ------------------------------------------------------------------
    allowed_origins: List[str] = []

    # ------------------------------------------------------------------
    # Feature Flags
    # ------------------------------------------------------------------
    enable_embeddings: bool = False

    # ------------------------------------------------------------------
    # Pydantic config
    # ------------------------------------------------------------------
    model_config = SettingsConfigDict(
        env_prefix=ENV_PREFIX,
        case_sensitive=False,
        env_file=str(ENV_FILE_PATH) if ENV_FILE_PATH else None,
    )

    # -------------------------- Validators ----------------------------
    @field_validator("db_url")
    @classmethod
    def _validate_db_scheme(cls, v: str) -> str:  # pylint: disable=no-self-argument
        allowed = ("postgresql+asyncpg://", "sqlite+aiosqlite://")
        if not v.startswith(allowed):
            raise ValueError(
                "db_url must start with postgresql+asyncpg:// or sqlite+aiosqlite://"
            )
        return v

    @field_validator("upload_dir", mode="after")
    @classmethod
    def _ensure_upload_dir(cls, v: Path) -> Path:  # pylint: disable=no-self-argument
        v.mkdir(parents=True, exist_ok=True)
        return v

    # --------------------------- Post-init ---------------------------
    def model_post_init(self, __context):  # type: ignore[override]
        """Apply environment-specific override logic after validation."""
        if self.environment == "test":
            object.__setattr__(self, "db_url", "sqlite+aiosqlite:///:memory:")
            object.__setattr__(self, "log_level", "WARNING")

    # ---------------------------- Helpers ----------------------------
    @property
    def async_db_url(self) -> str:
        """Alias for :attr:`db_url` (semantic sugar)."""
        return self.db_url

    @property
    def upload_path(self) -> Path:
        """Guaranteed-to-exist upload directory."""
        return self.upload_dir

    def to_public_dict(self) -> dict[str, str]:
        """Return a dict representation without sensitive fields."""
        data = self.model_dump()
        data.pop("jwt_secret", None)
        return data


# ----------------------------------------------------------------------
# Singleton access helpers
# ----------------------------------------------------------------------


@lru_cache
def get_settings() -> Settings:  # pragma: no cover
    try:
        return Settings()  # type: ignore[call-arg]
    except ValidationError as exc:  # pragma: no cover
        raise RuntimeError(f"Configuration error: {exc}") from exc


settings: Settings = get_settings()

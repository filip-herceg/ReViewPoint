"""
Centralized runtime configuration for ReViewPoint.

Import the cached singleton everywhere::

    from backend.core.config import settings

All variables are read from the REVIEWPOINT_* environment variables. A .env file is loaded as fallback,
or a custom path can be specified by setting ENV_FILE. Unknown variables are ignored, which is useful
for CI systems that inject extra environment variables.
"""

from __future__ import annotations

import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

from pydantic import Field, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ["Settings", "get_settings", "settings"]

ENV_PREFIX = "REVIEWPOINT_"

# Determine .env file path at import time
_env_path = os.getenv("ENV_FILE")
if _env_path:
    _ENV_FILE: Path | None = Path(_env_path)
elif Path(".env").exists():
    _ENV_FILE = Path(".env")
else:
    _ENV_FILE = None


class Settings(BaseSettings):
    """
    Typed runtime configuration container.

    Reads from environment variables with the REVIEWPOINT_ prefix, optionally loading from a .env file.
    """

    # Metadata
    app_name: str = "ReViewPoint"
    environment: Literal["dev", "test", "prod"] = "dev"
    debug: bool = False

    # Logging configuration
    log_level: Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"] = "INFO"

    # Database settings
    db_url: str = Field(..., description="Async SQLAlchemy database URL")

    # Authentication settings
    jwt_secret: str = Field(..., repr=False)
    jwt_algorithm: str = "HS256"
    jwt_exp_minutes: int = 30

    pwd_hash_scheme: str = "pbkdf2_sha256"
    pwd_rounds: int = 100_000

    # Upload settings
    upload_dir: Path = Path("uploads")
    max_upload_mb: int = 50

    # CORS settings
    allowed_origins: list[str] = []

    # Feature flags
    enable_embeddings: bool = False

    # Pydantic settings configuration
    model_config = SettingsConfigDict(
        env_prefix=ENV_PREFIX,
        case_sensitive=False,
        env_file=str(_ENV_FILE) if _ENV_FILE else None,
        extra="ignore",
    )

    @field_validator("db_url", mode="before")
    @classmethod
    def check_db_scheme(cls, v: str) -> str:
        """
        Ensure the database URL uses a supported scheme.

        Accepted schemes:
        - postgresql+asyncpg://
        - sqlite+aiosqlite://
        """
        if not v.startswith(("postgresql+asyncpg://", "sqlite+aiosqlite://")):
            raise ValueError(
                "db_url must use postgresql+asyncpg or sqlite+aiosqlite scheme"
            )
        return v

    @field_validator("upload_dir", mode="after")
    @classmethod
    def ensure_upload_dir_exists(cls, v: Path) -> Path:
        """
        Create the upload directory if it does not exist.
        """
        v.mkdir(parents=True, exist_ok=True)
        return v

    def model_post_init(self, __context: Any) -> None:
        """
        Post-initialization adjustments for specific environments.

        - In 'test' environment, use in-memory SQLite and set log level to WARNING.
        """
        if self.environment == "test":
            object.__setattr__(self, "db_url", "sqlite+aiosqlite:///:memory:")
            object.__setattr__(self, "log_level", "WARNING")

    @property
    def async_db_url(self) -> str:
        """Alias for the database URL to emphasize async usage."""
        return self.db_url

    @property
    def upload_path(self) -> Path:
        """Alias for the upload directory path."""
        return self.upload_dir

    def to_public_dict(self) -> dict[str, str]:
        """
        Return settings as a dict, excluding sensitive fields.
        """
        data = self.model_dump()
        data.pop("jwt_secret", None)
        return data


@lru_cache
def get_settings() -> Settings:
    """
    Return a cached singleton of Settings, raising RuntimeError on validation errors.
    """
    try:
        return Settings()  # type: ignore[call-arg]
    except ValidationError as exc:
        raise RuntimeError(f"Configuration error: {exc}") from exc


# Initialize settings and log the loaded configuration
settings: Settings = get_settings()
logger = logging.getLogger(__name__)
logger.debug("Settings initialized: %s", settings.to_public_dict())

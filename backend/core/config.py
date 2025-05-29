"""
Centralized runtime configuration for ReViewPoint.

Import the cached singleton everywhere::

    from backend.core.config import settings

All variables are read from the REVIEWPOINT_* environment variables. A .env file is loaded as fallback,
or a custom path can be specified by setting ENV_FILE. Unknown variables are ignored, which is useful
for CI systems that inject extra environment variables.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

from loguru import logger
from pydantic import Field, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ["Settings", "get_settings", "settings"]

ENV_PREFIX = "REVIEWPOINT_"

# Determine .env file path at import time
_env_path = os.getenv("ENV_FILE")
if _env_path:
    _env_file: Path | None = Path(_env_path)
elif Path(".env").exists():
    _env_file = Path(".env")
else:
    _env_file = None


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

    # Storage (Optional)
    storage_url: str | None = None
    storage_region: str | None = None
    storage_secure: bool = Field(
        False, description="Whether to use secure (SSL) connection for storage"
    )

    # Email (Optional)
    email_host: str | None = None
    email_port: int | None = None
    email_user: str | None = None
    email_password: str | None = None
    email_from: str | None = None

    # Monitoring (Optional)
    sentry_dsn: str | None = None
    loggly_token: str | None = None

    # Pydantic settings configuration
    model_config = SettingsConfigDict(
        env_prefix=ENV_PREFIX,
        case_sensitive=False,
        env_file=str(_env_file) if _env_file else None,
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

    @field_validator("storage_secure", mode="before")
    @classmethod
    def parse_storage_secure(cls, v: object) -> bool:
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in ("1", "true", "yes", "on")
        return bool(v)

    @field_validator("email_port", mode="before")
    @classmethod
    def parse_email_port(cls, v: object) -> int | None:
        if v is None:
            return None
        if isinstance(v, int):
            return v
        if isinstance(v, str):
            try:
                return int(v)
            except ValueError as err:
                raise ValueError("email_port must be an integer") from err
        raise TypeError("email_port must be an integer or string")

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
logger.debug("Settings initialized: %s", settings.to_public_dict())

"""Centralized runtime configuration for ReViewPoint.

Import the settings using the lazy getter everywhere::

    from src.core.config import get_settings
    settings = get_settings()

Never use a global `settings = Settings()` at import time. This ensures all environment variables are set before config is loaded, especially in tests.

All variables are read from the REVIEWPOINT_* environment variables. A .env file is loaded as fallback,
or a custom path can be specified by setting ENV_FILE. Unknown variables are ignored, which is useful
for CI systems that inject extra environment variables.
"""

from __future__ import annotations

import os
import sys
from collections.abc import Mapping
from functools import lru_cache
from pathlib import Path
from typing import (
    Any,
    ClassVar,
    Final,
    Literal,
)

from loguru import logger
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ["Settings", "get_settings"]


ENV_PREFIX: Final[str] = "REVIEWPOINT_"


# Determine .env file path at import time, but skip if running under pytest (test suite)
IS_PYTEST: Final[bool] = "pytest" in sys.modules or any(
    "PYTEST_CURRENT_TEST" in k for k in os.environ
)
_env_path: str | None = os.getenv("ENV_FILE")
_env_file: Path | None
if IS_PYTEST:
    _env_file = None  # Always ignore .env during tests
    if (
        _env_path
        or Path("config/.env").exists()
        or Path("backend/config/.env").exists()
        or Path("backend/.env").exists()
    ):
        # Defensive: log if any .env file would have been loaded during tests
        # Only warn, do not print or log debug/devlog
        try:
            logger.warning(
                f"Prevented .env loading during tests. ENV_FILE={_env_path}, "
                f"config/.env exists={Path('config/.env').exists()}, "
                f"backend/config/.env exists={Path('backend/config/.env').exists()}, "
                f"backend/.env exists={Path('backend/.env').exists()}",
            )
        except Exception:
            pass
elif _env_path:
    _env_file = Path(_env_path)
elif Path("config/.env").exists():
    _env_file = Path("config/.env")
elif Path("backend/config/.env").exists():
    _env_file = Path("backend/config/.env")
elif Path("backend/.env").exists():
    _env_file = Path("backend/.env")
else:
    _env_file = None


class Settings(BaseSettings):
    """Typed runtime configuration container.

    Reads from environment variables with the REVIEWPOINT_ prefix, optionally loading from a .env file.
    """

    # Metadata

    app_name: str = "ReViewPoint"
    environment: Literal["dev", "test", "prod"] = "dev"
    debug: bool = False

    # Logging configuration
    log_level: Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"] = "INFO"

    # Database settings
    db_url: str | None = Field(
        default=None,
        description="Async SQLAlchemy database URL",
    )

    # Authentication settings

    auth_enabled: bool = Field(
        True,
        description="Enable or disable authentication features (env: REVIEWPOINT_AUTH_ENABLED)",
    )
    jwt_secret_key: str | None = Field(
        None,
        repr=False,
        description="Secret key for JWT signing (env: REVIEWPOINT_JWT_SECRET_KEY)",
    )
    jwt_algorithm: str = Field(
        "HS256",
        description="JWT signing algorithm (env: REVIEWPOINT_JWT_ALGORITHM)",
    )
    jwt_expire_minutes: int = Field(
        30,
        description="JWT expiration in minutes (env: REVIEWPOINT_JWT_EXPIRE_MINUTES)",
    )
    # Backward compatibility: allow jwt_secret as alias for jwt_secret_key
    jwt_secret: str | None = Field(
        None,
        repr=False,
        description="[DEPRECATED] Use jwt_secret_key instead.",
    )

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
        False,
        description="Whether to use secure (SSL) connection for storage",
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

    # API URLs for OpenAPI servers
    api_local_url: str = Field(
        "http://localhost:8000",
        description="Local API server URL for OpenAPI schema",
    )
    api_prod_url: str = Field(
        "https://api.reviewpoint.org",
        description="Production API server URL for OpenAPI schema",
    )

    # API Key
    api_key_enabled: bool = Field(default=True, description="Enable API key validation")
    api_key: str | None = Field(
        default=None,
        repr=False,
        description="API key for authentication (env: REVIEWPOINT_API_KEY)",
    )

    # Pydantic settings configuration

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_prefix=ENV_PREFIX,
        case_sensitive=False,
        env_file=None if IS_PYTEST else (str(_env_file) if _env_file else None),
        extra="ignore",
        # env_map removed; use Field(..., alias=...) for env var mapping if
        # needed
    )

    @field_validator("db_url", mode="before")
    @classmethod
    def check_db_scheme(cls: type[Settings], v: str | None) -> str:
        """Ensure the database URL uses a supported scheme and is not empty.

        Accepted schemes:
        - postgresql+asyncpg:// (production, dev)
        - sqlite+aiosqlite:// (dev, testing)

        :param v: The database URL string or None.
        :raises RuntimeError: If DB URL is missing in production mode.
        :raises ValueError: If DB URL uses an unsupported scheme.
        :return: The validated database URL string.
        """
        is_explicit_test_mode: bool = (
            os.environ.get("REVIEWPOINT_ENVIRONMENT") == "test"
            or os.environ.get("FAST_TESTS") == "1"
            or os.environ.get("REVIEWPOINT_TEST_MODE") == "1"
        )
        is_dev_mode: bool = os.environ.get("REVIEWPOINT_ENVIRONMENT") == "dev"

        if not v:
            if not is_explicit_test_mode:
                raise RuntimeError("Missing database URL: set REVIEWPOINT_DB_URL")
            v = "sqlite+aiosqlite:///:memory:"

        if v.startswith("postgresql+asyncpg://"):
            return v
        if v.startswith("sqlite+aiosqlite://"):
            if is_explicit_test_mode or is_dev_mode:
                return v
            raise ValueError(
                "SQLite database is only allowed in dev or test environments",
            )
        accepted_schemes: str = "postgresql+asyncpg://"
        if is_explicit_test_mode or is_dev_mode:
            accepted_schemes += " or sqlite+aiosqlite://"
        raise ValueError(f"db_url must use {accepted_schemes} scheme")

    def model_post_init(self: Settings, __context: object) -> None:
        """Post-initialization adjustments for specific environments.
        - If environment is 'test', override DB URL to use SQLite in memory
        - If jwt_secret_key is not set but jwt_secret is, use it (for backward compatibility)
        - Raise error if neither is set (only in production mode)

        :param __context: Context object (unused).
        :raises RuntimeError: If JWT secret is missing in production mode.
        """
        is_explicit_test_mode: bool = (
            os.environ.get("REVIEWPOINT_ENVIRONMENT") == "test"
            or os.environ.get("FAST_TESTS") == "1"
            or os.environ.get("REVIEWPOINT_TEST_MODE") == "1"
        )
        if (
            self.environment == "test"
            and os.environ.get("REVIEWPOINT_ENVIRONMENT") == "test"
        ):
            object.__setattr__(self, "db_url", "sqlite+aiosqlite:///:memory:")
            object.__setattr__(self, "log_level", "WARNING")
        if not getattr(self, "jwt_secret_key", None) and getattr(
            self,
            "jwt_secret",
            None,
        ):
            object.__setattr__(self, "jwt_secret_key", self.jwt_secret)
        if not getattr(self, "jwt_secret_key", None) and not is_explicit_test_mode:
            raise RuntimeError(
                "Missing JWT secret: set REVIEWPOINT_JWT_SECRET_KEY or legacy REVIEWPOINT_JWT_SECRET.",
            )
        logger.debug("Settings initialized for environment: {}", self.environment)

    @field_validator("upload_dir", mode="after")
    @classmethod
    def ensure_upload_dir_exists(cls: type[Settings], v: Path) -> Path:
        """Create the upload directory if it does not exist.

        :param v: The upload directory path.
        :return: The ensured upload directory path.
        """
        v.mkdir(parents=True, exist_ok=True)
        return v

    @field_validator("storage_secure", mode="before")
    @classmethod
    def parse_storage_secure(cls: type[Settings], v: object) -> bool:
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in ("1", "true", "yes", "on")
        return bool(v)

    @field_validator("email_port", mode="before")
    @classmethod
    def parse_email_port(cls: type[Settings], v: object) -> int | None:
        if v is None:
            return None
        if isinstance(v, int):
            return v
        if isinstance(v, str):
            # Handle empty strings as None
            if v.strip() == "":
                return None
            try:
                return int(v)
            except ValueError as err:
                raise ValueError("email_port must be an integer") from err
        raise TypeError("email_port must be an integer or string")

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls: type[Settings], v: object) -> list[str]:
        if v is None:
            return []
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            # Try to parse as JSON array
            try:
                import json

                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return [str(item) for item in parsed]
                # If it's a single string, split by comma
                return [item.strip() for item in v.split(",") if item.strip()]
            except json.JSONDecodeError:
                # If JSON parsing fails, split by comma
                return [item.strip() for item in v.split(",") if item.strip()]
        raise TypeError("allowed_origins must be a list or string")

    def __init__(self: Settings, **values: Any) -> None:
        super().__init__(**values)

    @property
    def async_db_url(self: Settings) -> str:
        """Alias for the database URL to emphasize async usage."""
        if self.db_url is None:
            raise RuntimeError("Database URL is not configured")
        return self.db_url

    @property
    def upload_path(self: Settings) -> Path:
        """Alias for the upload directory path."""
        return self.upload_dir

    def to_public_dict(self: Settings) -> Mapping[str, str]:
        """Return settings as a dict, excluding sensitive fields.

        :return: Mapping of public settings.
        """
        data: dict[str, str] = self.model_dump()
        data.pop("jwt_secret", None)
        data.pop("jwt_secret_key", None)
        return data


@lru_cache
def get_settings() -> Settings:
    """Lazily load and cache the Settings instance.

    :return: The cached Settings instance.
    """
    s: Settings = Settings()
    return s


def clear_settings_cache() -> None:
    """Clear the settings cache. Useful for tests when environment variables change.

    :return: None
    """
    get_settings.cache_clear()


def reload_settings() -> Settings:
    """Force reload settings from environment. Useful for tests.

    :return: The reloaded Settings instance.
    """
    clear_settings_cache()
    return get_settings()


# Create a module-level settings object for backward compatibility with tests


class SettingsProxy:
    """Proxy object that always returns the current settings"""

    def __getattr__(self, name: str) -> object:
        return getattr(get_settings(), name)


settings: Final[SettingsProxy] = SettingsProxy()


# Remove eager settings initialization! Use get_settings() everywhere.
# ENFORCEMENT: Never create a global settings = Settings() at import time. Always use get_settings().
# This is critical for testability and correct environment variable handling.

"""Centralised runtime configuration for ReViewPoint.

`settings` is the singleton import used by the whole backend::

    from core.config import settings

Configuration is read from `REVIEWPOINT_*` environment variables; a fallback
`.env` file is loaded if present (or a custom path is supplied via `ENV_FILE`).
Unknown variables are silently ignored so CI/CD can set unrelated vars without
breaking startup.
"""

from __future__ import annotations

# -----------------------------------------------------------------------------
# Stdlib imports
# -----------------------------------------------------------------------------
import os
from functools import lru_cache
from pathlib import Path
from typing import List, Literal

# -----------------------------------------------------------------------------
# Third‑party imports
# -----------------------------------------------------------------------------
from pydantic import Field, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ["Settings", "get_settings", "settings"]

ENV_PREFIX = "REVIEWPOINT_"

# -----------------------------------------------------------------------------
# Decide which .env file to use (once at import time)
# -----------------------------------------------------------------------------
if (env_path := os.getenv("ENV_FILE")) :
    _ENV_FILE = Path(env_path)
elif Path(".env").exists():
    _ENV_FILE = Path(".env")
else:
    _ENV_FILE: Path | None = None


# -----------------------------------------------------------------------------
# Settings model
# -----------------------------------------------------------------------------
class Settings(BaseSettings):
    """Typed runtime configuration container."""

    # ░░ Meta ░░
    app_name: str = "ReViewPoint"
    environment: Literal["dev", "test", "prod"] = "dev"
    debug: bool = False

    # ░░ Logging ░░
    log_level: Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"] = "INFO"

    # ░░ Database ░░
    db_url: str = Field(..., description="Async SQLAlchemy database URL")

    # ░░ Auth ░░
    jwt_secret: str = Field(..., repr=False)
    jwt_algorithm: str = "HS256"
    jwt_exp_minutes: int = 30

    pwd_hash_scheme: str = "pbkdf2_sha256"
    pwd_rounds: int = 100_000

    # ░░ Uploads ░░
    upload_dir: Path = Path("uploads")
    max_upload_mb: int = 50

    # ░░ CORS ░░
    allowed_origins: List[str] = []

    # ░░ Feature Flags ░░
    enable_embeddings: bool = False

    # pydantic‑settings meta
    model_config = SettingsConfigDict(
        env_prefix=ENV_PREFIX,
        case_sensitive=False,
        env_file=str(_ENV_FILE) if _ENV_FILE else None,
        extra="ignore",  # ignore unrelated env vars like REVIEWPOINT_OPENAI_API_KEY
    )

    # ---------------- Validators ----------------
    @field_validator("db_url", mode="before")
    @classmethod
    def _check_db_scheme(cls, v: str) -> str:  # pylint: disable=no-self-argument
        if not v.startswith(("postgresql+asyncpg://", "sqlite+aiosqlite://")):
            raise ValueError("db_url must use postgresql+asyncpg or sqlite+aiosqlite scheme")
        return v

    @field_validator("upload_dir", mode="after")
    @classmethod
    def _ensure_dir(cls, v: Path) -> Path:  # pylint: disable=no-self-argument
        v.mkdir(parents=True, exist_ok=True)
        return v

    # -------------- Post‑init tweaks --------------
    def model_post_init(self, __ctx):  # type: ignore[override]
        if self.environment == "test":
            object.__setattr__(self, "db_url", "sqlite+aiosqlite:///:memory:")
            object.__setattr__(self, "log_level", "WARNING")

    # ----------------- Helpers -------------------
    @property
    def async_db_url(self) -> str:
        return self.db_url

    @property
    def upload_path(self) -> Path:
        return self.upload_dir

    def to_public_dict(self) -> dict[str, str]:
        d = self.model_dump()
        d.pop("jwt_secret", None)
        return d


# -----------------------------------------------------------------------------
# Singleton factory
# -----------------------------------------------------------------------------
@lru_cache
def get_settings() -> Settings:  # pragma: no cover
    try:
        return Settings()  # type: ignore[call-arg]
    except ValidationError as exc:  # pragma: no cover
        raise RuntimeError(f"Configuration error: {exc}") from exc


settings: Settings = get_settings()

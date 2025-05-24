from __future__ import annotations

import importlib
import logging
import sys
from json import dumps
from pathlib import Path
from types import ModuleType

import pytest

MODULE = "core.config"
PFX = "REVIEWPOINT_"  # env-var prefix


# --------------------------------------------------------------------------- #
# Helpers                                                                     #
# --------------------------------------------------------------------------- #
def _clear_module() -> None:
    """Drop cached singleton + module so we can reload with fresh env."""
    if MODULE in sys.modules:
        cfg = sys.modules[MODULE]
        if hasattr(cfg, "get_settings"):
            cfg.get_settings.cache_clear()  # type: ignore[attr-defined]
        del sys.modules[MODULE]


def _reload(monkeypatch, **env: str) -> ModuleType:
    """
    Reload core.config with custom env overrides.

    Example:
        cfg = _reload(monkeypatch, DB_URL="postgres://...", JWT_SECRET="x")
    """
    _clear_module()
    for k, v in env.items():
        monkeypatch.setenv(f"{PFX}{k}", v)
    return importlib.import_module(MODULE)


# --------------------------------------------------------------------------- #
# Mandatory / precedence tests                                                #
# --------------------------------------------------------------------------- #
def test_env_precedence(monkeypatch, tmp_path: Path):
    """Real ENV beats value from .env file."""
    envfile = tmp_path / ".env"
    envfile.write_text(
        "REVIEWPOINT_DB_URL=postgresql+asyncpg://dotenv\n"
        "REVIEWPOINT_JWT_SECRET=dummy\n"
    )
    monkeypatch.setenv("ENV_FILE", str(envfile))
    override = "postgresql+asyncpg://env"
    cfg = _reload(monkeypatch, DB_URL=override, JWT_SECRET="dummy")
    assert cfg.settings.db_url == override


def test_missing_jwt_secret(monkeypatch):
    monkeypatch.delenv("REVIEWPOINT_JWT_SECRET", raising=False)
    with pytest.raises(RuntimeError):
        _reload(monkeypatch, DB_URL="postgresql+asyncpg://db")


def test_missing_db_url(monkeypatch):
    monkeypatch.delenv("REVIEWPOINT_DB_URL", raising=False)
    with pytest.raises(RuntimeError):
        _reload(monkeypatch, JWT_SECRET="secret")


# --------------------------------------------------------------------------- #
# Representation / singleton                                                  #
# --------------------------------------------------------------------------- #
def test_repr_hides_secret(monkeypatch):
    secret = "supersecret"
    cfg = _reload(monkeypatch, DB_URL="postgresql+asyncpg://db", JWT_SECRET=secret)
    assert secret not in repr(cfg.settings)


def test_singleton_identity(monkeypatch):
    cfg1 = _reload(monkeypatch, DB_URL="postgresql+asyncpg://db", JWT_SECRET="s")
    cfg2 = importlib.reload(sys.modules[MODULE])  # no env change
    assert cfg1.settings is cfg2.settings


# --------------------------------------------------------------------------- #
# Helper properties                                                            #
# --------------------------------------------------------------------------- #
def test_async_db_url(monkeypatch):
    url = "postgresql+asyncpg://u:p@h/db"
    cfg = _reload(monkeypatch, DB_URL=url, JWT_SECRET="s")
    assert cfg.settings.async_db_url == url


def test_upload_dir_creates_path(tmp_path: Path, monkeypatch):
    upload = tmp_path / "uploads"
    cfg = _reload(
        monkeypatch,
        DB_URL="postgresql+asyncpg://db",
        JWT_SECRET="s",
        UPLOAD_DIR=str(upload),
    )
    # property should coerce to Path and directory should exist
    assert cfg.settings.upload_path.exists()
    assert cfg.settings.upload_path.is_dir()


# --------------------------------------------------------------------------- #
# Environment == test overrides                                               #
# --------------------------------------------------------------------------- #
def test_test_env_overrides(monkeypatch):
    cfg = _reload(
        monkeypatch,
        ENVIRONMENT="test",
        DB_URL="postgresql+asyncpg://ignored",
        JWT_SECRET="s",
    )
    assert cfg.settings.environment == "test"
    assert cfg.settings.db_url.startswith("sqlite+aiosqlite:///:memory")
    assert cfg.settings.log_level == "WARNING"


# --------------------------------------------------------------------------- #
# Validation specifics                                                        #
# --------------------------------------------------------------------------- #
def test_invalid_db_scheme_rejected(monkeypatch):
    with pytest.raises(RuntimeError):
        _reload(monkeypatch, DB_URL="mysql://oops", JWT_SECRET="s")


def test_log_level_override(monkeypatch):
    cfg = _reload(
        monkeypatch,
        DB_URL="postgresql+asyncpg://db",
        JWT_SECRET="s",
        LOG_LEVEL="DEBUG",
    )
    assert cfg.settings.log_level == "DEBUG"


def test_allowed_origins_json_parsing(monkeypatch):
    lst = ["https://foo.com", "https://bar.com"]
    cfg = _reload(
        monkeypatch,
        DB_URL="postgresql+asyncpg://db",
        JWT_SECRET="s",
        ALLOWED_ORIGINS=dumps(lst),
    )
    assert cfg.settings.allowed_origins == lst


def test_feature_flags_bool(monkeypatch):
    cfg = _reload(
        monkeypatch,
        DB_URL="postgresql+asyncpg://db",
        JWT_SECRET="s",
        ENABLE_EMBEDDINGS="true",
    )
    assert cfg.settings.enable_embeddings is True


def test_password_rounds_int(monkeypatch):
    cfg = _reload(
        monkeypatch,
        DB_URL="postgresql+asyncpg://db",
        JWT_SECRET="s",
        PWD_ROUNDS="120000",
    )
    assert cfg.settings.pwd_rounds == 120000


def test_public_dict_filters_secrets(monkeypatch):
    cfg = _reload(
        monkeypatch,
        DB_URL="postgresql+asyncpg://db",
        JWT_SECRET="s",
    )
    public = cfg.settings.to_public_dict()
    assert "jwt_secret" not in public
    assert public["db_url"].startswith("postgresql")


def test_settings_debug_logged(monkeypatch, caplog):
    # Setze ENV so, dass get_settings() erfolgreich lädt
    monkeypatch.setenv("REVIEWPOINT_DB_URL", "postgresql+asyncpg://db")
    monkeypatch.setenv("REVIEWPOINT_JWT_SECRET", "secret")

    # Log-Level auf DEBUG, damit Debug-Messages durchkommen
    caplog.set_level(logging.DEBUG, logger="core.config")

    # Modul neu laden und Settings instanziieren
    _ = _reload(monkeypatch, DB_URL="postgresql+asyncpg://db", JWT_SECRET="secret")

    # Prüfe, dass der Debug-Log mit unserem Marker eintrifft
    assert any(
        "Settings initialized" in record.getMessage() for record in caplog.records
    ), "Expected a 'Settings initialized' debug log in core.config"

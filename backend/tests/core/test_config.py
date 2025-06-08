from __future__ import annotations

import importlib
import logging
import sys
from json import dumps
from pathlib import Path
from types import ModuleType

import pytest
from _pytest.monkeypatch import MonkeyPatch

from src.core.config import settings
from src.core.security import create_access_token, verify_access_token

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
            cfg.get_settings.cache_clear()
        del sys.modules[MODULE]


def _reload(monkeypatch: MonkeyPatch, **env: str) -> ModuleType:
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
def test_env_precedence(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
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


def test_missing_jwt_secret(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.delenv("REVIEWPOINT_JWT_SECRET", raising=False)
    with pytest.raises(RuntimeError):
        _reload(monkeypatch, DB_URL="postgresql+asyncpg://db")


def test_missing_db_url(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.delenv("REVIEWPOINT_DB_URL", raising=False)
    with pytest.raises(RuntimeError):
        _reload(monkeypatch, JWT_SECRET="secret")


# --------------------------------------------------------------------------- #
# Representation / singleton                                                  #
# --------------------------------------------------------------------------- #
def test_repr_hides_secret(monkeypatch: MonkeyPatch) -> None:
    secret = "supersecret"
    cfg = _reload(monkeypatch, DB_URL="postgresql+asyncpg://db", JWT_SECRET=secret)
    assert secret not in repr(cfg.settings)


def test_singleton_identity(monkeypatch: MonkeyPatch) -> None:
    cfg1 = _reload(monkeypatch, DB_URL="postgresql+asyncpg://db", JWT_SECRET="s")
    cfg2 = importlib.reload(sys.modules[MODULE])  # no env change
    assert cfg1.settings is cfg2.settings


# --------------------------------------------------------------------------- #
# Helper properties                                                            #
# --------------------------------------------------------------------------- #
def test_async_db_url(monkeypatch: MonkeyPatch) -> None:
    url = "postgresql+asyncpg://u:p@h/db"
    cfg = _reload(monkeypatch, DB_URL=url, JWT_SECRET="s")
    assert cfg.settings.async_db_url == url


def test_upload_dir_creates_path(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
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
def test_test_env_overrides(monkeypatch: MonkeyPatch) -> None:
    cfg = _reload(
        monkeypatch,
        ENVIRONMENT="test",
        DB_URL="postgresql+asyncpg://ignored",
        JWT_SECRET="s",
    )
    assert cfg.settings.environment == "test"
    # The DB URL should now be file-based, not in-memory
    assert cfg.settings.db_url.startswith("sqlite+aiosqlite:///"), cfg.settings.db_url
    assert cfg.settings.log_level == "WARNING"


# --------------------------------------------------------------------------- #
# Validation specifics                                                        #
# --------------------------------------------------------------------------- #
def test_invalid_db_scheme_rejected(monkeypatch: MonkeyPatch) -> None:
    with pytest.raises(RuntimeError):
        _reload(monkeypatch, DB_URL="mysql://oops", JWT_SECRET="s")


def test_log_level_override(monkeypatch: MonkeyPatch) -> None:
    cfg = _reload(
        monkeypatch,
        DB_URL="postgresql+asyncpg://db",
        JWT_SECRET="s",
        LOG_LEVEL="DEBUG",
    )
    assert cfg.settings.log_level == "DEBUG"


def test_allowed_origins_json_parsing(monkeypatch: MonkeyPatch) -> None:
    lst = ["https://foo.com", "https://bar.com"]
    cfg = _reload(
        monkeypatch,
        DB_URL="postgresql+asyncpg://db",
        JWT_SECRET="s",
        ALLOWED_ORIGINS=dumps(lst),
    )
    assert cfg.settings.allowed_origins == lst


def test_feature_flags_bool(monkeypatch: MonkeyPatch) -> None:
    cfg = _reload(
        monkeypatch,
        DB_URL="postgresql+asyncpg://db",
        JWT_SECRET="s",
        ENABLE_EMBEDDINGS="true",
    )
    assert cfg.settings.enable_embeddings is True


def test_password_rounds_int(monkeypatch: MonkeyPatch) -> None:
    cfg = _reload(
        monkeypatch,
        DB_URL="postgresql+asyncpg://db",
        JWT_SECRET="s",
        PWD_ROUNDS="120000",
    )
    assert cfg.settings.pwd_rounds == 120000


def test_public_dict_filters_secrets(monkeypatch: MonkeyPatch) -> None:
    cfg = _reload(
        monkeypatch,
        DB_URL="postgresql+asyncpg://db",
        JWT_SECRET="s",
    )
    public = cfg.settings.to_public_dict()
    assert "jwt_secret" not in public
    assert public["db_url"].startswith("postgresql")


def test_settings_debug_logged(
    monkeypatch: MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
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


def test_optional_env_vars(monkeypatch: MonkeyPatch) -> None:
    cfg = _reload(
        monkeypatch,
        DB_URL="postgresql+asyncpg://db",
        JWT_SECRET="s",
        STORAGE_URL="s3://bucket",
        STORAGE_REGION="us-east-1",
        STORAGE_SECURE="true",
        EMAIL_HOST="smtp.example.com",
        EMAIL_PORT="2525",
        EMAIL_USER="user",
        EMAIL_PASSWORD="pw",
        EMAIL_FROM="from@example.com",
        SENTRY_DSN="dsn",
        LOGGLY_TOKEN="token",
    )
    s = cfg.settings
    assert s.storage_url == "s3://bucket"
    assert s.storage_region == "us-east-1"
    assert s.storage_secure is True
    assert s.email_host == "smtp.example.com"
    assert s.email_port == 2525
    assert s.email_user == "user"
    assert s.email_password == "pw"
    assert s.email_from == "from@example.com"
    assert s.sentry_dsn == "dsn"
    assert s.loggly_token == "token"


def test_jwt_config_fields(monkeypatch: MonkeyPatch) -> None:
    cfg = _reload(
        monkeypatch,
        DB_URL="postgresql+asyncpg://db",
        JWT_SECRET_KEY="supersecret",
        JWT_ALGORITHM="HS512",
        JWT_EXPIRE_MINUTES="123",
        AUTH_ENABLED="false",
    )
    s = cfg.settings
    assert s.jwt_secret_key == "supersecret"
    assert s.jwt_algorithm == "HS512"
    assert s.jwt_expire_minutes == 123
    assert s.auth_enabled is False


def test_jwt_config_defaults(monkeypatch: MonkeyPatch) -> None:
    cfg = _reload(
        monkeypatch,
        DB_URL="postgresql+asyncpg://db",
        JWT_SECRET_KEY="abc",
    )
    s = cfg.settings
    assert s.jwt_algorithm == "HS256"
    assert s.jwt_expire_minutes == 30
    assert s.auth_enabled is True


def test_jwt_secret_legacy(monkeypatch: MonkeyPatch) -> None:
    # Only set legacy JWT_SECRET, not JWT_SECRET_KEY
    cfg = _reload(
        monkeypatch,
        DB_URL="postgresql+asyncpg://db",
        JWT_SECRET="legacysecret",
    )
    s = cfg.settings
    assert s.jwt_secret_key == "legacysecret"
    # Both fields should be hidden from public dict
    public = s.to_public_dict()
    assert "jwt_secret" not in public
    assert "jwt_secret_key" not in public


def test_auth_enabled_toggle(monkeypatch: MonkeyPatch) -> None:
    cfg = _reload(
        monkeypatch,
        DB_URL="postgresql+asyncpg://db",
        JWT_SECRET_KEY="s",
        AUTH_ENABLED="0",
    )
    assert cfg.settings.auth_enabled is False
    cfg2 = _reload(
        monkeypatch,
        DB_URL="postgresql+asyncpg://db",
        JWT_SECRET_KEY="s",
        AUTH_ENABLED="1",
    )
    assert cfg2.settings.auth_enabled is True


def test_verify_access_token_bypass(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "auth_enabled", False)
    token = create_access_token({"sub": "anyuser", "role": "user"})
    payload = verify_access_token(token)
    assert payload["sub"] == "dev-user"
    assert payload["role"] == "admin"
    assert payload["is_authenticated"] is True
    monkeypatch.setattr(settings, "auth_enabled", True)


def test_verify_access_token_invalid_token_bypass(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "auth_enabled", False)
    payload = verify_access_token("not.a.jwt.token")
    assert payload["sub"] == "dev-user"
    monkeypatch.setattr(settings, "auth_enabled", True)


def test_verify_access_token_expired_token_bypass(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "auth_enabled", False)
    import time

    expired_token = create_access_token(
        {"sub": "expired", "exp": int(time.time()) - 1000}
    )
    payload = verify_access_token(expired_token)
    assert payload["sub"] == "dev-user"
    monkeypatch.setattr(settings, "auth_enabled", True)

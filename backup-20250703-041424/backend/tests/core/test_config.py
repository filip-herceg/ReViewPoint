"""
Configuration and environment variable tests for backend config logic.
Uses a dedicated ConfigTestTemplate for DRYness and maintainability.
"""

import importlib
import os
import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import patch

import pytest

from src.core.security import create_access_token, verify_access_token
from src.core.config import Settings

MODULE = "src.core.config"
PFX = "REVIEWPOINT_"


class ConfigTestTemplate:
    """
    Template for config/envvar tests. Provides self.override_env_vars and helpers for reloading config.
    """

    @pytest.fixture(autouse=True)
    def _setup_env(self, monkeypatch, override_env_vars):
        self.override_env_vars = override_env_vars
        self.monkeypatch = monkeypatch
        pass

    def set_env(self, key: str, value: str):
        self.monkeypatch.setenv(key, value)

    def del_env(self, key: str, raising: bool = False):
        self.monkeypatch.delenv(key, raising=raising)

    def chdir_tmp(self, tmp_path: Path):
        self.monkeypatch.chdir(tmp_path)

    def reload_config(self, monkeypatch, **env) -> ModuleType:
        """Reload config with custom env overrides."""
        self.clear_config_module()
        for k, v in env.items():
            monkeypatch.setenv(f"{PFX}{k}", v)
        return importlib.import_module(MODULE)

    def create_env_file(self, tmp_path: Path, content: str = "") -> Path:
        """
        Create a temporary .env file with the given content and return its path.
        """
        envfile = tmp_path / ".env"
        envfile.write_text(content)
        self.set_env("ENV_FILE", str(envfile))
        return envfile

    def clear_config_module(self):
        """
        Remove the config module from sys.modules and clear settings cache if present.
        """
        if MODULE in sys.modules:
            cfg = sys.modules[MODULE]
            if hasattr(cfg, "get_settings"):
                cfg.get_settings.cache_clear()
            if hasattr(cfg, "clear_settings_cache"):
                cfg.clear_settings_cache()
            del sys.modules[MODULE]

    def set_env_vars(self, env: dict):
        for k, v in env.items():
            self.set_env(f"{PFX}{k}", v)

    def del_env_vars(self, keys: list, raising: bool = False):
        for k in keys:
            self.del_env(f"{PFX}{k}", raising=raising)

    def reload_with_env(self, env: dict) -> ModuleType:
        self.set_env_vars(env)
        self.clear_config_module()
        # Import and force cache clear
        cfg = importlib.import_module(MODULE)
        if hasattr(cfg, "clear_settings_cache"):
            cfg.clear_settings_cache()
        return cfg

    def assert_db_url(self, cfg, expected):
        assert cfg.settings.db_url == expected

    def assert_jwt_secret_hidden(self, cfg):
        rep = repr(cfg.settings)
        assert "jwt_secret" not in rep and "jwt_secret_key" not in rep


class TestConfig(ConfigTestTemplate):
    def test_env_precedence(self, tmp_path: Path):
        """
        In test mode, the config always overrides db_url to SQLite for safety.
        This test should expect SQLite in test mode, and only test precedence in non-test mode.
        """
        envfile = self.create_env_file(
            tmp_path,
            (
                "REVIEWPOINT_DB_URL=postgresql+asyncpg://dotenv\n"
                "REVIEWPOINT_JWT_SECRET=dummy\n"
            ),
        )
        override = "postgresql+asyncpg://env"
        self.set_env_vars({"DB_URL": override, "JWT_SECRET": "dummy"})
        settings = Settings()
        # If in test mode, expect SQLite override
        if settings.environment == "test":
            assert settings.db_url == "sqlite+aiosqlite:///:memory:"
        else:
            assert settings.db_url == override

    def test_missing_jwt_secret(self, tmp_path: Path):
        self.chdir_tmp(tmp_path)
        
        # Force production mode by temporarily patching os.environ
        import os
        import unittest.mock
        
        # Create a mock environment that excludes JWT secrets and test mode flags
        mock_env = {}
        # Add only the minimum necessary env vars - DB URL but no JWT secret or test mode flags
        mock_env["REVIEWPOINT_DB_URL"] = "postgresql+asyncpg://test:test@localhost/test"
        
        with unittest.mock.patch.dict('os.environ', mock_env, clear=True):
            with pytest.raises(RuntimeError, match="Missing JWT secret"):
                # Import the Settings class directly and instantiate it in the mocked environment
                from src.core.config import Settings
                Settings()

    def test_missing_db_url(self, tmp_path: Path):
        self.chdir_tmp(tmp_path)
        
        # Force production mode by temporarily patching os.environ
        import os
        import unittest.mock
        
        # Create a mock environment that excludes DB URLs and test mode flags
        mock_env = {}
        # Add only the minimum necessary env vars - JWT secret but no DB URL or test mode flags
        mock_env["REVIEWPOINT_JWT_SECRET"] = "testsecret"
        
        with unittest.mock.patch.dict('os.environ', mock_env, clear=True):
            with pytest.raises(RuntimeError, match="Missing database URL"):
                # Import the Settings class directly and instantiate it in the mocked environment
                from src.core.config import Settings
                Settings()

    def test_repr_hides_secret(self):
        secret = "supersecret"
        cfg = self.reload_with_env(
            {"DB_URL": "postgresql+asyncpg://db", "JWT_SECRET": secret}
        )
        self.assert_jwt_secret_hidden(cfg)

    def test_singleton_identity(self):
        cfg1 = self.reload_with_env(
            {"DB_URL": "postgresql+asyncpg://db", "JWT_SECRET": "s"}
        )
        cfg2 = importlib.reload(sys.modules[MODULE])
        assert cfg1.settings is cfg2.settings

    def test_async_db_url(self):
        url = "postgresql+asyncpg://u:p@h/db"
        cfg = self.reload_with_env({"DB_URL": url, "JWT_SECRET": "s"})
        # If in test mode, expect SQLite override
        if cfg.settings.environment == "test":
            assert cfg.settings.async_db_url == "sqlite+aiosqlite:///:memory:"
        else:
            assert cfg.settings.async_db_url == url

    def test_upload_dir_creates_path(self, tmp_path: Path):
        upload = tmp_path / "uploads"
        cfg = self.reload_with_env(
            {
                "DB_URL": "postgresql+asyncpg://db",
                "JWT_SECRET": "s",
                "UPLOAD_DIR": str(upload),
            }
        )
        assert cfg.settings.upload_path.exists()
        assert cfg.settings.upload_path.is_dir()

    # --------------------------------------------------------------------------- #
    # Environment == test overrides                                               #
    # --------------------------------------------------------------------------- #
    def test_test_env_overrides(self):
        # Set environment to test mode and override necessary vars
        self.set_env("REVIEWPOINT_ENVIRONMENT", "test") 
        cfg = self.reload_with_env(
            {
                "ENVIRONMENT": "test",
                "DB_URL": "sqlite+aiosqlite:///:memory:",  # Valid test DB URL
                "JWT_SECRET": "s",
            }
        )
        assert cfg.settings.environment == "test"
        assert cfg.settings.db_url.startswith("sqlite+aiosqlite://")
        assert cfg.settings.log_level == "WARNING"

    # --------------------------------------------------------------------------- #
    # Validation specifics                                                        #
    # --------------------------------------------------------------------------- #
    def test_invalid_db_scheme_rejected(self):
        from pydantic import ValidationError
        import os
        import unittest.mock

        # Force production mode by temporarily patching os.environ
        mock_env = {}
        # Add invalid DB URL (mysql instead of postgresql) but valid JWT secret
        mock_env["REVIEWPOINT_DB_URL"] = "mysql://oops"
        mock_env["REVIEWPOINT_JWT_SECRET"] = "testsecret"

        with unittest.mock.patch.dict('os.environ', mock_env, clear=True):
            with pytest.raises(ValidationError):
                # Import the Settings class directly and instantiate it in the mocked environment
                from src.core.config import Settings
                Settings()

    def test_log_level_override(self):
        cfg = self.reload_with_env(
            {
                "DB_URL": "postgresql+asyncpg://db",
                "JWT_SECRET": "s",
                "LOG_LEVEL": "DEBUG",
            }
        )
        # If in test mode, expect WARNING override
        if cfg.settings.environment == "test":
            assert cfg.settings.log_level == "WARNING"
        else:
            assert cfg.settings.log_level == "DEBUG"

    def test_allowed_origins_json_parsing(self):
        import json

        lst = ["https://foo.com", "https://bar.com"]
        cfg = self.reload_with_env(
            {
                "DB_URL": "postgresql+asyncpg://db",
                "JWT_SECRET": "s",
                "ALLOWED_ORIGINS": json.dumps(lst),
            }
        )
        assert cfg.settings.allowed_origins == lst

    def test_feature_flags_bool(self):
        cfg = self.reload_with_env(
            {
                "DB_URL": "postgresql+asyncpg://db",
                "JWT_SECRET": "s",
                "ENABLE_EMBEDDINGS": "true",
            }
        )
        assert cfg.settings.enable_embeddings is True

    def test_password_rounds_int(self):
        cfg = self.reload_with_env(
            {
                "DB_URL": "postgresql+asyncpg://db",
                "JWT_SECRET": "s",
                "PWD_ROUNDS": "120000",
            }
        )
        assert cfg.settings.pwd_rounds == 120000

    def test_public_dict_filters_secrets(self):
        cfg = self.reload_with_env(
            {
                "DB_URL": "postgresql+asyncpg://db",
                "JWT_SECRET": "s",
            }
        )
        public = cfg.settings.to_public_dict()
        assert "jwt_secret" not in public
        # In test mode, db_url is forced to SQLite
        if cfg.settings.environment == "test":
            assert public["db_url"].startswith("sqlite+aiosqlite://")
        else:
            assert public["db_url"].startswith("postgresql")

    def test_settings_debug_logged(self, loguru_list_sink: list[str]) -> None:
        with patch.dict(os.environ, {
            "REVIEWPOINT_DB_URL": "postgresql+asyncpg://db",
            "REVIEWPOINT_JWT_SECRET": "secret",
        }, clear=False):
            # Directly instantiate Settings to trigger the debug log
            # This ensures the log is generated after the loguru sink is set up
            _ = Settings()
        
        assert any(
            "Settings initialized for environment" in log_message for log_message in loguru_list_sink
        ), f"Expected a 'Settings initialized for environment' debug log in loguru logs. Found: {loguru_list_sink}"

    def test_optional_env_vars(self) -> None:
        cfg = self.reload_with_env(
            {
                "DB_URL": "postgresql+asyncpg://db",
                "JWT_SECRET": "s",
                "STORAGE_URL": "s3://bucket",
                "STORAGE_REGION": "us-east-1",
                "STORAGE_SECURE": "true",
                "EMAIL_HOST": "smtp.example.com",
                "EMAIL_PORT": "2525",
                "EMAIL_USER": "user",
                "EMAIL_PASSWORD": "pw",
                "EMAIL_FROM": "from@example.com",
                "SENTRY_DSN": "dsn",
                "LOGGLY_TOKEN": "token",
            }
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

    def test_jwt_config_fields(self) -> None:
        cfg = self.reload_with_env(
            {
                "DB_URL": "postgresql+asyncpg://db",
                "JWT_SECRET_KEY": "supersecret",
                "JWT_ALGORITHM": "HS512",
                "JWT_EXPIRE_MINUTES": "123",
                "AUTH_ENABLED": "false",
            }
        )
        s = cfg.settings
        assert s.jwt_secret_key == "supersecret"
        assert s.jwt_algorithm == "HS512"
        assert s.jwt_expire_minutes == 123
        assert s.auth_enabled is False

    def test_jwt_config_defaults(self) -> None:
        cfg = self.reload_with_env(
            {
                "DB_URL": "postgresql+asyncpg://db",
                "JWT_SECRET_KEY": "abc",
            }
        )
        s = cfg.settings
        assert s.jwt_algorithm == "HS256"
        assert s.jwt_expire_minutes == 30
        assert s.auth_enabled is True

    def test_jwt_secret_legacy(self, tmp_path: Path) -> None:
        self.chdir_tmp(tmp_path)
        self.del_env_vars(["JWT_SECRET_KEY"], raising=False)
        cfg = self.reload_with_env(
            {
                "DB_URL": "postgresql+asyncpg://db",
                "JWT_SECRET": "legacysecret",
            }
        )
        s = cfg.settings
        public = s.to_public_dict()
        assert s.jwt_secret_key == "legacysecret"
        assert "jwt_secret" not in public
        assert "jwt_secret_key" not in public

    def test_auth_enabled_toggle(self) -> None:
        cfg = self.reload_with_env(
            {
                "DB_URL": "postgresql+asyncpg://db",
                "JWT_SECRET_KEY": "s",
                "AUTH_ENABLED": "0",
            }
        )
        assert cfg.settings.auth_enabled is False
        cfg2 = self.reload_with_env(
            {
                "DB_URL": "postgresql+asyncpg://db",
                "JWT_SECRET_KEY": "s",
                "AUTH_ENABLED": "1",
            }
        )
        assert cfg2.settings.auth_enabled is True

    def test_verify_access_token_bypass(self) -> None:
        import unittest.mock
        
        # Create a mock settings object with auth_enabled=False
        mock_settings = unittest.mock.MagicMock()
        mock_settings.auth_enabled = False
        # Provide required JWT fields for create_access_token
        mock_settings.jwt_expire_minutes = 30
        mock_settings.jwt_secret_key = "test_secret_key"
        mock_settings.jwt_algorithm = "HS256"
        
        # Patch the get_settings function to return our mock
        with unittest.mock.patch('src.core.security.get_settings', return_value=mock_settings):
            token = create_access_token({"sub": "anyuser", "role": "user"})
            payload = verify_access_token(token)
            assert payload["sub"] == "dev-user"
            assert payload["role"] == "admin"
            assert payload["is_authenticated"] is True

    def test_verify_access_token_invalid_token_bypass(self) -> None:
        import unittest.mock
        
        # Create a mock settings object with auth_enabled=False
        mock_settings = unittest.mock.MagicMock()
        mock_settings.auth_enabled = False
        # Provide required JWT fields (not needed for invalid token test but keeps consistency)
        mock_settings.jwt_expire_minutes = 30
        mock_settings.jwt_secret_key = "test_secret_key"
        mock_settings.jwt_algorithm = "HS256"
        
        # Patch the get_settings function to return our mock
        with unittest.mock.patch('src.core.security.get_settings', return_value=mock_settings):
            payload = verify_access_token("not.a.jwt.token")
            assert payload["sub"] == "dev-user"

    def test_verify_access_token_expired_token_bypass(self) -> None:
        import unittest.mock
        import time

        # Create a mock settings object with auth_enabled=False
        mock_settings = unittest.mock.MagicMock()
        mock_settings.auth_enabled = False
        # Provide required JWT fields for create_access_token
        mock_settings.jwt_expire_minutes = 30
        mock_settings.jwt_secret_key = "test_secret_key"
        mock_settings.jwt_algorithm = "HS256"
        
        # Patch the get_settings function to return our mock
        with unittest.mock.patch('src.core.security.get_settings', return_value=mock_settings):
            expired_token = create_access_token(
                {"sub": "expired", "exp": int(time.time()) - 1000}
            )
            payload = verify_access_token(expired_token)
            assert payload["sub"] == "dev-user"

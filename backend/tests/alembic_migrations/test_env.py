import importlib
import os
import sys
import types
from typing import Any
from unittest import mock

import pytest

from src.alembic_migrations import env
from tests.test_templates import AlembicEnvTestTemplate

# TEST_DB_URL for legacy tests (use the test_db_url fixture)
TEST_DB_URL = os.environ.get("REVIEWPOINT_DB_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/reviewpoint")


class TestAlembicEnv(AlembicEnvTestTemplate):
    @pytest.fixture(autouse=True)
    def reset_logger_handlers(self):
        env.logger.handlers.clear()
        yield
        env.logger.handlers.clear()

    def _make_context(self, url=None, config_file_name="fake.ini", section="section"):
        fake_context = types.SimpleNamespace()
        fake_config = types.SimpleNamespace()
        fake_config.config_file_name = config_file_name
        fake_config.get_main_option = lambda key: (
            url if key == "sqlalchemy.url" else None
        )
        fake_config.get_section = lambda s: {}
        fake_config.config_ini_section = section
        fake_context.config = fake_config
        fake_context.get_section = lambda s: {}
        fake_context.configure = mock.Mock()
        fake_context.begin_transaction = mock.MagicMock()
        fake_context.run_migrations = mock.Mock()
        return fake_context

    def test_run_migrations_offline_success(
        self, monkeypatch: pytest.MonkeyPatch, test_db_url
    ) -> None:
        fake_context = self._make_context(
            url=test_db_url
        )
        self.patch_alembic_context(monkeypatch, fake_context)
        monkeypatch.setattr("logging.config.fileConfig", lambda *a, **k: None)
        env.run_migrations_offline()
        self.assert_called_once(fake_context.configure)
        self.assert_called_once(fake_context.run_migrations)

    def test_run_migrations_offline_no_url(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        fake_context = self._make_context(url=None)
        self.patch_alembic_context(monkeypatch, fake_context)
        monkeypatch.setattr("logging.config.fileConfig", lambda *a, **k: None)
        self.assert_raises(ValueError, env.run_migrations_offline)

    def test_run_migrations_online_success(
        self, monkeypatch: pytest.MonkeyPatch, test_db_url
    ) -> None:
        fake_context = self._make_context(
            url=test_db_url
        )
        self.patch_alembic_context(monkeypatch, fake_context)
        monkeypatch.setattr("logging.config.fileConfig", lambda *a, **k: None)

        class FakeConnection:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                return False

        class FakeEngine:
            def connect(self):
                return FakeConnection()

        def fake_engine_from_config(*a, **k):
            return FakeEngine()

        env.run_migrations_online(fake_engine_from_config)
        self.assert_called_once(fake_context.configure)
        self.assert_called_once(fake_context.run_migrations)

    def test_run_migrations_online_no_url(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        fake_context = self._make_context(url=None)
        self.patch_alembic_context(monkeypatch, fake_context)
        monkeypatch.setattr("logging.config.fileConfig", lambda *a, **k: None)

        def fake_engine_from_config(*a, **k):
            return mock.Mock(
                connect=lambda: mock.Mock(
                    __enter__=lambda s: s, __exit__=lambda s, a, b, c: False
                )
            )

        self.assert_raises(
            ValueError, env.run_migrations_online, fake_engine_from_config
        )

    # --- Begin migrated tests from test_alembic_env.py ---
    def test_run_migrations_offline_configure_raises(self, monkeypatch):
        context_mod = self._make_context(url=f"sqlite:///{TEST_DB_URL}")
        context_mod.configure = mock.MagicMock(
            side_effect=RuntimeError("configure failed")
        )
        self.patch_alembic_context(monkeypatch, context_mod)
        monkeypatch.setitem(
            sys.modules,
            "logging.config",
            types.SimpleNamespace(fileConfig=mock.MagicMock()),
        )
        monkeypatch.setitem(
            sys.modules,
            "backend.core.logging",
            types.SimpleNamespace(init_logging=mock.MagicMock()),
        )
        sys.modules.pop("backend.alembic_migrations.env", None)
        importlib.invalidate_caches()
        import src.alembic_migrations.env as env_mod

        importlib.reload(env_mod)
        self.assert_raises(
            RuntimeError, env_mod.run_migrations_offline, match="configure failed"
        )

    def test_run_migrations_offline_handles_missing_url(self, monkeypatch):
        context_mod = self._make_context(url=None)
        self.patch_alembic_context(monkeypatch, context_mod)
        monkeypatch.setitem(
            sys.modules,
            "logging.config",
            types.SimpleNamespace(fileConfig=mock.MagicMock()),
        )
        monkeypatch.setitem(
            sys.modules,
            "backend.core.logging",
            types.SimpleNamespace(init_logging=mock.MagicMock()),
        )
        sys.modules.pop("backend.alembic_migrations.env", None)
        importlib.invalidate_caches()
        import src.alembic_migrations.env as env_mod

        importlib.reload(env_mod)
        self.assert_raises(
            ValueError,
            env_mod.run_migrations_offline,
            match="No sqlalchemy.url provided",
        )

    def test_run_migrations_online_happy_path(self, monkeypatch):
        context_mod = self._make_context(url=f"sqlite:///{TEST_DB_URL}")
        self.patch_alembic_context(monkeypatch, context_mod)
        monkeypatch.setitem(
            sys.modules,
            "logging.config",
            types.SimpleNamespace(fileConfig=mock.MagicMock()),
        )
        monkeypatch.setitem(
            sys.modules,
            "backend.core.logging",
            types.SimpleNamespace(init_logging=mock.MagicMock()),
        )
        mock_connection = mock.MagicMock()
        mock_engine = mock.MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        sys.modules.pop("backend.alembic_migrations.env", None)
        importlib.invalidate_caches()
        import src.alembic_migrations.env as env_mod

        env_mod.run_migrations_online(lambda *a, **kw: mock_engine)
        self.assert_true(mock_engine.connect.called)
        self.assert_true(context_mod.configure.called)
        self.assert_true(context_mod.begin_transaction.called)
        self.assert_true(context_mod.run_migrations.called)

    def test_run_migrations_online_missing_url(self, monkeypatch):
        context_mod = self._make_context(url=None)
        self.patch_alembic_context(monkeypatch, context_mod)
        monkeypatch.setitem(
            sys.modules,
            "logging.config",
            types.SimpleNamespace(fileConfig=mock.MagicMock()),
        )
        monkeypatch.setitem(
            sys.modules,
            "backend.core.logging",
            types.SimpleNamespace(init_logging=mock.MagicMock()),
        )
        sys.modules.pop("backend.alembic_migrations.env", None)
        importlib.invalidate_caches()
        import src.alembic_migrations.env as env_mod

        self.assert_raises(
            ValueError,
            env_mod.run_migrations_online,
            lambda *a, **kw: mock.MagicMock(),
            match="No sqlalchemy.url provided",
        )

    def test_run_migrations_online_engine_connect_raises(self, monkeypatch):
        context_mod = self._make_context(url=f"sqlite:///{TEST_DB_URL}")
        self.patch_alembic_context(monkeypatch, context_mod)
        monkeypatch.setitem(
            sys.modules,
            "logging.config",
            types.SimpleNamespace(fileConfig=mock.MagicMock()),
        )
        monkeypatch.setitem(
            sys.modules,
            "backend.core.logging",
            types.SimpleNamespace(init_logging=mock.MagicMock()),
        )
        mock_engine = mock.MagicMock()
        mock_engine.connect.side_effect = RuntimeError("connect failed")
        sys.modules.pop("backend.alembic_migrations.env", None)
        importlib.invalidate_caches()
        import src.alembic_migrations.env as env_mod

        self.assert_raises(
            RuntimeError,
            env_mod.run_migrations_online,
            lambda *a, **kw: mock_engine,
            match="connect failed",
        )

    def test_run_migrations_offline_configures_logging(self, monkeypatch):
        context_mod = self._make_context(url=f"sqlite:///{TEST_DB_URL}")
        context_mod.config.config_file_name = "dummy.ini"
        self.patch_alembic_context(monkeypatch, context_mod)
        file_config_mock = mock.MagicMock()
        monkeypatch.setitem(
            sys.modules,
            "logging.config",
            types.SimpleNamespace(fileConfig=file_config_mock),
        )
        monkeypatch.setitem(
            sys.modules,
            "backend.core.logging",
            types.SimpleNamespace(init_logging=mock.MagicMock()),
        )
        sys.modules.pop("backend.alembic_migrations.env", None)
        importlib.invalidate_caches()
        import src.alembic_migrations.env as env_mod

        env_mod.run_migrations_offline()
        self.assert_true(file_config_mock.called)

    def test_run_migrations_online_configures_logging(self, monkeypatch):
        context_mod = self._make_context(url=f"sqlite:///{TEST_DB_URL}")
        context_mod.config.config_file_name = "dummy.ini"
        self.patch_alembic_context(monkeypatch, context_mod)
        file_config_mock = mock.MagicMock()
        monkeypatch.setitem(
            sys.modules,
            "logging.config",
            types.SimpleNamespace(fileConfig=file_config_mock),
        )
        monkeypatch.setitem(
            sys.modules,
            "backend.core.logging",
            types.SimpleNamespace(init_logging=mock.MagicMock()),
        )
        mock_connection = mock.MagicMock()
        mock_engine = mock.MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        sys.modules.pop("backend.alembic_migrations.env", None)
        importlib.invalidate_caches()
        import src.alembic_migrations.env as env_mod

        env_mod.run_migrations_online(lambda *a, **kw: mock_engine)
        self.assert_true(file_config_mock.called)

    def test_run_migrations_offline_fileConfig_not_called_when_no_config_file(
        self, monkeypatch
    ):
        context_mod = self._make_context(url=f"sqlite:///{TEST_DB_URL}")
        context_mod.config.config_file_name = None
        self.patch_alembic_context(monkeypatch, context_mod)
        fileConfig_mock = mock.MagicMock()
        monkeypatch.setitem(
            sys.modules,
            "logging.config",
            types.SimpleNamespace(fileConfig=fileConfig_mock),
        )
        monkeypatch.setitem(
            sys.modules,
            "backend.core.logging",
            types.SimpleNamespace(init_logging=mock.MagicMock()),
        )
        sys.modules.pop("backend.alembic_migrations.env", None)
        importlib.invalidate_caches()
        import src.alembic_migrations.env as env_mod

        env_mod.run_migrations_offline()
        self.assert_not_called(fileConfig_mock)

    def test_run_migrations_offline_fileConfig_raises(self, monkeypatch):
        context_mod = self._make_context(url=f"sqlite:///{TEST_DB_URL}")
        context_mod.config.config_file_name = "dummy.ini"
        self.patch_alembic_context(monkeypatch, context_mod)
        fileConfig_mock = mock.MagicMock(side_effect=RuntimeError("fileConfig failed"))
        monkeypatch.setitem(
            sys.modules,
            "logging.config",
            types.SimpleNamespace(fileConfig=fileConfig_mock),
        )
        monkeypatch.setitem(
            sys.modules,
            "backend.core.logging",
            types.SimpleNamespace(init_logging=mock.MagicMock()),
        )
        sys.modules.pop("backend.alembic_migrations.env", None)
        importlib.invalidate_caches()
        import src.alembic_migrations.env as env_mod

        self.assert_raises(
            RuntimeError, env_mod.run_migrations_offline, match="fileConfig failed"
        )

    def test_run_migrations_offline_begin_transaction_raises(self, monkeypatch):
        context_mod = self._make_context(url=f"sqlite:///{TEST_DB_URL}")
        begin_transaction_mock = mock.MagicMock(
            side_effect=RuntimeError("begin_transaction failed")
        )
        context_mod.begin_transaction = begin_transaction_mock
        self.patch_alembic_context(monkeypatch, context_mod)
        monkeypatch.setitem(
            sys.modules,
            "logging.config",
            types.SimpleNamespace(fileConfig=mock.MagicMock()),
        )
        monkeypatch.setitem(
            sys.modules,
            "backend.core.logging",
            types.SimpleNamespace(init_logging=mock.MagicMock()),
        )
        sys.modules.pop("backend.alembic_migrations.env", None)
        importlib.invalidate_caches()
        import src.alembic_migrations.env as env_mod

        self.assert_raises(
            RuntimeError,
            env_mod.run_migrations_offline,
            match="begin_transaction failed",
        )

    def test_run_migrations_offline_run_migrations_raises(self, monkeypatch):
        context_mod = self._make_context(url=f"sqlite:///{TEST_DB_URL}")
        run_migrations_mock = mock.MagicMock(
            side_effect=RuntimeError("run_migrations failed")
        )
        context_mod.run_migrations = run_migrations_mock
        self.patch_alembic_context(monkeypatch, context_mod)
        monkeypatch.setitem(
            sys.modules,
            "logging.config",
            types.SimpleNamespace(fileConfig=mock.MagicMock()),
        )
        monkeypatch.setitem(
            sys.modules,
            "backend.core.logging",
            types.SimpleNamespace(init_logging=mock.MagicMock()),
        )
        sys.modules.pop("backend.alembic_migrations.env", None)
        importlib.invalidate_caches()
        import src.alembic_migrations.env as env_mod

        self.assert_raises(
            RuntimeError, env_mod.run_migrations_offline, match="run_migrations failed"
        )

    def test_run_migrations_online_engine_from_config_raises(self, monkeypatch):
        context_mod = self._make_context(url=f"sqlite:///{TEST_DB_URL}")
        self.patch_alembic_context(monkeypatch, context_mod)
        monkeypatch.setitem(
            sys.modules,
            "logging.config",
            types.SimpleNamespace(fileConfig=mock.MagicMock()),
        )
        monkeypatch.setitem(
            sys.modules,
            "backend.core.logging",
            types.SimpleNamespace(init_logging=mock.MagicMock()),
        )

        def engine_from_config(*args: Any, **kwargs: Any) -> Any:
            raise RuntimeError("engine_from_config failed")

        sys.modules.pop("backend.alembic_migrations.env", None)
        importlib.invalidate_caches()
        import src.alembic_migrations.env as env_mod

        self.assert_raises(
            RuntimeError,
            env_mod.run_migrations_online,
            engine_from_config=engine_from_config,
            match="engine_from_config failed",
        )

    # --- End migrated tests ---
    def test_env_py_configures_context_with_postgres_url(self, monkeypatch):
        context_mod = self._make_context(
            url="postgresql+asyncpg://postgres:postgres@localhost:5432/reviewpoint_test"
        )
        self.patch_alembic_context(monkeypatch, context_mod)
        monkeypatch.setitem(
            sys.modules,
            "logging.config",
            types.SimpleNamespace(fileConfig=mock.MagicMock()),
        )
        monkeypatch.setitem(
            sys.modules,
            "backend.core.logging",
            types.SimpleNamespace(init_logging=mock.MagicMock()),
        )
        sys.modules.pop("backend.alembic_migrations.env", None)
        importlib.invalidate_caches()
        import src.alembic_migrations.env as env_mod

        def fake_engine_from_config(*a, **k):
            class FakeConnection:
                def __enter__(self): return self
                def __exit__(self, exc_type, exc_val, exc_tb): return False
            class FakeEngine:
                def connect(self): return FakeConnection()
            return FakeEngine()

        env_mod.run_migrations_online(fake_engine_from_config)
        self.assert_called_once(context_mod.configure)
        self.assert_called_once(context_mod.run_migrations)

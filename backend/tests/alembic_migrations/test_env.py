"""
Test module for Alembic migration environment functionality.

This module tests the offline and online migration functions in the Alembic env module,
ensuring proper error handling, configuration, and migration execution under various scenarios.
"""

import importlib
import os
import sys
import types
from collections.abc import Callable, Generator
from typing import Final, Optional, Type, TypedDict
from unittest import mock

import pytest

from tests.test_templates import AlembicEnvTestTemplate

TEST_DB_URL: Final[str] = os.environ.get(
    "REVIEWPOINT_DB_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/reviewpoint",
)



# Strictly typed context and config mocks for Alembic env tests
class AlembicConfigDict(TypedDict, total=False):
    config_file_name: str | None
    get_main_option: Callable[[str], str | None]
    get_section: Callable[[str], dict[str, object]]
    config_ini_section: str

class AlembicContextNamespace(types.SimpleNamespace):
    config: types.SimpleNamespace
    get_section: Callable[[str], dict[str, object]]
    configure: mock.Mock
    begin_transaction: mock.MagicMock
    run_migrations: mock.Mock


class TestAlembicEnv(AlembicEnvTestTemplate):
    """
    Test class for Alembic environment migration functions.
    Tests both offline and online migration scenarios including error conditions,
    configuration validation, and proper execution flow.
    """

    @pytest.fixture(autouse=True)
    def reset_logger_handlers(self) -> Generator[None, None, None]:
        """Reset logger handlers before and after each test to ensure clean state."""
        from src.alembic_migrations import env
        env.logger.handlers.clear()
        yield
        env.logger.handlers.clear()

    def _make_context(
        self,
        url: Optional[str] = None,
        config_file_name: str = "fake.ini",
        section: str = "section",
    ) -> AlembicContextNamespace:
        """
        Create a strictly typed fake Alembic context for testing.
        Args:
            url: Database URL to configure, or None to simulate missing URL
            config_file_name: Name of the config file to simulate
            section: Config section name
        Returns:
            AlembicContextNamespace: a strictly typed mock context
        """
        def get_main_option_func(key: str) -> Optional[str]:
            return url if key == "sqlalchemy.url" else None
        def get_section_func(s: str) -> dict[str, object]:
            return {}
        fake_config: types.SimpleNamespace = types.SimpleNamespace()
        fake_config.config_file_name = config_file_name
        fake_config.get_main_option = get_main_option_func
        fake_config.get_section = get_section_func
        fake_config.config_ini_section = section
        fake_context: AlembicContextNamespace = AlembicContextNamespace()
        fake_context.config = fake_config
        fake_context.get_section = get_section_func
        fake_context.configure = mock.Mock()
        fake_context.begin_transaction = mock.MagicMock()
        fake_context.run_migrations = mock.Mock()
        return fake_context

    def test_run_migrations_offline_success(
        self, monkeypatch: pytest.MonkeyPatch, test_db_url: str
    ) -> None:
        """
        Test successful offline migration execution with valid database URL.
        Ensures configure and run_migrations are called exactly once.
        """
        from src.alembic_migrations import env
        fake_context: Final[AlembicContextNamespace] = self._make_context(url=test_db_url)
        self.patch_alembic_context(monkeypatch, fake_context)
        monkeypatch.setattr("logging.config.fileConfig", lambda *a, **k: None)
        env.run_migrations_offline()
        self.assert_called_once(fake_context.configure)
        self.assert_called_once(fake_context.run_migrations)

    def test_run_migrations_offline_no_url(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """
        Test that offline migration raises ValueError when no URL is provided.
        """
        from src.alembic_migrations import env
        fake_context: AlembicContextNamespace = self._make_context(url=None)
        self.patch_alembic_context(monkeypatch, fake_context)
        monkeypatch.setattr("logging.config.fileConfig", lambda *a, **k: None)
        self.assert_raises(ValueError, env.run_migrations_offline)

    def test_run_migrations_online_success(
        self,
        monkeypatch: pytest.MonkeyPatch,
        test_db_url: str,
    ) -> None:
        """
        Test successful online migration execution with valid database URL.
        Ensures configure and run_migrations are called exactly once.
        """
        from src.alembic_migrations import env
        from src.alembic_migrations.env import EngineFromConfigType

        fake_context: AlembicContextNamespace = self._make_context(url=test_db_url)
        self.patch_alembic_context(monkeypatch, fake_context)
        file_config_lambda: Callable[..., None] = lambda *a, **k: None
        monkeypatch.setattr("logging.config.fileConfig", file_config_lambda)
        mock_connection: mock.MagicMock = mock.MagicMock()
        mock_engine: mock.MagicMock = mock.MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection

        def fake_engine_from_config(
            configuration: object, prefix: str, poolclass: Optional[object]
        ) -> mock.MagicMock:
            return mock_engine

        typed_engine_factory: EngineFromConfigType = fake_engine_from_config
        env.run_migrations_online(typed_engine_factory)
        self.assert_called_once(fake_context.configure)
        self.assert_called_once(fake_context.run_migrations)

    def test_run_migrations_online_no_url(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that online migration raises ValueError when no URL is provided."""
        from src.alembic_migrations import env
        from src.alembic_migrations.env import EngineFromConfigType

        fake_context: types.SimpleNamespace = self._make_context(url=None)
        self.patch_alembic_context(monkeypatch, fake_context)
        file_config_lambda: Callable[..., None] = lambda *a, **k: None
        monkeypatch.setattr("logging.config.fileConfig", file_config_lambda)

        def fake_engine_from_config(
            configuration: object, prefix: str, poolclass: Optional[object]
        ) -> mock.Mock:
            return mock.Mock(
                connect=lambda: mock.Mock(__enter__=lambda s: s, __exit__=lambda s, a, b, c: False)
            )

        typed_engine_factory: EngineFromConfigType = fake_engine_from_config
        self.assert_raises(ValueError, env.run_migrations_online, typed_engine_factory)

    def test_run_migrations_offline_configure_raises(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that configure errors are properly propagated during offline migration."""
        from src.alembic_migrations import env

        context_mod: types.SimpleNamespace = self._make_context(url=f"sqlite:///{TEST_DB_URL}")
        context_mod.configure = mock.MagicMock(side_effect=RuntimeError("configure failed"))
        self.patch_alembic_context(monkeypatch, context_mod)
        monkeypatch.setitem(sys.modules, "logging.config", types.SimpleNamespace(fileConfig=mock.MagicMock()))
        monkeypatch.setitem(sys.modules, "backend.core.logging", types.SimpleNamespace(init_logging=mock.MagicMock()))
        sys.modules.pop("backend.alembic_migrations.env", None)
        importlib.invalidate_caches()
        importlib.reload(env)
        self.assert_raises(RuntimeError, env.run_migrations_offline, match="configure failed")

    def test_run_migrations_offline_handles_missing_url(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that missing URL error is properly raised during offline migration."""
        from src.alembic_migrations import env

        context_mod: types.SimpleNamespace = self._make_context(url=None)
        self.patch_alembic_context(monkeypatch, context_mod)
        monkeypatch.setitem(sys.modules, "logging.config", types.SimpleNamespace(fileConfig=mock.MagicMock()))
        monkeypatch.setitem(sys.modules, "backend.core.logging", types.SimpleNamespace(init_logging=mock.MagicMock()))
        sys.modules.pop("backend.alembic_migrations.env", None)
        importlib.invalidate_caches()
        importlib.reload(env)
        self.assert_raises(ValueError, env.run_migrations_offline, match="No sqlalchemy.url provided")

    def test_run_migrations_online_happy_path(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test successful online migration execution through module reload."""
        from src.alembic_migrations import env
        from src.alembic_migrations.env import EngineFromConfigType

        context_mod: types.SimpleNamespace = self._make_context(url=f"sqlite:///{TEST_DB_URL}")
        self.patch_alembic_context(monkeypatch, context_mod)
        monkeypatch.setitem(sys.modules, "logging.config", types.SimpleNamespace(fileConfig=mock.MagicMock()))
        monkeypatch.setitem(sys.modules, "backend.core.logging", types.SimpleNamespace(init_logging=mock.MagicMock()))
        mock_connection: mock.MagicMock = mock.MagicMock()
        mock_engine: mock.MagicMock = mock.MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        sys.modules.pop("backend.alembic_migrations.env", None)
        importlib.invalidate_caches()
        importlib.reload(env)

        def typed_engine_factory(configuration: object, prefix: str, poolclass: Optional[object]) -> mock.MagicMock:
            return mock_engine

        engine_factory: EngineFromConfigType = typed_engine_factory
        env.run_migrations_online(engine_factory)
        self.assert_true(mock_engine.connect.called)
        self.assert_true(context_mod.configure.called)
        self.assert_true(context_mod.begin_transaction.called)
        self.assert_true(context_mod.run_migrations.called)

    def test_run_migrations_online_missing_url(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that missing URL error is properly raised during online migration."""
        from src.alembic_migrations import env
        from src.alembic_migrations.env import EngineFromConfigType

        context_mod: types.SimpleNamespace = self._make_context(url=None)
        self.patch_alembic_context(monkeypatch, context_mod)
        monkeypatch.setitem(sys.modules, "logging.config", types.SimpleNamespace(fileConfig=mock.MagicMock()))
        monkeypatch.setitem(sys.modules, "backend.core.logging", types.SimpleNamespace(init_logging=mock.MagicMock()))
        sys.modules.pop("backend.alembic_migrations.env", None)
        importlib.invalidate_caches()
        importlib.reload(env)

        def typed_engine_factory(configuration: object, prefix: str, poolclass: Optional[object]) -> mock.MagicMock:
            return mock.MagicMock()

        engine_factory: EngineFromConfigType = typed_engine_factory
        self.assert_raises(ValueError, env.run_migrations_online, engine_factory, match="No sqlalchemy.url provided")

    def test_run_migrations_online_engine_connect_raises(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that engine connection errors are properly propagated during online migration."""
        from src.alembic_migrations import env
        from src.alembic_migrations.env import EngineFromConfigType

        context_mod: types.SimpleNamespace = self._make_context(url=f"sqlite:///{TEST_DB_URL}")
        self.patch_alembic_context(monkeypatch, context_mod)
        monkeypatch.setitem(sys.modules, "logging.config", types.SimpleNamespace(fileConfig=mock.MagicMock()))
        monkeypatch.setitem(sys.modules, "backend.core.logging", types.SimpleNamespace(init_logging=mock.MagicMock()))
        mock_engine: mock.MagicMock = mock.MagicMock()
        mock_engine.connect.side_effect = RuntimeError("connect failed")
        sys.modules.pop("backend.alembic_migrations.env", None)
        importlib.invalidate_caches()
        importlib.reload(env)

        def typed_engine_factory(configuration: object, prefix: str, poolclass: Optional[object]) -> mock.MagicMock:
            return mock_engine

        engine_factory: EngineFromConfigType = typed_engine_factory
        self.assert_raises(RuntimeError, env.run_migrations_online, engine_factory, match="connect failed")

    def test_run_migrations_offline_configures_logging(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that logging configuration is properly set up during offline migration."""
        from src.alembic_migrations import env

        context_mod: types.SimpleNamespace = self._make_context(url=f"sqlite:///{TEST_DB_URL}")
        context_mod.config.config_file_name = "dummy.ini"
        self.patch_alembic_context(monkeypatch, context_mod)
        file_config_mock: mock.MagicMock = mock.MagicMock()
        monkeypatch.setitem(sys.modules, "logging.config", types.SimpleNamespace(fileConfig=file_config_mock))
        monkeypatch.setitem(sys.modules, "backend.core.logging", types.SimpleNamespace(init_logging=mock.MagicMock()))
        sys.modules.pop("backend.alembic_migrations.env", None)
        importlib.invalidate_caches()
        importlib.reload(env)

        env.run_migrations_offline()
        self.assert_true(file_config_mock.called)

    def test_run_migrations_online_configures_logging(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that logging configuration is properly set up during online migration."""
        from src.alembic_migrations import env
        from src.alembic_migrations.env import EngineFromConfigType

        context_mod: types.SimpleNamespace = self._make_context(url=f"sqlite:///{TEST_DB_URL}")
        context_mod.config.config_file_name = "dummy.ini"
        self.patch_alembic_context(monkeypatch, context_mod)
        file_config_mock: mock.MagicMock = mock.MagicMock()
        monkeypatch.setitem(sys.modules, "logging.config", types.SimpleNamespace(fileConfig=file_config_mock))
        monkeypatch.setitem(sys.modules, "backend.core.logging", types.SimpleNamespace(init_logging=mock.MagicMock()))
        mock_connection: mock.MagicMock = mock.MagicMock()
        mock_engine: mock.MagicMock = mock.MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        sys.modules.pop("backend.alembic_migrations.env", None)
        importlib.invalidate_caches()
        importlib.reload(env)

        def typed_engine_factory(configuration: object, prefix: str, poolclass: Optional[object]) -> mock.MagicMock:
            return mock_engine

        engine_factory: EngineFromConfigType = typed_engine_factory
        env.run_migrations_online(engine_factory)
        self.assert_true(file_config_mock.called)

    def test_run_migrations_offline_fileConfig_not_called_when_no_config_file(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that fileConfig is not called when no config file is specified."""
        from src.alembic_migrations import env

        context_mod: types.SimpleNamespace = self._make_context(url=f"sqlite:///{TEST_DB_URL}")
        context_mod.config.config_file_name = None
        self.patch_alembic_context(monkeypatch, context_mod)
        fileConfig_mock: mock.MagicMock = mock.MagicMock()
        monkeypatch.setitem(sys.modules, "logging.config", types.SimpleNamespace(fileConfig=fileConfig_mock))
        monkeypatch.setitem(sys.modules, "backend.core.logging", types.SimpleNamespace(init_logging=mock.MagicMock()))
        sys.modules.pop("backend.alembic_migrations.env", None)
        importlib.invalidate_caches()
        importlib.reload(env)

        env.run_migrations_offline()
        self.assert_not_called(fileConfig_mock)

    def test_run_migrations_offline_fileConfig_raises(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that fileConfig errors are properly propagated during offline migration."""
        from src.alembic_migrations import env

        context_mod: types.SimpleNamespace = self._make_context(url=f"sqlite:///{TEST_DB_URL}")
        context_mod.config.config_file_name = "dummy.ini"
        self.patch_alembic_context(monkeypatch, context_mod)
        fileConfig_mock: mock.MagicMock = mock.MagicMock(side_effect=RuntimeError("fileConfig failed"))
        monkeypatch.setitem(sys.modules, "logging.config", types.SimpleNamespace(fileConfig=fileConfig_mock))
        monkeypatch.setitem(sys.modules, "backend.core.logging", types.SimpleNamespace(init_logging=mock.MagicMock()))
        sys.modules.pop("backend.alembic_migrations.env", None)
        importlib.invalidate_caches()
        importlib.reload(env)

        self.assert_raises(RuntimeError, env.run_migrations_offline, match="fileConfig failed")

    def test_run_migrations_offline_begin_transaction_raises(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that begin_transaction errors are properly propagated during offline migration."""
        from src.alembic_migrations import env

        context_mod: types.SimpleNamespace = self._make_context(url=f"sqlite:///{TEST_DB_URL}")
        begin_transaction_mock: mock.MagicMock = mock.MagicMock(side_effect=RuntimeError("begin_transaction failed"))
        context_mod.begin_transaction = begin_transaction_mock
        self.patch_alembic_context(monkeypatch, context_mod)
        monkeypatch.setitem(sys.modules, "logging.config", types.SimpleNamespace(fileConfig=mock.MagicMock()))
        monkeypatch.setitem(sys.modules, "backend.core.logging", types.SimpleNamespace(init_logging=mock.MagicMock()))
        sys.modules.pop("backend.alembic_migrations.env", None)
        importlib.invalidate_caches()
        importlib.reload(env)

        self.assert_raises(RuntimeError, env.run_migrations_offline, match="begin_transaction failed")

    def test_run_migrations_offline_run_migrations_raises(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that run_migrations errors are properly propagated during offline migration."""
        from src.alembic_migrations import env

        context_mod: types.SimpleNamespace = self._make_context(url=f"sqlite:///{TEST_DB_URL}")
        run_migrations_mock: mock.MagicMock = mock.MagicMock(side_effect=RuntimeError("run_migrations failed"))
        context_mod.run_migrations = run_migrations_mock
        self.patch_alembic_context(monkeypatch, context_mod)
        monkeypatch.setitem(sys.modules, "logging.config", types.SimpleNamespace(fileConfig=mock.MagicMock()))
        monkeypatch.setitem(sys.modules, "backend.core.logging", types.SimpleNamespace(init_logging=mock.MagicMock()))
        sys.modules.pop("backend.alembic_migrations.env", None)
        importlib.invalidate_caches()
        importlib.reload(env)

        self.assert_raises(RuntimeError, env.run_migrations_offline, match="run_migrations failed")

    def test_run_migrations_online_engine_from_config_raises(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that engine_from_config errors are properly propagated during online migration."""
        from src.alembic_migrations import env
        from src.alembic_migrations.env import EngineFromConfigType

        context_mod: types.SimpleNamespace = self._make_context(url=f"sqlite:///{TEST_DB_URL}")
        self.patch_alembic_context(monkeypatch, context_mod)
        monkeypatch.setitem(sys.modules, "logging.config", types.SimpleNamespace(fileConfig=mock.MagicMock()))
        monkeypatch.setitem(sys.modules, "backend.core.logging", types.SimpleNamespace(init_logging=mock.MagicMock()))

        def engine_from_config(configuration: object, prefix: str, poolclass: Optional[object]) -> mock.MagicMock:
            raise RuntimeError("engine_from_config failed")

        sys.modules.pop("backend.alembic_migrations.env", None)
        importlib.invalidate_caches()
        importlib.reload(env)
        typed_engine_factory: EngineFromConfigType = engine_from_config
        self.assert_raises(RuntimeError, env.run_migrations_online, typed_engine_factory, match="engine_from_config failed")

    def test_env_py_configures_context_with_postgres_url(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that the environment module properly configures context with PostgreSQL URL."""
        from src.alembic_migrations import env
        from src.alembic_migrations.env import EngineFromConfigType

        context_mod: types.SimpleNamespace = self._make_context(url="postgresql+asyncpg://postgres:postgres@localhost:5432/reviewpoint_test")
        self.patch_alembic_context(monkeypatch, context_mod)
        monkeypatch.setitem(sys.modules, "logging.config", types.SimpleNamespace(fileConfig=mock.MagicMock()))
        monkeypatch.setitem(sys.modules, "backend.core.logging", types.SimpleNamespace(init_logging=mock.MagicMock()))
        sys.modules.pop("backend.alembic_migrations.env", None)
        importlib.invalidate_caches()
        importlib.reload(env)
        mock_connection: mock.MagicMock = mock.MagicMock()
        mock_engine: mock.MagicMock = mock.MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection

        def fake_engine_from_config(
            configuration: object, prefix: str, poolclass: Optional[object]
        ) -> mock.MagicMock:
            return mock_engine

        typed_engine_factory: EngineFromConfigType = fake_engine_from_config
        env.run_migrations_online(typed_engine_factory)
        self.assert_called_once(context_mod.configure)
        self.assert_called_once(context_mod.run_migrations)

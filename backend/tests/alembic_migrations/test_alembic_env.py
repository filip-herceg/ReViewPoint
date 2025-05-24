import importlib
import sys
import types
from typing import Any  # <-- Fix for NameError in test signatures
from unittest import mock

import pytest


def patch_alembic_context(monkeypatch, context_mod):
    monkeypatch.setitem(sys.modules, "alembic.context", context_mod)
    monkeypatch.setitem(sys.modules, "alembic_migrations.context", context_mod)
    monkeypatch.setitem(
        sys.modules, "alembic", types.SimpleNamespace(context=context_mod)
    )
    monkeypatch.setitem(
        sys.modules, "alembic_migrations", types.SimpleNamespace(context=context_mod)
    )


def test_run_migrations_offline_configures_and_runs(monkeypatch):
    context_mod = types.SimpleNamespace()

    def get_main_option(key):
        return "sqlite:///:memory:"

    context_mod.config = mock.Mock()
    context_mod.config.get_main_option = get_main_option
    context_mod.configure = mock.MagicMock()
    context_mod.begin_transaction = mock.MagicMock()
    context_mod.run_migrations = mock.MagicMock()
    patch_alembic_context(monkeypatch, context_mod)
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
    import backend.alembic_migrations.env as env

    # Act
    env.run_migrations_offline()
    # Assert
    assert (
        context_mod.configure.called
    ), "context.configure should be called in offline mode"
    assert (
        context_mod.begin_transaction.called
    ), "context.begin_transaction should be called in offline mode"
    assert (
        context_mod.run_migrations.called
    ), "context.run_migrations should be called in offline mode"


def test_run_migrations_offline_handles_missing_url(monkeypatch):
    # Arrange: Patch alembic.context with get_main_option returning None
    context_mod = types.ModuleType("alembic.context")

    def get_main_option(key: str) -> str | None:
        return None

    context_mod.config = mock.Mock()
    context_mod.config.get_main_option = get_main_option
    context_mod.configure = mock.MagicMock()
    context_mod.begin_transaction = mock.MagicMock()
    context_mod.run_migrations = mock.MagicMock()
    alembic_mod = types.ModuleType("alembic_migrations")
    alembic_mod.context = context_mod
    monkeypatch.setitem(sys.modules, "alembic_migrations", alembic_mod)
    # Patch alembic as well
    alembic_mod2 = types.ModuleType("alembic")
    alembic_mod2.context = context_mod
    monkeypatch.setitem(sys.modules, "alembic", alembic_mod2)
    monkeypatch.setitem(sys.modules, "alembic.context", context_mod)
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
    # Only remove backend.alembic.env to force reload
    sys.modules.pop("backend.alembic_migrations.env", None)
    importlib.invalidate_caches()
    import backend.alembic_migrations.env as env

    importlib.reload(env)
    # Act & Assert: Should raise an error due to missing URL
    with pytest.raises(ValueError, match="No sqlalchemy.url provided"):
        env.run_migrations_offline()


def test_run_migrations_offline_configure_raises(monkeypatch):
    # Arrange: Patch alembic.context.configure to raise
    context_mod = types.ModuleType("alembic.context")

    def get_main_option(key: str) -> str:
        return "sqlite:///:memory:"

    context_mod.config = mock.Mock()
    context_mod.config.get_main_option = get_main_option

    def raise_configure(*a: Any, **kw: Any) -> None:
        raise RuntimeError("configure failed")

    context_mod.configure = mock.MagicMock(side_effect=raise_configure)
    context_mod.begin_transaction = mock.MagicMock()
    context_mod.run_migrations = mock.MagicMock()
    alembic_mod = types.ModuleType("alembic_migrations")
    alembic_mod.context = context_mod
    monkeypatch.setitem(sys.modules, "alembic_migrations", alembic_mod)
    # Patch alembic as well
    alembic_mod2 = types.ModuleType("alembic")
    alembic_mod2.context = context_mod
    monkeypatch.setitem(sys.modules, "alembic", alembic_mod2)
    monkeypatch.setitem(sys.modules, "alembic.context", context_mod)
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
    # Only remove backend.alembic.env to force reload
    sys.modules.pop("backend.alembic_migrations.env", None)
    importlib.invalidate_caches()
    import backend.alembic_migrations.env as env

    importlib.reload(env)
    # Act & Assert: Should raise the configure error
    with pytest.raises(RuntimeError, match="configure failed"):
        env.run_migrations_offline()


def test_run_migrations_online_happy_path(monkeypatch):
    # Arrange: Patch alembic.context and provide a mock engine_from_config
    context_mod = types.ModuleType("alembic.context")

    def get_main_option(key: str) -> str:
        return "sqlite:///:memory:"

    context_mod.config = mock.Mock()
    context_mod.config.get_main_option = get_main_option
    context_mod.config.get_section = mock.Mock(return_value={})
    context_mod.config.config_ini_section = "section"
    context_mod.configure = mock.MagicMock()
    context_mod.begin_transaction = mock.MagicMock()
    context_mod.run_migrations = mock.MagicMock()
    patch_alembic_context(monkeypatch, context_mod)
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
    # Mock engine and connection
    mock_connection = mock.MagicMock()
    mock_engine = mock.MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_connection
    # Remove env.py from sys.modules to force reload
    sys.modules.pop("backend.alembic_migrations.env", None)
    importlib.invalidate_caches()
    import backend.alembic_migrations.env as env

    # Act
    env.run_migrations_online(lambda *a, **kw: mock_engine)
    # Assert
    assert mock_engine.connect.called, "engine.connect should be called in online mode"
    assert (
        context_mod.configure.called
    ), "context.configure should be called in online mode"
    assert (
        context_mod.begin_transaction.called
    ), "context.begin_transaction should be called in online mode"
    assert (
        context_mod.run_migrations.called
    ), "context.run_migrations should be called in online mode"


def test_run_migrations_online_missing_url(monkeypatch):
    # Arrange: Patch alembic.context with get_main_option returning None
    context_mod = types.ModuleType("alembic.context")

    def get_main_option(key: str) -> str | None:
        return None

    context_mod.config = mock.Mock()
    context_mod.config.get_main_option = get_main_option
    context_mod.config.get_section = mock.Mock(return_value={})
    context_mod.config.config_ini_section = "section"
    context_mod.configure = mock.MagicMock()
    context_mod.begin_transaction = mock.MagicMock()
    context_mod.run_migrations = mock.MagicMock()
    alembic_mod = types.ModuleType("alembic_migrations")
    alembic_mod.context = context_mod
    monkeypatch.setitem(sys.modules, "alembic_migrations", alembic_mod)
    # Patch alembic as well
    alembic_mod2 = types.ModuleType("alembic")
    alembic_mod2.context = context_mod
    monkeypatch.setitem(sys.modules, "alembic", alembic_mod2)
    monkeypatch.setitem(sys.modules, "alembic.context", context_mod)
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
    import backend.alembic_migrations.env as env

    # Act & Assert
    with pytest.raises(ValueError, match="No sqlalchemy.url provided"):
        env.run_migrations_online(lambda *a, **kw: mock.MagicMock())


def test_run_migrations_online_engine_connect_raises(monkeypatch):
    # Arrange: Patch alembic.context and provide a mock engine_from_config that raises on connect
    context_mod = types.ModuleType("alembic.context")

    def get_main_option(key: str) -> str:
        return "sqlite:///:memory:"

    context_mod.config = mock.Mock()
    context_mod.config.get_main_option = get_main_option
    context_mod.config.get_section = mock.Mock(return_value={})
    context_mod.config.config_ini_section = "section"
    context_mod.configure = mock.MagicMock()
    context_mod.begin_transaction = mock.MagicMock()
    context_mod.run_migrations = mock.MagicMock()
    patch_alembic_context(monkeypatch, context_mod)
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
    # Mock engine.connect to raise
    mock_engine = mock.MagicMock()
    mock_engine.connect.side_effect = RuntimeError("connect failed")
    sys.modules.pop("backend.alembic_migrations.env", None)
    importlib.invalidate_caches()
    import backend.alembic_migrations.env as env

    # Act & Assert
    with pytest.raises(RuntimeError, match="connect failed"):
        env.run_migrations_online(lambda *a, **kw: mock_engine)


def test_run_migrations_offline_configures_logging(monkeypatch):
    # Arrange: Patch alembic.context and logging.config.fileConfig
    context_mod = types.ModuleType("alembic.context")

    def get_main_option(key: str) -> str:
        return "sqlite:///:memory:"

    context_mod.config = mock.Mock()
    context_mod.config.get_main_option = get_main_option
    context_mod.config.config_file_name = "dummy.ini"
    context_mod.configure = mock.MagicMock()
    context_mod.begin_transaction = mock.MagicMock()
    context_mod.run_migrations = mock.MagicMock()
    patch_alembic_context(monkeypatch, context_mod)
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
    # Remove env.py from sys.modules to force reload
    sys.modules.pop("backend.alembic_migrations.env", None)
    importlib.invalidate_caches()
    import backend.alembic_migrations.env as env

    # Act
    env.run_migrations_offline()
    # Assert
    assert (
        file_config_mock.called
    ), "logging.config.fileConfig should be called in offline mode"


def test_run_migrations_online_configures_logging(monkeypatch):
    # Arrange: Patch alembic.context and logging.config.fileConfig
    context_mod = types.ModuleType("alembic.context")

    def get_main_option(key: str) -> str:
        return "sqlite:///:memory:"

    context_mod.config = mock.Mock()
    context_mod.config.get_main_option = get_main_option
    context_mod.config.get_section = mock.Mock(return_value={})
    context_mod.config.config_ini_section = "section"
    context_mod.config.config_file_name = "dummy.ini"
    context_mod.configure = mock.MagicMock()
    context_mod.begin_transaction = mock.MagicMock()
    context_mod.run_migrations = mock.MagicMock()
    patch_alembic_context(monkeypatch, context_mod)
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
    # Mock engine and connection
    mock_connection = mock.MagicMock()
    mock_engine = mock.MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_connection
    # Remove env.py from sys.modules to force reload
    sys.modules.pop("backend.alembic_migrations.env", None)
    importlib.invalidate_caches()
    import backend.alembic_migrations.env as env

    # Act
    env.run_migrations_online(lambda *a, **kw: mock_engine)
    # Assert
    assert (
        file_config_mock.called
    ), "logging.config.fileConfig should be called in online mode"


def test_run_migrations_offline_logs(monkeypatch, caplog):
    # Arrange: Patch alembic.context and logging.config.fileConfig
    context_mod = types.ModuleType("alembic.context")

    def get_main_option(key: str) -> str:
        return "sqlite:///:memory:"

    context_mod.config = mock.Mock()
    context_mod.config.get_main_option = get_main_option
    context_mod.config.config_file_name = "dummy.ini"
    context_mod.configure = mock.MagicMock()
    context_mod.begin_transaction = mock.MagicMock()
    context_mod.run_migrations = mock.MagicMock()
    patch_alembic_context(monkeypatch, context_mod)
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
    # Remove env.py from sys.modules to force reload
    sys.modules.pop("backend.alembic_migrations.env", None)
    importlib.invalidate_caches()
    import backend.alembic_migrations.env as env

    # Act
    with caplog.at_level("INFO", logger="alembic.env"):
        env.run_migrations_offline()
    # Assert
    logs = caplog.text
    assert "Starting offline migrations" in logs
    assert "Configuring context for offline migration" in logs
    assert "Running offline migrations..." in logs
    assert "Offline migrations complete." in logs


def test_run_migrations_online_logs(monkeypatch, caplog):
    # Arrange: Patch alembic.context and logging.config.fileConfig
    context_mod = types.ModuleType("alembic.context")

    def get_main_option(key: str) -> str:
        return "sqlite:///:memory:"

    context_mod.config = mock.Mock()
    context_mod.config.get_main_option = get_main_option
    context_mod.config.get_section = mock.Mock(return_value={})
    context_mod.config.config_ini_section = "section"
    context_mod.config.config_file_name = "dummy.ini"
    context_mod.configure = mock.MagicMock()
    context_mod.begin_transaction = mock.MagicMock()
    context_mod.run_migrations = mock.MagicMock()
    patch_alembic_context(monkeypatch, context_mod)
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
    # Mock engine and connection
    mock_connection = mock.MagicMock()
    mock_engine = mock.MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_connection
    # Remove env.py from sys.modules to force reload
    sys.modules.pop("backend.alembic_migrations.env", None)
    importlib.invalidate_caches()
    import backend.alembic_migrations.env as env

    # Act
    with caplog.at_level("INFO", logger="alembic.env"):
        env.run_migrations_online(lambda *a, **kw: mock_engine)
    # Assert
    logs = caplog.text
    assert "Starting online migrations" in logs
    assert "Configuring engine and context for online migration" in logs
    assert "Connected to database, configuring context..." in logs
    assert "Running online migrations..." in logs
    assert "Online migrations complete." in logs


def test_run_migrations_offline_fileConfig_not_called_when_no_config_file(
    monkeypatch,
):
    # Arrange: Patch alembic.context and logging.config
    context_mod = types.ModuleType("alembic.context")

    def get_main_option(key: str) -> str:
        return "sqlite:///:memory:"

    config_mock = mock.Mock()
    config_mock.get_main_option = get_main_option
    config_mock.config_file_name = None  # Patch here
    context_mod.config = config_mock
    context_mod.configure = mock.MagicMock()
    context_mod.begin_transaction = mock.MagicMock()
    context_mod.run_migrations = mock.MagicMock()
    monkeypatch.setitem(
        sys.modules, "alembic", types.SimpleNamespace(context=context_mod)
    )
    monkeypatch.setitem(sys.modules, "alembic.context", context_mod)
    fileConfig_mock = mock.MagicMock()
    monkeypatch.setitem(
        sys.modules, "logging.config", types.SimpleNamespace(fileConfig=fileConfig_mock)
    )
    monkeypatch.setitem(
        sys.modules,
        "backend.core.logging",
        types.SimpleNamespace(init_logging=mock.MagicMock()),
    )
    # Remove env.py from sys.modules to force reload
    sys.modules.pop("backend.alembic_migrations.env", None)
    import importlib

    importlib.invalidate_caches()
    import backend.alembic_migrations.env as env

    # Act
    env.run_migrations_offline()
    # Assert
    fileConfig_mock.assert_not_called()


def test_run_migrations_offline_fileConfig_raises(monkeypatch):
    # Arrange: Patch alembic.context and logging.config
    context_mod = types.ModuleType("alembic.context")

    def get_main_option(key: str) -> str:
        return "sqlite:///:memory:"

    config_mock = mock.Mock()
    config_mock.get_main_option = get_main_option
    config_mock.config_file_name = "dummy.ini"
    context_mod.config = config_mock
    context_mod.configure = mock.MagicMock()
    context_mod.begin_transaction = mock.MagicMock()
    context_mod.run_migrations = mock.MagicMock()
    monkeypatch.setitem(
        sys.modules, "alembic", types.SimpleNamespace(context=context_mod)
    )
    monkeypatch.setitem(sys.modules, "alembic.context", context_mod)
    fileConfig_mock = mock.MagicMock(side_effect=RuntimeError("fileConfig failed"))
    monkeypatch.setitem(
        sys.modules, "logging.config", types.SimpleNamespace(fileConfig=fileConfig_mock)
    )
    monkeypatch.setitem(
        sys.modules,
        "backend.core.logging",
        types.SimpleNamespace(init_logging=mock.MagicMock()),
    )
    # Remove env.py from sys.modules to force reload
    sys.modules.pop("backend.alembic_migrations.env", None)
    import importlib

    importlib.invalidate_caches()
    import backend.alembic_migrations.env as env

    # Act & Assert
    with pytest.raises(RuntimeError, match="fileConfig failed"):
        env.run_migrations_offline()


def test_run_migrations_offline_init_logging_raises(monkeypatch):
    # Arrange: Patch alembic.context and logging.config
    context_mod = types.ModuleType("alembic.context")

    def get_main_option(key: str) -> str:
        return "sqlite:///:memory:"

    config_mock = mock.Mock()
    config_mock.get_main_option = get_main_option
    config_mock.config_file_name = None  # So fileConfig is not called
    context_mod.config = config_mock
    context_mod.configure = mock.MagicMock()
    context_mod.begin_transaction = mock.MagicMock()
    context_mod.run_migrations = mock.MagicMock()
    monkeypatch.setitem(
        sys.modules, "alembic", types.SimpleNamespace(context=context_mod)
    )
    monkeypatch.setitem(sys.modules, "alembic.context", context_mod)
    monkeypatch.setitem(
        sys.modules,
        "logging.config",
        types.SimpleNamespace(fileConfig=mock.MagicMock()),
    )
    init_logging_mock = mock.MagicMock(side_effect=RuntimeError("init_logging failed"))
    monkeypatch.setitem(
        sys.modules,
        "backend.core.logging",
        types.SimpleNamespace(init_logging=init_logging_mock),
    )
    # Remove env.py from sys.modules to force reload
    sys.modules.pop("backend.alembic_migrations.env", None)
    import importlib

    importlib.invalidate_caches()
    import backend.alembic_migrations.env as env

    # Act & Assert
    with pytest.raises(RuntimeError, match="init_logging failed"):
        env.run_migrations_offline()


def test_run_migrations_offline_begin_transaction_raises(
    monkeypatch,
):
    # Arrange: Patch alembic.context and logging.config
    context_mod = types.ModuleType("alembic.context")

    def get_main_option(key: str) -> str:
        return "sqlite:///:memory:"

    config_mock = mock.Mock()
    config_mock.get_main_option = get_main_option
    config_mock.config_file_name = None
    context_mod.config = config_mock
    context_mod.configure = mock.MagicMock()
    begin_transaction_mock = mock.MagicMock(
        side_effect=RuntimeError("begin_transaction failed")
    )
    context_mod.begin_transaction = begin_transaction_mock
    context_mod.run_migrations = mock.MagicMock()
    monkeypatch.setitem(
        sys.modules, "alembic", types.SimpleNamespace(context=context_mod)
    )
    monkeypatch.setitem(sys.modules, "alembic.context", context_mod)
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
    # Remove env.py from sys.modules to force reload
    sys.modules.pop("backend.alembic_migrations.env", None)
    import importlib

    importlib.invalidate_caches()
    import backend.alembic_migrations.env as env

    # Act & Assert
    with pytest.raises(RuntimeError, match="begin_transaction failed"):
        env.run_migrations_offline()


def test_run_migrations_offline_run_migrations_raises(monkeypatch):
    # Arrange: Patch alembic.context and logging.config
    context_mod = types.ModuleType("alembic.context")

    def get_main_option(key: str) -> str:
        return "sqlite:///:memory:"

    config_mock = mock.Mock()
    config_mock.get_main_option = get_main_option
    config_mock.config_file_name = None
    context_mod.config = config_mock
    context_mod.configure = mock.MagicMock()
    context_mod.begin_transaction = mock.MagicMock()
    run_migrations_mock = mock.MagicMock(
        side_effect=RuntimeError("run_migrations failed")
    )
    context_mod.run_migrations = run_migrations_mock
    monkeypatch.setitem(
        sys.modules, "alembic", types.SimpleNamespace(context=context_mod)
    )
    monkeypatch.setitem(sys.modules, "alembic.context", context_mod)
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
    # Remove env.py from sys.modules to force reload
    sys.modules.pop("backend.alembic_migrations.env", None)
    import importlib

    importlib.invalidate_caches()
    import backend.alembic_migrations.env as env

    # Act & Assert
    with pytest.raises(RuntimeError, match="run_migrations failed"):
        env.run_migrations_offline()


def test_run_migrations_online_engine_from_config_raises(
    monkeypatch,
):
    # Arrange: Patch alembic.context, alembic.config, and sqlalchemy
    context_mod = types.ModuleType("alembic.context")

    def get_main_option(key: str) -> str:
        return "sqlite:///:memory:"

    config_mock = mock.Mock()
    config_mock.get_main_option = get_main_option
    config_mock.config_file_name = None
    context_mod.config = config_mock
    context_mod.configure = mock.MagicMock()
    context_mod.begin_transaction = mock.MagicMock()
    context_mod.run_migrations = mock.MagicMock()
    monkeypatch.setitem(
        sys.modules, "alembic", types.SimpleNamespace(context=context_mod)
    )
    monkeypatch.setitem(sys.modules, "alembic.context", context_mod)
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

    # Patch engine_from_config to raise
    def engine_from_config(*args: Any, **kwargs: Any) -> Any:
        raise RuntimeError("engine_from_config failed")

    # Remove env.py from sys.modules to force reload
    sys.modules.pop("backend.alembic_migrations.env", None)
    import importlib

    importlib.invalidate_caches()
    import backend.alembic_migrations.env as env

    # Act & Assert
    with pytest.raises(RuntimeError, match="engine_from_config failed"):
        env.run_migrations_online(engine_from_config=engine_from_config)

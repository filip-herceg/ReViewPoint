import importlib
import sys
import types
from typing import Any
from unittest import mock

import pytest

from src.alembic_migrations import env
from tests.conftest import TEST_DB_PATH


@pytest.fixture(autouse=True)
def reset_logger_handlers():
    # Reset logger handlers before each test
    env.logger.handlers.clear()
    yield
    env.logger.handlers.clear()


def patch_alembic_context(monkeypatch: pytest.MonkeyPatch, context_mod: Any) -> None:
    monkeypatch.setitem(sys.modules, "alembic.context", context_mod)
    monkeypatch.setitem(sys.modules, "alembic_migrations.context", context_mod)
    monkeypatch.setitem(
        sys.modules, "alembic", types.SimpleNamespace(context=context_mod)
    )
    monkeypatch.setitem(
        sys.modules, "alembic_migrations", types.SimpleNamespace(context=context_mod)
    )


def test_run_migrations_offline_success(monkeypatch):
    # Patch alembic.context and fileConfig
    fake_context = types.SimpleNamespace()
    fake_config = types.SimpleNamespace()
    fake_config.config_file_name = "fake.ini"
    fake_config.get_main_option = lambda key: (
        "sqlite:///:memory:" if key == "sqlalchemy.url" else None
    )
    fake_context.config = fake_config
    fake_context.configure = mock.Mock()
    fake_context.begin_transaction = mock.MagicMock()
    fake_context.run_migrations = mock.Mock()
    monkeypatch.setattr("alembic.context", fake_context)
    monkeypatch.setattr("logging.config.fileConfig", lambda *a, **k: None)

    env.run_migrations_offline()
    fake_context.configure.assert_called_once()
    fake_context.run_migrations.assert_called_once()


def test_run_migrations_offline_no_url(monkeypatch):
    fake_context = types.SimpleNamespace()
    fake_config = types.SimpleNamespace()
    fake_config.config_file_name = "fake.ini"
    fake_config.get_main_option = lambda key: None
    fake_context.config = fake_config
    monkeypatch.setattr("alembic.context", fake_context)
    monkeypatch.setattr("logging.config.fileConfig", lambda *a, **k: None)
    with pytest.raises(ValueError):
        env.run_migrations_offline()


def test_run_migrations_online_success(monkeypatch):
    fake_context = types.SimpleNamespace()
    fake_config = types.SimpleNamespace()
    fake_config.config_file_name = "fake.ini"
    fake_config.get_main_option = lambda key: (
        "sqlite:///:memory:" if key == "sqlalchemy.url" else None
    )
    fake_config.get_section = lambda section: {}
    fake_config.config_ini_section = "section"
    fake_context.config = fake_config
    fake_context.get_section = lambda section: {}
    fake_context.configure = mock.Mock()
    fake_context.begin_transaction = mock.MagicMock()
    fake_context.run_migrations = mock.Mock()
    monkeypatch.setattr("alembic.context", fake_context)
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
    fake_context.configure.assert_called_once()
    fake_context.run_migrations.assert_called_once()


def test_run_migrations_online_no_url(monkeypatch):
    fake_context = types.SimpleNamespace()
    fake_config = types.SimpleNamespace()
    fake_config.config_file_name = "fake.ini"
    fake_config.get_main_option = lambda key: None
    fake_context.config = fake_config
    fake_context.get_section = lambda section: {}
    fake_context.config_ini_section = "section"
    monkeypatch.setattr("alembic.context", fake_context)
    monkeypatch.setattr("logging.config.fileConfig", lambda *a, **k: None)

    def fake_engine_from_config(*a, **k):
        return mock.Mock(
            connect=lambda: mock.Mock(
                __enter__=lambda s: s, __exit__=lambda s, a, b, c: False
            )
        )

    with pytest.raises(ValueError):
        env.run_migrations_online(fake_engine_from_config)


# --- Begin migrated tests from test_alembic_env.py ---
def test_run_migrations_offline_configure_raises(monkeypatch: pytest.MonkeyPatch):
    context_mod = types.SimpleNamespace()

    def get_main_option(key: str) -> str:
        return f"sqlite:///{TEST_DB_PATH}"

    context_mod.config = mock.Mock()
    context_mod.config.get_main_option = get_main_option

    def raise_configure(*a: Any, **kw: Any) -> None:
        raise RuntimeError("configure failed")

    context_mod.configure = mock.MagicMock(side_effect=raise_configure)
    context_mod.begin_transaction = mock.MagicMock()
    context_mod.run_migrations = mock.MagicMock()
    alembic_mod = types.SimpleNamespace()
    alembic_mod.context = context_mod
    monkeypatch.setitem(sys.modules, "alembic_migrations", alembic_mod)
    alembic_mod2 = types.SimpleNamespace()
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
    import src.alembic_migrations.env as env

    importlib.reload(env)
    with pytest.raises(RuntimeError, match="configure failed"):
        env.run_migrations_offline()


def test_run_migrations_offline_handles_missing_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context_mod = types.SimpleNamespace()

    def get_main_option(key: str) -> str | None:
        return None

    config_mock = mock.Mock()
    config_mock.get_main_option = get_main_option
    context_mod.config = config_mock
    context_mod.configure = mock.MagicMock()
    context_mod.begin_transaction = mock.MagicMock()
    context_mod.run_migrations = mock.MagicMock()
    alembic_mod = types.SimpleNamespace()
    alembic_mod.context = context_mod
    monkeypatch.setitem(sys.modules, "alembic_migrations", alembic_mod)
    alembic_mod2 = types.SimpleNamespace()
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
    import src.alembic_migrations.env as env

    importlib.reload(env)
    with pytest.raises(ValueError, match="No sqlalchemy.url provided"):
        env.run_migrations_offline()


def test_run_migrations_online_happy_path(monkeypatch: pytest.MonkeyPatch) -> None:
    context_mod = types.SimpleNamespace()

    def get_main_option(key: str) -> str:
        return f"sqlite:///{TEST_DB_PATH}"

    config_mock = mock.Mock()
    config_mock.get_main_option = get_main_option
    config_mock.get_section = mock.Mock(return_value={})
    config_mock.config_ini_section = "section"
    context_mod.config = config_mock
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
    mock_connection = mock.MagicMock()
    mock_engine = mock.MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_connection
    sys.modules.pop("backend.alembic_migrations.env", None)
    importlib.invalidate_caches()
    import src.alembic_migrations.env as env

    env.run_migrations_online(lambda *a, **kw: mock_engine)
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


def test_run_migrations_online_missing_url(monkeypatch: pytest.MonkeyPatch) -> None:
    context_mod = types.SimpleNamespace()

    def get_main_option(key: str) -> str | None:
        return None

    config_mock = mock.Mock()
    config_mock.get_main_option = get_main_option
    config_mock.get_section = mock.Mock(return_value={})
    config_mock.config_ini_section = "section"
    context_mod.config = config_mock
    context_mod.configure = mock.MagicMock()
    context_mod.begin_transaction = mock.MagicMock()
    context_mod.run_migrations = mock.MagicMock()
    alembic_mod = types.SimpleNamespace()
    alembic_mod.context = context_mod
    monkeypatch.setitem(sys.modules, "alembic_migrations", alembic_mod)
    alembic_mod2 = types.SimpleNamespace()
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
    import src.alembic_migrations.env as env

    with pytest.raises(ValueError, match="No sqlalchemy.url provided"):
        env.run_migrations_online(lambda *a, **kw: mock.MagicMock())


def test_run_migrations_online_engine_connect_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context_mod = types.SimpleNamespace()

    def get_main_option(key: str) -> str:
        return f"sqlite:///{TEST_DB_PATH}"

    config_mock = mock.Mock()
    config_mock.get_main_option = get_main_option
    config_mock.get_section = mock.Mock(return_value={})
    config_mock.config_ini_section = "section"
    context_mod.config = config_mock
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
    mock_engine = mock.MagicMock()
    mock_engine.connect.side_effect = RuntimeError("connect failed")
    sys.modules.pop("backend.alembic_migrations.env", None)
    importlib.invalidate_caches()
    import src.alembic_migrations.env as env

    with pytest.raises(RuntimeError, match="connect failed"):
        env.run_migrations_online(lambda *a, **kw: mock_engine)


def test_run_migrations_offline_configures_logging(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context_mod = types.SimpleNamespace()

    def get_main_option(key: str) -> str:
        return f"sqlite:///{TEST_DB_PATH}"

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
    sys.modules.pop("backend.alembic_migrations.env", None)
    importlib.invalidate_caches()
    import src.alembic_migrations.env as env

    env.run_migrations_offline()
    assert (
        file_config_mock.called
    ), "logging.config.fileConfig should be called in offline mode"


def test_run_migrations_online_configures_logging(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context_mod = types.SimpleNamespace()

    def get_main_option(key: str) -> str:
        return f"sqlite:///{TEST_DB_PATH}"

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
    mock_connection = mock.MagicMock()
    mock_engine = mock.MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_connection
    sys.modules.pop("backend.alembic_migrations.env", None)
    importlib.invalidate_caches()
    import src.alembic_migrations.env as env

    env.run_migrations_online(lambda *a, **kw: mock_engine)
    assert (
        file_config_mock.called
    ), "logging.config.fileConfig should be called in online mode"


def test_run_migrations_offline_fileConfig_not_called_when_no_config_file(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context_mod = types.SimpleNamespace()

    def get_main_option(key: str) -> str:
        return f"sqlite:///{TEST_DB_PATH}"

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
    fileConfig_mock = mock.MagicMock()
    monkeypatch.setitem(
        sys.modules, "logging.config", types.SimpleNamespace(fileConfig=fileConfig_mock)
    )
    monkeypatch.setitem(
        sys.modules,
        "backend.core.logging",
        types.SimpleNamespace(init_logging=mock.MagicMock()),
    )
    sys.modules.pop("backend.alembic_migrations.env", None)
    importlib.invalidate_caches()
    import src.alembic_migrations.env as env

    env.run_migrations_offline()
    fileConfig_mock.assert_not_called()


def test_run_migrations_offline_fileConfig_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context_mod = types.SimpleNamespace()

    def get_main_option(key: str) -> str:
        return f"sqlite:///{TEST_DB_PATH}"

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
    sys.modules.pop("backend.alembic_migrations.env", None)
    importlib.invalidate_caches()
    import src.alembic_migrations.env as env

    with pytest.raises(RuntimeError, match="fileConfig failed"):
        env.run_migrations_offline()


def test_run_migrations_offline_begin_transaction_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context_mod = types.SimpleNamespace()

    def get_main_option(key: str) -> str:
        return f"sqlite:///{TEST_DB_PATH}"

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
    sys.modules.pop("backend.alembic_migrations.env", None)
    importlib.invalidate_caches()
    import src.alembic_migrations.env as env

    with pytest.raises(RuntimeError, match="begin_transaction failed"):
        env.run_migrations_offline()


def test_run_migrations_offline_run_migrations_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context_mod = types.SimpleNamespace()

    def get_main_option(key: str) -> str:
        return f"sqlite:///{TEST_DB_PATH}"

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
    sys.modules.pop("backend.alembic_migrations.env", None)
    importlib.invalidate_caches()
    import src.alembic_migrations.env as env

    with pytest.raises(RuntimeError, match="run_migrations failed"):
        env.run_migrations_offline()


def test_run_migrations_online_engine_from_config_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context_mod = types.SimpleNamespace()

    def get_main_option(key: str) -> str:
        return f"sqlite:///{TEST_DB_PATH}"

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

    def engine_from_config(*args: Any, **kwargs: Any) -> Any:
        raise RuntimeError("engine_from_config failed")

    sys.modules.pop("backend.alembic_migrations.env", None)
    importlib.invalidate_caches()
    import src.alembic_migrations.env as env

    with pytest.raises(RuntimeError, match="engine_from_config failed"):
        env.run_migrations_online(engine_from_config=engine_from_config)


# --- End migrated tests ---

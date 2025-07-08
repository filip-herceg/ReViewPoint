# Implements only the run_migrations_offline and run_migrations_online
# functions for modular testability

import logging
import os
import sys
from collections.abc import Callable, Mapping
from typing import Final

import sqlalchemy
from sqlalchemy.engine import Engine

from src.models.base import Base

LOGGER_NAME: Final[str] = "alembic.env"
LOG_LEVEL: Final[int] = logging.INFO

logger: Final[logging.Logger] = logging.getLogger(LOGGER_NAME)
logger.setLevel(LOG_LEVEL)
logger.propagate = True

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
# Add this to ensure Alembic sees all models for autogenerate

target_metadata: Final[sqlalchemy.MetaData] = Base.metadata


# Type alias for the engine_from_config callable signature
EngineFromConfigType = Callable[[Mapping[str, object], str, object | None], Engine]


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    Raises:
        ValueError: If no sqlalchemy.url is provided for offline migration.
    """
    from logging.config import fileConfig

    import alembic.context

    logger.info("Starting offline migrations")
    config_file = alembic.context.config.config_file_name
    if config_file is not None:
        fileConfig(config_file)
        logger.debug(f"Loaded logging config from {config_file}")
    url = alembic.context.config.get_main_option("sqlalchemy.url")
    if url is None:
        logger.error("No sqlalchemy.url provided for offline migration")
        raise ValueError("No sqlalchemy.url provided for offline migration")
    logger.info(f"Configuring context for offline migration (url={url})")
    alembic.context.configure(
        url=url, literal_binds=True, dialect_opts={"paramstyle": "named"}
    )
    # begin_transaction returns a _ProxyTransaction, not a ContextManager[None]
    proxy_transaction = alembic.context.begin_transaction()
    with proxy_transaction:
        logger.info("Running offline migrations...")
        alembic.context.run_migrations()
        logger.info("Offline migrations complete.")


def run_migrations_online(engine_from_config: EngineFromConfigType) -> None:
    """
    Run migrations in 'online' mode. The engine_from_config dependency must be provided for testability.
    Raises:
        ValueError: If no sqlalchemy.url is provided for online migration.
        TypeError: If the config section is not a Mapping.
    """
    from logging.config import fileConfig

    import alembic.context

    logger.info("Starting online migrations")
    config_file = alembic.context.config.config_file_name
    if config_file is not None:
        fileConfig(config_file)
        logger.debug(f"Loaded logging config from {config_file}")
    url = alembic.context.config.get_main_option("sqlalchemy.url")
    if url is None:
        logger.error("No sqlalchemy.url provided for online migration")
        raise ValueError("No sqlalchemy.url provided for online migration")
    logger.info(f"Configuring engine and context for online migration (url={url})")
    section_raw: object = alembic.context.config.get_section(
        alembic.context.config.config_ini_section
    )
    if not isinstance(section_raw, Mapping):
        raise TypeError("Expected config section to be a Mapping[str, object]")
    section: Mapping[str, object] = section_raw
    prefix: Final[str] = "sqlalchemy."
    poolclass: object | None = None
    engine: Engine = engine_from_config(section, prefix, poolclass)
    # engine.connect() returns a Connection, which is a context manager
    with engine.connect() as connection:
        logger.info("Connected to database, configuring context...")
        alembic.context.configure(connection=connection)
        proxy_transaction = alembic.context.begin_transaction()
        with proxy_transaction:
            logger.info("Running online migrations...")
            alembic.context.run_migrations()
            logger.info("Online migrations complete.")

# Implements only the run_migrations_offline and run_migrations_online
# functions for modular testability

import logging
import os
import sys
from collections.abc import Callable, Mapping
from typing import Any, Final

import sqlalchemy
from alembic import context
from alembic.config import Config
from sqlalchemy import engine_from_config
from sqlalchemy.engine import Engine

LOGGER_NAME: Final[str] = "alembic.env"
LOG_LEVEL: Final[int] = logging.INFO

logger: Final[logging.Logger] = logging.getLogger(LOGGER_NAME)
logger.setLevel(LOG_LEVEL)
logger.propagate = True

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
# Add this to ensure Alembic sees all models for autogenerate

# For initial migrations, disable model imports to prevent table conflicts
# Once migrations are applied, you can re-enable this for autogenerate functionality
target_metadata: sqlalchemy.MetaData | None = None
print("[ALEMBIC DEBUG] Using target_metadata = None to avoid table conflicts")


# Alembic Config object - accessed lazily to avoid issues in test environments
def get_config() -> Config:
    """Get the Alembic config object."""
    return context.config


# Get the database URL from environment variable, falling back to alembic.ini


def get_url() -> str | None:
    """Get database URL, converting from async to sync format if needed."""
    url: str | None = os.getenv("REVIEWPOINT_DB_URL")
    print(f"[ALEMBIC DEBUG] Environment variable REVIEWPOINT_DB_URL: {url}")
    if url:
        original_url = url
        # Convert async URL to sync for Alembic
        url = url.replace("postgresql+asyncpg://", "postgresql://")
        print(f"[ALEMBIC DEBUG] Original URL: {original_url}")
        print(f"[ALEMBIC DEBUG] Converted URL: {url}")
        print(f"[ALEMBIC DEBUG] Running with environment variable: {original_url}")
        logger.info(f"Using database URL from environment: {url}")
        return url

    # Fall back to alembic.ini
    config = get_config()
    url = config.get_main_option("sqlalchemy.url")
    print(f"[ALEMBIC DEBUG] Fallback URL from alembic.ini: {url}")
    print(f"[ALEMBIC DEBUG] No environment variable found, using alembic.ini")
    logger.info(f"Using database URL from alembic.ini: {url}")
    return url


# Type alias for the engine_from_config callable signature
EngineFromConfigType = Callable[[Mapping[str, object], str, Any | None], Engine]


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    Raises:
        ValueError: If no sqlalchemy.url is provided for offline migration.
    """
    from logging.config import fileConfig

    logger.info("Starting offline migrations")

    config = get_config()
    config_file: str | None = config.config_file_name
    if config_file is not None:
        fileConfig(config_file)
        logger.debug(f"Loaded logging config from {config_file}")

    url: str | None = get_url()
    if url is None:
        logger.error("No sqlalchemy.url provided for offline migration")
        raise ValueError("No sqlalchemy.url provided for offline migration")

    logger.info(f"Configuring context for offline migration (url={url})")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    # begin_transaction returns a _ProxyTransaction, not a ContextManager[None]
    with context.begin_transaction():
        logger.info("Running offline migrations...")
        context.run_migrations()
        logger.info("Offline migrations complete.")


def run_migrations_online(
    engine_from_config_func: EngineFromConfigType | None = None,
) -> None:
    """
    Run migrations in 'online' mode. The engine_from_config dependency must be provided for testability.
    Raises:
        ValueError: If no sqlalchemy.url is provided for online migration.
        TypeError: If the config section is not a Mapping.
    """
    from logging.config import fileConfig

    logger.info("Starting online migrations")
    config = get_config()
    config_file: str | None = config.config_file_name
    if config_file is not None:
        fileConfig(config_file)
        logger.debug(f"Loaded logging config from {config_file}")

    url: str | None = get_url()
    if url is None:
        logger.error("No sqlalchemy.url provided for online migration")
        raise ValueError("No sqlalchemy.url provided for online migration")

    # Override the URL in the config
    config = get_config()
    config.set_main_option("sqlalchemy.url", url)

    logger.info(f"Configuring engine and context for online migration (url={url})")
    section_raw: object = config.get_section(config.config_ini_section)
    if not isinstance(section_raw, Mapping):
        raise TypeError("Expected config section to be a Mapping[str, object]")
    section: Mapping[str, object] = section_raw
    prefix: Final[str] = "sqlalchemy."

    # Use the provided engine function or default
    if engine_from_config_func:
        configured_engine: Engine = engine_from_config_func(section, prefix, None)
    else:
        configured_engine = engine_from_config(dict(section), prefix)

    # engine.connect() returns a Connection, which is a context manager
    with configured_engine.connect() as connection:
        logger.info("Connected to database, configuring context...")
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            logger.info("Running online migrations...")
            context.run_migrations()
            logger.info("Online migrations complete.")


def run_migrations() -> None:
    """Run migrations based on the current context mode."""
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()


# Main execution for Alembic - only run if this is the main module
if __name__ == "__main__":
    run_migrations()

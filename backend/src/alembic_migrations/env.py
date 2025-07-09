# Implements only the run_migrations_offline and run_migrations_online
# functions for modular testability

import logging
import os
import sys
from collections.abc import Callable, Mapping
from typing import Final

import sqlalchemy
from sqlalchemy.engine import Engine
from alembic import context
from sqlalchemy import engine_from_config

from src.models.base import Base

LOGGER_NAME: Final[str] = "alembic.env"
LOG_LEVEL: Final[int] = logging.INFO

logger: Final[logging.Logger] = logging.getLogger(LOGGER_NAME)
logger.setLevel(LOG_LEVEL)
logger.propagate = True

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
# Add this to ensure Alembic sees all models for autogenerate

target_metadata: Final[sqlalchemy.MetaData] = Base.metadata

# Alembic Config object
config = context.config

# Get the database URL from environment variable, falling back to alembic.ini
def get_url():
    """Get database URL, converting from async to sync format if needed."""
    # Try environment variable first (from the app's .env file)
    url = os.getenv('REVIEWPOINT_DB_URL')
    if url:
        # Convert async URL to sync for Alembic
        url = url.replace('postgresql+asyncpg://', 'postgresql://')
        logger.info(f"Using database URL from environment: {url}")
        return url
    
    # Fall back to alembic.ini
    url = config.get_main_option("sqlalchemy.url")
    logger.info(f"Using database URL from alembic.ini: {url}")
    return url

# Type alias for the engine_from_config callable signature
EngineFromConfigType = Callable[[Mapping[str, object], str, object | None], Engine]


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    Raises:
        ValueError: If no sqlalchemy.url is provided for offline migration.
    """
    from logging.config import fileConfig

    logger.info("Starting offline migrations")
    config_file = context.config.config_file_name
    if config_file is not None:
        fileConfig(config_file)
        logger.debug(f"Loaded logging config from {config_file}")
    
    url = get_url()
    if url is None:
        logger.error("No sqlalchemy.url provided for offline migration")
        raise ValueError("No sqlalchemy.url provided for offline migration")
    
    logger.info(f"Configuring context for offline migration (url={url})")
    context.configure(
        url=url, 
        target_metadata=target_metadata,
        literal_binds=True, 
        dialect_opts={"paramstyle": "named"}
    )
    
    # begin_transaction returns a _ProxyTransaction, not a ContextManager[None]
    with context.begin_transaction():
        logger.info("Running offline migrations...")
        context.run_migrations()
        logger.info("Offline migrations complete.")


def run_migrations_online(engine_from_config_func: EngineFromConfigType | None = None) -> None:
    """
    Run migrations in 'online' mode. The engine_from_config dependency must be provided for testability.
    Raises:
        ValueError: If no sqlalchemy.url is provided for online migration.
        TypeError: If the config section is not a Mapping.
    """
    from logging.config import fileConfig

    logger.info("Starting online migrations")
    config_file = context.config.config_file_name
    if config_file is not None:
        fileConfig(config_file)
        logger.debug(f"Loaded logging config from {config_file}")
    
    url = get_url()
    if url is None:
        logger.error("No sqlalchemy.url provided for online migration")
        raise ValueError("No sqlalchemy.url provided for online migration")
    
    # Override the URL in the config
    config.set_main_option("sqlalchemy.url", url)
    
    logger.info(f"Configuring engine and context for online migration (url={url})")
    section_raw: object = context.config.get_section(
        context.config.config_ini_section
    )
    if not isinstance(section_raw, Mapping):
        raise TypeError("Expected config section to be a Mapping[str, object]")
    section: Mapping[str, object] = section_raw
    prefix: Final[str] = "sqlalchemy."
    
    # Use the provided engine function or default
    if engine_from_config_func:
        engine: Engine = engine_from_config_func(section, prefix, None)
    else:
        engine: Engine = engine_from_config(section, prefix)
    
    # engine.connect() returns a Connection, which is a context manager
    with engine.connect() as connection:
        logger.info("Connected to database, configuring context...")
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            logger.info("Running online migrations...")
            context.run_migrations()
            logger.info("Online migrations complete.")


# Main execution for Alembic
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

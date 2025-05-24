# Implements only the run_migrations_offline and run_migrations_online functions for modular testability
import logging
from typing import Callable, Any


def run_migrations_offline():
    import alembic.context
    from logging.config import fileConfig
    from core.logging import init_logging

    init_logging()
    logger = logging.getLogger("alembic.env")
    logger.info("Starting offline migrations")
    config_file = alembic.context.config.config_file_name
    if config_file:
        fileConfig(config_file)
        logger.debug(f"Loaded logging config from {config_file}")
    url = alembic.context.config.get_main_option("sqlalchemy.url")
    if not url:
        logger.error("No sqlalchemy.url provided for offline migration")
        raise ValueError("No sqlalchemy.url provided for offline migration")
    logger.info(f"Configuring context for offline migration (url={url})")
    alembic.context.configure(
        url=url, literal_binds=True, dialect_opts={"paramstyle": "named"}
    )
    with alembic.context.begin_transaction():
        logger.info("Running offline migrations...")
        alembic.context.run_migrations()
        logger.info("Offline migrations complete.")


def run_migrations_online(engine_from_config: Callable[..., Any]):
    """
    Run migrations in 'online' mode. The engine_from_config dependency must be provided for testability.
    """
    import alembic.context
    from logging.config import fileConfig
    from core.logging import init_logging

    init_logging()
    logger = logging.getLogger("alembic.env")
    logger.info("Starting online migrations")
    config_file = alembic.context.config.config_file_name
    if config_file:
        fileConfig(config_file)
        logger.debug(f"Loaded logging config from {config_file}")
    url = alembic.context.config.get_main_option("sqlalchemy.url")
    if not url:
        logger.error("No sqlalchemy.url provided for online migration")
        raise ValueError("No sqlalchemy.url provided for online migration")
    logger.info(f"Configuring engine and context for online migration (url={url})")
    engine = engine_from_config(
        alembic.context.config.get_section(alembic.context.config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=None,
    )
    with engine.connect() as connection:
        logger.info("Connected to database, configuring context...")
        alembic.context.configure(connection=connection)
        with alembic.context.begin_transaction():
            logger.info("Running online migrations...")
            alembic.context.run_migrations()
            logger.info("Online migrations complete.")

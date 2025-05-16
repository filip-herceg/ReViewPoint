from loguru import logger
import sys
import os


def init_logger():
    logger.remove()
    os.makedirs("logs", exist_ok=True)
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | <cyan>{message}</cyan>",
        level="DEBUG",
    )
    logger.add("logs/backend.log", rotation="1 MB", retention="7 days", level="DEBUG")


# Exportiert konfigurierten Logger
log = logger

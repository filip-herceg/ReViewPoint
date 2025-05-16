from loguru import logger
import sys

logger.remove()  # remove default logger
logger.add(
    sys.stdout,
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    level="INFO",
)

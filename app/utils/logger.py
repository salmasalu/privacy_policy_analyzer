import logging
import os
from datetime import datetime

# LOG DIRECTORY

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, f"app_{datetime.now().strftime('%Y%m%d')}.log")

# FORMATTER

formatter = logging.Formatter(
    fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# HANDLERS

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)

# File handler
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)

# MAIN FUNCTION — import this everywhere

def get_logger(name: str) -> logging.Logger:
    """
    Usage:
        from utils.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Analysis started")
        logger.error("Something failed")
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger
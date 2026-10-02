"""Application-wide logging: console (warnings+) plus detailed file log."""

import logging

from ai_cost_monitor import constants


def setup_logging(verbosity: int) -> logging.Logger:
    """Configure root logging.

    Args:
        verbosity: 0 = INFO to file/WARN to console, 1 = INFO console, 2+ = DEBUG.
    """
    constants.LOGS_DIR.mkdir(parents=True, exist_ok=True)

    root_logger = logging.getLogger("ai_cost_monitor")
    root_logger.setLevel(logging.DEBUG)
    if root_logger.handlers:
        return root_logger

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(constants.LOGS_DIR / constants.LOG_FILE_NAME, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO if verbosity >= 1 else logging.WARNING)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    return root_logger

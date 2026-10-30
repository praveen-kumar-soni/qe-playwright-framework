import logging
from datetime import datetime

from src.utils.file_utils import ensure_dir

_LOG_DIR = ensure_dir("logs")
_LOG_FILE = _LOG_DIR / f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"


def get_logger(name: str) -> logging.Logger:
    """Return a logger configured with a consistent, readable format.

    Logs to both the console and a shared file for the current test run,
    under ``logs/test_run_<timestamp>.log``. Safe to call repeatedly for the
    same ``name`` (e.g. once per test module) without attaching duplicate
    handlers.
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%H:%M:%S")

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        file_handler = logging.FileHandler(_LOG_FILE)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        logger.setLevel(logging.INFO)
        logger.propagate = False

    return logger

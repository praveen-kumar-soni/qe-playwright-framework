import logging


def get_logger(name: str) -> logging.Logger:
    """Return a logger configured with a consistent, readable format.

    The logger will output messages to the console with timestamps, log levels, and the logger name.
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%H:%M:%S"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False

    return logger

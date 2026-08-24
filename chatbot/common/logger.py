import logging


def logger(name: str):
    """Create a logger instance."""
    log = logging.getLogger(name)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    if not log.handlers:
        log.addHandler(handler)
    log.setLevel(logging.INFO)
    return log

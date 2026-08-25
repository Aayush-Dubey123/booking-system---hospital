import logging
import sys

# Reconfigure stdout and stderr streams to use UTF-8.
# This prevents UnicodeEncodeError ('charmap' codec can't encode character) on Windows
# when logging or printing emojis/unicode characters (such as \U0001f449).
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def logger(name: str) -> logging.Logger:
    log = logging.getLogger(name)

    if not log.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        log.addHandler(handler)
        log.setLevel(logging.DEBUG)

    return log


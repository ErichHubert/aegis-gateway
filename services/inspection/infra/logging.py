from __future__ import annotations

import logging

from uvicorn.logging import DefaultFormatter

_UVICORN_FMT = "%(levelprefix)s %(name)s - %(message)s"


def configure_logging() -> None:
    """Configure logging with the same console format uvicorn uses."""
    level = getattr(logging, "INFO", logging.INFO)
    root = logging.getLogger()

    # If uvicorn already configured logging (its dictConfig runs after imports),
    # just align levels and let its handlers/formatters stand.
    if root.handlers:
        root.setLevel(level)
    else:
        handler = logging.StreamHandler()
        handler.setLevel(level)
        handler.setFormatter(DefaultFormatter(_UVICORN_FMT, use_colors=True))
        root.addHandler(handler)
        root.setLevel(level)

    # Keep uvicorn loggers at the same level; they keep their own formatters.
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "watchfiles"):
        logging.getLogger(name).setLevel(level)

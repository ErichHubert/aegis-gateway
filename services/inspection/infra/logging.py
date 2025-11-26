from __future__ import annotations

import logging
from .config import settings


def configure_logging() -> None:
    """Configure global logging format and level.

    For PoC: simple text logging.
    Later: JSON logging / structured logging for production.
    """
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )
from __future__ import annotations

import logging


def configure_logging() -> None:
    """Configure global logging format and level.

    For PoC: simple text logging.
    Later: JSON logging / structured logging for production.
    """
    level = getattr(logging, "INFO", logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )
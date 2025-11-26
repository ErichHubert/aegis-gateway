from __future__ import annotations

import uvicorn

from infra.logging import configure_logging


def main() -> None:
    """Entry point for running the ML inspection service."""
    configure_logging()
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # dev-only, disable in production
    )


if __name__ == "__main__":
    main()
from infra.config import settings


def check_liveness() -> dict:
    return {"status": "ok"}


def check_readiness() -> dict:
    """
    Place for future readiness checks:
    - config loaded
    - models initialized
    - external dependencies reachable (if any)
    """
    # Example skeleton:
    # if not models_loaded:
    #     return {"status": "degraded", "details": "Models not loaded"}
    return {"status": "ready"}
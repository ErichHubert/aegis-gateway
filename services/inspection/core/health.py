def check_liveness() -> dict:
    return {"status": "ok"}


def check_readiness() -> dict:
    """
    Place for future readiness checks:
    - config loaded
    - models initialized
    - external dependencies reachable (if any)
    """
    from infra.warmup import WARMUP_ERRORS, WARMUP_OK

    if not WARMUP_OK:
        return {"status": "degraded", "details": WARMUP_ERRORS}

    return {"status": "ready"}

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.concurrency import run_in_threadpool

from core.health import check_liveness, check_readiness
from core.models import PromptInspectionRequest, PromptInspectionResponse
from core.rules import analyze_prompt
from bootstrap import initialize_pipeline
from infra.logging import configure_logging


logger = logging.getLogger(__name__)
# Ensure logging is configured even when uvicorn is launched directly (bypassing main.py).
configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize detectors before serving; app only starts if it succeeds."""
    detector_pipeline = initialize_pipeline()
    app.state.detectors = detector_pipeline
    logger.info("Inspection service started with %d detectors", len(detector_pipeline))
    yield


app = FastAPI(
    title="Aegis ML Inspection Service",
    description="""
            Aegis ML Inspection Service

            Inspects LLM prompts for:
            - secrets (API keys, tokens)
            - PII (emails, phone numbers, etc.)
            - prompt injection indicators

            Designed to be called from the Aegis Gateway.
            """,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


@app.post(
    "/inspect",
    response_model=PromptInspectionResponse,
    summary="Inspect a prompt for security issues",
    tags=["inspection"],
)
async def inspect(req: PromptInspectionRequest, request: Request) -> PromptInspectionResponse:
    """Runs all enabled detectors on the given prompt and returns findings."""
    meta = req.meta.dict() if req.meta else {}
    prompt_len = len(req.prompt or "")
    logger.info(
        "Inspect request received (prompt_len=%d, user_id=%s, source=%s)",
        prompt_len,
        meta.get("userId"),
        meta.get("source"),
    )
    detectors = getattr(request.app.state, "detectors", None)
    resp = await run_in_threadpool(analyze_prompt, req, detectors)
    finding_types = sorted({f.type for f in resp.findings})
    logger.info(
        "Inspect request completed (findings=%d, types=%s)",
        len(resp.findings),
        finding_types if finding_types else "none",
    )
    return resp


@app.get("/health/live", tags=["health"])
async def health_live() -> dict:
    return check_liveness()


@app.get("/health/ready", tags=["health"])
async def health_ready() -> dict:
    return check_readiness()

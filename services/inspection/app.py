from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.concurrency import run_in_threadpool

from core.health import check_liveness, check_readiness
from core.models import PromptInspectionRequest, PromptInspectionResponse
from core.rules import analyze_prompt
from bootstrap import initialize_pipeline


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize detectors before serving; app only starts if it succeeds."""
    detector_pipeline = initialize_pipeline()
    app.state.detectors = detector_pipeline
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
    detectors = getattr(request.app.state, "detectors", None)
    return await run_in_threadpool(analyze_prompt, req, detectors)



@app.get("/health/live", tags=["health"])
async def health_live() -> dict:
    return check_liveness()


@app.get("/health/ready", tags=["health"])
async def health_ready() -> dict:
    return check_readiness()

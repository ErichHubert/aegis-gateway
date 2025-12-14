from __future__ import annotations

from fastapi import FastAPI
from fastapi.concurrency import run_in_threadpool

from core.health import check_liveness, check_readiness
from core.models import PromptInspectionRequest, PromptInspectionResponse
from core.rules import analyze_prompt
from infra.warmup import run_warmup

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
    openapi_url="/openapi.json"
)


@app.on_event("startup")
def _warmup_sync() -> None:
    """Run warmup synchronously so the app only starts if it succeeds."""
    run_warmup()


@app.post(
    "/inspect",
    response_model=PromptInspectionResponse,
    summary="Inspect a prompt for security issues",
    tags=["inspection"],
)
async def inspect(req: PromptInspectionRequest) -> PromptInspectionResponse:
    """Runs all enabled detectors on the given prompt and returns findings."""
    return await run_in_threadpool(analyze_prompt, req)



@app.get("/health/live", tags=["health"])
async def health_live() -> dict:
    return check_liveness()


@app.get("/health/ready", tags=["health"])
async def health_ready() -> dict:
    return check_readiness()

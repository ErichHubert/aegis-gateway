from __future__ import annotations

from fastapi import FastAPI
from core.models import PromptInspectionRequest, PromptInspectionResponse
from core.health import check_liveness, check_readiness
from core.rules import analyze_prompt

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


@app.post(
    "/inspect",
    response_model=PromptInspectionResponse,
    summary="Inspect a prompt for security issues",
    tags=["inspection"],
)
async def inspect(req: PromptInspectionRequest) -> PromptInspectionResponse:
    """Runs all enabled detectors on the given prompt and returns findings."""
    return analyze_prompt(req)



@app.get("/health/live", tags=["health"])
async def health_live() -> dict:
    return check_liveness()


@app.get("/health/ready", tags=["health"])
async def health_ready() -> dict:
    return check_readiness()
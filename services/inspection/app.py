from __future__ import annotations

from fastapi import FastAPI
from core.models import PromptInspectionRequest, PromptInspectionResponse
from core.health import check_liveness, check_readiness
from core.rules import analyze_prompt
from infra.config import settings

app = FastAPI(
    title=settings.app_name,
    description=settings.app_desc,
    version=settings.app_version,
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
    openapi_url=settings.openapi_url
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
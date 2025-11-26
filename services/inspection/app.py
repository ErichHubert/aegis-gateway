from __future__ import annotations

from fastapi import FastAPI
from core.models import PromptInspectionRequest, PromptInspectionResponse
from core.rules import analyze_prompt
from infra.config import settings

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
)


@app.post("/inspect", response_model=PromptInspectionResponse)
async def inspect(req: PromptInspectionRequest) -> PromptInspectionResponse:
    """Main endpoint: called by the gateway to inspect a prompt."""
    # analyze_prompt is synchronous but fast enough to call from an async route
    return analyze_prompt(req)
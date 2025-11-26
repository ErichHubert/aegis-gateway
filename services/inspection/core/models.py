from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class PromptInspectionMeta(BaseModel):
    """Optional metadata about the prompt, forwarded by the gateway."""
    userId: Optional[str] = Field(default=None)
    source: Optional[str] = Field(
        default=None,
        description="Route/service identifier from the gateway (e.g. 'gateway/ollama').",
    )


class PromptInspectionRequest(BaseModel):
    """Request contract from the gateway to the ML service."""
    prompt: str = Field(..., description="The raw user prompt text.")
    meta: Optional[PromptInspectionMeta] = None


class Finding(BaseModel):
    """Represents a single finding, e.g. PII, secret, or injection indicator."""
    type: str = Field(..., description="Machine-readable type ID, e.g. 'secret_api_key'.")
    message: str = Field(..., description="Human-readable explanation of the finding.")


class PromptInspectionResponse(BaseModel):
    """Response back to the gateway: allow/deny plus a list of findings."""
    isAllowed: bool = Field(..., description="True if the request should be allowed.")
    findings: List[Finding] = Field(default_factory=list)
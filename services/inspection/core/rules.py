from __future__ import annotations

from typing import List
from core.models import PromptInspectionRequest, PromptInspectionResponse, Finding
from core.detectors.secrets import detect_secrets
from core.detectors.pii import detect_pii
from core.detectors.injection import detect_prompt_injection


def analyze_prompt(req: PromptInspectionRequest) -> PromptInspectionResponse:
    """Central rule engine.

    - invokes all detectors
    - decides if the prompt is allowed
    - aggregates findings in a response
    """
    text = req.prompt
    all_findings: List[Finding] = []

    all_findings.extend(detect_secrets(text))
    all_findings.extend(detect_pii(text))
    all_findings.extend(detect_prompt_injection(text))

    # PoC policy:
    # - Secrets => block
    # - Injection => block
    # - PII => warn only (still allowed)
    is_allowed = True
    for f in all_findings:
        if f.type.startswith("secret_") or f.type.startswith("prompt_injection_"):
            is_allowed = False
            break

    return PromptInspectionResponse(
        isAllowed=is_allowed,
        findings=all_findings
    )
from __future__ import annotations

from typing import List
from core.models import PromptInspectionRequest, PromptInspectionResponse, Finding
from core.detectors.secrets import find_secrets
from core.detectors.pii import find_pii
from core.detectors.injection import find_injections


def analyze_prompt(req: PromptInspectionRequest) -> PromptInspectionResponse:
    """Central rule engine.

    - invokes all detectors
    - decides if the prompt is allowed
    - aggregates findings in a response
    """
    text = req.prompt
    all_findings: List[Finding] = []

    all_findings.extend(find_secrets(text))
    all_findings.extend(find_pii(text))
    all_findings.extend(find_injections(text))

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
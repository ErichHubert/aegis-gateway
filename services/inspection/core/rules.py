from __future__ import annotations

from typing import List

from core.models import PromptInspectionRequest, PromptInspectionResponse, Finding
from core.detectors.secrets import detect_secrets
from core.detectors.pii import detect_pii
from core.detectors.injection import detect_prompt_injection
from infra.config import settings  

__all__ = ["analyze_prompt"]

# Order for comparing severity levels
_SEVERITY_ORDER = {
    "low": 1,
    "medium": 2,
    "high": 3,
}


def _get_severity(finding: Finding) -> str:
    """
    Resolve severity for a finding type.

    Priority:
    1. Explicit mapping from settings.detection.severity_by_type
    2. Fallback by type prefix (secret_ / prompt_injection_ / pii_)
    3. Default: "low"
    """

    mapping = settings.detection.severity_by_type
    if finding.type in mapping:
        return mapping[finding.type]

    # Fallback by naming convention 
    if finding.type.startswith("secret_"):
        return "high"
    if finding.type.startswith("prompt_injection_"):
        return "high"
    if finding.type.startswith("pii_"):
        return "medium"

    # Unknown everything-else
    return "low"


def _should_block(findings: List[Finding]) -> bool:
    """
    Decide whether the prompt should be blocked, based on:
    - findings severities
    - configured block threshold in settings.policy.block_severity
    """
    if not findings:
        return False

    block_severity = settings.policy.block_severity  # "low" | "medium" | "high"
    block_level = _SEVERITY_ORDER[block_severity]

    for f in findings:
        sev = _get_severity(f)
        level = _SEVERITY_ORDER.get(sev, 1)
        if level >= block_level:
            return True

    return False


def analyze_prompt(req: PromptInspectionRequest) -> PromptInspectionResponse:
    """
    Central rule engine.

    - invokes all detectors
    - decides if the prompt is allowed (based on severity + policy)
    - aggregates findings in a response
    """
    text = req.prompt or ""
    all_findings: List[Finding] = []

    all_findings.extend(detect_secrets(text))
    all_findings.extend(detect_pii(text))
    all_findings.extend(detect_prompt_injection(text))

    # Policy:
    # - severities are resolved per finding
    # - settings.policy.block_severity decides from which level on we block
    is_allowed = not _should_block(all_findings)

    return PromptInspectionResponse(
        isAllowed=is_allowed,
        findings=all_findings,
    )
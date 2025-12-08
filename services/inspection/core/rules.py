from __future__ import annotations

from typing import List

from core.models import PromptInspectionRequest, PromptInspectionResponse, Finding
from core.detectors.protocols import IDetector
from core.detectors.pii import PresidioPiiDetector
from core.detectors.secret  import SecretRegexDetector
from core.detectors.injection import InjectionPatternDetector

# Static detector pipeline for now.
# Each detector implements IDetector.detect(prompt: str) -> List[Finding]
_DETECTORS: tuple[IDetector, ...] = (
    SecretRegexDetector(),
    PresidioPiiDetector(),
    InjectionPatternDetector(),
)


def analyze_prompt(req: PromptInspectionRequest) -> PromptInspectionResponse:
    """
    Central rule engine for the inspection service.

    Responsibilities:
    - fan-out the prompt to all configured detectors
    - aggregate their findings
    """
    text = req.prompt or ""
    all_findings: List[Finding] = []

    for detector in _DETECTORS:
        # Each detector is responsible for:
        # - reading its own config (severity, enabled flags, thresholds)
        # - talking to Presidio / regex / ML, etc.
        findings = detector.detect(text)
        if findings:
            all_findings.extend(findings)

    return PromptInspectionResponse(findings=all_findings)
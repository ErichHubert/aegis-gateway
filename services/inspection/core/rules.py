from __future__ import annotations

from typing import List

from core.models import PromptInspectionRequest, PromptInspectionResponse, Finding
from core.detectors.protocols import IDetector

_DETECTORS: tuple[IDetector, ...] | None = None


def set_detectors(detectors: tuple[IDetector, ...]) -> None:
    """Configure the detector pipeline; called during warmup."""
    global _DETECTORS
    _DETECTORS = detectors


def analyze_prompt(req: PromptInspectionRequest) -> PromptInspectionResponse:
    """
    Central rule engine for the inspection service.

    Responsibilities:
    - fan-out the prompt to all configured detectors
    - aggregate their findings
    """
    if _DETECTORS is None:
        raise RuntimeError("Detector pipeline is not configured. Ensure warmup ran before handling requests.")

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

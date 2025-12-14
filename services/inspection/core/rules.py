from __future__ import annotations

from typing import List, Sequence

from core.models import PromptInspectionRequest, PromptInspectionResponse, Finding
from core.detectors.protocols import IDetector


def analyze_prompt(
    req: PromptInspectionRequest,
    detectors: Sequence[IDetector] | None,
) -> PromptInspectionResponse:
    """
    Central rule engine for the inspection service.

    Responsibilities:
    - fan-out the prompt to all configured detectors
    - aggregate their findings
    """
    if detectors is None:
        raise RuntimeError("Detector pipeline is not configured. Ensure warmup ran before handling requests.")

    text = req.prompt or ""
    all_findings: List[Finding] = []

    for detector in detectors:
        # Each detector is responsible for:
        # - reading its own config (severity, enabled flags, thresholds)
        # - talking to Presidio / regex / ML, etc.
        findings = detector.detect(text)
        if findings:
            all_findings.extend(findings)

    return PromptInspectionResponse(findings=all_findings)

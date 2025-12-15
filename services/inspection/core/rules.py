from __future__ import annotations

import logging
from typing import List, Sequence

from core.models import PromptInspectionRequest, PromptInspectionResponse, Finding
from core.detectors.protocols import IDetector

logger = logging.getLogger(__name__)


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
        logger.error("Detector pipeline is not configured; refusing to analyze prompt")
        raise RuntimeError("Detector pipeline is not configured. Ensure warmup ran before handling requests.")

    text = req.prompt or ""
    all_findings: List[Finding] = []

    logger.info("Analyzing prompt with %d detectors", len(detectors))

    for detector in detectors:
        detector_name = detector.__class__.__name__
        # Each detector is responsible for:
        # - reading its own config (severity, enabled flags, thresholds)
        # - talking to Presidio / regex / ML, etc.
        logger.debug("Running detector: %s", detector_name)
        try:
            findings = detector.detect(text)
        except Exception:
            logger.exception("Detector '%s' raised an exception", detector_name)
            raise

        if findings:
            logger.info(
                "Detector '%s' returned %d findings",
                detector_name,
                len(findings),
            )
            all_findings.extend(findings)

    logger.info("Prompt analysis complete; total findings=%d", len(all_findings))
    return PromptInspectionResponse(findings=all_findings)

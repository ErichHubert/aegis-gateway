from __future__ import annotations

from typing import List, Sequence

from core.models import Finding
from core.detectors.protocols import IInjectionDetector


class InjectionDetectionOrchestrator(IInjectionDetector):
    """High-level prompt injection detector orchestrating multiple lower-level detectors."""

    def __init__(self, detectors: Sequence[IInjectionDetector]) -> None:
        if not detectors:
            raise ValueError("InjectionDetectionOrchestrator requires at least one detector")
        self._detectors: list[IInjectionDetector] = list(detectors)

    def detect(self, prompt: str) -> List[Finding]:
        if not prompt:
            return []

        findings: list[Finding] = []

        for detector in self._detectors:
            try:
                detector_findings = detector.detect(prompt)
            except Exception:
                # In production you’d log this instead of silently ignoring
                continue

            if detector_findings:
                findings.extend(detector_findings)

        return _dedupe_findings(findings)


def _dedupe_findings(findings: list[Finding]) -> list[Finding]:
    """Simple de-duplication based on (type, start, end)."""
    seen: set[tuple[str, int, int]] = set()
    deduped: list[Finding] = []

    for f in findings:
        key = (f.type, f.start, f.end)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(f)

    return deduped
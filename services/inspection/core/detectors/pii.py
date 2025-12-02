from __future__ import annotations

from typing import List

from core.models import Finding
from core.engines.presidio_engine import get_analyzer
from infra.config import settings


def detect_pii(prompt: str) -> List[Finding]:
    """Detect PII using Presidio with a spaCy backend and map severities from config."""

    if not prompt:
        return []

    analyzer = get_analyzer()

    results = analyzer.analyze(
        text=prompt,
        language=settings.detection.pii_default_lang,
    )

    findings: List[Finding] = []

    for r in results:
        # Presidio entity_type examples: "EMAIL_ADDRESS", "PHONE_NUMBER", "IBAN_CODE"
        presidio_type = r.entity_type

        # Map Presidio type -> internal canonical type (e.g. "pii_email")
        internal_type = settings.detection.pii_type_map.get(
            presidio_type,
            f"pii_{presidio_type.lower()}",  # sane fallback
        )

        # Map internal type -> severity ("low" | "medium" | "high")
        severity = settings.detection.severity_by_type.get(
            internal_type,
            settings.detection.pii_default_severity,
        )

        findings.append(
            Finding(
                type=internal_type,
                start=r.start,
                end=r.end,
                snippet=prompt[r.start:r.end],
                message=f"Detected PII entity '{presidio_type}'.",
                severity=severity,
            )
        )

    return findings
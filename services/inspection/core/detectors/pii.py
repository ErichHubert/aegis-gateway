from __future__ import annotations

import re
from typing import List
from core.models import Finding

EMAIL_REGEX = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")


def find_pii(text: str) -> List[Finding]:
    """Very simple PII heuristic.

    Later:
    - integrate Presidio / spaCy / ML-based detectors
    """
    findings: List[Finding] = []

    if EMAIL_REGEX.search(text):
        findings.append(Finding(
            type="pii_email",
            message="Potential email address detected in prompt."
        ))

    return findings
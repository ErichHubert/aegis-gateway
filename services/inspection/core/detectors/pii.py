from __future__ import annotations

import re
from typing import List
from core.models import Finding

_PII_PATTERN = [
    (
        "pii_email",
        re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"),
        "Possible email address detected."
    ),
    (
        "pii_phone",
        re.compile(r"\+?[0-9][0-9\s\-\/]{6,}"),
        "Possible phone number detected."
    ),
]


def detect_pii(prompt: str) -> List[Finding]:
    findings: List[Finding] = []
    for type_id, pattern, message in _PII_PATTERN:
        for match in pattern.finditer(prompt):
            start, end = match.span()
            snippet = prompt[start:end]
            findings.append(
                Finding(
                    type=type_id,
                    start=start,
                    end=end,
                    snippet=snippet,
                    message=message
                )
            )

    return findings
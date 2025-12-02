from __future__ import annotations

import re
from typing import List
from core.models import Finding 


_SECRET_PATTERNS = [
    (
        "secret_aws_access_key", 
        re.compile(r"AKIA[0-9A-Z]{16}"), 
        "Possible AWS Access Key detected."
    ),
    (
        "secret_generic_token",
        re.compile(r"[A-Za-z0-9_\-]{20,}"), 
        "High-entropy token-like string detected."
    ),
    (
        "secret_jwt",
        re.compile(r"eyJ[a-zA-Z0-9_\-]+?\.[a-zA-Z0-9_\-]+?\.[a-zA-Z0-9_\-]+"),
        "Possible JWT token detected."
    ),
    (
        "secret_pem_block",
        re.compile(r"-----BEGIN (?:RSA |EC |)PRIVATE KEY-----"),
        "Possible private key block detected."
    ),
]


def detect_secrets(prompt: str) -> List[Finding]:
    findings: List[Finding] = []

    if not prompt:
        return findings

    for type_id, pattern, message in _SECRET_PATTERNS:
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
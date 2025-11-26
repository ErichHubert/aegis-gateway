from __future__ import annotations

from typing import List
from core.models import Finding

# Very naive keyword-based rules for prompt injection.
INJECTION_KEYWORDS = [
    "ignore previous instructions",
    "you are now",
    "disregard all prior rules",
    "system prompt",
]


def find_injections(text: str) -> List[Finding]:
    """Simple heuristic for obvious prompt injection attempts.

    Later:
    - classifier-based detection
    - language-agnostic / multi-language rules
    """
    lower = text.lower()
    findings: List[Finding] = []

    for keyword in INJECTION_KEYWORDS:
        if keyword in lower:
            findings.append(Finding(
                type="prompt_injection_suspected",
                message=f"Prompt contains injection keyword: '{keyword}'."
            ))

    return findings
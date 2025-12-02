from __future__ import annotations

import re
from typing import List

from core.models import Finding

# Each entry: (type_id, compiled_regex, human_readable_message)
_INJECTION_PATTERNS: list[tuple[str, re.Pattern[str], str]] = [
    (
        "prompt_injection_ignore_instructions",
        re.compile(r"(?i)ignore (all )?previous instructions"),
        "Prompt attempts to bypass prior instructions.",
    ),
    (
        "prompt_injection_disregard_safety",
        re.compile(
            r"(?i)(disregard|ignore) (the )?(safety|security|policy|guidelines?)",
        ),
        "Prompt attempts to bypass safety or security rules.",
    ),
    (
        "prompt_injection_system_override",
        re.compile(r"(?i)you are now no longer.*", re.DOTALL),
        "Prompt tries to override the system role.",
    ),
    (
        "prompt_injection_change_identity",
        re.compile(
            r"(?i)(forget that you are|you are not an ai|act as a human)",
        ),
        "Prompt asks the model to change or hide its identity.",
    ),
    (
        "prompt_injection_reveal_system_prompt",
        re.compile(
            r"(?i)(show|reveal|print) (your )?(system prompt|hidden instructions?)",
        ),
        "Prompt tries to exfiltrate the system prompt or hidden instructions.",
    ),
    (
        "prompt_injection_override_priority",
        re.compile(
            r"(?i)(follow my instructions.*even if|obey me instead of|my instructions override)",
        ),
        "Prompt explicitly tries to override higher-priority instructions.",
    ),
]


def detect_prompt_injection(prompt: str) -> List[Finding]:
    findings: List[Finding] = []

    if not prompt:
        return findings

    for type_id, pattern, message in _INJECTION_PATTERNS:
        for match in pattern.finditer(prompt):
            start, end = match.span()
            snippet = prompt[start:end]
            findings.append(
                Finding(
                    type=type_id,
                    start=start,
                    end=end,
                    snippet=snippet,
                    message=message,
                )
            )

    return findings
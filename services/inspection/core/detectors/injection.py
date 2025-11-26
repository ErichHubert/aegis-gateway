import re
from typing import List
from core.models import Finding

_INJECTION_PATTERNS = [
    (
        "prompt_injection_ignore_instructions",
        re.compile(r"(?i)ignore (all )?previous instructions"),
        "Prompt attempts to bypass prior instructions."
    ),
    (
        "prompt_injection_system_override",
        re.compile(r"(?i)you are now no longer.*", re.DOTALL),
        "Prompt tries to override the system role."
    ),
]


def detect_prompt_injection(prompt: str) -> List[Finding]:
    findings: List[Finding] = []

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
                    message=message
                )
            )

    return findings
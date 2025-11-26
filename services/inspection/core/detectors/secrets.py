from __future__ import annotations

import re
from typing import List
from core.models import Finding

# Very simple demo patterns – extend later.
AWS_KEY_REGEX = re.compile(r"AKIA[0-9A-Z]{16}")
GENERIC_TOKEN_REGEX = re.compile(r"[A-Za-z0-9_\-]{24,}")


def find_secrets(text: str) -> List[Finding]:
    """Search for obvious secrets in the text.

    Later:
    - more provider-specific patterns
    - entropy-based checks
    """
    findings: List[Finding] = []

    if AWS_KEY_REGEX.search(text):
        findings.append(Finding(
            type="secret_aws_access_key",
            message="Potential AWS access key detected."
        ))

    # Extremely naive heuristic: long token-like strings
    if GENERIC_TOKEN_REGEX.search(text):
        findings.append(Finding(
            type="secret_generic_token",
            message="Potential secret-like token detected (length >= 24)."
        ))

    return findings
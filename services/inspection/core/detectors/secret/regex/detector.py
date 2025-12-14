from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import List, Dict, Tuple

from infra.warmable import Warmable
from core.models import Finding
from core.detectors.protocols import IDetector
from core.config.loader import load_config
from core.config.models import InspectionConfig  # matches policy/config.yml

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class _SecretPattern:
    type_id: str
    pattern: re.Pattern[str]
    message: str
    severity: str


class SecretRegexDetector(IDetector, Warmable):
    """
    Regex-based secret detector.

    Responsibilities:
    - Read detection.secrets.engines.regex.* from policy.yml.
    - Respect `enabled` and `severity` per detector.
    - Run a fixed set of regex patterns for common secret types.
    - Return `Finding` objects with type, span, snippet, message, severity, confidence.

    This detector does *not* decide allow/block – the gateway does that
    based on the `severity` values and its own policy configuration.
    """

    # Map config detector keys -> (compiled regex, default human-readable message)
    _REGEX_DEFINITIONS: Dict[str, Tuple[re.Pattern[str], str]] = {
        "aws_access_key": (
            re.compile(r"AKIA[0-9A-Z]{16}"),
            "Possible AWS Access Key detected.",
        ),
        "generic_token": (
            re.compile(r"[A-Za-z0-9_\-]{20,}"),
            "High-entropy token-like string detected.",
        ),
        "jwt": (
            re.compile(
                r"eyJ[a-zA-Z0-9_\-]+?\.[a-zA-Z0-9_\-]+?\.[a-zA-Z0-9_\-]+"
            ),
            "Possible JWT token detected.",
        ),
        "pem_block": (
            re.compile(r"-----BEGIN (?:RSA |EC |)PRIVATE KEY-----"),
            "Possible private key block detected.",
        ),
    }

    def __init__(self) -> None:
        config: InspectionConfig = load_config()
        secrets_cfg = config.detection.secrets
        regex_cfg = secrets_cfg.engines.regex

        if not regex_cfg.enabled:
            logger.warning(
                "SecretRegexDetector: regex engine is disabled in policy. "
                "No secret patterns will be evaluated."
            )
            self._patterns: tuple[_SecretPattern, ...] = ()
            return

        detectors_cfg = regex_cfg.detectors or {}
        patterns: list[_SecretPattern] = []

        # Helper to add a pattern if the detector exists and is enabled
        def add_pattern(key: str, regex: re.Pattern[str], default_message: str) -> None:
            rule = detectors_cfg.get(key)
            if rule is None:
                logger.debug("SecretRegexDetector: detector '%s' not configured; skipping.", key)
                return

            if not rule.enabled:
                logger.info("SecretRegexDetector: detector '%s' is disabled in policy; skipping.", rule.id,)
                return

            type_id = rule.id
            severity = rule.severity
            message = rule.display_name or default_message

            patterns.append(
                _SecretPattern(
                    type_id=type_id,
                    pattern=regex,
                    message=message,
                    severity=severity,
                )
            )

        # Bind configured detectors to concrete regexes
        for key, (regex, default_message) in self._REGEX_DEFINITIONS.items():
            add_pattern(key, regex, default_message)

        if not patterns:
            logger.warning(
                "SecretRegexDetector initialized with no active patterns. "
                "Check detection.secrets.engines.regex.detectors in policy.yml."
            )

        self._patterns = tuple(patterns)

    def warmup(self) -> None:
        """No-op warmup hook; initialization already loads patterns."""
        _ = self._patterns

    def detect(self, prompt: str) -> List[Finding]:
        """
        Run all configured secret regex patterns over the prompt text.

        Returns:
            List[Finding]: zero or more findings with type, span, snippet, message, severity, confidence.
        """
        findings: List[Finding] = []

        if not prompt:
            return findings

        for p in self._patterns:
            for match in p.pattern.finditer(prompt):
                start, end = match.span()
                snippet = prompt[start:end]

                findings.append(
                    Finding(
                        type=p.type_id,
                        start=start,
                        end=end,
                        snippet=snippet,
                        message=p.message,
                        severity=p.severity,
                        confidence=1.0,
                    )
                )

        return findings

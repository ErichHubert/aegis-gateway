from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import List

from core.models import Finding
from core.detectors.protocols import IDetector
from core.config.loader import load_config
from core.config.models import InspectionConfig 

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class _SecretPattern:
    type_id: str
    pattern: re.Pattern[str]
    message: str
    severity: str


class SecretRegexDetector(IDetector):
    """
    Regex-based secret detector.

    Responsibilities:
    - Load secret detector config from policy.yaml (IDs, enabled flags, severity).
    - Run a fixed set of regex patterns for common secret types.
    - Return `Finding` objects with type, span, snippet, message, severity.

    This detector does *not* decide allow/block – that is done by the gateway
    based on the `severity` values.
    """

    def __init__(self) -> None:
        config: InspectionConfig = load_config()
        secrets_cfg = config.detection.secrets

        patterns: list[_SecretPattern] = []

        # Helper to add a pattern if the config entry exists and is enabled
        def add_pattern(cfg, regex: re.Pattern[str], default_message: str) -> None:
            if cfg is None:
                logger.debug("Secret detector config entry is missing; skipping pattern.")
                return
            if not cfg.enabled:
                logger.info(
                    "Secret detector '%s' is disabled in policy; skipping.",
                    getattr(cfg, "id", "<unknown>"),
                )
                return

            type_id = cfg.id
            severity = cfg.severity
            message = cfg.display_name or default_message

            patterns.append(
                _SecretPattern(
                    type_id=type_id,
                    pattern=regex,
                    message=message,
                    severity=severity,
                )
            )

        # Map your YAML secrets section → concrete regexes
        add_pattern(
            secrets_cfg.aws_access_key,
            re.compile(r"AKIA[0-9A-Z]{16}"),
            "Possible AWS Access Key detected.",
        )
        add_pattern(
            secrets_cfg.generic_token,
            re.compile(r"[A-Za-z0-9_\-]{20,}"),
            "High-entropy token-like string detected.",
        )
        add_pattern(
            secrets_cfg.jwt,
            re.compile(r"eyJ[a-zA-Z0-9_\-]+?\.[a-zA-Z0-9_\-]+?\.[a-zA-Z0-9_\-]+"),
            "Possible JWT token detected.",
        )
        add_pattern(
            secrets_cfg.pem_block,
            re.compile(r"-----BEGIN (?:RSA |EC |)PRIVATE KEY-----"),
            "Possible private key block detected.",
        )

        if not patterns:
            logger.warning(
                "SecretRegexDetector initialized with no active patterns. "
                "Check detection.secrets configuration in policy.yaml."
            )

        self._patterns: tuple[_SecretPattern, ...] = tuple(patterns)

    def detect(self, prompt: str) -> List[Finding]:
        """
        Run all configured secret regex patterns over the prompt text.

        Returns:
            List[Finding]: zero or more findings with type, span, snippet, message, severity.
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
                    )
                )

        return findings
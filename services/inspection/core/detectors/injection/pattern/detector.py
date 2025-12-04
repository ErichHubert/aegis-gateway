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
class _PatternDefinition:
    """Static definition: which policy entry this pattern belongs to."""
    policy_key: str              # e.g. "generic", "override", "suspicious"
    regex: re.Pattern[str]
    message: str


@dataclass(frozen=True)
class _ResolvedPattern:
    """Runtime pattern with resolved type + severity from policy."""
    type_id: str                 # e.g. "prompt_injection_generic"
    severity: str                # e.g. "high"
    regex: re.Pattern[str]
    message: str


# Static pattern definitions – grouped by policy_key
_PATTERN_DEFS: list[_PatternDefinition] = [
    _PatternDefinition(
        policy_key="generic",
        regex=re.compile(r"(?i)ignore (all )?previous instructions"),
        message="Prompt attempts to bypass prior instructions.",
    ),
    _PatternDefinition(
        policy_key="generic",
        regex=re.compile(r"(?i)(disregard|ignore) (the )?(safety|security|policy|guidelines?)"),
        message="Prompt attempts to bypass safety or security rules.",
    ),
    _PatternDefinition(
        policy_key="override",
        regex=re.compile(r"(?i)you are now no longer.*", re.DOTALL),
        message="Prompt tries to override the system role.",
    ),
    _PatternDefinition(
        policy_key="generic",
        regex=re.compile(r"(?i)(forget that you are|you are not an ai|act as a human)"),
        message="Prompt asks the model to change or hide its identity.",
    ),
    _PatternDefinition(
        policy_key="suspicious",
        regex=re.compile(r"(?i)(show|reveal|print) (your )?(system prompt|hidden instructions?)"),
        message="Prompt tries to exfiltrate the system prompt or hidden instructions.",
    ),
    _PatternDefinition(
        policy_key="override",
        regex=re.compile(r"(?i)(follow my instructions.*even if|obey me instead of|my instructions override)"),
        message="Prompt explicitly tries to override higher-priority instructions.",
    ),
]


class InjectionPatternDetector(IDetector):
    """
    Regex-based prompt injection detector.

    - Groups patterns into logical categories (generic / override / suspicious)
      via `policy_key`.
    - For each category, reads `id`, `enabled`, `severity` from policy.yaml
      under `detection.prompt_injection`.
    - Produces `Finding` objects with:
        - type    -> policy entry `id` (e.g. "prompt_injection_override")
        - snippet -> matched part of the prompt
        - severity-> from policy (e.g. "high", "medium")
    """

    def __init__(self) -> None:
        policy: InspectionConfig = load_config()
        cfg = policy.detection.prompt_injection

        resolved: list[_ResolvedPattern] = []

        for p in _PATTERN_DEFS:
            # Look up matching policy entry: generic / override / suspicious
            entry = getattr(cfg, p.policy_key, None)
            if entry is None:
                logger.warning(
                    "Prompt injection policy entry '%s' missing in config; "
                    "pattern '%s' will be skipped.",
                    p.policy_key,
                    p.regex.pattern,
                )
                continue

            if not entry.enabled:
                logger.info(
                    "Prompt injection detector '%s' is disabled; "
                    "pattern '%s' will be skipped.",
                    entry.id,
                    p.regex.pattern,
                )
                continue

            resolved.append(
                _ResolvedPattern(
                    type_id=entry.id,
                    severity=entry.severity,
                    regex=p.regex,
                    message=p.message,
                )
            )

        if not resolved:
            logger.warning(
                "PromptInjectionPatternDetector initialized with NO active patterns. "
                "Check detection.prompt_injection section in policy.yaml."
            )

        self._patterns: tuple[_ResolvedPattern, ...] = tuple(resolved)

    def detect(self, prompt: str) -> List[Finding]:
        findings: List[Finding] = []

        if not prompt or not self._patterns:
            return findings

        for p in self._patterns:
            for match in p.regex.finditer(prompt):
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
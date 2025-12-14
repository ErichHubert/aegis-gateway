from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import List

from infra.warmable import Warmable
from core.models import Finding
from core.detectors.protocols import IDetector
from core.config.models import InspectionConfig

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class _PatternDefinition:
    """Static definition: which policy detector this pattern belongs to."""
    detector_key: str            # e.g. "generic", "override", "suspicious"
    regex: re.Pattern[str]
    message: str


@dataclass(frozen=True)
class _ResolvedPattern:
    """Runtime pattern with resolved type + severity from policy."""
    type_id: str                 # e.g. "prompt_injection_override"
    severity: str                # e.g. "high"
    regex: re.Pattern[str]
    message: str


# Static pattern definitions – grouped by detector_key
_PATTERN_DEFS: list[_PatternDefinition] = [
    _PatternDefinition(
        detector_key="generic",
        regex=re.compile(r"(?i)ignore (all )?previous instructions"),
        message="Prompt attempts to bypass prior instructions.",
    ),
    _PatternDefinition(
        detector_key="generic",
        regex=re.compile(r"(?i)(disregard|ignore) (the )?(safety|security|policy|guidelines?)"),
        message="Prompt attempts to bypass safety or security rules.",
    ),
    _PatternDefinition(
        detector_key="override",
        regex=re.compile(r"(?i)you are now no longer.*", re.DOTALL),
        message="Prompt tries to override the system role.",
    ),
    _PatternDefinition(
        detector_key="generic",
        regex=re.compile(r"(?i)(forget that you are|you are not an ai|act as a human)"),
        message="Prompt asks the model to change or hide its identity.",
    ),
    _PatternDefinition(
        detector_key="suspicious",
        regex=re.compile(r"(?i)(show|reveal|print) (your )?(system prompt|hidden instructions?)"),
        message="Prompt tries to exfiltrate the system prompt or hidden instructions.",
    ),
    _PatternDefinition(
        detector_key="override",
        regex=re.compile(r"(?i)(follow my instructions.*even if|obey me instead of|my instructions override)"),
        message="Prompt explicitly tries to override higher-priority instructions.",
    ),
]


class InjectionPatternDetector(IDetector, Warmable):
    """
    Regex-based prompt injection detector.

    For each static pattern we:
      - look up the matching detector by its key (generic/override/suspicious)
      - skip if engine or detector is disabled
      - emit Finding with:
          type      -> detector.id   (e.g. "prompt_injection_override")
          severity  -> detector.severity
          snippet   -> matched part of the prompt
          confidence-> 1.0 (static rules)
    """

    def __init__(self, config: InspectionConfig) -> None:
        policy: InspectionConfig = config
        # Engine: detection.prompt_injection.engines.pattern
        pi_cfg = policy.detection.prompt_injection
        pattern_engine = pi_cfg.engines.pattern

        if not pattern_engine.enabled:
            logger.info(
                "Prompt injection pattern engine is disabled via config "
                "(detection.prompt_injection.engines.pattern.enabled=false)."
            )
            self._patterns: tuple[_ResolvedPattern, ...] = ()
            return

        resolved: list[_ResolvedPattern] = []

        for p in _PATTERN_DEFS:
            detector_cfg = pattern_engine.detectors.get(p.detector_key)

            if detector_cfg is None:
                logger.warning(
                    "Prompt injection detector config for key '%s' is missing; "
                    "pattern '%s' will be skipped.",
                    p.detector_key,
                    p.regex.pattern,
                )
                continue

            if not detector_cfg.enabled:
                logger.info(
                    "Prompt injection detector '%s' (key='%s') is disabled; "
                    "pattern '%s' will be skipped.",
                    detector_cfg.id,
                    p.detector_key,
                    p.regex.pattern,
                )
                continue

            resolved.append(
                _ResolvedPattern(
                    type_id=detector_cfg.id,
                    severity=detector_cfg.severity,
                    regex=p.regex,
                    message=p.message,
                )
            )

        if not resolved:
            logger.warning(
                "InjectionPatternDetector initialized with NO active patterns. "
                "Check detection.prompt_injection.engines.pattern.detectors in policy config."
            )

        self._patterns = tuple(resolved)

    def warmup(self) -> None:
        """Warmup hook to ensure patterns are bound."""
        _ = self._patterns

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
                        confidence=1.0,
                    )
                )

        return findings

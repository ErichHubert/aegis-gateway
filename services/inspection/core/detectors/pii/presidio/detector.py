from __future__ import annotations

from typing import Dict, List

from presidio_analyzer import AnalyzerEngine, RecognizerResult

from core.config.loader import load_config
from core.config.models import InspectionConfig, PiiConfig, PiiEntityConfig
from core.detectors.pii.presidio.engine import get_presidio_analyzer
from core.models import Finding
from core.detectors.protocols import IDetector 


_PiiLookup = Dict[str, PiiEntityConfig]


def _build_entity_lookup(entities_cfg: dict[str, PiiEntityConfig]) -> _PiiLookup:
    """Map Presidio entity types to enabled PII configs for fast lookup.

    Keys:   Presidio entity_type (e.g. "EMAIL_ADDRESS")
    Values: PiiEntityConfig for that entity, but only if enabled=True
    """
    return {
        cfg.presidio_type: cfg
        for cfg in entities_cfg.values()
        if cfg.enabled
    }


class PresidioPiiDetector(IDetector):
    """PII detector based on Presidio + spaCy.

    - Reads policy from the YAML config via `load_policy_config()`
    - Uses Presidio's AnalyzerEngine (cached in `get_analyzer()`)
    - Only entities enabled in the policy are considered.
    """

    def __init__(self, analyzer: AnalyzerEngine | None = None) -> None:
        # get_analyzer() should be lru_cached, so this is cheap and
        # the underlying spaCy/Presidio objects are reused across requests.
        self._analyzer: AnalyzerEngine = analyzer or get_presidio_analyzer()

    def detect(self, prompt: str) -> List[Finding]:
        """Detect PII using Presidio with a spaCy backend.

        Severities and enabled entities are driven by the YAML policy.
        """
        if not prompt:
            return []

        policy: InspectionConfig = load_config()
        pii_cfg: PiiConfig = policy.detection.pii

        # Build a mapping from Presidio entity type -> our PiiEntityConfig
        entity_lookup: _PiiLookup = _build_entity_lookup(pii_cfg.entities or {})
        if not entity_lookup:
            # No PII entities are enabled → no findings.
            return []

        results: List[RecognizerResult] = self._analyzer.analyze(
            text=prompt,
            language=pii_cfg.default_lang,
            score_threshold=pii_cfg.default_score_threshold,
        )

        findings: List[Finding] = []

        for result in results:
            cfg: PiiEntityConfig | None = entity_lookup.get(result.entity_type)
            if cfg is None:
                # Presidio entity not enabled in policy
                continue

            # Entity-specific score threshold, or fallback to global default
            threshold: float = (
                cfg.score_threshold
                if cfg.score_threshold is not None
                else pii_cfg.default_score_threshold
            )
            if result.score < threshold:
                continue

            findings.append(
                Finding(
                    type=cfg.id,
                    start=result.start,
                    end=result.end,
                    snippet=prompt[result.start:result.end],
                    message=f"Detected PII entity '{result.entity_type}'.",
                    severity=cfg.severity,
                    confidence=result.score,
                )
            )

        return findings
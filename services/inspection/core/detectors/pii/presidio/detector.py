from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Dict, List

from presidio_analyzer import AnalyzerEngine, RecognizerResult

from core.config.models import InspectionConfig, PiiPresidioDetectorConfig, PiiPresidioEngineConfig
from core.detectors.pii.presidio.engine import get_presidio_analyzer
from core.models import Finding
from core.detectors.protocols import IDetector

logger = logging.getLogger(__name__)


_PiiLookup = Dict[str, PiiPresidioDetectorConfig]


def _build_entity_lookup(detectors_cfg: Mapping[str, PiiPresidioDetectorConfig]) -> _PiiLookup:
    """Map Presidio entity types to enabled PII configs for fast lookup.

    Keys:   Presidio entity_type (e.g. "EMAIL_ADDRESS")
    Values: PiiEntityConfig for that entity, but only if enabled=True
    """
    return {
        cfg.presidio_type: cfg
        for cfg in detectors_cfg.values()
        if cfg.enabled
    }


class PresidioPiiDetector(IDetector):
    """PII detector based on Presidio + spaCy.

    - Reads policy from the YAML config via `load_policy_config()`
    - Uses Presidio's AnalyzerEngine (cached in `get_analyzer()`)
    - Only entities enabled in the policy are considered.
    """

    def __init__(
        self,
        config: InspectionConfig,
        analyzer: AnalyzerEngine | None = None,
    ) -> None:
        # get_analyzer() caches, so this is cheap; reuse underlying spaCy/Presidio objects.
        self._config = config
        self._analyzer: AnalyzerEngine = analyzer or get_presidio_analyzer(config)
        enabled_count = sum(1 for cfg in (config.detection.pii.engines.presidio.detectors or {}).values() if cfg.enabled)
        logger.info("PresidioPiiDetector initialized with %d enabled entities", enabled_count)

    def detect(self, prompt: str) -> List[Finding]:
        """Detect PII using Presidio with a spaCy backend.

        Enabled entities, thresholds and severities are driven by the YAML policy.
        """
        if not prompt:
            logger.debug("PresidioPiiDetector skipping empty prompt")
            return []

        presidio_cfg: PiiPresidioEngineConfig = self._config.detection.pii.engines.presidio

        # Build a mapping from Presidio entity type -> our PiiEntityConfig
        entity_lookup: _PiiLookup = _build_entity_lookup(presidio_cfg.detectors or {})
        if not entity_lookup:
            # No PII entities are enabled -> no findings.
            logger.warning("PresidioPiiDetector has no enabled entities; skipping detection")
            return []

        results: List[RecognizerResult] = self._analyzer.analyze(
            text=prompt,
            language=presidio_cfg.default_lang,
            score_threshold=presidio_cfg.default_score_threshold,
        )

        findings: List[Finding] = []

        for result in results:
            cfg: PiiPresidioDetectorConfig | None = entity_lookup.get(result.entity_type)
            if cfg is None:
                # Presidio entity not enabled in policy
                continue

            # Entity-specific score threshold, or fallback to global default
            threshold: float = (
                cfg.score_threshold
                if cfg.score_threshold is not None
                else presidio_cfg.default_score_threshold
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

        if findings:
            counts: Dict[str, int] = {}
            for finding in findings:
                counts[finding.type] = counts.get(finding.type, 0) + 1
            logger.info(
                "PresidioPiiDetector detected %d finding(s) across %d entity type(s)",
                len(findings),
                len(counts),
            )
        else:
            logger.debug("PresidioPiiDetector found no PII findings")

        return findings

    def warmup(self) -> None:
        pass

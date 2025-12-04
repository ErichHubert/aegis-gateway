from __future__ import annotations

from typing import List

from presidio_analyzer import AnalyzerEngine, RecognizerResult

from core.models import Finding
from core.engines.presidio_engine import get_analyzer
from core.config.loader import load_policy_config
from services.inspection.core.config.models import AegisPolicyConfig, PiiConfig, PiiEntityConfig


def detect_pii(prompt: str) -> List[Finding]:
    """Detect PII using Presidio with a spaCy backend. Severities and enabled entities are driven by the YAML policy via the policy loader."""

    if not prompt:
        return []

    analyzer: AnalyzerEngine = get_analyzer()
    policy: AegisPolicyConfig = load_policy_config()
    pii_cfg: PiiConfig = policy.detection.pii

    results: List[RecognizerResult] = analyzer.analyze(
        text=prompt,
        language=pii_cfg.default_lang,
        score_threshold=pii_cfg.default_score_threshold,
    )

    entities_cfg: dict[str, PiiEntityConfig] = pii_cfg.entities or {}
    presidio_to_entity_cfg: dict[str, PiiEntityConfig]  = {e.presidio_type: e for e in entities_cfg.values()}

    findings: List[Finding] = []

    for r in results:
        cfg: PiiEntityConfig | None = presidio_to_entity_cfg.get(r.entity_type)
        if cfg is None or not cfg.enabled:
            continue

        threshold: float = cfg.score_threshold or pii_cfg.default_score_threshold
        if r.score < threshold:
            continue

        findings.append(
            Finding(
                type=cfg.id,
                start=r.start,
                end=r.end,
                snippet=prompt[r.start:r.end],
                message=f"Detected PII entity '{r.entity_type}'.",
                severity=cfg.severity,
            )
        )

    return findings
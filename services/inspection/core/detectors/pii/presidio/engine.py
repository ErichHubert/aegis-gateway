from __future__ import annotations

from functools import lru_cache

from presidio_analyzer import AnalyzerEngine, EntityRecognizer, PatternRecognizer, RecognizerRegistry
from presidio_analyzer.nlp_engine import NlpEngineProvider, NlpEngine

from core.config.loader import load_config
from core.config.models import InspectionConfig


@lru_cache(maxsize=1)
def get_presidio_analyzer() -> AnalyzerEngine:
    """Create and cache a singleton Presidio AnalyzerEngine.

    - Reads language + model from policy config
    - Uses spaCy as NLP backend
    - Loads Presidio’s predefined recognizers
    """
    config: InspectionConfig = load_config()
    pii_cfg = config.detection.pii

    # Build NLP engine config for spaCy
    nlp_configuration = {
        "nlp_engine_name": "spacy",
        "models": [
            {
                "lang_code": pii_cfg.default_lang,  
                "model_name": pii_cfg.default_spacy_model,   
            }
        ],
    }

    # Create spaCy-based NLP engine via provider
    provider = NlpEngineProvider(nlp_configuration=nlp_configuration)
    nlp_engine: NlpEngine = provider.create_engine()

    registry = RecognizerRegistry()
    registry.load_predefined_recognizers(nlp_engine=nlp_engine)

    for _, entity_cfg in (pii_cfg.entities or {}).items():
        if not entity_cfg.enabled or not entity_cfg.context_words:
            continue

        recognizers: list[EntityRecognizer] = registry.get_recognizers(
            entities = [entity_cfg.presidio_type],
            language=pii_cfg.default_lang,
        )

        if recognizers:
            # enrich existing recognizers
            for r in recognizers:
                existing = set(r.context or [])
                r.context = list(existing | set(entity_cfg.context_words))
        else:
            # create a minimal PatternRecognizer that only adds context
            registry.add_recognizer(
                PatternRecognizer(
                    supported_entity=entity_cfg.presidio_type,
                    supported_language=pii_cfg.default_lang,
                    context=entity_cfg.context_words,
                )
            )

    return AnalyzerEngine(
        nlp_engine=nlp_engine,
        registry=registry,
        supported_languages=[pii_cfg.default_lang],
    )
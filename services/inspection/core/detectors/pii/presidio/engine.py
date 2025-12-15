from __future__ import annotations

from presidio_analyzer import AnalyzerEngine, EntityRecognizer, Pattern, PatternRecognizer, RecognizerRegistry
from presidio_analyzer.nlp_engine import NlpEngineProvider, NlpEngine

from core.config.models import InspectionConfig, PiiPresidioPatternConfig


_ANALYZER: AnalyzerEngine | None = None


def get_presidio_analyzer(config: InspectionConfig) -> AnalyzerEngine:
    """Create and cache a singleton Presidio AnalyzerEngine using the given config.

    - Reads language + model from policy config
    - Uses spaCy as NLP backend
    - Loads Presidio’s predefined recognizers
    """
    global _ANALYZER

    if _ANALYZER is not None:
        return _ANALYZER

    presidio_engine = config.detection.pii.engines.presidio

    # Build NLP engine config for spaCy
    nlp_configuration = {
        "nlp_engine_name": "spacy",
        "models": [
            {
                "lang_code": presidio_engine.default_lang,  
                "model_name": presidio_engine.default_spacy_model,   
            }
        ],
    }

    # Create spaCy-based NLP engine via provider
    provider = NlpEngineProvider(nlp_configuration=nlp_configuration)
    nlp_engine: NlpEngine = provider.create_engine()

    registry = RecognizerRegistry()
    registry.load_predefined_recognizers(nlp_engine=nlp_engine)

    for _, entity_cfg in (presidio_engine.detectors or {}).items():
        if not entity_cfg.enabled or not entity_cfg.context_words:
            continue

        recognizers: list[EntityRecognizer] = registry.get_recognizers(
            entities = [entity_cfg.presidio_type],
            language=presidio_engine.default_lang,
        )

        patterns: list[Pattern] = [
            Pattern(name=p.name, regex=p.regex, score=p.score)
            for p in (entity_cfg.patterns or ())
        ]

        context_words = list(entity_cfg.context_words)

        if recognizers:
            # enrich existing recognizers
            for r in recognizers:
                existing = set(r.context or [])
                r.context = list(existing | set(context_words))
            # add dedicated pattern recognizer if custom patterns are present
            if patterns:
                registry.add_recognizer(
                    PatternRecognizer(
                        supported_entity=entity_cfg.presidio_type,
                        supported_language=presidio_engine.default_lang,
                        patterns=patterns,
                        context=context_words,
                    )
                )
        else:
            # create a minimal PatternRecognizer that only adds context
            if patterns or context_words:
                registry.add_recognizer(
                    PatternRecognizer(
                        supported_entity=entity_cfg.presidio_type,
                        supported_language=presidio_engine.default_lang,
                        patterns=patterns,
                        context=context_words,
                    )
                )

    return AnalyzerEngine(
        nlp_engine=nlp_engine,
        registry=registry,
        supported_languages=[presidio_engine.default_lang],
    )


def warmup_analyzer(config: InspectionConfig) -> None:
    """Helper to explicitly build the cached analyzer during warmup."""
    get_presidio_analyzer(config)

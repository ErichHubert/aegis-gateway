from functools import lru_cache

from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_analyzer.nlp_engine import NlpEngineProvider

from infra.config import settings


@lru_cache(maxsize=1)
def get_analyzer() -> AnalyzerEngine:
    """Create and cache a singleton Presidio AnalyzerEngine."""

    # Build NLP engine config for spaCy
    nlp_configuration = {
        "nlp_engine_name": "spacy",
        "models": [
            {
                "lang_code": settings.detection.pii_default_lang,  
                "model_name": settings.detection.pii_spacy_model,   
            }
        ],
    }

    # Create spaCy-based NLP engine via provider
    provider = NlpEngineProvider(nlp_configuration=nlp_configuration)
    nlp_engine = provider.create_engine()

    # Load built-in recognizers
    registry = RecognizerRegistry()
    registry.load_predefined_recognizers(nlp_engine=nlp_engine)

    # Build analyzer
    analyzer = AnalyzerEngine(
        nlp_engine=nlp_engine,
        registry=registry,
        supported_languages=[settings.detection.pii_default_lang],
    )

    return analyzer
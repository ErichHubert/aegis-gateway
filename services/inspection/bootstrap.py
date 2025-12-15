from __future__ import annotations

import logging
import os

from core.config.loader import load_config
from core.detectors.injection.pattern.detector import InjectionPatternDetector
from core.detectors.pii.presidio.detector import PresidioPiiDetector
from core.detectors.pii.presidio.engine import warmup_analyzer
from core.detectors.protocols import IDetector
from core.detectors.secret.detectsecret.detector import DetectSecretsDetector

logger = logging.getLogger(__name__)


WARMUP_OK = False
WARMUP_ERRORS: list[str] = []


def initialize_pipeline() -> tuple[IDetector, ...]:
    """
    Load config and prime heavy dependencies before the app starts serving.

    - load_config() validates config.yml and caches it
    - warmup_analyzer() builds the Presidio analyzer (spaCy load)
    - detector instances build their rule maps / patterns

    Any exception is allowed to bubble up so startup fails fast.
    """
    global WARMUP_OK, WARMUP_ERRORS
    cfg_path = os.getenv("INSPECTION_CONFIG_PATH")

    try:
        logger.info("Initialization: loading inspection config (path=%s)", cfg_path or "default bundled config")
        config = load_config(cfg_path)

        logger.info("Initialization: initializing Presidio analyzer")
        warmup_analyzer(config)

        detector_pipeline: tuple[IDetector, ...] = (
            DetectSecretsDetector(config),
            PresidioPiiDetector(config),
            InjectionPatternDetector(config),
        )

        for detector in detector_pipeline:
            detector.warmup()

        WARMUP_OK = True
        logger.info("Initialization: completed successfully")
        return detector_pipeline
    except Exception as exc:  # bubble up to fail startup
        WARMUP_ERRORS.append(str(exc))
        logger.exception("Initialization failed: %s", exc)
        raise

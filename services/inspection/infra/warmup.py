from __future__ import annotations

import logging
import os
from core.config.loader import load_config
from core.detectors.injection.pattern.detector import InjectionPatternDetector
from core.detectors.pii.presidio.engine import warmup_analyzer
from core.detectors.secret.detectsecret.detector import DetectSecretsDetector
from core.detectors.secret.regex.detector import SecretRegexDetector
from infra.warmable import Warmable

logger = logging.getLogger(__name__)


WARMUP_OK = False
WARMUP_ERRORS: list[str] = []


def run_warmup() -> None:
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
        logger.info("Warmup: loading inspection config (path=%s)", cfg_path or "default bundled config")
        load_config(cfg_path)

        logger.info("Warmup: initializing Presidio analyzer")
        warmup_analyzer()

        warmables: list[Warmable] = [
            SecretRegexDetector(),
            DetectSecretsDetector(),
            InjectionPatternDetector(),
        ]

        for component in warmables:
            component.warmup()

        WARMUP_OK = True
        logger.info("Warmup: completed successfully")
    except Exception as exc:  # bubble up to fail startup
        WARMUP_ERRORS.append(str(exc))
        logger.exception("Warmup failed: %s", exc)
        raise

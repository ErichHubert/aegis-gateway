from __future__ import annotations

from typing import Any, Literal, Optional
from collections.abc import Mapping
from types import MappingProxyType

from pydantic import BaseModel, ConfigDict, Field, model_validator

SeverityLevel = Literal["low", "medium", "high"]


def _deep_freeze(value: Any) -> Any:
    """Recursively freeze nested dict/list structures.

    - dict-like objects become MappingProxyType (read-only mapping)
    - lists/tuples become tuples

    This gives us practical deep immutability for config objects.
    """
    if isinstance(value, Mapping):
        return MappingProxyType({k: _deep_freeze(v) for k, v in value.items()})

    if isinstance(value, (list, tuple)):
        return tuple(_deep_freeze(v) for v in value)

    return value


class FrozenModel(BaseModel):
    """Base class for immutable config models.

    Notes:
    - `frozen=True` prevents attribute reassignment.
    - `_deep_freeze` also makes nested mappings/sequences read-only.
    - `extra="forbid"` prevents typos in YAML/JSON from being silently accepted.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def _freeze_nested(cls, data: Any) -> Any:
        if data is None:
            return data
        return _deep_freeze(data)


# ---------- Base Models ----------

class EngineBase(FrozenModel):
    """Base configuration for a detection engine (regex, Presidio, ...)."""
    enabled: bool = True  # enable/disable entire engine


class DetectorBase(FrozenModel):
    """Base configuration for a single detector/rule inside an engine."""
    id: str                                   # logical id -> Finding.type
    display_name: Optional[str] = None       # optional human-readable name
    enabled: bool = True                     # enable/disable this rule
    severity: SeverityLevel                  # how serious a hit is


# ---------- Secrets ----------
FilterMode = Literal["blacklist", "whitelist"]

class SecretsRegexEngineConfig(EngineBase):
    """Configuration for the regex-based secrets engine."""
    detectors: Mapping[str, DetectorBase]


class SecretDetectSecretDetectorConfig(DetectorBase):
    """Configuration for a single detect-secrets plugin."""
    plugin_name: str
    plugin_type: str
    

class DetectSecretsFiltersConfig(FrozenModel):
    disable: tuple[str, ...] = Field(default_factory=tuple)


class SecretDetectSecretEngineConfig(EngineBase):
    """Configuration for the detect-secrets engine."""
    detectors: Mapping[str, SecretDetectSecretDetectorConfig]
    filters: DetectSecretsFiltersConfig = Field(default_factory=DetectSecretsFiltersConfig)


class SecretEnginesConfig(FrozenModel):
    """Container for all secret-detection engines (regex, ml, ...)."""
    regex: SecretsRegexEngineConfig
    detect_secrets: SecretDetectSecretEngineConfig


class SecretsConfig(FrozenModel):
    engines: SecretEnginesConfig



# ---------- PII ----------

class PiiPresidioDetectorConfig(DetectorBase):
    """Configuration for a single Presidio-backed PII type."""
    presidio_type: str                       # e.g. EMAIL_ADDRESS
    score_threshold: Optional[float] = None  # fallback: engine default_score_threshold
    context_words: tuple[str, ...] = Field(default_factory=tuple)


class PiiPresidioEngineConfig(EngineBase):
    """Configuration for the Presidio NLP engine used for PII."""
    default_lang: str                        # e.g. "en"
    default_spacy_model: str                 # e.g. "en_core_web_lg"
    default_score_threshold: float           # global default threshold
    detectors: Mapping[str, PiiPresidioDetectorConfig]  # email/phone/iban/...


class PiiEnginesConfig(FrozenModel):
    """Container for all PII engines."""
    presidio: PiiPresidioEngineConfig        # später evtl. andere Engines


class PiiConfig(FrozenModel):
    engines: PiiEnginesConfig


# ---------- Prompt Injection ----------

class PromptInjectionPatternEngineConfig(EngineBase):
    """Configuration for the pattern-based prompt-injection engine."""
    detectors: Mapping[str, DetectorBase]       


class PromptInjectionEnginesConfig(FrozenModel):
    """Container for all prompt-injection engines."""
    pattern: PromptInjectionPatternEngineConfig


class PromptInjectionConfig(FrozenModel):
    engines: PromptInjectionEnginesConfig


# ---------- Top-Level Detection & Policy ----------

class DetectionConfig(FrozenModel):
    secrets: SecretsConfig
    pii: PiiConfig
    prompt_injection: PromptInjectionConfig


class InspectionConfig(FrozenModel):
    detection: DetectionConfig
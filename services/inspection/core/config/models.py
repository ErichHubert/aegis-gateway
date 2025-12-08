from __future__ import annotations

from typing import Dict, Literal, Optional
from pydantic import BaseModel, Field

SeverityLevel = Literal["low", "medium", "high"]


# ---------- Base Models ----------

class EngineBase(BaseModel):
    """Base configuration for a detection engine (regex, Presidio, ...)."""
    enabled: bool = True  # enable/disable entire engine


class DetectorBase(BaseModel):
    """Base configuration for a single detector/rule inside an engine."""
    id: str                                   # logical id -> Finding.type
    display_name: Optional[str] = None       # optional human-readable name
    enabled: bool = True                     # enable/disable this rule
    severity: SeverityLevel                  # how serious a hit is


# ---------- Secrets ----------

class SecretsRegexEngineConfig(EngineBase):
    """Configuration for the regex-based secrets engine."""
    detectors: Dict[str, DetectorBase]       # e.g. aws_access_key, generic_token, ...


class SecretEnginesConfig(BaseModel):
    """Container for all secret-detection engines (regex, ml, ...)."""
    regex: SecretsRegexEngineConfig          # later: ml: SecretsMlEngineConfig, ...


class SecretsConfig(BaseModel):
    engines: SecretEnginesConfig


# ---------- PII ----------

class PiiPresidioDetectorConfig(DetectorBase):
    """Configuration for a single Presidio-backed PII type."""
    presidio_type: str                       # e.g. EMAIL_ADDRESS
    score_threshold: Optional[float] = None  # fallback: engine default_score_threshold
    context_words: list[str] = Field(default_factory=list)


class PiiPresidioEngineConfig(EngineBase):
    """Configuration for the Presidio NLP engine used for PII."""
    default_lang: str                        # e.g. "en"
    default_spacy_model: str                 # e.g. "en_core_web_lg"
    default_score_threshold: float           # global default threshold
    detectors: Dict[str, PiiPresidioDetectorConfig]  # email/phone/iban/...


class PiiEnginesConfig(BaseModel):
    """Container for all PII engines."""
    presidio: PiiPresidioEngineConfig        # später evtl. andere Engines


class PiiConfig(BaseModel):
    engines: PiiEnginesConfig


# ---------- Prompt Injection ----------

class PromptInjectionPatternEngineConfig(EngineBase):
    """Configuration for the pattern-based prompt-injection engine."""
    detectors: Dict[str, DetectorBase]       # generic/override/suspicious


class PromptInjectionEnginesConfig(BaseModel):
    """Container for all prompt-injection engines."""
    pattern: PromptInjectionPatternEngineConfig


class PromptInjectionConfig(BaseModel):
    engines: PromptInjectionEnginesConfig


# ---------- Top-Level Detection & Policy ----------

class DetectionConfig(BaseModel):
    secrets: SecretsConfig
    pii: PiiConfig
    prompt_injection: PromptInjectionConfig


class InspectionConfig(BaseModel):
    detection: DetectionConfig
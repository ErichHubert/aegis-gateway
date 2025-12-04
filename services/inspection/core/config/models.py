from __future__ import annotations

from typing import Dict, Literal, Optional
from pydantic import BaseModel, Field

SeverityLevel = Literal["low", "medium", "high"]
ActionOverride = Literal["block", "warn", "allow"]


# ---------- Secrets ----------

class SecretRule(BaseModel):
    id: str                                   # REQUIRED
    display_name: Optional[str] = None        # OPTIONAL
    enabled: bool = True                      # OPTIONAL, default: true
    severity: SeverityLevel                   # REQUIRED


class SecretsConfig(BaseModel):
    aws_access_key: SecretRule
    generic_token: SecretRule
    jwt: SecretRule
    pem_block: SecretRule


# ---------- PII ----------

class PiiEntityConfig(BaseModel):
    id: str                                   # REQUIRED
    presidio_type: str                        # REQUIRED
    enabled: bool = True                      # OPTIONAL, default: true
    severity: SeverityLevel                   # REQUIRED
    score_threshold: Optional[float] = None   # OPTIONAL (fallback: default_score_threshold)
    context_words: list[str] = Field(default_factory=list)
    action_override: Optional[ActionOverride] = None  # OPTIONAL


class PiiConfig(BaseModel):
    default_lang: str                         # REQUIRED
    default_spacy_model: str                  # REQUIRED
    default_score_threshold: float            # REQUIRED
    entities: Dict[str, PiiEntityConfig]      # email/phone/iban/... as keys


# ---------- Prompt Injection ----------

class PromptInjectionRule(BaseModel):
    id: str                                   # REQUIRED
    enabled: bool = True                      # OPTIONAL, default: true
    severity: SeverityLevel                   # REQUIRED


class PromptInjectionConfig(BaseModel):
    generic: PromptInjectionRule
    override: PromptInjectionRule
    suspicious: PromptInjectionRule


# ---------- Top-Level Detection & Policy ----------

class DetectionConfig(BaseModel):
    secrets: SecretsConfig
    pii: PiiConfig
    prompt_injection: PromptInjectionConfig


class InspectionConfig(BaseModel):
    detection: DetectionConfig
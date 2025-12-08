from __future__ import annotations

from typing import Dict, Literal, Optional
from pydantic import BaseModel, Field

SeverityLevel = Literal["low", "medium", "high"]


# ---------- Base Modesl ----------

class EngineBase(BaseModel):
    enabled: bool = True                     

class DetectorBase(BaseModel):
    id: str                                   
    display_name: Optional[str] = None        
    enabled: bool = True                      
    severity: SeverityLevel                   


# ---------- Secrets ----------

class SecretsRegexEngineConfig(EngineBase):
    detectors: Dict[str, DetectorBase]

class SecretEnginesConfig(EngineBase):
    regex: SecretsRegexEngineConfig

class SecretsConfig(BaseModel):
    engines: SecretEnginesConfig


# ---------- PII ----------

class PiiPresidioDetectorConfig(DetectorBase):
    presidio_type: str                        
    score_threshold: Optional[float] = None   
    context_words: list[str] = Field(default_factory=list)


class PiiPresidioEngineConfig(EngineBase):
    default_lang: str                               
    default_spacy_model: str                        
    default_score_threshold: float                  
    detectors: Dict[str, PiiPresidioDetectorConfig]    


class PiiEnginesConfig(BaseModel):
    presidio: PiiPresidioEngineConfig


class PiiConfig(BaseModel):
    engines: PiiEnginesConfig


# ---------- Prompt Injection ----------

class PromptInjectionPatternEngineConfig(EngineBase):
    detectors: Dict[str, DetectorBase]

class PromptInjectionEnginesConfig(EngineBase):
    regex: PromptInjectionPatternEngineConfig

class PromptInjectionConfig(BaseModel):
    engines: PromptInjectionEnginesConfig


# ---------- Top-Level Detection & Policy ----------

class DetectionConfig(BaseModel):
    secrets: SecretsConfig
    pii: PiiConfig
    prompt_injection: PromptInjectionConfig


class InspectionConfig(BaseModel):
    detection: DetectionConfig
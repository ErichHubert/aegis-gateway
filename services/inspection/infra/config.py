from __future__ import annotations

from typing import Dict, Literal, List

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Severity levels the service understands
SeverityLevel = Literal["low", "medium", "high"]


class PiiContextSettings(BaseModel):
    """Context-word configuration for PII entities.

    Keys are Presidio entity types (e.g. 'EMAIL_ADDRESS', 'IBAN_CODE'),
    values are lists of context words that boost detection confidence.
    """

    enabled: bool = True

    # Map Presidio entity type -> list of context words
    words: Dict[str, List[str]] = Field(
        default_factory=lambda: {
            # Built-in Presidio entities
            "EMAIL_ADDRESS": ["email", "e-mail", "mail", "kontakt"],
            "PHONE_NUMBER": ["phone", "telefon", "tel", "nummer"],
            "IBAN_CODE": ["iban", "konto", "account", "bank"],
            "CREDIT_CARD": ["credit", "karte", "visa", "mastercard"],
            # Beispiel für spätere Custom-Entities
            # "EMPLOYEE_ID": ["employee", "mitarbeiter", "personalnummer"],
        }
    )


class DetectionSettings(BaseModel):
    """Settings for detection behavior (e.g. severity per finding type and PII mapping)."""

    # Central mapping: internal finding type -> severity
    # These keys should match Finding.type (e.g. "pii_email").
    severity_by_type: Dict[str, SeverityLevel] = Field(
        default_factory=lambda: {
            # secrets
            "secret_aws_access_key": "high",
            "secret_generic_token": "high",
            "secret_jwt": "high",
            "secret_pem_block": "high",
            # PII (internal canonical types)
            "pii_email": "medium",
            "pii_phone": "medium",
            "pii_iban": "high",
            # prompt injection
            "prompt_injection_override": "high",
            "prompt_injection_suspicious": "medium",
        }
    )

    # Default severity used when a finding type is not explicitly listed above
    pii_default_severity: SeverityLevel = "medium"

    # Map Presidio entity types -> internal canonical types used in severity_by_type
    # Example: Presidio "EMAIL_ADDRESS" -> internal "pii_email"
    pii_type_map: Dict[str, str] = Field(
        default_factory=lambda: {
            "EMAIL_ADDRESS": "pii_email",
            "PHONE_NUMBER": "pii_phone",
            "IBAN_CODE": "pii_iban",
        }
    )

    # PII / Presidio related
    pii_default_lang: str = "en"
    pii_spacy_model: str = "en_core_web_lg"
    pii_score_threshold: float = 0.35

    # NEW: context-aware PII tuning
    pii_context: PiiContextSettings = PiiContextSettings()


class PolicySettings(BaseModel):
    """High-level policy knobs controlling allow/block decisions."""

    # All findings with severity >= block_severity will block the request.
    block_severity: SeverityLevel = "high"


class Settings(BaseSettings):
    """Central configuration for the ML service."""

    app_name: str = "Aegis ML Inspection Service"
    app_desc: str = """
            Aegis ML Inspection Service

            Inspects LLM prompts for:
            - secrets (API keys, tokens)
            - PII (emails, phone numbers, etc.)
            - prompt injection indicators

            Designed to be called from the Aegis Gateway.
            """
    app_version: str = "0.1.0"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"
    log_level: str = "INFO"

    detection: DetectionSettings = DetectionSettings()
    policy: PolicySettings = PolicySettings()

    model_config = SettingsConfigDict(
        env_prefix="AEGIS_INSPECTION_",
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
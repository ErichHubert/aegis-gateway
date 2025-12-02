from __future__ import annotations

from typing import Dict, Literal

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Severity levels the service understands
SeverityLevel = Literal["low", "medium", "high"]


class DetectionSettings(BaseModel):
    """Settings for detection behavior (e.g. severity per finding type)."""

    severity_by_type: Dict[str, SeverityLevel] = Field(
        default_factory=lambda: {
            # secrets
            "secret_aws_access_key": "high",
            "secret_generic_token": "high",
            "secret_jwt": "high",
            "secret_pem_block": "high",
            # PII
            "pii_email": "medium",
            "pii_phone": "medium",
            "pii_iban": "high",
            # prompt injection
            "prompt_injection_override": "high",
            "prompt_injection_suspicious": "medium",
        }
    )


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
        env_prefix="AEGIS_ML_",
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
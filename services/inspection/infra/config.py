from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


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

    # Later:
    # enable_pii_ml: bool = False
    # enable_injection_ml: bool = False

    model_config = SettingsConfigDict(
        env_prefix="AEGIS_ML_",
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
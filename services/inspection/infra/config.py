from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for the ML service.

    Primary source: environment variables.
    """
    app_name: str = "Aegis ML Inspection Service"
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
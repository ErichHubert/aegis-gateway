from __future__ import annotations

from typing import Iterable, List
from dataclasses import dataclass

from detect_secrets.core.secrets_collection import SecretsCollection
from detect_secrets.core.scan import scan_line
from detect_secrets.settings import transient_settings

from core.detectors.protocols import ISecretDetector
from core.models import Finding
from core.config.models import SecretDetectSecretEngineConfig  
from core.config.loader import load_config


@dataclass(frozen=True)
class _SecretRuleRuntime:
    id: str           # internal type, e.g. "secret_aws_access_key"
    severity: str     # "high" | "medium" | "low"
    plugin_type: str  # e.g. "AWSKeyDetector"
    plugin_name: str  


def _build_runtime_rules(engine_cfg: SecretDetectSecretEngineConfig) -> tuple[dict[str, _SecretRuleRuntime], dict]:
    """
    Build:
      - lookup by plugin name -> rule
      - detect-secrets settings dict for transient_settings()
    """
    rules_by_plugin: dict[str, _SecretRuleRuntime] = {}
    plugins_used: list[dict] = []

    for cfg in engine_cfg.detectors.values():
        if not cfg.enabled:
            continue

        rule = _SecretRuleRuntime(
            id=cfg.id,
            severity=cfg.severity,
            plugin_type=cfg.plugin_type,
            plugin_name=cfg.plugin_name,
        )
        
        # Map by plugin_type for lookups when scanning
        rules_by_plugin[rule.plugin_type] = rule

        # Register plugin by class name for detect-secrets config
        plugins_used.append({"name": rule.plugin_name})

    settings = {"plugins_used": plugins_used}
    return rules_by_plugin, settings


class DetectSecretsDetector(ISecretDetector):
    """
    Adapter around `detect-secrets` to scan a single prompt string.

    - Uses config-driven rules (SecretDetectSecretEngineConfig)
    - Maps detect-secrets plugin outputs to internal Finding objects
    """

    def __init__(self, engine_cfg: SecretDetectSecretEngineConfig | None = None) -> None:
        if engine_cfg is None:
            cfg = load_config()
            engine_cfg = cfg.detection.secrets.engines.detect_secrets

        self._rules_by_plugin, self._settings = _build_runtime_rules(engine_cfg)

    def detect(self, prompt: str) -> List[Finding]:
        """Run detect-secrets on the given prompt and return mapped findings."""
        if not prompt:
            return []

        findings: List[Finding] = []

        # Apply detect-secrets settings only for this call
        with transient_settings(self._settings):
            secrets_iter = scan_line(line=prompt)

            for secret in secrets_iter:
                plugin_type = secret.type  # e.g. "AWSKeyDetector"

                rule = self._rules_by_plugin.get(plugin_type)
                if rule is None:
                    continue

                # Best effort: try to get the actual secret string
                secret_value = getattr(secret, "secret_value", None)

                start = 0
                end = len(prompt)

                if secret_value:
                    idx = prompt.find(secret_value)
                    if idx != -1:
                        start = idx
                        end = idx + len(secret_value)

                findings.append(
                    Finding(
                        type=rule.id,
                        start=start,
                        end=end,
                        snippet="***""",
                        message=f"Secret detected by {plugin_type}",
                        severity=rule.severity,
                        confidence=1.0, 
                    )
                )

        return findings
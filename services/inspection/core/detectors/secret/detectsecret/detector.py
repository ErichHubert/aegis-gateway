from __future__ import annotations

from typing import List, Tuple, Dict, Any
from dataclasses import dataclass
from threading import Lock

from detect_secrets.core.scan import scan_line
from detect_secrets.settings import transient_settings

from core.detectors.protocols import ISecretDetector
from core.models import Finding
from core.config.models import InspectionConfig, SecretDetectSecretEngineConfig  


@dataclass(frozen=True)
class _SecretRuleRuntime:
    id: str           # internal type, e.g. "secret_aws_access_key"
    severity: str     # "high" | "medium" | "low"
    plugin_type: str  # e.g. "AWSKeyDetector"
    plugin_name: str  


# detect-secrets mutates global settings; guard with a process-wide lock
_DETECT_SECRETS_GLOBAL_LOCK = Lock()


def _build_runtime_rules(
    engine_cfg: SecretDetectSecretEngineConfig,
) -> Tuple[Dict[str, _SecretRuleRuntime], Dict[str, Any], Tuple[str, ...]]:
    """Build runtime lookup tables for detect-secrets.

    Returns:
      - rules_by_plugin: lookup by plugin type (e.g. "AWSKeyDetector") -> rule
      - settings: detect-secrets settings dict for `transient_settings()`
      - disabled_filters: fully-qualified filter paths to disable via `settings.disable_filters()`

    Notes:
      - We keep detect-secrets default heuristic filters enabled by default.
      - You can optionally disable specific default filters via config (blacklist-style).
      - This function remains backward compatible with an older nested config shape:
        `engine_cfg.filters.disable: ["detect_secrets.filters...", ...]`.
    """
    rules_by_plugin: Dict[str, _SecretRuleRuntime] = {}
    plugins_used: List[Dict[str, Any]] = []
    filters_disabled: Tuple[str, ...] = ()

    for cfg in engine_cfg.detectors.values():
        if not cfg.enabled:
            continue

        rule = _SecretRuleRuntime(
            id=cfg.id,
            severity=cfg.severity,
            plugin_type=cfg.plugin_type,
            plugin_name=cfg.plugin_name,
        )

        if rule.plugin_type in rules_by_plugin:
            raise ValueError(
                f"Duplicate detect-secrets plugin_type configured: '{rule.plugin_type}'. "
                "Each enabled rule must have a unique plugin_type."
            )

        # Map by plugin_type for lookups when scanning
        rules_by_plugin[rule.plugin_type] = rule

        # Register plugin by class name for detect-secrets config
        plugins_used.append({"name": rule.plugin_name})

    settings: Dict[str, Any] = {"plugins_used": plugins_used}
    filters_cfg = getattr(engine_cfg, "filters", None)

    if filters_cfg is not None:
        filters_disabled = tuple(getattr(filters_cfg, "disable", ()) or ())

    return rules_by_plugin, settings, filters_disabled


class DetectSecretsDetector(ISecretDetector):
    """
    Adapter around `detect-secrets` to scan a single prompt string.

    - Uses config-driven rules (SecretDetectSecretEngineConfig)
    - Maps detect-secrets plugin outputs to internal Finding objects
    - Thread-safe: guarded by a process-wide lock because detect-secrets settings are global.
    """

    def __init__(self, config: InspectionConfig) -> None:
        engine_cfg = config.detection.secrets.engines.detect_secrets

        self._rules_by_plugin, self._settings, self._disabled_filters = _build_runtime_rules(engine_cfg)

    def warmup(self) -> None:
        """Warmup hook to ensure rules are built."""
        _ = self._rules_by_plugin

    def detect(self, prompt: str) -> List[Finding]:
        """Run detect-secrets on the given prompt and return mapped findings."""
        if not prompt:
            return []

        findings: List[Finding] = []

        # Apply detect-secrets settings only for this call; guard with a process-wide lock
        # because detect-secrets mutates global settings.
        with _DETECT_SECRETS_GLOBAL_LOCK:
            with transient_settings(self._settings) as settings:
                # Disable only the configured filters (blacklist-style).
                # Note: detect-secrets mutates global settings, so this must remain inside
                # the transient_settings scope and guarded by the global lock.
                if self._disabled_filters:
                    settings.disable_filters(*self._disabled_filters)

                # scan_line() is line-oriented; scan per line and keep accurate offsets
                offset = 0
                for raw_line in prompt.splitlines(keepends=True):
                    # Preserve offsets including newline characters
                    line_for_scan = raw_line.rstrip("\r\n")

                    secrets_iter = scan_line(line=line_for_scan)
                    for secret in secrets_iter:
                        plugin_type = secret.type  # e.g. "AWSKeyDetector"

                        rule = self._rules_by_plugin.get(plugin_type)
                        if rule is None:
                            continue

                        # Best effort: try to locate the detected secret value inside the line
                        secret_value = getattr(secret, "secret_value", None)

                        if secret_value:
                            idx = line_for_scan.find(secret_value)
                            if idx != -1:
                                start = offset + idx
                                end = start + len(secret_value)
                            else:
                                # fallback: mark the whole line (but not the whole prompt)
                                start = offset
                                end = offset + len(line_for_scan)
                        else:
                            # fallback: mark the whole line (but not the whole prompt)
                            start = offset
                            end = offset + len(line_for_scan)

                        findings.append(
                            Finding(
                                type=rule.id,
                                start=start,
                                end=end,
                                snippet="***",
                                message=f"Secret detected: {plugin_type}",
                                severity=rule.severity,
                                confidence=1.0,
                            )
                        )

                    offset += len(raw_line)

        return findings

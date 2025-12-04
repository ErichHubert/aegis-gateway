from __future__ import annotations

import pathlib
from functools import lru_cache
from typing import Any

import yaml
from pydantic import ValidationError
from yaml import YAMLError

from core.config.models import AegisPolicyConfig

DEFAULT_POLICY_FILENAME = "policy.yml"
DEFAULT_POLICY_PATH = pathlib.Path(__file__).with_name(DEFAULT_POLICY_FILENAME)


class PolicyConfigError(RuntimeError):
    """Raised when the policy config cannot be loaded or validated."""


def load_policy_config(path: str | pathlib.Path | None = None) -> AegisPolicyConfig:
    """
    Load and validate the Aegis inspection policy from a YAML file.

    - Defaults to the bundled policy.yml in this package.
    - Falls back to the module directory when a relative path is given.
    - Cached per resolved path so the config is parsed once per process.
    """
    resolved_path: pathlib.Path = _resolve_policy_path(path)
    return _load_cached_policy(str(resolved_path.resolve()))


def _resolve_policy_path(path: str | pathlib.Path | None) -> pathlib.Path:
    """Resolve the policy file path, preferring the caller-provided path."""
    candidates: list[pathlib.Path]

    if path is None:
        candidates = [DEFAULT_POLICY_PATH]
    else:
        provided = pathlib.Path(path).expanduser()
        candidates = [provided]
        if not provided.is_absolute():
            candidates.append(DEFAULT_POLICY_PATH.parent / provided)

    for candidate in candidates:
        if candidate.exists():
            return candidate

    tried: str = ", ".join(str(c.resolve()) for c in candidates)
    raise FileNotFoundError(f"Policy config file not found. Looked for: {tried}")


@lru_cache(maxsize=32)
def _load_cached_policy(resolved_path: str) -> AegisPolicyConfig:
    path = pathlib.Path(resolved_path)
    try:
        raw: dict[str,Any] = _read_policy_yaml(path)
        return AegisPolicyConfig.model_validate(raw)
    except ValidationError as exc:
        raise PolicyConfigError(f"Policy config validation failed for {path}") from exc


def _read_policy_yaml(path: pathlib.Path) -> dict[str, Any]:
    """Read and parse YAML from disk with helpful error messages."""
    if not path.is_file():
        raise FileNotFoundError(f"Policy config file not found at {path}")

    try:
        with path.open("r", encoding="utf-8") as f:
            data: Any = yaml.safe_load(f)
    except YAMLError as exc:
        raise PolicyConfigError(f"Invalid YAML in {path}: {exc}") from exc

    if data is None:
        raise PolicyConfigError(f"Policy config at {path} is empty")
    if not isinstance(data, dict):
        raise PolicyConfigError(
            f"Policy config at {path} must be a YAML mapping, got {type(data).__name__}"
        )

    return data

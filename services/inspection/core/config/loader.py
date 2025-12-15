from __future__ import annotations

import pathlib
from functools import lru_cache
from typing import Any, TYPE_CHECKING

import yaml
from pydantic import ValidationError
from yaml import YAMLError

if TYPE_CHECKING:
    from core.config.models import InspectionConfig

DEFAULT_POLICY_FILENAME = "config.yml"
DEFAULT_POLICY_PATH = pathlib.Path(__file__).with_name(DEFAULT_POLICY_FILENAME)


class ConfigError(RuntimeError):
    """Raised when the config cannot be loaded or validated."""


def load_config(path: str | pathlib.Path | None = None) -> "InspectionConfig":
    """
    Load and validate the Aegis inspection config from a YAML file.

    - Defaults to the bundled policy.yml in this package.
    - Falls back to the module directory when a relative path is given.
    - Cached per resolved path so the config is parsed once per process.
    """
    resolved_path: pathlib.Path = _resolve_config_path(path)
    return _load_cached_config(str(resolved_path.resolve()))


def _resolve_config_path(path: str | pathlib.Path | None) -> pathlib.Path:
    """Resolve the condig file path, preferring the caller-provided path."""
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
    raise FileNotFoundError(f"Config file not found. Looked for: {tried}")


@lru_cache(maxsize=1)
def _load_cached_config(resolved_path: str) -> "InspectionConfig":
    from core.config.models import InspectionConfig

    path = pathlib.Path(resolved_path)
    try:
        raw: dict[str, Any] = _read_config_yaml(path)
        return InspectionConfig.model_validate(raw)
    except ValidationError as exc:
        raise ConfigError(f"Config validation failed for {path}") from exc


def _read_config_yaml(path: pathlib.Path) -> dict[str, Any]:
    """Read and parse YAML from disk with helpful error messages."""
    if not path.is_file():
        raise FileNotFoundError(f"Config file not found at {path}")

    try:
        with path.open("r", encoding="utf-8") as f:
            data: Any = yaml.safe_load(f)
    except YAMLError as exc:
        raise ConfigError(f"Invalid YAML in {path}: {exc}") from exc

    if data is None:
        raise ConfigError(f"Config at {path} is empty")
    if not isinstance(data, dict):
        raise ConfigError(
            f"Config at {path} must be a YAML mapping, got {type(data).__name__}"
        )

    return data

import pathlib
import yaml  # add to requirements: pyyaml~=6.0
from functools import lru_cache

from core.config.models import AegisPolicyConfig


@lru_cache(maxsize=1)
def load_policy_config(path: str | pathlib.Path = "policy.yaml") -> AegisPolicyConfig:
    """
    Load and validate the Aegis inspection policy from a YAML file.

    - Fails fast on invalid or missing fields (Pydantic validation).
    - Cached via lru_cache so it's only parsed once per process.
    """
    p = pathlib.Path(path)
    with p.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    return AegisPolicyConfig.model_validate(raw)
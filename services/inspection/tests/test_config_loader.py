from __future__ import annotations

import pathlib

import pytest

from core.config.loader import (
    DEFAULT_POLICY_PATH,
    PolicyConfigError,
    load_policy_config,
)


def test_load_policy_config_defaults_to_bundled_file():
    cfg = load_policy_config()

    assert cfg.policy.block_severity == "high"
    assert "email" in cfg.detection.pii.entities


def test_load_policy_config_raises_for_missing_file(tmp_path: pathlib.Path):
    missing_path = tmp_path / "missing.yml"

    with pytest.raises(FileNotFoundError):
        load_policy_config(missing_path)


def test_load_policy_config_raises_for_bad_yaml(tmp_path: pathlib.Path):
    bad_yaml = tmp_path / "bad.yml"
    bad_yaml.write_text("::: not yaml :::", encoding="utf-8")

    with pytest.raises(PolicyConfigError):
        load_policy_config(bad_yaml)


def test_load_policy_config_caches_by_path(tmp_path: pathlib.Path):
    first = load_policy_config()
    second = load_policy_config()

    assert first is second  # cached for same resolved path

    copy_path = tmp_path / "copy.yml"
    copy_path.write_text(DEFAULT_POLICY_PATH.read_text(encoding="utf-8"), encoding="utf-8")

    copy_config = load_policy_config(copy_path)
    assert copy_config is not first  # different cache entry

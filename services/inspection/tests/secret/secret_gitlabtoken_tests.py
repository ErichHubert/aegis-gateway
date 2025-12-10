# Test payloads adapted from detect-secrets AWSKeyDetector tests
# (https://github.com/Yelp/detect-secrets), licensed under Apache-2.0.

import pytest

from core.models import PromptInspectionRequest
from core.rules import analyze_prompt

def _get_finding(findings, type_id: str):
    """Return first finding with matching type_id or None."""
    return next((f for f in findings if f.type == type_id), None)


@pytest.mark.parametrize(
    'secret, should_flag',
    [
        (
            # valid PAT prefix and token length
            'glpat-hellOworld380_testin',
            True,
        ),
        (
            # spaces are not part of the token
            'glpat-hellOWorld380 testin',
            False,
        ),
        (
            # invalid separator (underscore VS dash)
            'glpat_hellOworld380_testin',
            False,
        ),
        (
            # valid different prefix and token length
            'gldt-HwllOuhfw-wu0rlD_yep',
            True,
        ),
        (
            # token < 20 chars should be too short
            'gldt-seems_too000Sshorty',
            False,
        ),
        (
            # invalid prefix, but valid token length
            'foo-hello-world80_testin',
            False,
        ),
        (
            # token length may vary depending on the impl., but <= 50 chars should be fine
            'glsoat-PREfix_helloworld380_testin_pretty_long_token_long',
            True,
        ),
        (
            # token > 50 chars is too long
            'glsoat-PREfix_helloworld380_testin_pretty_long_token_long_',
            False,
        ),
        (
            # GitLab is not GitHub
            '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',
            False,
        ),
    ],
)
def test_gitlabtoken_detector_detects_expected_secrets(secret: str, should_flag: bool):
    """
    Integration-style test against the GitLabTokenDetector.

    Uses the same payload set as detect-secrets itself to ensure we
    correctly wire the GitLabTokenDetector via our inspection pipeline.
    """
    req = PromptInspectionRequest(prompt=f"This is my secret: {secret}", meta=None)
    resp = analyze_prompt(req)

    finding = _get_finding(resp.findings, "secret_gitlab_token")

    if should_flag:
        assert finding is not None, f"Expected finding for payload: {secret!r}"
        # Ensure severity mapping from config is applied
        assert finding.severity == "high"
        # Confidence should be present and in a sane range (0..1)
        assert finding.confidence is not None
        assert 0.0 <= finding.confidence <= 1.0
    else:
        assert finding is None, f"Did not expect finding for payload: {secret!r}"
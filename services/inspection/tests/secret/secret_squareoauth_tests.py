# Test payloads adapted from detect-secrets AWSKeyDetector tests
# (https://github.com/Yelp/detect-secrets), licensed under Apache-2.0.

import pytest

from core.models import PromptInspectionRequest
from core.rules import analyze_prompt

def _get_finding(findings, type_id: str):
    """Return first finding with matching type_id or None."""
    return next((f for f in findings if f.type == type_id), None)

SL_USERNAME = 'test@testy.test'
SL_TOKEN = 'abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234'

@pytest.mark.parametrize(
    'secret, should_flag',
    [
        ('square_oauth = sq0csp-ABCDEFGHIJK_LMNOPQRSTUVWXYZ-0123456789\\abcd', True),
    ],
)
def test_squareoauthsecret_detector_detects_expected_secrets(secret: str, should_flag: bool):
    """
    Integration-style test against the SquareOAuthDetector.

    Uses the same payload set as detect-secrets itself to ensure we
    correctly wire the SquareOAuthDetector via our inspection pipeline.
    """
    req = PromptInspectionRequest(prompt=f"This is my secret: {secret}", meta=None)
    resp = analyze_prompt(req)

    finding = _get_finding(resp.findings, "secret_square_oauth_secret")

    if should_flag:
        assert finding is not None, f"Expected finding for payload: {secret!r}"
        # Ensure severity mapping from config is applied
        assert finding.severity == "high"
        # Confidence should be present and in a sane range (0..1)
        assert finding.confidence is not None
        assert 0.0 <= finding.confidence <= 1.0
    else:
        assert finding is None, f"Did not expect finding for payload: {secret!r}"
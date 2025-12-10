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
        ('//registry.npmjs.org/:_authToken=743b294a-cd03-11ec-9d64-0242ac120002', True),
        ('//registry.npmjs.org/:_authToken=346a14f2-a672-4668-a892-956a462ab56e', True),
        ('//registry.npmjs.org/:_authToken= 743b294a-cd03-11ec-9d64-0242ac120002', True),
        ('//registry.npmjs.org/:_authToken=npm_xxxxxxxxxxx', True),
        ('//registry.npmjs.org:_authToken=743b294a-cd03-11ec-9d64-0242ac120002', False),
        ('registry.npmjs.org/:_authToken=743b294a-cd03-11ec-9d64-0242ac120002', False),
        ('///:_authToken=743b294a-cd03-11ec-9d64-0242ac120002', False),
        ('_authToken=743b294a-cd03-11ec-9d64-0242ac120002', False),
        ('foo', False),
        ('//registry.npmjs.org/:_authToken=${NPM_TOKEN}', False),
    ],
)
def test_npmtoken_detector_detects_expected_secrets(secret: str, should_flag: bool):
    """
    Integration-style test against the NpmDetector.

    Uses the same payload set as detect-secrets itself to ensure we
    correctly wire the NpmDetector via our inspection pipeline.
    """
    req = PromptInspectionRequest(prompt=f"This is my secret: {secret}", meta=None)
    resp = analyze_prompt(req)

    finding = _get_finding(resp.findings, "secret_npm_token")

    if should_flag:
        assert finding is not None, f"Expected finding for payload: {secret!r}"
        # Ensure severity mapping from config is applied
        assert finding.severity == "high"
        # Confidence should be present and in a sane range (0..1)
        assert finding.confidence is not None
        assert 0.0 <= finding.confidence <= 1.0
    else:
        assert finding is None, f"Did not expect finding for payload: {secret!r}"
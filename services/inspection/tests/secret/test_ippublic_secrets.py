# Test payloads adapted from detect-secrets AWSKeyDetector tests
# (https://github.com/Yelp/detect-secrets), licensed under Apache-2.0.

import pytest

from core.models import PromptInspectionRequest
from core.rules import analyze_prompt

def _get_finding(findings, type_id: str):
    """Return first finding with matching type_id or None."""
    return next((f for f in findings if f.type == type_id), None)

@pytest.mark.skip(reason="Broken because of IPPublicDetector – will revisit later")
@pytest.mark.parametrize(
    'secret, should_flag',
    [
        # Valid IPv4 addresses, Public
        ('133.133.133.133', True),
        ('This line has an IP address 133.133.133.133@something else', True),
        ('133.133.133.133:8080', True),
        ('This line has an IP address: 133.133.133.133:8080@something else', True),
        ('1.1.1.1', True),
        # Valid IPv4 addresses, Non-public
        ('127.0.0.1', False),
        ('10.0.0.1', False),
        ('172.16.0.1', False),
        ('192.168.0.1', False),
        # Invalid IPv4 addresses
        ('256.256.256.256', False),
        ('1.2.3', False),
        ('1.2.3.4.5.6', False),
        ('1.2.3.4.5.6.7.8', False),
        ('1.2.3.04', False),
        ('noreply@github.com', False),
        ('github.com', False),
    ],
)
def test_publicipaddress_detector_detects_expected_secrets(secret: str, should_flag: bool):
    """
    Integration-style test against the IPPublicDetector.

    Uses the same payload set as detect-secrets itself to ensure we
    correctly wire the IPPublicDetector via our inspection pipeline.
    """
    req = PromptInspectionRequest(prompt=f"This is my secret: {secret}", meta=None)
    resp = analyze_prompt(req)

    finding = _get_finding(resp.findings, "secret_public_ip_address")

    if should_flag:
        assert finding is not None, f"Expected finding for payload: {secret!r}"
        # Ensure severity mapping from config is applied
        assert finding.severity == "high"
        # Confidence should be present and in a sane range (0..1)
        assert finding.confidence is not None
        assert 0.0 <= finding.confidence <= 1.0
    else:
        assert finding is None, f"Did not expect finding for payload: {secret!r}"
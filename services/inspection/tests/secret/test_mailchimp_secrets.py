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
        ('343ea45721923ed956e2b38c31db76aa-us30', True),
        ('a2937653ed38c31a43ea46e2b19257db-us2', True),
        ('3ea4572956e2b381923ed34c31db76aa-2', False),
        ('aea462953eb192d38c31a433e76257db-al32', False),
        ('9276a43e2951aa46e2b1c33ED38357DB-us2', False),
        ('3a5633e829d3c71-us2', False),
    ],
)
def test_mailchimpaccesskey_detector_detects_expected_secrets(secret: str, should_flag: bool):
    """
    Integration-style test against the MailchimpDetector.

    Uses the same payload set as detect-secrets itself to ensure we
    correctly wire the MailchimpDetector via our inspection pipeline.
    """
    req = PromptInspectionRequest(prompt=f"This is my secret: {secret}", meta=None)
    resp = analyze_prompt(req)

    finding = _get_finding(resp.findings, "secret_mailchimp_access_key")

    if should_flag:
        assert finding is not None, f"Expected finding for payload: {secret!r}"
        # Ensure severity mapping from config is applied
        assert finding.severity == "high"
        # Confidence should be present and in a sane range (0..1)
        assert finding.confidence is not None
        assert 0.0 <= finding.confidence <= 1.0
    else:
        assert finding is None, f"Did not expect finding for payload: {secret!r}"
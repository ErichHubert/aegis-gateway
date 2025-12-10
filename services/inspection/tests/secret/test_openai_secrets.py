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
        # pragma: allowlist nextline secret
        ('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', True),
        # pragma: allowlist nextline secret
        ('sk-proj-Xi8tdMjHV6pmbBbwilTeT3BlbkFJ3UDnpdEwNNm6wVBpYM0o', True),
        # pragma: allowlist nextline secret
        ('sk-proj-Xi8tdMjHV6pmbBbwilTeT4BlbkFJ3UDnpdEwNNm6wVBpYM0o', False),
    ],
)
def test_openaitoken_detector_detects_expected_secrets(secret: str, should_flag: bool):
    """
    Integration-style test against the OpenAIDetector.

    Uses the same payload set as detect-secrets itself to ensure we
    correctly wire the OpenAIDetector via our inspection pipeline.
    """
    req = PromptInspectionRequest(prompt=f"This is my secret: {secret}", meta=None)
    resp = analyze_prompt(req)

    finding = _get_finding(resp.findings, "secret_openai_token")

    if should_flag:
        assert finding is not None, f"Expected finding for payload: {secret!r}"
        # Ensure severity mapping from config is applied
        assert finding.severity == "high"
        # Confidence should be present and in a sane range (0..1)
        assert finding.confidence is not None
        assert 0.0 <= finding.confidence <= 1.0
    else:
        assert finding is None, f"Did not expect finding for payload: {secret!r}"
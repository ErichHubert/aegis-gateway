# Test payloads adapted from detect-secrets AWSKeyDetector tests
# (https://github.com/Yelp/detect-secrets), licensed under Apache-2.0.

import pytest

from core.config.loader import load_config
from core.config.models import InspectionConfig
from core.detectors.secret.detectsecret.detector import DetectSecretsDetector
from core.models import Finding, PromptInspectionRequest, PromptInspectionResponse

def _get_finding(findings, type_id: str) -> Finding | None:
    """Return first finding with matching type_id or None."""
    return next((f for f in findings if f.type == type_id), None)

@pytest.mark.parametrize(
    'secret, should_flag',
    [
        ('xoxp-523423-234243-234233-e039d02840a0b9379c', True),
        ('xoxo-523423-234243-234233-e039d02840a0b9379c', True),
        ('xoxs-523423-234243-234233-e039d02840a0b9379c', True),
        ('xoxa-511111111-31111111111-3111111111111-e039d02840a0b9379c', True),
        ('xoxa-2-511111111-31111111111-3111111111111-e039d02840a0b9379c', True),
        ('xoxr-523423-234243-234233-e039d02840a0b9379c', True),
        ('xoxb-34532454-e039d02840a0b9379c', True),
        ('https://hooks.slack.com/services/Txxxxxxxx/Bxxxxxxxx/xxxxxxxxxxxxxxxxxxxxxxxx', True),
    ],
)
def test_slacktoken_detector_detects_expected_secrets(run_with_detector, secret: str, should_flag: bool):
    """
    Integration-style test against the SlackDetector.

    Uses the same payload set as detect-secrets itself to ensure we
    correctly wire the SlackDetector via our inspection pipeline.
    """
    # Arrange
    cfg: InspectionConfig = load_config()
    detector = DetectSecretsDetector(cfg)
    req = PromptInspectionRequest(prompt=f"This is my secret: {secret}", meta=None)
    
    # Act
    resp: PromptInspectionResponse = run_with_detector(detector, req)
    finding: Finding | None = _get_finding(resp.findings, "secret_slack_token")

    # Assert
    if should_flag:
        assert finding is not None, f"Expected finding for payload: {secret!r}"
        # Ensure severity mapping from config is applied
        assert finding.severity == "high"
        # Confidence should be present and in a sane range (0..1)
        assert finding.confidence is not None
        assert 0.0 <= finding.confidence <= 1.0
    else:
        assert finding is None, f"Did not expect finding for payload: {secret!r}"
# Test payloads adapted from detect-secrets AWSKeyDetector tests
# (https://github.com/Yelp/detect-secrets), licensed under Apache-2.0.

import pytest # autoloads conftest.py fixtures

from core.config.loader import load_config
from core.config.models import InspectionConfig
from core.detectors.secret.detectsecret.detector import DetectSecretsDetector
from core.models import Finding, PromptInspectionRequest, PromptInspectionResponse

def _get_finding(findings, type_id: str) -> Finding | None: 
    """Return first finding with matching type_id or None."""
    return next((f for f in findings if f.type == type_id), None)

@pytest.mark.parametrize(
    "secret, should_flag",
    [
        ('AP6xxxxxxxxxx', True),
        ('AP2xxxxxxxxxx', True),
        ('AP3xxxxxxxxxx', True),
        ('AP5xxxxxxxxxx', True),
        ('APAxxxxxxxxxx', True),
        ('APBxxxxxxxxxx', True),
        ('AKCxxxxxxxxxx', True),
        (' AP6xxxxxxxxxx', True),
        (' AKCxxxxxxxxxx', True),
        ('=AP6xxxxxxxxxx', True),
        ('=AKCxxxxxxxxxx', True),
        ('\"AP6xxxxxxxxxx\"', True),
        ('\"AKCxxxxxxxxxx\"', True),
        ('artif-key:AP6xxxxxxxxxx', True),
        ('artif-key:AKCxxxxxxxxxx', True),
        ('X-JFrog-Art-Api: AKCxxxxxxxxxx', True),
        ('X-JFrog-Art-Api: AP6xxxxxxxxxx', True),
        ('artifactoryx:_password=AKCxxxxxxxxxx', True),
        ('artifactoryx:_password=AP6xxxxxxxxxx', True),
        # negative / should not be detected
        ("testAKCwithinsomeirrelevantstring", False),
        ("testAP6withinsomeirrelevantstring", False),
        ("X-JFrog-Art-Api: $API_KEY", False),
        ("X-JFrog-Art-Api: $PASSWORD", False),
        ("artifactory:_password=AP6xxxxxx", False),
        ("artifactory:_password=AKCxxxxxxxx", False),
    ],
)
def test_artifactory_detector_detects_expected_secrets(run_with_detector, secret: str, should_flag: bool):
    """
    Integration-style test against the ArtifactoryDetector.

    Uses the same payload set as detect-secrets itself to ensure we
    correctly wire the ArtifactoryDetector via our inspection pipeline.
    """
    # Arrange
    cfg: InspectionConfig = load_config()
    detector = DetectSecretsDetector(cfg)
    req = PromptInspectionRequest(prompt=f"This is my secret: {secret}", meta=None)
    
    # Act
    resp: PromptInspectionResponse = run_with_detector(detector, req)
    finding: Finding | None = _get_finding(resp.findings, "secret_artifactory_credentials")

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
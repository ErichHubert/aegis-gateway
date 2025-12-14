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

ACCESS_KEY_ID = '1234567890abcdef1234567890abcdef'
SECRET_ACCESS_KEY = '1234567890abcdef1234567890abcdef1234567890abcdef'

@pytest.mark.parametrize(
    'secret, should_flag',
    [
        ('"secret_access_key": "{secret}"'.format(secret=SECRET_ACCESS_KEY), True),
        ('"secret_access_key": "{secret}extra"'.format(secret=SECRET_ACCESS_KEY), False),
        ('secret_access_key={secret}'.format(secret=SECRET_ACCESS_KEY), True),
        ('secret_access_key={secret}extra'.format(secret=SECRET_ACCESS_KEY), False),
        ('secret_access_key="{secret}"'.format(secret=SECRET_ACCESS_KEY), True),
        ('secret_access_key=\'{secret}\''.format(secret=SECRET_ACCESS_KEY), True),
        ('secret_access_key = "{secret}"'.format(secret=SECRET_ACCESS_KEY), True),
        ('COS_HMAC_SECRET_ACCESS_KEY = "{secret}"'.format(secret=SECRET_ACCESS_KEY), True),
        ('ibm_cos_SECRET_ACCESS_KEY = "{secret}"'.format(secret=SECRET_ACCESS_KEY), True),
        ('ibm_cos_secret_access_key = "{secret}"'.format(secret=SECRET_ACCESS_KEY), True),
        ('ibm_cos_secret_key = "{secret}"'.format(secret=SECRET_ACCESS_KEY), True),
        ('cos_secret_key = "{secret}"'.format(secret=SECRET_ACCESS_KEY), True),
        ('ibm-cos_secret_key = "{secret}"'.format(secret=SECRET_ACCESS_KEY), True),
        ('cos-hmac_secret_key = "{secret}"'.format(secret=SECRET_ACCESS_KEY), True),
        ('coshmac_secret_key = "{secret}"'.format(secret=SECRET_ACCESS_KEY), True),
        ('ibmcoshmac_secret_key = "{secret}"'.format(secret=SECRET_ACCESS_KEY), True),
        ('ibmcos_secret_key = "{secret}"'.format(secret=SECRET_ACCESS_KEY), True),
        ('not_secret = notapassword', False),
        ('someotherpassword = "doesnt start right"', False),
    ],
)
def test_ibmcoshmaccredentials_detector_detects_expected_secrets(run_with_detector, secret: str, should_flag: bool):
    """
    Integration-style test against the IbmCosHmacDetector.

    Uses the same payload set as detect-secrets itself to ensure we
    correctly wire the IbmCosHmacDetector via our inspection pipeline.
    """
    # Arrange
    cfg: InspectionConfig = load_config()
    detector = DetectSecretsDetector(cfg)
    req = PromptInspectionRequest(prompt=f"This is my secret: {secret}", meta=None)
    
    # Act
    resp: PromptInspectionResponse = run_with_detector(detector, req)
    finding: Finding | None = _get_finding(resp.findings, "secret_ibm_cos_hmac_credentials")

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
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

CLOUD_IAM_KEY = 'abcd1234abcd1234abcd1234ABCD1234ABCD1234--__'
CLOUD_IAM_KEY_BYTES = b'abcd1234abcd1234abcd1234ABCD1234ABCD1234--__'

@pytest.mark.parametrize(
    'secret, should_flag',
    [
        ('ibm-cloud_api_key: {cloud_iam_key}'.format(cloud_iam_key=CLOUD_IAM_KEY), True),
        ('ibm_cloud_iam-key : {cloud_iam_key}'.format(cloud_iam_key=CLOUD_IAM_KEY), True),
        ('IBM-API-KEY : "{cloud_iam_key}"'.format(cloud_iam_key=CLOUD_IAM_KEY), True),
        ('"iam_api_key" : "{cloud_iam_key}"'.format(cloud_iam_key=CLOUD_IAM_KEY), True),
        ('cloud-api-key: "{cloud_iam_key}"'.format(cloud_iam_key=CLOUD_IAM_KEY), True),
        ('"iam-password": "{cloud_iam_key}"'.format(cloud_iam_key=CLOUD_IAM_KEY), True),
        ('CLOUD_IAM_API_KEY:"{cloud_iam_key}"'.format(cloud_iam_key=CLOUD_IAM_KEY), True),
        ('ibm-cloud-key:{cloud_iam_key}'.format(cloud_iam_key=CLOUD_IAM_KEY), True),
        ('ibm_key:"{cloud_iam_key}"'.format(cloud_iam_key=CLOUD_IAM_KEY), True),
        (
            '"ibm_cloud_iam_api_key":"{cloud_iam_key}"'.format(
                cloud_iam_key=CLOUD_IAM_KEY,
            ), True,
        ),
        ('ibm_cloud_iamapikey= {cloud_iam_key}'.format(cloud_iam_key=CLOUD_IAM_KEY), True),
        ('ibm_cloud_api_key= "{cloud_iam_key}"'.format(cloud_iam_key=CLOUD_IAM_KEY), True),
        ('IBMCLOUDIAMAPIKEY={cloud_iam_key}'.format(cloud_iam_key=CLOUD_IAM_KEY), True),
        ('cloud_iam_api_key="{cloud_iam_key}"'.format(cloud_iam_key=CLOUD_IAM_KEY), True),
        ('ibm_api_key := {cloud_iam_key}'.format(cloud_iam_key=CLOUD_IAM_KEY), True),
        ('"ibm-iam_key" := "{cloud_iam_key}"'.format(cloud_iam_key=CLOUD_IAM_KEY), True),
        (
            '"ibm_cloud_iam_api_key":= "{cloud_iam_key}"'.format(
                cloud_iam_key=CLOUD_IAM_KEY,
            ), True,
        ),
        ('ibm-cloud_api_key:={cloud_iam_key}'.format(cloud_iam_key=CLOUD_IAM_KEY), True),
        ('"cloud_iam_api_key":="{cloud_iam_key}"'.format(cloud_iam_key=CLOUD_IAM_KEY), True),
        ('ibm_iam_key:= "{cloud_iam_key}"'.format(cloud_iam_key=CLOUD_IAM_KEY), True),
        ('ibm_iam_key:= "{cloud_iam_key}extra"'.format(cloud_iam_key=CLOUD_IAM_KEY), False),
        ('ibm_api_key:="{cloud_iam_key}"'.format(cloud_iam_key=CLOUD_IAM_KEY), True),
        ('ibm_password = "{cloud_iam_key}"'.format(cloud_iam_key=CLOUD_IAM_KEY), True),
        ('ibm-cloud-pwd = {cloud_iam_key}'.format(cloud_iam_key=CLOUD_IAM_KEY), True),
        ('ibm-cloud-pwd = {cloud_iam_key}extra'.format(cloud_iam_key=CLOUD_IAM_KEY), False),
        ('ibm-cloud-pwd = shorter-version', False),
        ('apikey:{cloud_iam_key}'.format(cloud_iam_key=CLOUD_IAM_KEY), True),
        ('iam_api_key="%s" % IBM_IAM_API_KEY_ENV', False),
        ('CLOUD_APIKEY: "insert_key_here"', False),
        ('cloud-iam-key:=afakekey', False),
        ('fake-cloud-iam-key= "not_long_enough"', False),
    ],
)
def test_ibmcloudiamkey_detector_detects_expected_secrets(run_with_detector, secret: str, should_flag: bool):
    """
    Integration-style test against the IbmCloudIamDetector.

    Uses the same payload set as detect-secrets itself to ensure we
    correctly wire the IbmCloudIamDetector via our inspection pipeline.
    """
    # Arrange
    cfg: InspectionConfig = load_config()
    detector = DetectSecretsDetector(cfg)
    req = PromptInspectionRequest(prompt=f"This is my secret: {secret}", meta=None)
    
    # Act
    resp: PromptInspectionResponse = run_with_detector(detector, req)
    finding: Finding | None = _get_finding(resp.findings, "secret_ibm_cloud_iam_key")

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
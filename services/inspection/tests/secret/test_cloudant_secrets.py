# Test payloads adapted from detect-secrets AWSKeyDetector tests
# (https://github.com/Yelp/detect-secrets), licensed under Apache-2.0.

import pytest

from core.config.loader import load_config
from core.config.models import InspectionConfig
from core.detectors.secret.detectsecret.detector import DetectSecretsDetector
from core.models import Finding, PromptInspectionRequest, PromptInspectionResponse

CL_ACCOUNT = 'testy_-test'  # also called user
# only detecting 64 hex CL generated password
CL_PW = 'abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234'

# detecting 24 alpha for CL generated API KEYS
CL_API_KEY = 'abcdefghijabcdefghijabcd'


def _get_finding(findings, type_id: str) -> Finding | None:
    """Return first finding with matching type_id or None."""
    return next((f for f in findings if f.type == type_id), None)


@pytest.mark.parametrize(
    'secret, should_flag',
    [
        (
            'https://{cl_account}:{cl_pw}@{cl_account}.cloudant.com"'.format(
                cl_account=CL_ACCOUNT, cl_pw=CL_PW,
            ), True,
        ),
        (
            'https://{cl_account}:{cl_pw}@{cl_account}.cloudant.com/_api/v2/'.format(
                cl_account=CL_ACCOUNT, cl_pw=CL_PW,
            ), True,
        ),
        (
            'https://{cl_account}:{cl_pw}@{cl_account}.cloudant.com/_api/v2/'.format(
                cl_account=CL_ACCOUNT, cl_pw=CL_PW,
            ), True,
        ),
        (
            'https://{cl_account}:{cl_pw}@{cl_account}.cloudant.com'.format(
                cl_account=CL_ACCOUNT, cl_pw=CL_PW,
            ), True,
        ),
        (
            'https://{cl_account}:{cl_api_key}@{cl_account}.cloudant.com'.format(
                cl_account=CL_ACCOUNT, cl_api_key=CL_API_KEY,
            ), True,
        ),
        (
            'https://{cl_account}:{cl_pw}.cloudant.com'.format(
                cl_account=CL_ACCOUNT, cl_pw=CL_PW,
            ), False,
        ),
        ('cloudant_password=\'{cl_pw}\''.format(cl_pw=CL_PW), True),
        ('cloudant_pw=\'{cl_pw}\''.format(cl_pw=CL_PW), True),
        ('cloudant_pw="{cl_pw}"'.format(cl_pw=CL_PW), True),
        ('clou_pw = "{cl_pw}"'.format(cl_pw=CL_PW), True),
        ('cloudant_key = "{cl_api_key}"'.format(cl_api_key=CL_API_KEY), True),
        ('cloudant_password = "a-fake-tooshort-key"', False),
        ('cl_api_key = "a-fake-api-key"', False),
    ],
)
def test_cloudant_detector_detects_expected_secrets(run_with_detector, secret: str, should_flag: bool):
    """
    Integration-style test against the CloudantDetector.

    Uses the same payload set as detect-secrets itself to ensure we
    correctly wire the CloudantDetector via our inspection pipeline.
    """
    # Arrange
    cfg: InspectionConfig = load_config()
    detector = DetectSecretsDetector(cfg)
    req = PromptInspectionRequest(prompt=f"This is my secret: {secret}", meta=None)

    # Act
    resp: PromptInspectionResponse = run_with_detector(detector, req)
    finding: Finding | None = _get_finding(resp.findings, "secret_cloudant_credentials")

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
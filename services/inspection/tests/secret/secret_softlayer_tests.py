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
        ('--softlayer-api-key "{sl_token}"'.format(sl_token=SL_TOKEN), True),
        ('--softlayer-api-key="{sl_token}"'.format(sl_token=SL_TOKEN), True),
        ('--softlayer-api-key {sl_token}'.format(sl_token=SL_TOKEN), True),
        ('--softlayer-api-key={sl_token}'.format(sl_token=SL_TOKEN), True),
        ('http://api.softlayer.com/soap/v3/{sl_token}'.format(sl_token=SL_TOKEN), True),
        ('http://api.softlayer.com/soap/v3.1/{sl_token}'.format(sl_token=SL_TOKEN), True),
        ('softlayer_api_key: {sl_token}'.format(sl_token=SL_TOKEN), True),
        ('softlayer-key : {sl_token}'.format(sl_token=SL_TOKEN), True),
        ('SOFTLAYER-API-KEY : "{sl_token}"'.format(sl_token=SL_TOKEN), True),
        ('"softlayer_api_key" : "{sl_token}"'.format(sl_token=SL_TOKEN), True),
        ('softlayer-api-key: "{sl_token}"'.format(sl_token=SL_TOKEN), True),
        ('"softlayer_api_key": "{sl_token}"'.format(sl_token=SL_TOKEN), True),
        ('SOFTLAYER_API_KEY:"{sl_token}"'.format(sl_token=SL_TOKEN), True),
        ('softlayer-key:{sl_token}'.format(sl_token=SL_TOKEN), True),
        ('softlayer_key:"{sl_token}"'.format(sl_token=SL_TOKEN), True),
        ('"softlayer_api_key":"{sl_token}"'.format(sl_token=SL_TOKEN), True),
        ('softlayerapikey= {sl_token}'.format(sl_token=SL_TOKEN), True),
        ('softlayer_api_key= "{sl_token}"'.format(sl_token=SL_TOKEN), True),
        ('SOFTLAYERAPIKEY={sl_token}'.format(sl_token=SL_TOKEN), True),
        ('softlayer_api_key="{sl_token}"'.format(sl_token=SL_TOKEN), True),
        ('sl_api_key: {sl_token}'.format(sl_token=SL_TOKEN), True),
        ('SLAPIKEY : {sl_token}'.format(sl_token=SL_TOKEN), True),
        ('sl_apikey : "{sl_token}"'.format(sl_token=SL_TOKEN), True),
        ('"sl_api_key" : "{sl_token}"'.format(sl_token=SL_TOKEN), True),
        ('sl-key: "{sl_token}"'.format(sl_token=SL_TOKEN), True),
        ('"sl_api_key": "{sl_token}"'.format(sl_token=SL_TOKEN), True),
        ('sl_api_key:"{sl_token}"'.format(sl_token=SL_TOKEN), True),
        ('sl_api_key:{sl_token}'.format(sl_token=SL_TOKEN), True),
        ('sl-api-key:"{sl_token}"'.format(sl_token=SL_TOKEN), True),
        ('"sl_api_key":"{sl_token}"'.format(sl_token=SL_TOKEN), True),
        ('sl_key= {sl_token}'.format(sl_token=SL_TOKEN), True),
        ('sl_api_key= "{sl_token}"'.format(sl_token=SL_TOKEN), True),
        ('sl-api-key={sl_token}'.format(sl_token=SL_TOKEN), True),
        ('slapi_key="{sl_token}"'.format(sl_token=SL_TOKEN), True),
        ('slapikey:= {sl_token}'.format(sl_token=SL_TOKEN), True),
        ('softlayer_api_key := {sl_token}'.format(sl_token=SL_TOKEN), True),
        ('sl_api_key := "{sl_token}"'.format(sl_token=SL_TOKEN), True),
        ('"softlayer_key" := "{sl_token}"'.format(sl_token=SL_TOKEN), True),
        ('sl_api_key: "{sl_token}"'.format(sl_token=SL_TOKEN), True),
        ('"softlayer_api_key":= "{sl_token}"'.format(sl_token=SL_TOKEN), True),
        ('sl-api-key:="{sl_token}"'.format(sl_token=SL_TOKEN), True),
        ('softlayer_api_key:={sl_token}'.format(sl_token=SL_TOKEN), True),
        ('slapikey:"{sl_token}"'.format(sl_token=SL_TOKEN), True),
        ('"softlayer_api_key":="{sl_token}"'.format(sl_token=SL_TOKEN), True),
        ('sl-api-key:= {sl_token}'.format(sl_token=SL_TOKEN), True),
        ('softlayer_key:= "{sl_token}"'.format(sl_token=SL_TOKEN), True),
        ('sl_api_key={sl_token}'.format(sl_token=SL_TOKEN), True),
        ('softlayer_api_key:="{sl_token}"'.format(sl_token=SL_TOKEN), True),
        ('softlayer_password = "{sl_token}"'.format(sl_token=SL_TOKEN), True),
        ('sl_pass="{sl_token}"'.format(sl_token=SL_TOKEN), True),
        ('softlayer-pwd = {sl_token}'.format(sl_token=SL_TOKEN), True),
        ('softlayer_api_key="%s" % SL_API_KEY_ENV', False),
        ('sl_api_key: "%s" % <softlayer_api_key>', False),
        ('SOFTLAYER_APIKEY: "insert_key_here"', False),
        ('sl-apikey: "insert_key_here"', False),
        ('softlayer-key:=afakekey', False),
        ('fake-softlayer-key= "not_long_enough"', False),
    ],
)
def test_softlayercredentials_detector_detects_expected_secrets(secret: str, should_flag: bool):
    """
    Integration-style test against the SoftlayerDetector.

    Uses the same payload set as detect-secrets itself to ensure we
    correctly wire the SoftlayerDetector via our inspection pipeline.
    """
    req = PromptInspectionRequest(prompt=f"This is my secret: {secret}", meta=None)
    resp = analyze_prompt(req)

    finding = _get_finding(resp.findings, "secret_softlayer_credentials")

    if should_flag:
        assert finding is not None, f"Expected finding for payload: {secret!r}"
        # Ensure severity mapping from config is applied
        assert finding.severity == "high"
        # Confidence should be present and in a sane range (0..1)
        assert finding.confidence is not None
        assert 0.0 <= finding.confidence <= 1.0
    else:
        assert finding is None, f"Did not expect finding for payload: {secret!r}"
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
        # From https://discord.com/developers/docs/reference#authentication
        (
            'MTk4NjIyNDgzNDcxOTI1MjQ4.Cl2FMQ.ZnCjm1XVW7vRze4b7Cq4se7kKWs',
            True,
        ),
        (
            'Nzk5MjgxNDk0NDc2NDU1OTg3.YABS5g.2lmzECVlZv3vv6miVnUaKPQi2wI',
            True,
        ),
        # From https://docs.gitguardian.com/secrets-detection/detectors/specifics/discord_bot_token#examples  # noqa: E501
        (
            'MZ1yGvKTjE0rY0cV8i47CjAa.uRHQPq.Xb1Mk2nEhe-4iUcrGOuegj57zMC',
            True,
        ),
        # From https://github.com/Yelp/detect-secrets/issues/627
        (
            'OTUyNED5MDk2MTMxNzc2MkEz.YjESug.UNf-1GhsIG8zWT409q2C7Bh_zWQ',
            True,
        ),
        (
            'OTUyNED5MDk2MTMxNzc2MkEz.GSroKE.g2MTwve8OnUAAByz8KV_ZTV1Ipzg4o_NmQWUMs',
            True,
        ),
        (
            'MTAyOTQ4MTN5OTU5MTDwMEcxNg.GSwJyi.sbaw8msOR3Wi6vPUzeIWy_P0vJbB0UuRVjH8l8',
            True,
        ),
        # Pass - token starts on the 3rd character (first segment is 24 characters)
        (
            'ATMyOTQ4MTN5OTU5MTDwMEcxNg.GSwJyi.sbaw8msOR3Wi6vPUzeIWy_P0vJbB0UuRVjH8l8',
            True,
        ),
        # Pass - token starts on the 2nd character (first segment is 25 characters)
        (
            '=MTAyOTQ4MTN5OTU5MTDwMEcxN.GSwJyi.sbaw8msOR3Wi6vPUzeIWy_P0vJbB0UuRVjH8l8',
            True,
        ),
        # Pass - token ends before the '!' (last segment is 27 characters)
        (
            'MTAyOTQ4MTN5OTU5MTDwMEcxNg.YjESug.UNf-1GhsIG8zWT409q2C7Bh_zWQ!4o_NmQWUMs',
            True,
        ),
        # Fail - all segments too short (23.5.26)
        (
            'MZ1yGvKTj0rY0cV8i47CjAa.uHQPq.Xb1Mk2nEhe-4icrGOuegj57zMC',
            False,
        ),
        # Fail - first segment too short (23.6.27)
        (
            'MZ1yGvKTj0rY0cV8i47CjAa.uRHQPq.Xb1Mk2nEhe-4iUcrGOuegj57zMC',
            False,
        ),
        # Fail - middle segment too short (24.5.27)
        (
            'MZ1yGvKTjE0rY0cV8i47CjAa.uHQPq.Xb1Mk2nEhe-4iUcrGOuegj57zMC',
            False,
        ),
        # Fail - last segment too short (24.6.26)
        (
            'MZ1yGvKTjE0rY0cV8i47CjAa.uRHQPq.Xb1Mk2nEhe-4iUcrGOuegj57zM',
            False,
        ),
        # Fail - contains invalid character ','
        (
            'MZ1yGvKTjE0rY0cV8i47CjAa.uRHQPq.Xb1Mk2nEhe,4iUcrGOuegj57zMC',
            False,
        ),
        # Fail - invalid first character 'P' (must be one of M/N/O)
        (
            'PZ1yGvKTjE0rY0cV8i47CjAa.uRHQPq.Xb1Mk2nEhe-4iUcrGOuegj57zMC',
            False,
        ),
        # Fail - first segment 1 character too long; causes invalid first character 'T'
        (
            'MTAyOTQ4MTN5OTU5MTDwMEcxNg0.GSwJyi.sbaw8msOR3Wi6vPUzeIWy_P0vJbB0UuRVjH8l8',
            False,
        ),
    ],
)
def test_discord_detector_detects_expected_secrets(secret: str, should_flag: bool):
    """
    Integration-style test against the DiscordBotTokenDetector.

    Uses the same payload set as detect-secrets itself to ensure we
    correctly wire the DiscordBotTokenDetector via our inspection pipeline.
    """
    req = PromptInspectionRequest(prompt=f"This is my secret: {secret}", meta=None)
    resp = analyze_prompt(req)

    finding = _get_finding(resp.findings, "secret_discord_bot_token")

    if should_flag:
        assert finding is not None, f"Expected finding for payload: {secret!r}"
        # Ensure severity mapping from config is applied
        assert finding.severity == "high"
        # Confidence should be present and in a sane range (0..1)
        assert finding.confidence is not None
        assert 0.0 <= finding.confidence <= 1.0
    else:
        assert finding is None, f"Did not expect finding for payload: {secret!r}"
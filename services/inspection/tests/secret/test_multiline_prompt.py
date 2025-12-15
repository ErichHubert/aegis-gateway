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


def test_detector_detects_secret_in_multiline_prompt(run_with_detector):
    """Ensure detectors work with multi-line prompts (e.g., chat transcripts)."""
    # Arrange
    cfg: InspectionConfig = load_config()
    detector = DetectSecretsDetector(cfg)

    secret = "MTk4NjIyNDgzNDcxOTI1MjQ4.Cl2FMQ.ZnCjm1XVW7vRze4b7Cq4se7kKWs"
    prompt = """System: You are a helpful assistant.
                User: Here is some context.
                User: This is my secret: {secret}
                Assistant: I will not leak secrets.
            """.format(secret=secret)

    req = PromptInspectionRequest(prompt=prompt, meta=None)

    # Act
    resp: PromptInspectionResponse = run_with_detector(detector, req)
    finding: Finding | None = _get_finding(resp.findings, "secret_discord_bot_token")

    # Assert
    assert finding is not None, "Expected Discord bot token finding for multiline prompt"
    assert finding.severity == "high"
    assert finding.start == 122
    assert finding.end == 181
    assert finding.confidence is not None
    assert 0.0 <= finding.confidence <= 1.0
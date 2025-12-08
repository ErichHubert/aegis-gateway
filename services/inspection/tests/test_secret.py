import pytest

from core.models import PromptInspectionRequest
from core.rules import analyze_prompt


def _get_finding(findings, type_id: str):
    return next((f for f in findings if f.type == type_id), None)


# -------------------
# aws tests (
# -------------------

def test_awskey_gas_high_severity():
    aws_key = "AKIA1234567890ABCDEF"
    text = f"My AWS Key is {aws_key}"

    req = PromptInspectionRequest(prompt=text, meta=None)
    resp = analyze_prompt(req)

    iban_finding = _get_finding(resp.findings, "secret_aws_access_key")
    assert iban_finding is not None, "Expected AWS Key to be detected as secret_aws_access_key"
    assert iban_finding.severity == "high"
    assert iban_finding.confidence is not None
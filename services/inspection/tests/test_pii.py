import pytest

from core.models import PromptInspectionRequest
from core.rules import analyze_prompt


def _get_finding(findings, type_id: str):
    return next((f for f in findings if f.type == type_id), None)


def test_iban_is_detected_as_pii_iban():
    # This is a valid German IBAN (official example from many docs)
    iban = "DE89 3704 0044 0532 0130 00"
    text = f"Please transfer the money to this account: {iban}."

    req = PromptInspectionRequest(prompt=text, meta=None)

    resp = analyze_prompt(req)

    iban_finding = _get_finding(resp.findings, "pii_iban")
    assert iban_finding is not None, "Expected IBAN to be detected as pii_iban"

    # Basic sanity checks on the finding
    assert "DE89" in iban_finding.snippet
    assert iban_finding.start >= 0
    assert iban_finding.end > iban_finding.start


def test_iban_finding_has_high_severity_in_config():
    # Same IBAN as above
    iban = "DE89 3704 0044 0532 0130 00"
    text = f"My IBAN is {iban}"

    req = PromptInspectionRequest(prompt=text, meta=None)
    resp = analyze_prompt(req)

    iban_finding = _get_finding(resp.findings, "pii_iban")
    assert iban_finding is not None, "Expected IBAN to be detected as pii_iban"
    assert iban_finding.severity == "high"
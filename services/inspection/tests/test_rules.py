from __future__ import annotations

from core.models import PromptInspectionRequest
from core.rules import analyze_prompt


def test_analyze_prompt_allows_harmless_text():
    req = PromptInspectionRequest(prompt="Explain the concept of zero trust architecture.")
    res = analyze_prompt(req)

    assert res.isAllowed is True
    assert res.findings == []


def test_analyze_prompt_blocks_obvious_secret():
    req = PromptInspectionRequest(prompt="Here is my key: AKIA1234567890ABCDEF")
    res = analyze_prompt(req)

    assert res.isAllowed is False
    types = {f.type for f in res.findings}
    assert "secret_aws_access_key" in types


def test_analyze_prompt_detects_email_pii_but_does_not_block():
    req = PromptInspectionRequest(prompt="Contact me at john.doe@example.com to proceed.")
    res = analyze_prompt(req)

    assert res.isAllowed is True
    email_findings = [f for f in res.findings if f.type == "pii_email"]
    assert len(email_findings) > 0
    assert any("john.doe@example.com" in f.snippet for f in email_findings)


def test_analyze_prompt_detects_phone_pii_but_does_not_block():
    req = PromptInspectionRequest(prompt="My phone number is +49 170 1234567.")
    res = analyze_prompt(req)

    assert res.isAllowed is True
    phone_findings = [f for f in res.findings if f.type == "pii_phone"]
    assert len(phone_findings) > 0
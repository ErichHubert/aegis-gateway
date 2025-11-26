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
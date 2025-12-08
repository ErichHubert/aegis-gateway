import pytest

from core.models import PromptInspectionRequest
from core.rules import analyze_prompt


def _get_finding(findings, type_id: str):
    return next((f for f in findings if f.type == type_id), None)


# -------------------
# IBAN tests (existing)
# -------------------

def test_iban_has_high_severity_and_confidence():
    iban = "DE89 3704 0044 0532 0130 00"
    text = f"My IBAN is {iban}"

    req = PromptInspectionRequest(prompt=text, meta=None)
    resp = analyze_prompt(req)

    iban_finding = _get_finding(resp.findings, "pii_iban")
    assert iban_finding is not None, "Expected IBAN to be detected as pii_iban"
    assert iban_finding.severity == "high"
    assert iban_finding.confidence is not None
    assert 0.0 <= iban_finding.confidence <= 1.0


# -------------------
# Email
# -------------------

def test_email_is_detected_as_pii_email():
    text = "Please contact john.doe@example.com for further information."

    req = PromptInspectionRequest(prompt=text, meta=None)
    resp = analyze_prompt(req)

    email_finding = _get_finding(resp.findings, "pii_email")
    assert email_finding is not None, "Expected email to be detected as pii_email"
    assert email_finding.severity == "medium"
    assert email_finding.confidence is not None
    assert 0.0 <= email_finding.confidence <= 1.0


# -------------------
# Phone
# -------------------

def test_phone_is_detected_as_pii_phone():
    text = "You can reach me at +1 212-555-0199 tomorrow."

    req = PromptInspectionRequest(prompt=text, meta=None)
    resp = analyze_prompt(req)

    phone_finding = _get_finding(resp.findings, "pii_phone")
    assert phone_finding is not None, "Expected phone to be detected as pii_phone"
    assert phone_finding.severity == "medium"
    assert phone_finding.confidence is not None
    assert 0.0 <= phone_finding.confidence <= 1.0


# -------------------
# Person
# -------------------

def test_person_is_detected_as_pii_person():
    text = "Our customer John Doe has opened a new support ticket."

    req = PromptInspectionRequest(prompt=text, meta=None)
    resp = analyze_prompt(req)

    person_finding = _get_finding(resp.findings, "pii_person")
    assert person_finding is not None, "Expected name to be detected as pii_person"
    assert person_finding.severity == "medium"
    assert person_finding.confidence is not None
    assert 0.0 <= person_finding.confidence <= 1.0


# -------------------
# Location
# -------------------

def test_location_is_detected_as_pii_location():
    text = "The office is located at 123 Main Street, Springfield."

    req = PromptInspectionRequest(prompt=text, meta=None)
    resp = analyze_prompt(req)

    location_finding = _get_finding(resp.findings, "pii_location")
    assert location_finding is not None, "Expected address to be detected as pii_location"
    assert location_finding.severity == "medium"
    assert location_finding.confidence is not None
    assert 0.0 <= location_finding.confidence <= 1.0


# -------------------
# Organization
# -------------------

def test_organization_is_detected_as_pii_organization():
    text = "He works at Acme Corporation in the finance department."

    req = PromptInspectionRequest(prompt=text, meta=None)
    resp = analyze_prompt(req)

    org_finding = _get_finding(resp.findings, "pii_organization")
    assert org_finding is not None, "Expected company to be detected as pii_organization"
    assert org_finding.severity == "medium"
    assert org_finding.confidence is not None
    assert 0.0 <= org_finding.confidence <= 1.0


# -------------------
# IP Address
# -------------------

def test_ip_is_detected_as_pii_ip_address():
    text = "The request originated from IP address 192.168.10.42 yesterday."

    req = PromptInspectionRequest(prompt=text, meta=None)
    resp = analyze_prompt(req)

    ip_finding = _get_finding(resp.findings, "pii_ip_address")
    assert ip_finding is not None, "Expected IP to be detected as pii_ip_address"
    assert ip_finding.severity == "high"
    assert ip_finding.confidence is not None
    assert 0.0 <= ip_finding.confidence <= 1.0


# -------------------
# Credit Card
# -------------------

def test_credit_card_is_detected_as_pii_credit_card():
    text = "The credit card number 4111 1111 1111 1111 was used for the payment."

    req = PromptInspectionRequest(prompt=text, meta=None)
    resp = analyze_prompt(req)

    cc_finding = _get_finding(resp.findings, "pii_credit_card")
    assert cc_finding is not None, "Expected card number to be detected as pii_credit_card"
    assert cc_finding.severity == "high"
    assert cc_finding.confidence is not None
    assert 0.0 <= cc_finding.confidence <= 1.0


# -------------------
# Date / Time
# -------------------

def test_datetime_is_detected_as_pii_datetime():
    text = "The follow-up meeting is scheduled on March 15, 2025 at 14:30."

    req = PromptInspectionRequest(prompt=text, meta=None)
    resp = analyze_prompt(req)

    dt_finding = _get_finding(resp.findings, "pii_datetime")
    assert dt_finding is not None, "Expected date/time to be detected as pii_datetime"
    assert dt_finding.severity == "low"
    assert dt_finding.confidence is not None
    assert 0.0 <= dt_finding.confidence <= 1.0
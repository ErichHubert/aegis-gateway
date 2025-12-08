import pytest

from core.models import PromptInspectionRequest
from core.rules import analyze_prompt


def _get_finding(findings, type_id: str):
    return next((f for f in findings if f.type == type_id), None)


# -------------------
# Secret detectors (detect-secrets based)
# -------------------

def test_aws_key_has_high_severity():
    aws_key = "AKIA1234567890ABCDEF"
    text = f"My AWS Key is {aws_key}"

    req = PromptInspectionRequest(prompt=text, meta=None)
    resp = analyze_prompt(req)

    finding = _get_finding(resp.findings, "secret_aws_access_key")
    assert finding is not None, "Expected AWS Key to be detected as secret_aws_access_key"
    assert finding.severity == "high"
    assert finding.confidence is not None


def test_artifactory_credentials_has_high_severity():
    secret = "AKCxxxxxxxxxx"
    text = f"My Artifactory secret is: {secret}"

    req = PromptInspectionRequest(prompt=text, meta=None)
    resp = analyze_prompt(req)

    finding = _get_finding(resp.findings, "secret_artifactory_credentials")
    assert finding is not None
    assert finding.severity == "high"
    assert finding.confidence is not None


def test_azure_storage_account_key_has_high_severity():
    secret = "EbydtO7j0zIw6xZ26pBLqzZo4PM5XrS5nspJtUr6wl2l50Tzw9uQYlFciai3Fv8waZE53PoJ5+vA8Z2Eq=="
    text = f"My Azure Storage key is: {secret}"

    req = PromptInspectionRequest(prompt=text, meta=None)
    resp = analyze_prompt(req)

    finding = _get_finding(resp.findings, "secret_azure_storage_account_key")
    assert finding is not None
    assert finding.severity == "high"
    assert finding.confidence is not None


def test_basic_auth_credentials_has_high_severity():
    secret = "Authorization: Basic dXNlcjpwYXNzd29yZA=="
    text = f"My basic auth header is: {secret}"

    req = PromptInspectionRequest(prompt=text, meta=None)
    resp = analyze_prompt(req)

    finding = _get_finding(resp.findings, "secret_basic_auth_credentials")
    assert finding is not None
    assert finding.severity == "high"
    assert finding.confidence is not None


def test_cloudant_credentials_has_high_severity():
    secret = "https://username:password@account.cloudant.com"
    text = f"My Cloudant URL is: {secret}"

    req = PromptInspectionRequest(prompt=text, meta=None)
    resp = analyze_prompt(req)

    finding = _get_finding(resp.findings, "secret_cloudant_credentials")
    assert finding is not None
    assert finding.severity == "high"
    assert finding.confidence is not None


def test_discord_bot_token_has_high_severity():
    secret = "MTEyMzQ1Njc4OTAxMjM0NTY3ODkwMTIzNA.ABCDEF.GHIJKLMNOPQRSTUVWXYZabcd"
    text = f"My Discord bot token is: {secret}"

    req = PromptInspectionRequest(prompt=text, meta=None)
    resp = analyze_prompt(req)

    finding = _get_finding(resp.findings, "secret_discord_bot_token")
    assert finding is not None
    assert finding.severity == "high"
    assert finding.confidence is not None


def test_github_token_has_high_severity():
    secret = "ghp_111111111111111111111111111111111111"
    text = f"My GitHub token is: {secret}"

    req = PromptInspectionRequest(prompt=text, meta=None)
    resp = analyze_prompt(req)

    finding = _get_finding(resp.findings, "secret_github_token")
    assert finding is not None
    assert finding.severity == "high"
    assert finding.confidence is not None


def test_gitlab_token_has_high_severity():
    secret = "glpat-1234567890abcdef1234567890abcdef"
    text = f"My GitLab token is: {secret}"

    req = PromptInspectionRequest(prompt=text, meta=None)
    resp = analyze_prompt(req)

    finding = _get_finding(resp.findings, "secret_gitlab_token")
    assert finding is not None
    assert finding.severity == "high"
    assert finding.confidence is not None


def test_ibm_cloud_iam_key_has_high_severity():
    secret = "ABCD1234efgh5678IJKL9012mnop3456QRST7890uvwx"
    text = f"My IBM Cloud IAM key is: {secret}"

    req = PromptInspectionRequest(prompt=text, meta=None)
    resp = analyze_prompt(req)

    finding = _get_finding(resp.findings, "secret_ibm_cloud_iam_key")
    assert finding is not None
    assert finding.severity == "high"
    assert finding.confidence is not None


def test_ibm_cos_hmac_credentials_has_high_severity():
    secret = "cos_hmac:ABCD1234efgh5678IJKL9012mnop3456"
    text = f"My IBM COS HMAC creds are: {secret}"

    req = PromptInspectionRequest(prompt=text, meta=None)
    resp = analyze_prompt(req)

    finding = _get_finding(resp.findings, "secret_ibm_cos_hmac_credentials")
    assert finding is not None
    assert finding.severity == "high"
    assert finding.confidence is not None


def test_public_ip_address_has_high_severity():
    secret = "8.8.8.8"
    text = f"My public IP is: {secret}"

    req = PromptInspectionRequest(prompt=text, meta=None)
    resp = analyze_prompt(req)

    finding = _get_finding(resp.findings, "secret_public_ip_address")
    assert finding is not None
    assert finding.severity == "high"
    assert finding.confidence is not None


def test_jwt_has_high_severity():
    secret = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJzdWIiOiIxMjM0NTY3ODkwIn0."
        "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    )
    text = f"My JWT is: {secret}"

    req = PromptInspectionRequest(prompt=text, meta=None)
    resp = analyze_prompt(req)

    finding = _get_finding(resp.findings, "secret_jwt")
    assert finding is not None
    assert finding.severity == "high"
    assert finding.confidence is not None


def test_mailchimp_access_key_has_high_severity():
    secret = "1234567890abcdef1234567890abcdef-us1"
    text = f"My Mailchimp key is: {secret}"

    req = PromptInspectionRequest(prompt=text, meta=None)
    resp = analyze_prompt(req)

    finding = _get_finding(resp.findings, "secret_mailchimp_access_key")
    assert finding is not None
    assert finding.severity == "high"
    assert finding.confidence is not None


def test_npm_token_has_high_severity():
    secret = "npm_1234567890abcdefghijklmnopqrstuvwxyz"
    text = f"My NPM token is: {secret}"

    req = PromptInspectionRequest(prompt=text, meta=None)
    resp = analyze_prompt(req)

    finding = _get_finding(resp.findings, "secret_npm_token")
    assert finding is not None
    assert finding.severity == "high"
    assert finding.confidence is not None


def test_openai_token_has_high_severity():
    secret = "sk-1234567890abcdefghijklmnopqrstuvwx"
    text = f"My OpenAI token is: {secret}"

    req = PromptInspectionRequest(prompt=text, meta=None)
    resp = analyze_prompt(req)

    finding = _get_finding(resp.findings, "secret_openai_token")
    assert finding is not None
    assert finding.severity == "high"
    assert finding.confidence is not None


def test_private_key_has_high_severity():
    secret = (
        "-----BEGIN PRIVATE KEY-----\n"
        "MIIEvQIBADANBgkqhkiG9w0BAQEFAASC...\n"
        "-----END PRIVATE KEY-----"
    )
    text = f"My private key is: {secret}"

    req = PromptInspectionRequest(prompt=text, meta=None)
    resp = analyze_prompt(req)

    finding = _get_finding(resp.findings, "secret_private_key")
    assert finding is not None
    assert finding.severity == "high"
    assert finding.confidence is not None


def test_pypi_token_has_high_severity():
    secret = "pypi-AgENdGVzdF90b2tlbl9hYmNkZWYxMjM0NTY3ODkw"
    text = f"My PyPI token is: {secret}"

    req = PromptInspectionRequest(prompt=text, meta=None)
    resp = analyze_prompt(req)

    finding = _get_finding(resp.findings, "secret_pypi_token")
    assert finding is not None
    assert finding.severity == "high"
    assert finding.confidence is not None


def test_sendgrid_api_key_has_high_severity():
    secret = "SG.abc123def456ghi789jkl012mno345pqr678stu901vwx234yz"
    text = f"My SendGrid API key is: {secret}"

    req = PromptInspectionRequest(prompt=text, meta=None)
    resp = analyze_prompt(req)

    finding = _get_finding(resp.findings, "secret_sendgrid_api_key")
    assert finding is not None
    assert finding.severity == "high"
    assert finding.confidence is not None


def test_slack_token_has_high_severity():
    secret = "xoxb-123456789012-123456789012-abcdefghijklmnopqrstuvwx"
    text = f"My Slack token is: {secret}"

    req = PromptInspectionRequest(prompt=text, meta=None)
    resp = analyze_prompt(req)

    finding = _get_finding(resp.findings, "secret_slack_token")
    assert finding is not None
    assert finding.severity == "high"
    assert finding.confidence is not None


def test_softlayer_credentials_has_high_severity():
    secret = "SL123456:abcdef1234567890abcdef1234567890"
    text = f"My SoftLayer credentials are: {secret}"

    req = PromptInspectionRequest(prompt=text, meta=None)
    resp = analyze_prompt(req)

    finding = _get_finding(resp.findings, "secret_softlayer_credentials")
    assert finding is not None
    assert finding.severity == "high"
    assert finding.confidence is not None


def test_square_oauth_secret_has_high_severity():
    secret = "sq0csp-1234567890abcdefghijklmnopqrstuv"
    text = f"My Square OAuth secret is: {secret}"

    req = PromptInspectionRequest(prompt=text, meta=None)
    resp = analyze_prompt(req)

    finding = _get_finding(resp.findings, "secret_square_oauth_secret")
    assert finding is not None
    assert finding.severity == "high"
    assert finding.confidence is not None


def test_stripe_access_key_has_high_severity():
    secret = "sk_live_4eC39HqLyjWDarjtT1zdp7dc"
    text = f"My Stripe access key is: {secret}"

    req = PromptInspectionRequest(prompt=text, meta=None)
    resp = analyze_prompt(req)

    finding = _get_finding(resp.findings, "secret_stripe_access_key")
    assert finding is not None
    assert finding.severity == "high"
    assert finding.confidence is not None


def test_telegram_bot_token_has_high_severity():
    secret = "123456789:ABCdefGhIjklmnOPQRstuVWxyZ1234567890"
    text = f"My Telegram bot token is: {secret}"

    req = PromptInspectionRequest(prompt=text, meta=None)
    resp = analyze_prompt(req)

    finding = _get_finding(resp.findings, "secret_telegram_bot_token")
    assert finding is not None
    assert finding.severity == "high"
    assert finding.confidence is not None


def test_twilio_api_key_has_high_severity():
    secret = "SK1234567890abcdef1234567890abcdef"
    text = f"My Twilio API key is: {secret}"

    req = PromptInspectionRequest(prompt=text, meta=None)
    resp = analyze_prompt(req)

    finding = _get_finding(resp.findings, "secret_twilio_api_key")
    assert finding is not None
    assert finding.severity == "high"
    assert finding.confidence is not None
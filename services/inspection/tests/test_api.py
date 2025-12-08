from __future__ import annotations

from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_inspect_endpoint_without_findings_in_prompt():
    response = client.post("/inspect", json={"prompt": "Hello world"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["findings"], list)
    assert data["findings"] == []

def test_inspect_endpoint_with_findings_in_prompt():
    resp = client.post("/inspect", json={"prompt": "Here is my key: AKIA1234567890ABCDEF", "meta": None})
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data["findings"], list)
    types = {f["type"] for f in data["findings"]}
    assert "secret_aws_access_key" in types
    secret_finding = next(f for f in data["findings"] if f["type"] == "secret_aws_access_key")
    assert secret_finding["severity"] == "high"
    assert secret_finding["confidence"] is not None
    assert 0.0 <= secret_finding["confidence"] <= 1.0

from __future__ import annotations

from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_inspect_endpoint_allows_normal_prompt():
    response = client.post("/inspect", json={"prompt": "Hello world"})
    assert response.status_code == 200
    data = response.json()
    assert data["isAllowed"] is True
    assert isinstance(data["findings"], list)

def test_inspect_endpoint_blocks_prompt():
    resp = client.post("/inspect", json={"prompt": "Here is my key: AKIA1234567890ABCDEF", "meta": None})
    assert resp.status_code == 200
    data = resp.json()
    assert data["isAllowed"] is False
    assert isinstance(data["findings"], list)
    types = {f["type"] for f in data["findings"]}
    assert "secret_aws_access_key" in types
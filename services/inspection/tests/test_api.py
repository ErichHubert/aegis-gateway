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
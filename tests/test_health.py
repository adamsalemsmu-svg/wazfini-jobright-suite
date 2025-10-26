from __future__ import annotations

from fastapi.testclient import TestClient


def test_healthz(client: TestClient) -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_readyz(client: TestClient) -> None:
    response = client.get("/readyz")
    assert response.status_code == 200
    assert response.json() == {"ok": True}

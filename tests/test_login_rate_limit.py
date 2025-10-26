from __future__ import annotations

from fastapi.testclient import TestClient


def test_login_rate_limit_triggers_lockout(client: TestClient) -> None:
    payload = {"email": "unknown@example.com", "password": "WrongPass!"}
    headers = {"x-forwarded-for": "198.51.100.10"}

    for attempt in range(5):
        response = client.post("/auth/login", json=payload, headers=headers)
        assert response.status_code == 401

    response = client.post("/auth/login", json=payload, headers=headers)
    assert response.status_code == 429
    assert response.headers.get("Retry-After") is not None

from __future__ import annotations

from fastapi.testclient import TestClient


def test_refresh_rotation_and_reuse_detection(client: TestClient, create_user) -> None:
    email = "rotator@example.com"
    password = "StrongPass!123"
    create_user(email=email, password=password)

    login_resp = client.post("/auth/login", json={"email": email, "password": password})
    assert login_resp.status_code == 200
    first_tokens = login_resp.json()
    first_refresh = first_tokens["refresh_token"]

    refresh_resp = client.post("/auth/refresh", json={"refresh_token": first_refresh})
    assert refresh_resp.status_code == 200
    rotated_tokens = refresh_resp.json()
    rotated_refresh = rotated_tokens["refresh_token"]
    assert rotated_refresh != first_refresh

    reuse_resp = client.post("/auth/refresh", json={"refresh_token": first_refresh})
    assert reuse_resp.status_code == 401

    second_attempt = client.post(
        "/auth/refresh", json={"refresh_token": rotated_refresh}
    )
    assert second_attempt.status_code == 401

    relogin = client.post("/auth/login", json={"email": email, "password": password})
    assert relogin.status_code == 200

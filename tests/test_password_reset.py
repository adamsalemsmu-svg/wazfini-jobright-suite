from __future__ import annotations

from fastapi.testclient import TestClient


def _run(redis_client, coro):
    loop = getattr(redis_client, "testing_loop")
    return loop.run_until_complete(coro)


def _get_reset_token(redis_client) -> str:
    keys = _run(redis_client, redis_client.keys("pwdreset:*"))
    assert keys, "password reset token not stored"
    key = next((k for k in keys if not k.startswith("pwdreset:attempts:")), None)
    assert key is not None, "password reset token key missing"
    return key.split(":", 1)[1]


def test_password_reset_flow(client: TestClient, create_user, redis_client) -> None:
    email = "reset@example.com"
    old_password = "OldPass!123"
    new_password = "BrandNewPass!456"
    create_user(email=email, password=old_password)

    request_resp = client.post("/auth/password-reset/request", json={"email": email})
    assert request_resp.status_code == 200

    token = _get_reset_token(redis_client)

    confirm_resp = client.post(
        "/auth/password-reset/confirm",
        json={"token": token, "new_password": new_password},
    )
    assert confirm_resp.status_code == 200

    assert _run(redis_client, redis_client.exists(f"pwdreset:{token}")) == 0

    reuse_resp = client.post(
        "/auth/password-reset/confirm",
        json={"token": token, "new_password": new_password},
    )
    assert reuse_resp.status_code == 400

    old_login = client.post(
        "/auth/login", json={"email": email, "password": old_password}
    )
    assert old_login.status_code == 401

    new_login = client.post(
        "/auth/login", json={"email": email, "password": new_password}
    )
    assert new_login.status_code == 200

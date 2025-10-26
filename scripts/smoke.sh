#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-${1:-}}"
if [[ -z "${BASE_URL}" ]]; then
  echo "Usage: BASE_URL=<url> $0" >&2
  exit 1
fi

BASE_URL="${BASE_URL%/}"

>&2 echo "[smoke] Checking health endpoints at ${BASE_URL}"
curl -fsS "${BASE_URL}/healthz" >/dev/null
curl -fsS "${BASE_URL}/openapi.json" >/dev/null

>&2 echo "[smoke] Seeding demo data"
PYTHONPATH="backend" python scripts/seed.py >/dev/null

>&2 echo "[smoke] Running authentication flow"
export BASE_URL
python - <<'PY'
import json
import os
import sys
import requests

base_url = os.environ.get("BASE_URL")
if not base_url:
    print("BASE_URL not set", file=sys.stderr)
    sys.exit(1)

session = requests.Session()


def dump_resp(resp: requests.Response) -> None:
    print("RESPONSE STATUS:", resp.status_code)
    print("RESPONSE HEADERS:", json.dumps(dict(resp.headers), indent=2))
    try:
        print("RESPONSE BODY:", resp.json())
    except Exception:
        print("RESPONSE TEXT:", resp.text[:10000])


def post(
    path: str,
    payload: dict[str, str],
    expected_status: int,
    *,
    headers: dict[str, str] | None = None,
) -> requests.Response:
    url = f"{base_url}{path}"
    resp = session.post(url, json=payload, headers=headers, timeout=30)
    print(f"POST {path} -> {resp.status_code}")
    if resp.status_code != expected_status:
        dump_resp(resp)
        forwarded_for = headers.get("x-forwarded-for") if headers else ""
        curl_cmd = (
            "curl -v -X POST "
            f"{url} "
            "-H 'Content-Type: application/json' "
            f"-H 'x-forwarded-for: {forwarded_for}' "
            f"-d '{json.dumps(payload)}'"
        )
        print("REPRODUCE WITH:", curl_cmd)
        sys.exit(1)
    return resp

fail_headers = {"x-forwarded-for": "198.51.100.10"}

for attempt in range(1, 7):
    status = 401 if attempt <= 5 else 429
    post(
        "/auth/login",
        {"email": "unknown@wazifni.ai", "password": "WrongPass!123"},
        status,
        headers=fail_headers,
    )

login_headers = {"x-forwarded-for": "203.0.113.42"}

login_resp = post(
    "/auth/login",
    {"email": "demo@wazifni.ai", "password": "ChangeMe!2024"},
    200,
    headers=login_headers,
)
tokens = login_resp.json()
refresh_initial = tokens["refresh_token"]

refresh_resp = post("/auth/refresh", {"refresh_token": refresh_initial}, 200, headers=login_headers)
refresh_rotated = refresh_resp.json()["refresh_token"]

reuse_resp = session.post(
    f"{base_url}/auth/refresh",
    json={"refresh_token": refresh_initial},
    headers=login_headers,
    timeout=15,
)
print(f"POST /auth/refresh (reuse) -> {reuse_resp.status_code}")
if reuse_resp.status_code != 401:
    print(reuse_resp.text)
    sys.exit(1)

final_resp = session.post(
    f"{base_url}/auth/refresh",
    json={"refresh_token": refresh_rotated},
    headers=login_headers,
    timeout=15,
)
print(f"POST /auth/refresh (rotated token after reuse) -> {final_resp.status_code}")
if final_resp.status_code != 401:
    print(final_resp.text)
    sys.exit(1)
PY

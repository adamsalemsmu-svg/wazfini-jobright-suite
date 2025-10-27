#!/usr/bin/env bash
set -euo pipefail

# Expect secrets injected by workflow or via env/argument
BASE_URL="${BASE_URL:-${1:-}}"
EMAIL="${SMOKE_USER_EMAIL:-${SMOKE_USER_EMAIL:-}}"
PASSWORD="${SMOKE_USER_PASSWORD:-${SMOKE_USER_PASSWORD:-}}"

if [[ -z "${BASE_URL}" ]]; then
    echo "Usage: BASE_URL=<url> $0" >&2
    exit 1
fi
if [[ -z "${EMAIL}" ]] || [[ -z "${PASSWORD}" ]]; then
    echo "SMOKE_USER_EMAIL and SMOKE_USER_PASSWORD must be provided as environment variables" >&2
    exit 1
fi

BASE_URL="${BASE_URL%/}"
LOGIN_URL="${BASE_URL}/auth/login"

MAX_RETRIES=3
SLEEP_BASE=2

echo "Smoke: login to ${LOGIN_URL} as ${EMAIL}"

attempt=0
while [ $attempt -lt $MAX_RETRIES ]; do
    attempt=$((attempt+1))
    echo "Attempt ${attempt}/${MAX_RETRIES}..."

    response=$(curl -s -w '\n%{http_code}' -X POST "${LOGIN_URL}" \
        -H "Content-Type: application/json" \
        -d "{\"email\":\"${EMAIL}\",\"password\":\"${PASSWORD}\"}" \
        -H "x-forwarded-for: 198.51.100.10" || true)

    http_code=$(echo "${response}" | tail -n1)
    body=$(echo "${response}" | sed '$d')

    echo "HTTP ${http_code} - Response: ${body}"

    if [ "${http_code}" -ge 200 ] && [ "${http_code}" -lt 300 ]; then
        echo "Smoke: login succeeded."
        exit 0
    fi

    if [ "${http_code}" -eq 401 ] || [ "${http_code}" -eq 403 ]; then
        echo "Smoke failed: invalid credentials or forbidden (HTTP ${http_code})."
        echo "Response body: ${body}"
        exit 1
    fi

    if [ "${http_code}" -eq 429 ] || [ "${http_code}" -ge 500 ]; then
        if [ ${attempt} -lt ${MAX_RETRIES} ]; then
            sleep_time=$((SLEEP_BASE ** attempt))
            echo "Transient error (HTTP ${http_code}). Retrying after ${sleep_time}s..."
            sleep ${sleep_time}
            continue
        else
            echo "Smoke failed after ${MAX_RETRIES} attempts (HTTP ${http_code})."
            echo "Response body: ${body}"
            exit 1
        fi
    fi

    echo "Unexpected response (HTTP ${http_code}). Failing smoke test."
    echo "Response body: ${body}"
    exit 1
done

echo "Smoke test failed unexpectedly."
exit 1

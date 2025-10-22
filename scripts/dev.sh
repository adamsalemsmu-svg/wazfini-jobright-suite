#!/usr/bin/env bash
set -euo pipefail
source backend/.venv/bin/activate || true
( cd backend && uvicorn app.main:app --reload --port 8000 ) &
( cd frontend && npm run dev ) &
wait

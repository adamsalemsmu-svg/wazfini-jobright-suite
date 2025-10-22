#!/usr/bin/env bash
set -euo pipefail
source backend/.venv/bin/activate || true
ruff . || true
black --check .
mypy backend/app || true
pytest -q

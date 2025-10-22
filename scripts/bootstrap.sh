#!/usr/bin/env bash
set -euo pipefail
python3 -m venv backend/.venv || true
source backend/.venv/bin/activate
python -m pip install -U pip
if [ -f backend/requirements.txt ]; then pip install -r backend/requirements.txt; fi
pip install "pydantic[email]" email-validator pre-commit pytest ruff black mypy pip-audit
pushd frontend >/dev/null || exit 0
npm ci || npm install
popd >/dev/null || true
pre-commit install || true
echo "Bootstrap complete."

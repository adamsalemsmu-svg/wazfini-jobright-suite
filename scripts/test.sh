#!/usr/bin/env bash
set -euo pipefail
source backend/.venv/bin/activate || true
pytest -q

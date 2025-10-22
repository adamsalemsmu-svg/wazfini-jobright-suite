Param()

$ErrorActionPreference = "Stop"
if (!(Test-Path "backend\.venv")) { python -m venv backend\.venv }
& backend\.venv\Scripts\Activate.ps1
python -m pip install -U pip
if (Test-Path "backend\requirements.txt") { pip install -r backend\requirements.txt }
pip install "pydantic[email]" email-validator pre-commit pytest ruff black mypy pip-audit
if (Test-Path "frontend\package-lock.json") {
  cd frontend; npm ci; cd ..
} elseif (Test-Path "frontend\package.json") {
  cd frontend; npm install; cd ..
}
pre-commit install
Write-Host "Bootstrap complete."

& backend\.venv\Scripts\Activate.ps1
ruff .
black --check .
mypy backend/app
pytest -q

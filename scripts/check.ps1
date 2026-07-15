$ErrorActionPreference = "Stop"
python -m pytest -q
python -m ruff check .
python -m compileall -q app.py opsready_lab

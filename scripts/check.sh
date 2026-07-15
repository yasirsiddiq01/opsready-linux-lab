#!/usr/bin/env bash
set -euo pipefail
python -m pytest -q
python -m ruff check .
python -m compileall -q app.py opsready_lab

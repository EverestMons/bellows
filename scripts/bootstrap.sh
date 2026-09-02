#!/usr/bin/env bash
# bellows bootstrap — thread 84 / MACHINE_SETUP.md §2 (plan bellows-bootstrap, 2026-09-02).
# Creates .venv with the newest python3.12 on PATH (else python3), installs requirements.txt,
# and runs the suite once. Idempotent: an existing .venv is reused. Run from anywhere.
# The daemon inherits the DASHBOARD's interpreter: start it as .venv/bin/python dashboard.py.
set -euo pipefail
cd "$(dirname "$0")/.."
PY="$(command -v python3.12 || command -v python3)"
echo "interpreter: $PY ($("$PY" --version 2>&1))"
[ -x .venv/bin/python ] || "$PY" -m venv .venv
.venv/bin/python -m pip install -q -r requirements.txt
echo "venv: $(pwd)/.venv ($(.venv/bin/python --version 2>&1))"
exec .venv/bin/python -m pytest tests -q -p no:cacheprovider

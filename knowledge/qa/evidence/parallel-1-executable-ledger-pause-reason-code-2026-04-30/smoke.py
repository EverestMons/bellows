import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from unittest.mock import patch
from pathlib import Path
import tempfile

import verdict

with tempfile.TemporaryDirectory() as tmp:
    with patch.object(verdict, "VERDICTS_DIR", Path(tmp) / "verdicts"):
        verdict.log_to_ledger(
            plan_path="/tmp/test-plan.md",
            step_number=1,
            gate_result={"failures": [], "files_changed": []},
            verdict="continue",
            reason="smoke test",
            pause_reason_code="qa_checkpoint",
        )
        ledger_path = Path(tmp) / "verdicts" / "ledger.jsonl"
        last_line = ledger_path.read_text().strip().splitlines()[-1]
        entry = json.loads(last_line)
        if entry["pause_reason_code"] == "qa_checkpoint":
            print(f"SUCCESS — pause_reason_code round-trips correctly: {entry}")
        else:
            print(f"FAILURE — expected pause_reason_code='qa_checkpoint', got: {entry}")
            sys.exit(1)

"""E2E test: verify total_steps=None raises ValueError."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
import tempfile
from pathlib import Path
from unittest.mock import patch
import verdict

with tempfile.TemporaryDirectory() as tmp:
    with patch.object(verdict, "VERDICTS_DIR", Path(tmp) / "verdicts"):
        gate_result = {"passed": True, "failures": [], "files_changed": []}
        try:
            verdict.post_verdict_request(
                "/fake/plan.md", "/fake/project", 1, "/fake/logs",
                gate_result, pause_reason="auto_close_disabled", total_steps=None
            )
            print("FAIL: no ValueError raised")
        except ValueError as e:
            if "total_steps must be an integer" in str(e):
                print(f"PASS: ValueError raised — {e}")
            else:
                print(f"FAIL: wrong ValueError message — {e}")
        except Exception as e:
            print(f"FAIL: unexpected exception — {type(e).__name__}: {e}")

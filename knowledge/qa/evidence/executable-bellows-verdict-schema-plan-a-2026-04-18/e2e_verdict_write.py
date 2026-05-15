"""E2E smoke test: verify all four new verdict fields are written correctly."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
import tempfile
from pathlib import Path
from unittest.mock import patch
import verdict

with tempfile.TemporaryDirectory() as tmp:
    with patch.object(verdict, "VERDICTS_DIR", Path(tmp) / "verdicts"):
        gate_result = {"passed": True, "failures": [], "files_changed": []}
        path = verdict.post_verdict_request(
            "/fake/plan.md", "/fake/project", 1, "/fake/logs",
            gate_result, pause_reason="auto_close_disabled", total_steps=1
        )
        content = open(path).read()

        checks = [
            ("**Project:** /fake/project", content.count("**Project:** /fake/project") == 1),
            ("**Pause Reason Code:** auto_close_disabled", content.count("**Pause Reason Code:** auto_close_disabled") == 1),
            ("**Gate Result Passed:** True", content.count("**Gate Result Passed:** True") == 1),
            ("**Total Steps:** 1", content.count("**Total Steps:** 1") == 1),
        ]

        all_pass = True
        for field, ok in checks:
            status = "PASS" if ok else "FAIL"
            if not ok:
                all_pass = False
            print(f"  {status}: {field}")

        print()
        print("RESULT: PASS" if all_pass else "RESULT: FAIL")
        os.unlink(path)

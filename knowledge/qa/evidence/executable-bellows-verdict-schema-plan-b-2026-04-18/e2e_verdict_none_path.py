"""E2E test: verdict request file contains 'Deposit: none' when no deposit found."""
import sys
import os
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
import verdict

with tempfile.TemporaryDirectory() as tmpdir:
    original_dir = verdict.VERDICTS_DIR
    verdict.VERDICTS_DIR = verdict.Path(tmpdir) / "verdicts"

    step_text = "This step has no deposits. Just commits code."
    gate_result = {"passed": True, "failures": [], "files_changed": []}

    result_path = verdict.post_verdict_request(
        plan_path="/tmp/test-plan.md",
        project_path="/tmp/test-project",
        step_number=1,
        log_path="/tmp/logs",
        gate_result=gate_result,
        pause_reason="qa_checkpoint",
        total_steps=2,
        step_text=step_text,
    )

    content = open(result_path).read()

    expected_line = "**Deposit:** none"
    count = content.count(expected_line)
    assert count == 1, f"Expected '**Deposit:** none' exactly once, found {count} times"

    verdict.VERDICTS_DIR = original_dir

print("PASS — Deposit field correctly shows 'none' when no deposit found")

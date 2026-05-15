"""E2E test: verdict request file contains Deposit field with extracted path."""
import sys
import os
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
import verdict

# Create temp dir structure for verdict output
with tempfile.TemporaryDirectory() as tmpdir:
    # Monkey-patch VERDICTS_DIR to use temp
    original_dir = verdict.VERDICTS_DIR
    verdict.VERDICTS_DIR = verdict.Path(tmpdir) / "verdicts"

    step_text = """## STEP 1 — DEV
Some instructions here.
**Deposit findings** to `bellows/knowledge/research/smoke-test.md`
More instructions after.
"""
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

    # Assert Deposit field has the extracted path
    expected_line = "**Deposit:** bellows/knowledge/research/smoke-test.md"
    assert expected_line in content, f"Expected '{expected_line}' in verdict file, got:\n{content}"
    assert "**Deposit:** none" not in content, "Found '**Deposit:** none' — extraction failed"

    # Restore
    verdict.VERDICTS_DIR = original_dir

print("PASS — Deposit field correctly populated with extracted path")

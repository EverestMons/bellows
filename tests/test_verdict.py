import json
import os
import sys
import tempfile
from unittest.mock import patch, MagicMock
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import verdict
import notifier


def test_extract_step_text_from_plan_ignores_in_fence_headers():
    """Regression: in-fence ## STEP N must not be returned as the real step text."""
    fixture = (
        "## STEP 1 — Real\n"
        "\n"
        "```markdown\n"
        "## STEP 2 — Bellows QA\n"
        "Example.\n"
        "```\n"
        "\n"
        "## STEP 2 — Developer\n"
        "\n"
        "Real step 2.\n"
    )
    result = verdict._extract_step_text_from_plan(fixture, 2)
    assert result is not None
    assert "Developer" in result
    assert "Bellows QA" not in result


def test_extract_step_text_from_plan_ignores_inline_code_references():
    """Regression: inline `## STEP N` in single backticks must not be matched as a real step header."""
    fixture = (
        "## STEP 1 — Developer\n"
        "\n"
        "The prior step references `## STEP 2` and also `## STEP 2 — QA` inline.\n"
        "These are documentation references, not real headers.\n"
        "\n"
        "## STEP 2 — Bellows QA\n"
        "\n"
        "Real step 2 body.\n"
    )
    result = verdict._extract_step_text_from_plan(fixture, 2)
    assert result is not None
    assert "Bellows QA" in result
    assert "documentation references" not in result


def test_post_verdict_request_creates_file():
    with tempfile.TemporaryDirectory() as tmp:
        with patch.object(verdict, "VERDICTS_DIR", Path(tmp) / "verdicts"):
            gate_result = {
                "passed": False,
                "failures": [{"gate": "receipt_status", "evidence": "Blocked"}],
                "is_qa_step": False,
                "files_changed": ["gates.py"],
            }
            path = verdict.post_verdict_request(
                "/tmp/plans/in-progress-executable-test-2026-04-16.md",
                "/tmp/project", 1, "/tmp/logs", gate_result, pause_reason="gate_failure", total_steps=2
            )
            assert os.path.isfile(path)
            content = open(path).read()
            assert "receipt_status" in content
            assert "Blocked" in content
            assert "gates.py" in content


def test_check_verdict_not_found():
    with tempfile.TemporaryDirectory() as tmp:
        with patch.object(verdict, "VERDICTS_DIR", Path(tmp) / "verdicts"):
            result = verdict.check_verdict("test-plan", 1)
            assert result["found"] is False


def test_check_verdict_continue():
    with tempfile.TemporaryDirectory() as tmp:
        verdicts_dir = Path(tmp) / "verdicts"
        resolved_dir = verdicts_dir / "resolved"
        resolved_dir.mkdir(parents=True)
        verdict_file = resolved_dir / "verdict-test-plan-step-1.md"
        verdict_file.write_text("verdict: continue\nAll gates look good after manual review.")
        with patch.object(verdict, "VERDICTS_DIR", verdicts_dir):
            result = verdict.check_verdict("test-plan", 1)
            assert result["found"] is True
            assert result["verdict"] == "continue"
            assert "manual review" in result["reason"]


def test_check_verdict_stop():
    with tempfile.TemporaryDirectory() as tmp:
        verdicts_dir = Path(tmp) / "verdicts"
        resolved_dir = verdicts_dir / "resolved"
        resolved_dir.mkdir(parents=True)
        verdict_file = resolved_dir / "verdict-test-plan-step-2.md"
        verdict_file.write_text("verdict: stop\nScope violation is too severe.")
        with patch.object(verdict, "VERDICTS_DIR", verdicts_dir):
            result = verdict.check_verdict("test-plan", 2)
            assert result["found"] is True
            assert result["verdict"] == "stop"


def _make_gate_result(passed=True, failures=None, is_qa=False, verdict_requested=False, files_changed=None):
    return {
        "passed": passed,
        "failures": failures or [],
        "is_qa_step": is_qa,
        "verdict_requested": {"requested": verdict_requested},
        "files_changed": files_changed or [],
    }


def test_pause_reason_gate_failure_renders_gate_failures_section():
    with tempfile.TemporaryDirectory() as tmp:
        with patch.object(verdict, "VERDICTS_DIR", Path(tmp) / "verdicts"):
            gate_result = _make_gate_result(
                passed=False,
                failures=[{"gate": "scope_check", "evidence": "File outside scope"}],
            )
            path = verdict.post_verdict_request(
                "/tmp/plan.md", "/tmp/project", 1, "/tmp/logs", gate_result, pause_reason="gate_failure", total_steps=2
            )
            content = open(path).read()
            assert "**Pause Reason:** Gate failure" in content
            assert "## Gate Failures" in content
            assert "scope_check" in content
            assert "File outside scope" in content
            assert "## Pause Reason" not in content


def test_pause_reason_qa_checkpoint():
    with tempfile.TemporaryDirectory() as tmp:
        with patch.object(verdict, "VERDICTS_DIR", Path(tmp) / "verdicts"):
            gate_result = _make_gate_result(passed=True, is_qa=True)
            path = verdict.post_verdict_request(
                "/tmp/plan.md", "/tmp/project", 2, "/tmp/logs", gate_result, pause_reason="qa_checkpoint", total_steps=3
            )
            content = open(path).read()
            assert "**Pause Reason:** QA checkpoint" in content
            assert "## Pause Reason" in content
            assert "QA checkpoint" in content
            assert "## Gate Failures" not in content


def test_pause_reason_agent_verdict_request():
    with tempfile.TemporaryDirectory() as tmp:
        with patch.object(verdict, "VERDICTS_DIR", Path(tmp) / "verdicts"):
            gate_result = _make_gate_result(passed=True, verdict_requested=True)
            path = verdict.post_verdict_request(
                "/tmp/plan.md", "/tmp/project", 2, "/tmp/logs", gate_result, pause_reason="agent_verdict_request", total_steps=3
            )
            content = open(path).read()
            assert "**Pause Reason:** Agent verdict request" in content
            assert "## Pause Reason" in content
            assert "verdict-request file" in content
            assert "## Gate Failures" not in content


def test_pause_reason_header_pause():
    with tempfile.TemporaryDirectory() as tmp:
        with patch.object(verdict, "VERDICTS_DIR", Path(tmp) / "verdicts"):
            gate_result = _make_gate_result(passed=True)
            path = verdict.post_verdict_request(
                "/tmp/plan.md", "/tmp/project", 1, "/tmp/logs", gate_result, pause_reason="header_pause", total_steps=2
            )
            content = open(path).read()
            assert "**Pause Reason:** Header pause (pause_for_verdict)" in content
            assert "## Pause Reason" in content
            assert "pause_for_verdict" in content
            assert "## Gate Failures" not in content


def test_pause_reason_auto_close_disabled():
    with tempfile.TemporaryDirectory() as tmp:
        with patch.object(verdict, "VERDICTS_DIR", Path(tmp) / "verdicts"):
            gate_result = _make_gate_result(passed=True)
            path = verdict.post_verdict_request(
                "/tmp/plan.md", "/tmp/project", 1, "/tmp/logs", gate_result, pause_reason="auto_close_disabled", total_steps=2
            )
            content = open(path).read()
            assert "**Pause Reason:** Auto-close disabled" in content
            assert "## Pause Reason" in content
            assert "Auto-close is disabled" in content
            assert "## Gate Failures" not in content


def test_old_fallback_string_never_appears():
    with tempfile.TemporaryDirectory() as tmp:
        with patch.object(verdict, "VERDICTS_DIR", Path(tmp) / "verdicts"):
            for reason in ["gate_failure", "qa_checkpoint", "agent_verdict_request", "header_pause", "auto_close_disabled"]:
                gate_result = _make_gate_result(passed=(reason != "gate_failure"))
                path = verdict.post_verdict_request(
                    "/tmp/plan.md", "/tmp/project", 1, "/tmp/logs", gate_result, pause_reason=reason, total_steps=2
                )
                content = open(path).read()
                assert "None (QA checkpoint — all gates passed)" not in content, \
                    f"Old fallback string found for pause_reason={reason}"


def test_post_verdict_request_handles_worktree_teardown_failure_dict_format():
    """Regression test: worktree teardown failure entries must be dicts, not strings.

    bellows.py appends failure entries to gate_result['failures']. verdict.py's
    post_verdict_request iterates them expecting dicts with 'gate' and 'evidence' keys.
    Plain strings cause 'string indices must be integers' TypeError.
    """
    with tempfile.TemporaryDirectory() as tmp:
        with patch.object(verdict, "VERDICTS_DIR", Path(tmp) / "verdicts"):
            gate_result = {
                "failures": [{"gate": "worktree_teardown", "evidence": "simulated teardown error"}],
                "files_changed": [],
                "passed": False,
                "is_qa_step": False,
            }
            # Must not raise TypeError
            path = verdict.post_verdict_request(
                "/tmp/plans/in-progress-executable-test-worktree-2026-05-03.md",
                "/tmp/project", 1, "/tmp/logs", gate_result,
                pause_reason="gate_failure", total_steps=2
            )
            assert os.path.isfile(path)
            content = open(path).read()
            assert "## Gate Failures" in content
            assert "worktree_teardown" in content
            assert "simulated teardown error" in content


def test_check_verdict_accepts_bare_continue():
    """S3 Fix A: check_verdict must accept bare 'continue' without 'verdict:' prefix."""
    with tempfile.TemporaryDirectory() as tmp:
        verdicts_dir = Path(tmp) / "verdicts"
        resolved_dir = verdicts_dir / "resolved"
        resolved_dir.mkdir(parents=True)
        verdict_file = resolved_dir / "verdict-test-bare-continue-step-1.md"
        verdict_file.write_text("continue\nReason text.")
        with patch.object(verdict, "VERDICTS_DIR", verdicts_dir):
            result = verdict.check_verdict("test-bare-continue", 1)
            assert result["found"] is True
            assert result["verdict"] == "continue"


def test_check_verdict_accepts_bare_stop():
    """S3 Fix A: check_verdict must accept bare 'stop' without 'verdict:' prefix."""
    with tempfile.TemporaryDirectory() as tmp:
        verdicts_dir = Path(tmp) / "verdicts"
        resolved_dir = verdicts_dir / "resolved"
        resolved_dir.mkdir(parents=True)
        verdict_file = resolved_dir / "verdict-test-bare-stop-step-1.md"
        verdict_file.write_text("stop\nReason text.")
        with patch.object(verdict, "VERDICTS_DIR", verdicts_dir):
            result = verdict.check_verdict("test-bare-stop", 1)
            assert result["found"] is True
            assert result["verdict"] == "stop"


def test_check_verdict_still_accepts_prefixed_continue():
    """S3 regression: check_verdict must still accept 'verdict: continue' format."""
    with tempfile.TemporaryDirectory() as tmp:
        verdicts_dir = Path(tmp) / "verdicts"
        resolved_dir = verdicts_dir / "resolved"
        resolved_dir.mkdir(parents=True)
        verdict_file = resolved_dir / "verdict-test-prefixed-step-1.md"
        verdict_file.write_text("verdict: continue\nReason text.")
        with patch.object(verdict, "VERDICTS_DIR", verdicts_dir):
            result = verdict.check_verdict("test-prefixed", 1)
            assert result["found"] is True
            assert result["verdict"] == "continue"


def test_check_verdict_rejects_garbage():
    """S3: check_verdict must reject non-verdict first lines."""
    with tempfile.TemporaryDirectory() as tmp:
        verdicts_dir = Path(tmp) / "verdicts"
        resolved_dir = verdicts_dir / "resolved"
        resolved_dir.mkdir(parents=True)
        verdict_file = resolved_dir / "verdict-test-garbage-step-1.md"
        verdict_file.write_text("random text\nMore text.")
        with patch.object(verdict, "VERDICTS_DIR", verdicts_dir):
            result = verdict.check_verdict("test-garbage", 1)
            assert result["found"] is False


def test_log_to_ledger_appends_json():
    with tempfile.TemporaryDirectory() as tmp:
        with patch.object(verdict, "VERDICTS_DIR", Path(tmp) / "verdicts"):
            gate_result = {
                "failures": [{"gate": "receipt_status", "evidence": "Partial"}],
                "files_changed": ["test.py"],
            }
            verdict.log_to_ledger("/tmp/plan.md", 1, gate_result, "continue", "Reviewed OK")
            verdict.log_to_ledger("/tmp/plan.md", 2, gate_result, "stop", "Bad scope")

            ledger_path = Path(tmp) / "verdicts" / "ledger.jsonl"
            assert ledger_path.exists()
            lines = ledger_path.read_text().strip().splitlines()
            assert len(lines) == 2
            entry1 = json.loads(lines[0])
            assert entry1["step"] == 1
            assert entry1["verdict"] == "continue"
            entry2 = json.loads(lines[1])
            assert entry2["step"] == 2
            assert entry2["verdict"] == "stop"


def test_log_to_ledger_without_pause_reason_code():
    """Legacy behavior: pause_reason_code defaults to None when not provided."""
    with tempfile.TemporaryDirectory() as tmp:
        with patch.object(verdict, "VERDICTS_DIR", Path(tmp) / "verdicts"):
            gate_result = {"failures": [], "files_changed": []}
            verdict.log_to_ledger("/tmp/plan.md", 1, gate_result, "continue", "OK")

            ledger_path = Path(tmp) / "verdicts" / "ledger.jsonl"
            lines = ledger_path.read_text().strip().splitlines()
            assert len(lines) == 1
            entry = json.loads(lines[0])
            assert "pause_reason_code" in entry
            assert entry["pause_reason_code"] is None


def test_log_to_ledger_with_pause_reason_code_qa_checkpoint():
    """Explicit pause_reason_code is persisted in the JSONL entry."""
    with tempfile.TemporaryDirectory() as tmp:
        with patch.object(verdict, "VERDICTS_DIR", Path(tmp) / "verdicts"):
            gate_result = {"failures": [], "files_changed": []}
            verdict.log_to_ledger("/tmp/plan.md", 2, gate_result, "continue", "QA passed",
                                  pause_reason_code="qa_checkpoint")

            ledger_path = Path(tmp) / "verdicts" / "ledger.jsonl"
            lines = ledger_path.read_text().strip().splitlines()
            assert len(lines) == 1
            entry = json.loads(lines[0])
            assert entry["pause_reason_code"] == "qa_checkpoint"


def test_log_to_ledger_all_pause_reason_codes():
    """Each documented pause_reason_code persists correctly."""
    codes = [
        "auto_close_disabled",
        "qa_checkpoint",
        "gate_failure",
        "header_pause",
        "agent_verdict_request",
        "auto_close",
    ]
    with tempfile.TemporaryDirectory() as tmp:
        with patch.object(verdict, "VERDICTS_DIR", Path(tmp) / "verdicts"):
            gate_result = {"failures": [], "files_changed": []}
            for i, code in enumerate(codes):
                verdict.log_to_ledger(f"/tmp/plan-{code}.md", i + 1, gate_result,
                                      "continue", f"test {code}",
                                      pause_reason_code=code)

            ledger_path = Path(tmp) / "verdicts" / "ledger.jsonl"
            lines = ledger_path.read_text().strip().splitlines()
            assert len(lines) == len(codes)
            for i, code in enumerate(codes):
                entry = json.loads(lines[i])
                assert entry["pause_reason_code"] == code, \
                    f"Expected pause_reason_code={code}, got {entry['pause_reason_code']}"


def test_intermediate_decisions_section_rendered_when_present():
    """Verdict request renders Intermediate Decisions Detected section when blocks are passed."""
    with tempfile.TemporaryDirectory() as tmp:
        with patch.object(verdict, "VERDICTS_DIR", Path(tmp) / "verdicts"):
            gate_result = _make_gate_result(passed=True)
            decisions = [
                {"event_idx": 3, "text": "I decided to change the approach.", "matched_phrases": ["decided to"]},
                {"event_idx": 7, "text": "Wait, that path is wrong.", "matched_phrases": ["wait,"]},
            ]
            path = verdict.post_verdict_request(
                "/tmp/plan.md", "/tmp/project", 1, "/tmp/logs", gate_result,
                pause_reason="auto_close_disabled", total_steps=2,
                intermediate_decisions=decisions,
            )
            content = open(path).read()
            assert "## Intermediate Decisions Detected" in content
            assert "2 phrase-matched blocks" in content
            assert "**Event 3:**" in content
            assert "decided to" in content
            assert "**Event 7:**" in content
            assert "wait," in content


def test_intermediate_decisions_section_omitted_when_empty():
    """Verdict request omits Intermediate Decisions Detected section when no blocks match."""
    with tempfile.TemporaryDirectory() as tmp:
        with patch.object(verdict, "VERDICTS_DIR", Path(tmp) / "verdicts"):
            gate_result = _make_gate_result(passed=True)
            path = verdict.post_verdict_request(
                "/tmp/plan.md", "/tmp/project", 1, "/tmp/logs", gate_result,
                pause_reason="auto_close_disabled", total_steps=2,
                intermediate_decisions=[],
            )
            content = open(path).read()
            assert "## Intermediate Decisions Detected" not in content


def test_intermediate_decisions_section_omitted_when_none():
    """Verdict request omits section when intermediate_decisions is None (default)."""
    with tempfile.TemporaryDirectory() as tmp:
        with patch.object(verdict, "VERDICTS_DIR", Path(tmp) / "verdicts"):
            gate_result = _make_gate_result(passed=True)
            path = verdict.post_verdict_request(
                "/tmp/plan.md", "/tmp/project", 1, "/tmp/logs", gate_result,
                pause_reason="auto_close_disabled", total_steps=2,
            )
            content = open(path).read()
            assert "## Intermediate Decisions Detected" not in content


# --- Schema validator + observability tests (verdict content validator 2026-05-12) ---


def test_check_verdict_logs_warning_on_malformed_first_line(tmp_path, capsys):
    """Schema validator: malformed first line produces WARN log with expected format."""
    verdicts_dir = tmp_path / "verdicts"
    resolved_dir = verdicts_dir / "resolved"
    resolved_dir.mkdir(parents=True)
    verdict_file = resolved_dir / "verdict-test-malformed-step-1.md"
    verdict_file.write_text("not a verdict\n")
    with patch.object(verdict, "VERDICTS_DIR", verdicts_dir), \
         patch.object(verdict, "_NOTIFIED_MALFORMED", set()), \
         patch("verdict.notifier.push", return_value=True):
        result = verdict.check_verdict("test-malformed", 1)
    assert result == {"found": False}
    captured = capsys.readouterr()
    assert "verdict file malformed:" in captured.err
    assert str(verdict_file) in captured.err
    assert "'not a verdict'" in captured.err
    assert "expected pattern:" in captured.err


def test_check_verdict_pushover_deduped_per_file_per_daemon_lifetime(tmp_path):
    """Pushover notification deduped: same malformed file, two calls, one push."""
    verdicts_dir = tmp_path / "verdicts"
    resolved_dir = verdicts_dir / "resolved"
    resolved_dir.mkdir(parents=True)
    verdict_file = resolved_dir / "verdict-test-dedup-step-1.md"
    verdict_file.write_text("not a verdict\n")
    dedup_set = set()
    mock_push = MagicMock(return_value=True)
    with patch.object(verdict, "VERDICTS_DIR", verdicts_dir), \
         patch.object(verdict, "_NOTIFIED_MALFORMED", dedup_set), \
         patch("verdict.notifier.push", mock_push):
        verdict.check_verdict("test-dedup", 1)
        verdict.check_verdict("test-dedup", 1)
    assert mock_push.call_count == 1


def test_check_verdict_no_warning_on_empty_file(tmp_path, capsys):
    """Empty verdict file: no WARN, returns found=False."""
    verdicts_dir = tmp_path / "verdicts"
    resolved_dir = verdicts_dir / "resolved"
    resolved_dir.mkdir(parents=True)
    verdict_file = resolved_dir / "verdict-test-empty-step-1.md"
    verdict_file.write_text("")
    with patch.object(verdict, "VERDICTS_DIR", verdicts_dir):
        result = verdict.check_verdict("test-empty", 1)
    assert result == {"found": False}
    captured = capsys.readouterr()
    assert "verdict file malformed" not in captured.err


def test_check_verdict_no_warning_on_missing_file(tmp_path, capsys):
    """Missing verdict file: no WARN, returns found=False."""
    verdicts_dir = tmp_path / "verdicts"
    with patch.object(verdict, "VERDICTS_DIR", verdicts_dir):
        result = verdict.check_verdict("test-missing", 1)
    assert result == {"found": False}
    captured = capsys.readouterr()
    assert "verdict file malformed" not in captured.err


def test_check_verdict_well_formed_verdict_continue(tmp_path, capsys):
    """Well-formed 'continue': found=True, no WARN."""
    verdicts_dir = tmp_path / "verdicts"
    resolved_dir = verdicts_dir / "resolved"
    resolved_dir.mkdir(parents=True)
    verdict_file = resolved_dir / "verdict-test-continue-step-1.md"
    verdict_file.write_text("continue")
    with patch.object(verdict, "VERDICTS_DIR", verdicts_dir):
        result = verdict.check_verdict("test-continue", 1)
    assert result == {"found": True, "verdict": "continue", "reason": ""}
    captured = capsys.readouterr()
    assert "verdict file malformed" not in captured.err


def test_check_verdict_well_formed_verdict_stop_with_reason(tmp_path):
    """Well-formed 'verdict: stop' with reason: return contract preserved."""
    verdicts_dir = tmp_path / "verdicts"
    resolved_dir = verdicts_dir / "resolved"
    resolved_dir.mkdir(parents=True)
    verdict_file = resolved_dir / "verdict-test-stop-reason-step-1.md"
    verdict_file.write_text("verdict: stop\nrationale text")
    with patch.object(verdict, "VERDICTS_DIR", verdicts_dir):
        result = verdict.check_verdict("test-stop-reason", 1)
    assert result["found"] is True
    assert result["verdict"] == "stop"
    assert result["reason"] == "rationale text"


def test_check_verdict_pushover_failure_swallowed(tmp_path):
    """Pushover failure swallowed: notifier.push raises, check_verdict returns normally."""
    verdicts_dir = tmp_path / "verdicts"
    resolved_dir = verdicts_dir / "resolved"
    resolved_dir.mkdir(parents=True)
    verdict_file = resolved_dir / "verdict-test-pushfail-step-1.md"
    verdict_file.write_text("not a verdict\n")
    with patch.object(verdict, "VERDICTS_DIR", verdicts_dir), \
         patch.object(verdict, "_NOTIFIED_MALFORMED", set()), \
         patch("verdict.notifier.push", side_effect=ConnectionError("Pushover unreachable")):
        result = verdict.check_verdict("test-pushfail", 1)
    assert result == {"found": False}


# --- Verification Results table + Rule 22 verdict enrichment tests ---


def test_verification_results_table_all_pass():
    """(a) Verification Results table renders all-PASS rows when no failures."""
    gate_result = _make_gate_result(passed=True, is_qa=True, files_changed=["a.py", "b.py"])
    table = verdict._build_verification_results_table(gate_result, None, 2, 3)
    assert "| Check | Result | Detail |" in table
    assert "PASS" in table
    assert "FAIL" not in table
    assert "receipt_status" in table
    assert "rule_22_verification" in table


def test_verification_results_table_fail_row():
    """(b) Verification Results table renders FAIL with verbatim evidence."""
    gate_result = _make_gate_result(
        passed=False,
        failures=[{"gate": "scope_check", "evidence": "out-of-scope files: rogue.py"}],
    )
    table = verdict._build_verification_results_table(gate_result, None, 1, 2)
    assert "| scope_check | FAIL |" in table
    assert "out-of-scope files: rogue.py" in table


def test_verification_results_table_intermediate_decisions_count():
    """(c) intermediate_decisions row shows correct count."""
    gate_result = _make_gate_result(passed=True)
    decisions = [{"event_idx": 1, "text": "test", "matched_phrases": ["decided"]}]
    table = verdict._build_verification_results_table(gate_result, None, 1, 2, intermediate_decisions=decisions)
    assert "| intermediate_decisions | INFORMATIONAL | 1 phrase-matched blocks |" in table

    table_empty = verdict._build_verification_results_table(gate_result, None, 1, 2)
    assert "| intermediate_decisions | INFORMATIONAL | 0 phrase-matched blocks |" in table_empty


def test_pause_reason_label_rule_22():
    """(d) _pause_reason_labels returns 'Rule 22 mechanical check failed' for rule_22_check_failed."""
    with tempfile.TemporaryDirectory() as tmp:
        with patch.object(verdict, "VERDICTS_DIR", Path(tmp) / "verdicts"):
            gate_result = _make_gate_result(
                passed=False,
                failures=[{"gate": "rule_22_verification", "evidence": "test"}],
            )
            path = verdict.post_verdict_request(
                "/tmp/plan.md", "/tmp/project", 1, "/tmp/logs", gate_result,
                pause_reason="rule_22_check_failed", total_steps=2,
            )
            content = open(path).read()
            assert "**Pause Reason:** Rule 22 mechanical check failed" in content


def test_gate_failures_section_renders_for_rule_22_check_failed():
    """(e) Gate Failures section renders when pause_reason is rule_22_check_failed."""
    with tempfile.TemporaryDirectory() as tmp:
        with patch.object(verdict, "VERDICTS_DIR", Path(tmp) / "verdicts"):
            gate_result = _make_gate_result(
                passed=False,
                failures=[{"gate": "rule_22_verification", "evidence": "(a) deposit missing"}],
            )
            path = verdict.post_verdict_request(
                "/tmp/plan.md", "/tmp/project", 1, "/tmp/logs", gate_result,
                pause_reason="rule_22_check_failed", total_steps=2,
            )
            content = open(path).read()
            assert "## Gate Failures" in content
            assert "rule_22_verification" in content
            assert "(a) deposit missing" in content


def test_planner_only_checks_remaining_section():
    """(f) Planner-Only Checks Remaining section appears in verdict request output."""
    with tempfile.TemporaryDirectory() as tmp:
        with patch.object(verdict, "VERDICTS_DIR", Path(tmp) / "verdicts"):
            gate_result = _make_gate_result(passed=True)
            path = verdict.post_verdict_request(
                "/tmp/plan.md", "/tmp/project", 1, "/tmp/logs", gate_result,
                pause_reason="auto_close_disabled", total_steps=2,
            )
            content = open(path).read()
            assert "## Planner-Only Checks Remaining" in content
            assert "Bellows verified mechanical pass/fail" in content

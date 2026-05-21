import os
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gates


def _clean_parsed():
    return {
        "receipt_status": "Complete",
        "ceo_flags": [],
        "is_error": False,
        "permission_denials": [],
        "result_text": "All done.",
        "cost_usd": 0.05,
        "verdict_requested": {"requested": False, "reason": None},
    }


PLAN_TEXT = """## STEP 1 — DEV (Developer)

> Build gates.py and verdict.py in the bellows root directory.

## STEP 2 — QA (QA Engineer)

> Run all tests and verify deliverables.
"""


def test_all_gates_pass_on_clean_parsed():
    result = gates.check(_clean_parsed(), PLAN_TEXT, 1, "/tmp")
    assert result["passed"] is True
    assert result["failures"] == []
    assert result["is_qa_step"] is False


def test_receipt_status_blocked():
    parsed = _clean_parsed()
    parsed["receipt_status"] = "Blocked"
    result = gates.check(parsed, PLAN_TEXT, 1, "/tmp")
    assert result["passed"] is False
    assert any(f["gate"] == "receipt_status" for f in result["failures"])
    assert any("Blocked" in f["evidence"] for f in result["failures"])


def test_receipt_status_partial():
    parsed = _clean_parsed()
    parsed["receipt_status"] = "Partial"
    result = gates.check(parsed, PLAN_TEXT, 1, "/tmp")
    assert result["passed"] is False
    assert any(f["gate"] == "receipt_status" and "Partial" in f["evidence"] for f in result["failures"])


def test_ceo_flags_nonempty():
    parsed = _clean_parsed()
    parsed["ceo_flags"] = ["Cost overrun detected"]
    result = gates.check(parsed, PLAN_TEXT, 1, "/tmp")
    assert result["passed"] is False
    assert any(f["gate"] == "ceo_flags" and "Cost overrun" in f["evidence"] for f in result["failures"])


def test_is_error_true():
    parsed = _clean_parsed()
    parsed["is_error"] = True
    parsed["error"] = "timeout"
    result = gates.check(parsed, PLAN_TEXT, 1, "/tmp")
    assert result["passed"] is False
    assert any(f["gate"] == "no_errors" for f in result["failures"])


def test_permission_denials_nonempty():
    parsed = _clean_parsed()
    parsed["permission_denials"] = ["Write denied for /etc/passwd"]
    result = gates.check(parsed, PLAN_TEXT, 1, "/tmp")
    assert result["passed"] is False
    assert any(f["gate"] == "no_permission_denials" and "1 blocking denial" in f["evidence"] for f in result["failures"])


def test_permission_denials_read_class_only_passes():
    parsed = _clean_parsed()
    parsed["permission_denials"] = [
        {"tool_name": "Grep", "tool_use_id": "toolu_1", "tool_input": {"pattern": "test"}},
        {"tool_name": "Glob", "tool_use_id": "toolu_2", "tool_input": {"pattern": "*.py"}},
        {"tool_name": "Read", "tool_use_id": "toolu_3", "tool_input": {"file_path": "/tmp/x"}},
    ]
    result = gates.check(parsed, PLAN_TEXT, 1, "/tmp")
    assert result["passed"] is True
    assert not any(f["gate"] == "no_permission_denials" for f in result["failures"])


def test_permission_denials_write_class_fails():
    parsed = _clean_parsed()
    parsed["permission_denials"] = [
        {"tool_name": "Edit", "tool_use_id": "toolu_1", "tool_input": {}},
    ]
    result = gates.check(parsed, PLAN_TEXT, 1, "/tmp")
    assert result["passed"] is False
    assert any(f["gate"] == "no_permission_denials" and "1 blocking denial" in f["evidence"] for f in result["failures"])


def test_permission_denials_mixed_read_write_fails():
    parsed = _clean_parsed()
    parsed["permission_denials"] = [
        {"tool_name": "Grep", "tool_use_id": "toolu_1", "tool_input": {"pattern": "test"}},
        {"tool_name": "Edit", "tool_use_id": "toolu_2", "tool_input": {}},
    ]
    result = gates.check(parsed, PLAN_TEXT, 1, "/tmp")
    assert result["passed"] is False
    assert any(f["gate"] == "no_permission_denials" and "1 blocking denial" in f["evidence"] for f in result["failures"])


def test_permission_denials_missing_tool_name_fails():
    parsed = _clean_parsed()
    parsed["permission_denials"] = [
        {"tool_use_id": "toolu_1", "tool_input": {}},
    ]
    result = gates.check(parsed, PLAN_TEXT, 1, "/tmp")
    assert result["passed"] is False
    assert any(f["gate"] == "no_permission_denials" for f in result["failures"])


def test_permission_denials_none_tool_name_fails():
    parsed = _clean_parsed()
    parsed["permission_denials"] = [
        {"tool_name": None, "tool_use_id": "toolu_1", "tool_input": {}},
    ]
    result = gates.check(parsed, PLAN_TEXT, 1, "/tmp")
    assert result["passed"] is False
    assert any(f["gate"] == "no_permission_denials" for f in result["failures"])


def test_permission_denials_unknown_tool_fails():
    parsed = _clean_parsed()
    parsed["permission_denials"] = [
        {"tool_name": "SomeNewTool", "tool_use_id": "toolu_1", "tool_input": {}},
    ]
    result = gates.check(parsed, PLAN_TEXT, 1, "/tmp")
    assert result["passed"] is False
    assert any(f["gate"] == "no_permission_denials" for f in result["failures"])


def test_permission_denials_string_form_fails():
    parsed = _clean_parsed()
    parsed["permission_denials"] = ["Grep denied for /some/path"]
    result = gates.check(parsed, PLAN_TEXT, 1, "/tmp")
    assert result["passed"] is False
    assert any(f["gate"] == "no_permission_denials" and "1 blocking denial" in f["evidence"] for f in result["failures"])


@patch("os.path.isfile", return_value=False)
def test_deposit_path_missing(mock_isfile):
    parsed = _clean_parsed()
    parsed["result_text"] = "### Files Deposited\n- /tmp/missing_file.txt\n\n### Next"
    result = gates.check(parsed, PLAN_TEXT, 1, "/tmp")
    assert result["passed"] is False
    assert any(f["gate"] == "deposit_exists" and "missing" in f["evidence"] for f in result["failures"])


def test_qa_step_detection():
    result = gates.check(_clean_parsed(), PLAN_TEXT, 2, "/tmp")
    assert result["is_qa_step"] is True


def test_file_change_audit_populates():
    files = ["gates.py", "verdict.py"]
    result = gates.check(_clean_parsed(), PLAN_TEXT, 1, "/tmp", files_changed=files)
    assert result["files_changed"] == ["gates.py", "verdict.py"]


def test_scope_check_passes_when_files_in_plan():
    result = gates.check(_clean_parsed(), PLAN_TEXT, 1, "/tmp", files_changed=["gates.py", "verdict.py"])
    assert result["passed"] is True
    assert not any(f["gate"] == "scope_check" for f in result["failures"])


def test_scope_check_fails_when_file_not_in_plan():
    result = gates.check(_clean_parsed(), PLAN_TEXT, 1, "/tmp", files_changed=["totally_unexpected.py"])
    assert result["passed"] is False
    assert any(f["gate"] == "scope_check" and "totally_unexpected.py" in f["evidence"] for f in result["failures"])


def test_scope_check_allowlist():
    result = gates.check(_clean_parsed(), PLAN_TEXT, 1, "/tmp",
                         files_changed=["agent-prompt-feedback.md", "PROJECT_STATUS.md"])
    assert result["passed"] is True
    assert not any(f["gate"] == "scope_check" for f in result["failures"])


def test_no_deposit_section_passes():
    parsed = _clean_parsed()
    parsed["result_text"] = "No deposit here, just results."
    result = gates.check(parsed, PLAN_TEXT, 1, "/tmp")
    assert not any(f["gate"] == "deposit_exists" for f in result["failures"])


def test_parse_plan_header_empty():
    plan_text = "# No Frontmatter Plan\n## STEP 1\ntest"
    header = gates._parse_plan_header(plan_text)
    assert header == {}


def test_parse_plan_header_basic():
    plan_text = "---\npause_for_verdict: after_step_1\nauto_close: false\n---\n# Title\nrest of plan"
    header = gates._parse_plan_header(plan_text)
    assert header.get("pause_for_verdict") == "after_step_1"
    assert header.get("auto_close") is False


def test_parse_plan_header_malformed():
    plan_text = "---\npause_for_verdict: after_step_1\n# No closing ---\n"
    header = gates._parse_plan_header(plan_text)
    assert header == {}


def test_parse_plan_header_pipe_format_with_pause_for_verdict():
    """Pipe-separated header with pause_for_verdict extracts correctly."""
    plan_text = "# Test Plan\n**Date:** 2026-05-08 | **Tier:** Small | **Test Scope:** targeted | **pause_for_verdict:** after_step_1\n\n## STEP 1\n"
    header = gates._parse_plan_header(plan_text)
    assert header.get("pause_for_verdict") == "after_step_1"
    assert header.get("date") == "2026-05-08"
    assert header.get("tier") == "Small"


def test_parse_plan_header_pipe_format_without_pause_for_verdict():
    """Pipe-separated header without pause_for_verdict returns empty string on .get()."""
    plan_text = "# Test Plan\n**Date:** 2026-05-08 | **Tier:** Small\n\n## STEP 1\n"
    header = gates._parse_plan_header(plan_text)
    assert header.get("pause_for_verdict", "") == ""
    assert header.get("date") == "2026-05-08"


def test_parse_plan_header_yaml_still_works():
    """YAML frontmatter regression — still parses correctly after pipe-format addition."""
    plan_text = "---\npause_for_verdict: after_step_1\nauto_close: false\n---\n# Title\nrest"
    header = gates._parse_plan_header(plan_text)
    assert header.get("pause_for_verdict") == "after_step_1"
    assert header.get("auto_close") is False


def test_parse_plan_header_no_format_returns_empty():
    """File with neither YAML nor pipe-format header returns {}."""
    plan_text = "Just some plain text\nwith no header format.\n"
    header = gates._parse_plan_header(plan_text)
    assert header == {}


def test_parse_plan_header_pipe_format_always():
    """Pipe-format with pause_for_verdict: always and multiple fields."""
    plan_text = "# Project — Feature\n**Date:** 2026-05-08 | **Tier:** Medium | **Execution:** Step 1 → Step 2 | **pause_for_verdict:** always\n\nBody.\n"
    header = gates._parse_plan_header(plan_text)
    assert header.get("pause_for_verdict") == "always"
    assert header.get("execution") is not None


def test_parse_plan_header_pipe_format_key_normalization():
    """Title-case keys with spaces normalize to lowercase underscored."""
    plan_text = "# Plan\n**Pause For Verdict:** after_step_1 | **Test Scope:** full-suite\n\nBody.\n"
    header = gates._parse_plan_header(plan_text)
    assert header.get("pause_for_verdict") == "after_step_1"
    assert header.get("test_scope") == "full-suite"


def test_pipe_header_pause_for_verdict_after_step_1_causes_pause():
    """End-to-end: pipe-parsed header with after_step_1 causes header_says_pause to return True at step 1."""
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import bellows
    plan_text = "# Test\n**Date:** 2026-05-08 | **pause_for_verdict:** after_step_1\n\n## STEP 1\n\n## STEP 2\n"
    header = gates._parse_plan_header(plan_text)
    assert bellows.header_says_pause(header, current_step=1, total_steps=2, is_qa_step=False) is True


def test_pipe_header_pause_for_verdict_always_causes_pause():
    """End-to-end: pipe-parsed header with always causes header_says_pause to return True."""
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import bellows
    plan_text = "# Test\n**Date:** 2026-05-08 | **pause_for_verdict:** always\n\n## STEP 1\n\n## STEP 2\n"
    header = gates._parse_plan_header(plan_text)
    assert bellows.header_says_pause(header, current_step=1, total_steps=2, is_qa_step=False) is True


def test_pipe_header_no_pause_for_verdict_no_pause():
    """End-to-end: pipe-parsed header without pause_for_verdict causes header_says_pause to return False."""
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import bellows
    plan_text = "# Test\n**Date:** 2026-05-08 | **Tier:** Small\n\n## STEP 1\n\n## STEP 2\n"
    header = gates._parse_plan_header(plan_text)
    assert bellows.header_says_pause(header, current_step=1, total_steps=2, is_qa_step=False) is False


def test_parse_plan_header_multi_line_bold_returns_all_fields():
    """Multi-line bold-Markdown headers (one **key:** val per line) parse all fields.
    Regression for BACKLOG 2026-05-10 multi-line bold parser gap."""
    text = """# Executable — Test

**Project:** bellows
**Date:** 2026-05-10
**Author:** Planner
**Tier:** Small
**Total Steps:** 2

**pause_for_verdict:** after_step_1

---

## Context
"""
    result = gates._parse_plan_header(text)
    assert result.get("project") == "bellows"
    assert result.get("date") == "2026-05-10"
    assert result.get("author") == "Planner"
    assert result.get("tier") == "Small"
    assert result.get("total_steps") == "2"
    assert result.get("pause_for_verdict") == "after_step_1"


def test_parse_plan_header_single_line_pipe_still_works():
    """Single-line pipe-format headers continue to parse correctly after multi-line extension."""
    text = """# Executable — Test

**Project:** bellows | **Date:** 2026-05-10 | **Author:** Planner | **Tier:** Small | **Total Steps:** 2 | **pause_for_verdict:** after_step_1

---

## Context
"""
    result = gates._parse_plan_header(text)
    assert result.get("project") == "bellows"
    assert result.get("pause_for_verdict") == "after_step_1"
    assert len(result) == 6


def test_parse_plan_header_multi_line_bold_with_blank_lines():
    """Blank lines between multi-line bold fields are tolerated."""
    text = """# Test

**Project:** bellows

**Date:** 2026-05-10


**pause_for_verdict:** always

---
"""
    result = gates._parse_plan_header(text)
    assert result.get("project") == "bellows"
    assert result.get("date") == "2026-05-10"
    assert result.get("pause_for_verdict") == "always"


def test_parse_plan_header_horizontal_rule_terminates_header_block():
    """A --- horizontal rule terminates the header block; bold lines after it are ignored."""
    text = """# Test

**Project:** bellows
**Date:** 2026-05-10

---

**This should NOT be parsed:** because it's after the rule
"""
    result = gates._parse_plan_header(text)
    assert result.get("project") == "bellows"
    assert result.get("date") == "2026-05-10"
    assert "this_should_not_be_parsed" not in result


def test_parse_plan_header_non_bold_line_terminates_header_block():
    """A non-bold, non-blank line terminates the header block."""
    text = """# Test

**Project:** bellows
**Date:** 2026-05-10
This is prose, not a header field.
**Not Parsed:** because prose ended the block

---
"""
    result = gates._parse_plan_header(text)
    assert result.get("project") == "bellows"
    assert result.get("date") == "2026-05-10"
    assert "not_parsed" not in result


def test_scope_check_prefix_allowlist_in_progress():
    result = gates.check(_clean_parsed(), PLAN_TEXT, 1, "/tmp",
                         files_changed=["knowledge/decisions/in-progress-executable-foo.md"])
    assert result["passed"] is True
    assert not any(f["gate"] == "scope_check" for f in result["failures"])


def test_scope_check_prefix_allowlist_verdict_pending():
    result = gates.check(_clean_parsed(), PLAN_TEXT, 1, "/tmp",
                         files_changed=["knowledge/decisions/verdict-pending-executable-bar.md"])
    assert result["passed"] is True
    assert not any(f["gate"] == "scope_check" for f in result["failures"])


def test_scope_check_prefix_allowlist_halted():
    result = gates.check(_clean_parsed(), PLAN_TEXT, 1, "/tmp",
                         files_changed=["knowledge/decisions/halted-executable-baz.md"])
    assert result["passed"] is True
    assert not any(f["gate"] == "scope_check" for f in result["failures"])


def test_scope_check_prefix_allowlist_does_not_suppress_real_violations():
    result = gates.check(_clean_parsed(), PLAN_TEXT, 1, "/tmp",
                         files_changed=["some-random-file.py"])
    assert result["passed"] is False
    assert any(f["gate"] == "scope_check" and "some-random-file.py" in f["evidence"]
               for f in result["failures"])


def test_verdict_requested_from_parsed_dict():
    parsed = _clean_parsed()
    parsed["verdict_requested"] = {"requested": True, "reason": "agent found inconsistency"}
    result = gates.check(parsed, PLAN_TEXT, 1, "/tmp")
    assert result["verdict_requested"]["requested"] is True
    assert result["verdict_requested"]["body"] == "agent found inconsistency"


def test_verdict_requested_defaults_when_key_missing():
    parsed = _clean_parsed()
    del parsed["verdict_requested"]
    result = gates.check(parsed, PLAN_TEXT, 1, "/tmp")
    assert result["verdict_requested"]["requested"] is False
    assert result["verdict_requested"]["body"] is None


# --- _resolve_deposit_path directory support (BACKLOG #11) ---

def test_resolve_deposit_path_directory_as_is(tmp_path):
    d = tmp_path / "evidence"
    d.mkdir()
    result = gates._resolve_deposit_path(str(d), "/nonexistent")
    assert result is not None
    assert os.path.isabs(result)


def test_resolve_deposit_path_directory_project_relative(tmp_path):
    d = tmp_path / "subdir"
    d.mkdir()
    result = gates._resolve_deposit_path("subdir", str(tmp_path))
    assert result is not None
    assert os.path.isabs(result)


def test_resolve_deposit_path_directory_parent_relative(tmp_path):
    parent = tmp_path / "project"
    parent.mkdir()
    d = tmp_path / "bellows" / "evidence"
    d.mkdir(parents=True)
    result = gates._resolve_deposit_path("bellows/evidence", str(parent))
    assert result is not None
    assert os.path.isabs(result)


@patch("os.path.isfile", return_value=False)
@patch("os.path.isdir", return_value=False)
def test_resolve_deposit_path_nonexistent(mock_isdir, mock_isfile):
    assert gates._resolve_deposit_path("/no/such/path", "/tmp") is None


def test_gate_deposit_exists_directory_in_deposits_block(tmp_path):
    d = tmp_path / "evidence"
    d.mkdir()
    plan_text = (
        "## STEP 1 — DEV\n\n"
        "> Do the work.\n>\n"
        "> **Deposits:**\n"
        f"> - `{d}/`\n"
    )
    parsed = _clean_parsed()
    parsed["result_text"] = f"### Files Deposited\n- {d}/\n\n### Next"
    failures = []
    gates._gate_deposit_exists(parsed, failures, str(tmp_path), plan_text=plan_text, step_number=1)
    assert failures == []


# --- agent-receipt backtick path extraction (deposit-parser-agent-receipt-fix) ---

def _build_parsed_with_receipt(receipt_line):
    """Helper: build a parsed dict with a single Files Deposited line."""
    parsed = _clean_parsed()
    parsed["result_text"] = f"### Files Deposited\n{receipt_line}\n\n### Next"
    return parsed


def test_deposit_exists_extracts_path_from_backtick_with_description(tmp_path):
    f = tmp_path / "gates.py"
    f.write_text("# placeholder")
    receipt_line = f"- `{f}` — agent receipt parser fix"
    parsed = _build_parsed_with_receipt(receipt_line)
    result = gates.check(parsed, PLAN_TEXT, 1, str(tmp_path))
    assert result["passed"] is True
    assert not any(f_item["gate"] == "deposit_exists" for f_item in result["failures"])


def test_deposit_exists_extracts_path_from_backtick_only(tmp_path):
    f = tmp_path / "verdict.py"
    f.write_text("# placeholder")
    receipt_line = f"- `{f}`"
    parsed = _build_parsed_with_receipt(receipt_line)
    result = gates.check(parsed, PLAN_TEXT, 1, str(tmp_path))
    assert result["passed"] is True
    assert not any(f_item["gate"] == "deposit_exists" for f_item in result["failures"])


def test_deposit_exists_extracts_path_from_bare_path_without_backticks(tmp_path):
    f = tmp_path / "bellows.py"
    f.write_text("# placeholder")
    receipt_line = f"- {f}"
    parsed = _build_parsed_with_receipt(receipt_line)
    result = gates.check(parsed, PLAN_TEXT, 1, str(tmp_path))
    assert result["passed"] is True
    assert not any(f_item["gate"] == "deposit_exists" for f_item in result["failures"])


def test_deposit_exists_still_fails_on_genuinely_missing_path_with_new_format():
    receipt_line = "- `/nonexistent/path/that/does/not/exist.md` — description text"
    parsed = _build_parsed_with_receipt(receipt_line)
    result = gates.check(parsed, PLAN_TEXT, 1, "/tmp")
    assert result["passed"] is False
    assert any(f_item["gate"] == "deposit_exists" for f_item in result["failures"])


# --- Rule 20 self-check verification gate ---

QA_PLAN_TEXT = """## STEP 1 — DEV (Developer)

> Build gates.py in the bellows root directory.
>
> **Deposits:**
> - `bellows/knowledge/development/dev-log.md`

## STEP 2 — QA (QA Engineer)

> Run all tests and verify deliverables.
>
> **Deposits:**
> - `bellows/knowledge/qa/qa-report.md`
"""


def test_extract_plan_required_deposits_inline_format():
    """Inline **Deposits:** format (paths on same line as marker) extracts correctly."""
    step_text = (
        "## STEP 2\n\n"
        "foo bar\n\n"
        "**Deposits:** `- /Users/marklehn/path/a.md`, `- /Users/marklehn/path/b/`.\n"
    )
    result = gates._extract_plan_required_deposits(step_text)
    assert "/Users/marklehn/path/a.md" in result
    assert "/Users/marklehn/path/b/" in result
    assert len(result) == 2


def test_extract_plan_required_deposits_multiline_format():
    """Multi-line **Deposits:** format (block with bullet lines) extracts correctly."""
    step_text = (
        "## STEP 1 — DEV\n\n"
        "> Do the work.\n>\n"
        "> **Deposits:**\n"
        "> - `/Users/marklehn/path/a.md`\n"
        "> - `/Users/marklehn/path/b/`\n"
    )
    result = gates._extract_plan_required_deposits(step_text)
    assert "/Users/marklehn/path/a.md" in result
    assert "/Users/marklehn/path/b/" in result
    assert len(result) == 2


def test_rule_20_self_check_passes_with_valid_banner_and_passed_line(tmp_path):
    report = tmp_path / "bellows" / "knowledge" / "qa" / "qa-report.md"
    report.parent.mkdir(parents=True)
    report.write_text(
        "# QA Report\n\nSome content.\n\n"
        "============================================================\n"
        "Rule 20 — QA Self-Check Results\n"
        "============================================================\n"
        "PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.\n"
    )
    parsed = _clean_parsed()
    result = gates.check(parsed, QA_PLAN_TEXT, 2, str(tmp_path))
    assert not any(f["gate"] == "rule_20_self_check" for f in result["failures"])


def test_rule_20_self_check_fails_when_banner_missing(tmp_path):
    report = tmp_path / "bellows" / "knowledge" / "qa" / "qa-report.md"
    report.parent.mkdir(parents=True)
    report.write_text("# QA Report\n\nAll tests passed. No issues found.\n")
    parsed = _clean_parsed()
    result = gates.check(parsed, QA_PLAN_TEXT, 2, str(tmp_path))
    assert result["passed"] is False
    r20 = [f for f in result["failures"] if f["gate"] == "rule_20_self_check"]
    assert len(r20) == 1
    assert "no QA deposit" in r20[0]["evidence"]


def test_rule_20_self_check_fails_when_banner_without_passed_line(tmp_path):
    report = tmp_path / "bellows" / "knowledge" / "qa" / "qa-report.md"
    report.parent.mkdir(parents=True)
    report.write_text(
        "# QA Report\n\n"
        "============================================================\n"
        "Rule 20 — QA Self-Check Results\n"
        "============================================================\n"
        "FAILED — SELF-CHECK FAILED — 2 issue(s):\n"
        "  - CRITICAL: evidence file missing\n"
    )
    parsed = _clean_parsed()
    result = gates.check(parsed, QA_PLAN_TEXT, 2, str(tmp_path))
    assert result["passed"] is False
    r20 = [f for f in result["failures"] if f["gate"] == "rule_20_self_check"]
    assert len(r20) == 1
    assert "banner present but PASSED line missing" in r20[0]["evidence"]


def test_rule_20_self_check_fails_when_deposit_unreadable(tmp_path):
    # Deposit declared but file does not exist on disk
    parsed = _clean_parsed()
    result = gates.check(parsed, QA_PLAN_TEXT, 2, str(tmp_path))
    assert result["passed"] is False
    # Both deposit_exists and rule_20_self_check should fail
    assert any(f["gate"] == "deposit_exists" for f in result["failures"])
    assert any(f["gate"] == "rule_20_self_check" for f in result["failures"])
    r20 = [f for f in result["failures"] if f["gate"] == "rule_20_self_check"]
    assert "deposit file unreadable" in r20[0]["evidence"]


def test_rule_20_self_check_skipped_on_non_qa_step(tmp_path):
    report = tmp_path / "bellows" / "knowledge" / "development" / "dev-log.md"
    report.parent.mkdir(parents=True)
    report.write_text("# Dev log\nNo Rule 20 banner here.\n")
    parsed = _clean_parsed()
    result = gates.check(parsed, QA_PLAN_TEXT, 1, str(tmp_path))
    assert not any(f["gate"] == "rule_20_self_check" for f in result["failures"])


def test_rule_20_self_check_passes_when_passed_line_after_banner_in_multi_section_report(tmp_path):
    report = tmp_path / "bellows" / "knowledge" / "qa" / "qa-report.md"
    report.parent.mkdir(parents=True)
    report.write_text(
        "# QA Report\n\n"
        "## Deliverable Verification\n\n"
        "| Item | Status |\n|---|---|\n| gates.py | OK |\n\n"
        "## Test Results\n\n38 tests passed.\n\n"
        "## Smoke Test\n\nAll 4 scenarios passed.\n\n"
        "============================================================\n"
        "Rule 20 — QA Self-Check Results\n"
        "============================================================\n"
        "PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.\n"
        "Evidence folder: bellows/knowledge/qa/evidence/\n"
        "Files verified: 7\n\n"
        "## Output Receipt\n**Agent:** Bellows QA\n"
    )
    parsed = _clean_parsed()
    result = gates.check(parsed, QA_PLAN_TEXT, 2, str(tmp_path))
    assert not any(f["gate"] == "rule_20_self_check" for f in result["failures"])


# --- _resolve_deposit_path refactor tests ---

def test_resolve_deposit_path_returns_absolute_path_when_found(tmp_path):
    f = tmp_path / "report.md"
    f.write_text("content")
    result = gates._resolve_deposit_path(str(f), str(tmp_path))
    assert isinstance(result, str)
    assert os.path.isabs(result)


def test_resolve_deposit_path_returns_none_when_not_found(tmp_path):
    result = gates._resolve_deposit_path("/nonexistent/path/file.md", str(tmp_path))
    assert result is None


# --- worktree-aware deposit path resolution (deposit-exists-worktree-aware fix) ---

def test_resolve_deposit_path_finds_file_in_worktree(tmp_path):
    """Test 2.1: Form B (project-relative) path resolves via worktree-first strategy."""
    project_path = tmp_path / "myproject"
    project_path.mkdir()
    wt_path = tmp_path / "worktree"
    wt_path.mkdir()
    deposit = wt_path / "knowledge" / "research" / "foo.md"
    deposit.parent.mkdir(parents=True)
    deposit.write_text("deposit content")
    # File does NOT exist at project_path
    result = gates._resolve_deposit_path("knowledge/research/foo.md", str(project_path), wt_path=str(wt_path))
    assert result is not None
    assert os.path.isfile(result)
    assert str(wt_path) in result


def test_resolve_deposit_path_finds_file_in_worktree_form_a(tmp_path):
    """Test 2.2: Form A (governance-root-relative) path with project basename prefix."""
    project_path = tmp_path / "invoice-pulse"
    project_path.mkdir()
    wt_path = tmp_path / "worktree"
    wt_path.mkdir()
    deposit = wt_path / "knowledge" / "research" / "foo.md"
    deposit.parent.mkdir(parents=True)
    deposit.write_text("deposit content")
    # Form A path includes the project basename as prefix
    result = gates._resolve_deposit_path("invoice-pulse/knowledge/research/foo.md", str(project_path), wt_path=str(wt_path))
    assert result is not None
    assert os.path.isfile(result)
    assert str(wt_path) in result


def test_resolve_deposit_path_bellows_self_no_wt_path_drift(tmp_path):
    """Test 2.3: bellows-self pattern (wt_path == project_path) skips Strategy 0."""
    project_path = tmp_path / "bellows"
    project_path.mkdir()
    deposit = project_path / "knowledge" / "research" / "foo.md"
    deposit.parent.mkdir(parents=True)
    deposit.write_text("deposit content")
    result = gates._resolve_deposit_path("knowledge/research/foo.md", str(project_path), wt_path=str(project_path))
    assert result is not None
    assert os.path.isabs(result)
    assert str(project_path) in result


def test_resolve_deposit_path_no_wt_path_backward_compat(tmp_path):
    """Test 2.4: no wt_path parameter — backward compatibility with existing callers."""
    project_path = tmp_path / "bellows"
    project_path.mkdir()
    deposit = project_path / "knowledge" / "research" / "foo.md"
    deposit.parent.mkdir(parents=True)
    deposit.write_text("deposit content")
    result = gates._resolve_deposit_path("knowledge/research/foo.md", str(project_path))
    assert result is not None
    assert os.path.isabs(result)
    assert str(project_path) in result


def test_gate_deposit_exists_threads_wt_path(tmp_path):
    """Test 2.5: _gate_deposit_exists passes wt_path through to _resolve_deposit_path."""
    project_path = tmp_path / "myproject"
    project_path.mkdir()
    wt_path = tmp_path / "worktree"
    wt_path.mkdir()
    deposit = wt_path / "knowledge" / "research" / "foo.md"
    deposit.parent.mkdir(parents=True)
    deposit.write_text("deposit content")
    plan_text = (
        "## STEP 1 — DEV\n\n"
        "> Do the work.\n>\n"
        "> **Deposits:**\n"
        "> - `knowledge/research/foo.md`\n"
    )
    parsed = _clean_parsed()
    parsed["result_text"] = "### Files Deposited\n- `knowledge/research/foo.md` — findings\n\n### Next"
    failures = []
    gates._gate_deposit_exists(parsed, failures, str(project_path), plan_text=plan_text, step_number=1, wt_path=str(wt_path))
    assert failures == []


def test_rule_20_self_check_resolves_via_worktree_path(tmp_path):
    """Regression: _gate_rule_20_self_check threads wt_path to _resolve_deposit_path.

    Without the fix, the gate only tries Strategies 1-3 (all look at project_path)
    and produces a false-positive 'file not found' failure even though the file
    exists in the worktree.
    """
    project_path = tmp_path / "myproject"
    project_path.mkdir()
    wt_path = tmp_path / "worktree"
    wt_path.mkdir()
    # QA report exists ONLY in worktree, not in project_path
    report = wt_path / "knowledge" / "qa" / "qa-report.md"
    report.parent.mkdir(parents=True)
    report.write_text(
        "# QA Report\n\n"
        "============================================================\n"
        "Rule 20 — QA Self-Check Results\n"
        "============================================================\n"
        "PASSED — SELF-CHECK PASSED — all evidence files present.\n"
    )
    qa_plan = (
        "## STEP 1 — DEV (Developer)\n\n"
        "> Build the feature.\n>\n"
        "> **Deposits:**\n"
        "> - `knowledge/development/dev-log.md`\n\n"
        "## STEP 2 — QA (QA Engineer)\n\n"
        "> Verify deliverables.\n>\n"
        "> **Deposits:**\n"
        "> - `knowledge/qa/qa-report.md`\n"
    )
    parsed = _clean_parsed()
    # Also place the file in wt_path for deposit_exists gate (so it doesn't fail separately)
    result = gates.check(parsed, qa_plan, 2, str(project_path), wt_path=str(wt_path))
    # rule_20_self_check should NOT fail — it resolves the file via worktree Strategy 0
    assert not any(f["gate"] == "rule_20_self_check" for f in result["failures"]), (
        f"rule_20_self_check should pass via worktree resolution but got: {result['failures']}"
    )


def test_extract_step_text_ignores_in_fence_headers():
    """Regression: in-fence ## STEP N must not be returned as the real step text."""
    fixture = (
        "## STEP 1 — Real Step One\n"
        "\n"
        "Some prose.\n"
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
    result = gates._extract_step_text(fixture, 2)
    assert result is not None
    assert "Developer" in result
    assert "Bellows QA" not in result


def test_gate_is_qa_step_ignores_in_fence_headers():
    """Regression: in-fence QA header must not cause misclassification."""
    fixture = (
        "## STEP 1 — Real Step One\n"
        "\n"
        "Some prose.\n"
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
    assert gates._gate_is_qa_step(fixture, 2) is False


def test_extract_step_text_ignores_inline_code_references():
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
    result = gates._extract_step_text(fixture, 2)
    assert result is not None
    assert "Bellows QA" in result
    assert "documentation references" not in result


def test_gate_is_qa_step_ignores_inline_code_references():
    """Regression: inline `## STEP N — Bellows QA` must not cause misclassification."""
    fixture = (
        "## STEP 1 — Developer\n"
        "\n"
        "The prior step references `## STEP 2 — Bellows QA` inline.\n"
        "\n"
        "## STEP 2 — Developer\n"
        "\n"
        "Real step 2 body.\n"
    )
    assert gates._gate_is_qa_step(fixture, 2) is False


def test_permission_denials_vexp_run_pipeline_exempt():
    """Regression: mcp__vexp__run_pipeline denial does NOT trip no_permission_denials gate."""
    parsed = _clean_parsed()
    parsed["permission_denials"] = [
        {"tool_name": "mcp__vexp__run_pipeline", "tool_use_id": "toolu_1", "tool_input": {}},
    ]
    result = gates.check(parsed, PLAN_TEXT, 1, "/tmp")
    assert result["passed"] is True
    assert not any(f["gate"] == "no_permission_denials" for f in result["failures"])


def test_gate_deposit_exists_fails_when_file_truly_missing(tmp_path):
    """Test 2.6: negative case — deposit missing from both wt_path and project_path."""
    project_path = tmp_path / "myproject"
    project_path.mkdir()
    wt_path = tmp_path / "worktree"
    wt_path.mkdir()
    plan_text = (
        "## STEP 1 — DEV\n\n"
        "> Do the work.\n>\n"
        "> **Deposits:**\n"
        "> - `knowledge/research/nonexistent.md`\n"
    )
    parsed = _clean_parsed()
    parsed["result_text"] = "### Files Deposited\n- `knowledge/research/nonexistent.md` — findings\n\n### Next"
    failures = []
    gates._gate_deposit_exists(parsed, failures, str(project_path), plan_text=plan_text, step_number=1, wt_path=str(wt_path))
    assert len(failures) > 0
    assert any(f["gate"] == "deposit_exists" for f in failures)


# --- Gate 2c: _staging_ filter tests (strike 4) ---

def test_extract_deposits_filters_staging_prefix():
    """Strike 4: step text mentioning both a real deposit and a _staging_* path returns only the real one."""
    step_text = (
        "## STEP 1\n\n"
        "Deposit the results to `knowledge/research/report.md`.\n"
        "The mechanism writes to `_staging_report.md` first, then moves it.\n"
    )
    result = gates._extract_plan_required_deposits(step_text)
    assert "knowledge/research/report.md" in result
    assert not any("_staging_" in p for p in result)


def test_extract_deposits_filters_staging_in_structured_block():
    """Strike 4: structured **Deposits:** block with a _staging_* path filters it out."""
    step_text = (
        "## STEP 1 — DEV\n\n"
        "> Do the work.\n>\n"
        "> **Deposits:**\n"
        "> - `knowledge/research/report.md`\n"
        "> - `_staging_diagnostic-canary.md`\n"
    )
    result = gates._extract_plan_required_deposits(step_text)
    assert "knowledge/research/report.md" in result
    assert "_staging_diagnostic-canary.md" not in result
    assert len(result) == 1


def test_extract_deposits_filters_staging_in_inline_format():
    """Strike 4: inline **Deposits:** format with a _staging_* path filters it out."""
    step_text = (
        "## STEP 1\n\n"
        "**Deposits:** `- knowledge/qa/qa-report.md`, `- _staging_qa-report.md`.\n"
    )
    result = gates._extract_plan_required_deposits(step_text)
    assert "knowledge/qa/qa-report.md" in result
    assert "_staging_qa-report.md" not in result
    assert len(result) == 1


def test_extract_deposits_filters_staging_in_legacy_prose():
    """Strike 4: legacy prose 'Deposit ... to `_staging_foo.md`' is filtered."""
    step_text = (
        "## STEP 1\n\n"
        "Deposit the dev log to `knowledge/development/dev-log.md`.\n"
        "The atomic deposit mechanism writes to `_staging_dev-log.md` first.\n"
    )
    result = gates._extract_plan_required_deposits(step_text)
    assert "knowledge/development/dev-log.md" in result
    assert not any("_staging_" in p for p in result)


# --- Gate 2c: tolerant rule_20 banner matching tests (strikes 3 & 5) ---

def test_rule_20_banner_in_fenced_block(tmp_path):
    """Strike 5: banner inside a fenced code block — gate should still pass."""
    report = tmp_path / "bellows" / "knowledge" / "qa" / "qa-report.md"
    report.parent.mkdir(parents=True)
    report.write_text(
        "# QA Report\n\n"
        "```\n"
        "Rule 20 — QA Self-Check Results\n"
        "PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.\n"
        "```\n"
    )
    parsed = _clean_parsed()
    result = gates.check(parsed, QA_PLAN_TEXT, 2, str(tmp_path))
    assert not any(f["gate"] == "rule_20_self_check" for f in result["failures"])


def test_rule_20_banner_with_decoration(tmp_path):
    """Strike 5: banner with === decoration lines bracketing it inside fence — gate passes."""
    report = tmp_path / "bellows" / "knowledge" / "qa" / "qa-report.md"
    report.parent.mkdir(parents=True)
    report.write_text(
        "# QA Report\n\n"
        "```\n"
        "============================================================\n"
        "Rule 20 — QA Self-Check Results\n"
        "============================================================\n"
        "PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.\n"
        "```\n"
    )
    parsed = _clean_parsed()
    result = gates.check(parsed, QA_PLAN_TEXT, 2, str(tmp_path))
    assert not any(f["gate"] == "rule_20_self_check" for f in result["failures"])


def test_rule_20_banner_with_shell_prompt_prefix(tmp_path):
    """Strike 3: $ python3 -c '...' line above banner inside fence — gate passes."""
    report = tmp_path / "bellows" / "knowledge" / "qa" / "qa-report.md"
    report.parent.mkdir(parents=True)
    report.write_text(
        "# QA Report\n\n"
        "```\n"
        '$ python3 -c "import os; ..."\n'
        "Rule 20 — QA Self-Check Results\n"
        "PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.\n"
        "```\n"
    )
    parsed = _clean_parsed()
    result = gates.check(parsed, QA_PLAN_TEXT, 2, str(tmp_path))
    assert not any(f["gate"] == "rule_20_self_check" for f in result["failures"])


def test_rule_20_passed_line_with_indentation(tmp_path):
    """Strike 5 variant: PASSED line has leading whitespace from indented code block."""
    report = tmp_path / "bellows" / "knowledge" / "qa" / "qa-report.md"
    report.parent.mkdir(parents=True)
    report.write_text(
        "# QA Report\n\n"
        "    Rule 20 — QA Self-Check Results\n"
        "    PASSED — SELF-CHECK PASSED — all evidence files present.\n"
    )
    parsed = _clean_parsed()
    result = gates.check(parsed, QA_PLAN_TEXT, 2, str(tmp_path))
    assert not any(f["gate"] == "rule_20_self_check" for f in result["failures"])


def test_rule_20_no_banner(tmp_path):
    """Strike 6 detection: deposit without banner — gate should fail."""
    report = tmp_path / "bellows" / "knowledge" / "qa" / "qa-report.md"
    report.parent.mkdir(parents=True)
    report.write_text(
        "# QA Report\n\n"
        "All 10 checks passed.\n"
        "No issues found.\n"
    )
    parsed = _clean_parsed()
    result = gates.check(parsed, QA_PLAN_TEXT, 2, str(tmp_path))
    assert result["passed"] is False
    r20 = [f for f in result["failures"] if f["gate"] == "rule_20_self_check"]
    assert len(r20) == 1
    assert "no QA deposit contains Rule 20 self-check banner" in r20[0]["evidence"]


def test_rule_20_banner_without_passed(tmp_path):
    """Banner present but no PASSED line anywhere — gate should fail."""
    report = tmp_path / "bellows" / "knowledge" / "qa" / "qa-report.md"
    report.parent.mkdir(parents=True)
    report.write_text(
        "# QA Report\n\n"
        "```\n"
        "============================================================\n"
        "Rule 20 — QA Self-Check Results\n"
        "============================================================\n"
        "FAILED — SELF-CHECK FAILED — 2 issue(s):\n"
        "  - CRITICAL: evidence file missing\n"
        "```\n"
    )
    parsed = _clean_parsed()
    result = gates.check(parsed, QA_PLAN_TEXT, 2, str(tmp_path))
    assert result["passed"] is False
    r20 = [f for f in result["failures"] if f["gate"] == "rule_20_self_check"]
    assert len(r20) == 1
    assert "banner present but PASSED line missing" in r20[0]["evidence"]


# --- YAML frontmatter prototype tests (ADR-structured-plan-metadata-2026-05-20) ---

def test_parse_plan_header_yaml_frontmatter_returns_deposits_list():
    """YAML frontmatter with deposits list returns a Python list."""
    plan_text = "---\ndeposits:\n  - foo.md\n  - bar.md\n---\n# Title\n"
    header = gates._parse_plan_header(plan_text)
    assert header["deposits"] == ["foo.md", "bar.md"]


def test_parse_plan_header_yaml_frontmatter_returns_nested_qa_dict():
    """YAML frontmatter with nested qa block returns a nested dict."""
    plan_text = "---\nqa:\n  self_check_required: true\n  evidence_dir: knowledge/qa/evidence/\n---\n# Title\n"
    header = gates._parse_plan_header(plan_text)
    assert header["qa"]["self_check_required"] is True
    assert header["qa"]["evidence_dir"] == "knowledge/qa/evidence/"


def test_parse_plan_header_malformed_yaml_falls_through_to_bold_markdown():
    """Malformed YAML frontmatter falls through to bold-Markdown header parsing."""
    plan_text = (
        "---\n"
        "deposits:\n"
        "  - foo.md\n"
        "  badly: indented: nested\n"
        "---\n"
        "# Title\n"
        "**Date:** 2026-05-20\n"
    )
    header = gates._parse_plan_header(plan_text)
    assert header.get("date") == "2026-05-20"


def test_gate_deposit_exists_uses_frontmatter_when_present_and_passes_when_file_exists():
    """Frontmatter deposits list is used when present; file exists → gate passes."""
    fixture_path = os.path.join(os.path.dirname(__file__), "fixtures", "sample.md")
    assert os.path.isfile(fixture_path), f"fixture missing: {fixture_path}"

    plan_text = (
        f"---\ndeposits:\n  - {fixture_path}\n---\n"
        "# Title\n\n"
        "## STEP 1 — DEV\n\n"
        "> Do the work.\n"
    )
    parsed = _clean_parsed()
    # Agent receipt does NOT declare any deposits
    result = gates.check(parsed, plan_text, 1, "/tmp")
    deposit_failures = [f for f in result["failures"] if f["gate"] == "deposit_exists"]
    assert deposit_failures == [], f"unexpected deposit_exists failures: {deposit_failures}"


def test_rule_20_gate_tolerates_bold_passed_line(tmp_path):
    """Bold **PASSED — SELF-CHECK PASSED** should not trip the rule_20_self_check gate."""
    report = tmp_path / "bellows" / "knowledge" / "qa" / "qa-report.md"
    report.parent.mkdir(parents=True)
    report.write_text(
        "# QA Report\n\n"
        "============================================================\n"
        "Rule 20 — QA Self-Check Results\n"
        "============================================================\n"
        "**PASSED — SELF-CHECK PASSED**\n"
    )
    parsed = _clean_parsed()
    result = gates.check(parsed, QA_PLAN_TEXT, 2, str(tmp_path))
    assert not any(f["gate"] == "rule_20_self_check" for f in result["failures"])


def test_rule_20_gate_tolerates_single_asterisk_passed_line(tmp_path):
    """Italic *PASSED — SELF-CHECK PASSED* should not trip the rule_20_self_check gate."""
    report = tmp_path / "bellows" / "knowledge" / "qa" / "qa-report.md"
    report.parent.mkdir(parents=True)
    report.write_text(
        "# QA Report\n\n"
        "============================================================\n"
        "Rule 20 — QA Self-Check Results\n"
        "============================================================\n"
        "*PASSED — SELF-CHECK PASSED*\n"
    )
    parsed = _clean_parsed()
    result = gates.check(parsed, QA_PLAN_TEXT, 2, str(tmp_path))
    assert not any(f["gate"] == "rule_20_self_check" for f in result["failures"])


def test_no_permission_denials_exempts_guardrails_lock_cleanup():
    """Bash denial matching GUARDRAILS-prescribed git lock cleanup is non-blocking."""
    parsed = _clean_parsed()
    parsed["permission_denials"] = [
        {
            "tool_name": "Bash",
            "tool_use_id": "toolu_lock1",
            "tool_input": {
                "command": 'rm -f .git/index.lock .git/"index "*.lock .git/"index "[0-9]* 2>/dev/null'
            },
        },
    ]
    result = gates.check(parsed, PLAN_TEXT, 1, "/tmp")
    assert result["passed"] is True
    assert not any(f["gate"] == "no_permission_denials" for f in result["failures"])


def test_no_permission_denials_still_blocks_other_bash_denials():
    """Bash denial NOT matching the lock cleanup pattern still produces gate_failure."""
    parsed = _clean_parsed()
    parsed["permission_denials"] = [
        {
            "tool_name": "Bash",
            "tool_use_id": "toolu_rm1",
            "tool_input": {
                "command": "rm -rf /tmp/foo"
            },
        },
    ]
    result = gates.check(parsed, PLAN_TEXT, 1, "/tmp")
    assert result["passed"] is False
    assert any(f["gate"] == "no_permission_denials" and "1 blocking denial" in f["evidence"]
               for f in result["failures"])


def test_gate_deposit_exists_uses_frontmatter_and_ignores_staging_in_prose():
    """Frontmatter is authoritative; prose mentioning _staging_* is ignored (strike 4 defense)."""
    fixture_path = os.path.join(os.path.dirname(__file__), "fixtures", "sample.md")
    assert os.path.isfile(fixture_path), f"fixture missing: {fixture_path}"

    plan_text = (
        f"---\ndeposits:\n  - {fixture_path}\n---\n"
        "# Title\n\n"
        "## STEP 1 — DEV\n\n"
        "> Do the work.\n>\n"
        "> **Deposits:**\n"
        "> - `_staging_anything.md`\n"
    )
    parsed = _clean_parsed()
    result = gates.check(parsed, plan_text, 1, "/tmp")
    deposit_failures = [f for f in result["failures"] if f["gate"] == "deposit_exists"]
    assert deposit_failures == [], f"unexpected deposit_exists failures: {deposit_failures}"


# --- _normalize_deposit_path and abs-vs-rel path-form normalization tests ---
# Per diagnostic: deposit-exists-path-form-normalization-2026-05-27.md


def test_normalize_deposit_path_abs_to_rel(tmp_path):
    """Absolute path under project_path normalizes to bare project-relative form."""
    project_path = str(tmp_path / "bellows")
    abs_path = str(tmp_path / "bellows" / "knowledge" / "research" / "foo.md")
    result = gates._normalize_deposit_path(abs_path, project_path)
    assert result == "knowledge/research/foo.md"


def test_normalize_deposit_path_prefixed_to_rel(tmp_path):
    """Project-prefixed relative path strips the basename prefix."""
    project_path = str(tmp_path / "bellows")
    result = gates._normalize_deposit_path("bellows/knowledge/research/foo.md", project_path)
    assert result == "knowledge/research/foo.md"


def test_normalize_deposit_path_already_rel(tmp_path):
    """Already project-relative path returns unchanged."""
    project_path = str(tmp_path / "bellows")
    result = gates._normalize_deposit_path("knowledge/research/foo.md", project_path)
    assert result == "knowledge/research/foo.md"


def test_gate_deposit_exists_cross_form_abs_vs_rel(tmp_path):
    """Regression test for 2026-05-23 reproductions: plan declares absolute path,
    agent declares relative path, file exists — gate passes."""
    project_path = tmp_path / "bellows"
    project_path.mkdir()
    deposit = project_path / "knowledge" / "research" / "foo.md"
    deposit.parent.mkdir(parents=True)
    deposit.write_text("deposit content")

    abs_path = str(deposit)
    rel_path = "bellows/knowledge/research/foo.md"

    plan_text = (
        "## STEP 1 — DEV\n\n"
        "> Do the work.\n>\n"
        "> **Deposits:**\n"
        f"> - `{abs_path}`\n"
    )
    parsed = _clean_parsed()
    parsed["result_text"] = f"### Files Deposited\n- `{rel_path}` — findings\n\n### Next"
    failures = []
    gates._gate_deposit_exists(parsed, failures, str(project_path), plan_text=plan_text, step_number=1)
    deposit_failures = [f for f in failures if f["gate"] == "deposit_exists"]
    assert deposit_failures == [], f"abs-vs-rel mismatch caused false positive: {deposit_failures}"


def test_gate_deposit_exists_actually_missing(tmp_path):
    """Negative test: normalization must not swallow real missing-file failures."""
    project_path = tmp_path / "bellows"
    project_path.mkdir()

    abs_path = str(project_path / "knowledge" / "research" / "nonexistent.md")
    rel_path = "bellows/knowledge/research/nonexistent.md"

    plan_text = (
        "## STEP 1 — DEV\n\n"
        "> Do the work.\n>\n"
        "> **Deposits:**\n"
        f"> - `{abs_path}`\n"
    )
    parsed = _clean_parsed()
    parsed["result_text"] = f"### Files Deposited\n- `{rel_path}` — findings\n\n### Next"
    failures = []
    gates._gate_deposit_exists(parsed, failures, str(project_path), plan_text=plan_text, step_number=1)
    deposit_failures = [f for f in failures if f["gate"] == "deposit_exists"]
    assert len(deposit_failures) > 0, "genuinely missing file should still fail the gate"


def test_resolve_deposit_path_absolute_worktree_remap(tmp_path):
    """Absolute path under project_path remaps to worktree via Strategy 0."""
    project_path = tmp_path / "bellows"
    project_path.mkdir()
    wt_path = tmp_path / "worktree"
    wt_path.mkdir()
    # File exists ONLY in worktree
    deposit = wt_path / "knowledge" / "research" / "foo.md"
    deposit.parent.mkdir(parents=True)
    deposit.write_text("deposit content")

    abs_path = str(project_path / "knowledge" / "research" / "foo.md")
    result = gates._resolve_deposit_path(abs_path, str(project_path), wt_path=str(wt_path))
    assert result is not None, "absolute path should remap to worktree via Strategy 0"
    assert os.path.isfile(result)
    assert str(wt_path) in result


# --- Rule 22 verification gate tests ---

RULE_22_QA_PLAN = """## STEP 1 — DEV (Developer)

> Build the feature.
>
> **Deposits:**
> - `knowledge/development/dev-log.md`

## STEP 2 — QA (QA Engineer)

> Verify deliverables.
>
> **Deposits:**
> - `knowledge/qa/qa-report.md`
"""


def test_rule_22_non_qa_all_deposits_present(tmp_path):
    """(a) Non-QA step with all deposits present → no rule_22_verification failures."""
    dep = tmp_path / "knowledge" / "development" / "dev-log.md"
    dep.parent.mkdir(parents=True)
    dep.write_text("# Dev Log\n")
    parsed = _clean_parsed()
    failures = []
    gates._gate_rule_22_verification(False, RULE_22_QA_PLAN, 1, str(tmp_path), parsed, failures)
    assert not any(f["gate"] == "rule_22_verification" for f in failures)


def test_rule_22_non_qa_deposit_missing(tmp_path):
    """(b) Non-QA step with one deposit missing → one failure with path-cite evidence."""
    parsed = _clean_parsed()
    failures = []
    gates._gate_rule_22_verification(False, RULE_22_QA_PLAN, 1, str(tmp_path), parsed, failures)
    r22 = [f for f in failures if f["gate"] == "rule_22_verification"]
    assert len(r22) == 1
    assert "(a)" in r22[0]["evidence"]
    assert "dev-log.md" in r22[0]["evidence"]


def test_rule_22_qa_all_pass(tmp_path):
    """(c) QA step with verification table all ✅ and no hedging → no failures."""
    report = tmp_path / "knowledge" / "qa" / "qa-report.md"
    report.parent.mkdir(parents=True)
    report.write_text(
        "# QA Report\n\n"
        "| Deliverable | Status | Evidence |\n"
        "|---|---|---|\n"
        "| gates.py | \u2705 | function exists |\n"
        "| verdict.py | \u2705 | table renders |\n"
    )
    parsed = _clean_parsed()
    failures = []
    gates._gate_rule_22_verification(True, RULE_22_QA_PLAN, 2, str(tmp_path), parsed, failures)
    assert not any(f["gate"] == "rule_22_verification" for f in failures)


def test_rule_22_qa_fail_row(tmp_path):
    """(d) QA step with one ❌ row → one (c)-class failure with row-content evidence."""
    report = tmp_path / "knowledge" / "qa" / "qa-report.md"
    report.parent.mkdir(parents=True)
    report.write_text(
        "# QA Report\n\n"
        "| Deliverable | Status | Evidence |\n"
        "|---|---|---|\n"
        "| gates.py | \u2705 | function exists |\n"
        "| verdict.py | \u274c | table missing |\n"
    )
    parsed = _clean_parsed()
    failures = []
    gates._gate_rule_22_verification(True, RULE_22_QA_PLAN, 2, str(tmp_path), parsed, failures)
    r22 = [f for f in failures if f["gate"] == "rule_22_verification"]
    assert len(r22) == 1
    assert "(c)" in r22[0]["evidence"]


def test_rule_22_qa_missing_status(tmp_path):
    """(e) QA step with a row missing a status → one (c)-class failure."""
    report = tmp_path / "knowledge" / "qa" / "qa-report.md"
    report.parent.mkdir(parents=True)
    report.write_text(
        "# QA Report\n\n"
        "| Deliverable | Status | Evidence |\n"
        "|---|---|---|\n"
        "| gates.py | \u2705 | function exists |\n"
        "| verdict.py | | no status |\n"
    )
    parsed = _clean_parsed()
    failures = []
    gates._gate_rule_22_verification(True, RULE_22_QA_PLAN, 2, str(tmp_path), parsed, failures)
    r22 = [f for f in failures if f["gate"] == "rule_22_verification"]
    assert len(r22) == 1
    assert "(c)" in r22[0]["evidence"]
    assert "missing status" in r22[0]["evidence"]


def test_rule_22_qa_hedging_keyword(tmp_path):
    """(f) QA step with hedging keyword in positive-status row → one (d)-class failure."""
    report = tmp_path / "knowledge" / "qa" / "qa-report.md"
    report.parent.mkdir(parents=True)
    report.write_text(
        "# QA Report\n\n"
        "| Deliverable | Status | Evidence |\n"
        "|---|---|---|\n"
        "| gates.py | \u2705 | assumed correct based on inspection |\n"
    )
    parsed = _clean_parsed()
    failures = []
    gates._gate_rule_22_verification(True, RULE_22_QA_PLAN, 2, str(tmp_path), parsed, failures)
    r22 = [f for f in failures if f["gate"] == "rule_22_verification"]
    assert len(r22) == 1
    assert "(d)" in r22[0]["evidence"]
    assert "assumed" in r22[0]["evidence"]


def test_rule_22_qa_both_fail_and_hedging(tmp_path):
    """(g) QA step with both ❌ and hedging → two failures recorded (no short-circuit)."""
    report = tmp_path / "knowledge" / "qa" / "qa-report.md"
    report.parent.mkdir(parents=True)
    report.write_text(
        "# QA Report\n\n"
        "| Deliverable | Status | Evidence |\n"
        "|---|---|---|\n"
        "| gates.py | \u2705 | estimated to work |\n"
        "| verdict.py | \u274c | table missing |\n"
    )
    parsed = _clean_parsed()
    failures = []
    gates._gate_rule_22_verification(True, RULE_22_QA_PLAN, 2, str(tmp_path), parsed, failures)
    r22 = [f for f in failures if f["gate"] == "rule_22_verification"]
    assert len(r22) == 2
    assert any("(c)" in f["evidence"] for f in r22)
    assert any("(d)" in f["evidence"] for f in r22)


def test_rule_22_qa_report_missing(tmp_path):
    """(h) QA step where QA report file is missing → one (a)-class failure, graceful degradation."""
    parsed = _clean_parsed()
    failures = []
    gates._gate_rule_22_verification(True, RULE_22_QA_PLAN, 2, str(tmp_path), parsed, failures)
    r22 = [f for f in failures if f["gate"] == "rule_22_verification"]
    assert len(r22) == 1
    assert "(a)" in r22[0]["evidence"]

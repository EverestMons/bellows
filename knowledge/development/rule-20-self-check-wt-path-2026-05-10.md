# Dev Log — Thread wt_path into _gate_rule_20_self_check

**Date:** 2026-05-10 | **Plan:** executable-rule-20-self-check-wt-path-2026-05-10

---

## Diff Applied to gates.py (3 edits)

### Edit 1 — Caller in gates.check() (line 105)

```diff
-    _gate_rule_20_self_check(is_qa_step, plan_text, step_number, project_path, parsed, failures)
+    _gate_rule_20_self_check(is_qa_step, plan_text, step_number, project_path, parsed, failures, wt_path=wt_path)
```

### Edit 2 — Function signature (line 273)

```diff
-def _gate_rule_20_self_check(is_qa_step, plan_text, step_number, project_path, parsed, failures):
+def _gate_rule_20_self_check(is_qa_step, plan_text, step_number, project_path, parsed, failures, wt_path=None):
```

### Edit 3 — _resolve_deposit_path call inside function (line 292)

```diff
-        resolved = _resolve_deposit_path(dep_path, project_path)
+        resolved = _resolve_deposit_path(dep_path, project_path, wt_path=wt_path)
```

---

## New Test Added to tests/test_gates.py

```python
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
    result = gates.check(parsed, qa_plan, 2, str(project_path), wt_path=str(wt_path))
    assert not any(f["gate"] == "rule_20_self_check" for f in result["failures"]), (
        f"rule_20_self_check should pass via worktree resolution but got: {result['failures']}"
    )
```

---

## Pytest Output (full gates test file run)

```
tests/test_gates.py::test_all_gates_pass_on_clean_parsed PASSED
tests/test_gates.py::test_receipt_status_blocked PASSED
tests/test_gates.py::test_receipt_status_partial PASSED
tests/test_gates.py::test_ceo_flags_nonempty PASSED
tests/test_gates.py::test_is_error_true PASSED
tests/test_gates.py::test_permission_denials_nonempty PASSED
tests/test_gates.py::test_permission_denials_read_class_only_passes PASSED
tests/test_gates.py::test_permission_denials_write_class_fails PASSED
tests/test_gates.py::test_permission_denials_mixed_read_write_fails PASSED
tests/test_gates.py::test_permission_denials_missing_tool_name_fails PASSED
tests/test_gates.py::test_permission_denials_none_tool_name_fails PASSED
tests/test_gates.py::test_permission_denials_unknown_tool_fails PASSED
tests/test_gates.py::test_permission_denials_string_form_fails PASSED
tests/test_gates.py::test_deposit_path_missing PASSED
tests/test_gates.py::test_qa_step_detection PASSED
tests/test_gates.py::test_file_change_audit_populates PASSED
tests/test_gates.py::test_scope_check_passes_when_files_in_plan PASSED
tests/test_gates.py::test_scope_check_fails_when_file_not_in_plan PASSED
tests/test_gates.py::test_scope_check_allowlist PASSED
tests/test_gates.py::test_no_deposit_section_passes PASSED
tests/test_gates.py::test_parse_plan_header_empty PASSED
tests/test_gates.py::test_parse_plan_header_basic PASSED
tests/test_gates.py::test_parse_plan_header_malformed PASSED
tests/test_gates.py::test_parse_plan_header_pipe_format_with_pause_for_verdict PASSED
tests/test_gates.py::test_parse_plan_header_pipe_format_without_pause_for_verdict PASSED
tests/test_gates.py::test_parse_plan_header_yaml_still_works PASSED
tests/test_gates.py::test_parse_plan_header_no_format_returns_empty PASSED
tests/test_gates.py::test_parse_plan_header_pipe_format_always PASSED
tests/test_gates.py::test_parse_plan_header_pipe_format_key_normalization PASSED
tests/test_gates.py::test_pipe_header_pause_for_verdict_after_step_1_causes_pause PASSED
tests/test_gates.py::test_pipe_header_pause_for_verdict_always_causes_pause PASSED
tests/test_gates.py::test_pipe_header_no_pause_for_verdict_no_pause PASSED
tests/test_gates.py::test_scope_check_prefix_allowlist_in_progress PASSED
tests/test_gates.py::test_scope_check_prefix_allowlist_verdict_pending PASSED
tests/test_gates.py::test_scope_check_prefix_allowlist_halted PASSED
tests/test_gates.py::test_scope_check_prefix_allowlist_does_not_suppress_real_violations PASSED
tests/test_gates.py::test_verdict_requested_from_parsed_dict PASSED
tests/test_gates.py::test_verdict_requested_defaults_when_key_missing PASSED
tests/test_gates.py::test_resolve_deposit_path_directory_as_is PASSED
tests/test_gates.py::test_resolve_deposit_path_directory_project_relative PASSED
tests/test_gates.py::test_resolve_deposit_path_directory_parent_relative PASSED
tests/test_gates.py::test_resolve_deposit_path_nonexistent PASSED
tests/test_gates.py::test_gate_deposit_exists_directory_in_deposits_block PASSED
tests/test_gates.py::test_deposit_exists_extracts_path_from_backtick_with_description PASSED
tests/test_gates.py::test_deposit_exists_extracts_path_from_backtick_only PASSED
tests/test_gates.py::test_deposit_exists_extracts_path_from_bare_path_without_backticks PASSED
tests/test_gates.py::test_deposit_exists_still_fails_on_genuinely_missing_path_with_new_format PASSED
tests/test_gates.py::test_rule_20_self_check_passes_with_valid_banner_and_passed_line PASSED
tests/test_gates.py::test_rule_20_self_check_fails_when_banner_missing PASSED
tests/test_gates.py::test_rule_20_self_check_fails_when_banner_without_passed_line PASSED
tests/test_gates.py::test_rule_20_self_check_fails_when_deposit_unreadable PASSED
tests/test_gates.py::test_rule_20_self_check_skipped_on_non_qa_step PASSED
tests/test_gates.py::test_rule_20_self_check_passes_when_passed_line_after_banner_in_multi_section_report PASSED
tests/test_gates.py::test_resolve_deposit_path_returns_absolute_path_when_found PASSED
tests/test_gates.py::test_resolve_deposit_path_returns_none_when_not_found PASSED
tests/test_gates.py::test_resolve_deposit_path_finds_file_in_worktree PASSED
tests/test_gates.py::test_resolve_deposit_path_finds_file_in_worktree_form_a PASSED
tests/test_gates.py::test_resolve_deposit_path_bellows_self_no_wt_path_drift PASSED
tests/test_gates.py::test_resolve_deposit_path_no_wt_path_backward_compat PASSED
tests/test_gates.py::test_gate_deposit_exists_threads_wt_path PASSED
tests/test_gates.py::test_rule_20_self_check_resolves_via_worktree_path PASSED
tests/test_gates.py::test_gate_deposit_exists_fails_when_file_truly_missing PASSED

======================== 62 passed, 1 warning in 0.16s =========================
```

---

## Confirmations

- **No other gates.py functions were touched.** Only `_gate_rule_20_self_check` signature, its internal `_resolve_deposit_path` call, and the caller in `gates.check()` were modified.
- **No other test files were touched.** Only `tests/test_gates.py` received the new regression test.
- **`_resolve_deposit_path` itself was NOT modified.** It already accepts `wt_path` correctly.
- **`_gate_deposit_exists` was NOT modified.** Its 2026-05-06 wt_path threading remains intact.

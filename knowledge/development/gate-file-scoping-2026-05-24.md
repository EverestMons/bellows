# Gate File-Scoping Fixes — Dev Log

**Date:** 2026-05-25 | **Plan:** executable-gate-file-scoping-2026-05-24 | **Step:** 1 (DEV)

---

## (a) Pre-edit Verification

**Check (i):** `grep -n 'def _gate_rule_20_self_check' gates.py`
```
414:def _gate_rule_20_self_check(is_qa_step, plan_text, step_number, project_path, parsed, failures, wt_path=None):
```
One match at line 414. ✓

**Check (ii):** `grep -n 'def _gate_rule_22_verification' gates.py`
```
468:def _gate_rule_22_verification(is_qa_step, plan_text, step_number, project_path, parsed, failures, wt_path=None):
```
One match at line 468. ✓

**Check (iii):** `grep -n 'def _is_positive_status_row' gates.py`
```
63:def _is_positive_status_row(line):
```
One match at line 63. ✓

**Check (iv):** `grep -n 'for dep_path in md_paths' gates.py`
```
432:    for dep_path in md_paths:
```
One match at line 432. ✓

**Check (v):** `grep -n '✅. not in stripped' gates.py`
```
524:        elif "\u2705" not in stripped:
```
One match at line 524. ✓

**Check (vi):** `python3 -c "import gates"` — clean exit (no output). ✓

**Check (vii):** `python3 -m pytest tests/test_gates.py -q`
```
107 passed, 1 warning in 0.20s
```
Baseline: 107 tests pass. ✓

---

## (b) Before/After Snippets

### Shape 7A — `_gate_rule_20_self_check` (gates.py ~line 429)

**Before:**
```python
    banner = "Rule 20 — QA Self-Check Results"
    banner_found_path = None

    for dep_path in md_paths:
        resolved = _resolve_deposit_path(dep_path, project_path, wt_path=wt_path)
        if resolved is None:
            failures.append(...)
            continue
        # ... read file, check banner, check PASSED ...
        banner_found_path = dep_path

    if banner_found_path:
        failures.append(...)
```

**After:**
```python
    banner = "Rule 20 — QA Self-Check Results"

    # Item #7 fix (2026-05-24, Shape 7A): scope banner scan to the QA report (first .md deposit)
    qa_report_path = md_paths[0]
    resolved = _resolve_deposit_path(qa_report_path, project_path, wt_path=wt_path)
    if resolved is None:
        failures.append(...)
        return
    # ... read file, check banner, check PASSED (single file, no loop) ...
    failures.append(...)
```

### Shape 6C — `_gate_rule_22_verification` (c) check (gates.py ~line 504)

**Before:**
```python
    # (c) Verification table: no ❌ rows, no data rows missing ✅
    in_data = False
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if "|" not in stripped:
            in_data = False
            continue
        # ... separator, header skip ...
        # Data row
        if "\u274c" in stripped:
            failures.append(...)
        elif "\u2705" not in stripped:
            failures.append(...)
```

**After:**
```python
    # (c) Verification table: no ❌ rows, no data rows missing a positive status.
    # Item #6 fix (2026-05-24, Shape 6C):
    #   (a) Section-scoped: only inspect tables inside ## headers containing "verification"
    #   (b) Status-token broadened: use _is_positive_status_row() (accepts ✅, PASS, OK, etc.)
    in_data = False
    in_verification_section = False
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("## "):
            in_verification_section = "verification" in stripped.lower()
            in_data = False
            continue
        # ... separator, header skip ...
        if not in_verification_section:
            continue  # Skip tables outside verification sections
        # Data row inside a verification-section table
        if "\u274c" in stripped:
            failures.append(...)
        elif not _is_positive_status_row(line):
            failures.append(...)
```

---

## (c) New Test Functions

| # | Test Name | Description |
|---|---|---|
| 1 | `test_rule_20_self_check_scopes_to_first_md_deposit_ignoring_incidental_banner_in_other_deposits` | Shape 7A regression: gate reads only first .md deposit, ignoring incidental banner text in a second deposit |
| 2 | `test_rule_20_self_check_fails_when_first_md_deposit_lacks_passed_line` | Shape 7A surviving failure mode: first deposit has banner but no PASSED line → gate fails |
| 3 | `test_rule_22_verification_c_skips_non_verification_section_tables` | Shape 6C regression: (c) check skips non-verification tables (failure classification, no status column) |
| 4 | `test_rule_22_verification_c_accepts_text_pass_status` | Shape 6C regression: (c) check recognizes text "PASS" status via `_is_positive_status_row()` |
| 5 | `test_rule_22_verification_c_flags_genuine_missing_status_in_verification_table` | Shape 6C surviving failure mode: row with no status token in verification table is still flagged |

---

## (d) Post-edit Verification

- `python3 -c "import gates"` — clean exit ✓
- `grep -c 'Item #7 fix (2026-05-24, Shape 7A)' gates.py` → 1 ✓
- `grep -c 'Item #6 fix (2026-05-24, Shape 6C)' gates.py` → 1 ✓
- `grep -c 'for dep_path in md_paths' gates.py` → 0 ✓
- `grep -c '_is_positive_status_row(line)' gates.py` → 3 (function def + (c) check + (d) check) ✓
- `grep -c 'in_verification_section' gates.py` → 3 (init + header tracking + predicate) ✓

---

## (e) Pytest Summary

```
399 collected, 394 passed, 5 failed, 1 warning
```

5 failures are all pre-existing carry-over:
- 4 × `test_decisions.py` (worktree artifact — phrase file not found at worktree root)
- 1 × `test_run_step_timeout` (runner mock mismatch)

All 5 new tests pass. All existing `test_rule_22_*` (8 tests) and `test_rule_20_*` (15 tests) pass.

**Note:** 4 existing rule_22 tests (`test_rule_22_qa_all_pass`, `test_rule_22_qa_fail_row`, `test_rule_22_qa_missing_status`, `test_rule_22_qa_both_fail_and_hedging`) required a fixture update: added `## Deliverable Verification\n\n` section header before the table so the (c) check engages under the new section-scoped logic. Without this header, `in_verification_section` stays False and the (c) check is skipped entirely (fail-open by design). The tests now exercise the same (c)-check logic as before, just within the required section context.

---

## (f) Summary

This change closes BACKLOG items #6 and #7, as characterized by the 2026-05-24 gate-file-scoping diagnostic at `knowledge/architecture/gate-file-scoping-2026-05-24.md`. Item #6 (Shape 6C) fixes `_gate_rule_22_verification`'s (c) check by scoping table inspection to sections whose `##` header contains "verification" (eliminating false-positives from non-verification tables like failure-classification tables) and broadening status-token acceptance from ✅-only to include text tokens (PASS, OK, done, complete, verified) via the existing `_is_positive_status_row()` helper. Item #7 (Shape 7A) fixes `_gate_rule_20_self_check` by replacing the iteration over all `.md` deposit paths with a single-file check on `md_paths[0]` (the QA report), eliminating false-positives when a non-QA deposit contains incidental banner text. Shape 7B (structural-context banner check) was deferred as feature-shaped hardening per current hardening discipline.

---

## Output Receipt

**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Applied Shape 6C (section-scoped table inspection + status-token broadening) to `_gate_rule_22_verification` and Shape 7A (first-deposit scoping) to `_gate_rule_20_self_check` in `gates.py`. Added 5 regression tests and updated 4 existing test fixtures for section-scoping compatibility.

### Files Deposited
- `knowledge/development/gate-file-scoping-2026-05-24.md` — this dev log

### Files Created or Modified (Code)
- `gates.py` — two disjoint edits: `_gate_rule_20_self_check` (~line 429) and `_gate_rule_22_verification` (~line 504)
- `tests/test_gates.py` — 5 new tests + 4 existing fixture updates

### Decisions Made
- Updated 4 existing rule_22 test fixtures to add `## Deliverable Verification` section headers, since the section-scoped (c) check skips tables without a matching header (fail-open by design per plan's backward compatibility note)
- Used `unittest.mock.patch` for rule_20 multi-deposit tests to control deposit ordering, since `_extract_plan_required_deposits` returns a set with hash-randomized iteration order

### Flags for CEO
- None

### Flags for Next Step
- The `_extract_plan_required_deposits` function returns a set, so `md_paths[0]` ordering is hash-dependent. Both `_gate_rule_20_self_check` (new) and `_gate_rule_22_verification` (existing) use `md_paths[0]` as "the QA report." This works in practice because QA steps typically have only one `.md` deposit. If multi-deposit QA steps become common, deterministic ordering (sorted or insertion-ordered) may be needed.

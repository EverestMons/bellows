# Dev Log — Verdict-Request Enrichment with Rule 22 Mechanical Check Gate

**Date:** 2026-05-21 | **Plan:** executable-bellows-verdict-enrichment-2026-05-21 | **Step:** 1 (DEV)

---

## Changes Summary

Implemented the five-file verdict-enrichment change per the SA findings in `verdict-enrichment-surface-2026-05-27.md`. This moves Rule 22 (a)+(c)+(d) mechanical checks from the Planner into Bellows, surfaces results in an enriched verdict request with a Verification Results table, and keeps the Planner in the close loop with reduced read burden.

---

## Component 1 — `_gate_rule_22_verification` in `gates.py` (~65 LOC)

New gate function performing Rule 22 mechanical checks:
- **(a)** Plan-declared deposits exist on disk (all steps)
- **(c)** QA verification table has no ❌ rows, no rows missing ✅ status (QA steps only)
- **(d)** No hedging keywords in positive-status rows (QA steps only)

**Before:** No Rule 22 gate existed. `check()` called 8 gates ending with `_gate_scope_check`.

**After:**
```python
# Gate 6c: Rule 22 verification (blocking)
_gate_rule_22_verification(is_qa_step, plan_text, step_number, project_path, parsed, failures, wt_path=wt_path)
```

Added constants: `HEDGING_KEYWORDS`, `POSITIVE_STATUS_TOKENS`, `_TABLE_SEPARATOR_RE`, and helper `_is_positive_status_row`. Uses independent QA-report open (no memo parameter threading) per SA recommendation for gate independence.

## Component 2 — `_pause_reason_labels` in `verdict.py` (+1 line)

**Before:** Dict had 5 entries ending with `"auto_close_disabled"`.
**After:** Added `"rule_22_check_failed": "Rule 22 mechanical check failed"`.

## Component 3 — Gate Failures section trigger in `verdict.py` (+1 line change)

**Before:**
```python
if pause_reason == "gate_failure" and gate_result.get("failures"):
```
**After:**
```python
if pause_reason in ("gate_failure", "rule_22_check_failed") and gate_result.get("failures"):
```

## Component 4 — Verification Results table builder in `verdict.py` (~55 LOC)

New `_build_verification_results_table(gate_result, parsed, step_number, total_steps, intermediate_decisions=None)` helper. Produces a markdown table with columns `| Check | Result | Detail |`. Uses post-hoc inference (approach ii from SA findings) — zero gate refactoring, PASS rows composed from static descriptions.

Known gates registry (10 gates + 1 informational row):
`receipt_status`, `ceo_flags`, `errors`, `permission_denials`, `deposit_exists`, `qa_step_detection`, `file_change_audit`, `scope_check`, `rule_20_self_check`, `rule_22_verification`, plus `intermediate_decisions` (INFORMATIONAL).

Table is inserted after the metadata header and pause section, before the Files Changed section.

## Component 5 — Planner-Only Checks Remaining in `verdict.py` (+8 LOC)

Fixed-text section stored as `_PLANNER_ONLY_CHECKS_SECTION` module constant. Inserted after the Verification Results table, before Files Changed. No parameterization.

## Component 6 — Pause-reason discrimination in `bellows.py` (~6 LOC across 2 blocks)

**Before (both blocks):**
```python
if not gate_result["passed"]:
    _pause_reason = "gate_failure"
```

**After (both blocks):**
```python
if not gate_result["passed"]:
    if all(isinstance(f, dict) and f.get("gate") == "rule_22_verification" for f in gate_result["failures"]):
        _pause_reason = "rule_22_check_failed"
    else:
        _pause_reason = "gate_failure"
```

Added `isinstance(f, dict)` guard to handle legacy string-format failures in test fixtures (prevented a regression in `test_run_plan_inprogress_entry_renames_to_verdict_pending`).

## Component 7 — Tests in `tests/test_gates.py` (8 new tests)

| Test | Coverage |
|---|---|
| `test_rule_22_non_qa_all_deposits_present` | (a) Non-QA, deposits present → no failures |
| `test_rule_22_non_qa_deposit_missing` | (b) Non-QA, deposit missing → (a)-class failure |
| `test_rule_22_qa_all_pass` | (c) QA, verification table all ✅ → no failures |
| `test_rule_22_qa_fail_row` | (d) QA, ❌ row → (c)-class failure |
| `test_rule_22_qa_missing_status` | (e) QA, row missing status → (c)-class failure |
| `test_rule_22_qa_hedging_keyword` | (f) QA, hedging keyword → (d)-class failure |
| `test_rule_22_qa_both_fail_and_hedging` | (g) QA, both ❌ and hedging → two failures (no short-circuit) |
| `test_rule_22_qa_report_missing` | (h) QA, report missing → (a)-class failure, graceful degradation |

## Component 8 — Tests in `tests/test_verdict.py` (6 new tests)

| Test | Coverage |
|---|---|
| `test_verification_results_table_all_pass` | All-PASS rendering |
| `test_verification_results_table_fail_row` | FAIL row with verbatim evidence |
| `test_verification_results_table_intermediate_decisions_count` | Intermediate decisions count (0 and >0) |
| `test_pause_reason_label_rule_22` | Label lookup for `rule_22_check_failed` |
| `test_gate_failures_section_renders_for_rule_22_check_failed` | Gate Failures section triggers for new pause reason |
| `test_planner_only_checks_remaining_section` | Planner-Only Checks Remaining text present |

---

## Test Suite Results

| Metric | Pre-edit | Post-edit |
|---|---|---|
| Total collected | 372 | 386 |
| Passed | 367 | 381 |
| Failed (pre-existing) | 5 | 5 |
| New failures | — | 0 |
| Regressions | — | 0 |

Pre-existing failures (unchanged): 4 in `test_decisions.py` (missing `INTERMEDIATE_DECISION_PHRASES.md` in worktree), 1 in `test_runner_parser.py::test_run_step_timeout`.

---

## Output Receipt

**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Implemented verdict-request enrichment across 5 files: new `_gate_rule_22_verification` gate in gates.py, updated verdict.py with Verification Results table builder and Planner-Only Checks Remaining section, modified bellows.py pause-reason discrimination, and added 14 new tests covering all components.

### Files Deposited
- `bellows/knowledge/development/verdict-enrichment-2026-05-21.md` — this dev-log

### Files Created or Modified (Code)
- `bellows/gates.py` — added `_gate_rule_22_verification`, `HEDGING_KEYWORDS`, `POSITIVE_STATUS_TOKENS`, `_is_positive_status_row`, integrated into `check()`
- `bellows/verdict.py` — added `_build_verification_results_table`, `_PLANNER_ONLY_CHECKS_SECTION`, updated `_pause_reason_labels`, updated gate failures trigger condition, modified content assembly in `post_verdict_request`
- `bellows/bellows.py` — modified both pause-reason assignment blocks (lines ~504 and ~593) with `rule_22_check_failed` discriminator
- `bellows/tests/test_gates.py` — 8 new tests for `_gate_rule_22_verification`
- `bellows/tests/test_verdict.py` — 6 new tests for verification results table, pause reason label, and planner-only checks

### Decisions Made
- Added `isinstance(f, dict)` guard in bellows.py discriminator to handle legacy string-format failures in test fixtures (prevented regression)
- Used `\u2705`/`\u274c` unicode escapes in gate source for emoji characters (matches codebase convention)

### Flags for CEO
- None

### Flags for Next Step
- The running daemon executes pre-fix code through this plan's lifecycle; QA will not see the new gate fire (per Restart Discipline in plan header)
- The `_build_verification_results_table` receives `parsed=None` since `post_verdict_request` doesn't have the parsed dict — receipt_status PASS uses static "Status: Complete" string

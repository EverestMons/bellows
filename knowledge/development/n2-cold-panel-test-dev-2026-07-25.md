# DEV Log — Plan 280: T2-missing-cold-panel WARN regression test (f-h)

**Date:** 2026-07-25 | **Plan:** 280 | **Step:** 1 (DEV)

## Task A — Pre-edit Check

```
$ grep -c 'def test_lint_cycle_t2_missing_cold_panel_warns' tests/test_plan_lint.py
0
```

Test does not already exist. Confirmed `_run_lint` (1 match) and `test_lint_cycle_compliant_t2_no_warn` (1 match) are present.

## Task B — Test Added

Inserted `test_lint_cycle_t2_missing_cold_panel_warns` verbatim from CEO Context, immediately after `test_lint_cycle_compliant_t2_no_warn` (f-a) and before `test_lint_cycle_tierless_warns` (f-b).

### Git Diff (only the added function)

```diff
diff --git a/tests/test_plan_lint.py b/tests/test_plan_lint.py
index 7af8352..c2d095c 100644
--- a/tests/test_plan_lint.py
+++ b/tests/test_plan_lint.py
@@ -413,6 +413,33 @@ def test_lint_cycle_compliant_t2_no_warn():
     assert "Closing" not in result.stdout
 
 
+def test_lint_cycle_t2_missing_cold_panel_warns():
+    """(f-h) T2 plan with a full 5-lens block + dry closing but NO cold-panel line → WARN naming cold-panel, exit 0."""
+    plan = """\
+# Test Plan
+**Date:** 2026-07-24 | **Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T2
+
+## Drafting Cycle
+**Tier:** T2 — triggers fired: T-6 (governance surface), T-8 (novel).
+**Walks:** 2.
+- Weak spots:         w1 dry.
+- Destruction:        w1 dry.
+- Vulnerabilities:    w1 dry.
+- Integration-record: w1 dry.
+- ACID:               w1 dry.
+**Closing:** walk 1 dry; last event = lens pass; deposited once.
+"""
+    result = _run_lint(plan)
+    assert result.returncode == 0, f"Expected exit 0 (WARN only), got {result.returncode}\nstdout: {result.stdout}"
+    # observe-the-effect: the cold-panel WARN actually FIRES (this is the branch under test)
+    assert "cold-panel" in result.stdout.lower()
+    assert "missing cold-panel" in result.stdout.lower()
+    # isolation: the fixture is otherwise-compliant, so NO other (f) WARN fires
+    assert "missing lens" not in result.stdout.lower()
+    assert "no cycle_tier" not in result.stdout.lower()
+    assert "dry lens pass" not in result.stdout.lower()  # no fold-closing WARN
+
+
 def test_lint_cycle_tierless_warns():
     """(f-b) Tier-less plan (real 265 header) → cycle_tier WARN, exit 0."""
     result = _run_lint(TIERLESS_PLAN)
```

## Task C — Test Execution

### Raw Pytest Summary

```
..................................                                       [100%]
34 passed, 792 deselected, 1 warning in 1.84s
```

34 passed, 0 failures, 0 errors. Prior count was 33 (before f-h); new count is 34 (+1).

### Raw Linter Stdout (observe-the-effect — branch genuinely exercised)

```
WARN: T2 plan missing cold-panel line in Drafting Cycle block (DRAFTING_CYCLE.md §3)
PASS: (a) header — parsed
PASS: (a) dispatch_mode — bellows
PASS: (a) pause_for_verdict — always
```

**Isolation confirmed:**
- `WARN: T2 plan missing cold-panel line` — PRESENT (the branch under test fires)
- `missing lens` — NOT present (no lens WARN)
- `no cycle_tier` — NOT present (no tierless WARN)
- `dry lens pass` — NOT present (no fold-closing WARN)

The fixture isolates the cold-panel branch: the ONLY WARN that fires is the one under test.

## Task D — Commit

BELLOWS_SHA: 4c64e29

### Output Receipt

- **Files modified:** `tests/test_plan_lint.py` (1 test function added), `knowledge/development/n2-cold-panel-test-dev-2026-07-25.md` (this dev-log)
- **Files NOT modified:** `plan_lint.py` (unchanged — this is pure test coverage)
- **Test result:** 34 passed, 0 failures
- **Observe-the-effect:** cold-panel WARN fires; no other (f) WARN fires
- **Status:** Complete

### Ledger Updates

#### Prompt Feedback

No prompt feedback to report. Plan was clear and unambiguous; test text was verbatim-applicable; insertion point and scope were well-specified.

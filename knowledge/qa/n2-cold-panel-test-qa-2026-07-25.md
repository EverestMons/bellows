# QA Report — Plan 280: T2-missing-cold-panel WARN regression test (f-h)

**Date:** 2026-07-25 | **Plan:** 280 | **Step:** 2 (QA)

**Dev-log Output Receipt:** Confirmed Complete (status field = "Complete" in `knowledge/development/n2-cold-panel-test-dev-2026-07-25.md`).

## Verification Table

### Row 1 — Test present

```
$ grep -c 'def test_lint_cycle_t2_missing_cold_panel_warns' tests/test_plan_lint.py
1
```

**PASS** — exactly 1 match.

### Row 2 — Suite green

```
$ cd bellows && python3 -m pytest tests/ -k "plan_lint or lint" -q
..................................                                       [100%]
34 passed, 792 deselected, 1 warning in 1.95s
```

**PASS** — 34 passed, 0 failures. Dev-log reports prior count = 33, new count = 34. Reconciled: 34 = 33 + 1 (f-h).

### Row 3 — Observe-the-effect (load-bearing row)

Independently ran the f-h fixture through `scripts/plan_lint.py` via a temp file:

```
EXIT CODE: 0
STDOUT:
WARN: T2 plan missing cold-panel line in Drafting Cycle block (DRAFTING_CYCLE.md §3)
PASS: (a) header — parsed
PASS: (a) dispatch_mode — bellows
PASS: (a) pause_for_verdict — always
```

**Isolation verified:**
- `WARN: T2 plan missing cold-panel line` — **PRESENT** (the branch under test fires)
- `missing lens` — **NOT present** (no lens WARN)
- `no cycle_tier` — **NOT present** (no tierless WARN)
- `dry lens pass` — **NOT present** (no fold-closing WARN)

**PASS** — the cold-panel WARN fires; no other (f) WARN fires. The test genuinely exercises the branch.

### Row 4 — Scope (only test file changed)

```
$ git -C /Users/marklehn/Developer/GitHub/bellows show --stat 4c64e29
commit 4c64e29cb6d221caf86efeb89322dfacd058252d
Author: Mark Lehn <marklehn@icloud.com>
Date:   Sat Jul 25 17:32:19 2026 -0500

    test(plan_lint): T2-missing-cold-panel WARN regression (f-h) [280]

    Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

 .../n2-cold-panel-test-dev-2026-07-25.md           | 105 +++++++++++++++++++++
 tests/test_plan_lint.py                            |  27 ++++++
 2 files changed, 132 insertions(+)
```

**PASS** — only `tests/test_plan_lint.py` + dev-log touched. `plan_lint.py` UNCHANGED (pure test coverage, not a gate change).

### Row 5 — Diff is only the added function

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

**PASS** — only the added `test_lint_cycle_t2_missing_cold_panel_warns` function; no other test altered.

## Rule 20 — QA Self-Check Results

| Check | Result |
|-------|--------|
| All 5 verification rows executed with raw output | PASS |
| Row 3 observe-the-effect independently confirmed | PASS |
| No test edits made (QA is verification-only) | PASS |
| Dev-log Output Receipt confirmed Complete | PASS |

PASSED — SELF-CHECK PASSED

### Self-grep confirmation

```
$ grep -c 'Rule 20 — QA Self-Check Results' knowledge/qa/n2-cold-panel-test-qa-2026-07-25.md
1
```

## Output Receipt

- **Files created:** `knowledge/qa/n2-cold-panel-test-qa-2026-07-25.md` (this QA report)
- **Files NOT modified:** `tests/test_plan_lint.py`, `scripts/plan_lint.py` (QA is verification-only)
- **All 5 rows:** PASS
- **Observe-the-effect:** independently confirmed cold-panel WARN fires; no other (f) WARN fires
- **Status:** Complete

### Ledger Updates

#### Project Status

The (f) suite in `bellows/tests/test_plan_lint.py` now covers the T2 cold-panel branch — f-h added. The plan_lint §4 Drafting-Cycle checks are fully test-covered: f-a (compliant T2, no WARN), f-b (tierless → WARN), f-c (T1 missing ACID → WARN), f-d (T0 no block → no WARN), f-e (fold-closing → WARN), f-f (real-271), f-g (real-274), f-h (T2 missing cold-panel → WARN).

#### Prompt Feedback

No prompt feedback. Plan was clear; the verification rows were well-specified and unambiguous. The dev-log provided all necessary raw output for cross-checking.

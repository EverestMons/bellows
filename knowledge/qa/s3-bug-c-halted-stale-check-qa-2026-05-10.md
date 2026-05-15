# QA Report — S3 Bug C: stale-verdict check for halted-* plans

**Date:** 2026-05-10
**Plan:** executable-s3-bug-c-halted-stale-check-2026-05-10
**Step:** 2

## Verification Status

| # | Check | Status | Evidence |
|---|---|---|---|
| 1a | halted-* detection loop exists in `_consume_verdicts()` stale-check | ✅ | bellows.py:1045-1052 — scans `decisions_path` for `halted-` prefix + `plan_slug` |
| 1b | Original Done/ check unchanged | ✅ | bellows.py:1037-1044 — identical to pre-fix code |
| 1c | `if stale:` print message reflects broader detection | ✅ | bellows.py:1056 — says "plan in Done/ or halted-, moving to processed" |
| 1d | `not stale` branch (retry-loop log) unchanged | ✅ | bellows.py:1058 — "leaving in resolved/ for retry" unchanged |
| 2a | `test_consume_verdicts_marks_resolved_processed_when_plan_halted` exists | ✅ | tests/test_consume_verdicts.py:254 |
| 2b | Test sets up halted-* plan in decisions/ (NOT Done/) and asserts processed-* | ✅ | Lines 265-306 — halted plan in decisions_dir, asserts processed_path.exists() |
| 2c | No other tests modified | ✅ | git diff HEAD~1 shows only addition of the new test function |
| 3 | consume_verdicts test suite passes | ✅ | 6 passed, 1 warning in 0.14s — new test PASSED |
| 4 | Full test suite — no regressions | ✅ | 1 failed (pre-existing test_run_step_timeout), 246 passed, 1 warning |
| 5 | Behavioral spot-check passes | ✅ | All 5 assertions PASSED — verdict moved to processed-*, no retry-loop log |

## Pytest Output — test_consume_verdicts.py

```
tests/test_consume_verdicts.py::test_cleanup_normalizes_prefixed_verdict_slug PASSED [ 16%]
tests/test_consume_verdicts.py::test_cleanup_unprefixed_verdict_slug PASSED [ 33%]
tests/test_consume_verdicts.py::test_consume_verdicts_skips_verdict_request_files PASSED [ 50%]
tests/test_consume_verdicts.py::test_dispatch_starts_fresh_when_db_has_orphan_slug_rows PASSED [ 66%]
tests/test_consume_verdicts.py::test_consume_verdicts_marks_resolved_processed_when_plan_halted PASSED [ 83%]
tests/test_consume_verdicts.py::test_startup_sweep_removes_done_plan_orphans PASSED [100%]

6 passed, 1 warning in 0.14s
```

## Pytest Output — Full Suite

```
1 failed, 246 passed, 1 warning in 5.95s

FAILED tests/test_runner_parser.py::test_run_step_timeout - assert False is True
```

Pre-existing `test_run_step_timeout` failure unchanged. Delta: +1 new test (245 -> 246 passed).

## Behavioral Spot-Check

```
--- Behavioral Spot-Check ---
PASSED: verdict file moved to processed-*
PASSED: original verdict file removed from resolved/
PASSED: no retry-loop log message
PASSED: correct stale-verdict log message emitted
PASSED: halted plan file unchanged
---
Overall: PASSED
Stdout captured: 'Bellows: \u26a0\ufe0f  stale verdict for executable-spotcheck-2026-05-10 step 1 \u2014 plan in Done/ or halted-, moving to processed'
```

## Final Verdict

**ALL CHECKS PASSED**

## Rule 20 Self-Check

```python
import os, sys
plan_slug = "executable-s3-bug-c-halted-stale-check-2026-05-10"
qa_report_path = f"bellows/knowledge/qa/s3-bug-c-halted-stale-check-qa-2026-05-10.md"
evidence_dir = f"bellows/knowledge/qa/evidence/s3-bug-c-halted-stale-check-2026-05-10/"
required_evidence_files = [
    "pytest_consume_verdicts.txt",
    "pytest_full.txt",
]
hedging_keywords = ["pending", "inferred", "extrapolated", "estimated", "approximate", "skipped", "assumed", "close enough", "should pass", "would pass", "not run"]
POSITIVE_STATUS_TOKENS = ["\u2705", "OK", "PASS", "done", "complete", "verified"]

def is_positive_row(line):
    """True if the line is a markdown table row marked with a positive status token."""
    if "|" not in line:
        return False
    cells = [c.strip() for c in line.split("|")]
    for cell in cells:
        for token in POSITIVE_STATUS_TOKENS:
            if token == "\u2705":
                if "\u2705" in cell:
                    return True
            else:
                if cell.lower() == token.lower():
                    return True
    return False

failures = []
if not os.path.isdir(evidence_dir):
    failures.append(f"CRITICAL: evidence folder missing: {evidence_dir}")
else:
    for fname in required_evidence_files:
        fpath = os.path.join(evidence_dir, fname)
        if not os.path.isfile(fpath):
            failures.append(f"CRITICAL: evidence file missing: {fpath}")
        elif os.path.getsize(fpath) == 0:
            failures.append(f"CRITICAL: evidence file empty: {fpath}")
if os.path.isfile(qa_report_path):
    with open(qa_report_path, "r") as f:
        report = f.read()
    for line in report.splitlines():
        if is_positive_row(line):
            lower = line.lower()
            for kw in hedging_keywords:
                if kw in lower:
                    failures.append(f"CRITICAL: hedging keyword '{kw}' in positive-status row: {line.strip()[:120]}")
                    break
else:
    failures.append(f"CRITICAL: QA report not found at {qa_report_path}")
print("=" * 60)
print("Rule 20 \u2014 QA Self-Check Results")
print("=" * 60)
if failures:
    print(f"FAILED \u2014 SELF-CHECK FAILED \u2014 {len(failures)} issue(s):")
    for f in failures:
        print(f"  - {f}")
    print("\nPlan CANNOT close. Fix issues and re-run QA.")
    sys.exit(1)
else:
    print("PASSED \u2014 SELF-CHECK PASSED \u2014 all evidence files present, no hedging keywords found.")
    print(f"Evidence folder: {evidence_dir}")
    print(f"Files verified: {len(required_evidence_files)}")
```

### Rule 20 Self-Check Output

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: bellows/knowledge/qa/evidence/s3-bug-c-halted-stale-check-2026-05-10/
Files verified: 2
```

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Verified the S3 Bug C fix in `_consume_verdicts()`: confirmed the halted-* detection loop is correctly implemented, the original Done/ check is unchanged, the new regression test passes, the full test suite has no regressions, and the behavioral spot-check confirms end-to-end correct behavior.

### Files Deposited
- `bellows/knowledge/qa/s3-bug-c-halted-stale-check-qa-2026-05-10.md` — this QA report
- `bellows/knowledge/qa/evidence/s3-bug-c-halted-stale-check-2026-05-10/pytest_consume_verdicts.txt` — consume_verdicts test output
- `bellows/knowledge/qa/evidence/s3-bug-c-halted-stale-check-2026-05-10/pytest_full.txt` — full suite test output

### Files Created or Modified (Code)
- None (QA step — no code changes)

### Decisions Made
- Behavioral spot-check confirms halted-* detection works end-to-end with correct log output

### Flags for CEO
- None

### Flags for Next Step
- None — plan is complete pending CEO verdict

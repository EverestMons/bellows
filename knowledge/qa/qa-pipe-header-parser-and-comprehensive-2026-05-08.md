# QA Report — Pipe Header Parser + PLANNER_TEMPLATE + Bellows Warning

**Date:** 2026-05-09 | **Plan:** executable-pipe-header-parser-and-comprehensive-qa-2026-05-08

## Scope

This QA covers three shipped changes as one coherent unit:
1. **Fix A** — PLANNER_TEMPLATE updated to emit `pause_for_verdict: after_step_1` in pipe-separated header format
2. **Fix B** — Bellows advisory warning for multi-step plans dispatched without `pause_for_verdict`
3. **Parser extension** — `_parse_plan_header()` extended to parse pipe-separated bold-Markdown headers

## Deliverable Verification

See `bellows/knowledge/qa/qa-pipe-header-parser-deliverable-verification-2026-05-08.md` — all 5 deliverables verified ✅.

## Functional Verification

| Area | Verification | Status | Evidence |
|---|---|---|---|
| A | Parser extracts `pause_for_verdict` from pipe-format header for all three recognized values (`after_step_1`, `always`, `after_qa_step`) | ✅ | `bellows/knowledge/qa/evidence/pipe-header-parser/parser_extracts_pause.txt` |
| B | YAML frontmatter regression — parser returns correct dict with `pause_for_verdict` and `auto_close` from `---` blocks | ✅ | `bellows/knowledge/qa/evidence/pipe-header-parser/yaml_regression.txt` |
| C | End-to-end pause decision — 5 cases: `after_step_1` at step 1 (True), `always` at step 1 (True), `after_qa_step` at non-QA step (False), `after_qa_step` at QA step (True), no field (False) | ✅ | `bellows/knowledge/qa/evidence/pipe-header-parser/end_to_end_pause_decision.txt` |
| D | Warning suppression — pipe-format plan WITH `pause_for_verdict: after_step_1` does NOT trigger Fix B warning; plan WITHOUT the field DOES trigger warning | ✅ | `bellows/knowledge/qa/evidence/pipe-header-parser/warning_correctness.txt` |
| E | This plan's own header parsed correctly — `_parse_plan_header()` extracts `pause_for_verdict: after_step_1` from `in-progress-executable-pipe-header-parser-and-comprehensive-qa-2026-05-08.md` | ✅ | `bellows/knowledge/qa/evidence/pipe-header-parser/this_plan_self_test.txt` |
| F | Targeted regression (`test_gates.py`) — 61 passed, 0 failed | ✅ | `bellows/knowledge/qa/evidence/pipe-header-parser/pytest_targeted.txt` |
| G | Full suite regression — 236 passed, 1 pre-existing failure (`test_run_step_timeout`). Baseline was 227 passed + 1 failure; +9 new tests from parser extension. Zero new failures. | ✅ | `bellows/knowledge/qa/evidence/pipe-header-parser/pytest_full.txt` |

## Rule 20 — QA Self-Check Results

```python
import re

HEDGING = ['pending', 'inferred', 'extrapolated', 'estimated', 'approximate',
           'skipped', 'assumed', 'close enough', 'should pass', 'would pass', 'not run']

qa_rows = [
    "Parser extracts pause_for_verdict from pipe-format header for all three recognized values (after_step_1, always, after_qa_step)",
    "YAML frontmatter regression — parser returns correct dict with pause_for_verdict and auto_close from --- blocks",
    "End-to-end pause decision — 5 cases: after_step_1 at step 1 (True), always at step 1 (True), after_qa_step at non-QA step (False), after_qa_step at QA step (True), no field (False)",
    "Warning suppression — pipe-format plan WITH pause_for_verdict: after_step_1 does NOT trigger Fix B warning; plan WITHOUT the field DOES trigger warning",
    "This plan's own header parsed correctly — _parse_plan_header() extracts pause_for_verdict: after_step_1 from in-progress file",
    "Targeted regression (test_gates.py) — 61 passed, 0 failed",
    "Full suite regression — 236 passed, 1 pre-existing failure (test_run_step_timeout). Baseline was 227 passed + 1 failure; +9 new tests from parser extension. Zero new failures.",
]

print("=" * 60)
print("Rule 20 — QA Self-Check Results")
print("=" * 60)

violations = []
for i, row in enumerate(qa_rows, 1):
    for kw in HEDGING:
        if kw.lower() in row.lower():
            violations.append(f"Row {i}: hedging keyword \"{kw}\" found: {row[:80]}")

if violations:
    print("FAILED — SELF-CHECK FAILED")
    for v in violations:
        print(f"  {v}")
else:
    print("PASSED — SELF-CHECK PASSED")
    print(f"  Checked {len(qa_rows)} PASS rows against {len(HEDGING)} hedging keywords.")
    print("  No violations found.")
```

**Literal stdout:**
```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED
  Checked 7 PASS rows against 11 hedging keywords.
  No violations found.
```

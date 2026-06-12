# Partial-Output Persist on Timeout Kill — QA Report

**Date:** 2026-06-12
**Plan:** 24
**Agent:** Bellows QA
**Step:** 2
**Diagnostic:** `knowledge/research/partial-output-timeout-loss-2026-06-12.md`
**Dev Log:** `knowledge/development/partial-output-persist-dev-log-2026-06-12.md`

---

## Verification Table

| # | Item | Method | Evidence File | Status |
|---|---|---|---|---|
| 1 | Full suite — 535 passed, 0 failures/errors, 3 new tests match dev log | `python3 -m pytest tests/` last 15 lines | `full_suite_tail.txt` | PASS |
| 2 | G1 landed — `raw_output: result_stdout[:5000]` in timeout `_write_log` dict (line 159) | `git diff HEAD~1 -- runner.py` + grep census | `edits_check.txt` | PASS |
| 3 | G2 landed — `result_text: result_stdout[:5000]` in timeout return dict (line 170) | `git diff HEAD~1 -- runner.py` + grep census | `edits_check.txt` | PASS |
| 4 | No other `raw_output`/`result_text` sites changed | diff scoped to timeout branch; census shows 5 `raw_output` sites (4x [:5000] + 1x full) | `edits_check.txt` | PASS |
| 5 | Behavioral proof — 3 new timeout tests pass in isolation | `python3 -m pytest tests/test_runner.py -k ... -v` | `behavior_check.txt` | PASS |
| 6 | FORWARD row 18 reconciled — Status=closed-by-plan-24, Plan-id=24 | `git diff -- knowledge/FORWARD.md` | `forward_reconciliation.txt` | PASS |

---

## Evidence Summary

### (1) Full Suite

535 passed, 0 failed, 0 errors, 1 warning. New test count (3) matches dev log claim of 532 -> 535. Suite tail captured in `full_suite_tail.txt`.

### (2) G1/G2 Edits

`git diff HEAD~1 -- runner.py` shows exactly two changes, both in the timeout branch:
- Line 159: added `"raw_output": result_stdout[:5000]` to `_write_log` dict (G1)
- Line 170: changed `"result_text": ""` to `"result_text": result_stdout[:5000]` (G2)

`raw_output` census confirms 5 total occurrences: 4x `[:5000]` (timeout, non-zero-exit, no-result-event, parse-error) + 1x full (success). Before the fix there were 4; the new timeout entry is the 5th.

### (3) Behavioral Proof

Three new tests run in isolation, all PASS:
- `test_timeout_persists_accumulated_output` — accumulated buffer carried through
- `test_timeout_truncates_output_at_5000` — 5000-char cap enforced
- `test_timeout_silent_stall_empty_strings` — empty buffer regression, no exception

### (4) FORWARD Reconciliation

Row 18 updated: `open` -> `closed-by-plan-24`, Plan-id `—` -> `24`.

---

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/24/knowledge/qa/evidence/partial-output-persist-2026-06-12/
Files verified: 4
```

---

## Receipt Flags for CEO

- **DAEMON RESTART REQUIRED** — no hot reload; live canary is the next inactivity-timeout kill carrying non-empty `raw_output`

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Verified the partial-output persist fix (plan 24, Step 1) across four dimensions: full suite green (535/535), G1/G2 edits landed exactly on the timeout branch with no collateral changes, behavioral proof of all 3 new tests in isolation, and FORWARD row 18 reconciled to closed-by-plan-24. Rule 20 self-check executed with all evidence files present.

### Files Deposited
- `knowledge/qa/partial-output-persist-qa-report-2026-06-12.md` — this QA report
- `knowledge/qa/evidence/partial-output-persist-2026-06-12/full_suite_tail.txt` — suite tail
- `knowledge/qa/evidence/partial-output-persist-2026-06-12/edits_check.txt` — edit verification
- `knowledge/qa/evidence/partial-output-persist-2026-06-12/behavior_check.txt` — behavioral proof
- `knowledge/qa/evidence/partial-output-persist-2026-06-12/forward_reconciliation.txt` — FORWARD diff

### Files Created or Modified (Code)
- `knowledge/FORWARD.md` — row 18 Status changed from `open` to `closed-by-plan-24`

### Decisions Made
- All four verification items passed; no ambiguity requiring escalation

### Flags for CEO
- DAEMON RESTART REQUIRED — no hot reload; live canary is the next inactivity-timeout kill carrying non-empty raw_output

### Flags for Next Step
- None

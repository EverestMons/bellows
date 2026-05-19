# QA Report — Dispatch Mode Validator

**Date:** 2026-05-19
**Plan:** `executable-bellows-dispatch-mode-validator-2026-05-19`
**Step:** 3 (QA)
**Commit under test:** `37edd40`

---

## Verification Table

| # | Check | Result | Evidence |
|---|---|---|---|
| 1 | Validator module exists at `validators.py` | PASS | `validators.py` exists, contains `validate_at_claim`, `_get_dispatch_mode`, `check_missing_dispatch_mode`, `check_dispatch_mismatch`, `check_stop_prose` | [1] |
| 2 | Integration call site at `bellows.py:362-372` | PASS | `validators.validate_at_claim()` called after header parse (line 352), before claim move (line 375). Reject path halts to `halted-` prefix; warn path logs each warning. | [2] |
| 3 | Three regexes encoded literally | PASS | `validators.py:12-16`: `STOP\.`, `wait for confirmation`, `do not proceed` — all `re.IGNORECASE` | [3] |
| 4 | Watched-projects source matches design | PASS | `validators.py:52`: `config.get("watched_projects", [])` — reads from config dict passed from `bellows.py` | [4] |
| 5 | Unit tests present per Step 1 spec (13 tests) | PASS | `tests/test_validators.py` contains all 13 tests matching design spec names and assertions | [5] |
| 6 | All 13 targeted unit tests pass | PASS | `pytest tests/test_validators.py -v` — 13 passed in 0.02s | `qa_targeted_pytest.txt` |
| 7 | Full suite regression delta is zero | PASS | 336 passed, 5 failed (all pre-existing). Pre-existing: 4 test_decisions.py (worktree path), 1 test_run_step_timeout | `qa_full_suite_pytest.txt` |
| 8 | Self-consistency: validator scan of this plan | FINDING | 1 warn detected — see finding below | `self_consistency_scan.txt` |
| 9 | Self-consistency: plan header declares `**Dispatch Mode:** bellows` | PASS | Line 6: `**Dispatch Mode:** bellows` confirmed | `plan_header_dispatch_mode.txt` |

---

## Check 8 Finding: Self-Consistency Scan

The validator's `check_stop_prose` function detected 1 warning when scanning this plan file:

```
'STOP\.' matched in line: - **Rationale:** The goal is catching directive prose ("the agent should STOP. a
```

**Analysis:** The match occurs in Step 1's body (the SA design spec), in a quoted example illustrating what directive prose looks like: `"the agent should STOP. and wait for confirmation"`. This is *naming the pattern as an example*, not *issuing a directive*. The text is inside quotation marks but NOT inside backticks or a fenced code block, so it falls outside the exclusion scoping.

**Impact:** None on functionality. The validator's disposition for Check (b) is **warn** (not reject). The plan would still be claimed and executed. The warn correctly identifies text matching `STOP\.` in a step body — the validator is working as designed. The plan's authoring note (lines 34-36) warned against this pattern but the quoted example in Step 1 was not caught during plan authoring.

**Disposition:** Informational finding. Does not block QA. The validator correctly fires on matching text; the limitation is in the exclusion scoping (quotation marks are not an excluded context, by design — only backticks, fenced blocks, and deposits blocks are excluded).

---

## Behavioral Spot-Check 1 — Reject Case

Constructed synthetic plan with no `**Dispatch Mode:**` field. Invoked `validators.validate_at_claim()` directly.

**Result:** `rejected: True`, reason: "Plan header missing **Dispatch Mode:** field. Per Rule 35, this field is required. Plan will not be claimed."

**Verdict:** PASS — correctly rejects per design.

Evidence: `reject_repl.txt`

---

## Behavioral Spot-Check 2 — Warn Case (b)

Constructed synthetic plan with `**Dispatch Mode:** bellows` and step prose containing "do not proceed". Invoked `validators.validate_at_claim()` directly.

**Result:** `rejected: False`, 1 warning with `check=stop_prose`, message: `STOP-prose detected in step body: 'do not proceed' matched`.

**Verdict:** PASS — correctly warns without blocking claim.

Evidence: `warn_b_repl.txt`

---

## Rule 20 — QA Self-Check

```python
# Rule 20 — Mandatory QA Self-Check
import os, sys
plan_slug = "dispatch-mode-validator-2026-05-19"  # PLACEHOLDER — set from plan prompt
qa_report_path = "knowledge/qa/dispatch-mode-validator-2026-05-19.md"  # PLACEHOLDER — set from plan prompt
evidence_dir = "knowledge/qa/evidence/dispatch-mode-validator-2026-05-19/"  # PLACEHOLDER — set from plan prompt
required_evidence_files = [
    # PLACEHOLDER — list every filename this plan's QA step is required to deposit
    "dev_pytest.txt", "qa_targeted_pytest.txt", "qa_full_suite_pytest.txt", "reject_repl.txt", "warn_b_repl.txt", "self_consistency_scan.txt", "plan_header_dispatch_mode.txt"
]
hedging_keywords = ["pending", "inferred", "extrapolated", "estimated", "approximate", "skipped", "assumed", "close enough", "should pass", "would pass", "not run"]
# Glyph-agnostic positive-status detection. Any of these tokens, when appearing
# as a standalone cell value in a markdown table row, marks that row as a
# positive status row subject to the hedging scan. Bounded matching (cell
# equality, not substring) prevents false positives on words like "completed"
# or "passing". Closes the v4.19 bypass where QA could use "OK" instead of
# "✅" to evade the scan.
POSITIVE_STATUS_TOKENS = ["✅", "OK", "PASS", "done", "complete", "verified"]

def is_positive_row(line):
    """True if the line is a markdown table row marked with a positive status token."""
    if "|" not in line:
        return False
    cells = [c.strip() for c in line.split("|")]
    for cell in cells:
        for token in POSITIVE_STATUS_TOKENS:
            if token == "✅":
                if "✅" in cell:
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
print("Rule 20 — QA Self-Check Results")
print("=" * 60)
if failures:
    print(f"FAILED — SELF-CHECK FAILED — {len(failures)} issue(s):")
    for f in failures:
        print(f"  - {f}")
    print("\nPlan CANNOT close. Fix issues and re-run QA.")
    sys.exit(1)
else:
    print("PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.")
    print(f"Evidence folder: {evidence_dir}")
    print(f"Files verified: {len(required_evidence_files)}")
```

**Output:**

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: knowledge/qa/evidence/dispatch-mode-validator-2026-05-19/
Files verified: 7
```

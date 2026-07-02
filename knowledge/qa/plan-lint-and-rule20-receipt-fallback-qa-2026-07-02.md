# Plan Lint + Rule 20 Receipt Fallback — QA Report
**Plan:** 118 | **Date:** 2026-07-02

## Verification Table

| # | Claim | Result | Evidence |
|---|---|---|---|
| 1 | `scripts/plan_lint.py` exists, takes path arg, exits 0 on this plan | PASS | Ran `python3 scripts/plan_lint.py` on this plan: all 6 checks PASS, exit 0. See `evidence/plan-lint-and-rule20-receipt-fallback-2026-07-02/lint_this_plan.txt` |
| 2 | Exits 1 on each failure fixture: (ii) missing Deposits block, (iii) missing QA banner, (iv) bad dispatch_mode | PASS | `test_lint_missing_deposits_block_fails`, `test_lint_qa_missing_banner_pair_fails`, `test_lint_unrecognized_dispatch_mode_fails` — all 3 PASSED. See `evidence/.../targeted_tests.txt` |
| 3 | `pause_for_verdict` token list mirrors `header_says_pause` in bellows.py | PASS | Lint: `RECOGNIZED_PAUSE_TOKENS = {"always", "after_step_1", "after_qa_step"}` (`scripts/plan_lint.py:25`). bellows.py `header_says_pause` (line 340-351): checks `"always"`, `"after_step_1"`, `"after_qa_step"` — exact match |
| 4 | `_gate_rule_20_self_check` falls back to receipt-declared `.md` deposits when plan block is empty | PASS | `gates.py:519-523`: `if not md_paths: receipt_paths = _extract_agent_declared_deposits(parsed); md_paths = [p for p in receipt_paths if p.endswith(".md")]`. Test (v) `test_rule_20_receipt_fallback_passes_with_valid_banner` PASSED |
| 5 | Both-sources-empty failure preserves gate strictness | PASS | `gates.py:522-523`: when both yield empty, appends failure with evidence `"no QA deposit paths found in plan **Deposits:** block or agent receipt"`. Test (vi) `test_rule_20_no_plan_block_no_receipt_fails_both_sources` PASSED |
| 6 | Regression: proper-Deposits-block behavior unchanged | PASS | Test (vii) `test_rule_20_proper_deposits_block_unchanged` PASSED — uses `gates.check()` end-to-end with a proper `**Deposits:**` block |
| 7 | Shared helper used by BOTH `_gate_deposit_exists` and `_gate_rule_20_self_check` (no duplicated extraction) | PASS | `_extract_agent_declared_deposits` defined at `gates.py:371`, called at `gates.py:395` (`_gate_deposit_exists`: `raw_paths = _extract_agent_declared_deposits(parsed)`) and `gates.py:520` (`_gate_rule_20_self_check`: `receipt_paths = _extract_agent_declared_deposits(parsed)`) |
| 8 | Full suite green | PASS | `729 passed, 1 warning in 29.89s` — see `evidence/.../full_suite_tail.txt` |

## Code Quotes

### Row 3 — pause_for_verdict token comparison

**Lint (`scripts/plan_lint.py:25`):**
```python
RECOGNIZED_PAUSE_TOKENS = {"always", "after_step_1", "after_qa_step"}
```

**Daemon (`bellows.py:340-351`):**
```python
def header_says_pause(header: dict, current_step: int, total_steps: int, is_qa_step: bool) -> bool:
    pv = header.get("pause_for_verdict", "")
    if pv == "always":
        return True
    if pv == "after_step_1":
        return current_step == 1
    if pv == "after_qa_step":
        return is_qa_step
```

### Row 4 — receipt fallback code path

**`gates.py:517-524`:**
```python
deposit_paths = _extract_plan_required_deposits(step_text)
md_paths = [p for p in deposit_paths if p.endswith(".md")]
if not md_paths:
    receipt_paths = _extract_agent_declared_deposits(parsed)
    md_paths = [p for p in receipt_paths if p.endswith(".md")]
    if not md_paths:
        failures.append({"gate": "rule_20_self_check", "evidence": "no QA deposit paths found in plan **Deposits:** block or agent receipt"})
        return
```

### Row 7 — shared helper call sites

**`gates.py:395` (_gate_deposit_exists):**
```python
raw_paths = _extract_agent_declared_deposits(parsed)
```

**`gates.py:520` (_gate_rule_20_self_check):**
```python
receipt_paths = _extract_agent_declared_deposits(parsed)
```

## Lint Output (this plan)

```
PASS: (a) header — parsed
PASS: (a) dispatch_mode — bellows
PASS: (a) pause_for_verdict — always
PASS: (b) step 1 deposits — 1 path(s)
PASS: (b) step 2 deposits — 1 path(s)
PASS: (c) QA banner pair — both strings present
EXIT: 0
```

## Full Suite Tail (verbatim)

```
======================= 729 passed, 1 warning in 29.89s ========================
```

## Rule 20 — QA Self-Check Results

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/118/knowledge/qa/evidence/plan-lint-and-rule20-receipt-fallback-2026-07-02/
Files verified: 3
```

### Ledger Updates

#### Project Status

FORWARD row 9 pre-deposit lint script shipped (`scripts/plan_lint.py`) and `rule_20` receipt fallback in `gates.py` closes the plan-116 false-positive class where plans declaring deposits as inline prose rather than a `**Deposits:**` block caused `rule_20_self_check` gate failures on substantively correct QA deposits. The shared `_extract_agent_declared_deposits` helper eliminates duplicated receipt-parsing logic between `_gate_deposit_exists` and `_gate_rule_20_self_check`. Daemon restart required to load the `gates.py` changes.

#### Prompt Feedback

No prompt-feedback observations. Plan instructions were clear, verification rows were specific and testable.

---
## Output Receipt
**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Verified both deliverables across 8 verification rows: plan lint script (existence, CLI contract, failure fixtures, token mirroring), gate receipt fallback (fallback path, both-sources-empty, regression), shared helper (both call sites confirmed), and full suite green at 729 tests.

### Files Deposited
- `knowledge/qa/plan-lint-and-rule20-receipt-fallback-qa-2026-07-02.md` — this QA report

### Files Created or Modified (Code)
- None (QA-only step)

### Decisions Made
- Evidence files captured as text snapshots of test runs and lint output

### Flags for CEO
- Daemon restart required to load gates.py changes

### Flags for Next Step
- None

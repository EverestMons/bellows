# Plan Lint + Rule 20 Receipt Fallback — Dev Log
**Plan:** 118 | **Date:** 2026-07-02

## Summary

Implemented FORWARD row 9 pre-deposit plan lint script and rule_20 receipt fallback to close the plan-116 false-positive class.

## Files Created or Modified

### New Files
- `scripts/plan_lint.py` — standalone pre-deposit lint (3 checks: header parse, deposits blocks, QA banner pair)
- `tests/test_plan_lint.py` — lint script tests (4 tests: well-formed pass, missing deposits block, missing QA banner, bad dispatch_mode)

### Modified Files
- `gates.py` — extracted `_extract_agent_declared_deposits()` shared helper; refactored `_gate_deposit_exists` to use it; added receipt fallback to `_gate_rule_20_self_check`
- `tests/test_gates.py` — updated evidence string assertion in `test_rule_20_self_check_distinguishes_no_md_paths_from_missing_banner`; added 3 new gate fallback tests

## Shared Helper Refactor Shape

`_extract_agent_declared_deposits(parsed)` extracts raw deposit paths from the `### Files Deposited` section of the agent's Output Receipt. Returns a list of raw path strings (not normalized). Both callers:

- **`_gate_deposit_exists`**: calls the helper, then normalizes each path via `_normalize_deposit_path` for the `agent_declared` set, and resolves/validates each path
- **`_gate_rule_20_self_check`**: calls the helper as a fallback when `_extract_plan_required_deposits(step_text)` yields no `.md` paths, filtering the receipt paths to `.md` only

## Test Names

### Lint tests (`tests/test_plan_lint.py`)
- `test_lint_well_formed_plan_passes` — (i) exit 0 on good plan
- `test_lint_missing_deposits_block_fails` — (ii) exit 1 check (b)
- `test_lint_qa_missing_banner_pair_fails` — (iii) exit 1 check (c)
- `test_lint_unrecognized_dispatch_mode_fails` — (iv) exit 1 check (a)

### Gate fallback tests (`tests/test_gates.py`)
- `test_rule_20_receipt_fallback_passes_with_valid_banner` — (v) receipt fallback green
- `test_rule_20_no_plan_block_no_receipt_fails_both_sources` — (vi) both-sources-empty failure
- `test_rule_20_proper_deposits_block_unchanged` — (vii) regression

## Full Suite Tail (verbatim)

```
tests/test_worktree.py::test_auto_stage_handles_multiple_deposits PASSED [ 99%]
tests/test_worktree.py::test_auto_stage_noop_when_all_committed PASSED   [100%]

=============================== warnings summary ===============================
../../../../../Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:35
  /Users/marklehn/Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:35: NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'. See: https://github.com/urllib3/urllib3/issues/3020
    warnings.warn(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================= 729 passed, 1 warning in 29.67s ========================
```

## Self-Lint Output (this plan)

```
PASS: (a) header — parsed
PASS: (a) dispatch_mode — bellows
PASS: (a) pause_for_verdict — always
PASS: (b) step 1 deposits — 1 path(s)
PASS: (b) step 2 deposits — 1 path(s)
PASS: (c) QA banner pair — both strings present
```

Exit code: 0

### Ledger Updates

#### Prompt Feedback

No prompt-feedback observations for this step. The plan instructions were clear and the implementation proceeded without ambiguity.

---
## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Implemented three deliverables: `scripts/plan_lint.py` (pre-deposit lint with header, deposits, and QA banner checks), receipt fallback in `_gate_rule_20_self_check` via shared `_extract_agent_declared_deposits` helper, and 7 new tests (4 lint + 3 gate fallback). Full suite green at 729 tests.

### Files Deposited
- `knowledge/development/plan-lint-and-rule20-receipt-fallback-2026-07-02.md` — this dev log

### Files Created or Modified (Code)
- `scripts/plan_lint.py` — new standalone pre-deposit lint script
- `tests/test_plan_lint.py` — new lint tests (4 tests)
- `gates.py` — extracted shared helper, added receipt fallback to rule_20
- `tests/test_gates.py` — updated evidence assertion, added 3 gate fallback tests

### Decisions Made
- Shared helper returns raw (non-normalized) paths; callers normalize as needed
- Lint tests use subprocess execution of the script (matching CLI contract)
- Gate fallback tests use direct function calls (matching existing test patterns)

### Flags for CEO
- Daemon restart required to load the gates.py changes

### Flags for Next Step
- None

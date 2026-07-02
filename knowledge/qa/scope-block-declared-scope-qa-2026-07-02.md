# QA Report — Declared `**Scope:**` Block for scope_check
**Date:** 2026-07-02 | **Plan:** 119 | **Step:** 2

## Summary

Verified the declared `**Scope:**` block mechanism in `gates.py` and `scripts/plan_lint.py`. All seven specified tests pass individually and in the full suite (736 passed). The parser mirrors the `_extract_plan_required_deposits` idiom. Backward compatibility is preserved — plans without a Scope block behave identically to pre-change behavior.

## Verification Table

| # | Claim | Test | Status | Evidence |
|---|-------|------|--------|----------|
| 1 | `_extract_plan_scope` exists and mirrors `_extract_plan_required_deposits` idiom | Source inspection | ✅ | Signature: `def _extract_plan_scope(step_text):` at line 508; `def _extract_plan_required_deposits(step_text):` at line 451. Both use identical regex pattern `r'[> ]*\*\*<Header>:\*\*\s*\n(?:[> ]*\n)*((?:[> ]*-\s+.*\n?)+)'` for block extraction. |
| 2 | Prefix pass works | `test_scope_check_declared_prefix_passes` | ✅ | 1 passed in 0.40s — file under declared prefix `tests/` passes scope_check with no failure. |
| 3 | Exact-file pass works | `test_scope_check_declared_exact_file_passes` | ✅ | 1 passed in 0.21s — exact declared file `gates.py` passes scope_check. |
| 4 | Undeclared file still fails with extended evidence | `test_scope_check_undeclared_file_fails_with_scope_mention` | ✅ | 1 passed in 0.21s — `totally_rogue.py` in evidence, `Scope` in evidence string. Test asserts: `assert "Scope" in sc[0]["evidence"]`. Evidence format: `out-of-scope files: totally_rogue.py | plan step context: ...; not in declared **Scope:** block`. |
| 5 | Backward compat proven | `test_scope_check_no_scope_block_backward_compat` | ✅ | 1 passed in 0.20s — mentioned files pass (no scope_check failure), unmentioned files fail, and evidence does NOT contain `Scope` (asserts `assert "Scope" not in sc[0]["evidence"]`). |
| 6 | Cross-step scope union | `test_scope_check_declared_scope_unions_across_steps` | ✅ | 1 passed in 0.21s — file declared in step 2's Scope block passes when checked at step 2. |
| 7 | Lint check (d) and WARN behave per spec | `test_lint_empty_scope_block_fails` + `test_lint_test_mentioned_no_test_scope_warns` | ✅ | 2 passed in 0.35s — empty Scope block triggers exit 1 naming check (d); test-mentioned-no-test-scope WARN fires but does not change exit code. |
| 8 | Full suite green | `python3 -m pytest tests/ -v --timeout=600` | ✅ | 736 passed, 1 warning in 29.52s. |
| 9 | Self-lint of plan file exits 0 | `python3 scripts/plan_lint.py` on plan | ✅ | All checks pass: (a) header parsed, dispatch_mode bellows, pause_for_verdict always; (b) step 1 deposits 1 path, step 2 deposits 1 path; (c) QA banner pair present; (d) step 1 scope 5 files 0 prefixes, step 2 scope 1 file 0 prefixes. |

## Full Suite Tail

```
tests/test_worktree.py::test_auto_stage_handles_multiple_deposits PASSED [ 99%]
tests/test_worktree.py::test_auto_stage_noop_when_all_committed PASSED   [100%]

=============================== warnings summary ===============================
../../../../../Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:35
  NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================= 736 passed, 1 warning in 29.52s ========================
```

## Self-Lint Output

```
PASS: (a) header — parsed
PASS: (a) dispatch_mode — bellows
PASS: (a) pause_for_verdict — always
PASS: (b) step 1 deposits — 1 path(s)
PASS: (b) step 2 deposits — 1 path(s)
PASS: (c) QA banner pair — both strings present
PASS: (d) step 1 scope — 5 file(s), 0 prefix(es)
PASS: (d) step 2 scope — 1 file(s), 0 prefix(es)
```

## Rule 20 — QA Self-Check Results

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/119/knowledge/qa/evidence/scope-block-declared-scope-2026-07-02/
Files verified: 0
```

### Ledger Updates

#### Project Status

Declared `**Scope:**` block shipped (CEO 2026-07-02 design: norm-shaped changes are authorable scope, not failures). `scope_check` now supports a three-tier pass path: global allowlist, declared scope (exact file or prefix), and text-mention — in that priority order. Strictness against undeclared files is preserved; evidence text extended with `; not in declared **Scope:** block` when a plan has scope declarations. Backward compatibility verified: plans without a Scope block produce byte-identical behavior to pre-change. Lint check (d) prevents dead convention text (present-but-empty blocks). Daemon restart required to load the updated `gates.py` (covers plan 118's fallback too). PLANNER_TEMPLATE codification of the authoring convention is the deliberate follow-up once the mechanism is proven live.

#### Prompt Feedback

No prompt feedback to report. Step 2 instructions were precise — verification table structure and individual test execution requirements were clear.

---
## Output Receipt
**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Executed full QA verification of the declared `**Scope:**` block mechanism across 9 verification rows. All 7 individual tests pass, full suite green (736 passed), self-lint exits 0. Rule 20 self-check executed.

### Files Deposited
- `knowledge/qa/scope-block-declared-scope-qa-2026-07-02.md` — QA report for plan 119 step 2

### Files Created or Modified (Code)
- None (QA step — verification only)

### Decisions Made
- No evidence files required beyond the QA report itself (no code changes in this step)

### Flags for CEO
- Daemon restart required to load updated `gates.py` (covers both plan 118 fallback and plan 119 scope block)

### Flags for Next Step
- None

# QA Report — wrap-hook plan B: per-session sentinel + anti-hijack message

**Plan:** executable-497 (wrap-hook-plan-b-session-sentinel-2026-08-21)
**Date:** 2026-08-21
**Role:** QA (Step 2)

## 1. Full Test Suite

**Command:** `python3 -m pytest tests/ -v --timeout=120 --tb=short`

| Metric | Baseline (plan A) | Current (plan B) |
|---|---|---|
| Passed | 1183 | 1231 |
| Failed | 0 | 0 |
| Errors | 0 | 0 |
| Warnings | 1 | 1 |

**Baseline line:** `1183 passed, 1 warning in 38.45s`
**Current line:** `1231 passed, 1 warning in 40.59s`

48 additional tests from plans A and B. Zero regressions: no test that passed at baseline now fails or errors, and the failure/error counts did not rise.

Raw output: `knowledge/qa/evidence/wrap-hook-sentinel-2026-08-21/pytest_full.txt`

## 2. Two-Session Sentinel Canary

Hooks driven: `/Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/` (vendored, plan-A-wired).
`BELLOWS_DISPATCH` unset (daemon exemption disabled). `ELUVIAN_WRAP_ROOT` pointed at a scratch tmpdir.
Pre-check: `find /Users/marklehn/Developer/GitHub -maxdepth 1 -name '.wrap-in-progress*'` — empty (clean).
Prompt used for arm trigger: `"/wrap"`.

### Canary assertions (hook scripts, real subprocesses, `wrap_check` genuinely failing)

**(i)** Session A's arm creates `.wrap-in-progress-canary-session-AAAA-1111` and no bare file.
**Result:** PASSED. Sentinels after arm: `['.wrap-in-progress-canary-session-AAAA-1111']`. Bare: NO.

**(ii)** With A's sentinel present and session B UNARMED, B's Stop hook BLOCKS (ARM-IF-ANY) and leaves A's sentinel in place.
**Result:** PASSED. Decision: `block`. A's sentinel still exists: YES. B did not create or remove any sentinel.

**(iii)** With both armed, B's Stop hook BLOCKS on its own sentinel and its message names A's foreign sentinel and its age, instructing waiting rather than resolution.
**Result:** PASSED. Decision: `block`. Message includes `.wrap-in-progress-canary-session-AAAA-1111`: YES. Includes `age:`: YES. Instructs waiting: YES. Includes `Do NOT`: YES.

### Unit-test assertions (from `test_wrap_sentinel.py`, `wrap_check` monkeypatched to return 0)

**(iv)** On a passing check, session B removes ONLY `.wrap-in-progress-<B>` and leaves `<A>` — the disarm defect.
**Result:** PASSED (`TestDisarmDefect::test_b_removes_only_own_on_pass`).

**(v)** On a passing check, session A removes its own `<A>`.
**Result:** PASSED (`TestDisarmDefect::test_a_can_still_clear_own_on_pass`).

**(vi)** A legacy bare sentinel arms, clears on a passing check, and is never renamed.
**Result:** PASSED (`TestBareSentinel::test_bare_still_blocks`, `test_bare_clears_on_pass`, `test_bare_never_renamed_on_block`, `test_bare_never_renamed_on_pass`).

Post-check: `find /Users/marklehn/Developer/GitHub -maxdepth 1 -name '.wrap-in-progress*'` — empty (clean).

Raw output: `knowledge/qa/evidence/wrap-hook-sentinel-2026-08-21/canary.txt`

## 3. Pre-Migration Originals Revert Check

Plan A's vendor-time commit (the commit that ADDED the vendored tree): `c42ab49b8cc067a1546d07be1dbcc4d5101d89ed`.
Resolved mechanically: `git -C /Users/marklehn/Developer/GitHub/bellows log --diff-filter=A --format=%H -- hooks/eluvian/wrap_stop_hook.py | tail -1`.

| File | Command | cmp exit |
|---|---|---|
| wrap_check.py | `git show ${VC}:hooks/eluvian/wrap_check.py \| cmp - ~/.claude/eluvian/wrap_check.py` | 0 |
| wrap_arm_hook.py | `git show ${VC}:hooks/eluvian/wrap_arm_hook.py \| cmp - ~/.claude/eluvian/wrap_arm_hook.py` | 0 |
| wrap_stop_hook.py | `git show ${VC}:hooks/eluvian/wrap_stop_hook.py \| cmp - ~/.claude/eluvian/wrap_stop_hook.py` | 0 |
| wrap_debt_hook.py | `git show ${VC}:hooks/eluvian/wrap_debt_hook.py \| cmp - ~/.claude/eluvian/wrap_debt_hook.py` | 0 |

All four files at `~/.claude/eluvian/` are byte-identical to their plan-A vendor-time state. The pre-migration originals are untouched.

## Verification Summary

| # | Check | Status |
|---|---|---|
| 1 | Full suite — no regression from baseline | ✅ |
| 2 | (i) Per-session arm creates named sentinel, no bare | ✅ |
| 3 | (ii) ARM-IF-ANY — B blocks on A's foreign sentinel | ✅ |
| 4 | (iii) Anti-hijack message names foreign sentinel with age | ✅ |
| 5 | (iv) UNLINK-ONLY-MINE — B removes only own on pass | ✅ |
| 6 | (v) A can clear own sentinel on pass | ✅ |
| 7 | (vi) Legacy bare sentinel — arms, clears, never renamed | ✅ |
| 8 | Pre-migration originals untouched (4/4 cmp exit 0) | ✅ |
| 9 | No governance-root sentinels created (pre/post clean) | ✅ |

## Rule 20 — QA Self-Check Results

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/497/knowledge/qa/evidence/wrap-hook-sentinel-2026-08-21/
Files verified: 2
```

**PASSED — SELF-CHECK PASSED**


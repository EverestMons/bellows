# QA Receipt — detector-coverage-lint (exec-576)

**Date:** 2026-08-27
**Plan:** executable-576 — plan_lint (s)+(t) WARN-only; measured funnel
**DEV commit:** f7d8fd2939943efd866f9d30879d2ef2e335d4f2
**Worktree:** /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/576

## DEV commit stat (3 files)

```
 knowledge/dev-logs/detector-coverage-lint-dev-2026-08-27.md |  47 ++++++
 scripts/plan_lint.py                                        |  48 ++++++
 tests/test_plan_lint_detector_checks.py                     | 168 +++++++++++++++++++++
 3 files changed, 263 insertions(+)
```

## Numstat vs DEV commit (QA-only changes)

```
4	1	scripts/plan_lint.py
```

One QA-discovered fix: `Path(mut_val).exists()` wrapped in `try/except OSError` to handle long continuation-folded stanza values (the plan's own `mutants:` field, folded into a 300+ char string, triggered `OSError: File name too long`).

## Toplevel

```
/Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/576
```

## Reflog (0 amends)

```
f7d8fd2 HEAD@{0}: reset: moving to HEAD
f7d8fd2 HEAD@{1}:
```

## Re-measured funnel

| population | count |
|---|---|
| Done executables | 321 |
| ...with a manifest `target:` field | 28 |
| ...whose target is a `.py` | 25 |
| ...whose target BASENAME matches detector pattern | 12 |
| ...declaring `target_class:` today | 0 |

Numbers match E4 exactly (321 / 28 / 25 / 12).

## Full test suite

1631 passed, 1 skipped, 0 failed (1632 collected).
Baseline E5: 1623 collected (1622 passed + 1 skipped). Delta: +9 new tests from DEV.

## Verification

| Item | Check | Status |
|---|---|---|
| 1 | Full suite: 1632 collected, 1631 passed, 0 failed | ✅ |
| 2.1 | (t) fires on exec-573 (detector name, no target_class) | ✅ |
| 2.2 | (t) silent on exec-514 (target: test_bellows.py, non-detector name) — grep count 0 | ✅ |
| 2.3 | Exit code unaffected: before=0, after=0 (DEV sha f7d8fd2) | ✅ |
| 2.4 | (s) end-to-end: both WARNs fire on constructed plan, exit=0 | ✅ |
| 2.5 | (s) fires on THIS PLAN (in-progress-executable-576.md) — mutants WARN present | ✅ |
| 2.6 | state_space clause silent on THIS PLAN (declares state_space) — discriminates | ✅ |
| fix | OSError on long mut_val wrapped in try/except — 9/9 targeted tests still pass | ✅ |

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/576/knowledge/qa/evidence/detector-coverage-lint-2026-08-27/
Files verified: 3
```

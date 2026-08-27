# QA Receipt — exec-575: mutation-runner-fix (PYTHONDONTWRITEBYTECODE isolation)

**Date:** 2026-08-27
**Plan:** executable-575.md
**DEV commit:** `2f4e37c` — `[575] mutation-runner-fix: PYTHONDONTWRITEBYTECODE isolation; same-length mutant regression test`
**Toplevel:** `/Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/575`

## Numstat (DEV commit, 3 files)

```
59	0	knowledge/dev-logs/mutation-runner-fix-dev-2026-08-27.md
98	0	tests/test_mutation_check.py
8	0	tools/mutation_check.py
```

## Reflog (last 4)

```
2f4e37c HEAD@{0}: reset: moving to HEAD
2f4e37c HEAD@{1}:
```

0 amends — the reflog shows only the worktree creation entries, both at the same commit.

## D6 Derivation

Plan D6 predicted: 1620 (baseline) + 3 new = **1623 collected, 0 failed**.
Measured: `python3 -m pytest tests/ -q --collect-only | tail -1` → **1623 tests collected**.
Full run: **1622 passed, 1 skipped, 0 failed**. Gate met.

## Mutation Result on Real Manifest

**Both mutants KILLED.** `python3 tools/mutation_check.py knowledge/mutants/gate_watcher.json` → exit 0, 2 killed, 0 survived, 0 error.

## Verification

| Item | Description | Status | Evidence |
|------|-------------|--------|----------|
| 1 | Full suite: 0 failed, 1622 passed, 1623 collected | ✅ | `pytest_full.txt` |
| 2 | Real mutant run: 2 killed, 0 survived, 0 error, exit 0 | ✅ | `probes-raw.txt` |
| 2a | LIVE-TREE UNCHANGED confirmed; sha256 before=`e8a8e0b628dc13ef796bfa3c268fa923e2e61606219cd990eb330e51c11ecd22`, after=`e8a8e0b628dc13ef796bfa3c268fa923e2e61606219cd990eb330e51c11ecd22` | ✅ | sha256 match |
| 3 | Empty-selector trap: nonsense node id → ERROR (not KILLED), exit 1 | ✅ | raw output below |
| 4 | Same-length trap (synthetic target): `return a + b` → `return a - b` (12 bytes = 12 bytes), KILLED, exit 0 | ✅ | raw output below |
| 5 | Numstat: 3 files; reflog: 0 amends | ✅ | sections above |

### Item 3 — Empty-Selector Trap (raw)

```
HEAD: 2f4e37ca7d842d880733314ed15ee606376599ed
TARGET: tools/gate_watcher.py sha256=e8a8e0b628dc

MUTANT nonsense-selector-trap: ERROR — baseline not green (pytest exit 4)

LIVE-TREE UNCHANGED: e8a8e0b628dc

MUTATION: 0 killed, 0 survived, 1 error
exit=1
```

### Item 4 — Same-Length Trap, Synthetic Target (raw)

Target: synthetic git repo with `def add(a, b): return a + b` and test asserting `add(1, 2) == 3`.
Mutation: `return a + b` → `return a - b`. Byte lengths: anchor=12, replacement=12 (equal).

```
HEAD: b337b3fdd1e1dd78ad37e1969b8fc01d5fbdb34b
TARGET: target.py sha256=ba1a531f581d

MUTANT same-length-flip: KILLED — suite caught the defect

LIVE-TREE UNCHANGED: ba1a531f581d

MUTATION: 1 killed, 0 survived, 0 error
exit=0
```

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/575/knowledge/qa/evidence/mutation-runner-fix-2026-08-27/
Files verified: 3
```

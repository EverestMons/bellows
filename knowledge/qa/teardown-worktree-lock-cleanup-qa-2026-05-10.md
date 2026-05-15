# QA Report — _teardown_worktree stale lock detection + orphan cleanup

**Plan:** executable-teardown-worktree-lock-cleanup-2026-05-10 (Step 2)
**Date:** 2026-05-10
**Diagnostic:** `bellows/knowledge/research/teardown-worktree-reliability-2026-05-10.md`
**Dev log:** `bellows/knowledge/development/teardown-worktree-lock-cleanup-dev-log-2026-05-10.md`

---

## Verification Status Table

| Check | Description | Result | Evidence |
|-------|-------------|--------|----------|
| 1a | Lock detection code exists before cherry-pick loop | ✅ | `bellows.py:638-656` — checks `os.path.exists(lock_path)`, removes stale (>5s) or waits 3s+removes fresh, try/except OSError wrapping |
| 1b | Orphan cleanup exists after `git worktree remove` | ✅ | `bellows.py:711-716` — `os.path.exists(wt_path)` check, `shutil.rmtree(wt_path, ignore_errors=True)` in try/except |
| 1c | Cherry-pick loop unchanged | ✅ | `bellows.py:658-673` — identical to diagnostic snapshot (L639-653 pre-edit), `for sha in commit_shas:` with subprocess cherry-pick and abort-on-failure |
| 1d | Call site error handling unchanged | ✅ | L362: `except WorktreeTeardownError` → gate_failure append. L448: same pattern. L474: same + verbose logging. All match diagnostic Q2 exactly |
| 2a | `test_teardown_worktree_removes_stale_index_lock` exists | ✅ | `test_bellows.py:2663` — creates lock with mtime 30s ago, mocks subprocess, asserts lock removed |
| 2b | `test_teardown_worktree_waits_for_fresh_index_lock` exists | ✅ | `test_bellows.py:2691` — creates fresh lock, patches `time.sleep`, asserts lock removed after wait |
| 2c | `test_teardown_worktree_force_removes_orphaned_directory` exists | ✅ | `test_bellows.py:2719` — creates wt_path dir, mocks worktree remove to fail (rc=1), asserts dir gone |
| 2d | No other tests modified | ✅ | `git log -1 --stat` shows only `tests/test_bellows.py` touched; no other test files in diff |
| 3 | Bellows test suite — 3 new tests pass, 0 regressions | ✅ | 93 passed, 0 failed — see pytest_bellows.txt |
| 4 | Full test suite — +3 new, 0 regressions, 1 pre-existing failure | ✅ | 245 passed, 1 failed (`test_run_step_timeout` pre-existing) — see pytest_full.txt |
| 5 | Spot-check: stale lock removal end-to-end | ✅ | Lock file (mtime 30s ago) removed; printed "removed stale .git/index.lock (30s old)" |
| 6 | Spot-check: orphaned dir cleanup on worktree remove failure | ✅ | Directory force-removed despite mocked rc=1 failure; printed "worktree removal failed" then cleaned up |

---

## Pytest Output — test_bellows.py

```
tests/test_bellows.py::test_teardown_worktree_removes_stale_index_lock PASSED [ 97%]
tests/test_bellows.py::test_teardown_worktree_waits_for_fresh_index_lock PASSED [ 98%]
tests/test_bellows.py::test_teardown_worktree_force_removes_orphaned_directory PASSED [100%]

======================== 93 passed, 1 warning in 0.38s =========================
```

Full output: `knowledge/qa/evidence/teardown-worktree-lock-cleanup-2026-05-10/pytest_bellows.txt`

---

## Pytest Output — Full Suite

```
tests/test_bellows.py .................................................. [ 20%]
...........................................                              [ 37%]
tests/test_cleanup_verdicts.py ....                                      [ 39%]
tests/test_consume_verdicts.py .....                                     [ 41%]
tests/test_extract_primary_deposit_blocks.py .........                   [ 45%]
tests/test_gates.py .................................................... [ 66%]
..........                                                               [ 70%]
tests/test_notifier_server.py ......                                     [ 72%]
tests/test_phase4_parser.py ...                                          [ 73%]
tests/test_phase4_planner_retry.py ..                                    [ 74%]
tests/test_planner.py ...                                                [ 76%]
tests/test_rule_26_deposit_parser.py .........                           [ 79%]
tests/test_runner.py ...............                                     [ 85%]
tests/test_runner_parser.py ..F......                                    [ 89%]
tests/test_verdict.py ...................                                [ 97%]
tests/test_worktree.py .......                                           [100%]

FAILED tests/test_runner_parser.py::test_run_step_timeout - assert False is True
=================== 1 failed, 245 passed, 1 warning in 6.06s ===================
```

Delta: +3 new tests passing (242 → 245). Pre-existing `test_run_step_timeout` failure unchanged.

Full output: `knowledge/qa/evidence/teardown-worktree-lock-cleanup-2026-05-10/pytest_full.txt`

---

## Behavioral Spot-Check 1 — Stale Lock Removal

```
Bellows: ⚠ could not detect main branch for test-slug, falling back to 'main'
Bellows: ⚠ removed stale .git/index.lock (30s old) for test-slug
SPOT-CHECK 1 (stale lock removal): PASSED — lock file removed successfully
```

---

## Behavioral Spot-Check 2 — Orphaned Directory Cleanup

```
Bellows: ⚠ could not detect main branch for test-slug, falling back to 'main'
Bellows: ⚠ worktree removal failed for test-slug: fatal: worktree remove failed — next startup prune will clean it
SPOT-CHECK 2 (orphaned dir cleanup): PASSED — directory removed despite git worktree remove failure
```

---

## Final Verdict

**ALL CHECKS PASSED**

---

## RULE 20 SELF-CHECK

```python
import os, sys
deposits = [
    "/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/teardown-worktree-lock-cleanup-qa-2026-05-10.md",
    "/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/teardown-worktree-lock-cleanup-2026-05-10/pytest_bellows.txt",
    "/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/teardown-worktree-lock-cleanup-2026-05-10/pytest_full.txt",
]
missing = [d for d in deposits if not os.path.isfile(d)]
if missing:
    print(f"RULE 20 SELF-CHECK FAILED — missing: {missing}")
    sys.exit(1)
else:
    print("RULE 20 SELF-CHECK PASSED")
    sys.exit(0)
```

**Output:**
```
RULE 20 SELF-CHECK PASSED
```

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Verified the stale `.git/index.lock` detection + removal and orphaned worktree directory cleanup shipped in Step 1. All 12 verification checks passed: code changes match the plan spec, cherry-pick loop and call sites are unchanged, 3 new regression tests pass, full suite shows +3 with no regressions, and both behavioral spot-checks confirmed end-to-end correctness.

### Files Deposited
- `bellows/knowledge/qa/teardown-worktree-lock-cleanup-qa-2026-05-10.md` — this QA report
- `bellows/knowledge/qa/evidence/teardown-worktree-lock-cleanup-2026-05-10/pytest_bellows.txt` — bellows test suite output
- `bellows/knowledge/qa/evidence/teardown-worktree-lock-cleanup-2026-05-10/pytest_full.txt` — full test suite output

### Files Created or Modified (Code)
- None (QA step — verification only)

### Decisions Made
- Used `os.utime` to set lock mtime 30s in the past for spot-check 1 (consistent with test approach)
- Verified call sites by reading actual line numbers rather than relying solely on dev log claims

### Flags for CEO
- None

### Flags for Next Step
- None

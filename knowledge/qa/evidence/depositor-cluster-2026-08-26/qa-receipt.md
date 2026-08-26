# QA Receipt — depositor-cluster-2026-08-26

**Plan:** executable-569 (depositor-cluster)
**Date:** 2026-08-26
**Commit:** a92200674a05183919a54942a1ec2b665fc17d47
**Branch:** bellows-wt/569

## Numstat (HEAD~1..HEAD)

```
114	0	knowledge/dev-logs/depositor-cluster-dev-2026-08-26.md
1	0	tests/test_deposit_receipt.py
154	0	tests/test_gate_watcher.py
27	3	tools/deposit_receipt.py
132	0	tools/gate_watcher.py
```

5 files changed.

## Toplevel

```
/Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/569
```

## Reflog (last 4)

```
a922006 HEAD@{0}: reset: moving to HEAD
a922006 HEAD@{1}: 
```

0 amends observed.

## Verification

| Item | Check | Status | Evidence |
|---|---|---|---|
| 1 | Full pytest suite — 0 failures | ✅ | 1531 passed, 0 failed, 1 warning in 47.77s — `pytest_full.txt` |
| 2.1 | gate_watcher --status THIS plan → in_progress id=569, exit 0 | ✅ | `probes-raw.txt` probe 1 |
| 2.2 | gate_watcher --status no-such-plan → pre-claim, exit 0 | ✅ | `probes-raw.txt` probe 2 |
| 2.3 | dup_probe cleanup in worktree receipts dir → 0, git status clean | ✅ | `probes-raw.txt` probe 3 |
| 3 | Hygiene: numstat 5 files, toplevel confirmed, reflog 0 amends | ✅ | Above sections |

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: knowledge/qa/evidence/depositor-cluster-2026-08-26/
Files verified: 3
```

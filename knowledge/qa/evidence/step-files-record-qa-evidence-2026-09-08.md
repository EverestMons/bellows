# QA Receipt — step-files-record — 2026-09-08

**Plan:** 100049 — `lifecycle.py` step_files table + replay tool (thread 209)
**Step:** 2 — QA (full suite + tool on LIVE db, read-only)
**Date:** 2026-09-09
**Worktree:** /Users/marklehn/Developer/bellows/.bellows-worktrees/100049

---

## Environment

- Root check: `TREE_OK` (lifecycle.py present)
- Interpreter: `/Users/marklehn/Developer/bellows/.venv/bin/python` → `VENV_OK` (import pytest succeeded)

---

## Item 1 — Full Suite

**Command:** `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ --tb=short -q > knowledge/qa/evidence/step-files-record-suite-2026-09-08.txt 2>&1`

**Result:** `2097 passed, 1 skipped in 73.70s` — no failures, no errors.

**Evidence file:** `knowledge/qa/evidence/step-files-record-suite-2026-09-08.txt`

---

## Item 2 — Tool on LIVE db, read-only

**Command:** `tools/replay_scope_check.py /Users/marklehn/Developer/bellows/lifecycle.db`

**Output:**
```
step_files: table absent — the daemon has not restarted since the plan that added it; nothing to replay
```

**Exit:** 0

**mtime before:** 1788958647
**mtime after:**  1788958647 (unchanged — confirmed read-only)

**step_files count in live db:** `sqlite3 "file:…?mode=ro" "select count(*) from sqlite_master where name = 'step_files'"` → `0` (table not present until daemon restarts)

---

## Item 3 — Writer on tmp copy of live db

**Command:** `cp lifecycle.db .qa-scratch/copy.db && init_lifecycle_db(copy) && record_gate_events(85, …) && replay_scope_check.py copy.db`

**init_lifecycle_db on copy:** `step_files present: True`; all other table counts unchanged:

| Table | Before | After |
|---|---|---|
| clearances | 52 | 52 |
| commits | 93 | 93 |
| deposits | 287 | 287 |
| diagnostic_meta | 10 | 10 |
| executable_meta | 42 | 42 |
| gate_events | 627 | 627 |
| id_sequence | 1 | 1 |
| plans | 52 | 52 |
| steps | 87 | 87 |
| verdicts | 88 | 88 |
| step_files | — | 0 (new, empty) |

**record_gate_events(85, {"failures": [], "files_changed": ["x.py"]}, copy):**
→ `step_files rows for step 85: [(85, 'x.py')]` — one row inserted.

**Tool on copy:** `100048/2: plan text not found` and `FLIPS: 0`, exit 0 (step 85 = plan 100048 step 2; plan text not in worktree, tool continues gracefully).

**Scratch cleanup:** `.qa-scratch/` removed before commit (Item 6).

---

## Item 4 — Production Writes

None outside the two evidence files. The daemon restart is owed at close (post-close note in plan).

---

## Item 5 — numstat and Receipt Details

### numstat over DEV commits (b701924..HEAD — six files across two commits)

| File | +lines | -lines |
|---|---|---|
| `knowledge/development/dev-log-step-files-record-2026-09-08.md` | 103 | 0 |
| `knowledge/mutants/step-files-record.json` | 45 | 0 |
| `knowledge/mutants/step-files-record.run.txt` | 15 | 0 |
| `lifecycle.py` | 18 | 0 |
| `tests/test_step_files_record.py` | 369 | 0 |
| `tools/replay_scope_check.py` | 121 | 0 |

Total: 6 files across 2 commits. ✅

### Run file HEAD matches mutants commit

- `HEAD:` in `step-files-record.run.txt`: `9ffb96cbdbf637bf6befd1a5489b76f12664ccc0`
- `git log -1 --format=%H -- knowledge/mutants/step-files-record.json`: `9ffb96cbdbf637bf6befd1a5489b76f12664ccc0`
- **Match:** ✅

### Unchanged tests (git diff b701924..HEAD)

- `tests/test_lifecycle.py` diff: EMPTY ✅
- `tests/test_gate_transaction_mechanization.py` diff: EMPTY ✅

### Toplevel

`/Users/marklehn/Developer/bellows/.bellows-worktrees/100049`

### Reflog — 0 amends, 0 resets in DEV commits

`git reflog -n 6`: no `amend` entries in the two DEV commits (9ffb96c, 3987601). ✅

### Dev-log headings grepped

```
## Pins re-derived (P1–P4, P7)
## Failing-first (the eight tests red, then green)
## Mutation run
## Cost
```

All four required headings present. ✅

---

## Verification

| Item | Check | Status |
|---|---|---|
| Item 1 | Full suite: 2097 passed, 0 failed, 0 errors (1 skip-marker) | ✅ |
| Item 2 | Tool on live db: `table absent` line, exit 0, mtime unchanged, step_files count = 0 | ✅ |
| Item 3 | Writer on copy: step_files added, counts unchanged, 1 row inserted, tool ran exit 0 | ✅ |
| Item 4 | Production writes: none (daemon restart owed at close) | ✅ |
| Item 5 numstat | 6 files across 2 commits | ✅ |
| Item 5 HEAD match | run file HEAD matches mutants commit sha | ✅ |
| Item 5 unchanged tests | test_lifecycle.py and test_gate_transaction_mechanization.py diff EMPTY | ✅ |
| Item 5 reflog | 0 amends in DEV commits | ✅ |
| Item 5 dev-log headings | All four required headings present | ✅ |
| suite evidence file | step-files-record-suite-2026-09-08.txt non-empty | ✅ |
| qa evidence file | step-files-record-qa-evidence-2026-09-08.md non-empty | ✅ |

---

## Rule 20 Self-Check Output

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100049/knowledge/qa/evidence/
Files verified: 2
```

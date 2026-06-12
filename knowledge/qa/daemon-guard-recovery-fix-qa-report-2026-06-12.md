# QA Report — Daemon Single-Instance Guard + Project-Scoped Recovery + Age Guard + in_progress Write

**Date:** 2026-06-12 | **Plan:** 22, Step 2 | **Agent:** Bellows QA

---

## Verification Table

| # | Item | Method | Evidence File | Result |
|---|---|---|---|---|
| 1 | Full test suite — 532 passed, 0 failures | `python3 -m pytest tests/` — last 15 lines captured | `full_suite_tail.txt` | PASS |
| 2 | G1 — project-scoped recovery filter landed | grep `recover_half_claimed` for project filter + live DB query | `g1_check.txt` | PASS |
| 3 | G2 — flock single-instance guard landed | grep `__main__` for flock before migration/recovery/watcher | `g2_check.txt` | PASS |
| 4 | G3 — 5-minute age guard landed | grep age check before abandoned branch | `g3_check.txt` | PASS |
| 5 | G4 — mark_plan_state in_progress after claim | grep + live canary condition (expected: claimed, not in_progress) | `g4_check.txt` | PASS |
| 6 | FORWARD reconciliation (Rule 42) | Updated rows 19 and 20 to closed-by-plan-22 | `forward_reconciliation.txt` | PASS |

---

## Verification Details

### 1. Full Suite
- Command: `python3 -m pytest tests/`
- Result: 532 passed, 1 warning, 0 failures, 0 errors
- New test count: 8 (532 - 524 = 8, matches dev log)

### 2. G1 — Project-Scoped Recovery
- `recover_half_claimed()` at lifecycle.py:190 accepts `project_root` parameter
- When provided, SELECT filters by `WHERE lifecycle_state = 'claimed' AND target_project = ?` (lifecycle.py:209)
- Callsite at bellows.py:1842 derives project_root via `Path(decisions_path).parent.parent`
- Live DB confirms plan rows carry `target_project` values the filter can key on

### 3. G2 — flock Single-Instance Guard
- `import fcntl` at bellows.py:3
- flock acquisition at bellows.py:1831: `fcntl.flock(_lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)`
- Ordered BEFORE: `migrate_db()` (1837), `init_lifecycle_db()` (1838), recovery loop (1839-1847), watcher startup (1849)
- Contention branch logs ERROR and exits non-zero
- Lock handle kept open for daemon lifetime (kernel releases on death)

### 4. G3 — Age Guard (5 minutes)
- `created_at` added to SELECT at lifecycle.py:208, 214
- Age check at lifecycle.py:241-250: if plan younger than `age_guard_seconds` (default 300), logs INFO "recovery: plan <id> younger than 5m — skipping" and appends `skipped_too_recent`
- Check occurs BEFORE the abandoned fallthrough at lifecycle.py:253-258
- Malformed timestamps handled gracefully (fall through to abandon)

### 5. G4 — in_progress Write
- `lifecycle.mark_plan_state(plan_id, "in_progress")` at bellows.py:462
- Immediately after `shutil.move(plan_path, inprogress_path)` at bellows.py:459
- Wrapped in try/except with log-and-continue semantics
- Live canary: plan 22 shows `lifecycle_state='claimed'` — EXPECTED because the running daemon predates the G4 fix. After daemon restart, the first claimed plan will show `in_progress` mid-run.

### 6. FORWARD Reconciliation
- Row 19 (concurrent-daemon recovery race): Status → `closed-by-plan-22`
- Row 20 (intermediate states never written): Status → `closed-by-plan-22`

---

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/22/knowledge/qa/evidence/daemon-guard-recovery-fix-2026-06-12/
Files verified: 6
```

---

## Receipt Flags for CEO

1. **DAEMON RESTART REQUIRED** — no hot reload. The running daemon keeps its loaded code; all four fixes (G1-G4) take effect only at the next restart.
2. **Live canaries after restart:**
   - The first claimed plan shows `lifecycle_state='in_progress'` mid-run (G4 confirmation)
   - A deliberate second `python3 bellows.py` start exits immediately on the flock (G2 confirmation)

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Verified all four diagnostic-21 gap fixes (G1-G4) with executed evidence: full test suite pass (532/532), code grep confirmations for each gap, live DB sanity queries, and FORWARD.md reconciliation closing rows 19 and 20.

### Files Deposited
- `knowledge/qa/daemon-guard-recovery-fix-qa-report-2026-06-12.md` — this QA report
- `knowledge/qa/evidence/daemon-guard-recovery-fix-2026-06-12/` — six evidence files

### Files Created or Modified (Code)
- `knowledge/FORWARD.md` — rows 19 and 20 Status updated to closed-by-plan-22

### Decisions Made
- G4 live canary showing `claimed` instead of `in_progress` classified as expected pre-restart condition, not a failure

### Flags for CEO
- DAEMON RESTART REQUIRED — no hot reload
- Live canaries after restart: (1) first claimed plan shows lifecycle_state='in_progress' mid-run, (2) deliberate second python3 bellows.py exits immediately on flock

### Flags for Next Step
- None

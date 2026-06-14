# Clean-Restart Smoke Test — 2026-06-14

**Plan:** diagnostic-47 | **Agent:** Bellows Systems Analyst | **Date:** 2026-06-14

---

## Check 1 — Self-row live

```
$ sqlite3 "file:lifecycle.db?mode=ro" "SELECT id, type, lifecycle_state, plan_doc_ref FROM plans WHERE id=47"
47|diagnostic|in_progress|knowledge/decisions/in-progress-diagnostic-47.md
```

- type = diagnostic — **PASS**
- lifecycle_state = in_progress — **PASS**
- plan_doc_ref populated — **PASS**

## Check 2 — Single daemon (flock guard)

```
$ ps aux | grep "[b]ellows.py" | wc -l
       1
```

Exactly 1 bellows.py process holds the lock — **PASS**

## Check 3 — Daemon currency

```
$ git -C /Users/marklehn/Developer/GitHub/bellows log --oneline -1
4ba2b7d docs(diagnostic): post-Phase-3 smoke test — all checks PASS [46]
```

HEAD SHA: `4ba2b7d` — **PASS**

---

## Result

**ALL CHECKS PASS** — daemon is healthy on a clean single-instance launch.

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Ran three smoke checks against the clean-restart daemon: verified self-row in lifecycle.db, confirmed single-daemon flock guard, recorded HEAD SHA for daemon currency. All checks passed.

### Files Deposited
- `knowledge/research/clean-restart-smoke-2026-06-14.md` — smoke test findings

### Files Created or Modified (Code)
- None

### Decisions Made
- None (read-only diagnostic)

### Flags for CEO
- None

### Flags for Next Step
- None

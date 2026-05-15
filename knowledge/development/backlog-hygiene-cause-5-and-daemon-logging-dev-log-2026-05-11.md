# Dev Log — Backlog Hygiene: Cause 5 RC2 Closure + Daemon Code-Version Logging

**Date:** 2026-05-11
**Plan:** executable-backlog-hygiene-cause-5-and-daemon-logging-2026-05-11
**Step:** 1 (Documentation Analyst)

---

## Edits Applied

### Edit 1 — New Closed entry (top of Closed section)

Inserted `Closed 2026-05-11` entry documenting empirical RC2 closure for
`deposit_exists` Cause 5 (plan-agent evidence path convention mismatch).
Entry cites the audit findings file, canary diagnostic, Rule 26 governance
fix (PLANNER_TEMPLATE v4.37, governance-root commit `75904fd`), and three
executable/diagnostic plan files in Done/.

### Edit 2 — New Open entry (top of Open section)

Inserted `2026-05-11` entry for daemon code-version observability gap.
Entry documents the operational exposure (no mechanism to detect
code-vs-runtime drift), three post-fix reproductions from the audit,
proposed fix shape (startup mtime/SHA log + optional heartbeat surfacing),
scope estimate (~10-15 LOC), and priority (low).

---

## Verification Grep Output

```
grep -c "Closed 2026-05-11.*Cause 5 — plan-agent evidence path convention mismatch" → 1
grep -c "2026-05-11.*Daemon code-version observability gap" → 1
grep -c "75904fd" → 1
grep -c "executable-rule-26-evidence-path-fix-2026-05-11" → 1
```

All 4 checks returned exactly 1. Pass.

---

## Commit

**SHA:** `60c56e9`
**Message:** `docs(backlog): close Cause 5 RC2, open daemon code-version logging`
**Files:** `knowledge/BACKLOG.md`

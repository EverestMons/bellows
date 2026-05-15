# BACKLOG Append — QA Report (3 new items from plan-mutation-source diagnostic)
**Date:** 2026-04-19 | **Agent:** Bellows QA | **Plan:** executable-backlog-append-2026-04-19

---

## Deliverable Verification (Rule 17)

| Deliverable | Expected | Status | Evidence |
|---|---|---|---|
| Bullet 1: scope_check false-positive | `grep -c` returns 1 | ✅ | `grep_bullets.txt`: `grep -c "2026-04-19: scope_check false-positive"` → 1 |
| Bullet 2: deposit parser gap | `grep -c` returns 1 | ✅ | `grep_bullets.txt`: `grep -c "2026-04-19: deposit parser gap"` → 1 |
| Bullet 3: single-step diagnostic generates | `grep -c` returns 1 | ✅ | `grep_bullets.txt`: `grep -c "2026-04-19: single-step diagnostic generates"` → 1 |

---

## Structural Verification

- All three new bullets appear at lines 9, 11, 13 of `knowledge/BACKLOG.md` (top of `## Open` section)
- Existing first bullet (`2026-04-18: Planner should read verdicts folder directly`) preserved at line 15
- No test regression needed — documentation-only change, no code touched

---

## Commit

- `e1b0e7c` — `docs: BACKLOG — 3 new items from plan-mutation-source diagnostic`
- Source document: `knowledge/research/plan-mutation-source-2026-04-19.md`

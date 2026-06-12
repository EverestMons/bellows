# Dev Log — Session-Wrap Errata (Plan 12)

**Date:** 2026-06-12

## Edits

### E1 — Baton function names (shop_next_session.md)
- **Anchor:** `read_lifecycle_plans()`
- **Before grep:** `grep -c "read_lifecycle_plans|resolve_plan_pointer|assemble_reconstruction" shop_next_session.md` → 1
- **After grep:** → 0
- **Replacement:** `generate_reconstruction_data()`, `write_reconstruction_report()`, `get_live_plans_status()` (plus `_open_lifecycle_db()`, `_query_*`, and `_resolve_*` helpers)
- **Ground truth:** `grep -n "^def " forge/src/reporter.py` confirms all three top-level names and helper prefixes exist

### E2 — Plan-7 coverage claim (shop_next_session.md)
- **Anchor:** `first two-row step coverage with turns populated across plans 4/5/6/7`
- **Before grep:** 1 match
- **After grep:** 0 (old text gone); new text: `FIRST plan with two-row step coverage and turns populated (plans 4/5 permanently lack their step-2 rows — pre-fix era; plan 6 is single-step)` → 1 match

### E3 — Forge SA filename (shop_next_session.md)
- **Anchor:** `FORGE_SA.md`
- **Before grep:** 1 match
- **After grep:** 0 (old); `FORGE_SYSTEMS_ANALYST.md` → 1 match
- **Ground truth:** `ls forge/agents/` shows FORGE_SYSTEMS_ANALYST.md

### E4 — LESSONS duplicate sentence (LESSONS.md)
- **Anchor:** `corrections discovered at verdict time`
- **Before grep:** 2 occurrences (body paragraph + bolded standalone)
- **After grep:** 1 occurrence (bolded standalone only)

## Commit

- **Root SHA:** bccbefe
- **Message:** docs: session-wrap errata — baton function names, plan-7 coverage claim, FORGE_SYSTEMS_ANALYST filename, LESSONS dedupe [12]
- **Files:** shop_next_session.md, LESSONS.md (governance root)

# Dev Log: Shadow Copy Plan Cache

**Plan:** executable-shadow-copy-cache-2026-04-17.md
**Step:** 1 (DEV)
**Date:** 2026-04-17

## Changes

### bellows.py

1. **SHADOW_CACHE_DIR constant** (line 18): `BELLOWS_ROOT / ".bellows-cache"` — central location for all shadow copies.

2. **Four helper functions** (lines 90-120):
   - `_shadow_path(plan_filename)` — canonical path resolution, strips lifecycle prefixes (`in-progress-`, `verdict-pending-`, `halted-`) so all lifecycle states map to the same shadow file.
   - `_write_shadow(plan_filename, plan_text)` — creates `.bellows-cache/` if needed, writes `.pristine` file.
   - `_read_shadow(plan_filename)` — returns shadow content or None.
   - `_delete_shadow(plan_filename)` — idempotent cleanup.

3. **run_plan shadow read** (lines 196-201): After loading `plan_text`, checks for shadow copy. Uses shadow for `metadata_text` if available, else falls back to `plan_text`. All metadata extraction (`extract_total_steps`) reads from `metadata_text`.

4. **run_plan shadow write** (lines 211-212): Immediately after `shutil.move` claim, writes pristine `plan_text` to shadow cache.

5. **run_plan shadow print** (lines 214-215): `"Bellows: using cached plan content ({total_steps} steps)"` when shadow is used.

6. **Shadow cleanup on Done/Skip/Halt** — `_delete_shadow()` called at:
   - Auto-close to Done (line 354)
   - SKIPPED (0 steps) to Done (line 218)
   - `_consume_verdicts` continue-to-done (line 630)
   - `_consume_verdicts` halt (line 647)

7. **_consume_verdicts fallback chain** (lines 611-620): shadow -> verdict metadata (`total_steps_from_request`) -> `load_file` as last resort. Shadow prints when used.

### .gitignore

Added `.bellows-cache/` — ephemeral runtime files, not tracked.

## Tests

104/104 pass. Zero regressions. No new tests in this step (QA step will verify).

## Output Receipt

- **Status:** Complete
- **Files changed:** bellows.py, .gitignore
- **Commit:** `feat: shadow copy plan cache — preserve pristine plan content for metadata reads`

# Cleanup Slug Normalization — Dev Log
**Date:** 2026-05-01 | **Plan:** executable-cleanup-slug-normalization-2026-05-01

## Line Number Verification

All SA-cited line numbers matched exactly — zero drift.

| SA Cited | Actual | Description |
|---|---|---|
| 130–140 | 130–140 | `_cleanup_verdicts_for_slug` helper |
| 669 | 669 | pending-req-file lookup |
| 706 | 706 | plan match (`plan_slug in pname`) |
| 736 | 736 | continue-to-done cleanup call |
| 756 | 756 | halt cleanup call |
| 768 | 768 | per-step pending file cleanup |
| 824–828 | 824–828 | Done/ loop in startup sweep |

## Edits

### Edit 1 — Compute `cleanup_slug` after plan matching

**Before (line 707–710):**
```python
                        plan_matched = True
                        full_plan_path = os.path.join(decisions_path, pname)
                        original_name = pname.replace("verdict-pending-", "", 1)
```

**After:**
```python
                        plan_matched = True
                        full_plan_path = os.path.join(decisions_path, pname)
                        original_name = pname.replace("verdict-pending-", "", 1)
                        cleanup_slug = verdict.slug_from_path(original_name)
```

### Edit 2 — Replace `plan_slug` with `cleanup_slug` at three call sites

**Line 736 (continue-to-done):**
Before: `_cleanup_verdicts_for_slug(plan_slug)`
After: `_cleanup_verdicts_for_slug(cleanup_slug)`

**Line 756 (halt):**
Before: `_cleanup_verdicts_for_slug(plan_slug)`
After: `_cleanup_verdicts_for_slug(cleanup_slug)`

**Line 768 (per-step cleanup):**
Before: `f"verdict-request-{plan_slug}-step-{step_number}.md"`
After: `f"verdict-request-{cleanup_slug}-step-{step_number}.md"`

### Edit 3 — Normalize slug at pending-req-file lookup (line 669)

**Before:**
```python
            pending_req_file = BELLOWS_ROOT / "verdicts" / "pending" / f"verdict-request-{plan_slug}-step-{step_number}.md"
```

**After:**
```python
            lookup_slug = plan_slug
            for prefix in ("diagnostic-", "executable-"):
                if lookup_slug.startswith(prefix):
                    lookup_slug = lookup_slug[len(prefix):]
                    break
            pending_req_file = BELLOWS_ROOT / "verdicts" / "pending" / f"verdict-request-{lookup_slug}-step-{step_number}.md"
```

### Edit 4 — Remove Done/ slug loop from startup sweep

**Removed (lines 824–828):**
```python
            done_dir = os.path.join(decisions_path, "Done")
            if os.path.isdir(done_dir):
                for fname in os.listdir(done_dir):
                    if fname.endswith(".md"):
                        active_slugs.add(verdict.slug_from_path(fname))
```

This loop was adding Done/ plan slugs to `active_slugs`, preventing the startup sweep from ever removing orphaned verdict-request files for completed plans.

### Pre-existing test fix

Updated `test_consume_verdicts_deletes_pending_file` in `tests/test_bellows.py`: changed pending file name from `verdict-request-diagnostic-baz-2026-04-16-step-1.md` to `verdict-request-baz-2026-04-16-step-1.md` to match production behavior (verdict.py strips the plan-type prefix when creating verdict-request files).

## Test Results

- Full suite: **180 passed, 1 failed** (pre-existing `test_run_step_timeout` in `test_runner_parser.py` — unrelated to these changes)
- 3 new regression tests in `tests/test_consume_verdicts.py`: all pass
- Syntax check: `ast.parse` returns valid

## Files Created or Modified

- `bellows/bellows.py` — 4 edits (cleanup_slug computation, 3 call-site replacements, lookup_slug normalization, Done/ loop removal)
- `bellows/tests/test_bellows.py` — 1 line fix (pending file name in existing test)
- `bellows/tests/test_consume_verdicts.py` — new file, 3 regression tests
- `bellows/knowledge/development/cleanup-slug-normalization-dev-log-2026-05-01.md` — this file

## Notes

- CEO restart required to load the new code
- Output Receipt status: **Complete**

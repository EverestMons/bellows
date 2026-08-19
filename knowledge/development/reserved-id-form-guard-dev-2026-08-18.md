# Reserved Canonical-ID-Form Claim Guard — Dev Log
**Date:** 2026-08-18 | **Plan:** `executable-reserved-id-form-claim-guard-2026-08-18`

## Output Receipt
- **Status:** Step 1 complete (dev)
- **Files changed:** `validators.py` (new `is_reserved_canonical_form` predicate), `bellows.py` (claim-path guard before `validate_at_claim`)
- **Targeted sanity:** `tests/test_validators.py` — 32 passed

## What Changed

### validators.py — `is_reserved_canonical_form`
Pure predicate: returns `True` for filenames matching `<type>-<N>.md` where type is `diagnostic|executable|qa` and N is one or more digits. Uses `re.fullmatch` so lifecycle-prefixed forms (`in-progress-`, `halted-`), descriptive slugs, and non-`.md` extensions all return `False`.

### bellows.py — claim-path guard (RC-2)
Inserted immediately before `validate_at_claim()` inside the first `if not plan_filename.startswith("in-progress-"):` block (~line 781). When a fresh deposit matches the reserved canonical id-form:
1. Logs a WARN with the filename and namespace-ownership reason.
2. Quarantines the file to `halted-<base_filename>`.
3. Discards it from `_seen` to prevent re-processing.
4. Returns without minting an id — no orphan row created.

## Root Cause Context
The diagnostic-444 → phantom-445 collision (2026-08-18): a worktree teardown-merge leaked `diagnostic-444.md` into `decisions/`. The watcher treated it as a new deposit and minted id 445. The file then vanished, stranding 445 in `claimed` status forever. The existing dedup guard (`active_plan_for_placeholder`) keys on the descriptive slug and is structurally blind to bare id-form filenames.

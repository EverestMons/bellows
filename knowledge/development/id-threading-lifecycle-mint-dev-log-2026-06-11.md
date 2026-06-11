# Dev Log — Id-Threading + Lifecycle Mint v2 (Step 1 DEV)
**Date:** 2026-06-11

## Summary

Implemented monotonic id-threading and lifecycle DB minting for Bellows (Reporting Phase 1, Executable A). All deposit filenames now carry a global-monotonic integer id minted at claim time. Two latent substring-match bugs were fixed, and commit messages are tagged with the plan id.

## Work Items

### 1. lifecycle.py (NEW)

New module implementing the minimal lifecycle-DB subset (id_sequence + plans tables only).

- `lifecycle.py:16` — `LIFECYCLE_DB_PATH` resolved via `resolve_bellows_root() / "lifecycle.db"`
- `lifecycle.py:19-49` — `init_lifecycle_db()`: creates `id_sequence` (single-row counter, `next_id=1`) and `plans` tables; idempotent `CREATE TABLE IF NOT EXISTS`, WAL mode
- `lifecycle.py:52-82` — `mint_and_claim()`: `BEGIN IMMEDIATE` transaction wrapping `UPDATE id_sequence SET next_id = next_id + 1 RETURNING next_id - 1` and `INSERT INTO plans` atomically; rolls back on failure so no id is burned
- `lifecycle.py:85-100` — `mark_plan_state()`: updates `lifecycle_state` and optional `closed_at`
- `lifecycle.py:103-149` — `recover_half_claimed()`: blueprint 2.4a startup recovery — re-renames if deposit on disk, marks abandoned if not, transitions to in_progress if already renamed

### 2. bellows.py — Claim Path Integration

- `bellows.py:131` — `import lifecycle`
- `bellows.py:411-445` — Claim path: after `validate_at_claim`, parses type from filename prefix (`diagnostic-`/`executable-`/`qa-`), extracts title from `# Title` line, calls `lifecycle.mint_and_claim()`, performs single rename from deposit → `in-progress-<type>-<id>.md`, updates `base_filename`, `plan_filename`, `plan_slug`

### 3. Substring-Match Bug Fixes

Three comparison sites converted from substring `in` to exact `==` via `verdict.slug_from_path()`:

- `bellows.py:1460` — Verdict-pending match: `verdict.slug_from_path(pname) == lookup_slug`
- `bellows.py:1562` — Done/ stale scan: `verdict.slug_from_path(dname) == lookup_slug`
- `bellows.py:1570` — Halted stale scan: `verdict.slug_from_path(dname[len("halted-"):]) == lookup_slug` (manual strip of `halted-` prefix before calling `slug_from_path` since it's not in the function's strip list)

All three sites use `lookup_slug` (type-prefix-stripped at ~:1373-1377), not `plan_slug`, because verdict filenames include the type prefix and `slug_from_path()` strips it.

### 4. Commit-Message Id-Tagging

- `bellows.py:467` — `_id_tag_instruction` computed from `plan_id`
- `bellows.py:469-473` — All three bootstrap prompt variants appended with `_id_tag_instruction`
- `bellows.py:588` — Next-step prompt appended with `_id_tag_instruction`
- `bellows.py:981` — Auto-stage commit message includes `[<plan_id>]`
- `bellows.py:1086` — `--no-ff` merge switched from `--no-edit` to explicit `-m "Merge branch '<branch>' [<plan_id>]"`
- `bellows.py:921` — `_auto_stage_deposits()` signature: added `plan_id=None` parameter
- `bellows.py:992` — `_teardown_worktree()` signature: added `plan_id: int = None` parameter
- All call sites for both functions updated to thread `plan_id`

### 5. Startup Recovery

- `bellows.py:1717` — `lifecycle.init_lifecycle_db()` called at daemon startup
- `bellows.py:1721` — `lifecycle.recover_half_claimed(decisions_path)` called with logging of each recovery action

### 6. Test Infrastructure

#### tests/conftest.py

- `conftest.py:18-24` — `isolate_lifecycle_db` autouse fixture: monkeypatches `lifecycle.LIFECYCLE_DB_PATH` to tmp_path, calls `init_lifecycle_db()` — mirrors existing `isolate_verdicts_dir`/`isolate_runner_logs_dir` pattern

#### tests/test_lifecycle.py (NEW)

- `test_lifecycle.py:9-16` — `TestMintMonotonicity`: 3 sequential mints return consecutive ids (1, 2, 3)
- `test_lifecycle.py:18-20` — Mint returns integer type
- `test_lifecycle.py:23-35` — `TestMintAtomicity`: CHECK constraint violation does not consume id; next mint still returns 2
- `test_lifecycle.py:37-47` — Plans row written correctly on successful mint
- `test_lifecycle.py:50-66` — `TestMarkPlanState`: state updates and `closed_at` setting
- `test_lifecycle.py:69-124` — `TestRecoverHalfClaimed`: three recovery branches (deposit present → re-rename, deposit absent → abandoned, already renamed → in_progress)
- `test_lifecycle.py:127-134` — DB path resolves under bellows root
- `test_lifecycle.py:137-146` — Double init is idempotent

#### tests/test_bellows.py — Updated Tests

**Substring-fix regression tests (6 new):**
- `test_bellows.py:3962` — `test_consume_verdicts_numeric_slug_no_false_match`: slug 142 ≠ 1423
- `test_bellows.py:3972` — `test_stale_scan_numeric_slug_no_false_match_done`: Done/ slug 142 ≠ 1423
- `test_bellows.py:3981` — `test_stale_scan_numeric_slug_no_false_match_halted`: halted slug 142 ≠ 1423
- `test_bellows.py:3991` — `test_exact_match_still_works_for_legacy_slugs`: legacy verdict slug matches exactly
- `test_bellows.py:4001` — `test_exact_match_done_legacy`: legacy Done/ slug matches exactly
- `test_bellows.py:4009` — `test_exact_match_halted_legacy`: legacy halted slug matches exactly

**Claim-rename contract tests (2 new):**
- `test_bellows.py:4021` — `test_claim_rename_draft_placeholder`: `diagnostic-draft-143022.md` claims to `in-progress-diagnostic-1.md`
- `test_bellows.py:4064` — `test_claim_rename_legacy_descriptive_slug`: `diagnostic-foo-bar-2026-06-10.md` claims to `in-progress-diagnostic-1.md`

**Existing tests updated for id-canonical naming (~10 tests):**
Tests that previously expected legacy filenames in Done/, verdict-pending, and Mode A paths were updated to expect `<type>-1.md` (id=1 due to fresh lifecycle DB per test via conftest fixture). Changes include Done/ path assertions, verdict-pending path assertions, and Mode A `agent_moves_to_done` callback simulations.

## Bugs Discovered and Fixed During Implementation

1. **`plan_slug` vs `lookup_slug` mismatch** — When verdict filenames include the type prefix (e.g., `verdict-diagnostic-foo-step-1.md`), `slug_from_path` strips both the verdict prefix and the type prefix. Using `plan_slug` (which retains the type prefix) produced mismatches. Fixed by using `lookup_slug` (type-prefix-stripped) at all three comparison sites.

2. **`halted-` prefix not in `slug_from_path` strip list** — `slug_from_path("halted-executable-foo.md")` returns `"halted-executable-foo"` not `"foo"`. Fixed by manually stripping `"halted-"` before calling `slug_from_path`.

3. **Post-execution assertion timing in claim-rename tests** — After `run_plan()` completes, auto-close moves files to Done/, so `in-progress-*` files are absent. Fixed by using a `capture_claim` callback pattern that captures directory state during execution.

## Self-Verification

Scratch session against temp DB confirmed two sequential `mint_and_claim` calls return ids 1 and 2 (consecutive monotonic integers).

## Test Results

```
480 passed, 1 warning in 8.86s
```

Full output: `knowledge/development/pytest_full_id_threading.txt`

No pre-existing failures. No new failures introduced.

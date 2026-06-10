# Deposit-Loss Fix — Dev Log

**Date:** 2026-06-10 | **Plan:** bellows-deposit-loss-fix-2026-06-10 | **Step:** 1 (DEV)

## Summary

Implemented the two-layer deposit-loss fix per design `knowledge/architecture/silent-deposit-loss-teardown-fix-design-2026-06-10.md`:

**(a) PRESERVE — Auto-stage declared deposits before gates**
- Added `_auto_stage_deposits(plan_text, plan_header, project_path, wt_path, slug)` to `bellows.py` (line ~880).
- Extracts plan-declared deposit paths from prose (`gates._extract_plan_required_deposits`) and frontmatter (`plan_header.get("deposits")`).
- For each resolved deposit that exists but is uncommitted (`git status --porcelain`), runs path-scoped `git add` (never `git add -A`) and commits with message `bellows: auto-stage declared deposits before teardown`.
- Clean no-op when all deposits are already committed.
- Called immediately BEFORE each `gates.check()` at step completion (two call sites: first-step at ~line 497 and continuation-step at ~line 593), per the ORDERING CORRECTION that overrides the design's "before `_teardown_worktree`" placement. This ensures `deposit_exists` evaluates post-commit state and `files_changed` captures auto-committed deposits.

**(b) FAIL-LOUD — Gate failure on uncommitted declared deposit**
- Added `_check_deposit_uncommitted(resolved_path, original_path, wt_path, failures)` to `gates.py`.
- Extended `_gate_deposit_exists` to call this check after each successful `_resolve_deposit_path`, for agent-declared, frontmatter, and prose-declared deposits.
- When `git status --porcelain` shows any uncommitted state, appends gate failure `deposit_uncommitted: <path> exists on disk but is not committed — will be lost at teardown`.
- Added `import subprocess` to `gates.py`.

## Interaction with Hardened Teardown/Resume Family (CRITICAL — additivity confirmation)

| Component | Impact | Reasoning |
|---|---|---|
| `_teardown_worktree` land-or-raise contract | **UNCHANGED** | `_auto_stage_deposits` runs BEFORE teardown. It adds commits to the worktree branch that the existing merge step picks up normally. No teardown code was modified. |
| Gap-1b guard (block continue over uncleared `worktree_teardown` failure) | **UNCHANGED** | Auto-staging is in the step-completion path, before teardown. It does not touch teardown failure handling or the continue-verdict path. |
| Gap-1c (re-attempt recoverable dirty-tree teardown on continue-resume) | **UNCHANGED** | Gap-1c operates at resume time in `_consume_verdicts`. Auto-staging operates at step-completion, a completely separate code path. |
| Stranded-cleanup preserve-branch logic (Gap 2a) | **UNCHANGED** | Gap-2a operates in `_create_worktree` during stranded-cleanup. Auto-staging operates in step-completion, completely separate. |
| Deposit exists gate | **EXTENDED** — (b) adds `_check_deposit_uncommitted` after existing `os.path.isfile` checks. Existing check preserved; purely additive. |

**Confirmation: changes are strictly additive to the hardened teardown family. No existing contract, guard, or safety mechanism is altered.**

## Tests Added

### test_worktree.py (3 new)
1. `test_auto_stage_preserves_untracked_deposit_on_teardown` — untracked deposit auto-staged and survives teardown merge to main
2. `test_auto_stage_handles_multiple_deposits` — committed + untracked + staged-only deposits all survive teardown
3. `test_auto_stage_noop_when_all_committed` — no extra commit when deposits already committed

### test_gates.py (3 new)
4. `test_gate_fails_on_uncommitted_deposit` — gate fails with `deposit_uncommitted` for untracked deposit
5. `test_gate_deposit_uncommitted_evidence_message` — evidence contains path and clear description
6. `test_gate_passes_when_deposit_committed` — gate passes when deposit is committed (regression check)

## Test Results

```
461 passed, 1 warning in 6.54s
```

Full suite green, including 6 new tests and all existing regression tests.

## Files Modified

| File | Change |
|---|---|
| `bellows.py` | Added `_auto_stage_deposits()` helper; inserted calls before each `gates.check()` invocation |
| `gates.py` | Added `import subprocess`; added `_check_deposit_uncommitted()`; extended `_gate_deposit_exists()` |
| `tests/test_worktree.py` | Added 3 auto-stage tests; added `_auto_stage_deposits` import |
| `tests/test_gates.py` | Added 3 deposit_uncommitted gate tests |

## Pre-Edit Verification (Rule 39)

All 6 Section 6 Verification Blocks passed before editing:
1. No auto-staging code existed — PASS
2. Teardown merges via `git merge`, not file copy — PASS
3. `_resolve_deposit_path` uses `os.path.isfile`/`os.path.isdir` only — PASS
4. `_parse_diff_stat` uses `git diff` (excludes untracked) — PASS
5. Three pre-teardown call sites at lines 531, 624, 652 — PASS
6. `test_teardown_proceeds_on_empty_commit_list` confirms empty-commit legitimate — PASS

### Output Receipt

| Field | Value |
|---|---|
| Status | Complete |
| Deposit | `knowledge/development/deposit-loss-fix-2026-06-10.md` |
| Tests | 461 passed (6 new + 455 existing) |
| Daemon restart required | Yes |

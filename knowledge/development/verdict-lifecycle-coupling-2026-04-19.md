# Verdict Lifecycle Coupling — Dev Log (BACKLOG #9)
**Date:** 2026-04-19 | **Agent:** Bellows Developer | **Plan:** executable-verdict-lifecycle-coupling-2026-04-19

---

## Commits

| # | SHA | Message |
|---|-----|---------|
| 1 | c5c7742 | feat(bellows): add _cleanup_verdicts_for_slug helper |
| 2 | 7a6c5dc | feat(bellows): sweep stranded verdict requests on terminal-state transitions |
| 3 | a028c53 | feat(bellows): one-time startup sweep for orphaned verdict requests |
| 4 | cf2c68a | test(bellows): unit tests for _cleanup_verdicts_for_slug |

---

## Test Output

```
tests/test_cleanup_verdicts.py::TestCleanupVerdictsForSlug::test_cleanup_removes_all_step_files_for_slug PASSED [ 25%]
tests/test_cleanup_verdicts.py::TestCleanupVerdictsForSlug::test_cleanup_noop_when_no_matches PASSED [ 50%]
tests/test_cleanup_verdicts.py::TestCleanupVerdictsForSlug::test_cleanup_respects_slug_boundary PASSED [ 75%]
tests/test_cleanup_verdicts.py::TestCleanupVerdictsForSlug::test_cleanup_ignores_resolved_directory PASSED [100%]

4 passed, 1 warning in 0.10s
```

---

## Files Created or Modified (Code)

| File | Lines | What Changed |
|------|-------|--------------|
| `bellows.py` | L123–135 | New `_cleanup_verdicts_for_slug(slug, verdicts_root=None) -> int` helper — globs `verdict-request-{slug}-step-*.md` in `verdicts/pending/`, unlinks matches, prints count when >0. Optional `verdicts_root` parameter for testability. |
| `bellows.py` | L372 | Site A: auto-close call in `run_plan()` — `_cleanup_verdicts_for_slug(verdict._slug_from_path(plan_path))` before `shutil.move` |
| `bellows.py` | L663 | Site B: continue-to-done call in `_consume_verdicts()` — `_cleanup_verdicts_for_slug(plan_slug)` before `shutil.move` to Done |
| `bellows.py` | L681 | Site C: halt call in `_consume_verdicts()` — `_cleanup_verdicts_for_slug(plan_slug)` before `shutil.move` to halted |
| `bellows.py` | L715–748 | Startup sweep in `Bellows.start()` — collects active slugs from all watched project dirs (root + Done/), iterates `verdicts/pending/`, removes files whose slug is not in the active set |
| `tests/test_cleanup_verdicts.py` | L1–58 | 4 unit tests: removes all step files, noop on no matches, respects slug boundary (prefix collision), ignores resolved directory |

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Implemented verdict lifecycle coupling (BACKLOG #9). Added `_cleanup_verdicts_for_slug` helper that glob-sweeps all `verdict-request-{slug}-step-*.md` files from `verdicts/pending/`. Inserted sweep calls at three terminal-state transitions (auto-close, continue-to-done, halt) and added a one-time startup sweep that removes orphaned requests with no matching plan in any state. Four unit tests verify correctness including slug prefix collision safety.

### Files Deposited
- `knowledge/development/verdict-lifecycle-coupling-2026-04-19.md` — this dev log

### Files Created or Modified (Code)
- `bellows.py` — added `_cleanup_verdicts_for_slug` helper (L123–135), 3 terminal-state call sites (L372, L663, L681), startup sweep (L715–748)
- `tests/test_cleanup_verdicts.py` — 4 unit tests for the helper

### Decisions Made
- Added optional `verdicts_root` parameter to `_cleanup_verdicts_for_slug` for testability (keeps production call sites unchanged)
- Placed sweep calls BEFORE `shutil.move` at all three sites per diagnostic recommendation (section 7)
- Kept existing per-step cleanup at L688–690 as belt-and-suspenders per diagnostic section 7 recommendation

### Flags for CEO
- REMINDER: restart Bellows to load the startup sweep

### Flags for Next Step
- None — all 4 deliverables shipped and verified

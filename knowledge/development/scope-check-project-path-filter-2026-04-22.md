# Dev Log: scope_check project-path filter (BACKLOG #2 point fix)
**Date:** 2026-04-22 | **Plan:** executable-scope-check-project-path-filter-2026-04-22

## Change Summary

Added a `project_path` filter to `_parse_diff_stat` in `bellows.py` so that files outside the plan's project directory are excluded from `files_changed` before `scope_check` runs. This eliminates false positives where `git diff --stat` (run with `cwd=project_path`) reports files in sibling projects or the repo root via `../` prefixes, which then fail scope_check because their paths don't appear in step text.

## Files Modified

- `bellows.py` (lines 400-432) — updated `_parse_diff_stat` signature from `(post_diff, pre_diff)` to `(post_diff, pre_diff, project_path=None)`; added filter logic using `os.path.normpath` + `os.sep` split to drop paths with `..` components; added docstring explaining the filter rationale.
- `bellows.py` (line 267) — first call site in `run_plan`: now passes `project_path` as third arg.
- `bellows.py` (line 325) — second call site in `run_plan` (loop body): now passes `project_path` as third arg.
- `tests/test_bellows.py` — added 6 new test cases for the project-path filter.

## Tests Added

| Test Name | Purpose |
|---|---|
| `test_parse_diff_stat_no_project_path_returns_all` | Backward compat: no project_path → all files returned |
| `test_parse_diff_stat_project_path_all_inside` | All files inside project → all returned |
| `test_parse_diff_stat_project_path_filters_dotdot` | Mixed inside/outside files → only inside returned |
| `test_parse_diff_stat_project_path_filters_sibling_project` | Sibling project file (`../anvil/foo.py`) → filtered |
| `test_parse_diff_stat_project_path_filters_repo_root` | Repo root file (`../LESSONS.md`) → filtered |
| `test_parse_diff_stat_project_path_keeps_deep_paths` | Deep nested project files → all returned |

## Commit SHA

`fd9053f`

## Backward Compatibility Notes

- `_parse_diff_stat` retains its original 2-arg signature via `project_path=None` default. Existing callers (including all pre-existing unit tests) continue to work unchanged.
- Both call sites in `run_plan` now pass the third arg, so the filter is active during live execution.

---
## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Added project-path filter to `_parse_diff_stat` that drops files with `../` path components when `project_path` is provided. Updated both call sites in `run_plan`. Added 6 unit tests covering backward compat, filtering, and edge cases. All 52 tests pass.

### Files Deposited
- `knowledge/development/scope-check-project-path-filter-2026-04-22.md` — this dev log

### Files Created or Modified (Code)
- `bellows.py` — added `project_path` param to `_parse_diff_stat`, updated both call sites
- `tests/test_bellows.py` — added 6 project-path filter tests

### Decisions Made
- Used `os.path.normpath` + split on `os.sep` for `..` detection (simple, no filesystem access needed)
- Kept filter in `_parse_diff_stat` rather than a separate function (single responsibility, minimal change)

### Flags for CEO
- None

### Flags for Next Step
- QA should verify all 6 new tests plus existing `_parse_diff_stat` tests pass (52 total in test_bellows.py)

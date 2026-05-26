# QA Report — file_change_audit false-negative fix

**Date:** 2026-05-25
**Plan:** `executable-file-change-audit-fix-2026-05-25`
**DEV commit:** `950436cfbba1` (`fix(bellows): file_change_audit now detects committed changes — closes BACKLOG 2026-05-21`)

## Deliverable Verification Table

| # | Check | Status | Evidence |
|---|-------|--------|----------|
| 1 | `_capture_git_diff` body rewritten to call `git rev-parse HEAD` | ✅ | `bellows.py:692`: `["git", "--no-pager", "rev-parse", "HEAD"]` |
| 2 | `_capture_git_diff` returns empty string on subprocess error | ✅ | `bellows.py:695-696`: `if result.returncode != 0: return ""` and `bellows.py:698-699`: `except Exception: return ""` |
| 3 | `_parse_diff_stat` body rewritten to call `git diff --stat --relative <pre_diff> -- .` | ✅ | `bellows.py:730`: `["git", "--no-pager", "diff", "--stat", "--relative", pre_diff, "--", "."]` — only `--stat` occurrence in bellows.py |
| 4 | `_parse_diff_stat` short-circuits on empty `pre_diff` | ✅ | `bellows.py:723`: `if not pre_diff: return []` |
| 5 | `_parse_diff_stat` preserves `..` path filter | ✅ | `bellows.py:749-752`: `if project_path is not None:` block with `os.path.normpath(f).split(os.sep)` filter |
| 6 | All `_parse_diff_stat` call sites pass `wt_path` (not `project_path`) as third arg | ✅ | `bellows.py:487`: `_parse_diff_stat(post_diff, pre_diff, wt_path)` and `bellows.py:578`: `_parse_diff_stat(post_diff, pre_diff, wt_path)` — 2 call sites total (plan said 4 but there are only 2 `_parse_diff_stat` call sites; dev log documents this deviation) |
| 7 | 10 old tests deleted (from plan list) | ✅ | grep for all 10 deleted test names returns 0 hits in `tests/test_bellows.py` (dev deleted 12 total — 2 additional tests also testing old contract) |
| 8 | 6 new test functions present | ✅ | grep returns 6 hits: `test_capture_git_diff_returns_head_sha`, `test_capture_git_diff_returns_empty_on_no_git`, `test_parse_diff_stat_empty_pre_sha_returns_empty`, `test_parse_diff_stat_detects_committed_changes`, `test_parse_diff_stat_detects_uncommitted_changes`, `test_parse_diff_stat_filters_dotdot_paths` |
| 9 | 32 existing `patch("bellows._capture_git_diff", return_value="")` mock-patch sites unchanged | ✅ | grep count = 32; `git diff HEAD~1 tests/test_bellows.py` shows changes bounded to lines 536-642 region only — no modifications to mock-patch sites elsewhere |

## Full-Suite Pytest Summary

**Result:** 407 collected, 396 passed, 11 failed (0 new regressions)

All 6 new tests PASSED:
- `test_capture_git_diff_returns_head_sha` PASSED
- `test_capture_git_diff_returns_empty_on_no_git` PASSED
- `test_parse_diff_stat_empty_pre_sha_returns_empty` PASSED
- `test_parse_diff_stat_detects_committed_changes` PASSED
- `test_parse_diff_stat_detects_uncommitted_changes` PASSED
- `test_parse_diff_stat_filters_dotdot_paths` PASSED

11 pre-existing carry-over failures (zero new):
- 4 × `test_decisions.py` (worktree artifacts)
- 6 × `test_rule_26_deposit_parser.py` (set→list refactor, commit 4e805fa)
- 1 × `test_run_step_timeout`

Full output: `evidence/executable-file-change-audit-fix-2026-05-25/pytest_full.txt`

## Live Smoke Verification

```
_capture_git_diff returned: 950436cfbba1...
HEAD~1: 3ddb48b93afa...
Files changed in last commit: ['.../file-change-audit-fix-2026-05-25.md', 'bellows.py', 'knowledge/research/agent-prompt-feedback.md', 'tests/test_bellows.py']
PASS: scope_check is no longer silently no-opping on committed changes
```

Committed changes are now detected. The old implementation would have returned `files_changed = []` here.

Full output: `evidence/executable-file-change-audit-fix-2026-05-25/smoke_test.txt`

## Structural Compliance

**DEV commit files:** `bellows.py`, `tests/test_bellows.py`, `knowledge/development/file-change-audit-fix-2026-05-25.md`, `knowledge/research/agent-prompt-feedback.md` (4 files — the 4th is standard prompt feedback protocol, not a plan deviation).

**bellows.py diff bounded to:**
- (a) `_capture_git_diff` function body (signature `def _capture_git_diff(project_path: str) -> str:` unchanged)
- (b) `_parse_diff_stat` function body (signature `def _parse_diff_stat(post_diff: str, pre_diff: str, project_path: Optional[str] = None) -> list:` unchanged)
- (c) 2 call sites in `run_plan` changing third arg from `project_path` to `wt_path` (lines 487, 578)
- No other functions modified.

**tests/test_bellows.py diff bounded to:** lines 536-642 region (old tests removed, new tests added) plus `import subprocess` added to imports. No changes elsewhere.

Evidence files:
- `evidence/executable-file-change-audit-fix-2026-05-25/dev_commit.txt`
- `evidence/executable-file-change-audit-fix-2026-05-25/diff_bellows.txt`
- `evidence/executable-file-change-audit-fix-2026-05-25/diff_tests.txt`

## Rule 20 Self-Check

**Output:**

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/file-change-audit-fix-2026-05-25/knowledge/qa/evidence/executable-file-change-audit-fix-2026-05-25/
Files verified: 5
```

## Output Receipt

**Status: Complete**

- All 9 deliverable checks: ✅
- Full pytest suite: 396 passed, 11 pre-existing failures, 0 new regressions
- All 6 new tests: PASSED
- Smoke test: PASS — committed changes detected
- Structural compliance: bounded diff, signatures preserved
- Closes BACKLOG 2026-05-21 `file_change_audit` false-negative
- Closes cascading silent bypass of `_gate_scope_check`

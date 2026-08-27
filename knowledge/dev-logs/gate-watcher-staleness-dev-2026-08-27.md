# Dev Log — gate-watcher staleness: resolved-verdict check (exec-573)

**Date:** 2026-08-27

## Diff summary

```
 tests/test_gate_watcher.py | 215 ++++++++++++++++++++++++++++++---------------
 tools/gate_watcher.py      |  78 ++++++++--------
 2 files changed, 180 insertions(+), 113 deletions(-)
```

**Deletions:** `judge_watch_line` function (lines 113-134); `armed` flag, `arm_pending` seeding, and threading in `main`; `TestArmTimeSnapshot` class (8 tests).

**Additions:** `_verdict_issued` helper (disk check for both `verdict-<id>-step-<N>.md` and `processed-verdict-<id>-step-<N>.md`); `resolved_dir` kwarg on `read_state` with default derived from pending dir; staleness partition in the pause branch (unparseable names treated as live); `--resolved-dir` CLI arg threaded to both `read_state` call sites; `TestPauseStateSpace` class (6 named tests + 24 parametrized cells).

## Pin re-derivation

| id | plan value | measured | status |
|---|---|---|---|
| B1 | `verdicts/resolved/verdict-<id>-step-<N>.md` (issued) and `processed-verdict-<id>-step-<N>.md` (consumed) | `ls verdicts/resolved/` shows `processed-verdict-570-step-{1,2}.md`, `processed-verdict-571-step-{1,2}.md`; no pre-consumption `verdict-*` files present (all already consumed). Both naming forms confirmed in code. | matches |
| B2 | `verdict.py:180-188` writes `verdict-request-{slug}-step-{N}.md` | `verdict.py:181-187` — `slug_from_path` at `:85-95`. Line numbers shifted by 1 vs plan; supersedes. | matches (line shift) |
| B3 | `{abandoned, closed, halted, in_progress}`; `awaiting_verdict` absent | `SELECT DISTINCT lifecycle_state FROM plans` → `abandoned, closed, halted, in_progress`. Confirmed. | matches |
| B4 | `judge_watch_line` at `:113-134`; `arm_pending`/`armed` in `main` | Confirmed at those lines; all deleted. | matches |
| B5 | 24 tests (16 + 8 TestArmTimeSnapshot); full suite 1582 at exec-570 + 8 = 1590 | `--collect-only` → 24 tests pre-deletion. Post-deletion baseline: 16 passed. | matches |

## Test counts

`--collect-only` after all changes: **46 tests collected**
- 16 baseline (pre-572, restored)
- 6 named TestPauseStateSpace tests
- 24 parametrized cells (2 PENDING x 3 VERDICT x 4 STATE)

## Targeted test run

```
.........................................s....                           [100%]
45 passed, 1 skipped, 1 warning in 0.39s
```

The 1 skip is `test_reachable_states_match_the_classification_dimension` — no `lifecycle.db` in the worktree; QA Item 2.6 runs it with `GATE_WATCHER_LIVE_DB` pointed at the live checkout.

## Deletion probes

```
$ /usr/bin/grep -cF "arm_pending" tools/gate_watcher.py
0

$ /usr/bin/grep -cF "TestArmTimeSnapshot" tests/test_gate_watcher.py
0
```
